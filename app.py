"""
Файл для совместимости с Gunicorn.
Импортирует приложение из wsgi.py
"""
from wsgi import application as app 