#!/usr/bin/env python3
"""
Migration script to convert 'box' field from string to integer in storage_items collection.
This script updates all existing items in the database.
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB URI from environment
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/home_storage')

def migrate_box_field():
    """Convert box field from string to integer for all storage items."""
    
    print(f"Connecting to MongoDB: {MONGO_URI}")
    client = MongoClient(MONGO_URI)
    
    # Get database name from URI or use default
    if '/' in MONGO_URI.split('://')[-1]:
        db_name = MONGO_URI.split('/')[-1].split('?')[0]
    else:
        db_name = 'home_storage'
    
    db = client[db_name]
    collection = db.storage_items
    
    print(f"\nMigrating 'box' field in '{db_name}.storage_items' collection...")
    
    # Statistics
    total_items = collection.count_documents({})
    updated_count = 0
    converted_count = 0
    nullified_count = 0
    already_int_count = 0
    error_count = 0
    
    print(f"Total items in collection: {total_items}")
    
    # Process all documents
    for item in collection.find({}):
        item_id = item['_id']
        box_value = item.get('box')
        
        # Check current type
        if isinstance(box_value, int):
            already_int_count += 1
            continue
        
        # Determine new value
        new_box_value = None
        
        if box_value is None:
            # Already None, no update needed
            continue
        elif isinstance(box_value, str):
            box_str = box_value.strip()
            if box_str:
                try:
                    # Try to convert to integer
                    # Handle potential float strings (e.g., "1.0" or "1,234")
                    box_str_clean = box_str.replace(',', '')
                    new_box_value = int(float(box_str_clean))
                    converted_count += 1
                except (ValueError, TypeError) as e:
                    print(f"  Warning: Could not convert box value '{box_value}' for item {item_id}: {e}")
                    error_count += 1
                    # Set to None for non-numeric values
                    new_box_value = None
                    nullified_count += 1
            else:
                # Empty string -> None
                new_box_value = None
                nullified_count += 1
        else:
            # Unexpected type
            print(f"  Warning: Unexpected box type {type(box_value)} for item {item_id}: {box_value}")
            try:
                new_box_value = int(box_value)
                converted_count += 1
            except:
                new_box_value = None
                nullified_count += 1
                error_count += 1
        
        # Update the document
        try:
            collection.update_one(
                {'_id': item_id},
                {'$set': {'box': new_box_value}}
            )
            updated_count += 1
        except Exception as e:
            print(f"  Error updating item {item_id}: {e}")
            error_count += 1
    
    # Print summary
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)
    print(f"Total items processed:        {total_items}")
    print(f"Items updated:                {updated_count}")
    print(f"  - Converted to integer:     {converted_count}")
    print(f"  - Set to None (empty/null): {nullified_count}")
    print(f"  - Already integer:          {already_int_count}")
    print(f"Errors encountered:           {error_count}")
    print("="*60)
    
    if error_count > 0:
        print("\nNote: Some items could not be converted. These were set to None.")
    
    print("\nMigration complete!")
    client.close()

if __name__ == '__main__':
    try:
        migrate_box_field()
    except Exception as e:
        print(f"\nError during migration: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
