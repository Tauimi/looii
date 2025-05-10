from app.extensions import db
from datetime import datetime
from sqlalchemy import Index
from app.utils.cache import cache_with_args, cache_with_key

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    products = db.relationship('Product', backref='category', lazy='selectin', cascade='all, delete-orphan')
    
    @classmethod
    @cache_with_key('category', timeout=3600)
    def get_all_categories(cls):
        """Получить все категории с кэшированием"""
        return cls.query.all()
    
    @classmethod
    @cache_with_key('category_by_id', timeout=3600)
    def get_by_id(cls, category_id):
        """Получить категорию по ID с кэшированием"""
        return cls.query.get(category_id)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False, index=True)
    image = db.Column(db.String(200), default='default_product.jpg')
    stock = db.Column(db.Integer, default=0, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='CASCADE'), nullable=False, index=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Индексы для часто используемых комбинаций полей
    __table_args__ = (
        Index('idx_product_category_price', 'category_id', 'price'),
        Index('idx_product_stock_date', 'stock', 'date_added'),
    )
    
    @classmethod
    @cache_with_key('product_by_id', timeout=3600)
    def get_by_id(cls, product_id):
        """Получить продукт по ID с кэшированием"""
        return cls.query.get(product_id)
    
    @classmethod
    @cache_with_key('products_by_category', timeout=1800)
    def get_by_category(cls, category_id):
        """Получить все продукты категории с кэшированием"""
        return cls.query.filter_by(category_id=category_id).all()
    
    @classmethod
    @cache_with_key('products_in_stock', timeout=1800)
    def get_in_stock(cls):
        """Получить все продукты в наличии с кэшированием"""
        return cls.query.filter(cls.stock > 0).all()
    
    @classmethod
    @cache_with_key('products_new', timeout=1800)
    def get_new_products(cls, limit=8):
        """Получить новые продукты с кэшированием"""
        return cls.query.order_by(cls.date_added.desc()).limit(limit).all()
    
    def __repr__(self):
        return f'<Product {self.name}>' 