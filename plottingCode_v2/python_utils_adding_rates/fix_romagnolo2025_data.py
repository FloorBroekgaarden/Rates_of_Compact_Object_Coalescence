#!/usr/bin/env python3
from __future__ import annotations
"""
Fix the mislabeled "Riley_2025_StarTrack" entries.

The 18 rows in isolated-binary-evolution.csv tagged study_key=
"Riley_2025_StarTrack" / label="Riley et al. (2025)" (6 StarTrack submodels
R25-A..E x BH-BH/NS-BH/NS-NS) actually belong to Romagnolo et al. (2025)
(arXiv:2410.17315), and their rate values were wrong. A separate
"Romagnolo_2025_StarTrack" block already exists in
isolated-binary-evolution_relationships.csv (9 parameter-change edges among
the same 6 submodels) but with empty from/to rate columns.

This script:
  1. Re-labels the 18 IBE rows: study_key -> Romagnolo_2025_StarTrack,
     label -> "Romagnolo et al. (2025)", first_author -> "Romagnolo", and
     overwrites rate_Gpc3yr with the correct local (z<0.2) merger rate
     densities from Table 2 of Romagnolo et al. (2025).
  2. Fills in the from_rate_Gpc3yr / to_rate_Gpc3yr columns of the 9 existing
     Romagnolo_2025_StarTrack relationship edges using the corrected BH-BH
     rates (this relationships file drives the BH-BH parameter-impact plot).

Table 2 of Romagnolo et al. (2025) [Gpc^-3 yr^-1]:
  Model                    BH-BH   BH-NS   NS-NS
  M0                        65.9    13.2   112.8   -> R25-A-Fiducial
  M0RMAX                    63.6    11.9   114.1   -> R25-B-RMAX
  M_aML1.5                  12.3    12.4     5.1   -> R25-C-Conv_ML1.5
  M_aML1.5RMAX               3.0    12.6     5.1   -> R25-D-Conv_ML1.5_RMAX
  M_aML1.82_MLTpp          104.4    12.8    17.2   -> R25-E-Conv_ML1.82_MLTpp
  M_aML1.82_MLTppRMAX       38.9    12.5    15.7   -> R25-E-Conv_ML1.82_MLTpp_RMAX
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"
REL_CSV  = DATA_DIR / "isolated-binary-evolution_relationships.csv"

OLD_STUDY_KEY = "Riley_2025_StarTrack"
NEW_STUDY_KEY = "Romagnolo_2025_StarTrack"
NEW_LABEL     = "Romagnolo et al. (2025)"
NEW_AUTHOR    = "Romagnolo"

TABLE2_NOTE = "Local (z<0.2) merger rate density from Table 2 of Romagnolo et al. (2025)."

# submodel -> {compact_object_type: rate}
TABLE2 = {
    "R25-A-Fiducial":                {"BH-BH": "65.9",  "NS-BH": "13.2", "NS-NS": "112.8"},
    "R25-B-RMAX":                    {"BH-BH": "63.6",  "NS-BH": "11.9", "NS-NS": "114.1"},
    "R25-C-Conv_ML1.5":              {"BH-BH": "12.3",  "NS-BH": "12.4", "NS-NS": "5.1"},
    "R25-D-Conv_ML1.5_RMAX":         {"BH-BH": "3.0",   "NS-BH": "12.6", "NS-NS": "5.1"},
    "R25-E-Conv_ML1.82_MLTpp":       {"BH-BH": "104.4", "NS-BH": "12.8", "NS-NS": "17.2"},
    "R25-E-Conv_ML1.82_MLTpp_RMAX":  {"BH-BH": "38.9",  "NS-BH": "12.5", "NS-NS": "15.7"},
}

# BH-BH rates only, used to fill in the relationship edges
BHBH_RATE = {sm: vals["BH-BH"] for sm, vals in TABLE2.items()}


def fix_ibe():
    with open(IBE_CSV, newline="") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        rows = list(reader)

    n_fixed = 0
    for row in rows:
        if row["study_key"] != OLD_STUDY_KEY:
            continue
        submodel = row["submodel"]
        cot = row["compact_object_type"]
        row["study_key"] = NEW_STUDY_KEY
        row["label"] = NEW_LABEL
        row["first_author"] = NEW_AUTHOR
        row["rate_Gpc3yr"] = TABLE2[submodel][cot]
        row["notes"] = TABLE2_NOTE
        n_fixed += 1

    with open(IBE_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Fixed {n_fixed} rows in {IBE_CSV}")


def fix_relationships():
    with open(REL_CSV, newline="") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        rows = list(reader)

    n_fixed = 0
    for row in rows:
        if row["study_key"] != NEW_STUDY_KEY:
            continue
        row["from_rate_Gpc3yr"] = BHBH_RATE[row["from_submodel"]]
        row["to_rate_Gpc3yr"] = BHBH_RATE[row["to_submodel"]]
        n_fixed += 1

    with open(REL_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Fixed {n_fixed} relationship edges in {REL_CSV}")


def main():
    assert len(TABLE2) == 6
    fix_ibe()
    fix_relationships()


if __name__ == "__main__":
    main()
