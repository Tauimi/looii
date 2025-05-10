"""
Основной файл приложения, объединяющий инициализацию и запуск.
"""
from app import create_app, db
from app.utils.init_data import create_initial_data
from flask_migrate import Migrate
import os
import multiprocessing
from sqlalchemy import inspect, text
from app.extensions import cache

# Конфигурация Gunicorn
bind = "0.0.0.0:$PORT"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 60
keepalive = 5
errorlog = "-"
loglevel = "info"
accesslog = "-"
preload_app = True

def init_database(app):
    """Инициализация базы данных."""
    print("=== ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ ===")
    
    # Проверяем и корректируем URL базы данных для PostgreSQL
    if 'DATABASE_URL' in os.environ:
        database_url = os.environ['DATABASE_URL']
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
            os.environ['DATABASE_URL'] = database_url
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url
            print(f"Скорректированный URL базы данных: {database_url}")
    
    with app.app_context():
        try:
            # Проверяем соединение
            connection = db.engine.connect()
            connection.execute(text("SELECT 1"))
            connection.close()
            print("Соединение с базой данных установлено")
            
            # Проверяем таблицы
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Найденные таблицы: {tables}")
            
            required_tables = ['category', 'product', 'user', 'order', 'order_item', 'visitor']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                print(f"Отсутствуют таблицы: {missing_tables}")
                print("Создание таблиц...")
                db.create_all()
                
                # Заполняем данными только если создали новые таблицы
                print("Заполнение начальными данными...")
                create_initial_data()
            
            print("=== БАЗА ДАННЫХ УСПЕШНО ИНИЦИАЛИЗИРОВАНА ===")
            
        except Exception as e:
            print(f"ОШИБКА: {str(e)}")
            raise e

# Создаем приложение
app = create_app()

# Инициализируем миграции
migrate = Migrate(app, db)

# Инициализируем базу данных при запуске
init_database(app)

# Инициализация кэширования
cache.init_app(app)

# Для WSGI серверов
application = app

if __name__ == '__main__':
    # Запускаем приложение с отладкой, если не в продакшене
    app.run(debug=os.environ.get('FLASK_ENV') != 'production') 