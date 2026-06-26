"""
Interactive versions of the merger-rate-density figures from
Make_figures_COC_rates.ipynb.

Same layout / style / size as the static matplotlib figures (`make_figure`),
but rendered with Plotly so that hovering over a scatter point shows:
    - study name
    - model (submodel)
    - code (population-synthesis code)
    - parameter variation (where available, from the relationships file)

Output: one self-contained .html per figure in ../figures/interactive/.

Run with a python that has pandas + plotly, e.g.:
    /usr/local/bin/python3 make_interactive_figures.py
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ───────────────────────── paths & constants ──────────────────────────────
DATA_DIR = Path("../Data_Mandel_and_Broekgaarden_2026")
OUT_DIR = Path("../figures/interactive")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ALL_CHANNELS = [
    "observations-GWs", "observations-sGRBs", "observations-kilonovae",
    "observations-pulsars", "isolated-binary-evolution", "CHE", "population-III",
    "flybys", "triples", "globular-clusters", "nuclear-clusters",
    "young-stellar-clusters", "primordial",
]

# exact husl palette used by the static figures (orangered + seaborn husl)
CHANNEL_COLOR = {
    "observations-GWs": "#ff4500", "observations-sGRBs": "#f77189",
    "observations-kilonovae": "#e68332", "observations-pulsars": "#bb9832",
    "isolated-binary-evolution": "#97a431", "CHE": "#50b131",
    "population-III": "#34af84", "flybys": "#36ada4", "triples": "#38aabf",
    "globular-clusters": "#3ba3ec", "nuclear-clusters": "#a48cf4",
    "young-stellar-clusters": "#e866f4", "primordial": "#f668c2",
}
CHANNEL_LABEL = {
    "observations-GWs": "Gravitational waves",
    "observations-sGRBs": "Short gamma-ray bursts",
    "observations-kilonovae": "Kilonovae",
    "observations-pulsars": "Galactic pulsar binaries",
    "isolated-binary-evolution": "Isolated binary evolution",
    "CHE": "Chemically homogeneous evolution",
    "population-III": "Population III stars",
    "flybys": "Wide isolated binaries + flybys",
    "triples": "Triples / Multiples",
    "globular-clusters": "Globular clusters",
    "nuclear-clusters": "Nuclear star clusters",
    "young-stellar-clusters": "Young / Open star clusters",
    "primordial": "Primordial",
}
DCO_LABEL = {"BH-BH": "BH-BH", "NS-BH": "NS-BH", "NS-NS": "NS-NS"}

XMIN, XMAX = 1e-3, 1e5
FONTSIZE = 24


# ───────────────────────────── data loading ───────────────────────────────
def load_channel(channel: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / f"{channel}.csv",
                       dtype={"year": "Int64", "month": "Int64"}, engine="python")


def build_variation_lookup() -> dict:
    """(study_key, dco, submodel) -> human-readable parameter-variation string.

    A submodel is the *result* of a one-parameter variation when it appears as a
    `to_submodel` in the relationships file. Multiple variations are joined with '; '.
    """
    rel = pd.read_csv(DATA_DIR / "isolated-binary-evolution_relationships.csv",
                      dtype=str).fillna("")
    lut: dict[tuple, list[str]] = {}
    for _, r in rel.iterrows():
        key = (r["study_key"], r["compact_object_type"], r["to_submodel"])
        fam = r["parameter_family"]
        fv, tv = r["from_value"], r["to_value"]
        if fv or tv:
            desc = f"{fam}: {fv} → {tv}" if (fv or tv) else fam
        else:
            desc = fam
        lut.setdefault(key, [])
        if desc not in lut[key]:
            lut[key].append(desc)
    return {k: "; ".join(v) for k, v in lut.items()}


# ──────────────────────────── hover text ──────────────────────────────────
def hover_text(label, submodel, code, rate, variation):
    parts = [f"<b>{label}</b>"]
    if submodel:
        parts.append(f"Model: {submodel}")
    if code:
        parts.append(f"Code: {code}")
    parts.append(f"Rate: {rate:g} Gpc⁻³ yr⁻¹")
    parts.append(f"Variation: {variation if variation else '—'}")
    return "<br>".join(parts)


# ───────────────────────── main figure builder ────────────────────────────
def make_interactive_figure(dco_type, channels, order="year",
                            save_name=None, include_superseded=True,
                            dim_superseded=True, superseded_alpha=0.30,
                            code_label=False):
    var_lut = build_variation_lookup()

    frames = []
    for ch in channels:
        try:
            df_ch = load_channel(ch)
        except FileNotFoundError:
            print(f"WARNING: {ch}.csv not found - skipping.")
            continue
        frames.append(df_ch[df_ch["compact_object_type"] == dco_type])
    df = pd.concat(frames, ignore_index=True)

    if "superseded" not in df.columns:
        df["superseded"] = False
    df["superseded"] = df["superseded"].astype(str).str.lower() == "true"
    if not include_superseded:
        df = df[~df["superseded"]]

    # ── y positions (mirrors make_figure) ──
    y_pos, channel_label_y, separator_ys = {}, {}, []
    y, total_studies = 0.0, 0
    active = [ch for ch in channels if not df[df.formation_channel == ch].empty]
    for i_ch, ch in enumerate(active):
        ch_df = df[df.formation_channel == ch]
        y -= 1.0
        if order == "max_rate":
            keys = ch_df.groupby("study_key")["rate_Gpc3yr"].max().sort_values().index.tolist()
        else:
            keys = ch_df.drop_duplicates("study_key").sort_values(["year", "study_key"])["study_key"].tolist()
        channel_label_y[ch] = y - (len(keys) - 1) / 2
        for sk in keys:
            y_pos[(ch, sk)] = y
            y -= 1.0
            total_studies += 1
        y -= 1.0
        if i_ch < len(active) - 1:
            separator_ys.append(y + 0.5)
    y_min = y

    fig = go.Figure()

    # ── GWTC-5 observational band ──
    lvk = df[(df.study_key == "Abbott_2026_GWTC5") & (df.compact_object_type == dco_type)]
    lvk_rates = lvk["rate_Gpc3yr"].dropna() if not lvk.empty else pd.Series(dtype=float)
    if not lvk_rates.empty:
        fig.add_vrect(x0=lvk_rates.min(), x1=lvk_rates.max(),
                      fillcolor=CHANNEL_COLOR["observations-GWs"], opacity=0.15,
                      line_width=0, layer="below")

    # ── separators ──
    for sy in separator_ys:
        fig.add_shape(type="line", x0=XMIN, x1=XMAX, y0=sy, y1=sy,
                      line=dict(color="gray", width=1.5, dash="dot"), layer="below")

    annotations = []
    # ── per study ──
    for ch in active:
        ch_df = df[df.formation_channel == ch]
        color = CHANNEL_COLOR.get(ch, "gray")
        for sk, group in ch_df.groupby("study_key", sort=False):
            if (ch, sk) not in y_pos:
                continue
            yv = y_pos[(ch, sk)]
            is_sup = bool(group["superseded"].iloc[0])
            op = superseded_alpha if (is_sup and dim_superseded) else 1.0
            ps = group["plotting_style"].iloc[0]

            g = group.dropna(subset=["rate_Gpc3yr"]).copy()
            g = g[g["rate_Gpc3yr"].apply(lambda v: np.isfinite(v))]
            if g.empty:
                continue
            g = g.sort_values("rate_Gpc3yr")
            rates = g["rate_Gpc3yr"].to_numpy()
            label = str(group["label"].iloc[0])
            code = str(group["code"].iloc[0]) if "code" in group else ""

            # hover text per point
            htxt = []
            for _, row in g.iterrows():
                sm = str(row.get("submodel", "") or "")
                variation = var_lut.get((sk, dco_type, sm), "")
                htxt.append(hover_text(label, sm, code, row["rate_Gpc3yr"], variation))

            # range line (for range-type styles)
            if ps in ("range", "range_with_upper_limit", "range_with_lower_limit",
                      "credible_interval") and len(rates) > 1:
                fig.add_trace(go.Scatter(
                    x=[rates.min(), rates.max()], y=[yv, yv], mode="lines",
                    line=dict(color=color, width=6), opacity=op,
                    hoverinfo="skip", showlegend=False))

            # limit markers
            if ps == "upper_limit":
                fig.add_trace(go.Scatter(x=[rates.max()], y=[yv], mode="markers",
                    marker=dict(symbol="triangle-left", size=16, color="black"),
                    opacity=op, hovertext=[htxt[-1]], hoverinfo="text", showlegend=False))
            elif ps == "lower_limit":
                fig.add_trace(go.Scatter(x=[rates.min()], y=[yv], mode="markers",
                    marker=dict(symbol="triangle-right", size=16, color="black"),
                    opacity=op, hovertext=[htxt[0]], hoverinfo="text", showlegend=False))
            else:
                # the scatter points (these carry the hover)
                fig.add_trace(go.Scatter(
                    x=rates, y=np.full_like(rates, yv), mode="markers",
                    marker=dict(symbol="circle", size=11, color=color,
                                line=dict(width=0)),
                    opacity=op, hovertext=htxt, hoverinfo="text", showlegend=False))
                if ps == "range_with_upper_limit":
                    fig.add_trace(go.Scatter(x=[rates.max()], y=[yv], mode="markers",
                        marker=dict(symbol="triangle-left", size=16, color="black"),
                        opacity=op, hoverinfo="skip", showlegend=False))
                elif ps == "range_with_lower_limit":
                    fig.add_trace(go.Scatter(x=[rates.min()], y=[yv], mode="markers",
                        marker=dict(symbol="triangle-right", size=16, color="black"),
                        opacity=op, hoverinfo="skip", showlegend=False))

            # study label text (left or right of the points)
            lab = label.replace("&", "&amp;")
            if code_label and code:
                lab = f"{lab} [{code}]"
            if rates.min() > 2e-2:
                annotations.append(dict(x=np.log10(rates.min() / 1.25), y=yv, text=lab,
                                        xanchor="right", yanchor="middle", showarrow=False,
                                        font=dict(size=FONTSIZE - 7), opacity=op))
            else:
                xa = max(rates.max() * 1.25, 1e-3 * 1.35)
                annotations.append(dict(x=np.log10(xa), y=yv, text=lab,
                                        xanchor="left", yanchor="middle", showarrow=False,
                                        font=dict(size=FONTSIZE - 7), opacity=op))

        # channel label on the right
        if ch in channel_label_y:
            annotations.append(dict(
                x=np.log10(9e4), y=channel_label_y[ch],
                text=f"<b>{CHANNEL_LABEL.get(ch, ch)}</b>", xanchor="right",
                yanchor="middle", showarrow=False,
                font=dict(size=FONTSIZE + 2, color=color)))

    # ── layout / styling to match static figures ──
    xlabel = f"Local <b>{DCO_LABEL[dco_type]}</b> merger rate density [Gpc<sup>-3</sup> yr<sup>-1</sup>]"
    px_per_inch = 64
    fig_height = max(6, total_studies * 0.28 + 2 * len(active) * 0.28 + 2)
    width_px = int(20 * px_per_inch)
    height_px = int(max(500, (0.5 - y_min) * 26 + 120))

    fig.update_xaxes(type="log", range=[np.log10(XMIN), np.log10(XMAX)],
                     title=dict(text=xlabel, font=dict(size=FONTSIZE)),
                     showgrid=True, gridcolor="lightgray", gridwidth=1, griddash="dot",
                     ticks="outside", tickfont=dict(size=FONTSIZE - 6),
                     mirror=True, showline=True, linewidth=1.5, linecolor="black",
                     side="bottom")
    fig.update_yaxes(range=[y_min - 0.5, 0.5], showticklabels=False, showgrid=False,
                     zeroline=False, mirror=True, showline=True, linewidth=1.5,
                     linecolor="black")
    fig.update_layout(
        width=width_px, height=height_px, plot_bgcolor="white",
        margin=dict(l=40, r=40, t=70, b=70), annotations=annotations,
        hoverlabel=dict(bgcolor="white", font_size=14, align="left"),
        title=dict(text=f"Local {DCO_LABEL[dco_type]} merger rate density (interactive — hover the points)",
                   x=0.5, font=dict(size=FONTSIZE - 4)),
    )

    if save_name:
        out = OUT_DIR / f"{save_name}.html"
        fig.write_html(out, include_plotlyjs="cdn")
        print(f"Saved {out}")
    return fig


# ───────────────────────────── figure set ─────────────────────────────────
CHANNELS_FULL = {
    "BH-BH": ["observations-GWs", "isolated-binary-evolution", "CHE", "population-III",
              "triples", "flybys", "globular-clusters", "nuclear-clusters",
              "young-stellar-clusters", "primordial"],
    "NS-BH": ["observations-GWs", "observations-pulsars", "isolated-binary-evolution",
              "CHE", "population-III", "triples", "flybys", "globular-clusters",
              "nuclear-clusters", "young-stellar-clusters"],
    "NS-NS": ["observations-GWs", "observations-sGRBs", "observations-kilonovae",
              "observations-pulsars", "isolated-binary-evolution", "triples",
              "globular-clusters", "nuclear-clusters", "young-stellar-clusters"],
}
ISO = ["observations-GWs", "isolated-binary-evolution"]

if __name__ == "__main__":
    save = {"BH-BH": "Rates_BHBH", "NS-BH": "Rates_NSBH", "NS-NS": "Rates_NSNS"}
    for dco in ["BH-BH", "NS-BH", "NS-NS"]:
        make_interactive_figure(dco, CHANNELS_FULL[dco],
                                save_name=f"{save[dco]}_yearsorted_interactive")
        make_interactive_figure(dco, ISO, code_label=True,
                                save_name=f"{save[dco]}_isolated_only_interactive")
    print("\nDone. Open the .html files in ../figures/interactive/ in a browser.")
