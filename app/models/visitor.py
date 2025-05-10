from app.extensions import db
from datetime import datetime, timedelta
import uuid
from sqlalchemy import Index, func
from app.utils.cache import cache_with_key

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), index=True)
    user_agent = db.Column(db.String(200))
    session_id = db.Column(db.String(100), nullable=True, index=True)
    first_visit = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    last_visit = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    visit_count = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), unique=True, nullable=True, index=True)
    
    # Индексы для часто используемых комбинаций полей
    __table_args__ = (
        Index('idx_visitor_dates', 'first_visit', 'last_visit'),
        Index('idx_visitor_user_session', 'user_id', 'session_id'),
    )
    
    @staticmethod
    @cache_with_key('visitor_stats', timeout=300)  # Кэшируем на 5 минут
    def get_visitors_stats():
        """Получает статистику посещений за разные периоды"""
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Используем один запрос для получения всех статистик
        stats = db.session.query(
            func.count(Visitor.id).label('total'),
            func.count(db.case([(Visitor.last_visit >= yesterday, 1)])).label('today'),
            func.count(db.case([(Visitor.last_visit >= week_ago, 1)])).label('week'),
            func.count(db.case([(Visitor.last_visit >= month_ago, 1)])).label('month'),
            func.sum(Visitor.visit_count).label('total_visits')
        ).first()
        
        return {
            'total': stats.total or 0,
            'today': stats.today or 0,
            'week': stats.week or 0,
            'month': stats.month or 0,
            'total_visits': stats.total_visits or 0
        }
    
    @classmethod
    def record_visit(cls, ip_address, user_agent, current_flask_session_id=None, user_id=None):
        visitor_record = None
        final_session_id_for_flask = current_flask_session_id

        if user_id:
            # Пользователь авторизован, ищем или создаем его каноническую запись
            visitor_record = cls.query.filter_by(user_id=user_id).first()
            if not visitor_record:
                visitor_record = cls(user_id=user_id, first_visit=datetime.utcnow())
                db.session.add(visitor_record)

            if current_flask_session_id:
                # Ищем анонимную сессию, если есть current_flask_session_id
                anonymous_session_record = cls.query.filter_by(session_id=current_flask_session_id).filter(cls.user_id.is_(None)).first()
                if anonymous_session_record:
                    # Объединяем анонимную сессию с записью пользователя
                    if visitor_record.visit_count is None:
                        visitor_record.visit_count = 0
                    if anonymous_session_record.visit_count is not None:
                        visitor_record.visit_count += anonymous_session_record.visit_count
                    visitor_record.first_visit = min(visitor_record.first_visit, anonymous_session_record.first_visit)
                    db.session.delete(anonymous_session_record)
                    visitor_record.session_id = current_flask_session_id
                    final_session_id_for_flask = current_flask_session_id
                else:
                    # Проверяем, не принадлежит ли current_flask_session_id другому пользователю
                    other_user_with_session = cls.query.filter(
                        cls.session_id == current_flask_session_id, 
                        cls.user_id.isnot(None), 
                        cls.user_id != user_id
                    ).first()

                    if other_user_with_session:
                        # Если session_id принадлежит другому пользователю, генерируем новый
                        visitor_record.session_id = str(uuid.uuid4())
                        final_session_id_for_flask = visitor_record.session_id
                    else:
                        visitor_record.session_id = current_flask_session_id
                        final_session_id_for_flask = current_flask_session_id
            
            elif not visitor_record.session_id:
                visitor_record.session_id = str(uuid.uuid4())
            
            final_session_id_for_flask = visitor_record.session_id

        else:  # Анонимный пользователь
            if current_flask_session_id:
                # Ищем существующую АНОНИМНУЮ сессию
                visitor_record = cls.query.filter_by(session_id=current_flask_session_id).filter(cls.user_id.is_(None)).first()
                if visitor_record:
                    final_session_id_for_flask = current_flask_session_id
                else:
                    # Если сессия не найдена, создаем новую
                    visitor_record = cls(session_id=current_flask_session_id, first_visit=datetime.utcnow())
                    db.session.add(visitor_record)
                    final_session_id_for_flask = current_flask_session_id
            else:
                # Если нет session_id, создаем новую запись
                new_session_id = str(uuid.uuid4())
                visitor_record = cls(session_id=new_session_id, first_visit=datetime.utcnow())
                db.session.add(visitor_record)
                final_session_id_for_flask = new_session_id

        # Обновляем статистику
        if visitor_record:
            visitor_record.last_visit = datetime.utcnow()
            if visitor_record.visit_count is None:
                visitor_record.visit_count = 1
            else:
                visitor_record.visit_count += 1
            visitor_record.ip_address = ip_address
            visitor_record.user_agent = user_agent
        else:
            # Создаем новую запись, если по какой-то причине visitor_record не определена
            new_session_id = str(uuid.uuid4())
            visitor_record = cls(
                session_id=new_session_id,
                user_id=user_id,
                first_visit=datetime.utcnow(),
                ip_address=ip_address,
                user_agent=user_agent,
                visit_count=1
            )
            db.session.add(visitor_record)
            final_session_id_for_flask = new_session_id
            
        try:
            db.session.commit()
            # Очищаем кэш статистики после успешного обновления
            from app.utils.cache import clear_cache_by_prefix
            clear_cache_by_prefix('visitor_stats')
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при записи посещения: {str(e)}")
            # В случае ошибки возвращаем текущий session_id
            return current_flask_session_id
            
        return final_session_id_for_flask
        
    def __repr__(self):
        return f'<Visitor {self.id}>' 