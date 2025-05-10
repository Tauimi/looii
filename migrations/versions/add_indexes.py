"""Add indexes to models

Revision ID: add_indexes
Revises: 
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_indexes'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Product indexes
    op.create_index('ix_product_name', 'product', ['name'])
    op.create_index('ix_product_price', 'product', ['price'])
    op.create_index('ix_product_stock', 'product', ['stock'])
    op.create_index('ix_product_category_id', 'product', ['category_id'])
    op.create_index('ix_product_date_added', 'product', ['date_added'])
    op.create_index('idx_product_category_price', 'product', ['category_id', 'price'])
    op.create_index('idx_product_stock_date', 'product', ['stock', 'date_added'])
    
    # Category indexes
    op.create_index('ix_category_name', 'category', ['name'])
    
    # Order indexes
    op.create_index('ix_order_user_id', 'order', ['user_id'])
    op.create_index('ix_order_total_amount', 'order', ['total_amount'])
    op.create_index('ix_order_order_date', 'order', ['order_date'])
    op.create_index('ix_order_status', 'order', ['status'])
    op.create_index('idx_order_user_date', 'order', ['user_id', 'order_date'])
    op.create_index('idx_order_status_date', 'order', ['status', 'order_date'])
    
    # OrderItem indexes
    op.create_index('ix_orderitem_order_id', 'order_item', ['order_id'])
    op.create_index('ix_orderitem_product_id', 'order_item', ['product_id'])
    op.create_index('idx_orderitem_order_product', 'order_item', ['order_id', 'product_id'])
    
    # User indexes
    op.create_index('ix_user_username', 'user', ['username'])
    op.create_index('ix_user_email', 'user', ['email'])
    op.create_index('ix_user_phone', 'user', ['phone'])
    op.create_index('ix_user_date_registered', 'user', ['date_registered'])
    op.create_index('idx_user_name_email', 'user', ['username', 'email'])
    op.create_index('idx_user_registration', 'user', ['date_registered'])
    
    # Visitor indexes
    op.create_index('ix_visitor_ip_address', 'visitor', ['ip_address'])
    op.create_index('ix_visitor_session_id', 'visitor', ['session_id'])
    op.create_index('ix_visitor_first_visit', 'visitor', ['first_visit'])
    op.create_index('ix_visitor_last_visit', 'visitor', ['last_visit'])
    op.create_index('ix_visitor_user_id', 'visitor', ['user_id'])
    op.create_index('idx_visitor_dates', 'visitor', ['first_visit', 'last_visit'])
    op.create_index('idx_visitor_user_session', 'visitor', ['user_id', 'session_id'])

def downgrade():
    # Product indexes
    op.drop_index('ix_product_name', table_name='product')
    op.drop_index('ix_product_price', table_name='product')
    op.drop_index('ix_product_stock', table_name='product')
    op.drop_index('ix_product_category_id', table_name='product')
    op.drop_index('ix_product_date_added', table_name='product')
    op.drop_index('idx_product_category_price', table_name='product')
    op.drop_index('idx_product_stock_date', table_name='product')
    
    # Category indexes
    op.drop_index('ix_category_name', table_name='category')
    
    # Order indexes
    op.drop_index('ix_order_user_id', table_name='order')
    op.drop_index('ix_order_total_amount', table_name='order')
    op.drop_index('ix_order_order_date', table_name='order')
    op.drop_index('ix_order_status', table_name='order')
    op.drop_index('idx_order_user_date', table_name='order')
    op.drop_index('idx_order_status_date', table_name='order')
    
    # OrderItem indexes
    op.drop_index('ix_orderitem_order_id', table_name='order_item')
    op.drop_index('ix_orderitem_product_id', table_name='order_item')
    op.drop_index('idx_orderitem_order_product', table_name='order_item')
    
    # User indexes
    op.drop_index('ix_user_username', table_name='user')
    op.drop_index('ix_user_email', table_name='user')
    op.drop_index('ix_user_phone', table_name='user')
    op.drop_index('ix_user_date_registered', table_name='user')
    op.drop_index('idx_user_name_email', table_name='user')
    op.drop_index('idx_user_registration', table_name='user')
    
    # Visitor indexes
    op.drop_index('ix_visitor_ip_address', table_name='visitor')
    op.drop_index('ix_visitor_session_id', table_name='visitor')
    op.drop_index('ix_visitor_first_visit', table_name='visitor')
    op.drop_index('ix_visitor_last_visit', table_name='visitor')
    op.drop_index('ix_visitor_user_id', table_name='visitor')
    op.drop_index('idx_visitor_dates', table_name='visitor')
    op.drop_index('idx_visitor_user_session', table_name='visitor') 