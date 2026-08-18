import asyncio
import time
import config
from src.utils.helper import logger, kirim_tele


class OrderSyncManager:
    """
    Manages synchronization of pending orders with the exchange.
    Responsibilities:
    - Detect manually cancelled orders.
    - Auto-cancel expired limit orders.
    - Update tracker state accordingly.
    """
    def __init__(self, exchange, tracker, positions):
        self.exchange = exchange
        self.tracker = tracker
        self.positions = positions

    async def ensure_position_mode(self, hedged: bool = False) -> bool:
        """
        Memastikan mode posisi akun di Binance sesuai dengan kebutuhan bot (Default: One-Way Mode / hedged=False).
        - Menangani respon -4059 ('No need to change') secara aman jika sudah sesuai.
        - Menangani respon -4068 jika terhalang order/posisi aktif dengan memberi log dan alert solutif.
        """
        mode_name = "Hedge Mode (Dual-Side)" if hedged else "One-Way Mode (Single-Side)"
        try:
            logger.info(f"⚙️ Memverifikasi Position Mode Binance (Target: {mode_name})...")
            if hasattr(self.exchange, 'set_position_mode'):
                await self.exchange.set_position_mode(hedged)
            else:
                await self.exchange.fapiPrivatePostPositionSideDual({
                    'dualSidePosition': 'true' if hedged else 'false'
                })
            logger.info(f"✅ Position Mode Binance berhasil disetel ke {mode_name}.")
            return True
        except Exception as e:
            err_msg = str(e).lower()
            if "no need to change" in err_msg or "-4059" in err_msg:
                logger.info(f"✅ Position Mode Binance sudah sesuai ({mode_name}).")
                return True
            elif "open orders or positions" in err_msg or "-4068" in err_msg:
                warning_msg = (
                    f"⚠️ <b>PERINGATAN POSITION MODE BINANCE</b>\n"
                    f"Akun Binance saat ini belum dalam <b>{mode_name}</b>.\n"
                    f"Bot tidak dapat mengubahnya otomatis karena ada posisi/order aktif di Binance.\n"
                    f"👉 <i>Solusi: Tutup order/posisi di Binance, lalu restart bot, atau ubah manual di Binance Futures Preferences -> Position Mode -> One-Way Mode.</i>"
                )
                logger.warning(f"⚠️ {warning_msg}")
                await kirim_tele(warning_msg, alert=True)
                return False
            else:
                logger.warning(f"⚠️ Gagal mengatur Position Mode: {e}")
                return False

    async def sync_pending_orders(self):
        """
        Sync open orders to detect manual cancellations.
        Only checks symbols that are in 'WAITING_ENTRY' status.
        """
        # 1. Identify symbols to check
        symbols_to_check = [
            sym for sym, data in self.tracker.data.items()
            if data.get('status') == 'WAITING_ENTRY'
        ]
        
        if not symbols_to_check:
            return

        # 2. Check symbols in parallel
        sem = asyncio.Semaphore(getattr(config, 'CONCURRENCY_LIMIT', 10))
        
        # Run all checks and collect results
        results = await asyncio.gather(*[
            self._check_symbol(sym, sem) for sym in symbols_to_check
        ])
        
        # 3. Save tracker if any changes were made
        if any(results):
            await self.tracker.save()

    async def _check_symbol(self, symbol: str, sem: asyncio.Semaphore) -> bool:
        """
        Check status of a single symbol's pending order.
        Returns True if tracker was modified, False otherwise.
        """
        async with sem:
            try:
                # Fetch Open Orders from Binance
                open_orders = await self.exchange.fetch_open_orders(symbol)
                open_order_ids = [str(o['id']) for o in open_orders]
                
                if not self.tracker.exists(symbol):
                    return False

                tracker_data = self.tracker.get(symbol)
                tracked_id = str(tracker_data.get('entry_id', ''))
                
                # [NEW] Check Expiry Time First
                current_time = time.time()
                expires_at = tracker_data.get('expires_at', float('inf'))

                if current_time > expires_at:
                    # Order expired -> Cancel & Cleanup
                    logger.info(f"⏰ Limit Order {symbol} expired after timeout. Cancelling...")
                    try:
                        await self.exchange.cancel_order(tracked_id, symbol)
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to cancel expired order {symbol} (might be already gone): {e}")

                    # Clean tracker
                    self.tracker.delete(symbol)
                    
                    await kirim_tele(
                        f"⏰ <b>ORDER EXPIRED</b>\n"
                        f"Limit Order {symbol} dibatalkan karena timeout > 2 jam.\n"
                        f"Tracker cleaned."
                    )
                    return True  # Skip further checks since we removed it
                
                if tracked_id not in open_order_ids:
                    # Order is missing! Either Filled or Cancelled.
                    
                    # Case A: Filled? (Check Position Cache)
                    if self.positions.has_position(symbol):
                        # It is filled! Update tracker.
                        logger.info(f"✅ Order {symbol} found filled during sync. Queuing for Safety Orders (PENDING).")
                        self.tracker.update(symbol, {
                            'status': 'PENDING',
                            'last_check': time.time()
                        })
                        return True
                    
                    # Case B: Cancelled/Expired?
                    else:
                        # Not active, not in open orders -> Cancelled manually
                        logger.info(f"🗑️ Found Stale/Cancelled Order for {symbol}. Removing from tracker.")
                        self.tracker.delete(symbol)

                        await kirim_tele(
                            f"🗑️ <b>ORDER SYNC</b>\n"
                            f"Order for {symbol} was cancelled manually/expired.\n"
                            f"Tracker cleaned."
                        )
                        return True

                return False

            except Exception as e:
                logger.error(f"⚠️ Sync Pending Error for {symbol}: {e}")
                return False
