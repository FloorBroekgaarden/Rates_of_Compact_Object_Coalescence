"""
plot_rates.py — Plotting helpers for the restructured COC-rates dataset.

New data format (Data_Mandel_and_Broekgaarden_2026/):
  One CSV per formation channel; columns:
    compact_object_type  – "BH-BH" | "NS-BH" | "NS-NS"
    formation_channel    – e.g. "isolated-binary-evolution"
    study_key            – machine-readable unique label per (DCO type, study)
    label                – human-readable display label
    first_author         – first author name
    year                 – publication year
    month                – publication month (may be NaN)
    ads_url              – ADS abstract URL
    arxiv_url            – arXiv URL
    code                 – simulation code name (empty if not applicable)
    plotting_style       – one of:
                             "range"                 – span of simulation values
                             "credible_interval"     – CI with lower/central/upper
                             "single_value"          – single point estimate
                             "upper_limit"           – only upper limit(s)
                             "lower_limit"           – only lower limit(s)
                             "range_with_upper_limit"– range where max is an upper limit
                             "range_with_lower_limit"– range where min is a lower limit
    rate_Gpc3yr          – merger rate in Gpc^-3 yr^-1
    rate_type            – "lower" | "upper" | "central" | "single" | "" (generic model value)
    submodel             – model variant label (e.g. "fiducial", "pessimistic"), may be NaN
    notes                – raw notes from original data
"""

from pathlib import Path
from typing import Literal

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import rc, rcParams
from matplotlib.ticker import AutoMinorLocator

# ── Matplotlib style ───────────────────────────────────────────────────────────
rc("font", family="serif", weight="bold")
rc("text", usetex=True)
rcParams["text.latex.preamble"] = r"\usepackage{amsmath}" + "\n" + r"\boldmath"
rc("axes", linewidth=2)
rcParams.update({
    "xtick.major.size": 12, "ytick.major.size": 12,
    "xtick.minor.size": 8,  "ytick.minor.size": 8,
    "font.weight": "bold",
})
FONTSIZE = 24

# ── Colour palette ─────────────────────────────────────────────────────────────
_CHANNEL_NAMES = [
    "observations-GWs", "observations-sGRBs", "observations-kilonovae",
    "observations-pulsars", "isolated-binary-evolution", "CHE",
    "population-III", "flybys", "triples",
    "globular-clusters", "nuclear-clusters", "young-stellar-clusters",
    "primordial",
]
_PALETTE = ["orangered"] + list(sns.color_palette("husl", len(_CHANNEL_NAMES) - 1))
CHANNEL_COLOR: dict[str, tuple] = dict(zip(_CHANNEL_NAMES, _PALETTE))

CHANNEL_LABEL: dict[str, str] = {
    "observations-GWs":              r"Gravitational waves",
    "observations-sGRBs":            r"Short gamma-ray bursts",
    "observations-kilonovae":        r"Kilonovae",
    "observations-pulsars":          r"Galactic pulsar binaries",
    "isolated-binary-evolution":     r"Isolated binary evolution",
    "CHE":                           r"Chemically homogeneous evolution",
    "population-III":                r"Population III stars",
    "flybys":                        r"Wide isolated binaries + flybys",
    "triples":                       r"Triples / Multiples",
    "globular-clusters":             r"Globular clusters",
    "nuclear-clusters":              r"Nuclear star clusters",
    "young-stellar-clusters":        r"Young / Open star clusters",
    "primordial":                    r"Primordial",
}

DCO_LABEL = {"BH-BH": "BH-BH", "NS-BH": "NS-BH", "NS-NS": "NS-NS"}


# ── Data loading ───────────────────────────────────────────────────────────────

def load_channel(
    channel: str,
    data_dir: str | Path = "Data_Mandel_and_Broekgaarden_2026",
) -> pd.DataFrame:
    """Load one formation-channel CSV and return its DataFrame."""
    path = Path(data_dir) / f"{channel}.csv"
    return pd.read_csv(path, dtype={"year": "Int64", "month": "Int64"})


def load_all(
    data_dir: str | Path = "Data_Mandel_and_Broekgaarden_2026",
) -> pd.DataFrame:
    """Load and concatenate all formation-channel CSVs into one DataFrame."""
    dfs = [
        pd.read_csv(p, dtype={"year": "Int64", "month": "Int64"})
        for p in sorted(Path(data_dir).glob("*.csv"))
    ]
    return pd.concat(dfs, ignore_index=True)


# ── Drawing helpers ────────────────────────────────────────────────────────────

def _rates_for_group(group: pd.DataFrame) -> np.ndarray:
    """Return all rate values for a study group as a sorted array."""
    return np.sort(group["rate_Gpc3yr"].dropna().to_numpy())


def draw_study(
    ax: plt.Axes,
    group: pd.DataFrame,
    y: float,
    color,
    alpha: float = 1.0,
) -> None:
    """
    Draw one study (a group of rows sharing the same study_key + DCO type)
    onto `ax` at vertical position `y`.

    The visual encoding follows `plotting_style`:
      range / range_with_* → horizontal error bar spanning min–max,
                              individual values as dots
      credible_interval     → error bar with different central marker
      single_value          → single dot
      upper_limit           → downward-triangle marker at maximum
      lower_limit           → upward-triangle marker at minimum
    Pass alpha < 1 to dim superseded studies.
    """
    ps = group["plotting_style"].iloc[0]
    rates = _rates_for_group(group)
    if len(rates) == 0:
        return

    LWIDTH = 5.5
    DOT_S  = 125
    LIM_S  = 400
    Y = np.full_like(rates, y)

    if ps == "single_value":
        ax.scatter(rates[0], y, s=DOT_S, c=[color], zorder=100, marker="o", alpha=alpha)
        return

    if ps == "upper_limit":
        ax.scatter(rates[-1], y, s=LIM_S, c="k", zorder=1e6, marker=4, alpha=alpha)
        return

    if ps == "lower_limit":
        ax.scatter(rates[0], y, s=LIM_S, c="k", zorder=1e6, marker=5, alpha=alpha)
        return

    # For all range-based styles: draw horizontal error bar
    ax.errorbar(
        x=[rates.min(), rates.max()], y=[y, y], yerr=[0.42, 0.42],
        color=color, lw=LWIDTH, ecolor=color, zorder=5, alpha=alpha,
    )
    ax.errorbar(
        x=[rates.min(), rates.max()], y=[y, y], yerr=[0.42, 0.42],
        fmt="o", lw=3.5, ecolor="k", color="k", zorder=1e5, alpha=alpha,
    )
    ax.scatter(rates, Y, s=DOT_S, color=[color], zorder=100, marker="o", alpha=alpha)

    if ps == "range_with_upper_limit":
        ax.scatter(rates.max(), y, s=LIM_S, c="k", zorder=1e6, marker=4, alpha=alpha)
    elif ps == "range_with_lower_limit":
        ax.scatter(rates.min(), y, s=LIM_S, c="k", zorder=1e6, marker=5, alpha=alpha)

    if ps == "credible_interval":
        # highlight centre value
        central_rows = group[group["rate_type"] == "central"]
        if not central_rows.empty:
            cx = central_rows["rate_Gpc3yr"].iloc[0]
            ax.scatter(cx, y, s=DOT_S, c="k", zorder=1e6, marker="o", alpha=alpha)


# ── Main figure function ───────────────────────────────────────────────────────

def make_figure(
    dco_type: Literal["BH-BH", "NS-BH", "NS-NS"],
    channels: list[str],
    data_dir: str | Path = "Data_Mandel_and_Broekgaarden_2026",
    order: Literal["year", "max_rate"] = "year",
    fig_width: float = 20,
    save_path: str | Path | None = None,
    include_superseded: bool = True,
    dim_superseded: bool = True,
    superseded_alpha: float = 0.30,
) -> tuple[plt.Figure, plt.Axes]:
    """
    Build a horizontal-rate-density figure for `dco_type`.

    Parameters
    ----------
    dco_type          : "BH-BH" | "NS-BH" | "NS-NS"
    channels          : list of formation-channel names to include (in display order)
    data_dir          : path to Data_Mandel_and_Broekgaarden_2026/
    order             : sort studies within each channel by "year" or "max_rate"
    fig_width         : figure width in inches
    save_path         : if given, save figure to this path (PNG + PDF)
    include_superseded: if False, drop studies with superseded==True entirely
    dim_superseded    : if True (and include_superseded=True), draw superseded
                        studies at `superseded_alpha` opacity
    superseded_alpha  : alpha value for superseded studies (default 0.30)
    """
    xmin, xmax = 1e-3, 1e5

    # ── Load and filter data ─────────────────────────────────────────────
    frames = []
    for ch in channels:
        try:
            df_ch = load_channel(ch, data_dir)
        except FileNotFoundError:
            print(f"WARNING: {ch}.csv not found — skipping.")
            continue
        frames.append(df_ch[df_ch["compact_object_type"] == dco_type])

    if not frames:
        raise ValueError("No data found for the requested channels / DCO type.")

    df_all = pd.concat(frames, ignore_index=True)

    # Normalise superseded column (may be absent in some channel CSVs)
    if "superseded" not in df_all.columns:
        df_all["superseded"] = False
    df_all["superseded"] = df_all["superseded"].astype(str).str.lower() == "true"

    if not include_superseded:
        df_all = df_all[~df_all["superseded"]]

    # ── Determine y positions and collect y-tick labels ──────────────────
    y_pos: dict[tuple[str, str], float] = {}  # (channel, study_key) → y
    ytick_labels: list[str] = []
    ytick_positions: list[float] = []
    channel_label_positions: dict[str, float] = {}

    y = 0.0
    for ch in channels:
        ch_df = df_all[df_all["formation_channel"] == ch]
        if ch_df.empty:
            continue

        y -= 1.0  # blank row above each channel

        # Determine study order within channel
        studies = ch_df.groupby("study_key", sort=False)
        if order == "max_rate":
            order_vals = {k: g["rate_Gpc3yr"].max() for k, g in studies}
            sorted_keys = sorted(order_vals, key=order_vals.__getitem__)
        else:  # year
            order_vals = {k: (g["year"].dropna().min(), g.name) for k, g in studies}
            sorted_keys = list(ch_df.drop_duplicates("study_key")
                               .sort_values(["year", "study_key"])["study_key"])

        channel_label_positions[ch] = y - len(sorted_keys) / 2

        for sk in sorted_keys:
            y_pos[(ch, sk)] = y
            label = ch_df.loc[ch_df["study_key"] == sk, "label"].iloc[0]
            ytick_labels.append(label)
            ytick_positions.append(y)
            y -= 1.0

        y -= 1.0  # blank row below each channel

    total_height = -y

    # ── Create figure ────────────────────────────────────────────────────
    fig_height = max(6, total_height * 0.28 + 2)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    ax.set_xscale("log")
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(y - 0.5, 0.5)
    ax.set_yticks([])

    xlabel = (
        r"$\mathrm{Local}\ \mathbf{" + DCO_LABEL[dco_type].replace("-", r"\text{-}")
        + r"}\ \mathbf{merger\ rate\ density}\ [\mathrm{Gpc}^{-3}\ \mathrm{yr}^{-1}]$"
    )
    ax.set_xlabel(xlabel, fontsize=FONTSIZE + 6, labelpad=4)
    ax.tick_params(which="major", length=10, width=1.5)
    ax.tick_params(which="minor", length=5,  width=1.5)
    for spine in ax.spines.values():
        spine.set_linewidth(1.2)

    # Vertical grid lines
    for xv in [1e-4, 1e-3, 1e-2, 1e-1, 1, 10, 1e2, 1e3, 1e4, 1e5]:
        ax.axvline(xv, lw=1.5, color="gray", ls=":", zorder=0)

    # ── Plot each study ──────────────────────────────────────────────────
    for ch in channels:
        ch_df = df_all[df_all["formation_channel"] == ch]
        color = CHANNEL_COLOR.get(ch, "gray")

        for sk, group in ch_df.groupby("study_key", sort=False):
            key = (ch, sk)
            if key not in y_pos:
                continue
            yv = y_pos[key]

            is_sup = bool(group["superseded"].iloc[0]) if "superseded" in group.columns else False
            alpha  = superseded_alpha if (is_sup and dim_superseded) else 1.0

            draw_study(ax, group, yv, color, alpha=alpha)

            # Study label to the left (or right) of the data
            rates = _rates_for_group(group)
            if len(rates) == 0:
                continue
            label_text = group["label"].iloc[0]
            if rates.min() > 2e-2:
                ax.text(rates.min() / 1.25, yv, label_text,
                        ha="right", va="center", fontsize=FONTSIZE - 5, alpha=alpha)
            else:
                ax.text(rates.max() * 1.25, yv, label_text,
                        ha="left", va="center", fontsize=FONTSIZE - 5, alpha=alpha)

        # Channel label
        if ch in channel_label_positions:
            ax.text(9e4, channel_label_positions[ch],
                    r"\textbf{%s}" % CHANNEL_LABEL.get(ch, ch),
                    ha="right", va="center", fontsize=FONTSIZE + 8,
                    color=color, weight="bold")

    plt.tight_layout()

    if save_path is not None:
        sp = Path(save_path)
        plt.savefig(sp.with_suffix(".png"), dpi=300)
        plt.savefig(sp.with_suffix(".pdf"))

    return fig, ax


# ── Quick-start example ────────────────────────────────────────────────────────

if __name__ == "__main__":
    CHANNELS_BHBH = [
        "observations-GWs",
        "isolated-binary-evolution", "CHE",
        "population-III", "triples", "flybys",
        "globular-clusters", "nuclear-clusters", "young-stellar-clusters",
        "primordial",
    ]
    fig, ax = make_figure(
        dco_type="BH-BH",
        channels=CHANNELS_BHBH,
        order="year",
        save_path="Rates_BHBH_yearsorted",
    )
    plt.show()
