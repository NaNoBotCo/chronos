"""Spectra of the symmetric and antisymmetric motion of the bead pair."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.signal import detrend, welch


@dataclass
class PeakInfo:
    freq_hz: float
    power: float            # PSD at the peak, mm^2/Hz
    fwhm_hz: float
    tau_s: float            # coherence time 1/(pi FWHM)
    resolution_limited: bool
    floor: float            # median PSD around the peak, mm^2/Hz
    snr: float              # power / floor


@dataclass
class AnalysisResult:
    fs: float
    n_samples: int
    duration_s: float
    n_bad: int
    resolution_hz: float
    sym: PeakInfo
    anti: PeakInfo
    dominant: str                         # "antisymmetric", "symmetric" or "none"
    control_ratio: float | None = None    # anti peak over control floor
    control_floor: float | None = None
    freqs: np.ndarray | None = None
    psd_sym: np.ndarray | None = None
    psd_anti: np.ndarray | None = None
    psd_control: np.ndarray | None = None


def load_csv(path: str):
    """Read a tracking CSV.  Returns t, z1, z2, ok (z2 NaN if absent)."""
    data = np.genfromtxt(path, delimiter=",", names=True, dtype=float)
    names = data.dtype.names
    t = np.atleast_1d(data["t_s"])
    z1 = np.atleast_1d(data["z1_mm"])
    z2 = np.atleast_1d(data["z2_mm"]) if "z2_mm" in names else np.full_like(z1, np.nan)
    ok = np.atleast_1d(data["ok"]) if "ok" in names else np.ones_like(z1)
    return t, z1, z2, ok.astype(bool)


def _fill(t: np.ndarray, z: np.ndarray, ok: np.ndarray) -> np.ndarray:
    """Linear interpolation across bad or missing samples."""
    good = ok & np.isfinite(z)
    if good.all():
        return z.copy()
    if good.sum() < 2:
        raise ValueError("fewer than two usable samples")
    return np.interp(t, t[good], z[good])


def _peak(f, p, fmin, fmax, df_res, floor_hz=2.0) -> PeakInfo:
    band = (f >= fmin) & (f <= fmax)
    idx = np.where(band)[0]
    k = idx[np.argmax(p[idx])]
    # parabola through log power at k-1, k, k+1
    if 0 < k < len(f) - 1 and p[k - 1] > 0 and p[k + 1] > 0:
        y0, y1, y2 = np.log(p[k - 1]), np.log(p[k]), np.log(p[k + 1])
        den = y0 - 2 * y1 + y2
        shift = 0.5 * (y0 - y2) / den if den < 0 else 0.0
        shift = float(np.clip(shift, -1, 1))
        f0 = f[k] + shift * (f[1] - f[0])
        pk = float(np.exp(y1 - 0.25 * (y0 - y2) * shift))
    else:
        f0, pk = float(f[k]), float(p[k])
    half = pk / 2.0
    lo = k
    while lo > 0 and p[lo] > half:
        lo -= 1
    hi = k
    while hi < len(f) - 1 and p[hi] > half:
        hi += 1
    f_lo = f[lo] + (half - p[lo]) / (p[lo + 1] - p[lo]) * (f[lo + 1] - f[lo]) if p[lo + 1] != p[lo] else f[lo]
    f_hi = f[hi - 1] + (p[hi - 1] - half) / (p[hi - 1] - p[hi]) * (f[hi] - f[hi - 1]) if p[hi - 1] != p[hi] else f[hi]
    fwhm = max(float(f_hi - f_lo), 1e-9)
    near = (np.abs(f - f0) <= floor_hz) & (np.abs(f - f0) > max(3 * fwhm, 3 * df_res))
    floor = float(np.median(p[near])) if near.any() else float("nan")
    limited = fwhm <= 1.5 * df_res
    return PeakInfo(
        freq_hz=float(f0),
        power=pk,
        fwhm_hz=fwhm,
        tau_s=1.0 / (math.pi * fwhm),
        resolution_limited=bool(limited),
        floor=floor,
        snr=pk / floor if floor and floor > 0 else float("inf"),
    )


def _psd(x: np.ndarray, fs: float, nperseg: int, pad: int = 8):
    x = detrend(x, type="linear")
    return welch(x, fs=fs, window="hann", nperseg=nperseg,
                 noverlap=nperseg // 2, nfft=nperseg * pad, detrend=False)


def analyze(
    path: str,
    control: str | None = None,
    fmin: float = 5.0,
    fmax: float | None = None,
    skip_s: float = 0.0,
    segment_s: float | None = None,
    plot: str | None = None,
    min_snr: float = 5.0,
) -> AnalysisResult:
    """Analyse a two-bead CSV.

    skip_s       Seconds to drop from the start (to leave out a transient).
    segment_s    Welch segment length in seconds.  Default is half the record.
    control      Optional single-bead CSV.  Its PSD floor near the peak is
                 compared with the antisymmetric peak.
    """
    t, z1, z2, ok = load_csv(path)
    keep = t >= (t[0] + skip_s)
    t, z1, z2, ok = t[keep], z1[keep], z2[keep], ok[keep]
    n_bad = int((~ok).sum())
    z1 = _fill(t, z1, ok)
    z2 = _fill(t, z2, ok)
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt
    s = 0.5 * (z1 + z2)
    a = 0.5 * (z1 - z2)
    n = len(t)
    seg = int(round(segment_s * fs)) if segment_s else n // 2
    seg = max(16, min(seg, n))

    ctrl_z = None
    if control is not None:
        ct, c1, c2, cok = load_csv(control)
        cz = c1 if np.isfinite(c1).sum() >= np.isfinite(c2).sum() else c2
        cok = cok & np.isfinite(cz)
        ctrl_z = _fill(ct, cz, cok)
        cfs = 1.0 / float(np.median(np.diff(ct)))
        if abs(cfs - fs) > 0.02 * fs:
            raise ValueError(f"control rate {cfs:.1f} Hz differs from run rate {fs:.1f} Hz")
        seg = min(seg, len(ctrl_z))

    f, ps = _psd(s, fs, seg)
    _, pa = _psd(a, fs, seg)
    df_res = fs / seg * 1.5          # Hann window equivalent noise bandwidth
    top = fmax if fmax is not None else fs / 2.0 - 1.0
    sym = _peak(f, ps, fmin, top, df_res)
    anti = _peak(f, pa, fmin, top, df_res)

    best = max(sym.power, anti.power)
    if max(sym.snr, anti.snr) < min_snr:
        dominant = "none"
    else:
        dominant = "antisymmetric" if anti.power >= sym.power else "symmetric"

    res = AnalysisResult(
        fs=fs, n_samples=n, duration_s=float(t[-1] - t[0]), n_bad=n_bad,
        resolution_hz=df_res, sym=sym, anti=anti, dominant=dominant,
        freqs=f, psd_sym=ps, psd_anti=pa,
    )
    if ctrl_z is not None:
        _, pc = _psd(ctrl_z, fs, seg)
        near = np.abs(f - anti.freq_hz) <= 1.0
        cfloor = float(np.median(pc[near]))
        res.control_floor = cfloor
        res.control_ratio = anti.power / cfloor if cfloor > 0 else float("inf")
        res.psd_control = pc
    if plot:
        save_plot(res, plot)
    return res


def save_plot(res: AnalysisResult, path: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.semilogy(res.freqs, res.psd_sym, label="symmetric", color="tab:blue", lw=1)
    ax.semilogy(res.freqs, res.psd_anti, label="antisymmetric", color="tab:red", lw=1)
    if res.psd_control is not None:
        ax.semilogy(res.freqs, res.psd_control, label="single bead", color="0.5", lw=1)
    for pk, c in ((res.sym, "tab:blue"), (res.anti, "tab:red")):
        ax.axvline(pk.freq_hz, color=c, ls="--", lw=0.8)
        ax.plot([pk.freq_hz], [pk.power], "o", color=c)
        ax.annotate(f"{pk.freq_hz:.2f} Hz", (pk.freq_hz, pk.power),
                    textcoords="offset points", xytext=(6, 4), fontsize=8)
    lo = max(0.0, min(res.sym.freq_hz, res.anti.freq_hz) - 20)
    hi = max(res.sym.freq_hz, res.anti.freq_hz) + 20
    ax.set_xlim(lo, hi)
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel("PSD (mm$^2$/Hz)")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
