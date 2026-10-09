"""Session 1: load one O'Doherty/Sabes reaching session, bin spikes, plot a raster.

Data: https://zenodo.org/records/583331  (file: indy_20160407_02.mat, about 420 MB)
Usage: python python/load_sabes.py data/indy_20160407_02.mat

Outputs:
  data/<session>_binned.npz   X (bins x channels spike counts), Y (bins x 2 velocity), bin_s
  figures/<session>_raster.png
"""

import sys
from pathlib import Path

import numpy as np

BIN_MS = 50          # decoder bin width. Try 20 later to match the on-device cadence.
PLOT_SECONDS = 10    # length of the raster window
MIN_RATE_HZ = 0.5    # channels firing below this are dropped


def load_session(path):
    """Return (spike_times, t, cursor_pos).

    spike_times: list with one array of spike times (seconds) per channel.
    t:           (T,) sample times of the behaviour, 250 Hz.
    cursor_pos:  (T, 2) cursor x, y in mm.
    """
    import h5py

    with h5py.File(path, "r") as f:  # the .mat is MATLAB v7.3, which is HDF5
        t = f["t"][()].ravel()
        cursor_pos = f["cursor_pos"][()].T

        # f["spikes"] is (units, channels) of references. Unit 0 is unsorted
        # threshold crossings, units 1+ are sorted neurons. We pool every unit on
        # a channel, because the Pico will only ever see threshold crossings.
        refs = f["spikes"]
        n_units, n_channels = refs.shape
        spike_times = []
        for ch in range(n_channels):
            per_unit = []
            for u in range(n_units):
                arr = f[refs[u, ch]][()]
                if arr.ndim == 2:  # empty cells are stored as a 1-D shape stub
                    per_unit.append(arr.ravel())
            times = np.sort(np.concatenate(per_unit)) if per_unit else np.array([])
            spike_times.append(times)
    return spike_times, t, cursor_pos


def bin_session(spike_times, t, cursor_pos, bin_s):
    """Bin spikes into counts and average cursor velocity over the same bins.

    Returns X (bins x channels, int16), Y (bins x 2, mm/s) and the bin edges.
    """
    edges = np.arange(t[0], t[-1], bin_s)
    n_bins = len(edges) - 1

    X = np.zeros((n_bins, len(spike_times)), dtype=np.int16)
    for ch, times in enumerate(spike_times):
        X[:, ch], _ = np.histogram(times, bins=edges)

    # Velocity at the behaviour sample rate, then the mean within each bin.
    vel = np.gradient(cursor_pos, t, axis=0)  # mm/s
    which_bin = np.digitize(t, edges) - 1
    Y = np.zeros((n_bins, 2))
    for d in range(2):
        sums = np.bincount(which_bin, weights=vel[:, d], minlength=n_bins + 1)[:n_bins]
        counts = np.bincount(which_bin, minlength=n_bins + 1)[:n_bins]
        Y[:, d] = sums / np.maximum(counts, 1)
    return X, Y, edges


def plot_raster(spike_times, t, cursor_pos, out_path, seconds):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t0 = t[0] + 60  # skip the first minute
    t1 = t0 + seconds
    fig, (ax_r, ax_v) = plt.subplots(
        2, 1, figsize=(11, 7), sharex=True, gridspec_kw={"height_ratios": [3, 1]}
    )
    for ch, times in enumerate(spike_times):
        w = times[(times >= t0) & (times < t1)]
        ax_r.plot(w - t0, np.full_like(w, ch), "|", color="k", markersize=2)
    ax_r.set_ylabel("Channel")
    ax_r.set_title(f"Spike raster and cursor velocity ({seconds} s)")

    m = (t >= t0) & (t < t1)
    vel = np.gradient(cursor_pos, t, axis=0)
    ax_v.plot(t[m] - t0, vel[m, 0], label="x")
    ax_v.plot(t[m] - t0, vel[m, 1], label="y")
    ax_v.set_ylabel("Velocity (mm/s)")
    ax_v.set_xlabel("Time (s)")
    ax_v.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)


def main():
    path = Path(sys.argv[1])
    bin_s = BIN_MS / 1000

    spike_times, t, cursor_pos = load_session(path)
    X, Y, _ = bin_session(spike_times, t, cursor_pos, bin_s)

    rates = X.sum(axis=0) / (X.shape[0] * bin_s)
    keep = rates > MIN_RATE_HZ
    X = X[:, keep]

    print(f"Session:   {path.stem}")
    print(f"Duration:  {t[-1] - t[0]:.0f} s at {1 / np.median(np.diff(t)):.0f} Hz")
    print(f"Channels:  {keep.sum()} kept of {len(keep)}")
    print(f"Bins:      {X.shape[0]} x {BIN_MS} ms")
    print(f"Mean rate: {rates[keep].mean():.1f} Hz per channel")
    print(f"Speed:     median {np.median(np.linalg.norm(Y, axis=1)):.0f} mm/s")

    out_npz = path.with_name(path.stem + "_binned.npz")
    np.savez_compressed(out_npz, X=X, Y=Y, bin_s=bin_s, kept_channels=np.where(keep)[0])
    print(f"Saved      {out_npz}")

    fig_dir = Path("figures")
    fig_dir.mkdir(exist_ok=True)
    out_png = fig_dir / f"{path.stem}_raster.png"
    plot_raster(spike_times, t, cursor_pos, out_png, PLOT_SECONDS)
    print(f"Saved      {out_png}")


if __name__ == "__main__":
    main()
