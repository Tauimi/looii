from app.extensions import db
from datetime import datetime
from sqlalchemy import Index

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=False, index=True)
    total_amount = db.Column(db.Float, nullable=False, index=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    status = db.Column(db.String(50), default='Pending', index=True)
    items = db.relationship('OrderItem', backref='order', lazy='selectin', cascade='all, delete-orphan')
    delivery_address = db.Column(db.String(200))
    delivery_city = db.Column(db.String(100))
    delivery_postal_code = db.Column(db.String(20))
    payment_method = db.Column(db.String(50))
    delivery_method = db.Column(db.String(50))
    
    # Индексы для часто используемых комбинаций полей
    __table_args__ = (
        Index('idx_order_user_date', 'user_id', 'order_date'),
        Index('idx_order_status_date', 'status', 'order_date'),
    )
    
    def __repr__(self):
        return f'<Order {self.id}>'

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='SET NULL'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    product = db.relationship('Product', lazy='selectin')
    
    # Индекс для часто используемой комбинации полей
    __table_args__ = (
        Index('idx_orderitem_order_product', 'order_id', 'product_id'),
    )
    
    def __repr__(self):
        return f'<OrderItem {self.id}>' 