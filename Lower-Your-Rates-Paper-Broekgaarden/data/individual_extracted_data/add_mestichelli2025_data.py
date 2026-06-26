#!/usr/bin/env python3
from __future__ import annotations
"""
Add Mestichelli et al. (2025) (arXiv:2506.13870) BHNS and BNS local merger
rate densities (R(z=0)) from Tables 3 and 5.

Pop. II (isolated binary evolution, fiducial model "kro1"):
  - BHNS: R(z=0) = 0.2 Gpc^-3 yr^-1            (Table 3)
  - BNS:  R(z=0) = 2.2e-3 Gpc^-3 yr^-1          (Table 5)
  -> appended to isolated-binary-evolution.csv

Pop. III (appended to population-III.csv, 15-column legacy schema):
  - BHNS: R(z=0) = 3.5e-2 Gpc^-3 yr^-1, model "lar1"
          (model producing the largest BHNS MRD; NOT the Pop. III
          fiducial model, which is "log1")                  (Table 3)
  - BNS:  R(z=0) = 1.4e-4 Gpc^-3 yr^-1, model "kro1"
          (model producing the highest BNS MRD for Pop. III stars;
          NOT the Pop. III fiducial model, which is "log1")  (Table 5)

Only the z=0 column is used (peak-redshift columns excluded per request).
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"
POP3_CSV = DATA_DIR / "population-III.csv"

STUDY_KEY = "Mestichelli_2025_SEVN"
LABEL     = "Mestichelli et al. (2025)"
ARXIV_URL = "https://arxiv.org/abs/2506.13870"
CODE      = "SEVN"


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
    # --- Pop. II rows -> isolated-binary-evolution.csv -----------------
    with open(IBE_CSV, newline="") as f:
        ibe_columns = csv.DictReader(f).fieldnames

    common = dict(
        study_key=STUDY_KEY, label=LABEL, first_author="Mestichelli",
        year="2025", month="6", ads_url="", arxiv_url=ARXIV_URL, code=CODE,
        formation_channel="isolated-binary-evolution",
        plotting_style="single_value", rate_type="single",
        submodel="kro1", **{"submodel string": "kro1"},
        sigma_kick="265", alpha_CE="1", RMP="Fryer et al. (2012) rapid",
    )

    ibe_rows = [
        dict(common,
             compact_object_type="NS-BH",
             rate_Gpc3yr="0.2",
             notes=("Pop. II fiducial model (kro1: Kroupa 2001 IMF + Sana "
                    "et al. 2012 orbital/mass-ratio distributions); R(z=0) "
                    "from Table 3 of Mestichelli et al. (2025).")),
        dict(common,
             compact_object_type="NS-NS",
             rate_Gpc3yr="0.0022",
             notes=("Pop. II fiducial model (kro1: Kroupa 2001 IMF + Sana "
                    "et al. 2012 orbital/mass-ratio distributions); R(z=0) "
                    "from Table 5 of Mestichelli et al. (2025).")),
    ]
    append_csv(IBE_CSV, ibe_columns, ibe_rows)

    # --- Pop. III rows -> population-III.csv ----------------------------
    with open(POP3_CSV, newline="") as f:
        pop3_columns = csv.DictReader(f).fieldnames

    pop3_common = dict(
        study_key=STUDY_KEY, label=LABEL, first_author="Mestichelli",
        year="2025", month="6", ads_url="", arxiv_url=ARXIV_URL, code=CODE,
        formation_channel="population-III",
        plotting_style="single_value", rate_type="single",
    )

    pop3_rows = [
        dict(pop3_common,
             compact_object_type="NS-BH",
             rate_Gpc3yr="0.035",
             submodel="lar1",
             notes=("Pop. III model producing the largest BHNS merger rate "
                    "density (lar1: Larson 1998 IMF + Sana et al. 2012 "
                    "orbital/mass-ratio distributions); not the Pop. III "
                    "fiducial model (log1). R(z=0) from Table 3 of "
                    "Mestichelli et al. (2025).")),
        dict(pop3_common,
             compact_object_type="NS-NS",
             rate_Gpc3yr="0.00014",
             submodel="kro1",
             notes=("Pop. III model producing the highest BNS merger rate "
                    "density (kro1: Kroupa 2001 IMF + Sana et al. 2012 "
                    "orbital/mass-ratio distributions); not the Pop. III "
                    "fiducial model (log1). R(z=0) from Table 5 of "
                    "Mestichelli et al. (2025).")),
    ]
    append_csv(POP3_CSV, pop3_columns, pop3_rows)

    print(f"Appended {len(ibe_rows)} rows to {IBE_CSV}")
    print(f"Appended {len(pop3_rows)} rows to {POP3_CSV}")


if __name__ == "__main__":
    main()
