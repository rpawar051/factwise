from app import app
import os
import json
# Define the path to the database folder
DB_PATH = os.path.join(app.root_path, 'db')

# Create the database folder if it doesn't exist
if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

print("DB Path: ", DB_PATH)
# Example: Using JSON files for data storage

def load_data(filename):
    """Loads data from a JSON file."""
    filepath = os.path.join(DB_PATH, filename)
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.decoder.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

def save_data(filename, data):
    """Saves data to a JSON file."""
    filepath = os.path.join(DB_PATH, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
