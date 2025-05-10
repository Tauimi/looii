from flask import session, redirect, url_for, flash
from flask_admin.contrib.sqla import ModelView
from app.extensions import admin, db
from app.models.product import Category, Product
from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.visitor import Visitor

# Класс для безопасного доступа к админке
class SecureModelView(ModelView):
    def is_accessible(self):
        # Проверяем, авторизован ли пользователь и является ли он администратором
        return 'user_id' in session and User.query.get(session['user_id']).username == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        # Перенаправляем на страницу входа, если нет доступа
        flash('Пожалуйста, авторизуйтесь как администратор для доступа к этой странице', 'warning')
        return redirect(url_for('auth.login', next=url_for('admin.index')))

# Регистрация моделей в админке с уникальными именами
admin.add_view(SecureModelView(Category, db.session, name='Категории', endpoint='admin_categories'))
admin.add_view(SecureModelView(Product, db.session, name='Товары', endpoint='admin_products'))
admin.add_view(SecureModelView(User, db.session, name='Пользователи', endpoint='admin_users'))
admin.add_view(SecureModelView(Order, db.session, name='Заказы', endpoint='admin_orders'))
admin.add_view(SecureModelView(OrderItem, db.session, name='Товары в заказах', endpoint='admin_order_items'))
admin.add_view(SecureModelView(Visitor, db.session, name='Посетители', endpoint='admin_visitors')) 