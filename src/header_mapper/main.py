#!/usr/bin/env python3
"""
Header Mapper - Excel to Schema Matching
Reads an Excel file and maps headers to canonical schema columns
"""

import sys
import json
import os
from typing import List
from header_mapper.services.schema_loader import SchemaLoader
from header_mapper.services.excel_header_extractor import ExcelHeaderExtractor
from header_mapper.services.header_matcher import HeaderMatcher
from header_mapper.models.matching_config import MatchingConfig
from header_mapper.enums.mapping_action import MappingAction

def process_excel_file(file_path: str, matcher: HeaderMatcher) -> dict:
    """Process an Excel file and return the mapping results as a dictionary"""
    extractor = ExcelHeaderExtractor()
    excel_result = extractor.extract_headers(file_path)
    
    output = {
        "file_path": excel_result.file_path,
        "sheets": []
    }
    
    for sheet in excel_result.sheets:
        sheet_data = {
            "sheet_name": sheet.sheet_name,
            "header_row_count": sheet.header_row_count,
            "total_columns": len(sheet.headers),
            "mappings": []
        }
        
        auto_mapped = 0
        needs_review = 0
        needs_manual = 0
        
        # Match each header
        for header in sheet.headers:
            match = matcher.map_single_header(header)
            sheet_data["mappings"].append(match.to_dict())
            
            if match.recommended_action == MappingAction.AUTO_MAP:
                auto_mapped += 1
            elif match.recommended_action == MappingAction.REVIEW:
                needs_review += 1
            elif match.recommended_action == MappingAction.MANUAL_MAP:
                needs_manual += 1
        
        # Add summary statistics
        sheet_data["summary"] = {
            "auto_mapped": auto_mapped,
            "needs_review": needs_review,
            "needs_manual": needs_manual,
            "auto_mapped_percentage": round(auto_mapped / len(sheet.headers) * 100, 2) if sheet.headers else 0,
            "needs_review_percentage": round(needs_review / len(sheet.headers) * 100, 2) if sheet.headers else 0,
            "needs_manual_percentage": round(needs_manual / len(sheet.headers) * 100, 2) if sheet.headers else 0
        }
        
        output["sheets"].append(sheet_data)
    
    # Add overall summary
    total_headers = sum(len(sheet.headers) for sheet in excel_result.sheets)
    total_auto = sum(s["summary"]["auto_mapped"] for s in output["sheets"])
    total_review = sum(s["summary"]["needs_review"] for s in output["sheets"])
    total_manual = sum(s["summary"]["needs_manual"] for s in output["sheets"])
    
    output["overall_summary"] = {
        "total_sheets": len(excel_result.sheets),
        "total_headers": total_headers,
        "total_auto_mapped": total_auto,
        "total_needs_review": total_review,
        "total_needs_manual": total_manual
    }
    
    return output

def start():
    """Main entry point for the script"""
    print("═" * 55)
    print("  Header Mapper - Excel to Schema Matching")
    print("═" * 55)
    print()
    
    try:
        # 1. Load canonical schema
        schema_loader = SchemaLoader()
        
        # Aliases directory is in the same folder as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        aliases_dir = os.path.join(script_dir, "aliases")
        
        if not os.path.exists(aliases_dir):
            print("Error: 'aliases' directory not found")
            print(f"   Expected location: {aliases_dir}")
            sys.exit(1)
        
        schema = schema_loader.load_all_schemas(aliases_dir)
        print(f"Loaded {len(schema)} canonical columns from schema files\n")
        
        # 2. Configure matching
        config = MatchingConfig(
            fuzzy_min_threshold=20
        )
        matcher = HeaderMatcher(schema, config)
        
        # 3. Get Excel file path
        excel_file_path = None
        
        if len(sys.argv) > 1:
            excel_file_path = sys.argv[1]
        else:
            print("Usage: python main.py <path_to_excel_file>")
            print("\nExample:")
            print("  python main.py data.xlsx")
            sys.exit(1)
        
        # 4. Process Excel file
        if os.path.exists(excel_file_path):
            print(f"Processing Excel file: {os.path.basename(excel_file_path)}\n")
            
            result = process_excel_file(excel_file_path, matcher)
            
            # Generate output filename
            base_name = os.path.splitext(os.path.basename(excel_file_path))[0]
            output_filename = f"{base_name}_mapping_result.json"
            output_path = os.path.join(os.path.dirname(os.path.abspath(excel_file_path)), output_filename)
            
            # Write JSON to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"Done! Processed {result['overall_summary']['total_headers']} headers from {result['overall_summary']['total_sheets']} sheet(s)")
            print(f"Output saved to: {output_path}")
        else:
            print(f"File not found: {excel_file_path}")
            sys.exit(1)
    
    except Exception as ex:
        print(f" Error: {str(ex)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    start()
