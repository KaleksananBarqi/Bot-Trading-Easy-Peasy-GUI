import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import config
from src.modules.market_data import _calculate_market_structure_static

class TestMarketStructure(unittest.TestCase):
    
    def setUp(self):
        # Setup common mock data if needed
        pass

    def create_bars(self, prices, volume=100.0, base_ts=1000):
        """Helper to create bars list from a list of Close prices.
        Assumes Open=Close, High=Close+1, Low=Close-1 for simplicity, 
        unless specific patterns are needed for High/Low."""
        bars = []
        for i, p in enumerate(prices):
            # [timestamp, open, high, low, close, volume]
            # Structure logic uses High and Low.
            # So we typically pass (High, Low) or just use logic to set them.
            # To make it simple, let's allow passing tuples (High, Low) or just Close.
            
            if isinstance(p, (tuple, list)):
                h, l = p
                o = c = (h + l) / 2
            else:
                c = p
                h = p
                l = p
                o = p
                
            bars.append([base_ts + i*60, o, h, l, c, volume])
        return bars

    def test_insufficient_data(self):
        """Test returning INSUFFICIENT_DATA if bars count < config limit"""
        # Config default is likely 50 based on original code check
        # Let's mock config.MIN_BARS_MARKET_STRUCTURE to be sure or use a very small list
        with patch.object(config, 'MIN_BARS_MARKET_STRUCTURE', 10):
            bars = self.create_bars([10] * 5) # Only 5 bars
            result = _calculate_market_structure_static(bars)
            self.assertEqual(result, "INSUFFICIENT_DATA")

    def test_bullish_structure(self):
        """Test HH + HL pattern"""
        # We need enough bars. Let's say 20 bars.
        # We need swings.
        # Swing Highs: A, B (B > A)
        # Swing Lows: X, Y (Y > X)
        
        # Pattern: Low -> High -> Higher Low -> Higher High
        # Let's verify with indices.
        # 0..4: Low base
        # 5: High (A) = 100
        # 8: Low (X) = 50
        # 12: High (B) = 110 (Higher High)
        # 15: Low (Y) = 60 (Higher Low)
        # 16..19: Current price action
        
        # Need config.MIN_BARS_MARKET_STRUCTURE to be met.
        # Let's assume we patch it to 10 for easier testing.
        
        with patch.object(config, 'MIN_BARS_MARKET_STRUCTURE', 10):
            # Construct a wave
            # Indices:  0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18
            highs =   [10, 20, 30, 40, 50,100, 90, 80, 50, 60, 70, 80,110, 90, 80, 60, 70, 75, 80]
            # HH at 12 (110) > HH at 5 (100)
            
            lows =    [ 5, 15, 25, 35, 45, 95, 85, 45, 50, 55, 65, 75,105, 85, 55, 60, 65, 70, 75]
            # HL at 15 (60) > HL at 8 (50)
            
            # Combine into bars
            bars = []
            for h, l in zip(highs, lows):
                bars.append([1000, 100, h, l, 100, 100])
                
            # Lookback is default 5.
            # argrelextrema checks 5 points either side.
            # Index 5 is order 5 max? 0..5..10. 
            # Sub-sequence: [10, 20, 30, 40, 50, 100, 90, 80, 50, 60, 70]
            # 100 is max.
            
            # Use smaller lookback for easier manual construction
            result = _calculate_market_structure_static(bars, lookback=2)
            
            # Debug helps if test fails
            # Swing Highs expected at index 5 (100) and 12 (110). 110 > 100 -> HH
            # Swing Lows expected at index 8 (50) and 15 (60). 60 > 50 -> HL
            
            self.assertEqual(result, "BULLISH (HH + HL)")

    def test_bearish_structure(self):
        """Test LH + LL pattern"""
        with patch.object(config, 'MIN_BARS_MARKET_STRUCTURE', 10):
            # Highs: peak at idx 2 (100) and idx 6 (90) -> 90 < 100 (LH)
            highs = [60, 80, 100, 80, 60, 70, 90, 70, 50, 50, 50, 50]
            # Lows: trough at idx 4 (40) and idx 8 (20) -> 20 < 40 (LL)
            lows  = [50, 70,  90, 60, 40, 55, 75, 50, 20, 40, 40, 40]
            
            bars = []
            for h, l in zip(highs, lows):
                bars.append([1000, 100, h, l, 100, 100])
                
            result = _calculate_market_structure_static(bars, lookback=2)
            self.assertEqual(result, "BEARISH (LH + LL)")

    def test_expanding_structure_megaphone(self):
        """Test Higher High + Lower Low"""
        with patch.object(config, 'MIN_BARS_MARKET_STRUCTURE', 10):
            # Highs: peak at idx 2 (100) and idx 6 (120) -> 120 > 100 (HH)
            highs = [60, 80, 100, 80, 70, 90, 120, 90, 50, 50, 50, 50]
            # Lows: trough at idx 4 (60) and idx 8 (30) -> 30 < 60 (LL)
            lows  = [50, 70,  85, 75, 60, 75, 100, 70, 30, 50, 50, 50]
            
            bars = []
            for h, l in zip(highs, lows):
                bars.append([1000, 100, h, l, 100, 100])
                
            result = _calculate_market_structure_static(bars, lookback=2)
            self.assertEqual(result, "EXPANDING (Megaphone)")

    def test_consolidation_structure_triangle(self):
        """Test Lower High + Higher Low"""
        with patch.object(config, 'MIN_BARS_MARKET_STRUCTURE', 10):
            # LH + HL
            # Peak 1: 100
            # Peak 2: 90 (Lower)
            # Trough 1: 50
            # Trough 2: 60 (Higher)
            
            # idx 3: 100
            # idx 6: 50
            # idx 9: 90
            # idx 12: 60
            
            highs = [80, 90, 95, 100, 90, 80, 60, 80, 85, 90, 85, 80, 70, 65, 70, 75, 75, 75]
            lows =  [70, 80, 85,  95, 80, 70, 50, 70, 75, 85, 75, 70, 60, 55, 60, 65, 65, 65]
            
            bars = []
            for h, l in zip(highs, lows):
                bars.append([1000, 100, h, l, 100, 100])
                
            result = _calculate_market_structure_static(bars, lookback=2)
            self.assertEqual(result, "CONSOLIDATION (Triangle)")

    def test_unclear_few_swings(self):
        """Test return UNCLEAR if swings found < 2"""
        with patch.object(config, 'MIN_BARS_MARKET_STRUCTURE', 10):
            # Straight line up, no swings
            highs = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
            lows =  [ 5, 15, 25, 35, 45, 55, 65, 75, 85, 95]
            
            bars = []
            for h, l in zip(highs, lows):
                bars.append([1000, 100, h, l, 100, 100])
                
            result = _calculate_market_structure_static(bars, lookback=2)
            self.assertEqual(result, "UNCLEAR")
            
    def test_error_handling(self):
        """Test graceful error handling"""
        # Malformed bars (e.g., None)
        bars = None
        result = _calculate_market_structure_static(bars)
        # Should catch exception and return ERROR or handle len() check crash?
        # The code calculates len(bars) first. if bars is None -> TypeError
        # The function wraps in try-except and returns "ERROR" or similar?
        
        # Checking code:
        # try:
        #   if len(bars) < ...
        # except Exception as e: return "ERROR"
        
        # So passing None should trigger TypeError on len(), caught by except -> "ERROR"
        self.assertEqual(result, "ERROR")

if __name__ == '__main__':
    unittest.main()
