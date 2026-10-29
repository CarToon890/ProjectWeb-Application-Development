"""user-to-user second-hand furniture marketplace"""
from alembic import op
import sqlalchemy as sa

revision = "0003_user_marketplace"
down_revision = "0002_add_performance_indexes"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("marketlisting",
        sa.Column("id",sa.Integer(),primary_key=True),sa.Column("seller_id",sa.Integer(),sa.ForeignKey("user.id"),nullable=False),
        sa.Column("title",sa.String(),nullable=False),sa.Column("furniture_type",sa.String(),nullable=False),sa.Column("condition",sa.String(),nullable=False),
        sa.Column("description",sa.String(),nullable=False),sa.Column("price",sa.Integer(),nullable=False),sa.Column("image_url",sa.String()),
        sa.Column("status",sa.String(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    op.create_index("ix_marketlisting_seller_id","marketlisting",["seller_id"]); op.create_index("ix_marketlisting_status","marketlisting",["status"])
    op.create_table("marketchat",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("listing_id",sa.Integer(),sa.ForeignKey("marketlisting.id"),nullable=False),sa.Column("buyer_id",sa.Integer(),sa.ForeignKey("user.id"),nullable=False),sa.Column("seller_id",sa.Integer(),sa.ForeignKey("user.id"),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    for col in ("listing_id","buyer_id","seller_id"): op.create_index(f"ix_marketchat_{col}","marketchat",[col])
    op.create_table("marketmessage",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("chat_id",sa.Integer(),sa.ForeignKey("marketchat.id"),nullable=False),sa.Column("sender_id",sa.Integer(),sa.ForeignKey("user.id"),nullable=False),sa.Column("body",sa.String(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    for col in ("chat_id","sender_id"): op.create_index(f"ix_marketmessage_{col}","marketmessage",[col])
    op.create_table("marketorder",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("listing_id",sa.Integer(),sa.ForeignKey("marketlisting.id"),nullable=False),sa.Column("buyer_id",sa.Integer(),sa.ForeignKey("user.id"),nullable=False),sa.Column("seller_id",sa.Integer(),sa.ForeignKey("user.id"),nullable=False),sa.Column("item_price",sa.Integer(),nullable=False),sa.Column("shipping_fee",sa.Integer(),nullable=False),sa.Column("address",sa.String(),nullable=False),sa.Column("status",sa.String(),nullable=False),sa.Column("payment_proof_url",sa.String()),sa.Column("rejection_reason",sa.String()),sa.Column("carrier",sa.String()),sa.Column("tracking_number",sa.String()),sa.Column("refund_reason",sa.String()),sa.Column("refund_proof_url",sa.String()),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    for col in ("listing_id","buyer_id","seller_id","status"): op.create_index(f"ix_marketorder_{col}","marketorder",[col])

def downgrade():
    op.drop_table("marketorder"); op.drop_table("marketmessage"); op.drop_table("marketchat"); op.drop_table("marketlisting")
