import numpy as np

from chronos.analyze import analyze


def write_csv(path, t, z1, z2):
    with open(path, "w") as fh:
        fh.write("frame,t_s,z1_mm,z2_mm,ok\n")
        for i, (a, b, c) in enumerate(zip(t, z1, z2)):
            fh.write(f"{i},{a:.6f},{b:.6f},{c:.6f},1\n")


def test_antisymmetric_peak(tmp_path):
    rng = np.random.default_rng(1)
    fs, n = 200.0, 20000
    t = np.arange(n) / fs
    sig = 0.1 * np.sin(2 * np.pi * 66.8 * t + 0.3)
    drift = 0.002 * t
    z1 = sig + drift + 0.02 * rng.normal(size=n)
    z2 = -sig + drift + 0.02 * rng.normal(size=n)
    p = tmp_path / "run.csv"
    write_csv(p, t, z1, z2)
    r = analyze(str(p))
    assert abs(r.anti.freq_hz - 66.8) < 0.2
    assert r.dominant == "antisymmetric"
    assert r.anti.power > 50 * r.sym.power


def test_control_ratio_and_plot(tmp_path):
    rng = np.random.default_rng(2)
    fs, n = 200.0, 20000
    t = np.arange(n) / fs
    sig = 0.1 * np.sin(2 * np.pi * 66.8 * t)
    p = tmp_path / "run.csv"
    write_csv(p, t, sig + 0.02 * rng.normal(size=n), -sig + 0.02 * rng.normal(size=n))
    c = tmp_path / "single.csv"
    write_csv(c, t, 0.02 * rng.normal(size=n), np.full(n, np.nan))
    png = tmp_path / "psd.png"
    r = analyze(str(p), control=str(c), plot=str(png))
    assert r.control_ratio > 100
    assert png.stat().st_size > 1000


def test_bad_rows_are_filled(tmp_path):
    fs, n = 200.0, 8000
    t = np.arange(n) / fs
    sig = 0.1 * np.sin(2 * np.pi * 66.8 * t)
    p = tmp_path / "gap.csv"
    with open(p, "w") as fh:
        fh.write("frame,t_s,z1_mm,z2_mm,ok\n")
        for i in range(n):
            if 1000 <= i < 1004:
                fh.write(f"{i},{t[i]:.6f},,,0\n")
            else:
                fh.write(f"{i},{t[i]:.6f},{sig[i]:.6f},{-sig[i]:.6f},1\n")
    r = analyze(str(p))
    assert r.n_bad == 4
    assert abs(r.anti.freq_hz - 66.8) < 0.2
