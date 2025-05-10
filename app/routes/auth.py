from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.user import User
from app import db
from app.utils.session_helpers import record_page_visit

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('profile.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Проверка данных
        if not all([username, email, password, confirm_password]):
            flash('Пожалуйста, заполните все поля', 'danger')
            return render_template('register.html', title='Регистрация')
            
        if password != confirm_password:
            flash('Пароли не совпадают', 'danger')
            return render_template('register.html', title='Регистрация')
            
        # Проверка уникальности
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            flash('Пользователь с таким именем или email уже существует', 'danger')
            return render_template('register.html', title='Регистрация')
            
        # Создаем нового пользователя
        new_user = User(
            username=username,
            email=email
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь вы можете войти в свой аккаунт.', 'success')
        return redirect(url_for('auth.login'))
        
    record_page_visit('register')
    return render_template('register.html', title='Регистрация')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('profile.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            flash('Вы успешно вошли в аккаунт!', 'success')
            return redirect(url_for('profile.index'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
    
    record_page_visit('login')
    return render_template('login.html', title='Вход')

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Вы вышли из аккаунта', 'success')
    return redirect(url_for('shop.home')) 