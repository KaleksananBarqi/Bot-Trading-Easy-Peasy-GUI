import sys
import os
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('src'))

import pytest
import pandas as pd
import numpy as np
import config
from src.modules.market_data import _calculate_volume_indicators, _prepare_dataframe
from src.modules.ai_eval_manager import AIEvaluationManager
from src.modules.pattern_recognizer import PatternRecognizer

def test_volume_ma_calculation_correctness():
    """Memastikan VOL_MA dihitung murni dari kolom volume, bukan close price."""
    # Setup data dimana price (~80,000) sangat jauh dari volume (~100)
    bars = []
    for i in range(30):
        # [timestamp, open, high, low, close, volume]
        bars.append([1000 + i*60, 80000.0, 80500.0, 79500.0, 80000.0, 100.0 + (i % 5)])
    
    df = _prepare_dataframe(bars)
    _calculate_volume_indicators(df)
    
    assert 'VOL_MA' in df.columns
    # VOL_MA harus sekitar 100-104, TIDAK BOLEH bernilai 80000
    assert df['VOL_MA'].iloc[-1] < 500
    assert df['VOL_MA'].iloc[-1] > 50
    assert not np.isnan(df['VOL_MA'].iloc[-1])

def test_ai_eval_manager_logging_and_stats():
    """Memastikan AIEvaluationManager dapat mencatat evaluasi dan menghitung stats."""
    manager = AIEvaluationManager()
    
    # Log BUY evaluation
    doc1 = manager.log_evaluation(
        symbol="BTC/USDT",
        decision="BUY",
        confidence=85.0,
        strategy_mode="LIQUIDITY_REVERSAL_MASTER",
        reason="Strong bounce off S1 support with volume spike",
        tech_data={"price": 65000, "volume": 150, "vol_ma": 100, "rsi": 32}
    )
    assert doc1["decision"] == "BUY"
    assert doc1["confidence"] == 85.0

    # Log WAIT evaluation
    doc2 = manager.log_evaluation(
        symbol="ETH/USDT",
        decision="WAIT",
        confidence=40.0,
        strategy_mode="STANDARD",
        reason="RSI neutral and no clear edge",
        tech_data={"price": 3200, "volume": 50, "vol_ma": 80, "rsi": 50}
    )
    assert doc2["decision"] == "WAIT"

    # Get stats
    stats = manager.get_stats()
    assert stats["total_evaluations"] >= 2
    assert stats["buy_count"] >= 1
    assert stats["wait_count"] >= 1

    # Get evaluations filter
    res = manager.get_evaluations(symbol="BTC/USDT", limit=10)
    assert res["status"] == "success"
    assert len(res["data"]) >= 1

def test_ai_eval_manager_objectid_and_custom_types_serialization():
    """Memastikan _save_local_cache tidak crash saat data mengandung bson.ObjectId atau custom types."""
    from bson import ObjectId
    manager = AIEvaluationManager()
    
    # Masukkan doc yang mengandung ObjectId ke local history
    custom_doc = {
        "_id": ObjectId(),
        "timestamp": "2026-08-19T03:50:00.000000",
        "symbol": "SOL/USDT",
        "decision": "BUY",
        "confidence": 92.0,
        "reason": "Breakout test with ObjectId",
    }
    manager.local_history.append(custom_doc)
    
    # Harus berhasil menyimpan tanpa TypeError ObjectId is not JSON serializable
    manager._save_local_cache()
    
    # Load kembali dari disk dan pastikan valid JSON
    loaded = manager._load_local_cache()
    assert len(loaded) > 0
    assert any(x.get("symbol") == "SOL/USDT" for x in loaded)

@pytest.mark.asyncio
async def test_pattern_recognizer_bypass_when_disabled(monkeypatch):
    """Memastikan PatternRecognizer mengembalikan is_valid=True saat dinonaktifkan."""
    monkeypatch.setattr(config, 'USE_PATTERN_RECOGNITION', False)
    
    pr = PatternRecognizer(None)
    result = await pr.analyze_pattern("BTC/USDT")
    
    assert result["is_valid"] is True
    assert "Disabled" in result["analysis"]


def test_pattern_recognizer_init_states(monkeypatch, caplog):
    """Memastikan log level INFO saat disabled dan WARNING saat missing key."""
    import logging
    
    # 1. State: Disabled by config -> harus log INFO
    caplog.clear()
    monkeypatch.setattr(config, 'USE_PATTERN_RECOGNITION', False)
    with caplog.at_level(logging.INFO):
        pr_disabled = PatternRecognizer(None)
        assert pr_disabled.client is None
        assert any("Vision AI Disabled by configuration" in r.message for r in caplog.records)
        assert not any(r.levelno >= logging.WARNING for r in caplog.records)
        
    # 2. State: Enabled but missing key -> harus log WARNING
    caplog.clear()
    monkeypatch.setattr(config, 'USE_PATTERN_RECOGNITION', True)
    monkeypatch.setattr(config, 'AI_API_KEY', "")
    with caplog.at_level(logging.INFO):
        pr_missing_key = PatternRecognizer(None)
        assert pr_missing_key.client is None
        assert any(r.levelno == logging.WARNING and "AI_API_KEY is missing" in r.message for r in caplog.records)


