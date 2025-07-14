import db.constant as c
from typing import Dict
from db.connection import DBConnection


def load_dimension_mapping(
    conn: DBConnection,
    table_name: str,
    key_col: str,
    label_col: str = c.Column.DESCRIPTION,
    schema_name: str = c.Schema.CLINICAL,
) -> Dict[str, int]:
    """
    Load a dimension mapping table from the database.

    Args:
        conn (DBConnection): Database connection object.
        table_name (str): Name of the dimension table.
        key_col (str): Column name for the key (integer).
        label_col (str): Column name for the label (string).

    Returns:
        Dict[str, int]: Mapping from label (lowercase) to key.
    """
    query = f"SELECT {label_col}, {key_col} FROM {schema_name}.{table_name}"
    df = conn.execute(query)
    return {row[label_col].lower(): row[key_col] for idx, row in df.iterrows()}
