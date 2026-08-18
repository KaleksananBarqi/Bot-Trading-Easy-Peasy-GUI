import unittest
import html
import sys
import os
import asyncio
from unittest.mock import patch, MagicMock

# Add project root path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
# Add src to path so 'import config' works inside helper.py
sys.path.append(os.path.join(project_root, 'src'))

# Mock Config BEFORE importing helper
with patch.dict('sys.modules', {'config': MagicMock()}):
    import config
    config.LOG_FILENAME = "test.log"
    
    # Import target module
    from src.utils.helper import kirim_tele, kirim_notif, logger

class TestNotificationSafety(unittest.TestCase):
    
    def test_html_escape_logic(self):
        """1. Verify HTML Escaping Logic (for AI Reason & Dashboard)"""
        print("\n--- TEST: HTML Escaping ---")
        
        dirty_inputs = [
            ("Price < 500", "Price &lt; 500"),
            ("RSI > 70", "RSI &gt; 70"),
            ("Tag <b>Bold</b>", "Tag &lt;b&gt;Bold&lt;/b&gt;"),
            ("Normal Text", "Normal Text")
        ]
        
        for raw, expected in dirty_inputs:
            escaped = html.escape(raw)
            print(f"Input: '{raw}' -> Escaped: '{escaped}'")
            self.assertEqual(escaped, expected)

    def test_kirim_tele_logging(self):
        """2. Verify kirim_tele (and alias kirim_notif) logs properly"""
        print("\n--- TEST: Local Notification Logging ---")
        
        with patch.object(logger, 'info') as mock_logger:
            asyncio.run(kirim_tele("<b>Test Alert</b>", alert=True, channel='trade'))
            mock_logger.assert_called()
            args, _ = mock_logger.call_args
            log_msg = args[0]
            print(f"Captured Log: {log_msg}")
            self.assertIn("TRADE: Test Alert", log_msg)
            self.assertIn("⚠️ [SYSTEM ALERT]", log_msg)

if __name__ == '__main__':
    unittest.main()
