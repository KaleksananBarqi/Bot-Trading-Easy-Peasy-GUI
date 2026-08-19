import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from src.utils.helper import logger, convert_timestamp_to_wib_str, get_wib_now

class AIEvaluationManager:
    """
    Manajer pencatatan dan rekapitulasi evaluasi pasar oleh AI.
    Menyimpan setiap keputusan AI (BUY, SELL, WAIT) ke MongoDB dan cache lokal JSON.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIEvaluationManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.cache_dir = os.path.join(self.root_dir, "data_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.cache_file = os.path.join(self.cache_dir, "ai_evaluations_history.json")
        self.max_local_history = 500
        
        # Load local cache
        self.local_history = self._load_local_cache()
        self._initialized = True

    def _load_local_cache(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            if not item.get("time_wib") and item.get("timestamp"):
                                item["time_wib"] = convert_timestamp_to_wib_str(item["timestamp"])
                        return data
            except Exception as e:
                logger.warning(f"⚠️ Gagal memuat local cache AI evaluations: {e}")
        return []

    def _save_local_cache(self):
        try:
            # Keep only last N records in local json file
            trimmed = self.local_history[-self.max_local_history:]
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(trimmed, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.warning(f"⚠️ Gagal menyimpan local cache AI evaluations: {e}")

    def log_evaluation(
        self,
        symbol: str,
        decision: str,
        confidence: float,
        strategy_mode: str,
        reason: str,
        tech_data: Optional[Dict[str, Any]] = None,
        pattern_analysis: Optional[Dict[str, Any]] = None,
        sentiment_data: Optional[Dict[str, Any]] = None,
        sentiment_analysis: Optional[Dict[str, Any]] = None,
        execution_mode: str = "MARKET",
        prompt: str = ""
    ) -> Dict[str, Any]:
        """
        Mencatat satu entri evaluasi AI dalam zona waktu WIB (UTC+7).
        """
        wib_now = get_wib_now()
        timestamp_iso = wib_now.isoformat()
        wib_time = wib_now.strftime('%d/%m/%Y %H:%M:%S WIB')
        
        decision_upper = str(decision).upper() if decision else "WAIT"
        if decision_upper not in ["BUY", "SELL", "WAIT", "LONG", "SHORT"]:
            decision_upper = "WAIT"

        # Build clean snapshot
        tech_snapshot = {}
        if tech_data and isinstance(tech_data, dict):
            tech_snapshot = {
                "price": tech_data.get("price", 0),
                "rsi": tech_data.get("rsi", 0),
                "adx": tech_data.get("adx", 0),
                "volume": tech_data.get("volume", 0),
                "vol_ma": tech_data.get("vol_ma", 0),
                "vol_ratio": round((tech_data.get("volume", 0) / tech_data.get("vol_ma", 1)), 2) if tech_data.get("vol_ma", 0) > 0 else 0,
                "ema_fast": tech_data.get("ema_fast", 0),
                "ema_slow": tech_data.get("ema_slow", 0),
                "price_vs_ema": tech_data.get("price_vs_ema", "-"),
                "trend_major": tech_data.get("trend_major", "-"),
                "btc_trend": tech_data.get("btc_trend", "-"),
                "btc_correlation": tech_data.get("btc_correlation", 0),
            }

        vision_summary = "N/A"
        if pattern_analysis and isinstance(pattern_analysis, dict):
            vision_summary = pattern_analysis.get("analysis", "No pattern context.")

        sentiment_score = 50
        sentiment_status = "NEUTRAL"
        if sentiment_analysis and isinstance(sentiment_analysis, dict):
            sentiment_score = sentiment_analysis.get("sentiment_score", 50)
            sentiment_status = sentiment_analysis.get("overall_sentiment", "NEUTRAL")
        elif sentiment_data and isinstance(sentiment_data, dict):
            sentiment_score = sentiment_data.get("fng_value", 50)
            sentiment_status = sentiment_data.get("fng_text", "Neutral")

        eval_doc = {
            "timestamp": timestamp_iso,
            "time_wib": wib_time,
            "symbol": symbol,
            "decision": decision_upper,
            "confidence": float(confidence or 0),
            "strategy_mode": strategy_mode or "STANDARD",
            "execution_mode": execution_mode or "MARKET",
            "reason": str(reason or "-"),
            "vision_summary": vision_summary,
            "sentiment_score": sentiment_score,
            "sentiment_status": sentiment_status,
            "technical_snapshot": tech_snapshot,
            "prompt_snippet": prompt[:500] if prompt else ""
        }

        # 1. Update in-memory & local cache
        self.local_history.append(eval_doc)
        self._save_local_cache()

        # 2. Insert to MongoDB if available
        try:
            from src.modules.mongo_manager import MongoManager
            mongo = MongoManager()
            mongo.insert_ai_evaluation(dict(eval_doc))
        except Exception as e:
            # Fallback to local is already handled
            pass

        return eval_doc

    def get_evaluations(
        self,
        symbol: str = "ALL",
        decision: str = "ALL",
        limit: int = 50,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Mengambil daftar evaluasi dengan filter & pagination.
        """
        page = max(1, page)
        limit = max(1, min(200, limit))
        skip = (page - 1) * limit

        # Coba ambil dari MongoDB terlebih dahulu
        try:
            from src.modules.mongo_manager import MongoManager
            mongo = MongoManager()
            filter_query = {}
            if symbol and symbol != "ALL":
                filter_query["symbol"] = symbol.upper()
            if decision and decision != "ALL":
                filter_query["decision"] = decision.upper()

            total_count = mongo.get_ai_evaluation_count(filter_query)
            if total_count > 0:
                raw_docs = mongo.get_ai_evaluations(filter_query, limit=limit, skip=skip)
                cleaned = []
                for d in raw_docs:
                    doc = dict(d)
                    if "_id" in doc:
                        doc["_id"] = str(doc["_id"])
                    # Pastikan time_wib selalu akurat dalam format WIB
                    doc["time_wib"] = convert_timestamp_to_wib_str(doc.get("timestamp") or doc.get("time_wib"))
                    cleaned.append(doc)

                total_pages = max(1, (total_count + limit - 1) // limit)
                return {
                    "status": "success",
                    "data": cleaned,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total_items": total_count,
                        "total_pages": total_pages
                    }
                }
        except Exception as e:
            logger.debug(f"MongoDB AI eval fetch fallback to local: {e}")

        # Fallback: Refresh & Query dari local history
        self.local_history = self._load_local_cache()
        filtered = list(reversed(self.local_history))
        if symbol and symbol != "ALL":
            filtered = [x for x in filtered if x.get("symbol") == symbol.upper()]
        if decision and decision != "ALL":
            filtered = [x for x in filtered if x.get("decision") == decision.upper()]

        total_count = len(filtered)
        paginated = filtered[skip:skip + limit]
        for p in paginated:
            p["time_wib"] = convert_timestamp_to_wib_str(p.get("timestamp") or p.get("time_wib"))

        total_pages = max(1, (total_count + limit - 1) // limit)

        return {
            "status": "success",
            "data": paginated,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_items": total_count,
                "total_pages": total_pages
            }
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        Menghitung ringkasan statistik evaluasi AI.
        """
        # 1. Coba ambil dari MongoDB terlebih dahulu jika tersedia
        try:
            from src.modules.mongo_manager import MongoManager
            mongo = MongoManager()
            total_count = mongo.get_ai_evaluation_count({})
            if total_count > 0:
                buys = mongo.get_ai_evaluation_count({"decision": {"$in": ["BUY", "LONG"]}})
                sells = mongo.get_ai_evaluation_count({"decision": {"$in": ["SELL", "SHORT"]}})
                waits = mongo.get_ai_evaluation_count({"decision": "WAIT"})
                recent_docs = mongo.get_ai_evaluations({}, limit=1)
                recent = dict(recent_docs[0]) if recent_docs else None
                if recent and "_id" in recent:
                    recent["_id"] = str(recent["_id"])

                # Ambil sample recent docs untuk rata-rata confidence
                recent_sample = mongo.get_ai_evaluations({}, limit=100)
                avg_conf = round(sum(d.get("confidence", 0) for d in recent_sample) / len(recent_sample), 1) if recent_sample else 0.0

                return {
                    "total_evaluations": total_count,
                    "buy_count": buys,
                    "sell_count": sells,
                    "wait_count": waits,
                    "avg_confidence": avg_conf,
                    "recent_decision": recent
                }
        except Exception as e:
            logger.debug(f"MongoDB stats calculation fallback to local: {e}")

        # 2. Fallback: Query dari local history cache
        self.local_history = self._load_local_cache()
        history = self.local_history
        total = len(history)
        if total == 0:
            return {
                "total_evaluations": 0,
                "buy_count": 0,
                "sell_count": 0,
                "wait_count": 0,
                "avg_confidence": 0.0,
                "recent_decision": None
            }

        buys = sum(1 for x in history if x.get("decision") in ["BUY", "LONG"])
        sells = sum(1 for x in history if x.get("decision") in ["SELL", "SHORT"])
        waits = sum(1 for x in history if x.get("decision") == "WAIT")
        avg_conf = round(sum(x.get("confidence", 0) for x in history) / total, 1)

        recent = history[-1] if history else None

        return {
            "total_evaluations": total,
            "buy_count": buys,
            "sell_count": sells,
            "wait_count": waits,
            "avg_confidence": avg_conf,
            "recent_decision": recent
        }
