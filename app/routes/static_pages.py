from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import Category, Product
from app.utils.session_helpers import record_page_visit

bp = Blueprint('static_pages', __name__)

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        # Здесь можно добавить код для отправки сообщения на почту
        
        flash('Ваше сообщение отправлено!', 'success')
        return redirect(url_for('static_pages.contact'))
    
    record_page_visit('contact')
    
    return render_template('contact.html', title="Контакты")

@bp.route('/about')
def about():
    record_page_visit('about')
    
    return render_template('about.html', title="О компании")

@bp.route('/delivery')
def delivery():
    record_page_visit('delivery')
    
    return render_template('delivery.html', title="Доставка и оплата")

@bp.route('/sitemap')
def sitemap():
    categories = Category.query.all()
    popular_products = Product.query.order_by(Product.date_added.desc()).limit(10).all()
    
    record_page_visit('sitemap')
    
    return render_template('sitemap.html', categories=categories, popular_products=popular_products, title="Карта сайта")

@bp.route('/warranty')
def warranty():
    record_page_visit('warranty')
    return render_template('warranty.html', title="Гарантия и сервис")

@bp.route('/returns')
def returns():
    record_page_visit('returns')
    return render_template('returns.html', title="Возврат и обмен")

@bp.route('/privacy')
def privacy():
    record_page_visit('privacy')
    return render_template('privacy.html', title="Политика конфиденциальности")

@bp.route('/terms')
def terms():
    record_page_visit('terms')
    return render_template('terms.html', title="Пользовательское соглашение")

@bp.route('/faq')
def faq():
    record_page_visit('faq')
    return render_template('faq.html', title="Часто задаваемые вопросы") 