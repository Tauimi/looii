import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'electroshop_secret_key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Конфигурация базы данных
    if os.environ.get('FLASK_ENV') == 'production':
        # Production настройки для Render
        database_url = os.environ.get('DATABASE_URL')
        if database_url and database_url.startswith("postgres://"):
            # Render предоставляет URL формата postgres://, но SQLAlchemy ожидает postgresql://
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///tmp/electroshop.db'
    else:
        # Локальные настройки для разработки (SQLite)
        SQLALCHEMY_DATABASE_URI = 'sqlite:///electroshop.db' 