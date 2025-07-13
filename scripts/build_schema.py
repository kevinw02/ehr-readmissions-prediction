"""
Dynamic DB Schema Builder Script

This script executes one or more SQL files sequentially to build or update a database schema.

- By default, it runs SQL files in the 'model/' and 'load/' subdirectories of --sql-dir.
- You can override the list via the `--sql-paths` argument, which accepts files or directories.
- The `--sql-dir` flag sets the root directory where SQL files and folders are located.
- The database connection configuration is loaded from a YAML file via `--config-path`.
- Progress and warnings are logged via Python's logging module.

Usage examples:
    python build_schema.py
    python build_schema.py --sql-paths model/ load/
    python build_schema.py --sql-paths model/encounter_dim.sql

Note: Ensure the feature store schema is built after required dimension tables are created.
"""

import argparse
import logging
import os
import yaml
from db.connection import create_db_connection

# CONSTANTS
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_DIR = os.path.join(SCRIPT_DIR, "..", "data_model", "sql")
DEFAULT_SQL_FILES = [
    "model",
    "load/dimension.sql",
    "load/readmission.sql",
]

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


def _arg_parse():
    parser = argparse.ArgumentParser(
        description="Build DB schema by executing SQL files in order."
    )
    parser.add_argument(
        "--config-path",
        type=str,
        default="data/duckdb_config.yaml",
        help="Path to db YAML configuration file.",
    )
    parser.add_argument(
        "--sql-dir",
        type=str,
        default=SQL_DIR,
        help="Base directory prepended to SQL file paths.",
    )
    parser.add_argument(
        "--sql-paths",
        nargs="+",
        required=False,
        default=DEFAULT_SQL_FILES,
        help=(
            "List of SQL files or directories (relative to sql-dir) to execute in order. "
            "Directories will be recursively searched for .sql files."
        ),
    )
    return parser.parse_args()


def _get_sql_files(base_dir, paths):
    """
    Given a list of files or directories relative to base_dir,
    return a list of absolute SQL file paths with the order of paths preserved.
    Directories expand to sorted lists of contained .sql files.
    """
    sql_files = []
    for path in paths:
        abs_path = os.path.join(base_dir, path)

        if os.path.isdir(abs_path):
            # Get sorted .sql files inside directory
            dir_files = [
                os.path.join(abs_path, f)
                for f in sorted(os.listdir(abs_path))
                if f.endswith(".sql") and os.path.isfile(os.path.join(abs_path, f))
            ]
            sql_files.extend(dir_files)
        elif os.path.isfile(abs_path) and abs_path.endswith(".sql"):
            sql_files.append(abs_path)
        else:
            _LOGGER.warning(f"Skipping invalid or non-SQL path: {abs_path}")
    return sql_files


def _execute_sql_files(conn, sql_files):
    for sql_file in sql_files:
        if not os.path.isfile(sql_file):
            _LOGGER.warning(f"SQL file {sql_file} does not exist. Skipping.")
            continue
        _LOGGER.info(f"Executing {sql_file} ...")
        conn.execute_file(sql_file, ddl=True)
    _LOGGER.info(f"✅ Successfully executed {len(sql_files)} SQL files.")


if __name__ == "__main__":
    args = _arg_parse()

    # Create db connection
    with open(args.config_path) as f:
        config = yaml.safe_load(f)
    conn = create_db_connection(config)

    # Find and execute sql files
    sql_files = _get_sql_files(args.sql_dir, args.sql_paths)
    _execute_sql_files(conn, sql_files)
