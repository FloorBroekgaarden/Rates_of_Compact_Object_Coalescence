#!/usr/bin/env python3
from __future__ import annotations
"""
Fix Romagnolo et al. (2023) (arXiv:2211.15800) entries in
isolated-binary-evolution.csv.

The existing 15 rows (BH-BH, NS-BH, NS-NS x 5 R_max models) were mislabeled
as study_key="Riley_2023_StarTrack" / label="Riley et al. (2023)", with rate
values that don't match the published Table 3. This script:

1. Removes those 15 mislabeled rows.
2. Appends 15 correctly labelled rows (study_key="Romagnolo_2023_StarTrack",
   label="Romagnolo et al. (2023)") using the local (z<0.2) merger rate
   densities from Table 3 for Model 1, 2, 3, 4a, 4b.

"submodel string" is set to the R23-* identifiers already used by the
existing parameter-relationship edges for Romagnolo_2023_StarTrack in
isolated-binary-evolution_relationships.csv, so those edges resolve rates
correctly via the (study_key, submodel string) join.
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"

OLD_STUDY_KEY = "Riley_2023_StarTrack"
OLD_ARXIV     = "2211.15800"

STUDY_KEY = "Romagnolo_2023_StarTrack"
LABEL     = "Romagnolo et al. (2023)"
ARXIV_URL = "https://arxiv.org/abs/2211.15800"

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

# Fixed StarTrack parameter columns, shared by all 5 models (only R_max
# differs between them); copied from the previously mislabeled rows.
COMMON = dict(
    first_author="Romagnolo",
    year="2023",
    arxiv_url=ARXIV_URL,
    code="StarTrack",
    plotting_style="range",
    sigma_kick="265",
    sigma_stripped_SN="265",
    alpha_CE="1",
    beta_MT="0.5",
    gamma_AM="specific AM of accretor (Belczynski et al. 2008 / StarTrack)",
    CE_pessimistic="pessimistic",
    CE_prescription="standard",
    lambda_CE="Nanjing",
    RMP="F12 delayed",
    PISN_prescription="Farmer et al. (2019)",
    MT_stability="Belczynski et al. (2008) / StarTrack zeta prescription",
    Eddington_limited="TRUE",
    f_WR="1",
    stellar_tracks="SSE",
)

# (submodel, submodel string, notes, BH-BH, NS-BH, NS-NS) -- Table 3, z<0.2
MODELS = [
    ("Model 1",  "R23-A-Fiducial", "Model 1: Hurley et al. (2000) Rmax (fiducial StarTrack)",
     "68.1", "15.6", "158.9"),
    ("Model 2",  "R23-B-RMAX2",    "Model 2: METISSE-BoOST Rmax prescription",
     "65.8", "14.9", "162.8"),
    ("Model 3",  "R23-C-RMAX3",    "Model 3: METISSE-MESA Rmax prescription",
     "46.6", "19.7", "157.7"),
    ("Model 4a", "R23-D-RMAX4",    "Model 4a: MESA (with MLT++) Rmax prescription",
     "18.7", "9.5",  "100.4"),
    ("Model 4b", "R23-E-RMAX4B",   "Model 4b: MESA (without MLT++) Rmax prescription",
     "65.6", "22.9", "160.8"),
]

CO_RATE_INDEX = {"BH-BH": 3, "NS-BH": 4, "NS-NS": 5}


def build_rows():
    rows = []
    for co_type, idx in CO_RATE_INDEX.items():
        for submodel, sub_string, notes, *rates in MODELS:
            row = {c: "" for c in IBE_COLUMNS}
            row.update(COMMON)
            row.update({
                "compact_object_type": co_type,
                "formation_channel": "isolated-binary-evolution",
                "study_key": STUDY_KEY,
                "label": LABEL,
                "rate_Gpc3yr": rates[idx - 3],
                "submodel": submodel,
                "submodel string": sub_string,
                "notes": notes,
            })
            rows.append(row)
    return rows


def main():
    with open(IBE_CSV, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        kept = []
        removed = 0
        for row in reader:
            d = dict(zip(header, row))
            if d["study_key"] == OLD_STUDY_KEY and OLD_ARXIV in d["arxiv_url"]:
                removed += 1
                continue
            kept.append(row)

    with open(IBE_CSV, "w", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(kept)
        dict_writer = csv.DictWriter(f, fieldnames=header, lineterminator="\n")
        for row in build_rows():
            dict_writer.writerow(row)

    print(f"Removed {removed} rows with study_key={OLD_STUDY_KEY!r} (arxiv {OLD_ARXIV})")
    print(f"Appended {len(build_rows())} rows with study_key={STUDY_KEY!r}")


if __name__ == "__main__":
    main()
