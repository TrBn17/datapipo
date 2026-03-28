from __future__ import annotations

from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET
from zipfile import ZipFile

XML_NS = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def resolve_input_path(project_root: Path, xlsx_path: Path) -> Path:
    if xlsx_path.is_absolute():
        return xlsx_path
    return project_root / xlsx_path


def load_workbook_rows(xlsx_path: Path) -> tuple[list[str], list[dict[str, Any]]]:
    with ZipFile(xlsx_path) as archive:
        headers = _load_headers(archive)
        rows = _load_rows(archive, headers)
    return headers, rows


def _load_shared_strings(archive: ZipFile) -> list[str]:
    try:
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return []

    shared_strings: list[str] = []
    for item in root.findall("main:si", XML_NS):
        text_node = item.find("main:t", XML_NS)
        if text_node is not None:
            shared_strings.append(text_node.text or "")
            continue

        runs = item.findall("main:r", XML_NS)
        shared_strings.append("".join(run.findtext("main:t", default="", namespaces=XML_NS) for run in runs))
    return shared_strings


def _load_headers(archive: ZipFile) -> list[str]:
    root = ET.fromstring(archive.read("xl/tables/table1.xml"))
    return [column.attrib["name"] for column in root.findall("main:tableColumns/main:tableColumn", XML_NS)]


def _cell_value(cell: ET.Element, shared_strings: list[str]) -> str | None:
    value = cell.findtext("main:v", default=None, namespaces=XML_NS)
    inline_string = cell.find("main:is/main:t", XML_NS)
    if inline_string is not None:
        return inline_string.text or ""

    if value in (None, ""):
        return None

    if cell.attrib.get("t") == "s":
        return shared_strings[int(value)]
    return value


def _column_letters(cell_reference: str) -> str:
    return "".join(character for character in cell_reference if character.isalpha())


def _excel_column_name(index: int) -> str:
    name = ""
    current = index
    while current > 0:
        current, remainder = divmod(current - 1, 26)
        name = chr(65 + remainder) + name
    return name


def _load_rows(archive: ZipFile, headers: list[str]) -> list[dict[str, Any]]:
    sheet_root = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    column_map = {_excel_column_name(index): header for index, header in enumerate(headers, start=1)}
    shared_strings = _load_shared_strings(archive)

    rows: list[dict[str, Any]] = []
    for row in sheet_root.findall("main:sheetData/main:row", XML_NS):
        if row.attrib.get("r") == "1":
            continue

        record = {header: None for header in headers}
        for cell in row.findall("main:c", XML_NS):
            header = column_map.get(_column_letters(cell.attrib["r"]))
            if header is None:
                continue
            record[header] = _cell_value(cell, shared_strings)

        rows.append(record)
    return rows
