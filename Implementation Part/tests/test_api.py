import json
import os
import sys
import pytest
import uuid
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, read_data, write_data, DATA_FILE

# Test data
TEST_DATA = [
    {
        "id": "12345-test-id",
        "name": "Test Attraction",
        "location": "Test Location",
        "description": "Test Description",
        "rating": 4.5,
        "image_url": "http://example.com/image.jpg",
        "website": "http://example.com",
        "created_at": "2023-01-01T00:00:00"
    }
]

# Test data file
TEST_DATA_FILE = "data/test_attractions.json"

@pytest.fixture
def client():
    """Create a test client for our app"""
    app.config['TESTING'] = True
    app.config['DATA_FILE'] = TEST_DATA_FILE
    
    # Create test data file
    os.makedirs(os.path.dirname(TEST_DATA_FILE), exist_ok=True)
    with open(TEST_DATA_FILE, 'w') as f:
        json.dump(TEST_DATA, f)
    
    with app.test_client() as client:
        yield client
    
    # Clean up test file
    if os.path.exists(TEST_DATA_FILE):
        os.remove(TEST_DATA_FILE)

def test_get_attractions(client):
    """Test getting all attractions"""
    response = client.get('/api/attractions')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['name'] == "Test Attraction"

def test_get_attraction(client):
    """Test getting a single attraction"""
    response = client.get('/api/attractions/12345-test-id')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['name'] == "Test Attraction"
    assert data['id'] == "12345-test-id"

def test_get_nonexistent_attraction(client):
    """Test getting a nonexistent attraction"""
    response = client.get('/api/attractions/nonexistent-id')
    data = json.loads(response.data)
    
    assert response.status_code == 404
    assert 'error' in data

def test_create_attraction(client):
    """Test creating a new attraction"""
    new_attraction = {
        "name": "New Attraction",
        "location": "New Location",
        "description": "New Description",
        "rating": 3.5
    }
    
    response = client.post('/api/attractions', 
                          data=json.dumps(new_attraction),
                          content_type='application/json')
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert data['name'] == "New Attraction"
    assert 'id' in data
    
    # Check that it was saved to the file
    with open(TEST_DATA_FILE, 'r') as f:
        saved_data = json.load(f)
    
    assert len(saved_data) == 2
    assert any(a['name'] == "New Attraction" for a in saved_data)

def test_create_invalid_attraction(client):
    """Test creating an attraction with invalid data"""
    invalid_attraction = {
        "name": "Invalid Attraction",
        # Missing required fields
    }
    
    response = client.post('/api/attractions', 
                          data=json.dumps(invalid_attraction),
                          content_type='application/json')
    
    assert response.status_code == 400

def test_update_attraction(client):
    """Test updating an attraction"""
    updated_data = {
        "name": "Updated Attraction",
        "rating": 5.0
    }
    
    response = client.put('/api/attractions/12345-test-id', 
                         data=json.dumps(updated_data),
                         content_type='application/json')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['name'] == "Updated Attraction"
    assert data['rating'] == 5.0
    assert data['location'] == "Test Location"  # Unchanged field
    
    # Check that it was saved to the file
    with open(TEST_DATA_FILE, 'r') as f:
        saved_data = json.load(f)
    
    assert saved_data[0]['name'] == "Updated Attraction"

def test_update_nonexistent_attraction(client):
    """Test updating a nonexistent attraction"""
    updated_data = {
        "name": "Updated Attraction"
    }
    
    response = client.put('/api/attractions/nonexistent-id', 
                         data=json.dumps(updated_data),
                         content_type='application/json')
    
    assert response.status_code == 404

def test_delete_attraction(client):
    """Test deleting an attraction"""
    response = client.delete('/api/attractions/12345-test-id')
    
    assert response.status_code == 200
    
    # Check that it was removed from the file
    with open(TEST_DATA_FILE, 'r') as f:
        saved_data = json.load(f)
    
    assert len(saved_data) == 0

def test_delete_nonexistent_attraction(client):
    """Test deleting a nonexistent attraction"""
    response = client.delete('/api/attractions/nonexistent-id')
    
    assert response.status_code == 404

def test_search_attractions(client):
    """Test searching attractions"""
    # Add another attraction for testing search
    another_attraction = {
        "name": "Dublin Castle",
        "location": "Dublin",
        "description": "Historic castle in Dublin",
        "rating": 4.0
    }
    
    client.post('/api/attractions', 
               data=json.dumps(another_attraction),
               content_type='application/json')
    
    # Search for Dublin
    response = client.get('/api/attractions?search=dublin')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['name'] == "Dublin Castle"
    
    # Search for Test
    response = client.get('/api/attractions?search=test')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['name'] == "Test Attraction"

def test_sort_attractions(client):
    """Test sorting attractions"""
    # Add another attraction for testing sorting
    another_attraction = {
        "name": "Blarney Castle",
        "location": "Cork",
        "description": "Famous for the Blarney Stone",
        "rating": 4.8
    }
    
    client.post('/api/attractions', 
               data=json.dumps(another_attraction),
               content_type='application/json')
    
    # Sort by name ascending
    response = client.get('/api/attractions?sort_by=name&order=asc')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]['name'] == "Blarney Castle"
    assert data[1]['name'] == "Test Attraction"
    
    # Sort by rating descending
    response = client.get('/api/attractions?sort_by=rating&order=desc')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]['name'] == "Blarney Castle"  # Higher rating
    assert data[1]['name'] == "Test Attraction"
