from flask import Blueprint, jsonify, session, render_template
from app.models import Product

bp = Blueprint('compare', __name__)

MAX_COMPARE_ITEMS = 4

@bp.route('/')
def index():
    if 'compare' not in session:
        session['compare'] = []
    
    compare = session['compare']
    products = Product.query.filter(Product.id.in_(compare)).all()
    
    return render_template('compare.html', compare_products=products)

@bp.route('/toggle/<int:product_id>', methods=['POST'])
def toggle_compare(product_id):
    if 'compare' not in session:
        session['compare'] = []
    
    compare = session['compare']
    
    if product_id in compare:
        compare.remove(product_id)
        is_added = False
    else:
        if len(compare) >= MAX_COMPARE_ITEMS:
            return jsonify({
                'success': False,
                'message': f'Максимальное количество товаров для сравнения: {MAX_COMPARE_ITEMS}'
            })
        compare.append(product_id)
        is_added = True
    
    session['compare'] = compare
    session.modified = True
    
    return jsonify({
        'success': True,
        'is_added': is_added,
        'compare_count': len(compare)
    })

@bp.route('/list')
def get_compare():
    if 'compare' not in session:
        session['compare'] = []
    
    compare = session['compare']
    products = Product.query.filter(Product.id.in_(compare)).all()
    
    return jsonify({
        'success': True,
        'products': [{
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'image': product.image,
            'description': product.description,
            'specifications': product.specifications
        } for product in products]
    }) 