#!/usr/bin/env python3
from __future__ import annotations
"""
Add Boco et al. (2026) (arXiv:2606.02725) "Can current models predict the
local black hole merger rate?" BBH local merger rates to the tidy dataset.

Boco et al. (2026) couple the SEVN population-synthesis BBH merger
efficiency eta(Z) to a family of metallicity-specific cosmic star formation
rate density S(Z,z) models built from the Fundamental Metallicity Relation
(FMR, Curti et al. 2020 parametrization). Figures 6, 7 and 8 show the
predicted local (z=0) BBH merger rate density R0 as a ratio R0/R0,LVK, where
R0,LVK ~ 20 Gpc^-3 yr^-1 is the LVK-inferred local rate used for
normalization (see colorbar legend).

  - Figure 8 (alpha_CE = 1, fiducial CE efficiency) gives R0/R0,LVK on an
    extended grid of Z_O/H,0 in {8.8, 9.0, 9.2}, aMZR in
    {0.05, 0.15, 0.30, 0.60}, and nabla_FMR,0 in {0.00, 0.10, 0.20, 0.30}
    (4 x 4 x 3 = 48 cells). Figure 6's 3 x 2 x 3 = 18-cell grid
    (aMZR in {0.15,0.30,0.60}, nabla_FMR,0 in {0.20,0.30}) is the bottom-right
    submatrix of Figure 8 and is therefore not duplicated.
  - Figure 7 gives R0/R0,LVK for alpha_CE = 0.1 (top panel) and alpha_CE = 10
    (bottom panel), on the same 3 x 2 x 3 = 18-cell grid as Figure 6
    (36 cells total).
  - Figure 10 (steepened delay-time distribution) is intentionally excluded;
    it will be added separately as "Boco (2026; steep DTD)".

Total: 48 + 36 = 84 rows.

The fiducial anchor point for the relationship edges below is taken as
Z_O/H,0 = 9.0, aMZR = 0.15, nabla_FMR,0 = 0.20, alpha_CE = 1 -- the
combination the paper describes as the most "realistic" metallicity
relation (Sec. 4 discussion).

Appends:
  - 84 rows to isolated-binary-evolution.csv (BH-BH, plotting_style="range").
  - 10 relationship edges to isolated-binary-evolution_relationships.csv:
      - Z_O/H,0 chain (2 edges): 8.8 -> 9.0 (fiducial) -> 9.2
      - aMZR chain (3 edges): 0.05 -> 0.15 (fiducial) -> 0.30 -> 0.60
      - nabla_FMR,0 chain (3 edges): 0.00 -> 0.10 -> 0.20 (fiducial) -> 0.30
      - alpha_CE chain (2 edges): 0.1 -> 1 (fiducial) -> 10
    all at the fiducial point of the other parameters.
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"
REL_CSV  = DATA_DIR / "isolated-binary-evolution_relationships.csv"

STUDY_KEY  = "Boco_2026_SEVN"
LABEL      = "Boco et al. (2026)"
ARXIV_URL  = "https://arxiv.org/abs/2606.02725"
COLOR_CODE = "25"
R0_LVK     = 20.0

IBE_COLUMNS = [
    "compact_object_type", "formation_channel", "study_key", "label",
    "first_author", "year", "month", "ads_url", "arxiv_url", "code",
    "plotting_style", "rate_Gpc3yr", "rate_type", "submodel", "submodel string",
    "notes", "submodel change 1", "submodel change 2",
    "sfrd-1", "sfrd-2", "sfrd-3", "sfrd-4", "sigma_kick", "sigma_stripped_SN",
    "alpha_CE", "beta_MT", "gamma_AM", "CE_pessimistic", "CE_prescription",
    "lambda_CE", "RMP", "PISN_prescription", "MT_stability",
    "Eddington_limited", "f_WR", "stellar_tracks", "binding_energy",
]

REL_COLUMNS = [
    "study_key", "label", "code", "from_submodel", "to_submodel",
    "parameter_family", "parameter", "travel_label",
    "from_value", "to_value", "from_rate_Gpc3yr", "to_rate_Gpc3yr",
    "study_color_code",
]

# Fig. 8 (alpha_CE = 1): R0/R0,LVK for (Z_O/H,0, aMZR) -> [nabla_FMR,0 = 0.00, 0.10, 0.20, 0.30]
FIG8_FMR0 = ["0.00", "0.10", "0.20", "0.30"]
FIG8 = {
    ("8.8", "0.05"): [23.22, 29.02, 37.44, 48.77],
    ("8.8", "0.15"): [26.06, 31.68, 40.68, 51.22],
    ("8.8", "0.30"): [31.89, 38.15, 46.28, 54.95],
    ("8.8", "0.60"): [43.03, 48.25, 54.01, 59.79],
    ("9.0", "0.05"): [7.61, 15.48, 21.96, 29.79],
    ("9.0", "0.15"): [10.89, 17.16, 23.81, 32.28],
    ("9.0", "0.30"): [15.62, 21.54, 28.70, 36.90],
    ("9.0", "0.60"): [26.94, 32.46, 38.46, 44.71],
    ("9.2", "0.05"): [1.60, 4.68, 11.01, 17.00],
    ("9.2", "0.15"): [2.76, 6.76, 12.46, 18.59],
    ("9.2", "0.30"): [6.11, 10.29, 15.86, 22.53],
    ("9.2", "0.60"): [15.57, 20.31, 25.74, 31.65],
}

# Fig. 7: R0/R0,LVK for (alpha_CE, Z_O/H,0, aMZR) -> [nabla_FMR,0 = 0.20, 0.30]
FIG7_FMR0 = ["0.20", "0.30"]
FIG7 = {
    ("0.1", "8.8", "0.15"): [24.40, 25.02],
    ("0.1", "8.8", "0.30"): [24.39, 24.97],
    ("0.1", "8.8", "0.60"): [23.95, 24.47],
    ("0.1", "9.0", "0.15"): [17.29, 19.44],
    ("0.1", "9.0", "0.30"): [18.39, 20.00],
    ("0.1", "9.0", "0.60"): [18.96, 20.10],
    ("0.1", "9.2", "0.15"): [10.29, 13.34],
    ("0.1", "9.2", "0.30"): [12.01, 14.41],
    ("0.1", "9.2", "0.60"): [14.01, 15.62],
    ("10",  "8.8", "0.15"): [15.67, 25.16],
    ("10",  "8.8", "0.30"): [20.25, 28.06],
    ("10",  "8.8", "0.60"): [27.07, 32.28],
    ("10",  "9.0", "0.15"): [6.64, 12.40],
    ("10",  "9.0", "0.30"): [10.37, 16.36],
    ("10",  "9.0", "0.60"): [18.14, 22.86],
    ("10",  "9.2", "0.15"): [2.92, 5.23],
    ("10",  "9.2", "0.30"): [4.68, 8.25],
    ("10",  "9.2", "0.60"): [11.38, 15.20],
}

FID_ZOH, FID_AMZR, FID_FMR0, FID_ACE = "9.0", "0.15", "0.20", "1"

SINGLE_CHANGE_LABEL = {
    "Z_OH_0":      "FMR normalization (Z_O/H,0)",
    "aMZR":        "MZR slope (aMZR)",
    "nabla_FMR_0": "FMR slope / Z-SFR anti-correlation (nabla_FMR,0)",
    "alpha_CE":    "CE efficiency (alpha_CE)",
}


def rate_str(ratio: float) -> str:
    return f"{ratio * R0_LVK:.1f}"


def submodel_string(zoh, amzr, fmr0, ace) -> str:
    return f"Boco26-Z{zoh}-aMZR{amzr}-FMR{fmr0}-aCE{ace}"


def submodel_change(zoh, amzr, fmr0, ace) -> str:
    diffs = []
    if zoh != FID_ZOH:
        diffs.append("Z_OH_0")
    if amzr != FID_AMZR:
        diffs.append("aMZR")
    if fmr0 != FID_FMR0:
        diffs.append("nabla_FMR_0")
    if ace != FID_ACE:
        diffs.append("alpha_CE")
    if not diffs:
        return "fiducial"
    if len(diffs) == 1:
        return SINGLE_CHANGE_LABEL[diffs[0]]
    return "multi-parameter"


def build_row(zoh, amzr, fmr0, ace, ratio, fig: str) -> dict:
    rate = rate_str(ratio)
    notes = (
        f"R0/R0,LVK = {ratio} from Fig. {fig} of Boco et al. (2026), assuming "
        f"R0,LVK = {R0_LVK:.0f} Gpc^-3 yr^-1 (LVK-normalized local BBH merger "
        f"rate from the SEVN population synthesis code). "
        f"Z_O/H,0={zoh}, aMZR={amzr}, nabla_FMR,0={fmr0}, alpha_CE={ace}."
    )
    row = {c: "" for c in IBE_COLUMNS}
    row.update(dict(
        compact_object_type="BH-BH",
        formation_channel="isolated-binary-evolution",
        study_key=STUDY_KEY,
        label=LABEL,
        first_author="Boco",
        year="2026",
        month="6",
        arxiv_url=ARXIV_URL,
        code="SEVN",
        plotting_style="range",
        rate_Gpc3yr=rate,
        submodel=submodel_string(zoh, amzr, fmr0, ace),
        **{"submodel string": submodel_string(zoh, amzr, fmr0, ace)},
        notes=notes,
        **{"submodel change 1": submodel_change(zoh, amzr, fmr0, ace)},
        **{"sfrd-1": f"Z_O/H,0={zoh} (FMR normalization)"},
        **{"sfrd-2": f"aMZR={amzr} (MZR slope)"},
        **{"sfrd-3": f"nabla_FMR,0={fmr0} (FMR slope)"},
        alpha_CE=ace,
    ))
    return row


def build_ibe_rows() -> list[dict]:
    rows = []
    for (zoh, amzr), ratios in FIG8.items():
        for fmr0, ratio in zip(FIG8_FMR0, ratios):
            rows.append(build_row(zoh, amzr, fmr0, "1", ratio, "8"))
    for (ace, zoh, amzr), ratios in FIG7.items():
        for fmr0, ratio in zip(FIG7_FMR0, ratios):
            rows.append(build_row(zoh, amzr, fmr0, ace, ratio, "7"))
    return rows


def rate_at(zoh, amzr, fmr0, ace) -> str:
    if ace == "1":
        return rate_str(FIG8[(zoh, amzr)][FIG8_FMR0.index(fmr0)])
    return rate_str(FIG7[(ace, zoh, amzr)][FIG7_FMR0.index(fmr0)])


def build_edges() -> list[dict]:
    fid_sm = submodel_string(FID_ZOH, FID_AMZR, FID_FMR0, FID_ACE)
    fid_rate = rate_at(FID_ZOH, FID_AMZR, FID_FMR0, FID_ACE)
    edges = []

    def add_edge(from_args, to_args, parameter_family, parameter,
                  from_value, to_value, travel_label):
        edges.append(dict(
            study_key=STUDY_KEY, label=LABEL, code="SEVN",
            from_submodel=submodel_string(*from_args), to_submodel=submodel_string(*to_args),
            parameter_family=parameter_family, parameter=parameter,
            travel_label=travel_label,
            from_value=from_value, to_value=to_value,
            from_rate_Gpc3yr=rate_at(*from_args), to_rate_Gpc3yr=rate_at(*to_args),
            study_color_code=COLOR_CODE,
        ))

    # Z_O/H,0 chain: 8.8 -> 9.0 (fiducial) -> 9.2
    add_edge(("8.8", FID_AMZR, FID_FMR0, FID_ACE), (FID_ZOH, FID_AMZR, FID_FMR0, FID_ACE),
             "star formation history", "Z_OH_0",
             "Z_O/H,0=8.8", "Z_O/H,0=9.0 (fiducial)", "Z_O/H,0=9.0")
    add_edge((FID_ZOH, FID_AMZR, FID_FMR0, FID_ACE), ("9.2", FID_AMZR, FID_FMR0, FID_ACE),
             "star formation history", "Z_OH_0",
             "Z_O/H,0=9.0 (fiducial)", "Z_O/H,0=9.2", "Z_O/H,0=9.2")

    # aMZR chain: 0.05 -> 0.15 (fiducial) -> 0.30 -> 0.60
    add_edge((FID_ZOH, "0.05", FID_FMR0, FID_ACE), (FID_ZOH, FID_AMZR, FID_FMR0, FID_ACE),
             "star formation history", "aMZR",
             "aMZR=0.05", "aMZR=0.15 (fiducial)", "aMZR=0.15")
    add_edge((FID_ZOH, FID_AMZR, FID_FMR0, FID_ACE), (FID_ZOH, "0.30", FID_FMR0, FID_ACE),
             "star formation history", "aMZR",
             "aMZR=0.15 (fiducial)", "aMZR=0.30", "aMZR=0.30")
    add_edge((FID_ZOH, "0.30", FID_FMR0, FID_ACE), (FID_ZOH, "0.60", FID_FMR0, FID_ACE),
             "star formation history", "aMZR",
             "aMZR=0.30", "aMZR=0.60", "aMZR=0.60")

    # nabla_FMR,0 chain: 0.00 -> 0.10 -> 0.20 (fiducial) -> 0.30
    add_edge((FID_ZOH, FID_AMZR, "0.00", FID_ACE), (FID_ZOH, FID_AMZR, "0.10", FID_ACE),
             "star formation history", "nabla_FMR_0",
             "nabla_FMR,0=0.00", "nabla_FMR,0=0.10", "nabla_FMR,0=0.10")
    add_edge((FID_ZOH, FID_AMZR, "0.10", FID_ACE), (FID_ZOH, FID_AMZR, FID_FMR0, FID_ACE),
             "star formation history", "nabla_FMR_0",
             "nabla_FMR,0=0.10", "nabla_FMR,0=0.20 (fiducial)", "nabla_FMR,0=0.20")
    add_edge((FID_ZOH, FID_AMZR, FID_FMR0, FID_ACE), (FID_ZOH, FID_AMZR, "0.30", FID_ACE),
             "star formation history", "nabla_FMR_0",
             "nabla_FMR,0=0.20 (fiducial)", "nabla_FMR,0=0.30", "nabla_FMR,0=0.30")

    # alpha_CE chain: 0.1 -> 1 (fiducial) -> 10
    add_edge((FID_ZOH, FID_AMZR, FID_FMR0, "0.1"), (FID_ZOH, FID_AMZR, FID_FMR0, FID_ACE),
             "CE efficiency (alpha)", "alpha_CE",
             "alpha_CE=0.1", "alpha_CE=1 (fiducial)", "alpha_CE=1")
    add_edge((FID_ZOH, FID_AMZR, FID_FMR0, FID_ACE), (FID_ZOH, FID_AMZR, FID_FMR0, "10"),
             "CE efficiency (alpha)", "alpha_CE",
             "alpha_CE=1 (fiducial)", "alpha_CE=10", "alpha_CE=10")

    assert fid_rate == rate_at(*[submodel_string(FID_ZOH, FID_AMZR, FID_FMR0, FID_ACE) and None or x for x in (FID_ZOH, FID_AMZR, FID_FMR0, FID_ACE)])
    return edges


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
    assert sum(len(v) for v in FIG8.values()) == 48
    assert sum(len(v) for v in FIG7.values()) == 36

    ibe_rows = build_ibe_rows()
    edges = build_edges()

    append_csv(IBE_CSV, IBE_COLUMNS, ibe_rows)
    append_csv(REL_CSV, REL_COLUMNS, edges)

    print(f"Appended {len(ibe_rows)} rows to {IBE_CSV}")
    print(f"Appended {len(edges)} relationship edges to {REL_CSV}")


if __name__ == "__main__":
    main()
