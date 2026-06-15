#!/usr/bin/env python3
from __future__ import annotations
"""
Add de Sa et al. (2024) (arXiv:2410.01451) local merger rate densities
(z_merger <= 0.014) from Table 3 / the "Full" row of Table 2, for the
Varying and Invariant IMF models (COMPAS-based BOSSA framework).

  Source     BHBH      BHNS     NSNS    [Gpc^-3 yr^-1]
  Varying    1314.4    432.5    64.0
  Invariant    25.5      7.0     6.6

No distinction is made between BHNS and NSBH in this paper.

This script appends 6 rows (3 DCO types x 2 IMF models) to
isolated-binary-evolution.csv.
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"

STUDY_KEY  = "deSa_2024_COMPAS"
LABEL      = "de Sá et al. (2024)"
ARXIV_URL  = "https://arxiv.org/abs/2410.01451"
CODE       = "COMPAS"

RATES = {
    ("BH-BH", "Varying"): "1314.4",
    ("BH-BH", "Invariant"): "25.5",
    ("NS-BH", "Varying"): "432.5",
    ("NS-BH", "Invariant"): "7.0",
    ("NS-NS", "Varying"): "64.0",
    ("NS-NS", "Invariant"): "6.6",
}

DCO_TYPES = ["BH-BH", "NS-BH", "NS-NS"]
IMF_MODELS = ["Invariant", "Varying"]


def submodel(imf) -> str:
    return f"deSa24-{imf}"


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
    # --- isolated-binary-evolution.csv rows -----------------------------
    with open(IBE_CSV, newline="") as f:
        ibe_columns = csv.DictReader(f).fieldnames

    common = dict(
        formation_channel="isolated-binary-evolution",
        study_key=STUDY_KEY, label=LABEL, first_author="de Sá",
        year="2024", month="10", ads_url="", arxiv_url=ARXIV_URL, code=CODE,
        plotting_style="range", rate_type="",
    )

    ibe_rows = []
    for co in DCO_TYPES:
        for imf in IMF_MODELS:
            sm = submodel(imf)
            ibe_rows.append(dict(
                common,
                compact_object_type=co,
                rate_Gpc3yr=RATES[(co, imf)],
                submodel=sm,
                **{"submodel string": sm},
                notes=(f"Local merger rate density (z_merger <= 0.014) for "
                       f"the '{imf}' IMF model, from the 'Full' row of "
                       f"Table 2 / Table 3 of de Sá et al. (2024) "
                       f"(BOSSA initial-conditions framework + COMPAS); "
                       f"BHNS and NSBH are not distinguished."),
            ))
    append_csv(IBE_CSV, ibe_columns, ibe_rows)

    print(f"Appended {len(ibe_rows)} rows to {IBE_CSV}")


if __name__ == "__main__":
    main()
