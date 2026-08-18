"""
Unit tests untuk QuantAnalyticsEngine.
Memverifikasi akurasi perhitungan:
- Win Rate, PnL, Fees
- Expected Value (EV)
- Profit Factor, Payoff Ratio
- Max Drawdown (USDT & %)
- Calmar Ratio, Sharpe Ratio, Sortino Ratio
- SQN (System Quality Number) & Kelly Criterion
- Edge cases: Kosong, 100% Win, 100% Loss, Cancelled-only trades
"""

import unittest
import os
import sys

# Ensure ROOT_DIR in sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Set dummy MONGO_URI for import safety
os.environ["MONGO_URI"] = "mongodb://localhost:27017/test_db"

from src.modules.quant_analytics import QuantAnalyticsEngine


class TestQuantAnalyticsEngine(unittest.TestCase):

    def setUp(self):
        # Inisialisasi engine tanpa koneksi database aktif untuk pure math test
        self.engine = QuantAnalyticsEngine.__new__(QuantAnalyticsEngine)

    def test_empty_trades(self):
        """Memastikan jika trades kosong, respon tidak error dan bernilai default 0."""
        res = self.engine.calculate_metrics([])
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["summary"]["total_recorded_trades"], 0)
        self.assertEqual(res["summary"]["expected_value_usdt"], 0.0)
        self.assertEqual(res["summary"]["calmar_ratio"], 0.0)
        self.assertEqual(res["summary"]["profit_factor"], 0.0)

    def test_cancelled_trades_only(self):
        """Memastikan trades dengan result CANCELLED/TIMEOUT tidak merusak kalkulasi."""
        dummy = [
            {"result": "CANCELLED", "pnl_usdt": 0, "symbol": "BTC/USDT", "timestamp": "2026-08-18T10:00:00"},
            {"result": "TIMEOUT", "pnl_usdt": 0, "symbol": "ETH/USDT", "timestamp": "2026-08-18T11:00:00"},
        ]
        res = self.engine.calculate_metrics(dummy)
        self.assertEqual(res["summary"]["total_recorded_trades"], 2)
        self.assertEqual(res["summary"]["total_executed_trades"], 0)
        self.assertEqual(res["summary"]["cancelled_count"], 2)
        self.assertEqual(res["summary"]["win_rate_percent"], 0.0)

    def test_quant_metrics_calculation(self):
        """
        Menguji dataset 4 transaksi:
        1: Win +$20, Fee $1, ROI 10%
        2: Loss -$10, Fee $1, ROI -5%
        3: Win +$30, Fee $1, ROI 15%
        4: Loss -$10, Fee $1, ROI -5%
        
        Total Executed = 4
        Wins = 2, Losses = 2 -> Win Rate = 50%
        Gross Profit = 50, Gross Loss = 20 -> PF = 50 / 20 = 2.5
        Total PnL = 30, Total Fees = 4 -> Net PnL = 26
        Avg Win = 25, Avg Loss = 10 -> Payoff = 2.5
        EV = (0.5 * 25) - (0.5 * 10) = 12.5 - 5 = 7.5 USDT per trade
        """
        dummy = [
            {"result": "WIN", "pnl_usdt": 20.0, "fee": 1.0, "size_usdt": 200.0, "roi_percent": 10.0, "symbol": "BTC/USDT", "strategy_tag": "MOMENTUM", "side": "BUY", "exit_type": "TP", "timestamp": "2026-08-18T10:00:00"},
            {"result": "LOSS", "pnl_usdt": -10.0, "fee": 1.0, "size_usdt": 200.0, "roi_percent": -5.0, "symbol": "BTC/USDT", "strategy_tag": "MOMENTUM", "side": "BUY", "exit_type": "SL", "timestamp": "2026-08-18T11:00:00"},
            {"result": "WIN", "pnl_usdt": 30.0, "fee": 1.0, "size_usdt": 200.0, "roi_percent": 15.0, "symbol": "ETH/USDT", "strategy_tag": "BREAKOUT", "side": "SELL", "exit_type": "TP", "timestamp": "2026-08-18T12:00:00"},
            {"result": "LOSS", "pnl_usdt": -10.0, "fee": 1.0, "size_usdt": 200.0, "roi_percent": -5.0, "symbol": "SOL/USDT", "strategy_tag": "BREAKOUT", "side": "BUY", "exit_type": "SL", "timestamp": "2026-08-18T13:00:00"},
        ]
        
        res = self.engine.calculate_metrics(dummy)
        s = res["summary"]

        self.assertEqual(s["total_executed_trades"], 4)
        self.assertEqual(s["win_count"], 2)
        self.assertEqual(s["loss_count"], 2)
        self.assertEqual(s["win_rate_percent"], 50.0)
        self.assertEqual(s["loss_rate_percent"], 50.0)
        self.assertEqual(s["gross_profit_usdt"], 50.0)
        self.assertEqual(s["gross_loss_usdt"], 20.0)
        self.assertEqual(s["total_pnl_usdt"], 30.0)
        self.assertEqual(s["total_fees_usdt"], 4.0)
        self.assertEqual(s["net_pnl_usdt"], 26.0)
        self.assertEqual(s["profit_factor"], 2.5)
        self.assertEqual(s["avg_win_usdt"], 25.0)
        self.assertEqual(s["avg_loss_usdt"], 10.0)
        self.assertEqual(s["payoff_ratio"], 2.5)
        self.assertEqual(s["expected_value_usdt"], 7.5)

        # Drawdown check:
        # Cum PnL: [20, 10, 40, 30]
        # Peak:    [20, 20, 40, 40]
        # Drawdown: [0, 10,  0, 10] -> Max DD = 10
        self.assertEqual(s["max_drawdown_usdt"], 10.0)

        # Calmar Ratio = Net PnL (26) / Max DD (10) = 2.6
        self.assertEqual(s["calmar_ratio"], 2.6)

        # SQN & Kelly Criterion should be > 0
        self.assertGreater(s["sqn"], 0)
        self.assertGreater(s["kelly_percent"], 0)

        # Check breakdown
        self.assertEqual(len(res["breakdown"]["by_symbol"]), 3)
        self.assertEqual(len(res["charts"]["equity_curve"]), 4)

    def test_all_wins_scenario(self):
        """Memastikan jika 100% win, tidak ada division by zero pada Calmar / Sortino / Profit Factor."""
        dummy = [
            {"result": "WIN", "pnl_usdt": 50.0, "fee": 1.0, "size_usdt": 100.0, "roi_percent": 50.0, "symbol": "BTC/USDT", "timestamp": "2026-08-18T10:00:00"},
            {"result": "WIN", "pnl_usdt": 50.0, "fee": 1.0, "size_usdt": 100.0, "roi_percent": 50.0, "symbol": "ETH/USDT", "timestamp": "2026-08-18T11:00:00"},
        ]
        res = self.engine.calculate_metrics(dummy)
        s = res["summary"]
        self.assertEqual(s["win_rate_percent"], 100.0)
        self.assertEqual(s["profit_factor"], 99.0)
        self.assertEqual(s["max_drawdown_usdt"], 0.0)
        self.assertEqual(s["calmar_ratio"], 99.0)
        self.assertEqual(s["sortino_ratio"], 99.0)

    def test_all_losses_scenario(self):
        """Memastikan jika 100% loss, perhitungan tetap konsisten."""
        dummy = [
            {"result": "LOSS", "pnl_usdt": -20.0, "fee": 1.0, "size_usdt": 100.0, "roi_percent": -20.0, "symbol": "BTC/USDT", "timestamp": "2026-08-18T10:00:00"},
            {"result": "LOSS", "pnl_usdt": -30.0, "fee": 1.0, "size_usdt": 100.0, "roi_percent": -30.0, "symbol": "ETH/USDT", "timestamp": "2026-08-18T11:00:00"},
        ]
        res = self.engine.calculate_metrics(dummy)
        s = res["summary"]
        self.assertEqual(s["win_rate_percent"], 0.0)
        self.assertEqual(s["loss_rate_percent"], 100.0)
        self.assertEqual(s["profit_factor"], 0.0)
        self.assertEqual(s["expected_value_usdt"], -25.0)


if __name__ == "__main__":
    unittest.main()
