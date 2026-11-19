import json

from smart_data_cleaner.reporter import save_report


def test_save_report(tmp_path):

    stats = {"original_rows": 100, "final_rows": 80, "duplicate_rows_removed": 20}

    output = tmp_path / "reports" / "report.json"

    save_report(stats, output)

    assert output.exists()

    with output.open("r", encoding="utf-8") as file:
        result = json.load(file)

    assert result["original_rows"] == 100
    assert result["final_rows"] == 80
    assert result["duplicate_rows_removed"] == 20
