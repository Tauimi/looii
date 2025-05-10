from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.user import User
from app.models.order import Order
from app import db
from app.utils.decorators import login_required
from app.utils.session_helpers import record_page_visit

bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.route('/')
@login_required
def index():
    user = User.query.get(session['user_id'])
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.order_date.desc()).all()
    
    record_page_visit('profile')
    return render_template('profile.html', title='Личный кабинет', user=user, orders=orders)

@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.phone = request.form.get('phone')
        user.address = request.form.get('address')
        user.city = request.form.get('city')
        user.postal_code = request.form.get('postal_code')
        
        # Проверка изменения пароля
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if current_password and new_password and confirm_password:
            if not user.check_password(current_password):
                flash('Текущий пароль введен неверно', 'danger')
                return render_template('edit_profile.html', title='Редактирование профиля', user=user)
                
            if new_password != confirm_password:
                flash('Новые пароли не совпадают', 'danger')
                return render_template('edit_profile.html', title='Редактирование профиля', user=user)
                
            user.set_password(new_password)
            
        db.session.commit()
        flash('Профиль успешно обновлен', 'success')
        return redirect(url_for('profile.index'))
    
    record_page_visit('edit_profile')
    return render_template('edit_profile.html', title='Редактирование профиля', user=user) 