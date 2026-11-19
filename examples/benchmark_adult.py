from pathlib import Path
from time import perf_counter

import pandas as pd

from smart_data_cleaner.cleaner import clean_dataframe
from smart_data_cleaner.file_handler import write_file
from smart_data_cleaner.reporter import save_report

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "examples" / "raw" / "adult"
OUTPUT_DIR = PROJECT_ROOT / "examples" / "cleaned" / "adult"

COLUMNS = [
    "age",
    "workclass",
    "fnlwgt",
    "education",
    "education_num",
    "marital_status",
    "occupation",
    "relationship",
    "race",
    "sex",
    "capital_gain",
    "capital_loss",
    "hours_per_week",
    "native_country",
    "income",
]


def run_benchmark(filename: str) -> None:
    input_path = RAW_DIR / filename

    if not input_path.exists():
        raise FileNotFoundError(f"Dataset not found: {input_path}")

    dataset_name = input_path.name.replace(".", "_")

    output_path = OUTPUT_DIR / f"{dataset_name}_cleaned.csv"
    report_path = OUTPUT_DIR / f"{dataset_name}_report.json"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    start_time = perf_counter()

    # Adult files have no column headers.
    # The test file also contains a comment line.
    dataframe = pd.read_csv(
        input_path,
        header=None,
        names=COLUMNS,
        skipinitialspace=True,
        na_values=["?"],
        comment="|",
    )
    whitespace_counts = {}

    for column in dataframe.columns:
        count = dataframe[column].map(
            lambda value: (
                isinstance(value, str)
                and value != value.strip()
            )
        ).sum()

        if count > 0:
            whitespace_counts[column] = int(count)

    print("\nWhitespace cells before cleaning:")

    for column, count in whitespace_counts.items():
        print(f"  {column}: {count:,}")

    print(
        "Total:",
        sum(whitespace_counts.values())
    )
    cleaned_dataframe, stats = clean_dataframe(dataframe)

    write_file(cleaned_dataframe, output_path)

    elapsed_time = perf_counter() - start_time

    # Add benchmark information to the cleaning report.
    stats["dataset"] = filename
    stats["execution_time_seconds"] = round(elapsed_time, 4)
    stats["input_size_bytes"] = input_path.stat().st_size
    stats["output_size_bytes"] = output_path.stat().st_size

    save_report(stats, report_path)

    print(f"\nBenchmark: {filename}")
    print("-" * 40)
    print(f"Original rows: {stats['original_rows']:,}")
    print(f"Final rows: {stats['final_rows']:,}")
    print(f"Original columns: {stats['original_columns']}")
    print(f"Final columns: {stats['final_columns']}")
    print(f"Empty rows removed: {stats['empty_rows_removed']}")
    print(f"Empty columns removed: {stats['empty_columns_removed']}")
    print(f"Whitespace cells trimmed: {stats['whitespace_cells_trimmed']}")
    print(f"Total missing values: {stats['total_missing_values']:,}")

    print("\nMissing values per column:")

    for column, count in stats["missing_values_per_column"].items():
        if count > 0:
            print(f"  {column}: {count:,}")
    print(f"Execution time: {elapsed_time:.4f} seconds")
    print(f"Input size: {stats['input_size_bytes']:,} bytes")
    print(f"Output size: {stats['output_size_bytes']:,} bytes")
    print(f"Cleaned file: {output_path}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    run_benchmark("adult.data")
    run_benchmark("adult.test")
