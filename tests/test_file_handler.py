import pandas as pd
import pytest

from smart_data_cleaner.file_handler import read_file, write_file


def test_csv_round_trip(tmp_path):

    original = pd.DataFrame({"name": ["Alice", "Bob"], "age": [21, 25]})

    path = tmp_path / "output" / "data.csv"

    write_file(original, path)
    result = read_file(path)

    pd.testing.assert_frame_equal(original, result)


def test_excel_round_trip(tmp_path):

    original = pd.DataFrame({"name": ["Alice", "Bob"], "age": [21, 25]})

    path = tmp_path / "output" / "data.xlsx"

    write_file(original, path)
    result = read_file(path)

    pd.testing.assert_frame_equal(original, result)


def test_missing_file_raises_error(tmp_path):

    path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        read_file(path)


def test_unsupported_extension_raises_error(tmp_path):

    path = tmp_path / "data.txt"
    path.write_text("hello", encoding="utf-8")

    with pytest.raises(ValueError):
        read_file(path)


def test_write_unsupported_extension_raises_error(tmp_path):
    dataframe = pd.DataFrame({"name": ["Alice"]})
    path = tmp_path / "data.txt"

    with pytest.raises(ValueError, match="Unsupported output format"):
        write_file(dataframe, path)


def test_write_non_dataframe_raises_error(tmp_path):
    path = tmp_path / "data.csv"

    with pytest.raises(TypeError, match="Input must be a pandas DataFrame"):
        write_file([1, 2, 3], path)


def test_read_csv_with_utf8_bom(tmp_path):
    path = tmp_path / "persian.csv"
    path.write_text(
        "\ufeffname\nعرفان\n",
        encoding="utf-8",
    )

    result = read_file(path)

    assert result.columns.tolist() == ["name"]
    assert result.iloc[0]["name"] == "عرفان"


def test_write_excel_creates_parent_directories(tmp_path):
    dataframe = pd.DataFrame({"name": ["Alice"]})
    path = tmp_path / "nested" / "folder" / "data.xlsx"

    write_file(dataframe, path)

    assert path.exists()
    pd.testing.assert_frame_equal(dataframe, read_file(path))


def test_read_unsupported_extension_raises_error(tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("hello", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported input format"):
        read_file(path)
