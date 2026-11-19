from pathlib import Path

import pandas as pd

SUPPORTED_INPUT = {".csv", ".xlsx"}
SUPPORTED_OUTPUT = {".csv", ".xlsx"}


def read_file(file_path: str | Path) -> pd.DataFrame:
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = file_path.suffix.lower()

    if suffix not in SUPPORTED_INPUT:
        raise ValueError(f"Unsupported input format: {suffix}")

    if suffix == ".csv":
        return pd.read_csv(file_path, encoding="utf-8-sig")

    if suffix == ".xlsx":
        return pd.read_excel(file_path, engine="openpyxl")

    raise ValueError(f"Unsupported input format: {suffix}")


def write_file(dataframe: pd.DataFrame, file_path: str | Path) -> None:

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    file_path = Path(file_path)
    suffix = file_path.suffix.lower()

    if suffix not in SUPPORTED_OUTPUT:
        raise ValueError(f"Unsupported output format: {suffix}")

    file_path.parent.mkdir(parents=True, exist_ok=True)

    if suffix == ".csv":
        dataframe.to_csv(file_path, index=False, encoding="utf-8-sig")

    elif suffix == ".xlsx":
        dataframe.to_excel(file_path, index=False, engine="openpyxl")
