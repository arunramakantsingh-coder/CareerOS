"""Merge the global Intelligence registry with the existing M02 profile branch.

Revision ID: 019_global_intelligence_provider_registry
Revises: 018_m02_profile_sections, 018_global_intelligence_provider_registry
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "019_global_intelligence_provider_registry"
down_revision: Union[str, tuple[str, str], None] = (
    "018_m02_profile_sections",
    "018_global_intelligence_provider_registry",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    return name in sa.inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    # The provider registry is created by 018_global_intelligence_provider_registry.
    # This revision intentionally acts as the merge point for both 018 branches.
    if not _has_table("intelligence_provider_configs"):
        raise RuntimeError(
            "Global Intelligence provider registry is missing; expected migration "
            "018_global_intelligence_provider_registry to create it before the merge."
        )


def downgrade() -> None:
    # The merge point owns no schema objects; the two parent revisions own their
    # respective changes and Alembic will downgrade through them independently.
    pass
