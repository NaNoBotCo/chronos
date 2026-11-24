"""Find two bright beads on a dark background in each frame.

Input is a video file or a folder of image frames.  Output is a table with
columns frame, t_s, z1_mm, z2_mm, ok.  z1 is the lower bead and z2 the upper
bead; z points up, in mm, relative to each bead's median position.
"""

from __future__ import annotations

import csv
import glob
import os
from dataclasses import dataclass

import cv2
import numpy as np

IMG_EXT = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp")


@dataclass
class TrackResult:
    frame: np.ndarray
    t: np.ndarray
    z1: np.ndarray
    z2: np.ndarray
    ok: np.ndarray
    fps: float
    n_dropped: int = 0
    n_failed: int = 0


def blob_centroids(
    gray: np.ndarray,
    min_area: int = 4,
    frac: float = 0.5,
    n_blobs: int = 2,
) -> list[tuple[float, float, float]]:
    """Return up to n_blobs (x, y, flux) tuples, brightest first.

    The threshold sits at `frac` of the way from the background (median) to
    the frame maximum.  Each centroid is an intensity-weighted mean over the
    blob's bounding box, after background subtraction.
    """
    img = gray.astype(np.float32)
    bg = float(np.median(img))
    peak = float(img.max())
    if peak - bg < 5.0:
        return []
    thr = bg + frac * (peak - bg)
    mask = (img >= thr).astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    h, w = img.shape
    found = []
    for i in range(1, n):
        x0, y0, bw, bh, area = stats[i]
        if area < min_area:
            continue
        pad = max(3, int(round(max(bw, bh))))
        xa, xb = max(0, x0 - pad), min(w, x0 + bw + pad)
        ya, yb = max(0, y0 - pad), min(h, y0 + bh + pad)
        win = img[ya:yb, xa:xb] - bg
        win = np.where(win > 0.1 * (peak - bg), win, 0.0)
        flux = float(win.sum())
        if flux <= 0:
            continue
        yy, xx = np.mgrid[ya:yb, xa:xb]
        cx = float((win * xx).sum() / flux)
        cy = float((win * yy).sum() / flux)
        found.append((cx, cy, flux))
    found.sort(key=lambda b: -b[2])
    return found[:n_blobs]


def _frame_source(path: str, fps: float | None):
    """Yield (gray_frame, timestamp_s or None) and return nominal fps."""
    if os.path.isdir(path):
        files = sorted(
            f for f in glob.glob(os.path.join(path, "*"))
            if f.lower().endswith(IMG_EXT)
        )
        if not files:
            raise FileNotFoundError(f"no image frames in {path}")
        use_fps = fps or 200.0

        def gen():
            for f in files:
                img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
                yield img, None

        return gen(), use_fps
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise FileNotFoundError(f"cannot open video {path}")
    use_fps = fps or cap.get(cv2.CAP_PROP_FPS) or 200.0

    def gen():
        try:
            while True:
                ok, fr = cap.read()
                if not ok:
                    break
                ts = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                if fr.ndim == 3:
                    fr = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
                yield fr, ts
        finally:
            cap.release()

    return gen(), use_fps


def track(
    path: str,
    scale: float = 0.139,
    fps: float | None = None,
    min_area: int = 4,
    min_sep_px: float = 4.0,
    use_timestamps: bool = True,
) -> TrackResult:
    """Track the two beads in a video or frame folder.

    scale   mm per pixel.
    fps     Nominal frame rate.  Read from the video if left out; 200 for a
            folder of frames.
    Frames lost between timestamps get an ok = 0 row so the time axis stays
    regular.  Frames where two beads are not found also get ok = 0.
    """
    frames, fps = _frame_source(path, fps)
    period = 1.0 / fps
    rows = []   # (index, t, y_lower, y_upper, ok)
    ts_list = []
    for idx, (gray, ts) in enumerate(frames):
        ts_list.append(ts)
        blobs = blob_centroids(gray, min_area=min_area)
        if len(blobs) == 2 and abs(blobs[0][1] - blobs[1][1]) >= min_sep_px:
            (_, ya, _), (_, yb, _) = sorted(blobs, key=lambda b: b[1])
            rows.append((idx, ya, yb, 1))     # ya: upper in image
        else:
            rows.append((idx, np.nan, np.nan, 0))

    # timestamps: use them only when they advance
    ts_arr = np.array([np.nan if t is None else t for t in ts_list], float)
    have_ts = (
        use_timestamps
        and len(ts_arr) > 2
        and np.all(np.isfinite(ts_arr))
        and ts_arr[-1] > ts_arr[0]
    )
    slot = (
        np.round((ts_arr - ts_arr[0]) / period).astype(int)
        if have_ts
        else np.arange(len(rows))
    )
    n_slots = int(slot[-1]) + 1
    n_dropped = n_slots - len(np.unique(slot))
    y_up = np.full(n_slots, np.nan)
    y_lo = np.full(n_slots, np.nan)
    ok = np.zeros(n_slots, dtype=int)
    for (idx, ya, yb, good), s in zip(rows, slot):
        y_up[s], y_lo[s], ok[s] = ya, yb, good
    n_failed = int(np.sum(~ok.astype(bool))) - n_dropped

    # image y grows downward; z grows upward, centred on the median
    z1 = -(y_lo)
    z2 = -(y_up)
    for z in (z1, z2):
        good = ok.astype(bool)
        if good.any():
            z -= np.median(z[good])
    z1 = z1 * scale
    z2 = z2 * scale
    frame = np.arange(n_slots)
    t = frame * period
    return TrackResult(frame, t, z1, z2, ok, fps, n_dropped, max(n_failed, 0))


def write_csv(res: TrackResult, path: str) -> None:
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["frame", "t_s", "z1_mm", "z2_mm", "ok"])
        for i in range(len(res.frame)):
            w.writerow([
                int(res.frame[i]),
                f"{res.t[i]:.6f}",
                "" if np.isnan(res.z1[i]) else f"{res.z1[i]:.5f}",
                "" if np.isnan(res.z2[i]) else f"{res.z2[i]:.5f}",
                int(res.ok[i]),
            ])
