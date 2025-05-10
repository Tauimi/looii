from flask import Blueprint, render_template, request, jsonify, Response
from app.models.product import Product, Category
from app.utils.session_helpers import record_page_visit
from datetime import datetime, timedelta
from app import db
import os
from app.models.visitor import Visitor

bp = Blueprint('shop', __name__)

@bp.route('/')
def home():
    # Получаем IP-адрес и User-Agent посетителя
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # Записываем визит
    visitor = Visitor.record_visit(ip_address, user_agent)
    
    # Получаем статистику посещений
    visitor_stats = Visitor.get_visitors_stats()
    
    # Получаем популярные товары
    popular_products = Product.query.order_by(Product.stock.desc()).limit(8).all()
    
    record_page_visit('home')
    
    return render_template('shop/home.html', 
                         popular_products=popular_products,
                         visitor_stats=visitor_stats)

@bp.route('/catalog')
def catalog():
    categories = Category.query.all()
    
    record_page_visit('catalog')
    
    return render_template('catalog.html', categories=categories, title="Каталог товаров")

@bp.route('/category/<int:category_id>')
def category(category_id):
    category = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(category_id=category_id).all()
    
    # Получение параметров фильтра
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort = request.args.get('sort', 'new')
    
    # Применение фильтров
    if min_price:
        products = [p for p in products if p.price >= min_price]
    
    if max_price:
        products = [p for p in products if p.price <= max_price]
    
    # Сортировка
    if sort == 'price_asc':
        products = sorted(products, key=lambda p: p.price)
    elif sort == 'price_desc':
        products = sorted(products, key=lambda p: p.price, reverse=True)
    elif sort == 'name_asc':
        products = sorted(products, key=lambda p: p.name)
    elif sort == 'name_desc':
        products = sorted(products, key=lambda p: p.name, reverse=True)
    elif sort == 'new':
        products = sorted(products, key=lambda p: p.date_added, reverse=True)
    
    record_page_visit(f'category/{category_id}')
    
    return render_template('category.html', category=category, products=products, title=f"Категория: {category.name}")

@bp.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Получаем похожие товары из той же категории
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id
    ).limit(4).all()
    
    record_page_visit(f'product/{product_id}')
    
    return render_template('product.html', product=product, related_products=related_products, title=f"Товар: {product.name}")

@bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    sort = request.args.get('sort', 'relevance')
    products = []
    related_queries = []
    
    if query:
        # Поиск товаров по имени и описанию
        products = Product.query.filter(
            (Product.name.contains(query)) | 
            (Product.description.contains(query))
        ).all()
        
        # Применение сортировки
        if sort == 'price_asc':
            products = sorted(products, key=lambda p: p.price)
        elif sort == 'price_desc':
            products = sorted(products, key=lambda p: p.price, reverse=True)
        elif sort == 'name_asc':
            products = sorted(products, key=lambda p: p.name)
        elif sort == 'name_desc':
            products = sorted(products, key=lambda p: p.name, reverse=True)
        
        # Генерация похожих запросов
        if not products:
            similar_products = Product.query.filter(Product.name.contains(query.split()[0] if query.split() else query)).limit(5).all()
            related_queries = [p.name for p in similar_products]
    
    record_page_visit(f'search?query={query}')
    
    return render_template('search_results.html', products=products, query=query, related_queries=related_queries, title="Результаты поиска")

@bp.route('/get_carousel_image/<int:slide_id>')
def get_carousel_image(slide_id):
    """Возвращает заглушку для изображения карусели по его ID"""
    try:
        # Базовые цвета для каждого слайда
        colors = {
            1: "#4169E1",  # Royal Blue
            2: "#FF6347",  # Tomato
            3: "#32CD32",  # Lime Green
            4: "#FFD700",  # Gold
            5: "#8A2BE2"   # Blue Violet
        }
        
        # Получаем цвет для слайда или используем черный по умолчанию
        color = colors.get(slide_id, "#000000")
        
        # Создаем SVG с нужным цветом и текстом
        svg = f"""
        <svg width="1200" height="400" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="{color}" />
            <text x="50%" y="50%" font-family="Arial" font-size="40" 
                  text-anchor="middle" fill="white">
                Слайд #{slide_id}
            </text>
        </svg>
        """
        
        return Response(svg, mimetype='image/svg+xml')
    except Exception as e:
        # В случае ошибки возвращаем пустое изображение
        print(f"Ошибка при генерации изображения карусели: {str(e)}")
        return "", 500

@bp.route('/get_visitors_count')
def get_visitors_count():
    try:
        # Получаем только общее количество уникальных посетителей
        total_visitors = Visitor.query.count()
        return jsonify({
            'total': total_visitors
        })
    except Exception as e:
        print(f"Ошибка при получении счетчика посетителей: {str(e)}")
        return jsonify({
            'total': 0
        }) 