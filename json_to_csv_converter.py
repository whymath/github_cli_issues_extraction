import json
import csv
import pandas as pd
from typing import Any, Dict, List, Union
from pathlib import Path

class JSONToCSVConverter:
    def __init__(self, flatten_strategy='dot_notation'):
        """
        Initialize the converter with a flattening strategy.
        
        Strategies:
        - 'dot_notation': Flatten nested objects using dot notation (e.g., 'address.street')
        - 'separate_columns': Create separate columns for array elements
        - 'json_string': Keep complex nested data as JSON strings
        - 'normalize': Use pandas json_normalize for automatic flattening
        """
        self.flatten_strategy = flatten_strategy
        print(f"Initialized converter with '{self.flatten_strategy}' strategy.")
    
    def flatten_dict(self, data: Dict[str, Any], parent_key: str = '', separator: str = '.') -> Dict[str, Any]:
        """
        Flatten a nested dictionary using dot notation.
        """
        items = []
        for key, value in data.items():
            new_key = f"{parent_key}{separator}{key}" if parent_key else key
            
            if isinstance(value, dict):
                # Recursively flatten nested dictionaries
                items.extend(self.flatten_dict(value, new_key, separator).items())
            elif isinstance(value, list):
                # Handle arrays based on strategy
                if self.flatten_strategy == 'dot_notation':
                    # Convert list to JSON string or create indexed columns
                    if all(isinstance(item, (str, int, float, bool)) for item in value):
                        # Simple list - join as string
                        items.append((new_key, ', '.join(map(str, value))))
                    else:
                        # Complex list - keep as JSON string
                        items.append((new_key, json.dumps(value)))
                elif self.flatten_strategy == 'separate_columns':
                    # Create separate columns for each array element
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            items.extend(self.flatten_dict(item, f"{new_key}_{i}", separator).items())
                        else:
                            items.append((f"{new_key}_{i}", item))
                else:
                    items.append((new_key, json.dumps(value)))
            else:
                items.append((new_key, value))
        
        return dict(items)
    
    def convert_with_custom_flattening(self, json_file: str, csv_file: str):
        """
        Convert JSON to CSV using custom flattening logic.
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both single objects and arrays of objects
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            raise ValueError("JSON must contain an object or array of objects")
        
        # Flatten each record
        flattened_data = []
        for record in data:
            if isinstance(record, dict):
                flattened_record = self.flatten_dict(record)
                flattened_data.append(flattened_record)
            else:
                # Handle non-dict items in array
                flattened_data.append({'value': record})
        
        if not flattened_data:
            raise ValueError("No data to convert")
        
        # Get all possible fieldnames
        fieldnames = set()
        for record in flattened_data:
            fieldnames.update(record.keys())
        fieldnames = sorted(list(fieldnames))
        
        # Write to CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(flattened_data)
        
        print(f"Converted {len(flattened_data)} records to {csv_file}")
        print(f"Columns: {', '.join(fieldnames)}")
    
    def convert_with_pandas(self, json_file: str, csv_file: str):
        """
        Convert JSON to CSV using pandas json_normalize for automatic flattening.
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Use pandas json_normalize to flatten
        if isinstance(data, dict):
            df = pd.json_normalize(data)
        elif isinstance(data, list):
            df = pd.json_normalize(data)
        else:
            raise ValueError("JSON must contain an object or array of objects")
        
        # Handle remaining nested data by converting to strings
        for column in df.columns:
            df[column] = df[column].apply(
                lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x
            )
        
        df.to_csv(csv_file, index=False)
        print(f"Converted {len(df)} records to {csv_file}")
        print(f"Columns: {', '.join(df.columns)}")
    
    def convert_with_array_explosion(self, json_file: str, csv_file: str, array_field: str = None):
        """
        Convert JSON to CSV with array explosion (create multiple rows for array elements).
        Useful when you want each array item to become a separate row.
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict):
            data = [data]
        
        exploded_data = []
        
        for record in data:
            if array_field and array_field in record and isinstance(record[array_field], list):
                # Create a row for each array element
                for item in record[array_field]:
                    new_record = record.copy()
                    del new_record[array_field]
                    
                    if isinstance(item, dict):
                        # Merge the array item's fields into the record
                        new_record.update(item)
                    else:
                        # Simple value - use the array field name
                        new_record[array_field] = item
                    
                    exploded_data.append(self.flatten_dict(new_record))
            else:
                exploded_data.append(self.flatten_dict(record))
        
        # Get all fieldnames
        fieldnames = set()
        for record in exploded_data:
            fieldnames.update(record.keys())
        fieldnames = sorted(list(fieldnames))
        
        # Write to CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(exploded_data)
        
        print(f"Converted {len(exploded_data)} records to {csv_file}")
        print(f"Columns: {', '.join(fieldnames)}")

def demo_conversion():
    """
    Demonstrate different conversion strategies with sample data.
    """
    # Sample nested JSON data
    sample_data = [
        {
            "id": 1,
            "name": "John Doe",
            "address": {
                "street": "123 Main St",
                "city": "Boston",
                "coordinates": {"lat": 42.3601, "lng": -71.0589}
            },
            "contacts": [
                {"type": "email", "value": "john@example.com"},
                {"type": "phone", "value": "555-1234"}
            ],
            "tags": ["customer", "premium", "active"]
        },
        {
            "id": 2,
            "name": "Jane Smith",
            "address": {
                "street": "456 Oak Ave",
                "city": "Seattle",
                "coordinates": {"lat": 47.6062, "lng": -122.3321}
            },
            "contacts": [
                {"type": "email", "value": "jane@example.com"}
            ],
            "tags": ["customer"]
        }
    ]
    
    # Save sample data
    with open('sample_data.json', 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    # Try different conversion strategies
    strategies = ['dot_notation', 'separate_columns', 'json_string']
    
    for strategy in strategies:
        print(f"\n--- Using {strategy} strategy ---")
        converter = JSONToCSVConverter(flatten_strategy=strategy)
        output_file = f'output_{strategy}.csv'
        converter.convert_with_custom_flattening('sample_data.json', output_file)
    
    # Try pandas normalization
    print(f"\n--- Using pandas json_normalize ---")
    converter = JSONToCSVConverter()
    converter.convert_with_pandas('sample_data.json', 'output_pandas.csv')
    
    # Try array explosion on contacts
    print(f"\n--- Using array explosion on 'contacts' ---")
    converter.convert_with_array_explosion('sample_data.json', 'output_exploded.csv', 'contacts')

# Usage examples
if __name__ == "__main__":
    # Basic usage
    strategy = 'json_string'  # Change to 'dot_notation' or 'separate_columns' as needed
    converter = JSONToCSVConverter(flatten_strategy=strategy)
    
    # Example 1: Convert with dot notation (default)
    # converter.convert_with_custom_flattening('input.json', 'output.csv')
    
    # Example 2: Convert with pandas (automatic flattening)
    # converter.convert_with_pandas('input.json', 'output.csv')
    
    # Example 3: Convert with array explosion
    # converter.convert_with_array_explosion('input.json', 'output.csv', 'array_field_name')
    
    # Run demonstration
    # demo_conversion()
    json_file_name = 'prs9'
    json_file = f'{json_file_name}.json'
    output_file = f'output_{json_file_name}_{strategy}.csv'
    converter.convert_with_custom_flattening(json_file, output_file)
