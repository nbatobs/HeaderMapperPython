# Header Mapper - Python Version

A Python tool that reads Excel files and maps their headers to canonical schema columns using exact matching, alias matching, and fuzzy matching algorithms.

## Features

- **Multi-sheet Excel Support**: Processes all sheets in an Excel file
- **Intelligent Header Detection**: Automatically detects and merges multi-row headers
- **Three-Layer Matching**:
  1. Exact match to canonical names
  2. Alias matching from predefined aliases
  3. Fuzzy matching using RapidFuzz for approximate matches
- **Confidence-Based Recommendations**: Provides action recommendations (Auto-map, Review, Manual)
- **JSON Output**: Returns results in structured JSON format with detailed statistics
- **High Performance**: Uses RapidFuzz for fast fuzzy string matching

## Project Structure

```
HeaderMapperPython/
├── src/
│   └── header_mapper/
│       ├── __init__.py
│       ├── main.py                    # Main script entry point
│       ├── enums/                     # Enum definitions
│       │   ├── __init__.py
│       │   ├── header_match_type.py
│       │   └── mapping_action.py
│       ├── models/                    # Data models
│       │   ├── __init__.py
│       │   ├── column_schema.py
│       │   ├── mapping_result.py
│       │   ├── matching_config.py
│       │   └── sheet_headers.py
│       ├── services/                  # Business logic services
│       │   ├── __init__.py
│       │   ├── schema_loader.py
│       │   ├── excel_header_extractor.py
│       │   └── header_matcher.py
│       └── aliases/                   # Schema alias JSON files
│           ├── feeding-data-alias.json
│           ├── production-data-alias.json
│           ├── stirrer-data-alias.json
│           └── tank-data-alias.json
├── run.py                             # Convenience runner script
├── pyproject.toml                     # Poetry configuration
├── requirements.txt                   # Python dependencies
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
          "canonicalColumn": "date",
          "confidence": 1.0,
          "recommendedAction": "AutoMap"
        },
        {
          "userColumn": "Feeding Maize",
          "canonicalColumn": "feeding_site_maize_t",
          "confidence": 0.95,
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
    fuzzy_min_threshold=65  # Minimum fuzzy match score (0-100)
)
```

### Matching Thresholds

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

- **Python**: ^3.9
- **openpyxl**: >=3.1.2 - Excel file reading and writing
- **rapidfuzz**: >=3.0.0 - Fast fuzzy string matching

## Schema Files

The tool includes four predefined schema files in the `src/header_mapper/aliases/` directory:
- `feeding-data-alias.json` - Feeding and substrate data schema
- `production-data-alias.json` - Biogas production metrics schema
- `stirrer-data-alias.json` - Mixer/stirrer performance data schema
- `tank-data-alias.json` - Digester tank parameters schema

Each schema file follows this format:

```json
{
  "columnKey": {
    "canonicalName": "column_name",
    "description": "Description of the column",
    "dataType": "string",
    "required": true,
    "exampleValues": ["example1", "example2"],
    "aliases": ["alias1", "alias2", "alias 3"]
  }
}
```

## How It Works

1. **Schema Loading**: Loads all canonical column definitions from JSON files
2. **Header Extraction**: Reads Excel file and detects header rows (handles multi-row headers)
3. **Three-Layer Matching**:
   - **Exact Match** (100% confidence): Direct match to canonical name
   - **Alias Match** (95% confidence): Match to predefined aliases
   - **Fuzzy Match** (variable confidence): Uses RapidFuzz for similar strings
4. **Action Recommendation**: Based on confidence and field requirements
5. **JSON Output**: Saves detailed mapping results with statistics

## Notes

- The tool looks for the `aliases` directory in `src/header_mapper/aliases/`
- All output is in JSON format for easy integration with other tools
- Handles merged cells and multi-row headers automatically
- Output file is saved in the same directory as the input Excel file
