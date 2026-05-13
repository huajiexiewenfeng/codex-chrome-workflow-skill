#!/usr/bin/env python3
"""Extract monthly task rows from Excel work-plan files.

This script is intentionally configurable so the public repository does not
need to contain private project names, employee IDs, or local paths.
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
from pathlib import Path
from typing import Any

import openpyxl


DEFAULT_COLUMNS = {
    "sequence": "序号",
    "task_name": "任务名称",
    "task_type": "任务类型",
    "start_date": "计划开始日期",
    "end_date": "计划完成日期",
    "estimate": "估计工作量",
    "owner": "责任人",
    "reviewer": "审核人",
    "participants": "参与人",
    "description": "任务描述",
    "acceptance": "验收标准",
    "status": "完成情况",
}

DEFAULT_PLANNING_MARKERS = ["下周计划", "下周任务", "后续计划", "后续任务"]


def parse_date(value: Any) -> dt.date | None:
    if value is None:
        return None
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    text = str(value).strip()
    match = re.search(r"(20\d{2})[-/](\d{1,2})[-/](\d{1,2})", text)
    if not match:
        return None
    year, month, day = map(int, match.groups())
    try:
        return dt.date(year, month, day)
    except ValueError:
        return None


def as_json_value(value: Any) -> Any:
    if isinstance(value, (dt.datetime, dt.date)):
        return str(value)
    return value


def normalize_name(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip())


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def find_header(data: list[tuple[Any, ...]], columns: dict[str, str]) -> tuple[int, dict[str, int]] | None:
    required = {columns["task_name"], columns["start_date"], columns["end_date"]}
    for row_index, row in enumerate(data[:15]):
        values = [str(cell).strip() if cell is not None else "" for cell in row]
        if columns["task_name"] not in values:
            continue
        if not (columns["start_date"] in values or columns["end_date"] in values):
            continue
        indexes = {key: values.index(title) for key, title in columns.items() if title in values}
        if required.intersection(values):
            return row_index, indexes
    return None


def extract(pattern: str, year: int, month: int, columns: dict[str, str], planning_markers: list[str]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    task_names: list[str] = []
    seen_names: set[str] = set()

    for file_path in sorted(glob.glob(pattern)):
        try:
            workbook = openpyxl.load_workbook(file_path, data_only=True, read_only=True)
        except Exception as exc:
            rows.append({"file": os.path.basename(file_path), "error": str(exc)})
            continue

        try:
            for sheet in workbook.worksheets:
                data = list(sheet.iter_rows(values_only=True))
                header = find_header(data, columns)
                if header is None:
                    continue

                header_index, indexes = header
                in_planning_block = False

                for row in data[header_index + 1 :]:
                    if not row or all(cell is None for cell in row):
                        continue

                    name_index = indexes.get("task_name")
                    if name_index is None or name_index >= len(row):
                        continue

                    raw_name = row[name_index]
                    if raw_name is None:
                        continue

                    task_name = normalize_name(raw_name)
                    if not task_name:
                        continue

                    if task_name in planning_markers:
                        in_planning_block = True
                        continue

                    start_index = indexes.get("start_date")
                    end_index = indexes.get("end_date")
                    start_date = parse_date(row[start_index]) if start_index is not None and start_index < len(row) else None
                    end_date = parse_date(row[end_index]) if end_index is not None and end_index < len(row) else None
                    in_month = (
                        (start_date is not None and start_date.year == year and start_date.month == month)
                        or (end_date is not None and end_date.year == year and end_date.month == month)
                    )
                    if not in_month:
                        continue

                    item: dict[str, Any] = {
                        "file": os.path.basename(file_path),
                        "sheet": sheet.title,
                        "planning_block": in_planning_block,
                    }
                    for key, column in indexes.items():
                        if column < len(row):
                            item[key] = as_json_value(row[column])
                    rows.append(item)

                    if in_planning_block:
                        continue

                    if task_name not in seen_names:
                        seen_names.add(task_name)
                        task_names.append(task_name)
        finally:
            workbook.close()

    return {
        "year": year,
        "month": month,
        "pattern": pattern,
        "count": len(task_names),
        "task_names": task_names,
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract monthly task names from Excel work plans.")
    parser.add_argument("--month", type=int, required=True, help="Month number, 1-12.")
    parser.add_argument("--year", type=int, default=None, help="Year. Defaults to config default_year or current year.")
    parser.add_argument("--pattern", default=None, help="Excel glob pattern. Overrides config excel_pattern.")
    parser.add_argument("--config", default=str(Path(__file__).resolve().parents[1] / "config.json"), help="Config path.")
    args = parser.parse_args()

    if not 1 <= args.month <= 12:
        raise SystemExit("--month must be between 1 and 12")

    config = load_config(Path(args.config))
    columns = DEFAULT_COLUMNS | config.get("columns", {})
    planning_markers = list(config.get("planning_markers", DEFAULT_PLANNING_MARKERS))
    year = args.year or int(config.get("default_year", dt.date.today().year))
    pattern = args.pattern or str(config.get("excel_pattern", ""))
    if not pattern:
        raise SystemExit("Missing Excel pattern. Set excel_pattern in config.json or pass --pattern.")

    print(json.dumps(extract(pattern, year, args.month, columns, planning_markers), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

