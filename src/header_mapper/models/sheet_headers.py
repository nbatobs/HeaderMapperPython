from dataclasses import dataclass, field
from typing import List

@dataclass
class SheetHeaders:
    """Represents the headers extracted from a single Excel sheet"""
    sheet_name: str = ""
    headers: List[str] = field(default_factory=list)
    header_row_count: int = 0

@dataclass
class ExcelHeaderResult:
    """Represents the complete result of extracting headers from an Excel file"""
    file_path: str = ""
    sheets: List[SheetHeaders] = field(default_factory=list)
