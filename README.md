# pyHydrogen

An interactive desktop application for visualising hydrogen atom wavefunctions
and energy levels. Built for physics students to explore quantum mechanics
through real-time 3D orbital plots.

## Features

- **3D Probability Density** — Interactive isosurface plots of |&psi;|&sup2;
  rendered with Plotly.js
- **Radial Distribution** — 2D plots of P(r) = r&sup2;|R(r)|&sup2; showing
  where electrons are most likely to be found
- **Energy Level Diagram** — Dynamic visualisation of E_n = -13.6 eV / n&sup2;
  with the selected state highlighted
- **Quantum Number Controls** — Cascading dropdowns for n, l, m with
  automatic validation of selection rules
- **Dark Theme** — Modern navy/coral interface designed for comfortable use

## Quick Start

```bash
# Clone the repository
git clone https://github.com/stanfordbshan/pyHydrogen.git
cd pyHydrogen

# Create and activate the conda environment
conda env create -f environment.yml
conda activate pyhydrogen

# Launch the application
cd src
python -m pyhydrogen.main
```

## Requirements

- Python &ge; 3.10, < 3.13
- numpy, scipy, pywebview

All dependencies are handled by the conda environment file. See
`environment.yml` for details.

## Project Structure

```
src/pyhydrogen/
├── core/physics_engine.py   # Wavefunction math (numpy/scipy)
├── api/bridge.py            # pywebview JS ↔ Python bridge
├── gui/assets/              # HTML, CSS, JS frontend
└── main.py                  # Entry point
```

## How It Works

The application uses **pywebview** to create a native desktop window that
renders an HTML/JS frontend. The frontend communicates with a Python backend
through pywebview's JavaScript API bridge:

1. The student selects quantum numbers (n, l, m) in the UI.
2. JavaScript calls Python methods via `pywebview.api.*()`.
3. Python computes wavefunctions using analytical solutions (associated
   Laguerre polynomials and spherical harmonics).
4. Results are returned as JSON and rendered as interactive Plotly.js charts.

## License

MIT
