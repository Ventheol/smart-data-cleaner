import pandas as pd
import pytest

from smart_data_cleaner.cleaner import clean_dataframe


def test_clean_dataframe():

    data = pd.DataFrame(
        {
            "name": [" Alice ", "Bob", None],
            "age": [21, 25, None],
            "empty": [None, None, None],
        }
    )

    result, stats = clean_dataframe(data)

    assert list(result.columns) == ["name", "age"]
    assert len(result) == 2
    assert result.iloc[0]["name"] == "Alice"
    assert stats["empty_rows_removed"] == 1
    assert stats["empty_columns_removed"] == 1


def test_remove_duplicates():

    data = pd.DataFrame({"name": ["Alice", "Alice", "Bob"], "age": [21, 21, 25]})

    result, stats = clean_dataframe(data, drop_duplicates=True)

    assert len(result) == 2
    assert stats["duplicate_rows_removed"] == 1


def test_keep_duplicates_by_default():

    data = pd.DataFrame({"name": ["Alice", "Alice"]})

    result, stats = clean_dataframe(data)

    assert len(result) == 2
    assert stats["duplicate_rows_removed"] == 0


def test_missing_values_statistics():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", None, "Charlie"],
            "age": [21, None, None],
            "city": ["London", "Paris", None],
        }
    )

    cleaned, stats = clean_dataframe(dataframe)

    assert stats["total_missing_values"] == 4

    assert stats["missing_values_per_column"] == {
        "name": 1,
        "age": 2,
        "city": 1,
    }

    assert cleaned.isna().sum().sum() == 4


def test_missing_values_are_not_counted_as_whitespace():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", None, "Bob"],
            "age": [21, None, 25],
        }
    )

    cleaned, stats = clean_dataframe(dataframe)

    assert stats["whitespace_cells_trimmed"] == 0
    assert stats["total_missing_values"] == 2


def test_preserve_missing_values():
    dataframe = pd.DataFrame(
        {
            "age": [20, None, 40],
            "city": ["London", "Paris", "Tokyo"],
        }
    )

    cleaned, stats = clean_dataframe(dataframe)

    assert cleaned["age"].isna().sum() == 1
    assert stats["missing_strategy"] == "preserve"
    assert stats["remaining_missing_values"] == 1


def test_drop_missing_rows():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", None, "Charlie"],
            "age": [20, 30, None],
        }
    )

    cleaned, stats = clean_dataframe(
        dataframe,
        missing_strategy="drop",
    )

    assert len(cleaned) == 1
    assert stats["missing_rows_removed"] == 2
    assert stats["remaining_missing_values"] == 0


def test_fill_mean():
    dataframe = pd.DataFrame(
        {
            "age": [20.0, None, 40.0],
        }
    )

    cleaned, stats = clean_dataframe(
        dataframe,
        missing_strategy="fill",
        fill_methods={"age": "mean"},
    )

    assert cleaned.loc[1, "age"] == 30.0
    assert stats["missing_values_filled"] == 1
    assert stats["remaining_missing_values"] == 0


def test_fill_median():
    dataframe = pd.DataFrame(
        {
            "age": [20.0, None, 40.0, 100.0],
        }
    )

    cleaned, stats = clean_dataframe(
        dataframe,
        missing_strategy="fill",
        fill_methods={"age": "median"},
    )

    assert cleaned.loc[1, "age"] == 40.0
    assert stats["missing_values_filled"] == 1


def test_fill_mode():
    dataframe = pd.DataFrame(
        {
            "city": ["London", None, "Paris", "London"],
        }
    )

    cleaned, stats = clean_dataframe(
        dataframe,
        missing_strategy="fill",
        fill_methods={"city": "mode"},
    )

    assert cleaned.loc[1, "city"] == "London"
    assert stats["missing_values_filled"] == 1


def test_fill_rejects_mean_for_text_column():
    dataframe = pd.DataFrame(
        {
            "city": ["London", None, "Paris"],
        }
    )

    with pytest.raises(TypeError):
        clean_dataframe(
            dataframe,
            missing_strategy="fill",
            fill_methods={"city": "mean"},
        )


def test_fill_rejects_entirely_empty_column():
    dataframe = pd.DataFrame(
        {
            "age": [None, None, None],
        }
    )

    with pytest.raises(ValueError, match="Cannot calculate"):
        clean_dataframe(
            dataframe,
            missing_strategy="fill",
            fill_methods="mean",
        )


def test_fill_counts_only_actually_filled_values():
    dataframe = pd.DataFrame(
        {
            "age": [20, None, 40, None],
        }
    )

    cleaned, stats = clean_dataframe(
        dataframe,
        missing_strategy="fill",
        fill_methods="mean",
    )

    assert stats["missing_values_filled"] == 2
    assert stats["remaining_missing_values"] == 0
    assert cleaned["age"].isna().sum() == 0


def test_drop_and_empty_rows_statistics():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", None, None, "Bob"],
            "age": [21, 30, None, 25],
        }
    )

    cleaned, stats = clean_dataframe(
        dataframe,
        missing_strategy="drop",
    )

    assert stats["missing_rows_removed"] == 2
    assert stats["empty_rows_removed"] == 0
    assert len(cleaned) == 2


def test_fill_only_selected_columns():
    dataframe = pd.DataFrame(
        {
            "age": [20, None, 40],
            "salary": [1000, None, 3000],
        }
    )

    cleaned, stats = clean_dataframe(
        dataframe,
        missing_strategy="fill",
        fill_methods={"age": "mean"},
    )

    assert cleaned["age"].isna().sum() == 0
    assert cleaned["salary"].isna().sum() == 1
    assert stats["missing_values_filled"] == 1
    assert stats["remaining_missing_values"] == 1


def test_fill_rejects_entirely_empty_column_with_mode():
    dataframe = pd.DataFrame(
        {
            "city": [None, None, None],
        }
    )

    with pytest.raises(ValueError, match="Cannot calculate"):
        clean_dataframe(
            dataframe,
            missing_strategy="fill",
            fill_methods="mode",
        )


def test_rejects_non_dataframe_input():
    with pytest.raises(TypeError, match="Input must be a pandas DataFrame"):
        clean_dataframe([1, 2, 3])


def test_rejects_invalid_missing_strategy():
    dataframe = pd.DataFrame({"age": [20, 30]})

    with pytest.raises(ValueError, match="Invalid missing strategy"):
        clean_dataframe(dataframe, missing_strategy="average")


def test_fill_requires_fill_methods():
    dataframe = pd.DataFrame({"age": [20, None, 40]})

    with pytest.raises(ValueError, match="fill_methods is required"):
        clean_dataframe(dataframe, missing_strategy="fill")


def test_fill_rejects_invalid_fill_methods_type():
    dataframe = pd.DataFrame({"age": [20, None, 40]})

    with pytest.raises(TypeError, match="fill_methods must be a dictionary or string"):
        clean_dataframe(
            dataframe,
            missing_strategy="fill",
            fill_methods=["mean"],
        )


def test_fill_rejects_unknown_column():
    dataframe = pd.DataFrame({"age": [20, None, 40]})

    with pytest.raises(ValueError, match="Unknown column"):
        clean_dataframe(
            dataframe,
            missing_strategy="fill",
            fill_methods={"salary": "mean"},
        )


def test_fill_rejects_invalid_method():
    dataframe = pd.DataFrame({"age": [20, None, 40]})

    with pytest.raises(ValueError, match="Invalid fill method"):
        clean_dataframe(
            dataframe,
            missing_strategy="fill",
            fill_methods={"age": "average"},
        )


def test_fill_rejects_median_for_text_column():
    dataframe = pd.DataFrame({"city": ["London", None, "Paris"]})

    with pytest.raises(TypeError, match="Median requires numeric column"):
        clean_dataframe(
            dataframe,
            missing_strategy="fill",
            fill_methods={"city": "median"},
        )


def test_drop_removes_completely_empty_rows():
    dataframe = pd.DataFrame(
        {
            "name": ["Alice", None, "Bob"],
            "age": [20, None, 30],
        }
    )

    cleaned, stats = clean_dataframe(
        dataframe,
        missing_strategy="drop",
    )

    assert len(cleaned) == 2
    assert stats["missing_rows_removed"] == 1
    assert stats["empty_rows_removed"] == 0


def test_trim_whitespace_in_string_columns():
    dataframe = pd.DataFrame(
        {
            "name": [" Alice ", "Bob ", " Charlie"],
            "age": [20, 30, 40],
        }
    )

    cleaned, stats = clean_dataframe(dataframe)

    assert cleaned["name"].tolist() == ["Alice", "Bob", "Charlie"]
    assert stats["whitespace_cells_trimmed"] == 3


def test_preserve_non_string_values_in_object_column():
    dataframe = pd.DataFrame(
        {
            "mixed": [" Alice ", 123, None],
            "other": ["x", "y", "z"],
        }
    )

    cleaned, stats = clean_dataframe(dataframe)

    assert cleaned["mixed"].iloc[0] == "Alice"
    assert cleaned["mixed"].iloc[1] == 123
    assert pd.isna(cleaned["mixed"].iloc[2])
    assert stats["whitespace_cells_trimmed"] == 1
