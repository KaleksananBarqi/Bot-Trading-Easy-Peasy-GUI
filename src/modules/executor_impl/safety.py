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
            
            sl_price = 0
            tp_price = 0
            
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
                    tp_price = entry_price - tp_percent
            
            if side == "LONG": side_api = 'sell'
            else: side_api = 'buy'

            p_sl = self.exchange.price_to_precision(symbol, sl_price)
            p_tp = self.exchange.price_to_precision(symbol, tp_price)

            try:
                # A. STOP LOSS (STOP_MARKET)
                sl_order = await self.exchange.create_order(symbol, 'STOP_MARKET', side_api, None, None, {
                    'stopPrice': p_sl, 'closePosition': True, 'workingType': 'MARK_PRICE'
                })
                # B. TAKE PROFIT (TAKE_PROFIT_MARKET)
                tp_order = await self.exchange.create_order(symbol, 'TAKE_PROFIT_MARKET', side_api, None, None, {
                    'stopPrice': p_tp, 'closePosition': True, 'workingType': 'CONTRACT_PRICE'
                })
                
                logger.info(f"✅ Safety Orders Installed: {symbol} | SL {p_sl} | TP {p_tp}")

                # [UPDATE] Save TP/SL info to tracker
                if self.tracker.exists(symbol):
                    self.tracker.update(symbol, {
                        "status": "SECURED",
                        "entry_price": entry_price,
                        "tp_price": tp_price,
                        "sl_price_initial": sl_price,
                        "sl_order_id": str(sl_order['id']),
                        "tp_order_id": str(tp_order['id']),
                        "side": side
                    })
                    await self.tracker.save()
                else:
                     # Create if not exists (e.g., manual position)
                    self.tracker.set(symbol, {
                        "status": "SECURED",
                        "entry_price": entry_price,
                        "tp_price": tp_price,
                        "sl_price_initial": sl_price,
                        "sl_order_id": str(sl_order['id']),
                        "tp_order_id": str(tp_order['id']),
                        "side": side,
                        "created_at": time.time()
                    })
                    await self.tracker.save()

                return True
            except Exception as e:
                logger.error(f"❌ Install Safety Failed {symbol}: {e}")
                return False
