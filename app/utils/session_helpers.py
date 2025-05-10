from flask import request, session
from app.models.visitor import Visitor
from app.models.product import Product
from sqlalchemy import inspect
from app import db
import os
import uuid

def record_page_visit(page_name):
    try:
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        user_id = session.get('user_id')
        current_flask_session_id = session.get('visitor_id')

        # Если на Render в продакшн-окружении используем более простую логику для избежания ошибок с SQLite
        if os.environ.get('FLASK_ENV') == 'production':
            # Просто сохраняем session_id в сессии пользователя, если его еще нет
            if 'visitor_id' not in session:
                session['visitor_id'] = str(uuid.uuid4())
            # В продакшне пропускаем запись в базу для надежности
            return

        # Проверяем существует ли таблица visitor перед попыткой записи
        try:
            inspector = inspect(db.engine)
            has_visitor_table = inspector.has_table('visitor')
            if not has_visitor_table:
                print("Таблица visitor не существует. Пропускаем запись посещения.")
                if 'visitor_id' not in session:
                    session['visitor_id'] = str(uuid.uuid4())
                return
        except Exception as table_check_error:
            print(f"Ошибка при проверке таблицы visitor: {str(table_check_error)}")
            if 'visitor_id' not in session:
                session['visitor_id'] = str(uuid.uuid4())
            return

        definitive_session_id = Visitor.record_visit(
            ip_address,
            user_agent,
            current_flask_session_id=current_flask_session_id,
            user_id=user_id
        )

        session['visitor_id'] = definitive_session_id
    except Exception as e:
        # В случае любой ошибки, логируем её, но не прерываем работу приложения
        print(f"Ошибка при записи посещения: {str(e)}")
        # Если visitor_id еще не установлен, генерируем новый, чтобы не потерять сессию пользователя
        if 'visitor_id' not in session:
            session['visitor_id'] = str(uuid.uuid4())

def validate_cart_items():
    if 'cart' not in session:
        session['cart'] = []
        return
    
    # Проверяем каждый товар в корзине
    updated = False
    valid_items = []
    
    for item in session['cart']:
        product = Product.query.get(item['product_id'])
        if product:
            # Проверяем наличие товара на складе и корректируем количество при необходимости
            if product.stock < item['quantity']:
                item['quantity'] = product.stock
                updated = True
            elif item['quantity'] < 1:
                item['quantity'] = 1
                updated = True
                
            valid_items.append(item)
        # Если товар не найден в базе, не добавляем его в валидные товары
    
    # Обновляем корзину только валидными товарами
    if len(valid_items) != len(session['cart']) or updated:
        session['cart'] = valid_items
        session.modified = True 