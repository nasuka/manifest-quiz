#!/usr/bin/env python3
"""
Script to concatenate all quiz CSV files into one combined file.
"""

import csv
import glob
from pathlib import Path
import argparse


def combine_quiz_csvs(input_pattern: str = "quiz_*.csv", output_file: str = "quiz_all_combined.csv", exclude_existing: bool = True):
    """
    Combine all quiz CSV files matching the pattern into one file.
    
    Args:
        input_pattern: Glob pattern to match quiz CSV files
        output_file: Output filename for the combined CSV
        exclude_existing: Whether to exclude the existing combined file from input
    """
    
    # Find all quiz CSV files
    csv_files = glob.glob(input_pattern)
    
    # Remove the output file from input files if it exists and exclude_existing is True
    if exclude_existing and output_file in csv_files:
        csv_files.remove(output_file)
    
    # Sort files for consistent ordering
    csv_files.sort()
    
    if not csv_files:
        print(f"No CSV files found matching pattern: {input_pattern}")
        return
    
    print(f"Found {len(csv_files)} quiz CSV files to combine:")
    for file in csv_files:
        print(f"  - {file}")
    
    # Combine all CSV files
    total_rows = 0
    header_written = False
    
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        
        for csv_file in csv_files:
            try:
                with open(csv_file, 'r', encoding='utf-8') as infile:
                    reader = csv.reader(infile)
                    
                    # Read and process each row
                    for row_num, row in enumerate(reader):
                        if row_num == 0:  # Header row
                            if not header_written:
                                # Write header only once
                                writer.writerow(row)
                                header_written = True
                                print(f"Header: {', '.join(row)}")
                        else:
                            # Data row
                            if row and len(row) >= 8:  # Ensure row has enough columns
                                writer.writerow(row)
                                total_rows += 1
                
                print(f"✅ Processed {csv_file}")
                
            except Exception as e:
                print(f"❌ Error processing {csv_file}: {e}")
    
    print(f"\n🎉 Combined {len(csv_files)} files into {output_file}")
    print(f"📊 Total quiz questions: {total_rows}")
    
    # Show sample of combined data
    print(f"\nFirst few rows of {output_file}:")
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i < 3:  # Show first 3 rows (header + 2 data rows)
                    print(f"  {i+1}: {', '.join(row[:3])}...")  # Show first 3 columns
                else:
                    break
    except Exception as e:
        print(f"Error reading combined file: {e}")


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(description='Combine quiz CSV files into one file')
    parser.add_argument('--pattern', default='quiz_*.csv', 
                       help='Glob pattern to match quiz CSV files (default: quiz_*.csv)')
    parser.add_argument('--output', default='quiz_all_combined.csv',
                       help='Output filename (default: quiz_all_combined.csv)')
    parser.add_argument('--include-existing', action='store_true',
                       help='Include existing combined file in input (default: exclude)')
    
    args = parser.parse_args()
    
    print("Quiz CSV Combiner")
    print("=" * 50)
    
    combine_quiz_csvs(
        input_pattern=args.pattern,
        output_file=args.output,
        exclude_existing=not args.include_existing
    )


if __name__ == "__main__":
    main()