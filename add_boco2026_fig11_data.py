#!/usr/bin/env python3
from __future__ import annotations
"""
Add Boco et al. (2026) (arXiv:2606.02725) Figure 11 BBH local merger rates
to the tidy dataset, as a new "metallicity calibration" parameter axis.

Figure 11 is "Same as Figure 6, but using oxygen abundances": the same
alpha_CE = 1 grid of Z_O/H,0 in {8.8, 9.0, 9.2}, aMZR in {0.15, 0.30, 0.60},
nabla_FMR,0 in {0.20, 0.30} (3 x 3 x 2 = 18 cells) as Figure 6/8, but with the
metallicity set directly from the oxygen abundance, Z = Z_sun * 10^[O/H],
instead of the iron-abundance calibration Z = Z_sun * 10^[Fe/H] (via the
Chruslinska et al. 2025 [O/Fe] correction) used for Figures 6-8.

This script:
  1. Fills in sfrd-4 = "metallicity_calibration=iron (...)" for the 84
     existing Boco_2026_SEVN rows (Figs 6-8), making the new axis explicit
     on both sides.
  2. Appends 18 new BH-BH rows (Fig. 11, oxygen-abundance calibration),
     submodel = "<Fig6/8 submodel>-ZcalO".
  3. Appends 1 relationship edge: iron-calibration fiducial
     (Z_O/H,0=9.0, aMZR=0.15, nabla_FMR,0=0.20, alpha_CE=1) ->
     oxygen-calibration counterpart, parameter="metallicity_calibration".

Figure 10 (steepened delay-time distribution) remains excluded.
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

IRON_CAL_DESC   = ("metallicity_calibration=iron (Z=Z_sun*10^[Fe/H]; "
                   "[Fe/H]=[O/H]-[O/Fe] via the Chruslinska et al. 2025 "
                   "O/Fe-sSFR relation)")
OXYGEN_CAL_DESC = ("metallicity_calibration=oxygen (Z=Z_sun*10^[O/H], "
                   "no [O/Fe] correction)")

# Fig. 11 (alpha_CE = 1, oxygen-abundance calibration):
# R0/R0,LVK for (Z_O/H,0, aMZR) -> [nabla_FMR,0 = 0.20, 0.30]
FIG11_FMR0 = ["0.20", "0.30"]
FIG11 = {
    ("8.8", "0.15"): [14.13, 22.13],
    ("8.8", "0.30"): [19.03, 26.43],
    ("8.8", "0.60"): [29.81, 36.20],
    ("9.0", "0.15"): [3.88, 8.99],
    ("9.0", "0.30"): [7.87, 12.97],
    ("9.0", "0.60"): [18.08, 23.34],
    ("9.2", "0.15"): [0.65, 2.38],
    ("9.2", "0.30"): [2.54, 5.30],
    ("9.2", "0.60"): [10.30, 14.15],
}

FID_ZOH, FID_AMZR, FID_FMR0, FID_ACE = "9.0", "0.15", "0.20", "1"


def rate_str(ratio: float) -> str:
    return f"{ratio * R0_LVK:.1f}"


def submodel_string(zoh, amzr, fmr0, ace) -> str:
    return f"Boco26-Z{zoh}-aMZR{amzr}-FMR{fmr0}-aCE{ace}"


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def write_csv(path: Path, columns: list[str], rows: list[dict]):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in columns})


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


def build_fig11_rows(template: dict, columns: list[str]) -> list[dict]:
    rows = []
    for (zoh, amzr), ratios in FIG11.items():
        for fmr0, ratio in zip(FIG11_FMR0, ratios):
            rate = rate_str(ratio)
            base_sm = submodel_string(zoh, amzr, fmr0, "1")
            sm = base_sm + "-ZcalO"
            is_fid_point = (zoh, amzr, fmr0) == (FID_ZOH, FID_AMZR, FID_FMR0)
            change = ("metallicity calibration (Fe vs O abundance)"
                      if is_fid_point else "multi-parameter")
            notes = (
                f"R0/R0,LVK = {ratio} from Fig. 11 of Boco et al. (2026), "
                f"assuming R0,LVK = {R0_LVK:.0f} Gpc^-3 yr^-1. Same grid as "
                f"Fig. 6 (Z_O/H,0={zoh}, aMZR={amzr}, nabla_FMR,0={fmr0}, "
                f"alpha_CE=1) but computed with the {OXYGEN_CAL_DESC.split(' (')[0]} "
                f"instead of the iron-abundance calibration used for Figs. 6-8."
            )
            row = dict(template)
            row.update({
                "rate_Gpc3yr": rate,
                "submodel": sm,
                "submodel string": sm,
                "notes": notes,
                "submodel change 1": change,
                "submodel change 2": "",
                "sfrd-1": f"Z_O/H,0={zoh} (FMR normalization)",
                "sfrd-2": f"aMZR={amzr} (MZR slope)",
                "sfrd-3": f"nabla_FMR,0={fmr0} (FMR slope)",
                "sfrd-4": OXYGEN_CAL_DESC,
                "alpha_CE": "1",
            })
            rows.append({c: row.get(c, "") for c in columns})
    return rows


def build_edge() -> dict:
    fid_sm = submodel_string(FID_ZOH, FID_AMZR, FID_FMR0, FID_ACE)

    # iron fiducial rate: Fig. 8 value at (9.0, 0.15, 0.20, 1) = 23.81 -> 476.2
    iron_rate = "476.2"
    oxygen_ratio = FIG11[(FID_ZOH, FID_AMZR)][FIG11_FMR0.index(FID_FMR0)]
    oxygen_rate = rate_str(oxygen_ratio)
    oxygen_sm = fid_sm + "-ZcalO"

    return dict(
        study_key=STUDY_KEY, label=LABEL, code="SEVN",
        from_submodel=fid_sm, to_submodel=oxygen_sm,
        parameter_family="star formation history", parameter="metallicity_calibration",
        travel_label="oxygen abundance (no [O/Fe] correction)",
        from_value="iron abundance (fiducial)", to_value="oxygen abundance",
        from_rate_Gpc3yr=iron_rate, to_rate_Gpc3yr=oxygen_rate,
        study_color_code=COLOR_CODE,
    )


def main():
    assert sum(len(v) for v in FIG11.values()) == 18

    ibe_columns, ibe_rows = read_csv(IBE_CSV)
    boco_rows = [r for r in ibe_rows if r["study_key"] == STUDY_KEY]
    assert len(boco_rows) == 84

    # 1. Fill in sfrd-4 for existing Figs 6-8 rows (iron calibration).
    for r in boco_rows:
        if r["sfrd-4"] == "":
            r["sfrd-4"] = IRON_CAL_DESC

    # 2. Build the 18 new Fig. 11 (oxygen calibration) rows.
    template = boco_rows[0]
    fig11_rows = build_fig11_rows(template, ibe_columns)

    write_csv(IBE_CSV, ibe_columns, ibe_rows + fig11_rows)

    # 3. Append the relationship edge.
    rel_columns, rel_rows = read_csv(REL_CSV)
    edge = build_edge()
    append_csv(REL_CSV, rel_columns, [edge])

    print(f"Updated sfrd-4 for {len(boco_rows)} existing Boco rows")
    print(f"Appended {len(fig11_rows)} new Fig. 11 rows to {IBE_CSV}")
    print(f"Appended 1 relationship edge to {REL_CSV}")


if __name__ == "__main__":
    main()
