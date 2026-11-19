import argparse
import sys

from smart_data_cleaner.pipeline import clean_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Clean CSV and Excel files automatically."
    )

    parser.add_argument(
        "input",
        help="Path to the input CSV or Excel file.",
    )

    parser.add_argument(
        "output",
        help="Path where the cleaned file will be saved.",
    )

    parser.add_argument(
        "--drop-duplicates",
        action="store_true",
        help="Remove duplicate rows.",
    )

    parser.add_argument(
        "--missing-strategy",
        choices=["preserve", "drop", "fill"],
        default="preserve",
        help="How to handle missing values.",
    )

    parser.add_argument(
        "--fill-method",
        choices=["mean", "median", "mode"],
        help="Fill method applied to all columns.",
    )

    parser.add_argument(
        "--fill-column",
        action="append",
        metavar="COLUMN=METHOD",
        help="Set a fill method for a specific column. Can be used multiple times.",
    )

    return parser


def parse_fill_columns(values: list[str] | None) -> dict[str, str]:
    fill_methods = {}

    if not values:
        return fill_methods

    for value in values:
        if "=" not in value:
            raise ValueError(
                f"Invalid fill-column format: {value}. Expected COLUMN=METHOD."
            )

        column, method = value.split("=", 1)

        column = column.strip()
        method = method.strip().lower()

        if not column:
            raise ValueError("Column name cannot be empty.")

        if method not in {"mean", "median", "mode"}:
            raise ValueError(f"Invalid fill method: {method}")

        if column in fill_methods:
            raise ValueError(f"Duplicate fill column: {column}")

        fill_methods[column] = method

    return fill_methods


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        fill_methods = parse_fill_columns(args.fill_column)

        if args.missing_strategy == "fill":
            if args.fill_method and fill_methods:
                parser.error("Use either --fill-method or --fill-column, not both.")

            if args.fill_method:
                fill_methods = args.fill_method

            elif not fill_methods:
                parser.error("Fill strategy requires --fill-method or --fill-column.")

        else:
            if args.fill_method or fill_methods:
                parser.error(
                    "--fill-method and --fill-column require --missing-strategy fill."
                )

            fill_methods = None

        stats = clean_file(
            args.input,
            args.output,
            drop_duplicates=args.drop_duplicates,
            missing_strategy=args.missing_strategy,
            fill_methods=fill_methods,
        )

    except (FileNotFoundError, ValueError, TypeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print("\nCleaning completed successfully!")
    print(f"Original rows: {stats['original_rows']}")
    print(f"Final rows: {stats['final_rows']}")
    print(f"Removed empty rows: {stats['empty_rows_removed']}")
    print(f"Removed missing rows: {stats['missing_rows_removed']}")
    print(f"Removed empty columns: {stats['empty_columns_removed']}")
    print(f"Removed duplicates: {stats['duplicate_rows_removed']}")
    print(f"Whitespace cells trimmed: {stats['whitespace_cells_trimmed']}")
    print(f"Total missing values: {stats['total_missing_values']}")
    print(f"Missing values filled: {stats['missing_values_filled']}")
    print(f"Remaining missing values: {stats['remaining_missing_values']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
