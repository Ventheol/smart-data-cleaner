
import json
from pathlib import Path


def save_report(stats: dict, output_path: str | Path) -> None:
    """
    Save cleaning statistics as a JSON report.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            stats,
            file,
            indent=4,
            ensure_ascii=False
        )
