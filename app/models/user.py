from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import Index

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20), index=True)
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    date_registered = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    orders = db.relationship('Order', backref='customer', lazy='selectin', cascade='all, delete-orphan')
    
    # Индексы для часто используемых комбинаций полей
    __table_args__ = (
        Index('idx_user_name_email', 'username', 'email'),
        Index('idx_user_registration', 'date_registered'),
    )
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def __repr__(self):
        return f'<User {self.username}>' 