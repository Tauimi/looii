from flask import Blueprint, render_template, redirect, url_for, flash, session
from app.models.order import Order
from app.models.user import User
from app.utils.decorators import login_required
from app.utils.session_helpers import record_page_visit

bp = Blueprint('order', __name__, url_prefix='/order')

@bp.route('/<int:order_id>')
@login_required
def detail(order_id):
    user = User.query.get(session['user_id'])
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != user.id:
        flash('У вас нет доступа к этому заказу', 'danger')
        return redirect(url_for('profile.index'))
    
    record_page_visit(f'order_detail/{order_id}')
    return render_template('order_detail.html', title=f'Заказ #{order.id}', order=order)

@bp.route('/success/<int:order_id>')
def success(order_id):
    order = Order.query.get_or_404(order_id)
    record_page_visit(f'order_success/{order_id}')
    return render_template('order_success.html', order=order, title="Заказ оформлен") 