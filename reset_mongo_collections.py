"""
Script to reset MongoDB collections for the Flask storage app.
- Drops: users, locations, storage_items
- Creates indexes for user_id fields for efficient per-user queries
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/home_storage')
DB_NAME = MONGO_URI.rsplit('/', 1)[-1]

print(f"Using MONGO_URI: {MONGO_URI}")
print(f"Using database: {DB_NAME}")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Drop collections if they exist
db.users.drop()
db.locations.drop()
db.storage_items.drop()

# Create collections and indexes
db.create_collection('users')
db.create_collection('locations')
db.create_collection('storage_items')

db.locations.create_index('user_id')
db.storage_items.create_index('user_id')
db.storage_items.create_index('location_id')

print('Dropped and recreated users, locations, and storage_items collections with indexes.')
