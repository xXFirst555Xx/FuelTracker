from pathlib import Path

# Expose our directory and the top-level migrations folder for Alembic
_here = Path(__file__).resolve().parent
_root_migrations = _here.parents[3] / "alembic"
__path__ = [str(_here), str(_root_migrations)]
