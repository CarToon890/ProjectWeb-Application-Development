"""add performance indexes

Revision ID: 0002_add_performance_indexes
Revises: 0001_initial_baseline
Create Date: 2026-10-03 12:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002_add_performance_indexes'
down_revision: Union[str, None] = '0001_initial_baseline'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Indexes on 'item'
    op.create_index(op.f('ix_item_user_id'), 'item', ['user_id'], unique=False)
    op.create_index(op.f('ix_item_status'), 'item', ['status'], unique=False)

    # 2. Indexes on 'product'
    op.create_index(op.f('ix_product_category'), 'product', ['category'], unique=False)

    # 3. Composite Index on 'timeslot' for availability filtering & datetime ordering
    op.create_index('ix_timeslot_available_datetime', 'timeslot', ['is_available', 'datetime'], unique=False)

    # 4. Indexes on 'booking'
    op.create_index(op.f('ix_booking_user_id'), 'booking', ['user_id'], unique=False)
    op.create_index(op.f('ix_booking_item_id'), 'booking', ['item_id'], unique=False)
    op.create_index(op.f('ix_booking_timeslot_id'), 'booking', ['timeslot_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_booking_timeslot_id'), table_name='booking')
    op.drop_index(op.f('ix_booking_item_id'), table_name='booking')
    op.drop_index(op.f('ix_booking_user_id'), table_name='booking')
    op.drop_index('ix_timeslot_available_datetime', table_name='timeslot')
    op.drop_index(op.f('ix_product_category'), table_name='product')
    op.drop_index(op.f('ix_item_status'), table_name='item')
    op.drop_index(op.f('ix_item_user_id'), table_name='item')
