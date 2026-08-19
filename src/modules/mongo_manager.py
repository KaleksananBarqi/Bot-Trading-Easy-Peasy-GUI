
import os
import sys
import time
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from src.utils.helper import logger
try:
    from src import config
except ImportError:
    import config

class MongoManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        # Guard check: MONGO_URI harus sudah divalidasi oleh config.py
        # Jika None, berarti config.py belum di-import atau validasi gagal
        if not config.MONGO_URI:
            raise RuntimeError(
                "MongoDB URI is not configured. "
                "Please ensure MONGO_URI is set in your environment before importing this module."
            )
        
        self.uri = config.MONGO_URI
        self.db_name = config.MONGO_DB_NAME
        self.collection_name = config.MONGO_COLLECTION_NAME
        self.client = None
        self.db = None
        self.trades_collection = None
        
        self.connect()
        self._initialized = True

    def connect(self):
        """Establishes connection to MongoDB."""
        try:
            # Set shorter timeout for initial connection check
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            
            # Trigger connection check
            self.client.admin.command('ping')
            
            self.db = self.client[self.db_name]
            self.trades_collection = self.db[self.collection_name]
            
            # Ensure indexes
            self._setup_indexes()
            
            logger.info(f"✅ MongoDB Connected: {self.db_name}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ MongoDB Connection Failed: {e}")
            return False
    def reload_config(self):
        """Reload konfigurasi MongoDB dari config.py dan switch collection jika berubah."""
        try:
            global config
            import importlib
            if "src.config" in sys.modules:
                import src.config
                config = importlib.reload(src.config)
            elif "config" in sys.modules:
                import config
                config = importlib.reload(config)
            
            new_db_name = getattr(config, 'MONGO_DB_NAME', self.db_name)
            new_collection_name = getattr(config, 'MONGO_COLLECTION_NAME', self.collection_name)
            
            if new_db_name != self.db_name and self.client:
                self.db_name = new_db_name
                self.db = self.client[self.db_name]
                logger.info(f"🔄 MongoDB DB Name switched to: {self.db_name}")
                
            if new_collection_name != self.collection_name:
                self.switch_collection(new_collection_name)
        except Exception as e:
            logger.warning(f"⚠️ Failed to reload MongoManager config: {e}")

    def switch_collection(self, collection_name: str) -> bool:
        """Mengganti target trades_collection secara dinamis."""
        if not collection_name or not isinstance(collection_name, str):
            return False
        
        clean_name = collection_name.strip()
        
        # Guard: Jika nama collection sama dan trades_collection sudah aktif, lewati
        if self.collection_name == clean_name and self.trades_collection is not None:
            return True

        try:
            self.collection_name = clean_name
            if self.db is not None:
                self.trades_collection = self.db[self.collection_name]
                self._setup_indexes()
                logger.info(f"🔄 MongoDB Collection switched to: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to switch MongoDB collection: {e}")
            return False

    def get_available_trade_collections(self) -> list:
        """Mengambil daftar semua collection di database MongoDB saat ini."""
        try:
            if self.db is None:
                if not self.connect():
                    return [self.collection_name]
            all_cols = self.db.list_collection_names()
            if self.collection_name not in all_cols:
                all_cols.append(self.collection_name)
            return sorted(list(set(all_cols)))
        except Exception as e:
            logger.warning(f"⚠️ Failed to list MongoDB collections: {e}")
            return [self.collection_name]

    def _setup_indexes(self):
        """Setup standard indexes for performance."""
        try:
            # Index on symbol (for filtering by coin)
            self.trades_collection.create_index([("symbol", ASCENDING)])
            
            # Index on timestamp (for date range filtering and sorting)
            self.trades_collection.create_index([("timestamp", DESCENDING)])
            
            # Index on strategy_tag (for strategy performance analysis)
            self.trades_collection.create_index([("strategy_tag", ASCENDING)])
            
            # Index on exit_type (for exit type analysis)
            self.trades_collection.create_index([("exit_type", ASCENDING)])
            
            logger.info("✅ MongoDB Indexes Verified")
        except Exception as e:
            logger.warning(f"⚠️ Failed to create indexes: {e}")

    def insert_trade(self, trade_data: dict) -> bool:
        """
        Inserts a single trade document.
        """
        try:
            if self.db is None:
                if not self.connect():
                    return False
            
            doc = dict(trade_data)
            result = self.trades_collection.insert_one(doc)
            return result.acknowledged
        except Exception as e:
            logger.error(f"❌ Failed to insert trade to MongoDB: {e}")
            return False

    ALLOWED_FILTER_FIELDS = frozenset({
        'timestamp', 'symbol', 'side', 'type',
        'entry_price', 'exit_price', 'size_usdt',
        'pnl_usdt', 'pnl_percent', 'roi_percent',
        'fee', 'strategy_tag', 'result',
        'prompt', 'reason', 'setup_at', 'filled_at',
        'exit_type', 'sl_price_initial'
    })

    ALLOWED_SORT_FIELDS = frozenset({
        'timestamp', 'symbol', 'side', 'type',
        'entry_price', 'exit_price', 'size_usdt',
        'pnl_usdt', 'pnl_percent', 'roi_percent',
        'fee', 'strategy_tag', 'result',
        'exit_type'
    })

    SAFE_VALUE_OPERATORS = frozenset({
        '$gt', '$gte', '$lt', '$lte', '$ne', '$eq', '$in', '$nin', '$exists'
    })

    DANGEROUS_OPERATORS = frozenset({
        '$where', '$function', '$expr', '$text', '$search', '$meta',
        '$near', '$nearSphere', '$geometry', '$maxDistance', '$minDistance',
        '$all', '$elemMatch', '$not', '$or', '$and', '$nor', '$regex',
        '$options', '$slice', '$size'
    })

    @staticmethod
    def _sanitize_filter_query(filter_query: dict) -> dict:
        if not filter_query:
            return {}
        sanitized = {}
        for key, value in filter_query.items():
            if str(key).startswith('$'):
                logger.warning(f"⚠️ Rejected MongoDB root operator in filter: {key}")
                continue
            if key not in MongoManager.ALLOWED_FILTER_FIELDS:
                logger.warning(f"⚠️ Rejected unknown field in filter: {key}")
                continue
            if isinstance(value, dict):
                valid_dict = {}
                is_safe = True
                for op, op_val in value.items():
                    if str(op).startswith('$'):
                        if op not in MongoManager.SAFE_VALUE_OPERATORS or op in MongoManager.DANGEROUS_OPERATORS:
                            logger.warning(f"⚠️ Rejected MongoDB operator in filter value: {op}")
                            is_safe = False
                            break
                        valid_dict[op] = op_val
                    else:
                        valid_dict[op] = op_val
                if is_safe:
                    sanitized[key] = valid_dict
            else:
                sanitized[key] = value
        return sanitized

    @staticmethod
    def _sanitize_sort_field(sort_by: str) -> str:
        if sort_by not in MongoManager.ALLOWED_SORT_FIELDS:
            logger.warning(f"⚠️ Rejected unknown sort field: {sort_by}, using 'timestamp'")
            return 'timestamp'
        return sort_by

    def get_trades(self, filter_query: dict = {}, sort_by: str = "timestamp", ascending: bool = False, limit: int = 0):
        """
        Retrieves trades based on filter.
        """
        try:
            if self.db is None:
                if not self.connect():
                    return []
            
            sanitized_filter = self._sanitize_filter_query(filter_query)
            sanitized_sort = self._sanitize_sort_field(sort_by)
            
            direction = ASCENDING if ascending else DESCENDING
            cursor = self.trades_collection.find(sanitized_filter).sort(sanitized_sort, direction)
            
            if limit > 0:
                cursor = cursor.limit(limit)
                
            return list(cursor)
        except Exception as e:
            logger.error(f"❌ Failed to fetch trades from MongoDB: {e}")
            return []

    def get_trade_count(self, filter_query: dict = {}) -> int:
        """Count trades matching filter."""
        try:
            if self.db is None:
                return 0
            sanitized_filter = self._sanitize_filter_query(filter_query)
            return self.trades_collection.count_documents(sanitized_filter)
        except Exception as e:
            logger.error(f"❌ Error counting trades: {e}")
            return 0

    # =========================================================================
    # AI EVALUATIONS COLLECTION
    # =========================================================================
    def insert_ai_evaluation(self, eval_data: dict) -> bool:
        """Insert single AI market evaluation record."""
        try:
            if self.db is None:
                if not self.connect():
                    return False
            col = self.db['ai_evaluations']
            doc = dict(eval_data)
            res = col.insert_one(doc)
            return res.acknowledged
        except Exception as e:
            logger.error(f"❌ Failed to insert AI evaluation: {e}")
            return False

    def get_ai_evaluations(self, filter_query: dict = {}, limit: int = 100, skip: int = 0) -> list:
        """Get AI evaluation records with sorting by timestamp DESC."""
        try:
            if self.db is None:
                if not self.connect():
                    return []
            col = self.db['ai_evaluations']
            cursor = col.find(filter_query).sort("timestamp", DESCENDING).skip(skip)
            if limit > 0:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"❌ Failed to fetch AI evaluations: {e}")
            return []

    def get_ai_evaluation_count(self, filter_query: dict = {}) -> int:
        """Count AI evaluation records matching query."""
        try:
            if self.db is None:
                if not self.connect():
                    return 0
            col = self.db['ai_evaluations']
            return col.count_documents(filter_query)
        except Exception as e:
            logger.error(f"❌ Error counting AI evaluations: {e}")
            return 0
