from pathlib import Path

from smart_data_cleaner.cleaner import clean_dataframe
from smart_data_cleaner.file_handler import read_file, write_file
from smart_data_cleaner.reporter import save_report


def clean_file(
    input_path: str | Path,
    output_path: str | Path,
    *,
    drop_duplicates: bool = False,
    missing_strategy: str = "preserve",
    fill_methods: dict | str | None = None,
) -> dict:
    input_path = Path(input_path)
    output_path = Path(output_path)

    # Read input file
    dataframe = read_file(input_path)

    # Clean data
    cleaned_dataframe, stats = clean_dataframe(
        dataframe,
        drop_duplicates=drop_duplicates,
        missing_strategy=missing_strategy,
        fill_methods=fill_methods,
    )

    # Save cleaned file
    write_file(cleaned_dataframe, output_path)

    # Save cleaning report
    report_path = output_path.with_name(f"{output_path.stem}_report.json")
    save_report(stats, report_path)

    return stats
