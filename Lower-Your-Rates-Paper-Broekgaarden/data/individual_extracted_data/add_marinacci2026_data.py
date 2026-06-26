#!/usr/bin/env python3
from __future__ import annotations
"""
Add Marinacci et al. (2026) (arXiv:2510.06311) z~0 GW progenitor merger rate
densities for BBH, BHNS and BNS, read off from the rightmost (z=0) point of
Fig. 3 (MTNG740 simulation box, sevn-based binary population synthesis).

Values were read off Fig. 3 by pixel-calibrating the log-scaled y-axis
(R [yr^-1 Gpc^-3]) using the labelled 10^3, 10^1 and 10^0 tick positions:
  - BBH  (blue):    ~88.4
  - BHNS (crimson): ~36.2
  - BNS  (gray):    ~155.2
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"

STUDY_KEY = "Marinacci_2025_SEVN"
LABEL     = "Marinacci et al. (2026)"
ARXIV_URL = "https://arxiv.org/abs/2510.06311"
CODE      = "SEVN"

NOTE_TMPL = (
    "{co} merger rate density at z~=0, read off the rightmost point of Fig. 3 "
    "of Marinacci et al. (2026) (MTNG740 simulation box, sevn-based binary "
    "population synthesis applied to MillenniumTNG galaxies)."
)


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
        columns = csv.DictReader(f).fieldnames

    common = dict(
        study_key=STUDY_KEY, label=LABEL, first_author="Marinacci",
        year="2025", month="10", ads_url="", arxiv_url=ARXIV_URL, code=CODE,
        formation_channel="isolated-binary-evolution",
        plotting_style="single_value", rate_type="single",
    )

    rows = [
        dict(common, compact_object_type="BH-BH", rate_Gpc3yr="88.4",
             notes=NOTE_TMPL.format(co="BBH")),
        dict(common, compact_object_type="NS-BH", rate_Gpc3yr="36.2",
             notes=NOTE_TMPL.format(co="BHNS")),
        dict(common, compact_object_type="NS-NS", rate_Gpc3yr="155.2",
             notes=NOTE_TMPL.format(co="BNS")),
    ]
    append_csv(IBE_CSV, columns, rows)
    print(f"Appended {len(rows)} rows to {IBE_CSV}")


if __name__ == "__main__":
    main()
