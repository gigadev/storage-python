# CSV Import Feature Documentation

## Overview
The CSV import feature allows users to bulk upload storage items and locations from a CSV file. This feature automatically creates locations if they don't exist and associates all imported data with the logged-in user.

## Changes Made

### 1. Updated `requirements.txt`
- Added `pandas` library for CSV parsing and date handling

### 2. Updated `app.py`
- Added imports: `pandas as pd`, `datetime`, `secure_filename` from werkzeug
- Created new route `/import_csv` with GET and POST methods
- Features of the import route:
  - Validates file upload (must be .csv)
  - Reads and parses CSV using pandas
  - Validates required columns (ItemName, ItemLocation)
  - Auto-creates locations if they don't exist for the user
  - Parses date fields (ExpirationDate, Manufactured Date)
  - Maps CSV columns to database fields
  - Handles errors gracefully with detailed error reporting
  - Provides import statistics (items imported, locations created)

### 3. Created `templates/import_csv.html`
- User-friendly upload form with file input
- Comprehensive documentation of CSV format requirements
- Lists all required and optional columns
- Provides sample CSV format for reference
- Shows helpful notes about auto-location creation

### 4. Updated `templates/items.html`
- Added "Import CSV" button next to "Add Item" button
- Button links to the new `/import_csv` route

## CSV Format

### Required Columns
- `ItemName` - The name of the storage item
- `ItemLocation` - The location name (auto-created if needed)

### Optional Columns
- `Manufacturer` - Brand/manufacturer (maps to `brand` field)
- `Quantity` - Quantity amount
- `Servings Per` - Servings per container (new field: `servings_per`)
- `Servings Size` - Size per serving (maps to `size` field)
- `Units` - Unit of measurement (new field: `units`)
- `Servings` - Total servings (maps to `nutritional_info`)
- `ExpirationDate` - Expiration date (auto-parsed to YYYY-MM-DD)
- `Box` - Box/container identifier (new field: `box`)
- `Manufactured Date` - Manufacturing date (new field: `manufactured_date`)
- `UPC` - UPC/barcode (new field: `upc`)
- `Damaged` - Damage notes (maps to `other_info`)

### New Database Fields Added
The import feature introduces these new fields to the `storage_items` collection:
- `servings_per` - Number of servings per container
- `units` - Unit of measurement
- `box` - Box or container identifier
- `manufactured_date` - Manufacturing date
- `upc` - UPC/barcode number

Existing fields are reused where possible:
- `brand` ← Manufacturer
- `size` ← Servings Size
- `nutritional_info` ← Servings
- `other_info` ← Damaged

## How It Works

1. **User uploads CSV file** through the import form
2. **File validation** ensures it's a .csv file
3. **Column validation** checks for required columns (ItemName, ItemLocation)
4. **Location processing**: For each unique location name:
   - Checks if location exists for this user
   - Creates new location if it doesn't exist
   - Maps location name to ObjectId for item creation
5. **Item processing**: For each row:
   - Parses date fields using pandas date parser
   - Maps CSV columns to database fields
   - Creates item with user_id for data isolation
   - Handles missing/null values gracefully
6. **Error handling**: Captures row-level errors and reports them
7. **Results display**: Shows success message with statistics

## Usage Instructions

1. Navigate to "Storage Items" page
2. Click "Import CSV" button
3. Review the format requirements on the import page
4. Select your CSV file
5. Click "Import CSV" button
6. Review import results (items imported, locations created, any errors)
7. View imported items in the items list

## Sample CSV
A sample CSV file is available at `ImportSamples/ShepherdStorage - Items.csv` with ~996 rows of data.

## Security Features
- Login required (`@login_required` decorator)
- All imported data tagged with `user_id` from session
- Users can only see their own imported data
- File validation (must be .csv)
- Error handling prevents data corruption

## Future Enhancements
Potential improvements:
- Download CSV template button
- CSV export functionality
- Mapping configuration for custom column names
- Preview before import
- Duplicate detection
- Update existing items instead of creating new ones
