#!/bin/bash
set -e

# Wait for MongoDB to be available
until nc -z mongo 27017; do
  echo "Waiting for MongoDB..."
  sleep 2
done

# Insert sample data (ignore errors if already inserted)
python insert_sample_data.py || echo "Sample data may already exist."

# Start Flask
flask run --host=0.0.0.0
