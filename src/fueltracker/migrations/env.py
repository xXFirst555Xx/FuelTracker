from importlib import util
from pathlib import Path

# Delegate to the top-level Alembic env script
_env = Path(__file__).resolve().parents[3] / "alembic" / "env.py"
spec = util.spec_from_file_location("alembic.env", _env)
assert spec is not None
module = util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(module)
globals().update(module.__dict__)
