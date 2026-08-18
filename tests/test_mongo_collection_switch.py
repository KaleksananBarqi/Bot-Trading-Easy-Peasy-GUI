"""
Unit test untuk memvalidasi dynamic collection switching pada MongoManager,
QuantAnalyticsEngine, dan FastAPI web app routes.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

os.environ["MONGO_URI"] = "mongodb://localhost:27017/test_db"

from fastapi.testclient import TestClient
from web_app.main import app
from src.modules.mongo_manager import MongoManager
from src.modules.quant_analytics import QuantAnalyticsEngine


class TestMongoCollectionSwitch(unittest.TestCase):

    def setUp(self):
        # Reset MongoManager singleton for clean test state
        MongoManager._instance = None

    def tearDown(self):
        MongoManager._instance = None

    @patch("src.modules.mongo_manager.MongoManager.connect", return_value=True)
    def test_mongo_manager_switch_collection(self, mock_connect):
        """Memastikan MongoManager dapat mengganti target collection secara dinamis."""
        mongo = MongoManager()
        mongo.db = MagicMock()
        mongo.db.list_collection_names.return_value = ["trades_07_2026", "trades_08_2026"]
        
        initial_col = mongo.collection_name
        self.assertTrue(mongo.switch_collection("trades_09_2026"))
        self.assertEqual(mongo.collection_name, "trades_09_2026")
        
        # Cek list collection
        cols = mongo.get_available_trade_collections()
        self.assertIn("trades_09_2026", cols)

    @patch("src.modules.mongo_manager.MongoManager.connect", return_value=True)
    def test_switch_collection_guard_same_name(self, mock_connect):
        """Memastikan switch_collection dengan nama yang sama tidak mengeksekusi _setup_indexes ulang."""
        mongo = MongoManager()
        mongo.db = MagicMock()
        mongo.trades_collection = MagicMock()
        mongo.collection_name = "trades_08_2026"
        
        with patch.object(mongo, "_setup_indexes") as mock_setup:
            result = mongo.switch_collection("trades_08_2026")
            self.assertTrue(result)
            mock_setup.assert_not_called()

    @patch("src.modules.mongo_manager.MongoManager.connect", return_value=True)
    def test_quant_analytics_collection_switch(self, mock_connect):
        """Memastikan QuantAnalyticsEngine meneruskan parameter collection_name ke MongoManager."""
        mongo = MongoManager()
        mongo.db = MagicMock()
        mongo.get_trades = MagicMock(return_value=[
            {"result": "WIN", "pnl_usdt": 15.0, "fee": 0.2, "size_usdt": 100.0, "roi_percent": 15.0, "symbol": "BTC/USDT", "strategy_tag": "MOMENTUM", "side": "BUY", "exit_type": "TP", "timestamp": "2026-08-18T10:00:00"}
        ])
        
        engine = QuantAnalyticsEngine(mongo_manager=mongo)
        trades = engine.fetch_raw_trades(days=30, collection_name="trades_custom_test")
        
        self.assertEqual(mongo.collection_name, "trades_custom_test")
        self.assertEqual(len(trades), 1)

    @patch("src.modules.mongo_manager.MongoManager.connect", return_value=True)
    @patch("src.modules.mongo_manager.MongoManager.get_available_trade_collections")
    def test_api_collections_endpoint(self, mock_get_cols, mock_connect):
        """Memastikan endpoint /api/data/trades/collections mengembalikan data dengan benar."""
        mock_get_cols.return_value = ["trades_07_2026", "trades_08_2026"]
        
        client = TestClient(app)
        response = client.get("/api/data/trades/collections")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("collections", data)
        self.assertIn("trades_08_2026", data["collections"])

    @patch("src.modules.mongo_manager.MongoManager.connect", return_value=True)
    @patch("src.modules.mongo_manager.MongoManager.get_trades")
    def test_api_history_with_collection_param(self, mock_get_trades, mock_connect):
        """Memastikan endpoint /api/data/trades/history menerima query param collection."""
        mock_get_trades.return_value = [
            {"symbol": "SOL/USDT", "pnl_usdt": 5.0, "timestamp": "2026-08-18"}
        ]
        
        client = TestClient(app)
        response = client.get("/api/data/trades/history?collection=trades_07_2026")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")


if __name__ == "__main__":
    unittest.main(verbosity=2)
