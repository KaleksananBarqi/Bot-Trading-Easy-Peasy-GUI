6. STRATEGY SELECTION (CHOOSE ONE):
   
   A. LIQUIDITY_REVERSAL_MASTER
      ✓ USE IF: Sweep rejection confirmed (wick > S1/R1, body closes back)
      ✓ REQUIRES: Volume spike > {volume_spike}x + RSI extreme
      → Select SCENARIO A (Long) or B (Short) based on sweep zone
      → NOTE: Must pass Exception criteria if Trend Lock is active.
   
   B. PULLBACK_CONTINUATION
      ✓ USE IF: Strong trend (ADX > {adx_period}) + price pulling back to EMA
      ✓ REQUIRES: Trend direction clear, no sweep happening
      → LONG in uptrend pullback to EMA {ema_fast}/{ema_slow}
      → SHORT in downtrend bounce to EMA {ema_fast}/{ema_slow}
   
   C. BREAKDOWN_FOLLOW
      ✓ USE IF: Price CLOSES beyond S1/R1 with volume (true breakout, not sweep)
      ✓ REQUIRES: Body close beyond level + volume confirmation
      → SHORT if breaks S1, LONG if breaks R1
   
   D. WAIT (No Trade)
      ✓ USE IF: Price in no-man's land (between S1-R1) OR conflicting signals

7. EXECUTION MODE:
   {execution_mode_text}
   - Limit Order: Use pre-calculated entry from EXECUTION SCENARIOS.
