"""initial baseline

Revision ID: 0001_initial_baseline
Revises: 
Create Date: 2026-08-22 01:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '0001_initial_baseline'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create table 'user'
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('password_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('full_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('phone', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('address', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('role', sqlmodel.sql.sqltypes.AutoString(), server_default='user', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)

    # 2. Create table 'product'
    op.create_table(
        'product',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('category', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('image_url', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('stock', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Create table 'timeslot'
    op.create_table(
        'timeslot',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('datetime', sa.DateTime(), nullable=False),
        sa.Column('technician_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('is_available', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. Create table 'item'
    op.create_table(
        'item',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('furniture_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('condition', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('photo_url', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('estimated_price', sa.Integer(), nullable=False),
        sa.Column('co2_saved_kg', sa.Float(), nullable=False),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), server_default='pending', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. Create table 'booking'
    op.create_table(
        'booking',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('timeslot_id', sa.Integer(), nullable=False),
        sa.Column('address', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('total_price', sa.Integer(), nullable=False),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), server_default='pending', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
        sa.ForeignKeyConstraint(['timeslot_id'], ['timeslot.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_booking_timeslot_active_unique',
        'booking',
        ['timeslot_id'],
        unique=True,
        postgresql_where=sa.text("status != 'cancelled'")
    )


def downgrade() -> None:
    op.drop_index('ix_booking_timeslot_active_unique', table_name='booking', postgresql_where=sa.text("status != 'cancelled'"))
    op.drop_table('booking')
    op.drop_table('item')
    op.drop_table('timeslot')
    op.drop_table('product')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
