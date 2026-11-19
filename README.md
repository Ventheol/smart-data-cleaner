# Smart Data Cleaner

[English](README.md) | [فارسی](README_FA.md)

A Python-based data cleaning tool for CSV and Excel files, built with Pandas.

Smart Data Cleaner automates common data preparation tasks, including handling missing values, removing duplicate rows, trimming whitespace, and generating JSON cleaning reports.

## Features

- **CSV and Excel support:** Read and write `.csv` and `.xlsx` files.
- **Missing value handling:** Preserve, drop, or fill missing values.
- **Multiple fill methods:** Mean, median, and mode.
- **Column-specific filling:** Apply different strategies to individual columns.
- **Duplicate removal:** Optionally remove duplicate rows.
- **Whitespace trimming:** Remove unnecessary leading and trailing whitespace from string values.
- **Automatic cleanup:** Remove completely empty rows and columns.
- **JSON reports:** Generate a report containing cleaning statistics.
- **Command-line interface:** Run cleaning operations directly from the terminal.

## Project Structure

```text
smart-data-cleaner/
├── examples/
│   ├── raw/
│   ├── cleaned/
│   └── benchmark_adult.py
├── src/
│   └── smart_data_cleaner/
│       ├── __init__.py
│       ├── cleaner.py
│       ├── cli.py
│       ├── file_handler.py
│       ├── pipeline.py
│       └── reporter.py
├── tests/
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── README.md
└── README_FA.md
```

## Requirements

- Python 3.10 or newer
- Pandas 2.0 or newer
- OpenPyXL 3.1 or newer

## Installation

Clone the repository:

```bash
git clone https://github.com/Ventheol/smart-data-cleaner.git
cd smart-data-cleaner
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On Linux / macOS:

```bash
source .venv/bin/activate
```

Install the project in editable mode:

```bash
python -m pip install -e .
```

To install development dependencies for running tests:

```bash
python -m pip install -e ".[dev]"
```

## Usage

After installation, the command-line tool is available as `smart-data-cleaner`.

Basic usage:

```bash
smart-data-cleaner input.csv output.csv
```

The same command works with Excel files:

```bash
smart-data-cleaner input.xlsx output.xlsx
```

You can also run the CLI as a Python module:

```bash
python -m smart_data_cleaner.cli input.csv output.csv
```

### Handling Missing Values

Smart Data Cleaner supports three missing-value strategies.

**1. Preserve (default)**

Keep missing values in partially populated rows and columns.

```bash
smart-data-cleaner input.csv output.csv
```

**2. Drop**

Remove rows containing missing values.

```bash
smart-data-cleaner input.csv output.csv --missing-strategy drop
```

**3. Fill**

Fill missing values using a selected statistical method.

Apply one method to all columns:

```bash
smart-data-cleaner input.csv output.csv --missing-strategy fill --fill-method mode
```

Apply different methods to specific columns:

```bash
smart-data-cleaner input.csv output.csv --missing-strategy fill --fill-column Age=median --fill-column Embarked=mode
```

Available fill methods:

| Method | Description |
|---|---|
| `mean` | Fill with the column mean |
| `median` | Fill with the column median |
| `mode` | Fill with the most frequent value |

Mean and median require numeric columns. The selected method must be compatible with the column's data type.

### Removing Duplicates

Use `--drop-duplicates` to remove duplicate rows:

```bash
smart-data-cleaner input.csv output.csv --drop-duplicates
```

Options can be combined:

```bash
smart-data-cleaner input.csv output.csv --missing-strategy drop --drop-duplicates
```

## Cleaning Reports

Every successful cleaning operation generates a JSON report next to the cleaned output file.

For example:

```text
output/
├── cleaned_data.csv
└── cleaned_data_report.json
```

The report includes:

- Original and final row counts
- Original and final column counts
- Removed empty rows and columns
- Removed duplicate rows
- Trimmed whitespace cells
- Original missing-value counts
- Filled missing values
- Remaining missing values
- Applied filling strategies

## Example: Titanic Dataset

The project includes a Titanic dataset example.

Fill missing ages using the median and missing embarkation ports using the mode:

```bash
smart-data-cleaner examples/raw/titanic/train.csv examples/cleaned/titanic/train_cleaned.csv --missing-strategy fill --fill-column Age=median --fill-column Embarked=mode
```

Observed results:

| Metric | Result |
|---|---:|
| Original rows | 891 |
| Final rows | 891 |
| Missing values filled | 179 |
| Remaining missing values | 687 |
| Removed duplicate rows | 0 |

The remaining missing values are primarily from the `Cabin` column, which is intentionally left unchanged.

## Adult Dataset Benchmark

The project also includes a benchmark script for the Adult dataset.

Run:

```bash
python examples/benchmark_adult.py
```

Observed results from the local benchmark:

| Dataset | Rows | Columns | Missing Values |
|---|---:|---:|---:|
| Adult training data | 32,561 | 15 | 4,262 |
| Adult test data | 16,281 | 15 | 2,203 |

These results demonstrate the tool's behavior on larger real-world tabular datasets. Execution times depend on the machine and environment.

## Running Tests

Install the development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run the test suite:

```bash
python -m pytest -v
```

Run tests with coverage:

```bash
python -m pytest --cov=smart_data_cleaner --cov-report=term-missing
```

The current development test suite contains **50 passing tests**. The project previously achieved **96% code coverage** in the local development environment.

## Limitations

- Currently supports CSV and XLSX files.
- Mean and median filling are limited to numeric columns.
- Filling an entirely empty column is not supported because no statistical fill value can be calculated.
- The tool focuses on general-purpose cleaning and does not automatically infer domain-specific data corrections.

## License

License information will be added when the project license is selected.

---

**Smart Data Cleaner** is a portfolio project focused on practical Python development, data processing, testing, and command-line tooling.