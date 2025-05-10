from app import db
from app.models import Category, Product, User
from sqlalchemy import inspect
from datetime import datetime

def create_initial_data():
    # Проверяем есть ли уже данные в БД
    if Category.query.count() > 0:
        return
    
    # Добавляем категории
    categories = [
        {'name': 'Смартфоны', 'description': 'Мобильные телефоны и смартфоны'},
        {'name': 'Ноутбуки', 'description': 'Ноутбуки и аксессуары'},
        {'name': 'Телевизоры', 'description': 'Телевизоры и аксессуары'},
        {'name': 'Холодильники', 'description': 'Холодильники и морозильники'},
        {'name': 'Стиральные машины', 'description': 'Стиральные и сушильные машины'},
        {'name': 'Планшеты', 'description': 'Планшеты и электронные книги'},
        {'name': 'Аудиотехника', 'description': 'Наушники, колонки и акустические системы'}
    ]
    
    for cat_data in categories:
        category = Category(name=cat_data['name'], description=cat_data['description'])
        db.session.add(category)
    
    db.session.commit()
    
    # Добавляем примеры товаров
    products = [
        # Смартфоны (категория 1)
        {'name': 'Смартфон Samsung Galaxy S21', 'description': 'Флагманский смартфон с мощным процессором', 'price': 59990, 'category_id': 1, 'stock': 10, 'image': 'samsung_s21.jpg'},
        {'name': 'Смартфон iPhone 13', 'description': 'Современный смартфон с отличной камерой', 'price': 79990, 'category_id': 1, 'stock': 7, 'image': 'iphone_13.jpg'},
        {'name': 'Смартфон Xiaomi Redmi Note 10', 'description': 'Доступный смартфон с хорошей производительностью', 'price': 19990, 'category_id': 1, 'stock': 15, 'image': 'xiaomi_redmi.jpg'},
        {'name': 'Смартфон OnePlus 9', 'description': 'Флагманский смартфон с Hasselblad камерой', 'price': 54990, 'category_id': 1, 'stock': 6, 'image': 'oneplus_9.jpg'},
        {'name': 'Смартфон Google Pixel 6', 'description': 'Смартфон с чистым Android и отличной камерой', 'price': 49990, 'category_id': 1, 'stock': 8, 'image': 'pixel_6.jpg'},
        
        # Ноутбуки (категория 2)
        {'name': 'Ноутбук ASUS ZenBook', 'description': 'Ультрабук с IPS экраном и Core i7', 'price': 89990, 'category_id': 2, 'stock': 5, 'image': 'asus_zenbook.jpg'},
        {'name': 'Ноутбук Lenovo ThinkPad', 'description': 'Надежный бизнес-ноутбук', 'price': 99990, 'category_id': 2, 'stock': 3, 'image': 'lenovo_thinkpad.jpg'},
        {'name': 'Ноутбук Apple MacBook Air M1', 'description': 'Ультратонкий ноутбук с процессором Apple M1', 'price': 109990, 'category_id': 2, 'stock': 7, 'image': 'macbook_air.jpg'},
        {'name': 'Ноутбук Dell XPS 13', 'description': 'Премиальный ультрабук с безрамочным дисплеем', 'price': 119990, 'category_id': 2, 'stock': 4, 'image': 'dell_xps.jpg'},
        {'name': 'Ноутбук HP Spectre x360', 'description': 'Трансформер премиум-класса с сенсорным экраном', 'price': 104990, 'category_id': 2, 'stock': 6, 'image': 'hp_spectre.jpg'},
    ]
    
    for prod_data in products:
        product = Product(
            name=prod_data['name'],
            description=prod_data['description'],
            price=prod_data['price'],
            category_id=prod_data['category_id'],
            stock=prod_data['stock'],
            image=prod_data['image']
        )
        db.session.add(product)
    
    # Создаем тестового администратора
    admin = User(
        username='admin',
        email='admin@tehnomarket.ru',
        first_name='Админ',
        last_name='Администраторов'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    db.session.commit()
    print("База данных заполнена начальными данными") 