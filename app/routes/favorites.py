from flask import Blueprint, jsonify, session, render_template
from app.models import Product

bp = Blueprint('favorites', __name__)

@bp.route('/')
def index():
    if 'favorites' not in session:
        session['favorites'] = []
    
    favorites = session['favorites']
    products = Product.query.filter(Product.id.in_(favorites)).all()
    
    return render_template('favorites.html', favorites=products)

@bp.route('/toggle/<int:product_id>', methods=['POST'])
def toggle_favorite(product_id):
    if 'favorites' not in session:
        session['favorites'] = []
    
    favorites = session['favorites']
    
    if product_id in favorites:
        favorites.remove(product_id)
        is_added = False
    else:
        favorites.append(product_id)
        is_added = True
    
    session['favorites'] = favorites
    session.modified = True
    
    return jsonify({
        'success': True,
        'is_added': is_added,
        'favorites_count': len(favorites)
    })

@bp.route('/list')
def get_favorites():
    if 'favorites' not in session:
        session['favorites'] = []
    
    favorites = session['favorites']
    products = Product.query.filter(Product.id.in_(favorites)).all()
    
    return jsonify({
        'success': True,
        'products': [{
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'image': product.image
        } for product in products]
    }) 