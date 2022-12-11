"""empty message

Revision ID: 41d840545e66
Revises: 
Create Date: 2022-12-05 22:11:46.273015

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '41d840545e66'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('phone', sa.String(), nullable=False),
    sa.Column('role', sa.Enum('boss', 'deputy_boss', 'manager', 'store_keeper', 'retailer', 'kitchen', 'eservices', 'cashier', 'no_role', name='roles'), server_default='no_role', nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone')
    )
    op.create_table('cash',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('label', sa.Enum('sale', 'eservice', 'purchase', name='cashlabel'), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('label_id', sa.String(), nullable=False),
    sa.Column('creator', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['creator'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('label_id')
    )
    op.create_table('e_services',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('creator', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['creator'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sale_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('unit', sa.String(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('creator', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['creator'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('stock_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('unit', sa.String(), nullable=False),
    sa.Column('creator', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['creator'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('kitchen_products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Float(), nullable=False),
    sa.Column('creator', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['creator'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['item_id'], ['sale_items.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('material_requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('stock_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Float(), nullable=False),
    sa.Column('creator', sa.Integer(), nullable=False),
    sa.Column('tag', sa.String(), nullable=True),
    sa.Column('accepted', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['creator'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['stock_id'], ['stock_items.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('requisitions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('stock_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Float(), nullable=False),
    sa.Column('creator', sa.Integer(), nullable=False),
    sa.Column('tag', sa.String(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['creator'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['stock_id'], ['stock_items.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sales',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Float(), nullable=False),
    sa.Column('creator', sa.Integer(), nullable=True),
    sa.Column('tag', sa.String(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['creator'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['item_id'], ['sale_items.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sales')
    op.drop_table('requisitions')
    op.drop_table('material_requests')
    op.drop_table('kitchen_products')
    op.drop_table('stock_items')
    op.drop_table('sale_items')
    op.drop_table('e_services')
    op.drop_table('cash')
    op.drop_table('users')
    # ### end Alembic commands ###