from python_calamine import CalamineWorkbook
from typing import List
from datetime import datetime
from models.sheet_headers import SheetHeaders, ExcelHeaderResult

class ExcelHeaderExtractor:
    """Extracts headers from Excel files, intelligently detecting and merging multiple header rows"""
    
    def extract_headers(self, file_path: str) -> ExcelHeaderResult:
        """Extract all headers from all sheets in an Excel file"""
        workbook = CalamineWorkbook.from_path(file_path)
        
        result = ExcelHeaderResult(file_path=file_path)
        
        for sheet_name in workbook.sheet_names:
            sheet_headers = self._extract_sheet_headers(workbook, sheet_name)
            result.sheets.append(sheet_headers)
        
        return result
    
    def _extract_sheet_headers(self, workbook: CalamineWorkbook, sheet_name: str) -> SheetHeaders:
        """Extract headers from a single worksheet, detecting multiple header rows"""
        sheet_headers = SheetHeaders(sheet_name=sheet_name)
        
        # Load sheet data as list of rows
        data = workbook.get_sheet_by_name(sheet_name).to_python()
        
        if not data or len(data) == 0:
            return sheet_headers  # Empty sheet
        
        max_cols = max(len(row) for row in data) if data else 0
        if max_cols == 0:
            return sheet_headers
        
        header_row_count = self._detect_header_row_count(data, max_cols)
        sheet_headers.header_row_count = header_row_count
        
        for col_idx in range(max_cols):
            merged_header = self._build_merged_header(data, header_row_count, col_idx)
            
            if merged_header.strip():
                sheet_headers.headers.append(merged_header)
        
        return sheet_headers
    
    def _detect_header_row_count(self, data: List[List], max_cols: int) -> int:
        """
        Detect how many rows contain header information
        Uses heuristics: looks for rows with text values followed by numeric data
        """
        max_header_rows = min(5, len(data))
        data_start_row = 1
        
        for row_idx in range(max_header_rows):
            if row_idx >= len(data):
                break
                
            row = data[row_idx]
            has_numeric_data = False
            has_text_data = False
            non_empty_cells = 0
            
            for col_idx in range(max_cols):
                value = row[col_idx] if col_idx < len(row) else None
                
                if value is not None:
                    non_empty_cells += 1
                    
                    if self._is_numeric_value(value):
                        has_numeric_data = True
                    elif isinstance(value, str) and value.strip():
                        has_text_data = True
            
            # If we find a row with mostly numeric data, headers end before this row
            if has_numeric_data and non_empty_cells > max_cols * 0.3:
                data_start_row = row_idx + 1
                break
            
            # If row is mostly text, it's likely a header row
            if has_text_data and non_empty_cells > 0:
                data_start_row = row_idx + 2
        
        return max(1, data_start_row - 1)
    
    def _build_merged_header(self, data: List[List], header_row_count: int, col_idx: int) -> str:
        """
        Build a merged header string from multiple header rows
        Example: Row1: "%DM", Row2: "Maize DM" -> "%DM Maize DM"
        Note: python-calamine doesn't handle merged cells the same way as openpyxl,
        so we simply concatenate values from header rows
        """
        header_parts = []
        
        for row_idx in range(header_row_count):
            if row_idx >= len(data):
                break
                
            row = data[row_idx]
            value = row[col_idx] if col_idx < len(row) else None
            
            if value is not None:
                text = str(value).strip()
                if text:
                    header_parts.append(text)
        
        return " ".join(header_parts)
    
    def _is_numeric_value(self, value) -> bool:
        """Check if a value is numeric (int, float, datetime treated as numeric data)"""
        return isinstance(value, (int, float, datetime))
