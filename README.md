# Header Mapper - Python Version

A Python script that reads Excel files and maps their headers to canonical schema columns using exact matching, alias matching, and fuzzy matching algorithms.

## Features

- **Multi-sheet Excel Support**: Processes all sheets in an Excel file
- **Intelligent Header Detection**: Automatically detects and merges multi-row headers
- **Three-Layer Matching**:
  1. Exact match to canonical names
  2. Alias matching from predefined aliases
  3. Fuzzy matching using RapidFuzz for approximate matches
- **Confidence-Based Recommendations**: Provides action recommendations (Auto-map, Review, Manual)
- **JSON Output**: Returns results in structured JSON format
- **High Performance**: Uses Rust-based libraries for fast Excel reading and fuzzy matching

## Project Structure

```
HeaderMapperPython/
├── src/
│   └── header_mapper/
│       ├── __init__.py
│       ├── main.py            # Main script entry point
│       ├── enums/             # Enum definitions
│       │   ├── __init__.py
│       │   ├── header_match_type.py
│       │   └── mapping_action.py
│       ├── models/            # Data models
│       │   ├── __init__.py
│       │   ├── column_schema.py
│       │   ├── mapping_result.py
│       │   ├── matching_config.py
│       │   └── sheet_headers.py
│       ├── services/          # Business logic services
│       │   ├── __init__.py
│       │   ├── schema_loader.py
│       │   ├── excel_header_extractor.py
│       │   └── header_matcher.py
│       └── aliases/           # Schema alias files
├── run.py                     # Convenience runner script
├── pyproject.toml             # Poetry configuration
├── requirements.txt           # Python dependencies
└── README.md
```

## Installation

### Using Poetry (Recommended)

1. Navigate to the HeaderMapperPython directory:
```bash
cd HeaderMapperPython
```

2. Install dependencies using Poetry:
```bash
poetry install
```

### Using pip

Alternatively, you can install dependencies directly with pip:
```bash
pip install -r requirements.txt
```

## Usage

### Using Poetry (Recommended)

**Option 1: Using the entry point (cleanest):**
```bash
poetry run header-mapper path/to/your/file.xlsx
```

**Option 2: Using the convenience script:**
```bash
poetry run python run.py path/to/your/file.xlsx
```

**Option 3: Using the module directly:**
```bash
poetry run python -m header_mapper.main path/to/your/file.xlsx
```

### Using Python directly

```bash
python run.py path/to/your/file.xlsx
```

The script will:
1. Load all canonical schemas from the `aliases` directory
2. Extract headers from all sheets in the Excel file
3. Match each header to canonical columns
4. Output the results as JSON

### Example Output

```json
{
  "file_path": "data.xlsx",
  "sheets": [
    {
      "sheet_name": "Sheet1",
      "header_row_count": 2,
      "total_columns": 10,
      "mappings": [
        {
          "userColumn": "Date Time",
          "canonicalColumn": "DateTime",
          "confidence": 1.0,
          "matchType": "ExactMatch",
          "matchDetails": "Exact match to canonical name",
          "recommendedAction": "AutoMap"
        }
      ],
      "summary": {
        "auto_mapped": 8,
        "needs_review": 1,
        "needs_manual": 1,
        "auto_mapped_percentage": 80.0,
        "needs_review_percentage": 10.0,
        "needs_manual_percentage": 10.0
      }
    }
  ],
  "overall_summary": {
    "total_sheets": 1,
    "total_headers": 10,
    "total_auto_mapped": 8,
    "total_needs_review": 1,
    "total_needs_manual": 1
  }
}
```

## Configuration

The matching behavior can be configured in the `main.py` file:

```python
config = MatchingConfig(
    fuzzy_min_threshold=20  # Minimum fuzzy match score (0-100)
)
```

Thresholds for different actions:
- **Required fields**:
  - Auto-map: ≥ 90% confidence
  - Review: ≥ 75% confidence
  - Manual: < 75% confidence
- **Optional fields**:
  - Auto-map: ≥ 85% confidence
  - Review: ≥ 70% confidence
  - Manual: < 70% confidence

## Dependencies

Modern, high-performance packages (2025):
- **python-calamine**: Rust-based Excel reader for massive speed improvements
- **rapidfuzz**: Fast fuzzy string matching with better licensing and performance

## Schema Files

The script expects JSON schema files in the `aliases` directory (located in the same folder as the script). Schema files should follow this format:

```json
{
  "columnKey": {
    "canonicalName": "ColumnName",
    "description": "Description of the column",
    "dataType": "string",
    "required": true,
    "exampleValues": ["example1", "example2"],
    "aliases": ["alias1", "alias2"]
  }
}
```

## Notes

- The script looks for the `aliases` directory in the same folder as `main.py`
- All output is in JSON format for easy integration with other tools
- The script maintains the same logic and functionality as the C# version
