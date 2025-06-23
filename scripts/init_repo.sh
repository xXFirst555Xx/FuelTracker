#!/usr/bin/env sh
# One-time setup for tufup repository
set -e

# create update repository
mkdir -p fueltracker-updates
cd fueltracker-updates

tufup repo init FuelTracker

tufup repo keys create root.ed25519
tufup repo keys create targets.ed25519

tufup repo keys add root root.ed25519.pub
tufup repo keys add targets targets.ed25519.pub

tufup repo sign root
tufup repo sign targets
