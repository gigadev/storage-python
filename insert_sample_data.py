"""
Sample script to insert demo data into users, locations, and storage_items collections for the Flask storage app.
Run this after reset_mongo_collections.py.
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/home_storage')
DB_NAME = MONGO_URI.rsplit('/', 1)[-1]

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Sample users
demo_users = [
    {'_id': 'demo-user', 'email': 'demo@example.com', 'name': 'Demo User'},
    {'_id': 'user1', 'email': 'user1@example.com', 'name': 'User One'},
    {'_id': 'user2', 'email': 'user2@example.com', 'name': 'User Two'},
]
try:
    db.users.insert_many(demo_users)
    print(f"Inserted {len(demo_users)} users.")
except Exception as e:
    print(f"Error inserting users: {e}")

# Sample locations (each tied to a user)
demo_locations = [
    {'name': 'Pantry', 'description': 'Main kitchen pantry', 'user_id': 'demo-user'},
    {'name': 'Garage Shelf', 'description': 'Shelf in garage', 'user_id': 'demo-user'},
    {'name': 'Basement Freezer', 'description': 'Freezer in basement', 'user_id': 'user1'},
    {'name': 'Office Cabinet', 'description': 'Cabinet in office', 'user_id': 'user2'},
]
loc_ids = db.locations.insert_many(demo_locations).inserted_ids
print(f"Inserted {len(loc_ids)} locations.")

# Sample storage items (each tied to a user and a location)
demo_items = [
    {
        'name': 'Canned Beans',
        'brand': 'BestBeans',
        'size': '15oz',
        'nutritional_info': 'Protein-rich',
        'date_purchased': '2025-06-01',
        'expiration_date': '2026-06-01',
        'ingredients': 'Beans, water, salt',
        'other_info': '',
        'location_id': str(loc_ids[0]),
        'user_id': 'demo-user',
    },
    {
        'name': 'Pasta',
        'brand': 'PastaCo',
        'size': '1lb',
        'nutritional_info': 'Carbs',
        'date_purchased': '2025-05-15',
        'expiration_date': '2026-05-15',
        'ingredients': 'Wheat',
        'other_info': '',
        'location_id': str(loc_ids[1]),
        'user_id': 'demo-user',
    },
    {
        'name': 'Frozen Pizza',
        'brand': 'PizzaBrand',
        'size': '12in',
        'nutritional_info': 'Cheese, carbs',
        'date_purchased': '2025-06-10',
        'expiration_date': '2025-12-10',
        'ingredients': 'Flour, cheese, tomato',
        'other_info': '',
        'location_id': str(loc_ids[2]),
        'user_id': 'user1',
    },
    {
        'name': 'Coffee',
        'brand': 'BrewMaster',
        'size': '2lb',
        'nutritional_info': 'Caffeine',
        'date_purchased': '2025-04-20',
        'expiration_date': '2026-04-20',
        'ingredients': 'Coffee beans',
        'other_info': '',
        'location_id': str(loc_ids[3]),
        'user_id': 'user2',
    },
]
try:
    db.storage_items.insert_many(demo_items)
    print(f"Inserted {len(demo_items)} storage items.")
except Exception as e:
    print(f"Error inserting storage items: {e}")

# Add Scott Shepherd user
scott_user = {'_id': '117740515392558077582', 'email': 'scott.shepherd@example.com', 'name': 'Scott Shepherd'}
db.users.insert_one(scott_user)

# Add locations for Scott Shepherd
scott_locations = [
    {'name': 'Scott Pantry', 'description': 'Scott\'s kitchen pantry', 'user_id': '117740515392558077582'},
    {'name': 'Scott Garage', 'description': 'Scott\'s garage shelf', 'user_id': '117740515392558077582'},
]
scott_loc_ids = db.locations.insert_many(scott_locations).inserted_ids

# Add storage items for Scott Shepherd
scott_items = [
    {
        'name': 'Granola Bars',
        'brand': 'Nature Valley',
        'size': '12 pack',
        'nutritional_info': 'Whole grain oats',
        'date_purchased': '2025-06-10',
        'expiration_date': '2026-01-10',
        'ingredients': 'Oats, honey, sugar',
        'other_info': 'Peanut free',
        'location_id': str(scott_loc_ids[0]),
        'user_id': '117740515392558077582',
    },
    {
        'name': 'Bottled Water',
        'brand': 'Aquafina',
        'size': '24 pack',
        'nutritional_info': 'Water',
        'date_purchased': '2025-05-20',
        'expiration_date': '2027-05-20',
        'ingredients': 'Water',
        'other_info': '',
        'location_id': str(scott_loc_ids[1]),
        'user_id': '117740515392558077582',
    },
    {
        'name': 'Soup Cans',
        'brand': 'Campbell\'s',
        'size': '10.5oz',
        'nutritional_info': 'Low sodium',
        'date_purchased': '2025-06-01',
        'expiration_date': '2026-06-01',
        'ingredients': 'Chicken, noodles, broth',
        'other_info': '',
        'location_id': str(scott_loc_ids[0]),
        'user_id': '117740515392558077582',
    },
]
db.storage_items.insert_many(scott_items)

print(f"Users count: {db.users.count_documents({})}")
print(f"Locations count: {db.locations.count_documents({})}")
print(f"Storage items count: {db.storage_items.count_documents({})}")

print('Inserted sample users, locations, and storage_items.')
