"""pywebview JavaScript ↔ Python API bridge.

The :class:`HydrogenAPI` instance is passed to ``webview.create_window``
via the ``js_api`` parameter.  Every *public* method becomes callable from
the frontend as ``pywebview.api.<methodName>(...)``, returning a Promise
that resolves with the method's return value.

Design rules
------------
* Method names use **camelCase** (JavaScript convention).
* Return values are plain JSON-serialisable types only
  (dict / list / str / int / float / bool / None).
* All numpy arrays MUST be converted with ``.tolist()`` before returning.
* Errors are returned as ``{"error": "<message>"}`` rather than raised.
"""

from __future__ import annotations

from pyhydrogen.core.physics_engine import PhysicsEngine


class HydrogenAPI:
    """Public API surface exposed to the frontend via pywebview."""

    def __init__(self) -> None:
        self._engine = PhysicsEngine()

    # ------------------------------------------------------------------
    # Quantum number helpers
    # ------------------------------------------------------------------

    def getQuantumNumbers(self, n: int) -> dict:  # noqa: N802
        """Return allowed *l* and *m* values for a given *n*.

        Called when the user changes the *n* dropdown so the UI can
        repopulate the *l* and *m* selectors.
        """
        try:
            n = int(n)
            valid, msg = self._engine.validate_quantum_numbers(n, 0, 0)
            if not valid and "n must" in msg:
                return {"error": msg}
            return self._engine.get_allowed_quantum_numbers(n)
        except Exception as exc:
            return {"error": str(exc)}

    def validateQuantumNumbers(  # noqa: N802
        self, n: int, l: int, m: int
    ) -> dict:
        """Validate a (n, l, m) triplet and return the result."""
        try:
            valid, msg = self._engine.validate_quantum_numbers(
                int(n), int(l), int(m)
            )
            return {"valid": valid, "message": msg}
        except Exception as exc:
            return {"valid": False, "message": str(exc)}

    # ------------------------------------------------------------------
    # Heavy computations
    # ------------------------------------------------------------------

    def computeIsosurface(  # noqa: N802
        self, n: int, l: int, m: int, grid_size: int = 40
    ) -> dict:
        """Compute 3-D probability density for Plotly isosurface rendering.

        Returns flat x/y/z/value arrays plus ``max_val``.
        """
        try:
            n, l, m, grid_size = int(n), int(l), int(m), int(grid_size)
            valid, msg = self._engine.validate_quantum_numbers(n, l, m)
            if not valid:
                return {"error": msg}
            return self._engine.probability_density_3d(n, l, m, grid_size)
        except Exception as exc:
            return {"error": str(exc)}

    def computeRadialDistribution(  # noqa: N802
        self, n: int, l: int
    ) -> dict:
        """Compute radial distribution P(r) = r² |R_nl(r)|²."""
        try:
            n, l = int(n), int(l)
            valid, msg = self._engine.validate_quantum_numbers(n, l, 0)
            if not valid:
                return {"error": msg}
            return self._engine.radial_distribution(n, l)
        except Exception as exc:
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Lightweight look-ups
    # ------------------------------------------------------------------

    def getEnergyLevels(self, max_n: int = 6) -> dict:  # noqa: N802
        """Return energy level data for the diagram."""
        try:
            return self._engine.energy_levels(int(max_n))
        except Exception as exc:
            return {"error": str(exc)}

    def getOrbitalLabel(  # noqa: N802
        self, n: int, l: int, m: int
    ) -> dict:
        """Return the spectroscopic label for a given state."""
        try:
            label = self._engine.orbital_label(int(n), int(l), int(m))
            return {"label": label}
        except Exception as exc:
            return {"error": str(exc)}
