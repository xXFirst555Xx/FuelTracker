from importlib import util
from pathlib import Path
from typing import TYPE_CHECKING

# Delegate to the top-level Alembic ``env.py`` script.  When running from a
# PyInstaller bundle the package is extracted into a temporary directory
# (``_MEIxxxxx``).  The original ``env.py`` resides one level above the bundled
# ``fueltracker`` package.  In normal source checkouts it lives three levels up.
if not TYPE_CHECKING:
    env_path = Path(__file__).resolve().parents[2] / "alembic" / "env.py"
    if not env_path.exists():
        env_path = Path(__file__).resolve().parents[3] / "alembic" / "env.py"
    spec = util.spec_from_file_location("alembic.env", env_path)
    assert spec is not None
    module = util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    globals().update(module.__dict__)
