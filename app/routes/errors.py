from flask import Blueprint, render_template, current_app
from app import db
from app.utils.session_helpers import record_page_visit
import os

bp = Blueprint('errors', __name__)

@bp.app_errorhandler(404)
def page_not_found(e):
    try:
        record_page_visit('error_404')
    except Exception as visit_error:
        print(f"Ошибка при записи посещения 404: {str(visit_error)}")
    return render_template('404.html', title='Страница не найдена'), 404

@bp.app_errorhandler(500)
def internal_server_error(e):
    print(f"500 Server Error: {str(e)}")
    try:
        db.session.rollback()  # Откатываем сессию в случае ошибки сервера
    except Exception as db_error:
        print(f"Ошибка при откате транзакции: {str(db_error)}")
    
    try:
        record_page_visit('error_500')
    except Exception as visit_error:
        print(f"Ошибка при записи посещения 500: {str(visit_error)}")
    
    return render_template('500.html', title='Ошибка сервера'), 500

@bp.route('/debug-templates')
def debug_templates():
    """
    Отладочный маршрут для проверки доступности шаблонов
    """
    template_folder = current_app.template_folder
    template_list = os.listdir(template_folder) if os.path.exists(template_folder) else []
    
    debug_info = {
        'template_folder': template_folder,
        'templates_exist': os.path.exists(template_folder),
        'template_list': template_list,
        'absolute_path': os.path.abspath(template_folder),
        'app_root_path': current_app.root_path,
    }
    
    response_html = f"""
    <html>
    <head><title>Debug Templates</title></head>
    <body>
        <h1>Flask Template Debug</h1>
        <ul>
            <li><strong>Template Folder:</strong> {debug_info['template_folder']}</li>
            <li><strong>Templates Exist:</strong> {debug_info['templates_exist']}</li>
            <li><strong>Absolute Path:</strong> {debug_info['absolute_path']}</li>
            <li><strong>App Root Path:</strong> {debug_info['app_root_path']}</li>
        </ul>
        
        <h2>Templates Found ({len(debug_info['template_list'])}):</h2>
        <ul>
    """
    
    for template in debug_info['template_list']:
        response_html += f"<li>{template}</li>"
    
    response_html += """
        </ul>
    </body>
    </html>
    """
    
    return response_html 