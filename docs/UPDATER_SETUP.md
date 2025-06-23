# TUF Update Repository Setup

```bash
# One-time setup for the FuelTracker update repository
# Create repository structure
mkdir fueltracker-updates && cd fueltracker-updates

# Generate signing keys
tufup repo keys create root.ed25519
tufup repo keys create targets.ed25519

# Initialize repository metadata
tufup repo init FuelTracker

# Register keys
tufup repo keys add root root.ed25519.pub
tufup repo keys add targets targets.ed25519.pub

# Sign initial metadata
tufup repo sign root
tufup repo sign targets
```
