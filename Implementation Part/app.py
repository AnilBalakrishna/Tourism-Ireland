import os
import json
import logging
from flask import Flask, jsonify, request, render_template, abort
from flask_cors import CORS
import uuid
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "ireland_tourism_default_key")
CORS(app)  # Enable CORS for all routes

# Path to the data file
DATA_FILE = "data/attractions.json"

# Ensure data directory and file exist
def initialize_data():
    """Initialize the data file if it doesn't exist"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        # Create default file with empty array
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)

initialize_data()

def read_data():
    """Read data from the JSON file"""
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Log the error for debugging
        logging.error(f"Error reading from {DATA_FILE}. Creating empty data array.")
        return []

def write_data(data):
    """Write data to the JSON file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        logging.debug(f"Successfully wrote data to {DATA_FILE}")
    except Exception as e:
        logging.error(f"Error writing to {DATA_FILE}: {str(e)}")
        raise

# API Routes
@app.route('/api/attractions', methods=['GET'])
def get_attractions():
    """Get all attractions with optional search and sort parameters"""
    attractions = read_data()
    
    # Search functionality
    search_term = request.args.get('search', '').lower()
    if search_term:
        attractions = [a for a in attractions if 
                      search_term in a.get('name', '').lower() or 
                      search_term in a.get('location', '').lower() or
                      search_term in a.get('description', '').lower()]
    
    # Sorting functionality
    sort_by = request.args.get('sort_by', 'name')
    reverse = request.args.get('order', 'asc') == 'desc'
    
    if sort_by in ['name', 'location', 'rating', 'created_at']:
        attractions = sorted(attractions, key=lambda x: x.get(sort_by, ''), reverse=reverse)
    
    return jsonify(attractions)

@app.route('/api/attractions/<attraction_id>', methods=['GET'])
def get_attraction(attraction_id):
    """Get a specific attraction by ID"""
    attractions = read_data()
    attraction = next((a for a in attractions if a.get('id') == attraction_id), None)
    
    if attraction:
        return jsonify(attraction)
    else:
        return jsonify({"error": "Attraction not found"}), 404

@app.route('/api/attractions', methods=['POST'])
def create_attraction():
    """Create a new attraction"""
    data = request.get_json()
    
    # Validation
    required_fields = ['name', 'location', 'description', 'rating']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Data type validation
    if not isinstance(data.get('rating'), (int, float)) or not (0 <= data.get('rating') <= 5):
        return jsonify({"error": "Rating must be a number between 0 and 5"}), 400
    
    # Create new attraction
    new_attraction = {
        'id': str(uuid.uuid4()),
        'name': data['name'],
        'location': data['location'],
        'description': data['description'],
        'rating': data['rating'],
        'image_url': data.get('image_url', ''),
        'website': data.get('website', ''),
        'created_at': datetime.now().isoformat()
    }
    
    attractions = read_data()
    attractions.append(new_attraction)
    write_data(attractions)
    
    return jsonify(new_attraction), 201

@app.route('/api/attractions/<attraction_id>', methods=['PUT'])
def update_attraction(attraction_id):
    """Update an existing attraction"""
    data = request.get_json()
    attractions = read_data()
    
    # Find attraction to update
    attraction_index = next((i for i, a in enumerate(attractions) if a.get('id') == attraction_id), None)
    
    if attraction_index is None:
        return jsonify({"error": "Attraction not found"}), 404
    
    # Data type validation
    if 'rating' in data and (not isinstance(data.get('rating'), (int, float)) or not (0 <= data.get('rating') <= 5)):
        return jsonify({"error": "Rating must be a number between 0 and 5"}), 400
    
    # Update attraction
    updated_attraction = attractions[attraction_index].copy()
    for key, value in data.items():
        if key != 'id' and key != 'created_at':  # Prevent updating these fields
            updated_attraction[key] = value
    
    updated_attraction['updated_at'] = datetime.now().isoformat()
    attractions[attraction_index] = updated_attraction
    write_data(attractions)
    
    return jsonify(updated_attraction)

@app.route('/api/attractions/<attraction_id>', methods=['DELETE'])
def delete_attraction(attraction_id):
    """Delete an attraction"""
    attractions = read_data()
    initial_count = len(attractions)
    
    # Remove attraction with matching ID
    attractions = [a for a in attractions if a.get('id') != attraction_id]
    
    if len(attractions) == initial_count:
        return jsonify({"error": "Attraction not found"}), 404
    
    write_data(attractions)
    return jsonify({"message": "Attraction deleted successfully"}), 200

# Front-end routes
@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

# Error handling
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
