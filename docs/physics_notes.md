# Physics Reference — Hydrogen Atom Wavefunctions

## Wavefunction Decomposition

The time-independent Schrödinger equation for the hydrogen atom admits
analytical solutions that separate into radial and angular parts:

$$
\psi_{nlm}(r, \theta, \phi) = R_{nl}(r) \cdot Y_l^m(\theta, \phi)
$$

## Quantum Numbers

| Symbol | Name | Range | Physical meaning |
|--------|------|-------|------------------|
| n | Principal | 1, 2, 3, … | Energy shell; determines energy E_n |
| l | Azimuthal (angular momentum) | 0, 1, …, n−1 | Orbital shape |
| m | Magnetic | −l, …, 0, …, +l | Orbital orientation |

**Selection rules:** n ≥ 1,  0 ≤ l < n,  |m| ≤ l.

### Spectroscopic Notation

| l | Letter |
|---|--------|
| 0 | s |
| 1 | p |
| 2 | d |
| 3 | f |
| 4 | g |

## Radial Wavefunction R_nl(r)

$$
R_{nl}(r) = N_{nl} \cdot e^{-\rho/2} \cdot \rho^l \cdot L_{n-l-1}^{2l+1}(\rho)
$$

where:
- ρ = 2r / (n · a₀)
- a₀ = Bohr radius (= 1 in atomic units)
- L is the generalised Laguerre polynomial (`scipy.special.genlaguerre`)

### Normalisation constant

$$
N_{nl} = \sqrt{ \left(\frac{2}{n a_0}\right)^3 \frac{(n-l-1)!}{2n \cdot (n+l)!} }
$$

This ensures ∫₀^∞ |R_nl(r)|² r² dr = 1.

## Spherical Harmonics Y_l^m(θ, φ)

$$
Y_l^m(\theta, \phi) = \sqrt{\frac{2l+1}{4\pi} \frac{(l-m)!}{(l+m)!}} P_l^m(\cos\theta) \cdot e^{im\phi}
$$

### scipy convention

`scipy.special.sph_harm_y(l, m, theta, phi)` uses the **physics convention**:
- θ (theta) = polar angle ∈ [0, π]
- φ (phi) = azimuthal angle ∈ [0, 2π)

This matches our code directly — no argument swapping needed.

## Probability Density

$$
|\psi_{nlm}|^2 = |R_{nl}(r)|^2 \cdot |Y_l^m(\theta, \phi)|^2
$$

This is always real and non-negative.

## Radial Distribution Function

$$
P(r) = r^2 |R_{nl}(r)|^2
$$

Gives the probability of finding the electron between r and r + dr
(integrated over all angles).  The most probable radius is where P(r)
is maximised.

For the 1s orbital (n=1, l=0): P(r) peaks at r = a₀.

## Energy Eigenvalues

$$
E_n = -\frac{13.6 \text{ eV}}{n^2}
$$

Key values:
- E₁ = −13.6 eV (ground state)
- E₂ = −3.4 eV
- E₃ = −1.511 eV
- E → 0 as n → ∞ (ionisation threshold)

**Degeneracy** (without spin): n² states share the same energy E_n.

## 3D Visualisation Strategy

1. Create a uniform Cartesian grid (x, y, z).
2. Convert each grid point to spherical coordinates (r, θ, φ).
3. Evaluate ψ = R_nl(r) · Y_lm(θ, φ) at every point.
4. Compute |ψ|² and render as a Plotly isosurface.
5. Grid extent scales adaptively: max_r = min(4n², 80) · a₀.
