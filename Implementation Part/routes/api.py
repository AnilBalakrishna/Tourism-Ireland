from flask import Blueprint, jsonify, request
from models.data_manager import (
    get_all_craftspeople, get_craftsperson, add_craftsperson, update_craftsperson, delete_craftsperson,
    get_all_products, get_product, add_product, update_product, delete_product
)
import logging

api_bp = Blueprint('api', __name__)

# Craftspeople endpoints
@api_bp.route('/craftspeople', methods=['GET'])
def get_craftspeople():
    """Get all craftspeople with optional search and sort parameters"""
    search_term = request.args.get('search', '').lower()
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')
    
    craftspeople = get_all_craftspeople()
    
    # Apply search filter if provided
    if search_term:
        craftspeople = [c for c in craftspeople if 
                       search_term in c['name'].lower() or 
                       search_term in c['craft_type'].lower() or 
                       search_term in c['county'].lower()]
    
    # Apply sorting
    reverse = sort_order.lower() == 'desc'
    craftspeople = sorted(craftspeople, key=lambda x: x[sort_by], reverse=reverse)
    
    return jsonify(craftspeople)

@api_bp.route('/craftspeople/<string:id>', methods=['GET'])
def get_craftsperson_by_id(id):
    """Get a specific craftsperson by ID"""
    craftsperson = get_craftsperson(id)
    if craftsperson:
        return jsonify(craftsperson)
    return jsonify({"error": "Craftsperson not found"}), 404

@api_bp.route('/craftspeople', methods=['POST'])
def create_craftsperson():
    """Create a new craftsperson"""
    data = request.json
    
    # Validate required fields
    required_fields = ['name', 'craft_type', 'county', 'email']
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    
    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "missing": missing_fields
        }), 400
    
    # Validate email format
    if '@' not in data.get('email', ''):
        return jsonify({"error": "Invalid email format"}), 400
    
    try:
        new_craftsperson = add_craftsperson(data)
        return jsonify(new_craftsperson), 201
    except Exception as e:
        logging.error(f"Error creating craftsperson: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/craftspeople/<string:id>', methods=['PUT'])
def update_craftsperson_by_id(id):
    """Update an existing craftsperson"""
    data = request.json
    
    # Validate email format if provided
    if 'email' in data and '@' not in data['email']:
        return jsonify({"error": "Invalid email format"}), 400
    
    try:
        updated = update_craftsperson(id, data)
        if updated:
            return jsonify(updated)
        return jsonify({"error": "Craftsperson not found"}), 404
    except Exception as e:
        logging.error(f"Error updating craftsperson: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/craftspeople/<string:id>', methods=['DELETE'])
def delete_craftsperson_by_id(id):
    """Delete a craftsperson"""
    try:
        if delete_craftsperson(id):
            return jsonify({"message": "Craftsperson deleted successfully"}), 200
        return jsonify({"error": "Craftsperson not found"}), 404
    except Exception as e:
        logging.error(f"Error deleting craftsperson: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Products endpoints
@api_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products with optional search and sort parameters"""
    search_term = request.args.get('search', '').lower()
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')
    
    products = get_all_products()
    
    # Apply search filter if provided
    if search_term:
        products = [p for p in products if 
                   search_term in p['name'].lower() or 
                   search_term in p['description'].lower() or 
                   search_term in p['category'].lower()]
    
    # Apply sorting
    reverse = sort_order.lower() == 'desc'
    if sort_by == 'price':
        products = sorted(products, key=lambda x: float(x[sort_by]), reverse=reverse)
    else:
        products = sorted(products, key=lambda x: x[sort_by], reverse=reverse)
    
    return jsonify(products)

@api_bp.route('/products/<string:id>', methods=['GET'])
def get_product_by_id(id):
    """Get a specific product by ID"""
    product = get_product(id)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

@api_bp.route('/products', methods=['POST'])
def create_product():
    """Create a new product"""
    data = request.json
    
    # Validate required fields
    required_fields = ['name', 'description', 'price', 'category', 'craftsperson_id']
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    
    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "missing": missing_fields
        }), 400
    
    # Validate price is a number
    try:
        price = float(data['price'])
        if price <= 0:
            return jsonify({"error": "Price must be greater than zero"}), 400
    except ValueError:
        return jsonify({"error": "Price must be a valid number"}), 400
    
    # Validate craftsperson exists
    craftsperson = get_craftsperson(data['craftsperson_id'])
    if not craftsperson:
        return jsonify({"error": "Craftsperson does not exist"}), 400
    
    try:
        new_product = add_product(data)
        return jsonify(new_product), 201
    except Exception as e:
        logging.error(f"Error creating product: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/products/<string:id>', methods=['PUT'])
def update_product_by_id(id):
    """Update an existing product"""
    data = request.json
    
    # Validate price if provided
    if 'price' in data:
        try:
            price = float(data['price'])
            if price <= 0:
                return jsonify({"error": "Price must be greater than zero"}), 400
        except ValueError:
            return jsonify({"error": "Price must be a valid number"}), 400
    
    # Validate craftsperson exists if craftsperson_id is provided
    if 'craftsperson_id' in data:
        craftsperson = get_craftsperson(data['craftsperson_id'])
        if not craftsperson:
            return jsonify({"error": "Craftsperson does not exist"}), 400
    
    try:
        updated = update_product(id, data)
        if updated:
            return jsonify(updated)
        return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        logging.error(f"Error updating product: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/products/<string:id>', methods=['DELETE'])
def delete_product_by_id(id):
    """Delete a product"""
    try:
        if delete_product(id):
            return jsonify({"message": "Product deleted successfully"}), 200
        return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        logging.error(f"Error deleting product: {str(e)}")
        return jsonify({"error": str(e)}), 500
