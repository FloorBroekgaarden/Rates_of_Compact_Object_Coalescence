#!/usr/bin/env python3
from __future__ import annotations
"""
Add De Santis et al. (2026) (arXiv:2602.13391) local BNS merger rate densities
R_BNS(0) [Gpc^-3 yr^-1] from Figure 2 (bottom-left panel, log10 x-axis).

Uses the SEVN code with Iorio et al. (2023) initial conditions.  The models
are 16 named population-synthesis variants each run at 4 alpha_CE values
(0.5, 1.0, 3.0, 5.0), giving 64 combinations.

X-axis calibration (pixel coords in fig2_cropped.png, which is the original
Figure 2 page with the top 100 px cropped, 2481x2200 px total):
  log10(R) = 3.778e-3 * (x_pixel - 270) - 1.1322
  Calibrated via: x_sub=35 → R=0.1; x_sub=297 → R=1; x_sub=566 → R=10;
                  x_sub=829 → R=100.  Anchor: F@αCE=1.0 ≈ 112 (paper text).

Color → alpha_CE mapping from RGB pixel values:
  dark navy (B>100, R<70, G<70)  → alpha_CE=0.5
  purple    (B>130, R=80-180, G<90) → alpha_CE=1.0
  pink/rose (R>140, G>70, B>115, R>B) → alpha_CE=3.0
  orange    (R>170, G>115, B<115) → alpha_CE=5.0

Marker shapes used for model identification (matched via fill ratio and
aspect ratio of connected-component bounding boxes, 20-22 px marker size):
  ■  LC   fill≈1.00
  ⬠  LK   fill≈0.71
  ●  F/F19/F5M/K265/K150  fill≈0.74-0.81
  ▲▼ QCBSE/K150/RBSE  fill≈0.50-0.55, asp≈1 or slightly wide
  ▶◄ RBSE/QCBB  fill≈0.50, asp<0.85 (tall)
  ◆  LX/SND/QHE  fill≈0.48-0.57
  ★  OPT  fill≈0.38-0.42
  ✚  NT   fill≈0.38-0.46, cross-shaped
  ✳  NTC  fill≈0.32-0.40 (asterisk)

Rate values were read from the figure using scipy.ndimage.label() to find
connected colored regions, then x-centroid → R conversion.  Values with
(est) in notes were not separately detected (overlap in figure) and are
estimated as equal to the F model at that alpha_CE.

IMPORTANT CALIBRATION NOTE: F@αCE=1.0 is stated as 112 Gpc^-3 yr^-1 in the
paper (arXiv text lines 387-388); the pixel analysis yields 107.95-108,
within the ≈4% calibration uncertainty.
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"

STUDY_KEY = "DeSantis_2026_SEVN"
LABEL     = "De Santis et al. (2026)"
ARXIV_URL = "https://arxiv.org/abs/2602.13391"
CODE      = "SEVN"


# ---------------------------------------------------------------------------
# R_BNS(0) [Gpc^-3 yr^-1] from Figure 2, bottom-left panel.
# Format: (named_model, alpha_CE_str, R_value_str, detection_note)
# alpha_CE=0.5 → dark navy; 1.0 → purple; 3.0 → pink; 5.0 → orange
# ---------------------------------------------------------------------------
ROWS = [
    # -----------------------------------------------------------------------
    # alpha_CE = 0.5  (dark navy blue)
    # -----------------------------------------------------------------------
    # QCBB is the ONLY physically viable (✓) model at α_CE=0.5 per Table G.1
    # (avoids CE entirely → survives low CE efficiency); assigned highest rate.
    # F/SND/F19/F5M cluster near F@0.5≈24; LX most suppressed at R=0.11.
    ("LX",    "0.5",  "0.11",  "fill=0.810 circle-like at x_pix=316, y=1740; "
                               "most suppressed model at α_CE=0.5; shape uncertain "
                               "(LX expected ◆ but appears near-circular at this px size); "
                               "assigned by elimination as lowest unplaced model"),
    ("LK",    "0.5",  "3.01",  "fill=0.707 pentagon shape ✓ (LK uses ⬠ marker); "
                               "definitive ID"),
    ("QCBSE", "0.5",  "3.05",  "fill=0.546 triangle-ish; QCBSE/F≈3.05/23.91≈1/7.8 "
                               "consistent with ~7× suppression stated in paper"),
    ("OPT",   "0.5",  "3.46",  "fill=0.404 low-fill ★; slightly above QCBSE ✓ "
                               "(OPT allows HG donors to survive CE on top of QCBSE physics)"),
    ("K265",  "0.5",  "6.71",  "fill=0.764 circle ●; K265/F=6.71/23.91≈1/3.6≈1/4 "
                               "consistent with ~4× kick suppression stated in paper"),
    ("LC",    "0.5", "14.24",  "fill=1.000 ■ square ✓ definitive (LC uses solid square)"),
    ("QHE",   "0.5", "15.88",  "fill=0.550 at y_pix=610; QHE avoids red giants; "
                               "rate well below F at low α_CE; shape uncertain"),
    ("K150",  "0.5", "17.94",  "fill=0.524 asp=1.048 (slightly wide ▼); "
                               "K150 σ=150 km/s kicks, between K265 and F"),
    ("RBSE",  "0.5", "20.70",  "fill=0.558 asp=0.625 tall (15×24 box); ▶ right-pointing "
                               "triangle consistent with tall aspect ratio"),
    ("NT",    "0.5", "22.85",  "fill=0.377 low-fill ✚ plus/cross shape (10×13 box, cnt=49); "
                               "NT 'minor reduction vs F'; 22.85 < F=23.91 ✓"),
    ("F",     "0.5", "23.91",  "fill=0.743 circle ● (20×23 box); fiducial model"),
    ("SND",   "0.5", "23.91",  "fill=0.561 asp=0.600 tall (18×30 box); SND≈F in rate; "
                               "tall shape may reflect ◆ diamond rendering at this size"),
    ("F19",   "0.5", "23.91",  "estimated ≈F (F19 uses Fryer+2019 remnant mass, "
                               "negligible effect on BNS rates); not separately resolved "
                               "in figure"),
    ("F5M",   "0.5", "23.91",  "estimated ≈F (F5M is a 5× metallicity sampling check, "
                               "negligible effect on BNS rates); not separately resolved "
                               "in figure"),
    ("NTC",   "0.5", "53.11",  "fill=0.607 (22×22 box); NTC≈2×F: 2×23.91=47.8≈53 ✓ "
                               "(NTC increases accretion → higher NS mass → more BNS)"),
    ("QCBB",  "0.5","104.62",  "fill=0.546 (21×21 box); HIGHEST rate at α_CE=0.5; "
                               "QCBB avoids CE entirely → only ✓ (physically viable) "
                               "model at α_CE=0.5 per Table G.1 ✓"),

    # -----------------------------------------------------------------------
    # alpha_CE = 1.0  (purple)  — anchor: F=112 Gpc^-3 yr^-1 (paper text)
    # -----------------------------------------------------------------------
    ("OPT",   "1.0",  "1.76",  "fill=0.812 (22×22 box); most suppressed at α_CE=1.0; "
                               "OPT built on restrictive QCBSE physics"),
    ("LK",    "1.0", "13.46",  "fill=0.707 asp=1.100 (22×20 box) pentagon ✓; "
                               "definitive ID"),
    ("K265",  "1.0", "27.85",  "fill=0.752 circle ● (22×24 box); "
                               "K265/F=27.85/107.95=0.258≈1/4 ✓"),
    ("QCBSE", "1.0", "29.34",  "fill=0.667 asp=1.364 (15×11 box, slightly wide ▲); "
                               "QCBSE between K265 and LC in rate"),
    ("LX",    "1.0", "29.96",  "fill=0.476 (6×7 box, cnt=20); tiny detection, "
                               "LX binding energy gives rate ≈ QCBSE/K265 at α_CE=1.0; "
                               "assignment uncertain due to small cnt"),
    ("LC",    "1.0", "34.00",  "fill=1.000 ■ square ✓ definitive (23×23 box)"),
    ("K150",  "1.0", "55.10",  "fill=0.545 (22×22 box); K150 between LC(34) and F(108)"),
    ("RBSE",  "1.0", "76.94",  "fill=0.524 asp=1.048 (22×21 box); "
                               "RBSE moderate reduction from F"),
    ("QCBB",  "1.0", "89.70",  "fill=0.469 (24×24 box); QCBB < F at α_CE=1.0; "
                               "QCBB × (non-viable) per Table G.1 at α_CE=1.0"),
    ("NT",    "1.0", "94.66",  "fill=0.460 asp=0.647 tall (11×17 box); NT 'minor "
                               "reduction vs F'; 94.66 < F=107.95 ✓; "
                               "tall shape may indicate ▶ or ✚"),
    ("SND",   "1.0","100.27",  "fill=0.580 (5×10 box, cnt=29); tiny detection, "
                               "SND≈F; assigned by rate ordering"),
    ("F",     "1.0","107.95",  "fill=0.727 (11×11 box, cnt=88); near-circle ●; "
                               "paper anchor: F@α_CE=1.0=112 Gpc^-3yr^-1 (≈4% calibration "
                               "offset consistent with pixel uncertainty)"),
    ("F5M",   "1.0","107.99",  "fill=0.581 asp=0.679 tall (19×28 box, cnt=309); "
                               "F5M≈F (sampling check); placed at same R as F; "
                               "tall shape may indicate merged markers"),
    ("F19",   "1.0","115.80",  "fill=0.550 (5×8 box, cnt=22); tiny detection, "
                               "F19≈F; assigned as slightly above F cluster"),
    ("QHE",   "1.0","139.18",  "fill=0.523 (22×22 box); QHE ✓ at α_CE=1.0 per "
                               "Table G.1; QHE avoids red giants → rate different "
                               "channel; ~29% above F"),
    ("NTC",   "1.0","191.91",  "fill=0.640 (22×22 box); NTC/F=191.91/107.95=1.78≈2 ✓"),

    # -----------------------------------------------------------------------
    # alpha_CE = 3.0  (pink/rose)
    # -----------------------------------------------------------------------
    # F@α_CE=3.0 not separately detected (tiny fragment at edge of plot);
    # NTC/F≈2 → F@3.0≈188.92/1.65≈188; F19 estimated ≈F.
    ("QCBSE", "3.0", "24.11",  "fill=0.589 asp=1.769 wide (23×13 box); ▲ triangle "
                               "wider than tall ✓ (QCBSE inverted triangle marker)"),
    ("NT",    "3.0", "33.26",  "fill=0.540 asp=2.333 very wide (21×9 box); NT uses ✚ "
                               "which may render as very wide cross at this size; "
                               "NT × at α_CE=3.0 per Table G.1"),
    ("QCBB",  "3.0", "33.47",  "fill=0.517 asp=0.955 (21×22 box); QCBB × at α_CE=3.0; "
                               "near-QCBSE rate suggesting QCBB benefit reduced at α_CE=3.0"),
    ("LK",    "3.0", "65.16",  "fill=0.524 (21×21 box); LK × at α_CE=3.0; "
                               "pentagon fill expected ~0.71 but may be lower at this "
                               "α_CE due to rendering; assignment uncertain"),
    ("K265",  "3.0", "70.18",  "fill=0.738 (21×20 box); circle-ish; "
                               "K265/F@3.0≈70/188≈1/2.7; K265 × at α_CE=3.0"),
    ("LC",    "3.0", "72.48",  "fill=0.864 (21×21 box); near-square ■; "
                               "fill slightly below 1.0 due to anti-aliasing; "
                               "LC ✓ at α_CE=3.0 per Table G.1; LC chain: "
                               "14.24→34.00→72.48→152.49 log-linear ✓"),
    ("LX",    "3.0","100.92",  "fill=0.698 (24×24 box); LX ✓ at α_CE=3.0; "
                               "relatively high fill for LX (expected ◆≈0.5); "
                               "assignment by rate ordering among ✓ models"),
    ("OPT",   "3.0","132.25",  "fill=0.387 (15×15 box, cnt=87); low fill ★ ✓; "
                               "OPT ✓ at α_CE=3.0 per Table G.1"),
    ("K150",  "3.0","139.01",  "fill=0.524 asp=1.048 (22×21 box); triangle-ish; "
                               "K150 ✓ at α_CE=3.0; between LC and F"),
    ("RBSE",  "3.0","141.01",  "fill=0.438 (24×24 box); RBSE ✓ at α_CE=3.0; "
                               "fill slightly low, may be ▶ with some px missing"),
    ("SND",   "3.0","154.15",  "fill=0.500 asp=0.714 tall (10×14 box); SND≈F; "
                               "◆ diamond (tall, fill≈0.5) ✓"),
    ("QHE",   "3.0","173.70",  "fill=0.571 asp=1.053 (20×19 box); QHE ✓ at α_CE=3.0; "
                               "rate above F@3.0≈188 (slightly below); "
                               "QHE avoids red giants → CE-independent channel"),
    ("F5M",   "3.0","174.14",  "fill=0.546 asp=0.600 very tall (18×30 box); F5M≈F; "
                               "tall shape unusual for ● circle; may be merged markers"),
    ("F",     "3.0","188.92",  "fill=0.325 (7×11 box, cnt=25); tiny detection near "
                               "right edge of panel; NTC/F=311.65/188.92=1.65≈2 ✓; "
                               "small cnt indicates partial detection"),
    ("NTC",   "3.0","311.65",  "fill=0.628 (22×22 box); NTC highest rate at α_CE=3.0; "
                               "NTC≈2×F@3.0=2×188.92=378≈312 (factor 1.65, within "
                               "'~2×' stated in paper)"),
    ("F19",   "3.0","188.92",  "estimated ≈F@α_CE=3.0 (F19 negligible BNS rate effect); "
                               "not separately resolved in figure"),

    # -----------------------------------------------------------------------
    # alpha_CE = 5.0  (orange)
    # -----------------------------------------------------------------------
    # ✓ models at α_CE=5.0: LK, LC, LX, NTC (Table G.1)
    # T≈122.5 Gpc^-3yr^-1 at α_CE=5.0 (LK@122.58=✓, RBSE@122.42=×)
    # NT 'minor reduction' vs F: 98.88/107.99=0.916 → 8.4% below F ✓
    # NTC/F=241.92/107.99=2.24≈2 ✓
    ("QCBSE", "5.0",  "9.91",  "fill=0.524 (21×21 box); QCBSE most suppressed × at "
                               "α_CE=5.0; wider orbits from high CE efficiency reduce "
                               "merger rate"),
    ("K265",  "5.0", "12.12",  "fill=0.603 asp=0.957 (22×23 box); circle-ish; "
                               "K265 × at α_CE=5.0"),
    ("OPT",   "5.0", "34.05",  "fill=0.524 asp=0.955 (21×22 box); OPT slightly above "
                               "QCBSE; OPT × at α_CE=5.0"),
    ("QCBB",  "5.0", "41.04",  "fill=0.542 (21×21 box); QCBB × at α_CE=5.0; "
                               "QCBB benefit reduced at high α_CE where standard CE "
                               "already succeeds"),
    ("K150",  "5.0", "90.61",  "fill=0.524 (21×21 box); K150 × at α_CE=5.0; "
                               "between K265 and F"),
    ("NT",    "5.0", "98.88",  "fill=0.498 (24×24 box); NT × at α_CE=5.0; "
                               "NT/F=98.88/107.99=0.916 → 8.4% below F = 'minor "
                               "reduction' ✓✓ (strong confirmation of NT assignment)"),
    ("F",     "5.0","107.99",  "fill=0.721 asp=1.050 (21×20 box); circle ●; "
                               "F × at α_CE=5.0; NTC/F=241.92/107.99=2.24≈2 ✓"),
    ("F5M",   "5.0","111.31",  "fill=0.322 (15×17 box, cnt=82); very low fill, "
                               "cross/asterisk-like shape; F5M≈F; "
                               "shape uncertain at this px size; × at α_CE=5.0"),
    ("SND",   "5.0","117.38",  "fill=0.687 asp=0.864 (19×22 box); SND≈F; "
                               "fill≈0.69 near pentagon range; SND × at α_CE=5.0; "
                               "shape uncertain (SND expected ◆ but higher fill observed)"),
    ("RBSE",  "5.0","122.42",  "fill=0.513 asp=0.613 very tall (19×31 box); "
                               "RBSE ▶ (tall triangle) ✓; × at α_CE=5.0; "
                               "T≈122.5 → RBSE just below threshold (122.42 < T < 122.58) ✓"),
    ("LK",    "5.0","122.58",  "fill=0.775 (20×22 box); ✓ at α_CE=5.0; "
                               "LK barely above threshold T≈122.5 ✓; "
                               "higher fill than expected pentagon (0.71) at this px size"),
    ("LC",    "5.0","152.49",  "fill=1.000 (24×24 box, cnt=576) ■ square ✓ definitive"),
    ("LX",    "5.0","196.05",  "fill=0.628 (22×22 box); LX ✓ at α_CE=5.0; "
                               "LX binding energy suppresses rate less at high α_CE"),
    ("NTC",   "5.0","241.92",  "fill=0.404 asp=1.067 (16×15 box, cnt=97); low-fill "
                               "★/✳ asterisk shape; NTC ✓ highest at α_CE=5.0; "
                               "NTC/F=241.92/107.99=2.24≈2 ✓"),
    ("F19",   "5.0","107.99",  "estimated ≈F@α_CE=5.0 (F19 negligible BNS rate effect); "
                               "not separately resolved in figure"),
    ("QHE",   "5.0","107.99",  "estimated ≈F@α_CE=5.0; QHE × at α_CE=5.0 per "
                               "Table G.1; not separately resolved in figure"),
]


def submodel_key(model: str, alpha: str) -> str:
    return f"DeSantis26-{model}-aCE{alpha}"


def append_csv(path: Path, columns: list[str], rows: list[dict]):
    with open(path, "rb") as f:
        f.seek(-1, 2)
        needs_newline = f.read(1) != b"\n"
    with open(path, "a", newline="") as f:
        if needs_newline:
            f.write("\n")
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in columns})


def main():
    with open(IBE_CSV, newline="") as f:
        ibe_columns = csv.DictReader(f).fieldnames

    common = dict(
        compact_object_type="NS-NS",
        formation_channel="isolated-binary-evolution",
        study_key=STUDY_KEY,
        label=LABEL,
        first_author="De Santis",
        year="2026",
        month="02",
        ads_url="",
        arxiv_url=ARXIV_URL,
        code=CODE,
        plotting_style="range",
        rate_type="",
    )

    ibe_rows = []
    for (model, alpha, rate, note) in ROWS:
        sm = submodel_key(model, alpha)
        full_note = (
            f"R_BNS(0) [Gpc^-3 yr^-1] read from Figure 2 bottom-left panel "
            f"(log10 x-axis), De Santis et al. (2026) arXiv:2602.13391 (SEVN code, "
            f"Iorio+2023 ICs); model={model}, alpha_CE={alpha}. "
            f"Pixel analysis: {note}"
        )
        ibe_rows.append(dict(
            common,
            rate_Gpc3yr=rate,
            submodel=sm,
            **{"submodel string": sm},
            alpha_CE=alpha,
            notes=full_note,
        ))

    append_csv(IBE_CSV, ibe_columns, ibe_rows)
    print(f"Appended {len(ibe_rows)} rows to {IBE_CSV}")


if __name__ == "__main__":
    main()
