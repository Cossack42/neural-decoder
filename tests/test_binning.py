"""Checks for the binning step, on small synthetic data (no recording needed)."""

import numpy as np

from load_sabes import bin_session


def make_session(duration_s=10.0, fs=250.0):
    t = np.arange(0, duration_s, 1 / fs)
    # Cursor moving at a constant 20 mm/s in x and -10 mm/s in y.
    cursor = np.stack([20.0 * t, -10.0 * t], axis=1)
    return t, cursor


def test_spike_counts_land_in_the_right_bins():
    t, cursor = make_session()
    spikes = [np.array([0.01, 0.02, 0.26]), np.array([])]
    X, _, edges = bin_session(spikes, t, cursor, bin_s=0.05)

    assert X.shape == (len(edges) - 1, 2)
    assert X[0, 0] == 2          # 0.01 s and 0.02 s fall in the first 50 ms bin
    assert X[5, 0] == 1          # 0.26 s falls in the bin starting at 0.25 s
    assert X[:, 0].sum() == 3    # no spike is counted twice or lost
    assert X[:, 1].sum() == 0    # an empty channel stays empty


def test_velocity_is_recovered_from_position():
    t, cursor = make_session()
    _, Y, _ = bin_session([np.array([])], t, cursor, bin_s=0.05)

    assert np.allclose(Y[:, 0], 20.0, atol=1e-6)
    assert np.allclose(Y[:, 1], -10.0, atol=1e-6)
