#!/usr/bin/env python3
from __future__ import annotations
"""
Add the remaining alpha_CE = 0.1 -> 1 -> 10 chains for Boco et al. (2026).

Figures 6 (alpha_CE=1) and 7 (alpha_CE=0.1, top; alpha_CE=10, bottom) of
Boco et al. (2026) cover the SAME 3x3x2=18-cell grid of
(Z_O/H,0, aMZR, nabla_FMR,0), each with all three alpha_CE values. The
initial Boco_2026_SEVN relationship edges only included ONE such chain (at
the global SFRD-fiducial point Z_O/H,0=9.0, aMZR=0.15, nabla_FMR,0=0.20),
giving a single line in the "CE efficiency" panel of
parameter_impact_rate.ipynb. This script adds the remaining 17 chains
(2 edges each = 34 edges), so all 18 alpha_CE variations show up as
separate lines.

All required (Z_O/H,0, aMZR, nabla_FMR,0, alpha_CE) submodels already exist
in isolated-binary-evolution.csv (added from Figs. 6-8); this script only
adds relationship edges, looking up rates from the existing rows.
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"
REL_CSV  = DATA_DIR / "isolated-binary-evolution_relationships.csv"

STUDY_KEY  = "Boco_2026_SEVN"
LABEL      = "Boco et al. (2026)"
COLOR_CODE = "25"

ZOH_VALUES  = ["8.8", "9.0", "9.2"]
AMZR_VALUES = ["0.15", "0.30", "0.60"]
FMR0_VALUES = ["0.20", "0.30"]

FID_COMBO = ("9.0", "0.15", "0.20")  # already has 2 edges


def submodel_string(zoh, amzr, fmr0, ace) -> str:
    return f"Boco26-Z{zoh}-aMZR{amzr}-FMR{fmr0}-aCE{ace}"


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
        ibe_rows = list(csv.DictReader(f))
    rate = {r["submodel"]: r["rate_Gpc3yr"]
            for r in ibe_rows if r["study_key"] == STUDY_KEY}

    with open(REL_CSV, newline="") as f:
        rel_columns = csv.DictReader(f).fieldnames

    edges = []
    for zoh in ZOH_VALUES:
        for amzr in AMZR_VALUES:
            for fmr0 in FMR0_VALUES:
                combo = (zoh, amzr, fmr0)
                if combo == FID_COMBO:
                    continue  # already has its 2 edges

                sm01 = submodel_string(zoh, amzr, fmr0, "0.1")
                sm1  = submodel_string(zoh, amzr, fmr0, "1")
                sm10 = submodel_string(zoh, amzr, fmr0, "10")
                r01, r1, r10 = rate[sm01], rate[sm1], rate[sm10]

                edges.append(dict(
                    study_key=STUDY_KEY, label=LABEL, code="SEVN",
                    from_submodel=sm01, to_submodel=sm1,
                    parameter_family="CE efficiency (alpha)", parameter="alpha_CE",
                    travel_label="alpha_CE=1",
                    from_value="alpha_CE=0.1", to_value="alpha_CE=1",
                    from_rate_Gpc3yr=r01, to_rate_Gpc3yr=r1,
                    study_color_code=COLOR_CODE,
                ))
                edges.append(dict(
                    study_key=STUDY_KEY, label=LABEL, code="SEVN",
                    from_submodel=sm1, to_submodel=sm10,
                    parameter_family="CE efficiency (alpha)", parameter="alpha_CE",
                    travel_label="alpha_CE=10",
                    from_value="alpha_CE=1", to_value="alpha_CE=10",
                    from_rate_Gpc3yr=r1, to_rate_Gpc3yr=r10,
                    study_color_code=COLOR_CODE,
                ))

    append_csv(REL_CSV, rel_columns, edges)
    print(f"Appended {len(edges)} alpha_CE edges to {REL_CSV}")


if __name__ == "__main__":
    main()
