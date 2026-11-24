"""Reduced model of the two-bead acoustic time crystal.

This follows the form of Morrell, Elliott & Grier, Phys. Rev. Lett. 136,
057201 (2026), arXiv 2504.15495, but it is NOT the paper's model.  The paper's
prefactors were not available, so every coupling number below is fitted by
hand to show the behaviour the paper reports:

  * a pair near ka = 1.07 / 1.21 (diameters 2.9 / 3.3 mm) settles into a
    limit cycle,
  * equal sizes ring down to a fixed point,
  * a size ratio of 1.5 rings down to a fixed point.

Dimensionless equations, zeta = k z, nu = d zeta / d tau, tau in units of t0:

    nu_j' = -1/2 sin(2 zeta_j) - Gamma_j nu_j + force_j
    Gamma_j = 2 eps / (ka_j)^2

The static pair force uses Phi(x) = [cos x + x sin x] / x^2 at the bead
separation x = n pi + (zeta_upper - zeta_lower).  The coupling strengths are
B_12 ~ (ka_2)^3 and B_21 ~ (ka_1)^3, so the force is nonreciprocal whenever
the radii differ.

The trap alone is a conservative pendulum-like well, and the static pair
force alone cannot sustain motion (the linearised system is stable for every
size pair).  To get a limit cycle the model adds a wave memory: each bead
also feels the other through a low-pass filtered position (time constant
`memory`), weighted by `activity` and by a gate that is a band in the size ratio,
close to zero for equal sizes and for large mismatch.  The gate shape and the numbers are a
fit, not a derivation.

Bead 1 is the lower bead, bead 2 the upper one.  z is positive upward.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

K_WAVE = 732.0          # rad/m
C0 = 343.0              # m/s
LATTICE_MM = 4.3        # node spacing, mm
EPS = 1.72e-3           # drag parameter from the paper
F_TRAP_HZ = 66.7        # small-amplitude trap frequency
T0 = 1.0 / (2.0 * math.pi * F_TRAP_HZ)   # seconds per model time unit
RHO_BEAD = 30.5         # kg/m^3, expanded polystyrene
RHO_AIR = 1.204         # kg/m^3


def diameter_to_ka(d_mm: float) -> float:
    """Bead diameter in mm to ka = k * radius."""
    return K_WAVE * (d_mm * 1e-3 / 2.0)


def ka_to_diameter(ka: float) -> float:
    """ka to bead diameter in mm."""
    return 2.0 * ka / K_WAVE * 1e3


def seconds_to_model(t_s: float) -> float:
    return t_s / T0


def model_to_seconds(tau: float) -> float:
    return tau * T0


def phi(x: float) -> float:
    """Pair-force shape Phi(x) = [cos x + x sin x] / x^2."""
    return (math.cos(x) + x * math.sin(x)) / (x * x)


@dataclass
class Coupling:
    """Tunable coupling parameters.  All defaults are fitted, not from the paper.

    strength  Prefactor g in B_12 = g (ka_2)^3 (1 - chi), B_21 = g (ka_1)^3 (1 - chi).
              It sets the split between the symmetric and antisymmetric modes.
    chi       Correction factor in (1 - chi); 0 leaves it out.
    n_sep     Number of node spacings between the beads (1 = neighbouring nodes).
    memory    Time constant of the wave memory filter, in model units.
    activity  Weight of the remembered (lagged) channel relative to the static one.
    ratio0    Size ratio (larger ka over smaller ka) at the centre of the
              active band.
    width     Width of the band in ln(ratio).  The gate is
              exp(-((ln ratio - ln ratio0) / width)^2), so it is close to
              zero for equal sizes and for ratios far above ratio0.
    """

    strength: float = 0.008
    chi: float = 0.0
    n_sep: int = 1
    memory: float = 1.0
    activity: float = 5.0
    ratio0: float = 1.13
    width: float = 0.07

    def b12_b21(self, ka1: float, ka2: float) -> tuple[float, float]:
        f = self.strength * (1.0 - self.chi)
        return f * ka2**3, f * ka1**3

    def gate(self, ka1: float, ka2: float) -> float:
        ratio = max(ka1, ka2) / min(ka1, ka2)
        u = (math.log(ratio) - math.log(self.ratio0)) / self.width
        return math.exp(-u * u)


@dataclass
class SimResult:
    t: np.ndarray          # seconds
    z1: np.ndarray         # lower bead, mm from its node
    z2: np.ndarray         # upper bead, mm from its node
    ka1: float
    ka2: float
    coupling: Coupling = field(repr=False, default_factory=Coupling)

    @property
    def sym(self) -> np.ndarray:
        return 0.5 * (self.z1 + self.z2)

    @property
    def anti(self) -> np.ndarray:
        return 0.5 * (self.z1 - self.z2)


def _as_coupling(coupling) -> Coupling:
    if coupling is None:
        return Coupling()
    if isinstance(coupling, Coupling):
        return coupling
    return Coupling(strength=float(coupling))


def simulate(
    ka1: float,
    ka2: float,
    t_end: float = 30.0,
    dt: float = 0.005,
    noise: float = 0.0,
    seed: int | None = 0,
    coupling=None,
    kick: float = 0.02,
) -> SimResult:
    """Integrate the pair and return positions in mm.

    ka1, ka2   k * radius of the lower and upper bead.
    t_end, dt  Run length and output sample spacing, in seconds.
    noise      Standard deviation of white acceleration noise, in model
               units per sqrt(model time).  0 gives a deterministic run.
    seed       Seed for the noise and for the initial kick.
    coupling   A Coupling, a float (strength only), or None for defaults.
    kick       Size of the initial random displacement, in zeta units.
    """
    cp = _as_coupling(coupling)
    rng = np.random.default_rng(seed)
    g1 = 2.0 * EPS / ka1**2
    g2 = 2.0 * EPS / ka2**2
    b12, b21 = cp.b12_b21(ka1, ka2)
    lam = cp.gate(ka1, ka2)
    kap = cp.activity * lam
    tau_m = cp.memory
    x0 = cp.n_sep * math.pi
    sin, cos = math.sin, math.cos

    def force_shape(x: float) -> float:
        return (cos(x) + x * sin(x)) / (x * x)

    def rhs(y):
        z1, z2, v1, v2, p1, p2 = y
        s = force_shape(x0 + z2 - z1)
        # remembered channel: each bead sees the other's filtered position
        sl1 = force_shape(x0 + p2 - z1)
        sl2 = force_shape(x0 + z2 - p1)
        f1 = -b12 * (s + kap * (sl1 - s))
        f2 = b21 * (s + kap * (sl2 - s))
        a1 = -0.5 * sin(2.0 * z1) - g1 * v1 + f1
        a2 = -0.5 * sin(2.0 * z2) - g2 * v2 + f2
        return (v1, v2, a1, a2, (z1 - p1) / tau_m, (z2 - p2) / tau_m)

    # start from a small random kick about the node
    z1_0 = kick * rng.normal()
    z2_0 = kick * rng.normal()
    y = [z1_0, z2_0, 0.0, 0.0, z1_0, z2_0]

    dt_m = dt / T0
    n_sub = max(1, int(math.ceil(dt_m / 0.2)))
    h = dt_m / n_sub
    n_out = int(round(t_end / dt)) + 1
    out = np.empty((n_out, 2))
    out[0] = (y[0], y[1])
    sig = noise * math.sqrt(h)

    for i in range(1, n_out):
        for _ in range(n_sub):
            k1 = rhs(y)
            k2 = rhs([a + 0.5 * h * b for a, b in zip(y, k1)])
            k3 = rhs([a + 0.5 * h * b for a, b in zip(y, k2)])
            k4 = rhs([a + h * b for a, b in zip(y, k3)])
            y = [a + h / 6.0 * (b + 2 * c + 2 * d + e)
                 for a, b, c, d, e in zip(y, k1, k2, k3, k4)]
            if noise:
                y[2] += sig * rng.normal()
                y[3] += sig * rng.normal()
        out[i] = (y[0], y[1])

    t = np.arange(n_out) * dt
    scale = 1e3 / K_WAVE
    return SimResult(t, out[:, 0] * scale, out[:, 1] * scale, ka1, ka2, cp)


def _rms(a: np.ndarray, b: np.ndarray) -> float:
    """Rms of the oscillation of both beads, static offset removed."""
    return float(np.sqrt(np.var(a) + np.var(b)))


def is_active(
    ka1: float,
    ka2: float,
    t_end: float = 40.0,
    dt: float = 0.01,
    coupling=None,
    min_amp_mm: float = 0.02,
    seed: int | None = 0,
) -> bool:
    """True if the pair settles into a sustained oscillation.

    Runs a deterministic simulation from a small kick.  The pair counts as
    active when the rms amplitude of the last quarter of the run is at least
    `min_amp_mm` and at least half the amplitude of the first quarter.  A
    ring-down fails the second test because its amplitude falls steadily.
    """
    r = simulate(ka1, ka2, t_end=t_end, dt=dt, coupling=coupling, seed=seed)
    q = len(r.t) // 4
    first = _rms(r.z1[:q], r.z2[:q])
    last = _rms(r.z1[-q:], r.z2[-q:])
    return bool(last >= min_amp_mm and last >= 0.5 * first)
