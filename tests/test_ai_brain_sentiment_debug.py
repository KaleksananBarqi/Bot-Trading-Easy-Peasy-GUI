import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from src.modules.ai_brain import AIBrain
import config

class TestAIBrainSentiment(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ai = AIBrain()
        self.ai.client = MagicMock()

    async def test_analyze_sentiment_empty_prompt(self):
        # Empty prompt should return None immediately and not crash
        res = await self.ai.analyze_sentiment("")
        self.assertIsNone(res)
        res_spaces = await self.ai.analyze_sentiment("   ")
        self.assertIsNone(res_spaces)

    async def test_analyze_sentiment_empty_ai_response(self):
        # Empty response from AI should return None gracefully
        mock_choice = MagicMock()
        mock_choice.message.content = ""
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        self.ai.client.chat.completions.create = AsyncMock(return_value=mock_completion)

        res = await self.ai.analyze_sentiment("Valid Prompt")
        self.assertIsNone(res)

    async def test_analyze_sentiment_valid_json(self):
        # Valid JSON response
        mock_choice = MagicMock()
        mock_choice.message.content = '```json\n{"analysis": "sentiment", "overall_sentiment": "BULLISH", "sentiment_score": 80}\n```'
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        self.ai.client.chat.completions.create = AsyncMock(return_value=mock_completion)

        res = await self.ai.analyze_sentiment("Valid Prompt")
        self.assertIsNotNone(res)
        self.assertEqual(res.get("overall_sentiment"), "BULLISH")
        self.assertEqual(res.get("sentiment_score"), 80)

    async def test_analyze_sentiment_invalid_json(self):
        # Non-JSON response should not crash and return None
        mock_choice = MagicMock()
        mock_choice.message.content = 'This is plain text without JSON'
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        self.ai.client.chat.completions.create = AsyncMock(return_value=mock_completion)

        res = await self.ai.analyze_sentiment("Valid Prompt")
        self.assertIsNone(res)

    def test_cfg_empty_string_fallback(self):
        from src.config import _cfg
        # If key has empty string in GUI override, it should fallback to default
        with patch.dict('src.config._GUI_OVERRIDE', {'EMPTY_KEY': ''}):
            self.assertEqual(_cfg('EMPTY_KEY', 'DEFAULT_VAL'), 'DEFAULT_VAL')
        with patch.dict('src.config._GUI_OVERRIDE', {'SPACES_KEY': '   '}):
            self.assertEqual(_cfg('SPACES_KEY', 'DEFAULT_VAL'), 'DEFAULT_VAL')
        with patch.dict('src.config._GUI_OVERRIDE', {'VALID_KEY': 'CUSTOM_VAL'}):
            self.assertEqual(_cfg('VALID_KEY', 'DEFAULT_VAL'), 'CUSTOM_VAL')
