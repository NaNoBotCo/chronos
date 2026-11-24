import cv2
import numpy as np

from chronos.cli import main


def test_simulate_and_analyze(tmp_path, capsys):
    out = str(tmp_path / "sim.csv")
    png = str(tmp_path / "sim.png")
    assert main(["simulate", "--d1", "2.9", "--d2", "3.3", "--t-end", "40",
                 "--out", out, "--plot", png]) == 0
    text = capsys.readouterr().out
    assert "limit cycle" in text
    assert main(["analyze", out, "--skip", "20"]) == 0
    assert "dominant" in capsys.readouterr().out


def test_ring_down_label(tmp_path, capsys):
    assert main(["simulate", "--d1", "3.0", "--d2", "3.0"]) == 0
    assert "ring-down" in capsys.readouterr().out


def test_track_command(tmp_path, capsys):
    d = tmp_path / "frames"
    d.mkdir()
    yy, xx = np.mgrid[0:100, 0:60]
    for i in range(10):
        img = 4 + 200 * np.exp(-((xx - 30) ** 2 + (yy - 30 - i * 0.2) ** 2) / 8)
        img += 200 * np.exp(-((xx - 30) ** 2 + (yy - 70) ** 2) / 8)
        cv2.imwrite(str(d / f"{i:03d}.png"), np.clip(img, 0, 255).astype(np.uint8))
    out = str(tmp_path / "run.csv")
    assert main(["track", str(d), "--scale", "0.139", "--out", out]) == 0
    assert "tracked 10" in capsys.readouterr().out
