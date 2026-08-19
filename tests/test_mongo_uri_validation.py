#!/usr/bin/env python3
"""
Test untuk validasi MONGO_URI configuration.

Test ini memastikan:
1. Validasi gagal jika MONGO_URI tidak di-set
2. Validasi gagal jika MONGO_URI memiliki format invalid
3. Validasi berhasil jika MONGO_URI valid
"""

import os
import sys
import unittest
from unittest.mock import patch

# Tambahkan root ke path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src import config


class TestMongoURIValidation(unittest.TestCase):
    """Test suite untuk MONGO_URI validation."""
    
    def test_missing_mongo_uri_raises_error(self):
        """Test: Validasi tanpa MONGO_URI harus raise ValueError."""
        with patch.object(config, 'MONGO_URI', None):
            with self.assertRaises(ValueError) as context:
                config._validate_mongo_uri()
            self.assertIn("MONGO_URI environment variable must be set", str(context.exception))
    
    def test_invalid_mongo_uri_scheme_raises_error(self):
        """Test: MONGO_URI dengan scheme invalid harus raise ValueError."""
        with patch.object(config, 'MONGO_URI', 'http://localhost:27017/'):
            with self.assertRaises(ValueError) as context:
                config._validate_mongo_uri()
            self.assertIn("must use mongodb:// or mongodb+srv://", str(context.exception))
    
    def test_mongo_uri_without_hostname_raises_error(self):
        """Test: MONGO_URI tanpa hostname harus raise ValueError."""
        with patch.object(config, 'MONGO_URI', 'mongodb://'):
            with self.assertRaises(ValueError) as context:
                config._validate_mongo_uri()
            self.assertIn("must include a hostname", str(context.exception))
    
    def test_valid_mongo_uri_localhost(self):
        """Test: MONGO_URI valid dengan localhost harus berhasil."""
        with patch.object(config, 'MONGO_URI', 'mongodb://localhost:27017/'):
            try:
                config._validate_mongo_uri()
            except ValueError as e:
                self.fail(f"_validate_mongo_uri dengan MONGO_URI valid tidak boleh raise exception: {e}")
    
    def test_valid_mongo_uri_with_auth(self):
        """Test: MONGO_URI valid dengan autentikasi harus berhasil."""
        with patch.object(config, 'MONGO_URI', 'mongodb://user:pass@mongodb.example.com:27017/dbname'):
            try:
                config._validate_mongo_uri()
            except ValueError as e:
                self.fail(f"_validate_mongo_uri dengan MONGO_URI valid tidak boleh raise exception: {e}")
    
    def test_valid_mongo_uri_srv(self):
        """Test: MONGO_URI valid dengan mongodb+srv harus berhasil."""
        with patch.object(config, 'MONGO_URI', 'mongodb+srv://user:pass@cluster.mongodb.net/dbname'):
            try:
                config._validate_mongo_uri()
            except ValueError as e:
                self.fail(f"_validate_mongo_uri dengan MONGO_URI valid tidak boleh raise exception: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
