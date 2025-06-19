from importlib import import_module

# Re-export all names from the package inside src so `python -m fueltracker`
# works without installation.
_module = import_module('src.fueltracker')
__all__ = getattr(_module, '__all__', [])
for attr in dir(_module):
    if attr.startswith('_'):  # skip private attributes
        continue
    globals()[attr] = getattr(_module, attr)
