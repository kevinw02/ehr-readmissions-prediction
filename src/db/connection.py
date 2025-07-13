"""
Database connection module. Currently supports DuckDB.
"""

import duckdb
import pandas as pd
from abc import ABC, abstractmethod
from pathlib import Path


# Abstract base class for DB connections
class DBConnection(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def execute(self, query: str, params=None):
        pass


class DuckDBConnection(DBConnection):
    def __init__(self, database=":memory:", read_only=False):
        """
        params:
            database: Path to the DuckDB file or ':memory:'.
            read_only: Open DB in read-only mode if True.
        """
        self.database = database
        self._read_only = read_only
        self._conn = None

    def __enter__(self):
        self._conn = duckdb.connect(database=self.database, read_only=self._read_only)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            self._conn.close()
            self._conn = None

    def connect(self):
        # External use only (if you want to connect manually)
        if not self._conn:
            self._conn = duckdb.connect(
                database=self.database, read_only=self._read_only
            )
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def execute(
        self, query: str, params: dict | None = None, ddl: bool = False
    ) -> pd.DataFrame | None:
        params = {} if params is None else params

        if self._conn:
            result = self._conn.execute(query, params)
            return None if ddl else result.df()

        with duckdb.connect(
            database=self.database, read_only=self._read_only
        ) as temp_conn:
            result = temp_conn.execute(query, params)
            return None if ddl else result.df()

    def execute_file(
        self, filepath: str, params: dict | None = None, ddl: bool = False
    ) -> pd.DataFrame | None:
        sql = Path(filepath).read_text()
        return self.execute(sql, params=params, ddl=ddl)


# Factory function
def create_db_connection(config: dict) -> DBConnection:
    db_type = config.get("db_type", "").lower()
    if db_type == "duckdb":
        database = config.get("database", ":memory:")
        read_only = config.get("read_only", False)
        return DuckDBConnection(database=database, read_only=read_only)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
