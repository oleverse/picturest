"""create roles

Revision ID: 6e01e4b0bba8
Revises: 256b44b492b4
Create Date: 2023-07-31 03:47:46.471376

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from api.database.models import RoleNames, Role


# revision identifiers, used by Alembic.
revision = '6e01e4b0bba8'
down_revision = '256b44b492b4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("roles", sa.Column('can_change_user_role', sa.Boolean(), nullable=False, default=False))
    roles_table = table(
        "roles",
        column("name", sa.String),
        column("can_post_own_pict", sa.Boolean),
        column("can_del_own_pict", sa.Boolean),
        column("can_mod_own_pict", sa.Boolean),
        column("can_post_own_comment", sa.Boolean),
        column("can_mod_own_comment", sa.Boolean),
        column("can_del_own_comment", sa.Boolean),
        column("can_post_tag", sa.Boolean),
        column("can_mod_tag", sa.Boolean),
        column("can_del_tag", sa.Boolean),
        column("can_post_not_own_pict", sa.Boolean),
        column("can_mod_not_own_pict", sa.Boolean),
        column("can_del_not_own_pict", sa.Boolean),
        column("can_post_not_own_comment", sa.Boolean),
        column("can_mod_not_own_comment", sa.Boolean),
        column("can_del_not_own_comment", sa.Boolean),
        column("can_change_user_role", sa.Boolean)
    )
    op.bulk_insert(
        roles_table,
        [
            {
                "name": f"{RoleNames.admin.name}",
                "can_post_own_pict": True,
                "can_del_own_pict": True,
                "can_mod_own_pict": True,
                "can_post_own_comment": True,
                "can_mod_own_comment": True,
                "can_del_own_comment": True,
                "can_post_tag": True,
                "can_mod_tag": True,
                "can_del_tag": True,
                "can_post_not_own_pict": True,
                "can_mod_not_own_pict": True,
                "can_del_not_own_pict": True,
                "can_post_not_own_comment": True,
                "can_mod_not_own_comment": True,
                "can_del_not_own_comment": True,
                "can_change_user_role": True
            },
            {
                "name": f"{RoleNames.moderator.name}",
                "can_post_own_pict": True,
                "can_del_own_pict": True,
                "can_mod_own_pict": True,
                "can_post_own_comment": True,
                "can_mod_own_comment": True,
                "can_del_own_comment": True,
                "can_post_tag": True,
                "can_mod_tag": True,
                "can_del_tag": True,
                "can_post_not_own_pict": True,
                "can_mod_not_own_pict": True,
                "can_del_not_own_pict": True,
                "can_post_not_own_comment": True,
                "can_mod_not_own_comment": True,
                "can_del_not_own_comment": True,
                "can_change_user_role": False
            },
            {
                "name": f"{RoleNames.user.name}",
                "can_post_own_pict": True,
                "can_del_own_pict": True,
                "can_mod_own_pict": True,
                "can_post_own_comment": True,
                "can_mod_own_comment": True,
                "can_del_own_comment": False,
                "can_post_tag": True,
                "can_mod_tag": False,
                "can_del_tag": False,
                "can_post_not_own_pict": False,
                "can_mod_not_own_pict": False,
                "can_del_not_own_pict": False,
                "can_post_not_own_comment": False,
                "can_mod_not_own_comment": False,
                "can_del_not_own_comment": False,
                "can_change_user_role": False
            }
        ]
    )


def downgrade() -> None:
    op.drop_column("roles", 'can_change_user_role')
