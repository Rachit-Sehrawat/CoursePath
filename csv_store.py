"""Shared, dependency-free CSV persistence for CoursePath."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Mapping

DATA_DIR = Path(__file__).resolve().parent / "data"
SCHEMAS = {
    "courses.csv": ["course_code", "course_name", "credits", "semester", "prerequisites"],
    "students.csv": ["student_id", "name", "program", "batch_section", "completed_courses"],
}


class CSVStore:
    """Reads and writes the shared CSV files; pipe separates list values."""
    def __init__(self, data_dir: Path | str = DATA_DIR):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def ensure_files(self) -> None:
        for filename, headers in SCHEMAS.items():
            path = self.data_dir / filename
            if not path.exists():
                with path.open("w", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerow(headers)

    def read(self, filename: str) -> list[dict[str, str]]:
        if filename not in SCHEMAS:
            raise ValueError(f"Unknown data file: {filename}")
        self.ensure_files()
        with (self.data_dir / filename).open("r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != SCHEMAS[filename]:
                raise ValueError(f"Unexpected columns in {filename}; expected {SCHEMAS[filename]}")
            return [{key: (value or "").strip() for key, value in row.items()} for row in reader]

    def write(self, filename: str, rows: Iterable[Mapping[str, object]]) -> None:
        if filename not in SCHEMAS:
            raise ValueError(f"Unknown data file: {filename}")
        self.ensure_files()
        path = self.data_dir / filename
        temp = path.with_suffix(path.suffix + ".tmp")
        with temp.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=SCHEMAS[filename], extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({key: row.get(key, "") for key in SCHEMAS[filename]})
        temp.replace(path)


def split_codes(value: str) -> list[str]:
    """Parse pipe-separated course codes, stripping whitespace and duplicates."""
    return list(dict.fromkeys(part.strip().upper() for part in value.split("|") if part.strip()))


def join_codes(codes: Iterable[str]) -> str:
    return "|".join(dict.fromkeys(str(code).strip().upper() for code in codes if str(code).strip()))
