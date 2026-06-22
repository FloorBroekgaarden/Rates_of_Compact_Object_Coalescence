#!/usr/bin/env python3
from __future__ import annotations
"""
Add Arca Sedda et al. (2026) (arXiv:2603.20430) local merger rate densities
for BBH mergers from different formation channels, read from Figure 2 at z~0.

This script appends 36 rows (9 models × 4 channels) to isolated-binary-evolution.csv.
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"

STUDY_KEY = "ArcaSedda_2026_BPop"
LABEL     = "Arca Sedda et al. (2026)"
ARXIV_URL = "https://arxiv.org/abs/2603.20430"
CODE      = "B-POP"

# Figure 2: z~0 local merger rates [Gpc^-3 yr^-1] read from left edge of each panel
RATES = {
    "F":     {"IB": 31, "YC": 9.5, "GC": 3.5, "NC": 19},
    "Fb0":   {"IB": 30, "YC": 9.0, "GC": 3.2, "NC": 19},
    "Fb1":   {"IB": 32, "YC": 10, "GC": 3.8, "NC": 20},
    "F5":    {"IB": 21, "YC": 12, "GC": 4.5, "NC": 15},
    "Fe":    {"IB": 33, "YC": 8.5, "GC": 3.0, "NC": 20},
    "Fb":    {"IB": 29, "YC": 9.0, "GC": 3.2, "NC": 18},
    "Fmxl":  {"IB": 30, "YC": 9.0, "GC": 3.0, "NC": 19},
    "Fgp":   {"IB": 30, "YC": 8.8, "GC": 3.1, "NC": 19},
    "Fst":   {"IB": 30, "YC": 9.0, "GC": 3.2, "NC": 19},
}

# Formation channel labels
CHANNEL_NAME = {
    "IB": "isolated-binary-evolution",
    "YC": "young-cluster",
    "GC": "globular-cluster",
    "NC": "nuclear-cluster",
}

CHANNEL_DESC = {
    "IB": "isolated binaries",
    "YC": "young clusters",
    "GC": "globular clusters",
    "NC": "nuclear star clusters",
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
        compact_object_type="BH-BH",
        study_key=STUDY_KEY, label=LABEL, first_author="Arca Sedda",
        year="2026", month="03", ads_url="", arxiv_url=ARXIV_URL,
        code=CODE, plotting_style="range", rate_type="",
    )

    ibe_rows = []
    for model_name, channels in RATES.items():
        for channel_abbr, rate in channels.items():
            sm = f"ArcaSedda26-{model_name}-1g-{channel_abbr}"
            ibe_rows.append(dict(
                common,
                formation_channel=CHANNEL_NAME[channel_abbr],
                rate_Gpc3yr=str(rate),
                submodel=sm,
                **{"submodel string": sm},
                notes=(
                    f"BBH merger rate for {CHANNEL_DESC[channel_abbr]} "
                    f"(model {model_name}): R(z~0) = {rate} Gpc^-3 yr^-1. "
                    f"Read from Figure 2 (z~0 edge) of Arca Sedda et al. (2026) "
                    f"arXiv:2603.20430 (B-POP semi-analytic code)."
                ),
            ))

    append_csv(IBE_CSV, ibe_columns, ibe_rows)
    print(f"Appended {len(ibe_rows)} rows to {IBE_CSV}")


if __name__ == "__main__":
    main()
