"""Analytical solutions of the hydrogen atom Schrodinger equation.

This module provides the PhysicsEngine class which computes:
- Radial wavefunctions R_nl(r) using associated Laguerre polynomials
- Spherical harmonics Y_lm(theta, phi)
- 3D probability density |psi|^2 on Cartesian grids
- Radial distribution functions P(r) = r^2 |R_nl(r)|^2
- Energy eigenvalues E_n = -13.6 eV / n^2

All calculations use atomic units where the Bohr radius a0 = 1.
"""

import numpy as np
from scipy.special import sph_harm_y, genlaguerre, factorial
from typing import Any, Dict, List, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
A0: float = 1.0  # Bohr radius in atomic units
ORBITAL_LETTERS: str = "spdfghiklmn"


class PhysicsEngine:
    """Compute hydrogen atom wavefunctions and related quantities.

    Every public method is a pure function (no hidden state) so the engine
    is safe to call from any thread.
    """

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def validate_quantum_numbers(n: int, l: int, m: int) -> Tuple[bool, str]:
        """Enforce the quantum-number selection rules.

        Rules
        -----
        * n >= 1  (principal)
        * 0 <= l < n  (azimuthal / angular momentum)
        * -l <= m <= l  (magnetic)

        Returns
        -------
        (is_valid, message) where *message* explains the first violated rule,
        or ``"Valid quantum numbers"`` when all rules pass.
        """
        if not isinstance(n, (int, np.integer)) or n < 1:
            return False, "n must be a positive integer (n >= 1)"
        if not isinstance(l, (int, np.integer)) or l < 0 or l >= n:
            return False, f"l must satisfy 0 <= l < n (0 <= l < {n})"
        if not isinstance(m, (int, np.integer)) or abs(m) > l:
            return False, f"m must satisfy -l <= m <= l (-{l} <= m <= {l})"
        return True, "Valid quantum numbers"

    # ------------------------------------------------------------------
    # Radial wavefunction
    # ------------------------------------------------------------------

    @staticmethod
    def radial_wavefunction(
        r: np.ndarray, n: int, l: int
    ) -> np.ndarray:
        r"""Normalised radial wavefunction R_{nl}(r).

        .. math::

            R_{nl}(r) = N_{nl}\, e^{-\rho/2}\, \rho^{l}\,
                         L_{n-l-1}^{2l+1}(\rho)

        where :math:`\rho = 2r/(n a_0)` and
        :math:`L_{n-l-1}^{2l+1}` is a generalised Laguerre polynomial
        (``scipy.special.genlaguerre``).

        The normalisation constant is

        .. math::

            N_{nl} = \sqrt{
                \left(\frac{2}{n a_0}\right)^3
                \frac{(n-l-1)!}{2n\,(n+l)!}
            }

        Parameters
        ----------
        r : array_like
            Radial distance(s) in units of a0.
        n, l : int
            Principal and azimuthal quantum numbers.

        Returns
        -------
        R : ndarray  (same shape as *r*)
            Real-valued radial wavefunction.
        """
        r = np.asarray(r, dtype=np.float64)
        rho = 2.0 * r / (n * A0)

        # Normalisation
        norm = np.sqrt(
            (2.0 / (n * A0)) ** 3
            * factorial(n - l - 1, exact=True)
            / (2.0 * n * factorial(n + l, exact=True))
        )

        # Generalised Laguerre polynomial L_{n-l-1}^{2l+1}(rho)
        laguerre_poly = genlaguerre(n - l - 1, 2 * l + 1)

        return float(norm) * np.exp(-rho / 2.0) * rho**l * laguerre_poly(rho)

    # ------------------------------------------------------------------
    # Spherical harmonics
    # ------------------------------------------------------------------

    @staticmethod
    def spherical_harmonic(
        theta: np.ndarray, phi: np.ndarray, l: int, m: int
    ) -> np.ndarray:
        r"""Spherical harmonic Y_l^m(theta, phi).

        Parameters use the **physics convention**:
            * *theta* — polar angle  [0, pi]
            * *phi*   — azimuthal angle  [0, 2 pi)

        Uses ``scipy.special.sph_harm_y`` which follows the same
        physics convention: ``sph_harm_y(n, m, theta, phi)`` where
        *theta* is the polar (colatitudinal) angle and *phi* is the
        azimuthal (longitudinal) angle.

        Returns
        -------
        Y : ndarray (complex)
        """
        return sph_harm_y(l, m, theta, phi)

    # ------------------------------------------------------------------
    # Full wavefunction helpers
    # ------------------------------------------------------------------

    def wavefunction(
        self,
        r: np.ndarray,
        theta: np.ndarray,
        phi: np.ndarray,
        n: int,
        l: int,
        m: int,
    ) -> np.ndarray:
        r"""Full hydrogen wavefunction psi_{nlm}(r, theta, phi).

        .. math::
            \psi_{nlm} = R_{nl}(r) \, Y_l^m(\theta, \phi)

        Returns a complex-valued array.
        """
        return self.radial_wavefunction(r, n, l) * self.spherical_harmonic(
            theta, phi, l, m
        )

    # ------------------------------------------------------------------
    # 3-D probability density for isosurface visualisation
    # ------------------------------------------------------------------

    def probability_density_3d(
        self,
        n: int,
        l: int,
        m: int,
        grid_size: int = 40,
    ) -> Dict[str, Any]:
        r"""Compute |psi|^2 on a uniform Cartesian grid.

        The grid extent is chosen automatically so that the classically
        allowed region (up to ~ 2 n^2 a0) is well contained.

        Parameters
        ----------
        n, l, m : int
            Quantum numbers (must satisfy selection rules).
        grid_size : int
            Number of sample points along each Cartesian axis.
            Total evaluation points = grid_size^3.

        Returns
        -------
        dict with keys
            ``x, y, z``   : flat lists of Cartesian coordinates
            ``value``      : flat list of |psi|^2 values
            ``max_val``    : float, peak probability density
            ``grid_size``  : int, echoed back
        """
        # Adaptive extent — larger orbitals need a bigger box
        max_r = float(min(4.0 * n * n * A0, 80.0 * A0))

        lin = np.linspace(-max_r, max_r, grid_size)
        X, Y, Z = np.meshgrid(lin, lin, lin, indexing="ij")

        # Cartesian → spherical
        R = np.sqrt(X**2 + Y**2 + Z**2)
        R = np.clip(R, 1e-10, None)  # avoid division by zero at origin
        THETA = np.arccos(np.clip(Z / R, -1.0, 1.0))  # polar  [0, pi]
        PHI = np.arctan2(Y, X) % (2.0 * np.pi)  # azimuthal [0, 2pi)

        # Evaluate wavefunction
        psi = self.wavefunction(R, THETA, PHI, n, l, m)
        prob = np.abs(psi) ** 2

        return {
            "x": X.ravel().tolist(),
            "y": Y.ravel().tolist(),
            "z": Z.ravel().tolist(),
            "value": prob.ravel().tolist(),
            "max_val": float(np.max(prob)),
            "grid_size": grid_size,
        }

    # ------------------------------------------------------------------
    # Radial distribution function
    # ------------------------------------------------------------------

    def radial_distribution(
        self, n: int, l: int, num_points: int = 500
    ) -> Dict[str, List[float]]:
        r"""Radial probability distribution P(r) = r^2 |R_{nl}(r)|^2.

        Returns
        -------
        dict with keys ``r`` and ``P_r``, each a list of floats.
        """
        max_r = 4.0 * n * n * A0 + 10.0 * A0
        r = np.linspace(0.0, max_r, num_points)
        R_nl = self.radial_wavefunction(r, n, l)
        P_r = r**2 * np.abs(R_nl) ** 2
        return {
            "r": r.tolist(),
            "P_r": P_r.tolist(),
        }

    # ------------------------------------------------------------------
    # Energy levels
    # ------------------------------------------------------------------

    @staticmethod
    def energy_levels(max_n: int = 6) -> Dict[str, Any]:
        r"""Hydrogen energy eigenvalues E_n = -13.6 eV / n^2.

        Returns
        -------
        dict with key ``levels`` (list of dicts) and ``unit`` ("eV").
        Each level dict contains ``n``, ``energy``, ``l_values``,
        ``degeneracy`` (n^2 without spin).
        """
        levels = []
        for n_val in range(1, max_n + 1):
            levels.append(
                {
                    "n": n_val,
                    "energy": -13.6 / n_val**2,
                    "l_values": list(range(n_val)),
                    "degeneracy": n_val**2,
                }
            )
        return {"levels": levels, "unit": "eV"}

    # ------------------------------------------------------------------
    # Allowed quantum numbers (for UI dropdowns)
    # ------------------------------------------------------------------

    @staticmethod
    def get_allowed_quantum_numbers(n: int) -> Dict[str, Any]:
        """Return valid *l* and *m* ranges for a given *n*.

        Returns
        -------
        dict
            ``l_values``     : list[int] — [0, 1, …, n-1]
            ``m_values_by_l``: dict[str, list[int]] — keyed by str(l)
        """
        l_values = list(range(0, n))
        m_values_by_l = {
            str(l_val): list(range(-l_val, l_val + 1))
            for l_val in l_values
        }
        return {
            "l_values": l_values,
            "m_values_by_l": m_values_by_l,
        }

    # ------------------------------------------------------------------
    # Spectroscopic label helper
    # ------------------------------------------------------------------

    @staticmethod
    def orbital_label(n: int, l: int, m: int) -> str:
        """Human-readable orbital name, e.g. '2p (m=1)'."""
        letter = ORBITAL_LETTERS[l] if l < len(ORBITAL_LETTERS) else str(l)
        base = f"{n}{letter}"
        if l > 0:
            base += f" (m={m})"
        return base
