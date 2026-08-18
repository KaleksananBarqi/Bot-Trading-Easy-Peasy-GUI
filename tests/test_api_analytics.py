"""
Test FastAPI endpoints untuk Trade Analytics & History.
Menggunakan mocking MongoManager agar cepat dan independen dari MongoDB service.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Ensure ROOT_DIR in sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Set dummy MONGO_URI for import safety
os.environ["MONGO_URI"] = "mongodb://localhost:27017/test_db"

from fastapi.testclient import TestClient
from web_app.main import app


class TestAPIAnalytics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        from src.modules.mongo_manager import MongoManager
        MongoManager._instance = None

    def tearDown(self):
        from src.modules.mongo_manager import MongoManager
        MongoManager._instance = None

    @patch("src.modules.mongo_manager.MongoManager.connect", return_value=True)
    @patch("src.modules.mongo_manager.MongoManager.get_trades")
    def test_analytics_endpoint_with_trades(self, mock_get_trades, mock_connect):
        """Memastikan endpoint /api/data/trades/analytics menghitung metrik dengan benar dari data mock."""
        mock_get_trades.return_value = [
            {"result": "WIN", "pnl_usdt": 25.0, "fee": 0.5, "size_usdt": 100.0, "roi_percent": 25.0, "symbol": "BTC/USDT", "strategy_tag": "MOMENTUM", "side": "BUY", "exit_type": "TP", "timestamp": "2026-08-18T10:00:00"},
            {"result": "LOSS", "pnl_usdt": -10.0, "fee": 0.5, "size_usdt": 100.0, "roi_percent": -10.0, "symbol": "ETH/USDT", "strategy_tag": "BREAKOUT", "side": "SELL", "exit_type": "SL", "timestamp": "2026-08-18T11:00:00"},
        ]
        
        response = self.client.get("/api/data/trades/analytics?days=30")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        
        summary = data["summary"]
        self.assertEqual(summary["total_executed_trades"], 2)
        self.assertEqual(summary["win_rate_percent"], 50.0)
        self.assertEqual(summary["profit_factor"], 2.5)
        self.assertEqual(summary["net_pnl_usdt"], 14.0)
        self.assertEqual(summary["expected_value_usdt"], 7.5)
        self.assertIn("equity_curve", data["charts"])

    @patch("src.modules.mongo_manager.MongoManager.connect", return_value=True)
    @patch("src.modules.mongo_manager.MongoManager.get_trade_count")
    @patch("src.modules.mongo_manager.MongoManager.get_trades")
    def test_history_endpoint_pagination(self, mock_get_trades, mock_get_count, mock_connect):
        """Memastikan endpoint /api/data/trades/history mengembalikan data dengan pagination yang benar."""
        mock_get_count.return_value = 25
        mock_get_trades.return_value = [{"symbol": f"COIN{i}/USDT", "pnl_usdt": 10.0, "timestamp": "2026-08-18"} for i in range(25)]
        
        response = self.client.get("/api/data/trades/history?page=1&limit=10")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["data"]), 10)
        self.assertEqual(data["pagination"]["total_items"], 25)
        self.assertEqual(data["pagination"]["total_pages"], 3)
        self.assertEqual(data["pagination"]["page"], 1)

    @patch("src.modules.mongo_manager.MongoManager.connect", return_value=True)
    @patch("src.modules.mongo_manager.MongoManager.get_trades")
    def test_filters_endpoint(self, mock_get_trades, mock_connect):
        """Memastikan endpoint /api/data/trades/filters mengembalikan list unik simbol & strategi."""
        mock_get_trades.return_value = [
            {"symbol": "BTC/USDT", "strategy_tag": "MOMENTUM"},
            {"symbol": "ETH/USDT", "strategy_tag": "BREAKOUT"},
            {"symbol": "BTC/USDT", "strategy_tag": "MOMENTUM"}
        ]
        response = self.client.get("/api/data/trades/filters")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["symbols"], ["BTC/USDT", "ETH/USDT"])
        self.assertEqual(data["strategies"], ["BREAKOUT", "MOMENTUM"])


if __name__ == "__main__":
    unittest.main()
