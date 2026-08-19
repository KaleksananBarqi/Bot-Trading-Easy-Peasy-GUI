import unittest
from unittest.mock import AsyncMock, MagicMock
import sys
import os
import asyncio

# Add project root and src to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

os.environ["MONGO_URI"] = "mongodb://dummy:27017/test"

import config
from src.modules.executor_impl.safety import SafetyManager
from src.modules.executor_impl.tracker import TradeTracker

class TestSafetyOrders(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_exchange = AsyncMock()
        self.mock_exchange.fapiPrivateDeleteAllOpenOrders = AsyncMock()
        self.mock_exchange.price_to_precision = MagicMock(side_effect=lambda s, p: f"{float(p):.4f}")
        self.mock_exchange.create_order = AsyncMock(side_effect=lambda sym, otype, side, amt, price, params: {
            'id': f"mock_{otype}_{side}",
            'status': 'NEW'
        })
        
        self.tracker = TradeTracker()
        self.tracker.data = {}
        self.tracker.save = AsyncMock()
        
        self.safety = SafetyManager(self.mock_exchange, self.tracker)

    async def test_fallback_percentage_short(self):
        """Uji posisi SHORT tanpa ATR menggunakan fallback percentage."""
        entry_price = 50000.0
        pos_data = {
            'entryPrice': entry_price,
            'contracts': 0.1,
            'side': 'SHORT'
        }
        # Mock ticker = entry price
        self.mock_exchange.fetch_ticker.return_value = {'last': entry_price, 'mark': entry_price}

        result = await self.safety.install_safety_orders("BTC/USDT", pos_data)
        self.assertTrue(result)

        # Expected calculations
        expected_sl = entry_price * (1 + config.DEFAULT_SL_PERCENT)
        expected_tp = entry_price * (1 - config.DEFAULT_TP_PERCENT)

        tracker_data = self.tracker.get("BTC/USDT")
        self.assertIsNotNone(tracker_data)
        self.assertEqual(tracker_data['status'], "SECURED")
        self.assertAlmostEqual(tracker_data['sl_price_initial'], expected_sl, places=2)
        self.assertAlmostEqual(tracker_data['tp_price'], expected_tp, places=2)

        # Verifikasi call create_order:
        # 1. STOP_MARKET side 'buy' workingType 'MARK_PRICE'
        # 2. TAKE_PROFIT_MARKET side 'buy' workingType 'MARK_PRICE'
        self.assertEqual(self.mock_exchange.create_order.call_count, 2)
        calls = self.mock_exchange.create_order.call_args_list
        sl_call = calls[0]
        tp_call = calls[1]

        self.assertEqual(sl_call.args[1], 'STOP_MARKET')
        self.assertEqual(sl_call.args[2], 'buy')
        self.assertEqual(sl_call.args[5]['workingType'], 'MARK_PRICE')

        self.assertEqual(tp_call.args[1], 'TAKE_PROFIT_MARKET')
        self.assertEqual(tp_call.args[2], 'buy')
        self.assertEqual(tp_call.args[5]['workingType'], 'MARK_PRICE')
        self.assertEqual(tp_call.args[5]['stopPrice'], f"{expected_tp:.4f}")

    async def test_fallback_percentage_long(self):
        """Uji posisi LONG tanpa ATR menggunakan fallback percentage."""
        entry_price = 60000.0
        pos_data = {
            'entryPrice': entry_price,
            'contracts': 0.1,
            'side': 'LONG'
        }
        self.mock_exchange.fetch_ticker.return_value = {'last': entry_price, 'mark': entry_price}

        result = await self.safety.install_safety_orders("BTC/USDT", pos_data)
        self.assertTrue(result)

        expected_sl = entry_price * (1 - config.DEFAULT_SL_PERCENT)
        expected_tp = entry_price * (1 + config.DEFAULT_TP_PERCENT)

        tracker_data = self.tracker.get("BTC/USDT")
        self.assertIsNotNone(tracker_data)
        self.assertEqual(tracker_data['status'], "SECURED")
        self.assertAlmostEqual(tracker_data['sl_price_initial'], expected_sl, places=2)
        self.assertAlmostEqual(tracker_data['tp_price'], expected_tp, places=2)

    async def test_market_price_adjustment_for_already_profitable_short(self):
        """Uji posisi SHORT manual yang sudah profit melewati TP awal saat bot sync."""
        entry_price = 50000.0
        current_price = 48000.0  # Harga sudah turun jauh di bawah entry
        pos_data = {
            'entryPrice': entry_price,
            'contracts': 0.1,
            'side': 'SHORT'
        }
        self.mock_exchange.fetch_ticker.return_value = {'last': current_price, 'mark': current_price}

        result = await self.safety.install_safety_orders("BTC/USDT", pos_data)
        self.assertTrue(result)

        tracker_data = self.tracker.get("BTC/USDT")
        # TP harus disesuaikan agar < current_price (48000) sehingga tidak error -2021 di Binance
        self.assertLess(tracker_data['tp_price'], current_price)

    async def test_market_price_adjustment_for_already_profitable_long(self):
        """Uji posisi LONG manual yang sudah profit melewati TP awal saat bot sync."""
        entry_price = 50000.0
        current_price = 52000.0  # Harga sudah naik di atas entry
        pos_data = {
            'entryPrice': entry_price,
            'contracts': 0.1,
            'side': 'LONG'
        }
        self.mock_exchange.fetch_ticker.return_value = {'last': current_price, 'mark': current_price}

        result = await self.safety.install_safety_orders("BTC/USDT", pos_data)
        self.assertTrue(result)

        tracker_data = self.tracker.get("BTC/USDT")
        # TP harus disesuaikan agar > current_price (52000) sehingga tidak error -2021 di Binance
        self.assertGreater(tracker_data['tp_price'], current_price)

if __name__ == '__main__':
    unittest.main()
