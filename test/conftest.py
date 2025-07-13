import numpy as np
import pandas as pd
import pytest
from db.connection import DuckDBConnection


@pytest.fixture
def db():
    with DuckDBConnection() as conn:
        yield conn


@pytest.fixture
def setup_test_table(db):
    schema = "main"
    table = "sample"
    db.execute(
        f"""
        CREATE TABLE {schema}.{table} (
            id INTEGER,
            value TEXT
        );
    """,
        ddl=True,
    )
    db.execute(
        f"""
        INSERT INTO {schema}.{table} VALUES (1, 'a'), (2, 'b'), (3, 'c');
    """,
        ddl=True,
    )
    return schema, table


@pytest.fixture
def setup_dimension_table(db):
    schema = "dimension"  # Assuming this matches c.Schema.DIMENSION
    table = "test_dim"
    key_col = "dim_key"
    label_col = "description"
    # Create schema if needed (DuckDB uses "main" as default schema usually)
    # Create table
    db.execute(
        f"""
        CREATE SCHEMA dimension;
        CREATE TABLE {schema}.{table} (
            {key_col} INTEGER,
            {label_col} TEXT
        );
    """,
        ddl=True,
    )

    # Insert sample data
    db.execute(
        f"""
        INSERT INTO {schema}.{table} VALUES
        (1, 'Alpha'),
        (2, 'Beta'),
        (3, 'Gamma');
    """,
        ddl=True,
    )

    return schema, table, key_col, label_col


@pytest.fixture
def synthetic_data():
    # 100 samples, 5 features
    X_train = pd.DataFrame(np.random.randn(100, 5), columns=[f"f{i}" for i in range(5)])
    y_train = np.random.randint(0, 2, 100)
    X_test = pd.DataFrame(np.random.randn(40, 5), columns=[f"f{i}" for i in range(5)])
    y_test = np.random.randint(0, 2, 40)
    return X_train, y_train, X_test, y_test
