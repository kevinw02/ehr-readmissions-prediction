from api.db_helpers import load_dimension_mapping  # Adjust this import


def test_load_dimension_mapping(db, setup_dimension_table):
    schema, table, key_col, label_col = setup_dimension_table

    result = load_dimension_mapping(
        db,
        table_name=table,
        key_col=key_col,
        label_col=label_col,
        schema_name=schema,
    )

    expected = {
        "alpha": 1,
        "beta": 2,
        "gamma": 3,
    }
    assert result == expected
