"""Initial database

Revision ID: e87b89623b31
Revises:
Create Date: 2022-12-27 12:58:12.980436

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e87b89623b31'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('message_id', sa.String(), nullable=True),
    sa.Column('topic', sa.String(), nullable=True),
    sa.Column('done', sa.Boolean(), nullable=True),
    sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('message_id')
    )
    op.create_table('tickets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rhbz_id', sa.Integer(), nullable=False),
    sa.Column('owner', sa.String(), nullable=True),
    sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('rhbz_id')
    )
    op.create_table('builds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bugzilla_message_id', sa.Integer(), nullable=True),
    sa.Column('copr_message_id', sa.Integer(), nullable=True),
    sa.Column('ticket_id', sa.Integer(), nullable=True),
    sa.Column('spec_url', sa.String(), nullable=True),
    sa.Column('srpm_url', sa.String(), nullable=True),
    sa.Column('copr_build_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('ok', 'copr_build_failed', 'review_failed', name='status'), nullable=True),
    sa.Column('issues', sa.String(), nullable=True),
    sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['bugzilla_message_id'], ['messages.id'], ),
    sa.ForeignKeyConstraint(['copr_message_id'], ['messages.id'], ),
    sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('builds')
    op.drop_table('tickets')
    op.drop_table('messages')
