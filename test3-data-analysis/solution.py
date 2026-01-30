#!/usr/bin/env python3
"""
TEST3: Real Estate Price Per Square Foot Analysis
Script to filter properties sold for less than average price per square foot
"""

import pandas as pd
import sys
import os
from pathlib import Path


def analyze_real_estate_data(input_file, output_file=None):
    """
    Analyze real estate data and filter properties below average price per sqft
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file (optional)
    
    Returns:
        tuple: (filtered_dataframe, average_price_per_sqft, statistics_dict)
    """
    
    print("Real Estate Price Per Square Foot Analysis")
    print("-" * 70)
    
    # Step 1: Validate input file
    if not os.path.exists(input_file):
        print(f"Error: input file '{input_file}' not found.")
        sys.exit(1)
    
    print(f"Reading input file: {input_file}")
    
    # Step 2: Read CSV file
    try:
        df = pd.read_csv(input_file)
        print(f"Loaded {len(df)} properties.")
    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
        sys.exit(1)
    
    # Step 3: Validate required columns
    required_columns = ['price', 'sq__ft']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Error: missing required columns: {missing_columns}")
        print(f"Available columns: {df.columns.tolist()}")
        sys.exit(1)
    
    # Step 4: Calculate price per square foot
    # Handle division by zero (properties with 0 sq__ft)
    df['price_per_sqft'] = df.apply(
        lambda row: row['price'] / row['sq__ft'] if row['sq__ft'] > 0 else 0,
        axis=1
    )
    
    print("\nData overview")
    print(f"Total properties: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Step 5: Calculate average price per square foot
    # Only include properties with sq__ft > 0 in average calculation
    valid_properties = df[df['sq__ft'] > 0]
    average_price_per_sqft = valid_properties['price_per_sqft'].mean()
    
    print(f"Properties with valid square footage: {len(valid_properties)}")
    print(f"Average price per square foot: {average_price_per_sqft:.2f}")
    
    # Step 6: Filter properties below average
    below_average = df[df['price_per_sqft'] < average_price_per_sqft].copy()
    above_average = df[df['price_per_sqft'] >= average_price_per_sqft].copy()
    
    print("\nFiltering results")
    print(f"Properties below average price per square foot: {len(below_average)}")
    print(f"Properties at or above average price per square foot: {len(above_average)}")
    if len(df) > 0:
        print(f"Percentage below average: {len(below_average) / len(df) * 100:.1f}%")
    
    # Step 7: Prepare output file name if not provided
    if output_file is None:
        output_file = 'properties_below_average_price_per_sqft.csv'
    
    # Step 8: Write filtered data to CSV
    try:
        below_average.to_csv(output_file, index=False)
        print(f"\nSaved filtered data to: {output_file}")
        print(f"Rows: {len(below_average)}")
        print(f"Columns: {len(below_average.columns)}")
    except Exception as e:
        print(f"Error writing output CSV: {str(e)}")
        sys.exit(1)
    
    # Step 9: Display sample data
    print("\nSample of filtered data (first 10 rows)")
    sample_cols = ['street', 'city', 'price', 'sq__ft', 'price_per_sqft']
    available_sample_cols = [col for col in sample_cols if col in below_average.columns]
    if not below_average.empty and available_sample_cols:
        print(below_average[available_sample_cols].head(10).to_string(index=False))
    else:
        print("No data to display.")
    
    # Step 10: Calculate statistics
    stats = {
        'total_properties': len(df),
        'below_average_count': len(below_average),
        'above_average_count': len(above_average),
        'average_price_per_sqft': average_price_per_sqft,
        'below_avg_mean_price': below_average['price'].mean() if not below_average.empty else 0,
        'below_avg_mean_sqft': below_average['sq__ft'].mean() if not below_average.empty else 0,
        'below_avg_mean_price_per_sqft': below_average['price_per_sqft'].mean() if not below_average.empty else 0,
        'below_avg_min_price_per_sqft': below_average['price_per_sqft'].min() if not below_average.empty else 0,
        'below_avg_max_price_per_sqft': below_average['price_per_sqft'].max() if not below_average.empty else 0,
        'above_avg_mean_price_per_sqft': above_average['price_per_sqft'].mean() if not above_average.empty else 0,
    }
    
    # Step 11: Display statistics
    print("\nStatistics for below-average properties")
    print(f"Average price: {stats['below_avg_mean_price']:.2f}")
    print(f"Average square footage: {stats['below_avg_mean_sqft']:.2f}")
    print(f"Average price per square foot: {stats['below_avg_mean_price_per_sqft']:.2f}")
    print(f"Minimum price per square foot: {stats['below_avg_min_price_per_sqft']:.2f}")
    print(f"Maximum price per square foot: {stats['below_avg_max_price_per_sqft']:.2f}")
    
    print("\nComparison with above-average properties")
    print(f"Below-average average price per square foot: {stats['below_avg_mean_price_per_sqft']:.2f}")
    print(f"Above-average average price per square foot: {stats['above_avg_mean_price_per_sqft']:.2f}")
    print(f"Difference: {stats['above_avg_mean_price_per_sqft'] - stats['below_avg_mean_price_per_sqft']:.2f}")
    
    print("\nAnalysis complete.")
    
    return below_average, average_price_per_sqft, stats


def main():
    """Main function"""
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python solution.py <input_csv> [output_csv]")
        print("Examples:")
        print("  python solution.py assignment-data-1-2.csv")
        print("  python solution.py assignment-data-1-2.csv output.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Run analysis
    analyze_real_estate_data(input_file, output_file)


if __name__ == '__main__':
    main()
