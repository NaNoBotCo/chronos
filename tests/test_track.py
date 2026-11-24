import os

import cv2
import numpy as np

from chronos import track

SCALE = 0.139
H, W = 120, 80
FPS = 200.0


def blob(cx, cy, sigma=2.5, amp=220.0):
    yy, xx = np.mgrid[0:H, 0:W]
    return amp * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * sigma**2))


def synth(n=400):
    t = np.arange(n) / FPS
    # image y grows downward; bead 1 is the lower one
    y_lo = 80 + 3.0 * np.sin(2 * np.pi * 66.8 * t)
    y_up = 40 - 3.0 * np.sin(2 * np.pi * 66.8 * t)
    frames = []
    for a, b in zip(y_up, y_lo):
        img = blob(40.3, a) + blob(39.6, b) + 4.0
        frames.append(np.clip(img, 0, 255).astype(np.uint8))
    return t, y_up, y_lo, frames


def expected(y_up, y_lo):
    z1 = -(y_lo - np.median(y_lo)) * SCALE
    z2 = -(y_up - np.median(y_up)) * SCALE
    return z1, z2


def test_folder_tracking(tmp_path):
    t, y_up, y_lo, frames = synth()
    d = tmp_path / "frames"
    d.mkdir()
    for i, f in enumerate(frames):
        cv2.imwrite(str(d / f"f{i:05d}.png"), f)
    res = track.track(str(d), scale=SCALE, fps=FPS)
    z1, z2 = expected(y_up, y_lo)
    assert res.ok.all()
    assert np.max(np.abs(res.z1 - z1)) < 0.05
    assert np.max(np.abs(res.z2 - z2)) < 0.05
    assert res.n_dropped == 0


def test_video_tracking_and_csv(tmp_path):
    t, y_up, y_lo, frames = synth(200)
    p = str(tmp_path / "beads.avi")
    vw = cv2.VideoWriter(p, cv2.VideoWriter_fourcc(*"MJPG"), FPS, (W, H), False)
    for f in frames:
        vw.write(f)
    vw.release()
    res = track.track(p, scale=SCALE)
    z1, z2 = expected(y_up, y_lo)
    assert res.ok.all()
    assert np.max(np.abs(res.z1 - z1)) < 0.05
    out = str(tmp_path / "run.csv")
    track.write_csv(res, out)
    with open(out) as fh:
        assert fh.readline().strip() == "frame,t_s,z1_mm,z2_mm,ok"


def test_failed_detection_is_flagged(tmp_path):
    t, y_up, y_lo, frames = synth(50)
    frames[10] = np.full((H, W), 4, np.uint8)
    d = tmp_path / "frames"
    d.mkdir()
    for i, f in enumerate(frames):
        cv2.imwrite(str(d / f"f{i:05d}.png"), f)
    res = track.track(str(d), scale=SCALE, fps=FPS)
    assert res.ok[10] == 0 and np.isnan(res.z1[10])
    assert res.ok.sum() == 49
    assert res.n_failed == 1
