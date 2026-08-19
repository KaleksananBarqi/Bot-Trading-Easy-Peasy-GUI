import asyncio
import time
import ccxt.async_support as ccxt
import config
from src.utils.helper import logger, kirim_tele

class SafetyManager:
    """
    Manages Safety Orders (SL/TP).
    Responsibilities:
    - Install SL/TP (Dynamic ATR-based or Fallback Percentage).
    """
    def __init__(self, exchange, tracker):
        self.exchange = exchange
        self.tracker = tracker
        self._safety_lock = asyncio.Lock()

    # --- SAFETY ORDERS (SL/TP) ---
    async def install_safety_orders(self, symbol, pos_data):
        """
        Pasang SL dan TP untuk posisi yang sudah terbuka.
        """
        async with self._safety_lock:  # Prevent race condition
            entry_price = float(pos_data['entryPrice'])
            side = pos_data['side']
            
            # 1. Cancel Old Orders
            try:
                await self.exchange.fapiPrivateDeleteAllOpenOrders({'symbol': symbol.replace('/', '')})
            except ccxt.BaseError as e:
                logger.debug(f"Cancel old orders for {symbol}: {e}")
            
            # 2. Hitung Jarak SL/TP
            # Cek apakah kita punya data ATR dari tracker (saat entry)
            tracker_data = self.tracker.get(symbol) or {}
            atr_val = tracker_data.get('atr_value', 0)
            
            sl_price = 0.0
            tp_price = 0.0
            
            if atr_val > 0:
                # --- DYNAMIC ATR LOGIC ---
                dist_sl = atr_val * config.TRAP_SAFETY_SL
                dist_tp = atr_val * config.ATR_MULTIPLIER_TP1
                
                if side == "LONG":
                    sl_price = entry_price - dist_sl
                    tp_price = entry_price + dist_tp
                else:
                    sl_price = entry_price + dist_sl
                    tp_price = entry_price - dist_tp
                    
                logger.info(f"🛡️ Safety Calc (ATR {atr_val}): SL dist {dist_sl}, TP dist {dist_tp}")
            
            else:
                # --- FALLBACK PERCENTAGE ---
                sl_percent = config.DEFAULT_SL_PERCENT
                tp_percent = config.DEFAULT_TP_PERCENT
                
                if side == "LONG":
                    sl_price = entry_price * (1 - sl_percent)
                    tp_price = entry_price * (1 + tp_percent)
                else:
                    sl_price = entry_price * (1 + sl_percent)
                    tp_price = entry_price * (1 - tp_percent)
                
                logger.info(f"🛡️ Safety Calc (Fallback %): SL {sl_percent*100:.2f}%, TP {tp_percent*100:.2f}% | Entry: {entry_price}")

            # 3. Validasi Harga Pasar Terkini vs Stop Price (Mencegah Binance Error -2021: Immediate Trigger)
            current_price = None
            try:
                ticker = await self.exchange.fetch_ticker(symbol)
                current_price = float(ticker.get('last') or ticker.get('mark') or entry_price)
            except Exception as e:
                logger.debug(f"Could not fetch latest ticker for {symbol}, using entry_price: {e}")
                current_price = entry_price

            if current_price and current_price > 0:
                if side == "LONG":
                    # Untuk LONG: SL (Sell) wajib < current_price, TP (Sell) wajib > current_price
                    if sl_price >= current_price:
                        logger.warning(f"⚠️ {symbol} SL ({sl_price}) >= Current Price ({current_price}). Adjusting SL to 0.5% below current price.")
                        sl_price = current_price * 0.995
                    if tp_price <= current_price:
                        logger.warning(f"⚠️ {symbol} TP ({tp_price}) <= Current Price ({current_price}). Position already in profit! Adjusting TP to above current price.")
                        tp_price = current_price * (1 + config.DEFAULT_TP_PERCENT)
                else:  # SHORT
                    # Untuk SHORT: SL (Buy) wajib > current_price, TP (Buy) wajib < current_price
                    if sl_price <= current_price:
                        logger.warning(f"⚠️ {symbol} SL ({sl_price}) <= Current Price ({current_price}). Adjusting SL to 0.5% above current price.")
                        sl_price = current_price * 1.005
                    if tp_price >= current_price:
                        logger.warning(f"⚠️ {symbol} TP ({tp_price}) >= Current Price ({current_price}). Position already in profit! Adjusting TP to below current price.")
                        tp_price = current_price * (1 - config.DEFAULT_TP_PERCENT)
            
            if side == "LONG":
                side_api = 'sell'
            else:
                side_api = 'buy'

            p_sl = self.exchange.price_to_precision(symbol, sl_price)
            p_tp = self.exchange.price_to_precision(symbol, tp_price)

            sl_order = None
            tp_order = None

            # 4. Pasang Stop Loss & Take Profit secara Terpisah
            try:
                # A. STOP LOSS (STOP_MARKET)
                sl_order = await self.exchange.create_order(symbol, 'STOP_MARKET', side_api, None, None, {
                    'stopPrice': p_sl, 'closePosition': True, 'workingType': 'MARK_PRICE'
                })
                logger.info(f"✅ SL Installed: {symbol} | SL {p_sl}")
            except Exception as e:
                logger.error(f"❌ Install SL Failed {symbol} @ {p_sl}: {e}")

            try:
                # B. TAKE PROFIT (TAKE_PROFIT_MARKET)
                tp_order = await self.exchange.create_order(symbol, 'TAKE_PROFIT_MARKET', side_api, None, None, {
                    'stopPrice': p_tp, 'closePosition': True, 'workingType': 'MARK_PRICE'
                })
                logger.info(f"✅ TP Installed: {symbol} | TP {p_tp}")
            except Exception as e:
                logger.error(f"❌ Install TP Failed {symbol} @ {p_tp}: {e}")

            # 5. Update Tracker
            if sl_order or tp_order:
                logger.info(f"✅ Safety Orders Result: {symbol} | SL: {'OK' if sl_order else 'FAILED'} | TP: {'OK' if tp_order else 'FAILED'}")
                status_to_set = "SECURED" if (sl_order and tp_order) else "PARTIALLY_SECURED"

                tracker_payload = {
                    "status": status_to_set,
                    "entry_price": entry_price,
                    "tp_price": float(tp_price),
                    "sl_price_initial": float(sl_price),
                    "side": side,
                    "last_check": time.time()
                }
                if sl_order:
                    tracker_payload["sl_order_id"] = str(sl_order['id'])
                if tp_order:
                    tracker_payload["tp_order_id"] = str(tp_order['id'])

                if self.tracker.exists(symbol):
                    self.tracker.update(symbol, tracker_payload)
                else:
                    tracker_payload["created_at"] = time.time()
                    self.tracker.set(symbol, tracker_payload)
                
                await self.tracker.save()
                return True
            else:
                logger.error(f"❌ Both SL and TP failed to install for {symbol}")
                return False
