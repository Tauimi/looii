from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.models.product import Product
from app.models.user import User
from app.models.order import Order, OrderItem
from app import db
from app.utils.session_helpers import record_page_visit, validate_cart_items
import uuid

bp = Blueprint('cart', __name__, url_prefix='/cart')

@bp.route('', methods=['GET', 'POST'])
def index():
    # Проверяем и валидируем товары в корзине
    validate_cart_items()
    
    cart_items = []
    total = 0
    
    for item in session['cart']:
        product = Product.query.get(item['product_id'])
        if product:
            subtotal = product.price * item['quantity']
            
            # Проверяем наличие товара на складе
            stock_warning = None
            if product.stock < item['quantity']:
                stock_warning = f'Доступно только {product.stock} шт.'
                # Корректируем количество товара, если оно превышает доступное на складе
                item['quantity'] = product.stock
                session.modified = True  # Помечаем сессию как измененную
            elif product.stock <= 3:
                stock_warning = f'Осталось всего {product.stock} шт.'
                
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'subtotal': subtotal,
                'stock_warning': stock_warning
            })
            total += subtotal
    
    record_page_visit('cart')
    
    return render_template('cart.html', cart_items=cart_items, total=total, title="Корзина")

@bp.route('/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    product = Product.query.get_or_404(product_id)
    
    # Проверяем наличие товара на складе
    if product.stock < quantity:
        message = f'К сожалению, доступно только {product.stock} шт. товара "{product.name}"'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': message
            })
        
        flash(message, 'warning')
        referer = request.referrer or url_for('shop.product', product_id=product_id)
        return redirect(referer)
    
    if 'cart' not in session:
        session['cart'] = []
    
    # Проверяем, есть ли уже такой товар в корзине
    found = False
    for item in session['cart']:
        if item['product_id'] == product_id:
            # Проверяем, не превышает ли общее количество доступное на складе
            if item['quantity'] + quantity > product.stock:
                message = f'Нельзя добавить больше {product.stock} шт. товара "{product.name}"'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': message
                    })
                
                flash(message, 'warning')
                referer = request.referrer or url_for('shop.product', product_id=product_id)
                return redirect(referer)
                
            item['quantity'] += quantity
            found = True
            break
    
    if not found:
        session['cart'].append({
            'product_id': product_id,
            'quantity': quantity
        })
    
    session.modified = True
    message = f'Товар "{product.name}" добавлен в корзину'
    
    # Проверяем, является ли запрос AJAX-запросом
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Считаем общее количество товаров в корзине для обновления индикатора
        cart_count = sum(item['quantity'] for item in session['cart'])
        return jsonify({
            'success': True,
            'message': message,
            'cart_count': cart_count
        })
    
    flash(message, 'success')
    
    # Получаем URL, с которого пришел запрос, или используем страницу продукта
    referer = request.referrer or url_for('shop.product', product_id=product_id)
    return redirect(referer)

@bp.route('/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['product_id'] != product_id]
        session.modified = True
        flash('Товар удален из корзины', 'success')
    
    return redirect(url_for('cart.index'))

@bp.route('/clear', methods=['POST'])
def clear_cart():
    if 'cart' in session:
        session['cart'] = []
        session.modified = True
        flash('Корзина очищена', 'success')
    
    return redirect(url_for('cart.index'))

@bp.route('/update/<int:product_id>', methods=['POST'])
def update_cart_item(product_id):
    quantity = int(request.form.get('quantity', 1))
    product = Product.query.get_or_404(product_id)
    
    # Validate the quantity against available stock
    if quantity > product.stock:
        quantity = product.stock
        flash(f'Количество товара "{product.name}" ограничено наличием на складе ({product.stock} шт.)', 'warning')
    elif quantity < 1:
        quantity = 1
    
    if 'cart' in session:
        cart_updated = False
        for item in session['cart']:
            if item['product_id'] == product_id:
                item['quantity'] = quantity
                cart_updated = True
                break
        
        # Если товар не найден в корзине, добавляем его
        if not cart_updated and quantity > 0:
            session['cart'].append({
                'product_id': product_id,
                'quantity': quantity
            })
        
        session.modified = True
    
    # If it's an AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'quantity': quantity,
            'subtotal': product.price * quantity,
            'message': 'Корзина обновлена'
        })
    
    return redirect(url_for('cart.index'))

@bp.route('/count')
def get_cart_count():
    """API-эндпоинт, возвращающий количество товаров в корзине"""
    if 'cart' not in session:
        count = 0
    else:
        count = sum(item['quantity'] for item in session['cart'])
    
    return jsonify({'count': count})

@bp.route('/apply_promocode', methods=['POST'])
def apply_promocode():
    promocode = request.form.get('promocode')
    flash('Промокод применен', 'success')
    return redirect(url_for('cart.index'))

@bp.route('/checkout')
def checkout():
    # Проверяем и валидируем товары в корзине
    validate_cart_items()
    
    if 'cart' not in session or not session['cart']:
        flash('Ваша корзина пуста', 'warning')
        return redirect(url_for('cart.index'))
    
    cart_items = []
    total = 0
    
    for item in session['cart']:
        product = Product.query.get(item['product_id'])
        if product:
            subtotal = product.price * item['quantity']
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'subtotal': subtotal
            })
            total += subtotal
    
    # Если пользователь авторизован, предзаполняем форму его данными
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    
    record_page_visit('checkout')
    
    return render_template('checkout.html', cart_items=cart_items, total=total, user=user, title="Оформление заказа")

@bp.route('/place_order', methods=['POST'])
def place_order():
    # Проверяем и валидируем товары в корзине
    validate_cart_items()
    
    if 'cart' not in session or not session['cart']:
        flash('Ваша корзина пуста', 'warning')
        return redirect(url_for('cart.index'))
    
    # Проверяем наличие товаров на складе
    insufficient_stock = []
    cart_items = []
    total = 0
    
    for item in session['cart']:
        product = Product.query.get(item['product_id'])
        if product:
            # Проверяем наличие на складе
            if product.stock < item['quantity']:
                insufficient_stock.append({
                    'name': product.name,
                    'available': product.stock,
                    'requested': item['quantity']
                })
            else:
                subtotal = product.price * item['quantity']
                cart_items.append({
                    'product': product,
                    'quantity': item['quantity'],
                    'subtotal': subtotal
                })
                total += subtotal
    
    if insufficient_stock:
        message = 'Недостаточно товаров на складе:<br>'
        for item in insufficient_stock:
            message += f"• {item['name']}: доступно {item['available']}, запрошено {item['requested']}<br>"
        flash(message, 'danger')
        return redirect(url_for('cart.index'))
    
    # Получаем данные из формы
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    city = request.form.get('city')
    address = request.form.get('address')
    postal_code = request.form.get('postal_code')
    delivery_method = request.form.get('delivery_method')
    payment_method = request.form.get('payment_method')
    comment = request.form.get('comment')
    
    # Если пользователь авторизован, используем его данные
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    else:
        # Создаем или получаем пользователя
        user = User.query.filter_by(email=email).first()
        if not user:
            # Генерируем имя пользователя на основе email
            username = email.split('@')[0]
            # Генерируем случайный пароль
            password = str(uuid.uuid4())[:8]
            
            user = User(
                username=username,
                email=email,
                phone=phone,
                city=city,
                address=address,
                postal_code=postal_code
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
    
    # Добавляем стоимость доставки, если нужно
    if delivery_method == 'courier' and total < 5000:
        total += 500
    
    # Создаем заказ
    order = Order(
        user_id=user.id,
        total_amount=total,
        status='Новый',
        delivery_address=address,
        delivery_city=city,
        delivery_postal_code=postal_code,
        payment_method=payment_method,
        delivery_method=delivery_method
    )
    db.session.add(order)
    db.session.commit()
    
    # Добавляем товары в заказ и уменьшаем количество на складе
    for item in cart_items:
        product = item['product']
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item['quantity'],
            price=product.price
        )
        db.session.add(order_item)
        
        # Уменьшаем остаток на складе
        product.stock -= item['quantity']
    
    db.session.commit()
    
    # Очищаем корзину
    session['cart'] = []
    session.modified = True
    
    flash('Ваш заказ успешно оформлен!', 'success')
    return redirect(url_for('order.success', order_id=order.id))

@bp.route('/check/<int:product_id>', methods=['GET'])
def check_cart_item(product_id):
    if 'cart' not in session:
        return jsonify({
            'in_cart': False,
            'quantity': 0
        })
    
    for item in session['cart']:
        if item['product_id'] == product_id:
            return jsonify({
                'in_cart': True,
                'quantity': item['quantity']
            })
    
    return jsonify({
        'in_cart': False,
        'quantity': 0
    }) 