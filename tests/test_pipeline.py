import json

import pandas as pd

from smart_data_cleaner.pipeline import clean_file


def test_clean_file_pipeline(tmp_path):
    input_path = tmp_path / "input.csv"
    output_path = tmp_path / "output" / "cleaned.csv"

    # Create a dirty input dataset
    dataframe = pd.DataFrame(
        {
            "name": [" Alice ", "Bob", None],
            "age": [21, 25, None],
            "empty": [None, None, None],
        }
    )

    dataframe.to_csv(input_path, index=False)

    # Run the complete pipeline
    stats = clean_file(
        input_path,
        output_path,
        drop_duplicates=True,
    )

    # Check output file
    assert output_path.exists()

    cleaned = pd.read_csv(output_path)

    assert len(cleaned) == 2
    assert "empty" not in cleaned.columns
    assert cleaned.loc[0, "name"] == "Alice"

    # Check JSON report
    report_path = output_path.with_name("cleaned_report.json")

    assert report_path.exists()

    with report_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    assert report["original_rows"] == 3
    assert report["final_rows"] == 2
    assert report["empty_columns_removed"] == 1

    # Check returned statistics
    assert stats["final_rows"] == 2
