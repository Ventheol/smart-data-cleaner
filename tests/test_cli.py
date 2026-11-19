import pytest

from smart_data_cleaner.cli import (
    build_parser,
    main,
    parse_fill_columns,
)


def test_cli_default_missing_strategy():
    parser = build_parser()

    args = parser.parse_args(["input.csv", "output.csv"])

    assert args.missing_strategy == "preserve"


def test_parse_fill_columns():
    result = parse_fill_columns(
        [
            "age=median",
            "city=mode",
            "salary=mean",
        ]
    )

    assert result == {
        "age": "median",
        "city": "mode",
        "salary": "mean",
    }


def test_cli_fill_method_argument():
    parser = build_parser()

    args = parser.parse_args(
        [
            "input.csv",
            "output.csv",
            "--missing-strategy",
            "fill",
            "--fill-method",
            "mode",
        ]
    )

    assert args.missing_strategy == "fill"
    assert args.fill_method == "mode"


def test_parse_fill_columns_invalid_format():
    with pytest.raises(ValueError, match="Invalid fill-column format"):
        parse_fill_columns(["age-median"])


def test_parse_fill_columns_empty_column():
    with pytest.raises(ValueError, match="Column name cannot be empty"):
        parse_fill_columns(["=median"])


def test_parse_fill_columns_invalid_method():
    with pytest.raises(ValueError, match="Invalid fill method"):
        parse_fill_columns(["age=average"])


def test_parse_fill_columns_duplicate_column():
    with pytest.raises(ValueError, match="Duplicate fill column"):
        parse_fill_columns(["age=mean", "age=median"])


def test_cli_success(monkeypatch, capsys):
    def fake_clean_file(input_path, output_path, **kwargs):
        assert input_path == "input.csv"
        assert output_path == "output.csv"
        assert kwargs["missing_strategy"] == "preserve"

        return {
            "original_rows": 100,
            "final_rows": 95,
            "empty_rows_removed": 2,
            "missing_rows_removed": 3,
            "empty_columns_removed": 1,
            "duplicate_rows_removed": 4,
            "whitespace_cells_trimmed": 2,
            "total_missing_values": 15,
            "missing_values_filled": 10,
            "remaining_missing_values": 5,
        }

    monkeypatch.setattr(
        "smart_data_cleaner.cli.clean_file",
        fake_clean_file,
    )
    monkeypatch.setattr(
        "sys.argv",
        ["cli.py", "input.csv", "output.csv"],
    )

    result = main()

    captured = capsys.readouterr()

    assert result == 0
    assert "Cleaning completed successfully!" in captured.out
    assert "Original rows: 100" in captured.out
    assert "Remaining missing values: 5" in captured.out


def test_cli_file_not_found(monkeypatch, capsys):
    def fake_clean_file(*args, **kwargs):
        raise FileNotFoundError("Input file not found")

    monkeypatch.setattr(
        "smart_data_cleaner.cli.clean_file",
        fake_clean_file,
    )
    monkeypatch.setattr(
        "sys.argv",
        ["cli.py", "missing.csv", "output.csv"],
    )

    result = main()

    captured = capsys.readouterr()

    assert result == 1
    assert "Input file not found" in captured.err


def test_cli_fill_without_method(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "cli.py",
            "input.csv",
            "output.csv",
            "--missing-strategy",
            "fill",
        ],
    )

    with pytest.raises(SystemExit) as error:
        main()

    assert error.value.code == 2


def test_cli_rejects_both_fill_options(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "cli.py",
            "input.csv",
            "output.csv",
            "--missing-strategy",
            "fill",
            "--fill-method",
            "mean",
            "--fill-column",
            "age=median",
        ],
    )

    with pytest.raises(SystemExit) as error:
        main()

    assert error.value.code == 2


def test_cli_rejects_fill_options_without_fill_strategy(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "cli.py",
            "input.csv",
            "output.csv",
            "--fill-method",
            "mean",
        ],
    )

    with pytest.raises(SystemExit) as error:
        main()

    assert error.value.code == 2


def test_cli_accepts_multiple_fill_columns(monkeypatch, capsys):
    def fake_clean_file(input_path, output_path, **kwargs):
        assert kwargs["fill_methods"] == {
            "age": "median",
            "city": "mode",
        }

        return {
            "original_rows": 10,
            "final_rows": 10,
            "empty_rows_removed": 0,
            "missing_rows_removed": 0,
            "empty_columns_removed": 0,
            "duplicate_rows_removed": 0,
            "missing_values_filled": 3,
            "remaining_missing_values": 0,
            "whitespace_cells_trimmed": 0,
            "total_missing_values": 3,
        }

    monkeypatch.setattr(
        "smart_data_cleaner.cli.clean_file",
        fake_clean_file,
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "cli.py",
            "input.csv",
            "output.csv",
            "--missing-strategy",
            "fill",
            "--fill-column",
            "age=median",
            "--fill-column",
            "city=mode",
        ],
    )

    result = main()

    assert result == 0
