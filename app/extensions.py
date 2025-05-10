from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_migrate import Migrate
from flask_caching import Cache

# Инициализация расширений
db = SQLAlchemy()
admin = Admin(name='Админ-панель', template_mode='bootstrap4')
migrate = Migrate()
cache = Cache(config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
}) 