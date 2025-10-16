#!/usr/bin/env python3
"""
Quick Quizizz CSV Converter
Converts Quizizz detailed format to simple name/score format for PTCC
"""
import pandas as pd
import sys
import re

def extract_real_name(full_name):
    """Extract real name from 'Nickname (Real Name)' format"""
    match = re.search(r'\(([^)]+)\)', full_name)
    if match:
        return match.group(1).strip()
    return full_name.strip()

def convert_quizizz_csv(input_file, output_file):
    """Convert Quizizz detailed CSV to simple format"""
    # Read the CSV
    df = pd.read_csv(input_file)
    
    # Find the summary row (contains overall percentages)
    # It's typically the row where Question column is empty but has percentage data
    summary_row = None
    for idx in range(len(df) - 1, max(len(df) - 10, -1), -1):
        row = df.iloc[idx]
        # Check if this row has percentage-like data
        # Look for rows with mostly percentage strings
        pct_count = sum(1 for val in row if isinstance(val, str) and '%' in val)
        if pct_count > 5:  # If more than 5 columns have percentage values
            summary_row = row
            print(f"Found summary row at index {idx}")
            break
    
    if summary_row is None:
        print("❌ Could not find summary row with percentages")
        return None
    
    last_row = summary_row
    
    # Student columns start after the metadata columns
    # Look for columns that contain percentage values
    student_data = []
    
    # Metadata column names to skip
    skip_keywords = ['#', 'Question', 'Standards', 'Accuracy', 'Time', 'Correct', 
                     'Yet to be graded', 'Partially correct', 'Incorrect', 
                     'Ungraded', 'Unattempted', 'Average']
    
    for col_name in df.columns:
        # Skip empty column names
        if not col_name or pd.isna(col_name):
            continue
        
        # Skip metadata columns
        if any(keyword in str(col_name) for keyword in skip_keywords):
            continue
        
        # Student columns should have spaces (names) or parentheses
        if ' ' not in str(col_name) and '(' not in str(col_name):
            continue
        
        # Get score from last row
        score_value = last_row[col_name]
        
        # Check if this looks like a percentage
        if pd.notna(score_value) and isinstance(score_value, (int, float, str)):
            try:
                # Handle percentage strings like "94%"
                if isinstance(score_value, str) and '%' in score_value:
                    percentage = float(score_value.replace('%', ''))
                elif isinstance(score_value, (int, float)):
                    percentage = float(score_value)
                else:
                    continue
                
                # Extract real name
                real_name = extract_real_name(col_name)
                
                student_data.append({
                    'Student Name': real_name,
                    'Percentage': percentage
                })
            except (ValueError, TypeError):
                continue
    
    # Create new DataFrame
    result_df = pd.DataFrame(student_data)
    
    # Save to CSV
    result_df.to_csv(output_file, index=False)
    
    print(f"✅ Converted {len(student_data)} students")
    print(f"📁 Saved to: {output_file}")
    print(f"\nSample data:")
    print(result_df.head())
    
    return result_df

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_quizizz.py <input_quizizz.csv> [output.csv]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "converted_quiz.csv"
    
    convert_quizizz_csv(input_file, output_file)
