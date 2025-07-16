"""
Data Validator - outputs report for visual inspection.

This script connects to the database and prints the total number of rows
and (by default) the first 2 rows of selected tables in a given schema.
"""

import argparse
import logging
import yaml
from db.connection import create_db_connection
from tabulate import tabulate


DEFAULT_TABLES = [
    "patients",
    "conditions",
    "medications",
    "procedures",
    "encounters",
]

_logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,  # Set minimum level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def _arg_parse():
    """
    Creates and returns an argparse.Namespace with parsed command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments with 'config_path', 'schema', and 'tables' attributes.
    """
    parser = argparse.ArgumentParser(
        description="Validate data in selected db tables by previewing sample rows."
    )
    parser.add_argument(
        "--config_path",
        type=str,
        default="data/duckdb_config.yaml",
        help="Path to db YAML configuration file.",
    )
    parser.add_argument(
        "--schema",
        type=str,
        default="staging",
        help="Schema where tables are located.",
    )
    parser.add_argument(
        "--tables",
        type=str,
        help="Comma-separated list of table names to check. Defaults to standard clinical tables.",
    )
    parser.add_argument(
        "--num-rows", type=str, default="2", help="Number of rows to display per table."
    )
    return parser.parse_args()


def _check_table_exists(conn, schema_name: str, table_name: str) -> bool:
    """
    Checks if a table exists in the specified schema.

    params:
        conn: Database connection object with an `execute` method.
        schema_name: Name of the schema.
        table_name: Name of the table to check.

    returns: True if the table exists, False otherwise.
    """
    query = f"""
    SELECT COUNT(*) 
    FROM duckdb_tables() 
    WHERE schema_name = '{schema_name}' AND table_name = '{table_name}';
    """

    try:
        return conn.execute(query).iloc[0, 0] > 0
    except Exception as e:
        _logger.info(f"❌ check_table_exists failed: {e}")
        return False


def _get_table_count(conn, schema_name: str, table_name: str) -> int:
    """
    Gets the total row count of a table in the specified schema.

    params:
        conn: Database connection object with an `execute` method.
        schema_name: Name of the schema.
        table_name: Name of the table.

    returns: Number of rows in the table.
    """
    query = f"""
    SELECT COUNT(*) 
    FROM {schema_name}.{table_name};
    """
    result = conn.execute(query).iloc[0, 0]
    return result


def _preview_table(conn, schema_name: str, table_name: str, limit: int):
    """
    Prints the first `limit` rows of a specified table.

    params:
        conn: Database connection object with an `execute` method.
        schema_name: Name of the schema.
        table_name: Name of the table.
        limit: Number of rows to preview.

    returns: None
    """
    query = f"SELECT * FROM {schema_name}.{table_name} LIMIT {limit}"
    _logger.info(f"\n📋 Previewing {schema_name}.{table_name}:")
    try:
        df = conn.execute(query)
        _logger.info(df)
    except Exception as e:
        _logger.info(f"❌ Error reading {table_name}: {e}")


if __name__ == "__main__":
    args = _arg_parse()
    config_path = args.config_path
    schema_name = args.schema
    num_rows = args.num_rows
    table_list = (
        [t.strip() for t in args.tables.split(",")] if args.tables else DEFAULT_TABLES
    )

    with open(config_path) as f:
        config = yaml.safe_load(f)
    conn = create_db_connection(config)

    validation_results = []

    for table_name in table_list:
        qualified_name = f"{schema_name}.{table_name}"
        exists = _check_table_exists(conn, schema_name, table_name)

        if exists:
            try:
                row_count = _get_table_count(conn, schema_name, table_name)
                _preview_table(conn, schema_name, table_name, limit=num_rows)
            except Exception as e:
                row_count = f"❌ Error: {e}"
        else:
            row_count = "--"

        validation_results.append(
            {
                "Table": qualified_name,
                "Exists": "✅" if exists else "❌",
                "Row Count": row_count,
            }
        )

    print("\n🧪 Validation Summary:")
    print(tabulate(validation_results, headers="keys", tablefmt="fancy_grid"))
