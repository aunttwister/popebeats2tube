"""init

Revision ID: 20b8d3935aed
Revises: 
Create Date: 2025-01-07 11:10:08.546448

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20b8d3935aed'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('youtube_access_token', sa.String(length=512), nullable=True),
    sa.Column('youtube_refresh_token', sa.String(length=512), nullable=True),
    sa.Column('youtube_token_expiry', sa.DateTime(), nullable=True),
    sa.Column('date_created', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('tunes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('upload_date', sa.DateTime(), nullable=True),
    sa.Column('executed', sa.Boolean(), nullable=True),
    sa.Column('video_title', sa.String(length=255), nullable=True),
    sa.Column('base_dest_path', sa.String(length=512), nullable=True),
    sa.Column('img_name', sa.String(length=255), nullable=True),
    sa.Column('img_type', sa.String(length=64), nullable=True),
    sa.Column('audio_name', sa.String(length=255), nullable=True),
    sa.Column('audio_type', sa.String(length=64), nullable=True),
    sa.Column('tags', sa.String(length=1024), nullable=True),
    sa.Column('category', sa.String(length=128), nullable=True),
    sa.Column('privacy_status', sa.String(length=32), nullable=True),
    sa.Column('embeddable', sa.Boolean(), nullable=True),
    sa.Column('license', sa.String(length=64), nullable=True),
    sa.Column('video_description', sa.String(length=1024), nullable=True),
    sa.Column('user_id', sa.String(length=36), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tunes_id'), 'tunes', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_tunes_id'), table_name='tunes')
    op.drop_table('tunes')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
