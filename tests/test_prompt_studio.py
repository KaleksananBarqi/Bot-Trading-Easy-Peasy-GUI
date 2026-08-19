import pytest
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from starlette.testclient import TestClient
from web_app.main import app
import config
from src.utils.prompt_builder import safe_format, build_market_prompt

client = TestClient(app)

def test_prompt_files_exist():
    """Memastikan semua file template markdown ada di direktori prompts/."""
    prompts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'prompts')
    required_files = [
        'system_role.md',
        'strategy_selection.md',
        'sentiment_analysis.md',
        'pattern_recognition.md',
        'btc_with_context.md',
        'btc_no_context.md',
        'market_analysis_output_format.md'
    ]
    for filename in required_files:
        filepath = os.path.join(prompts_dir, filename)
        assert os.path.exists(filepath), f"File {filename} tidak ditemukan di {prompts_dir}"
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            assert len(content) > 10, f"File {filename} kosong atau terlalu pendek"

def test_safe_format_functionality():
    """Menguji fungsi safe_format dengan berbagai kasus normal dan edge case."""
    # 1. Format normal
    res1 = safe_format("Hello {name}, price is {price}", name="Trader", price=65000)
    assert res1 == "Hello Trader, price is 65000"

    # 2. Format dengan placeholder yang hilang (tidak boleh crash)
    res2 = safe_format("Hello {name}, missing {unknown_tag}", name="Trader")
    assert "Hello Trader" in res2
    assert "{unknown_tag}" in res2

    # 3. Format dengan template rusak / invalid brackets
    res3 = safe_format("Invalid {{broken bracket {name}", name="Trader")
    assert "Trader" in res3

def test_api_prompts_defaults():
    """Menguji API endpoint /api/config/prompts/defaults."""
    res = client.get('/api/config/prompts/defaults')
    assert res.status_code == 200
    data = res.json().get('data', {})
    assert 'AI_SYSTEM_ROLE' in data
    assert 'PROMPT_STRATEGY_SELECTION' in data
    assert 'PROMPT_SENTIMENT_ANALYSIS' in data
    assert 'PROMPT_PATTERN_RECOGNITION' in data
    assert 'PROMPT_BTC_WITH_CONTEXT' in data
    assert 'PROMPT_MARKET_ANALYSIS_OUTPUT_FORMAT' in data
    assert len(data['AI_SYSTEM_ROLE']) > 50

def test_api_prompts_variables():
    """Menguji API endpoint /api/config/prompts/variables."""
    res = client.get('/api/config/prompts/variables')
    assert res.status_code == 200
    data = res.json().get('data', {})
    assert 'AI_SYSTEM_ROLE' in data
    assert isinstance(data['AI_SYSTEM_ROLE'], list)
    assert len(data['AI_SYSTEM_ROLE']) > 0
    assert 'tag' in data['AI_SYSTEM_ROLE'][0]

def test_api_prompts_sandbox_test():
    """Menguji API endpoint /api/config/prompts/test."""
    payload = {
        "symbol": "BTC/USDT",
        "call_ai": False,
        "prompt_overrides": {
            "AI_SYSTEM_ROLE": "Custom Test System Role for Unit Testing."
        }
    }
    res = client.post('/api/config/prompts/test', json=payload)
    assert res.status_code == 200
    res_data = res.json().get('data', {})
    assert res_data.get('symbol') == "BTC/USDT"
    assert 'tech_summary' in res_data
    assert 'rendered_prompt' in res_data
    assert "Custom Test System Role for Unit Testing" in res_data['rendered_prompt']
