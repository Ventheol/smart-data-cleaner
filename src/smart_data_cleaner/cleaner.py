import pandas as pd


def clean_dataframe(
    dataframe: pd.DataFrame,
    *,
    drop_duplicates: bool = False,
    missing_strategy: str = "preserve",
    fill_methods: dict | str | None = None,
) -> tuple[pd.DataFrame, dict]:

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    valid_strategies = {"preserve", "drop", "fill"}

    if missing_strategy not in valid_strategies:
        raise ValueError(f"Invalid missing strategy: {missing_strategy}")

    if missing_strategy == "fill":
        if fill_methods is None:
            raise ValueError("fill_methods is required when using fill strategy")

        if isinstance(fill_methods, str):
            fill_methods = {column: fill_methods for column in dataframe.columns}

        if not isinstance(fill_methods, dict):
            raise TypeError("fill_methods must be a dictionary or string")

        valid_methods = {"mean", "median", "mode"}

        for column, method in fill_methods.items():
            if column not in dataframe.columns:
                raise ValueError(f"Unknown column in fill_methods: {column}")

            if method not in valid_methods:
                raise ValueError(f"Invalid fill method: {method}")

    df = dataframe.copy()

    original_rows = len(df)
    original_columns = len(df.columns)

    missing_values_per_column = df.isna().sum().to_dict()
    total_missing_values = int(df.isna().sum().sum())

    missing_values_filled = 0
    missing_rows_removed = 0
    applied_fill_methods = {}
    empty_rows_removed = 0
    # Handle missing values
    if missing_strategy == "drop":
        before = len(df)
        df = df.dropna()
        missing_rows_removed = before - len(df)

    elif missing_strategy == "fill":
        for column, method in fill_methods.items():
            missing_count = int(df[column].isna().sum())

            if missing_count == 0:
                continue
            if df[column].isna().all():
                raise ValueError(
                    f"Cannot calculate {method} for entirely empty column: {column}"
                )
            if method == "mean":
                if not pd.api.types.is_numeric_dtype(df[column]):
                    raise TypeError(f"Mean requires numeric column: {column}")

                fill_value = df[column].mean()

            elif method == "median":
                if not pd.api.types.is_numeric_dtype(df[column]):
                    raise TypeError(f"Median requires numeric column: {column}")

                fill_value = df[column].median()

            else:
                modes = df[column].mode(dropna=True)
                fill_value = modes.iloc[0]

            if pd.isna(fill_value):
                raise ValueError(
                    f"Cannot calculate {method} for column: {column}. "
                    "The column may contain no valid values."
                )

            df[column] = df[column].fillna(fill_value)

            actual_filled = missing_count - int(df[column].isna().sum())
            missing_values_filled += actual_filled

            if actual_filled > 0:
                applied_fill_methods[column] = method

    # Remove completely empty rows
    before = len(df)
    df = df.dropna(axis=0, how="all")
    empty_rows_removed = before - len(df)

    # Remove completely empty columns
    columns_before = len(df.columns)
    df = df.dropna(axis=1, how="all")
    empty_columns_removed = columns_before - len(df.columns)

    # Trim whitespace
    whitespace_cells_trimmed = 0

    for column in df.columns:
        if pd.api.types.is_object_dtype(df[column]) or pd.api.types.is_string_dtype(
            df[column]
        ):
            before = df[column].copy()

            trimmed = df[column].map(
                lambda value: value.strip() if isinstance(value, str) else value
            )

            changed_mask = before.map(
                lambda value: isinstance(value, str) and value != value.strip()
            )

            whitespace_cells_trimmed += int(changed_mask.sum())
            df[column] = trimmed

    # Remove duplicate rows
    duplicate_rows_removed = 0

    if drop_duplicates:
        before = len(df)
        df = df.drop_duplicates()
        duplicate_rows_removed = before - len(df)

    stats = {
        "original_rows": original_rows,
        "original_columns": original_columns,
        "final_rows": len(df),
        "final_columns": len(df.columns),
        "empty_rows_removed": empty_rows_removed,
        "empty_columns_removed": empty_columns_removed,
        "duplicate_rows_removed": duplicate_rows_removed,
        "whitespace_cells_trimmed": whitespace_cells_trimmed,
        "total_missing_values": total_missing_values,
        "missing_values_per_column": {
            str(column): int(count)
            for column, count in missing_values_per_column.items()
        },
        "missing_strategy": missing_strategy,
        "missing_rows_removed": missing_rows_removed,
        "missing_values_filled": missing_values_filled,
        "applied_fill_methods": applied_fill_methods,
        "remaining_missing_values": int(df.isna().sum().sum()),
    }

    return df, stats
