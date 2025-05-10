# Импорт моделей для упрощения доступа
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.visitor import Visitor

__all__ = ['User', 'Product', 'Category', 'Order', 'OrderItem', 'Visitor'] 