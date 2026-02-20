# pyHydrogen — Developer Guide

## Overview

Desktop application for visualising hydrogen atom wavefunctions and energy
levels.  Built with a **Python backend** (numpy / scipy for physics) and an
**HTML / CSS / JS frontend** served via **pywebview**.  Interactive 3-D plots
are rendered with **Plotly.js**.

## Quick Start

```bash
# Create the conda environment (first time only)
conda env create -f environment.yml

# Activate the environment
conda activate pyhydrogen

# Run the application
cd src
python -m pyhydrogen.main
```

## Project Layout

```
src/pyhydrogen/
├── core/
│   └── physics_engine.py   # PhysicsEngine — all wavefunction math (pure numpy/scipy)
├── api/
│   └── bridge.py           # HydrogenAPI — pywebview js_api bridge
├── gui/
│   └── assets/
│       ├── index.html      # Main HTML page
│       ├── css/style.css   # Dark theme styles
│       └── js/app.js       # Frontend logic + Plotly rendering
└── main.py                 # Entry point — creates window, starts app
```

## Architecture

```
┌──────────────────────────────────────────────────┐
│  pywebview window                                │
│  ┌────────────────────────────────────────────┐  │
│  │  index.html  +  app.js  +  Plotly.js       │  │
│  │                                            │  │
│  │  pywebview.api.computeIsosurface(n,l,m) ───┼──┼─► HydrogenAPI.computeIsosurface()
│  │  pywebview.api.getQuantumNumbers(n) ───────┼──┼─► HydrogenAPI.getQuantumNumbers()
│  │                                            │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
         JS ←──Promise──→ Python (via pywebview js_api)
```

## API Methods (exposed to JavaScript)

| Method | Parameters | Returns |
|--------|-----------|---------|
| `getQuantumNumbers(n)` | int | `{l_values, m_values_by_l}` |
| `validateQuantumNumbers(n, l, m)` | int, int, int | `{valid, message}` |
| `computeIsosurface(n, l, m, grid_size)` | int×4 | `{x, y, z, value, max_val, grid_size}` |
| `computeRadialDistribution(n, l)` | int, int | `{r, P_r}` |
| `getEnergyLevels(max_n)` | int | `{levels, unit}` |
| `getOrbitalLabel(n, l, m)` | int×3 | `{label}` |

All methods return JSON-serialisable dicts.  Errors: `{"error": "msg"}`.

## Physics Notes

- **Units:** atomic units (Bohr radius a₀ = 1).
- **Radial wavefunction:** `scipy.special.genlaguerre` + `factorial`.
- **Spherical harmonics:** `scipy.special.sph_harm_y(l, m, theta, phi)` —
  uses the **physics convention** (theta = polar, phi = azimuthal).
- **Normalisation:** N_nl = sqrt((2/(n·a₀))³ · (n-l-1)! / (2n · (n+l)!)).
- **Energy eigenvalues:** E_n = −13.6 eV / n².

## Coding Conventions

- **Python internal:** `snake_case` for all private / internal names.
- **JS-exposed API:** `camelCase` (JavaScript convention).
- **numpy → JSON:** always convert with `.tolist()` before returning from API.
- **Error handling:** every API method wraps logic in try/except; returns
  `{"error": str}` instead of raising.

## Environment

- **Conda environment:** `pyhydrogen` (see `environment.yml`)
- **Python:** ≥ 3.10, < 3.13
- **Key dependencies:** numpy, scipy, pywebview

## Testing

```bash
# Verify physics engine normalization
cd <repo-root>
conda activate pyhydrogen
PYTHONPATH=src python -c "
from pyhydrogen.core.physics_engine import PhysicsEngine
from scipy.integrate import quad
e = PhysicsEngine()
for n,l in [(1,0),(2,0),(2,1),(3,0),(3,1),(3,2)]:
    val, _ = quad(lambda r: r**2 * e.radial_wavefunction(r,n,l)**2, 0, 200)
    print(f'R_{n}{l}: integral = {val:.6f}')
"
```
