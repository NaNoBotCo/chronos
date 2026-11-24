"""Command line: chronos simulate | track | analyze."""

from __future__ import annotations

import argparse
import csv
import sys

import numpy as np

from . import analyze as an
from . import model, track as tr


def _write_sim_csv(res: model.SimResult, path: str) -> None:
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["frame", "t_s", "z1_mm", "z2_mm", "ok"])
        for i, (t, a, b) in enumerate(zip(res.t, res.z1, res.z2)):
            w.writerow([i, f"{t:.6f}", f"{a:.6f}", f"{b:.6f}", 1])


def _print_analysis(r: an.AnalysisResult) -> None:
    print(f"samples {r.n_samples}  rate {r.fs:.1f} Hz  length {r.duration_s:.1f} s"
          f"  bad {r.n_bad}")
    for name, p in (("symmetric", r.sym), ("antisymmetric", r.anti)):
        lim = " (resolution limited, tau is a lower bound)" if p.resolution_limited else ""
        print(f"{name:14s} {p.freq_hz:8.3f} Hz  FWHM {p.fwhm_hz:.4f} Hz"
              f"  tau {p.tau_s:.1f} s  peak/floor {p.snr:.1f}{lim}")
    print(f"dominant: {r.dominant}")
    if r.control_ratio is not None:
        print(f"antisymmetric peak over single-bead floor: {r.control_ratio:.1f}")


def cmd_simulate(a) -> int:
    ka1 = model.diameter_to_ka(a.d1)
    ka2 = model.diameter_to_ka(a.d2)
    cp = model.Coupling(strength=a.strength)
    res = model.simulate(ka1, ka2, t_end=a.t_end, dt=a.dt, noise=a.noise,
                         seed=a.seed, coupling=cp)
    active = model.is_active(ka1, ka2, coupling=cp)
    print(f"d1 {a.d1} mm (ka {ka1:.3f})  d2 {a.d2} mm (ka {ka2:.3f})")
    print(f"regime: {'limit cycle' if active else 'ring-down'}")
    if a.out:
        _write_sim_csv(res, a.out)
        print(f"wrote {a.out}")
        r = an.analyze(a.out, skip_s=a.t_end / 2, plot=a.plot)
        _print_analysis(r)
    elif a.plot:
        print("--plot needs --out", file=sys.stderr)
        return 2
    return 0


def cmd_track(a) -> int:
    res = tr.track(a.source, scale=a.scale, fps=a.fps)
    tr.write_csv(res, a.out)
    good = int(res.ok.sum())
    print(f"frames {len(res.frame)}  tracked {good}  dropped {res.n_dropped}"
          f"  failed {res.n_failed}  wrote {a.out}")
    return 0


def cmd_analyze(a) -> int:
    r = an.analyze(a.csv, control=a.control, skip_s=a.skip, plot=a.plot)
    _print_analysis(r)
    if a.plot:
        print(f"wrote {a.plot}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="chronos", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("simulate", help="run the reduced two-bead model")
    s.add_argument("--d1", type=float, required=True, help="lower bead diameter, mm")
    s.add_argument("--d2", type=float, required=True, help="upper bead diameter, mm")
    s.add_argument("--t-end", type=float, default=40.0, help="seconds")
    s.add_argument("--dt", type=float, default=0.005, help="sample spacing, s")
    s.add_argument("--noise", type=float, default=0.0)
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--strength", type=float, default=model.Coupling().strength,
                   help="coupling prefactor (fitted)")
    s.add_argument("--out", help="write CSV here and analyse it")
    s.add_argument("--plot", help="PSD figure (needs --out)")
    s.set_defaults(fn=cmd_simulate)

    t = sub.add_parser("track", help="track two beads in a video or frame folder")
    t.add_argument("source")
    t.add_argument("--scale", type=float, default=0.139, help="mm per pixel")
    t.add_argument("--fps", type=float, default=None)
    t.add_argument("--out", required=True)
    t.set_defaults(fn=cmd_track)

    z = sub.add_parser("analyze", help="spectra of a tracking CSV")
    z.add_argument("csv")
    z.add_argument("--control", help="single-bead CSV")
    z.add_argument("--plot", help="save PSD figure")
    z.add_argument("--skip", type=float, default=0.0, help="seconds to drop at start")
    z.set_defaults(fn=cmd_analyze)

    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
