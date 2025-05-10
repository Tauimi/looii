from flask import Flask, session, redirect, url_for, flash
import os

# Импортируем расширения из нового файла
from app.extensions import db, admin, migrate
from app.config import Config

def create_app(config_class=Config):
    # Определяем разные возможные пути к директории шаблонов
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    possible_template_paths = [
        os.path.join(root_dir, 'templates'),  # /project/templates
        os.path.join(os.path.dirname(root_dir), 'templates'),  # /templates (на уровень выше)
        os.path.abspath('templates'),  # Текущая директория запуска/templates
        os.path.join(os.path.abspath('.'), 'templates'),  # Еще один вариант
        '/opt/render/project/src/templates',  # Специфичный путь для Render
    ]
    
    # Находим первый существующий путь
    template_dir = None
    for path in possible_template_paths:
        if os.path.exists(path) and os.path.isdir(path):
            template_dir = path
            break
    
    if not template_dir:
        print("ВНИМАНИЕ: Не удалось найти директорию с шаблонами! Используем путь по умолчанию.")
        template_dir = os.path.join(root_dir, 'templates')
    
    print(f"Используется директория шаблонов: {template_dir}")
    
    static_dir = os.path.join(root_dir, 'static')
    if not os.path.exists(static_dir):
        static_dir = os.path.abspath('static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    app.config.from_object(config_class)
    
    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)
    
    with app.app_context():
        # Импортируем декоратор login_required после инициализации приложения
        from app.utils.decorators import login_required
        
        # Импорт моделей
        from app.models.user import User
        from app.models.product import Product
        from app.models.category import Category
        from app.models.order import Order
        from app.models.order_item import OrderItem
        from app.models.visitor import Visitor
        
        # Регистрация маршрутов
        from app.routes.auth import bp as auth_bp
        from app.routes.shop import bp as shop_bp
        from app.routes.cart import bp as cart_bp
        from app.routes.profile import bp as profile_bp
        from app.routes.static_pages import bp as static_bp
        from app.routes.order import bp as order_bp
        from app.routes.favorites import bp as favorites_bp
        from app.routes.compare import bp as compare_bp
        from app.routes.errors import bp as errors_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(shop_bp)
        app.register_blueprint(cart_bp, url_prefix='/cart')
        app.register_blueprint(profile_bp)
        app.register_blueprint(static_bp)
        app.register_blueprint(order_bp, url_prefix='/order')
        app.register_blueprint(favorites_bp, url_prefix='/favorites')
        app.register_blueprint(compare_bp, url_prefix='/compare')
        app.register_blueprint(errors_bp)
        
        # Настройка административного интерфейса
        # импортируем views после регистрации всех маршрутов
        from app.admin import views
        
        # Добавляем маршрут для админ-панели
        @app.route('/admin-panel')
        @login_required
        def admin_panel():
            user = User.query.get(session['user_id'])
            if user.username != 'admin':
                flash('У вас нет доступа к административной панели', 'danger')
                return redirect(url_for('shop.home'))
            return redirect(url_for('admin.index'))
        
        # Проверка наличия шаблонов
        template_folder = app.template_folder
        print(f"Flask ищет шаблоны в: {template_folder}")
        if os.path.exists(template_folder):
            print(f"Директория с шаблонами существует. Содержимое: {os.listdir(template_folder)}")
        else:
            print(f"ОШИБКА: Директория с шаблонами не существует!")
        
        return app 