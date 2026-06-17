#!/usr/bin/env python3
from __future__ import annotations
"""
Add Chen et al. (2025) (arXiv:2508.14397) BNS local merger rate densities
for different common-envelope evolution scenarios, varying alpha (CE efficiency)
and f_HG (fraction of HG donors that cannot survive CE).

From Figure 1 (top panel) scatter points, models M1–M22.
Fiducial model: M6 (alpha=3, f_HG=0).

This script appends 22 rows to isolated-binary-evolution.csv.
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"

STUDY_KEY = "Chen_2025_BSE"
LABEL     = "Chen et al. (2025)"
ARXIV_URL = "https://arxiv.org/abs/2508.14397"
CODE      = "BSE"

# Figure 1 (top panel): BNS R_0 [Gpc^-3 yr^-1] for models M1–M22
# Format: model -> (alpha_CE, f_HG, rate_Gpc3yr)
MODELS = {
    "M1":  (1.0, 0.0, 373),
    "M2":  (1.0, 0.2, 361),
    "M3":  (1.0, 0.4, 354),
    "M4":  (1.0, 0.6, 351),
    "M5":  (1.0, 0.8, 331),
    "M6":  (3.0, 0.0, 383),    # Fiducial model
    "M7":  (3.0, 0.2, 345),
    "M8":  (3.0, 0.4, 293),
    "M9":  (3.0, 0.6, 240),
    "M10": (3.0, 0.8, 150),
    "M11": (3.0, 1.0, 130),
    "M12": (5.0, 0.8, 120),
    "M13": (5.0, 0.2, 410),
    "M14": (5.0, 0.4, 280),
    "M15": (5.0, 0.6, 200),
    "M16": (5.0, 0.0, 300),
    "M17": (7.0, 0.8, 90),
    "M18": (7.0, 0.2, 160),
    "M19": (7.0, 0.4, 130),
    "M20": (10.0, 0.6, 110),
    "M21": (10.0, 0.8, 90),
    "M22": (10.0, 1.0, 70),
}

# CE prescription mapping: f_HG=0 is "pessimistic" (all HG merge in CE),
# f_HG=1 is "optimistic" (no HG merge in CE), intermediate values in between.
CE_PRESCRIP = {
    0.0: "pessimistic (f_HG=0)",
    0.2: "pessimistic-moderate (f_HG=0.2)",
    0.4: "moderate (f_HG=0.4)",
    0.6: "moderate-optimistic (f_HG=0.6)",
    0.8: "optimistic (f_HG=0.8)",
    1.0: "fully optimistic (f_HG=1.0)",
}


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
        study_key=STUDY_KEY, label=LABEL, first_author="Chen",
        year="2025", month="09", ads_url="", arxiv_url=ARXIV_URL,
        code=CODE, plotting_style="range", rate_type="",
    )

    ibe_rows = []
    for model_name, (alpha, fhg, rate) in MODELS.items():
        sm = f"Chen25-{model_name}-a{alpha:.0f}-fHG{fhg:.1f}".replace(".", "p")
        ce_desc = CE_PRESCRIP.get(fhg, f"f_HG={fhg}")
        ibe_rows.append(dict(
            common,
            rate_Gpc3yr=str(rate),
            submodel=sm,
            **{"submodel string": sm},
            alpha_CE=str(alpha),
            notes=(
                f"BNS local merger rate R_0 = {rate} Gpc^-3 yr^-1 for model {model_name} "
                f"with α_CE={alpha} and f_HG={fhg} (fraction of HG donors surviving CE: {ce_desc}). "
                f"Read from Figure 1 (top panel) of Chen et al. (2025) arXiv:2508.14397 "
                f"(BSE population synthesis code)."
            ),
        ))

    append_csv(IBE_CSV, ibe_columns, ibe_rows)
    print(f"Appended {len(ibe_rows)} rows to {IBE_CSV}")


if __name__ == "__main__":
    main()
