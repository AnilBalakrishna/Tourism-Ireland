from flask import Blueprint, render_template

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@views_bp.route('/craftspeople')
def craftspeople():
    """Render the craftspeople management page"""
    return render_template('craftspeople.html')

@views_bp.route('/products')
def products():
    """Render the products management page"""
    return render_template('products.html')
