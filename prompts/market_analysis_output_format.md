OUTPUT FORMAT (JSON ONLY):
{{
  "analysis": {{
    "interaction_zone": "TESTING_S1 / TESTING_R1 / MID_RANGE",
    "zone_reaction": "WICK_REJECTION (Reversal) / BREAKOUT_CLOSE (Continuation) / TESTING (Indecisive)",
    "price_vs_pivot": "BELOW_S1 / ABOVE_R1 / INSIDE_RANGE"
  }},
  "selected_strategy": "NAME OF STRATEGY",
  "execution_mode": {execution_mode_json},
  "decision": "BUY" | "SELL" | "WAIT",
  "reason": "Explain your logic in INDONESIAN language, referencing specific macro and micro factors.",
  "confidence": 0-100,
  "risk_level": "LOW" | "MEDIUM" | "HIGH"
}}
