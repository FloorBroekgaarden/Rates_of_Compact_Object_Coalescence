#!/usr/bin/env python3
from __future__ import annotations
"""
Add Stevenson & Clarke (2022) BH-BH merger-rate range to the tidy dataset.

From their Figure 8, the combined isolated-binary (classical isolated binary
evolution + CHE) BH-BH merger rate is quoted as 10-400 Gpc^-3 yr^-1. Since the
authors note CHE can contribute up to 70% of this rate:
  - classical isolated binary evolution: lower = 0.3 x 10 = 3, upper = 400
  - CHE channel: lower = 0.7 x 10 = 7, upper = 400 (kept conservative)

Appends 2 rows to isolated-binary-evolution.csv and 2 rows to CHE.csv.
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"
CHE_CSV  = DATA_DIR / "CHE.csv"

STUDY_KEY = "StevensonClarke_2022"
LABEL     = "Stevenson and Clarke (2022)"

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

CHE_COLUMNS = [
    "compact_object_type", "formation_channel", "study_key", "label",
    "first_author", "year", "month", "ads_url", "arxiv_url", "code",
    "plotting_style", "rate_Gpc3yr", "rate_type", "submodel", "notes",
]

COMMON = dict(
    compact_object_type="BH-BH",
    study_key=STUDY_KEY,
    label=LABEL,
    first_author=LABEL,
    year="2022",
    plotting_style="range",
)

IBE_ROWS = [
    dict(COMMON,
         formation_channel="isolated-binary-evolution",
         rate_Gpc3yr="3", rate_type="lower",
         notes=("lower limit; from Fig. 8 combined isolated+CHE BH-BH range of "
                "10-400, reduced to 0.3x10 since CHE can contribute up to 70% "
                "of the combined rate")),
    dict(COMMON,
         formation_channel="isolated-binary-evolution",
         rate_Gpc3yr="400", rate_type="upper",
         notes=("upper limit; from Fig. 8 combined isolated+CHE BH-BH range of "
                "10-400, unchanged (kept the same upper limit for both the "
                "isolated and CHE channels)")),
]

CHE_ROWS = [
    dict(COMMON,
         formation_channel="CHE",
         rate_Gpc3yr="7", rate_type="lower",
         notes=("lower limit; from Fig. 8 combined isolated+CHE BH-BH range of "
                "10-400, taken as 0.7x10 since CHE can contribute up to 70% "
                "of the combined rate")),
    dict(COMMON,
         formation_channel="CHE",
         rate_Gpc3yr="400", rate_type="upper",
         notes=("upper limit; from Fig. 8 combined isolated+CHE BH-BH range of "
                "10-400, unchanged (kept the same upper limit for both the "
                "isolated and CHE channels)")),
]


def append_csv(path: Path, columns: list[str], rows: list[dict]):
    full_rows = [{c: row.get(c, "") for c in columns} for row in rows]
    with open(path, "rb") as f:
        f.seek(-1, 2)
        needs_newline = f.read(1) != b"\n"
    with open(path, "a", newline="") as f:
        if needs_newline:
            f.write("\n")
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        for row in full_rows:
            writer.writerow(row)


if __name__ == "__main__":
    append_csv(IBE_CSV, IBE_COLUMNS, IBE_ROWS)
    append_csv(CHE_CSV, CHE_COLUMNS, CHE_ROWS)
    print(f"Appended {len(IBE_ROWS)} rows to {IBE_CSV}")
    print(f"Appended {len(CHE_ROWS)} rows to {CHE_CSV}")
