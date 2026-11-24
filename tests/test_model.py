import numpy as np

from chronos import model


def test_limit_cycle_for_time_crystal_pair():
    ka1, ka2 = model.diameter_to_ka(2.9), model.diameter_to_ka(3.3)
    assert model.is_active(ka1, ka2)


def test_ring_down_equal_sizes():
    ka = model.diameter_to_ka(3.0)
    assert not model.is_active(ka, ka)


def test_ring_down_ratio_1p5():
    assert not model.is_active(model.diameter_to_ka(2.0), model.diameter_to_ka(3.0))


def test_ring_down_ratio_1p5_large_beads():
    assert not model.is_active(model.diameter_to_ka(2.6), model.diameter_to_ka(3.9))


def test_units():
    assert abs(model.diameter_to_ka(2.9) - 1.0614) < 1e-3
    assert abs(model.model_to_seconds(1.0) * 2 * np.pi * 66.7 - 1.0) < 1e-12


def test_limit_cycle_frequency_near_trap():
    r = model.simulate(model.diameter_to_ka(2.9), model.diameter_to_ka(3.3),
                       t_end=60, dt=0.005)
    x = r.anti[len(r.t) // 2:]
    spec = np.abs(np.fft.rfft((x - x.mean()) * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 0.005)[spec.argmax()]
    assert 65.0 < f < 67.0


def test_noise_run_is_reproducible():
    args = (1.0, 1.2)
    a = model.simulate(*args, t_end=1, dt=0.005, noise=0.01, seed=3)
    b = model.simulate(*args, t_end=1, dt=0.005, noise=0.01, seed=3)
    assert np.array_equal(a.z1, b.z1)
