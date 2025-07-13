"""
CSV Loader

This script loads CSV files from a specified directory into db tables
based on a YAML configuration file.

Generally used to load CSV files into a staging schema.
"""

import argparse
import glob
import logging
import os
import sys
import yaml
from db.connection import create_db_connection

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,  # Set minimum level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def _arg_parse():
    """
    Creates and returns an argparse.Namespace with parsed command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments with 'config_path' and 'csv_dir' attributes.
    """
    parser = argparse.ArgumentParser(
        description="Load CSV files into db tables using a YAML config."
    )
    parser.add_argument(
        "--config_path",
        type=str,
        default="data/duckdb_config.yaml",
        help="Path to db YAML configuration file.",
    )
    parser.add_argument(
        "--csv_dir",
        type=str,
        default="data/csv",
        help="Directory containing CSV files to load.",
    )
    parser.add_argument(
        "--schema", type=str, default="staging", help="Schema to populate."
    )
    return parser.parse_args()


def _load_csv_to_db(conn, csv_path, schema_name, table_name):
    """
    Loads a CSV file into a db table, replacing the table if it exists.

    params:
        conn: Database connection object.
        csv_path: Path to the CSV files to load.
        able_name: Name of the table to create or replace in the db.

    returns: None
    """
    logger.info(f"Loading {csv_path} into table {schema_name}.{table_name}...")
    conn.execute(
        f"""
        CREATE OR REPLACE TABLE {schema_name}.{table_name} AS
        SELECT * FROM read_csv_auto('{csv_path}')
    """,
        ddl=True,
    )
    logger.info(f"Loaded {table_name}")


if __name__ == "__main__":
    # Parse command-line arguments
    args = _arg_parse()
    config_path = args.config_path
    csv_dir = args.csv_dir
    schema_name = args.schema

    # Create db connection from YAML config
    with open(config_path) as f:
        config = yaml.safe_load(f)
    conn = create_db_connection(config)

    # Check if the CSV files exist
    csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
    if not csv_files:
        logger.info(f"No CSV files found in {csv_dir}")
        sys.exit(1)

    # Create schema if not exists
    create_schema = f"CREATE SCHEMA IF NOT EXISTS {schema_name}"
    conn.execute(create_schema, ddl=True)

    # Load CSV files from the specified directory
    for csv_file in csv_files:
        table_name = os.path.splitext(os.path.basename(csv_file))[0]
        _load_csv_to_db(conn, csv_file, schema_name=schema_name, table_name=table_name)
    logger.info("All files loaded!")
