import pytest
import pandas as pd

from db.connection import DuckDBConnection, create_db_connection


def test_connection_context_manager():
    with DuckDBConnection() as conn:
        assert conn._conn is not None
    # Should be closed after context
    assert conn._conn is None


def test_manual_connection_and_close():
    conn = DuckDBConnection()
    assert conn._conn is None
    conn.connect()
    assert conn._conn is not None
    conn.close()
    assert conn._conn is None


def test_execute_select(db):
    db.execute("CREATE TABLE test (id INTEGER, name TEXT);", ddl=True)
    db.execute("INSERT INTO test VALUES (1, 'Alice'), (2, 'Bob');", ddl=True)
    df = db.execute("SELECT * FROM test;")
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)
    assert list(df.columns) == ["id", "name"]


def test_execute_ddl_returns_none(db):
    result = db.execute("CREATE TABLE x (id INTEGER);", ddl=True)
    assert result is None


def test_execute_file(tmp_path):
    sql_file = tmp_path / "schema.sql"
    sql_file.write_text(
        """
        CREATE TABLE test (id INTEGER);
        INSERT INTO test VALUES (1), (2);
        SELECT * FROM test;
    """
    )

    conn = DuckDBConnection()
    result = conn.execute_file(str(sql_file))
    assert isinstance(result, pd.DataFrame)
    assert result.shape[0] == 2


def test_create_db_connection_valid():
    config = {"db_type": "duckdb", "database": ":memory:"}
    conn = create_db_connection(config)
    assert isinstance(conn, DuckDBConnection)


def test_create_db_connection_invalid():
    config = {"db_type": "unknown"}
    with pytest.raises(ValueError, match="Unsupported database type"):
        create_db_connection(config)
