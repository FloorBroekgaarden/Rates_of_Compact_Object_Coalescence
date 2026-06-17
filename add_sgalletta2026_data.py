#!/usr/bin/env python3
from __future__ import annotations
"""
Add Sgalletta et al. (2026) (arXiv:2605.06807) local merger rate densities
R(z~0) [Gpc^-3 yr^-1] read from Figure 8 (BBH left panel, BHNS centre,
BNS right), varying alpha_CE (0.5, 1, 3, 5) and binding-energy prescription
(This work / Claeys+14 / Klencki+21).

Reading method: pixel colour-scan of the leftmost visible region of each
panel (z~0.28-0.44) at 300 DPI rendering of the PDF.  Values are approximate
(~factor-2 precision) due to anti-aliasing and line-style overlap at low z.

Physics summary (paper text):
  BBH/BHNS : ThisWork ≈ Klencki21 >> Claeys14  (new E_bind boosts rates)
  BNS      : Claeys14 >> ThisWork ≈ Klencki21  (new E_bind quenches BNS for alpha<=1)
  Claeys14 BNS alpha=0.5 : below plot floor at z=0 (<0.1 Gpc^-3 yr^-1) — row omitted.

This script appends 35 rows to isolated-binary-evolution.csv.
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"

STUDY_KEY = "Sgalletta_2026_SEVN"
LABEL     = "Sgalletta et al. (2026)"
ARXIV_URL = "https://arxiv.org/abs/2605.06807"
CODE      = "SEVN"

# (compact_object_type, alpha_CE, binding_energy_label) -> rate [Gpc^-3 yr^-1]
# Read from Figure 8 at z~0 (far-left edge of each panel).
# Colors: purple=alpha=0.5, blue=alpha=1, green=alpha=3, yellow=alpha=5
# Line styles: solid=ThisWork, dashed=Claeys14, dotted=Klencki21
RATES = {
    # BBH — ThisWork/Klencki21 boosted relative to Claeys14
    ("BH-BH", "5.0", "ThisWork"):  "738",
    ("BH-BH", "5.0", "Klencki21"): "738",
    ("BH-BH", "5.0", "Claeys14"):  "138",
    ("BH-BH", "3.0", "ThisWork"):  "565",
    ("BH-BH", "3.0", "Klencki21"): "565",
    ("BH-BH", "3.0", "Claeys14"):  "175",
    ("BH-BH", "1.0", "ThisWork"):  "200",
    ("BH-BH", "1.0", "Klencki21"): "200",
    ("BH-BH", "1.0", "Claeys14"):  "120",
    ("BH-BH", "0.5", "ThisWork"):  "95",
    ("BH-BH", "0.5", "Klencki21"): "95",
    ("BH-BH", "0.5", "Claeys14"):  "55",

    # BHNS — same ordering as BBH
    ("NS-BH", "5.0", "ThisWork"):  "210",
    ("NS-BH", "5.0", "Klencki21"): "210",
    ("NS-BH", "5.0", "Claeys14"):  "56",
    ("NS-BH", "3.0", "ThisWork"):  "249",
    ("NS-BH", "3.0", "Klencki21"): "249",
    ("NS-BH", "3.0", "Claeys14"):  "66",
    ("NS-BH", "1.0", "ThisWork"):  "190",
    ("NS-BH", "1.0", "Klencki21"): "190",
    ("NS-BH", "1.0", "Claeys14"):  "82",
    ("NS-BH", "0.5", "ThisWork"):  "122",
    ("NS-BH", "0.5", "Klencki21"): "122",
    ("NS-BH", "0.5", "Claeys14"):  "87",

    # BNS — Claeys14 highest; ThisWork/Klencki21 quenched for low alpha
    ("NS-NS", "5.0", "ThisWork"):  "195",
    ("NS-NS", "5.0", "Klencki21"): "195",
    ("NS-NS", "5.0", "Claeys14"):  "341",
    ("NS-NS", "3.0", "ThisWork"):  "82",
    ("NS-NS", "3.0", "Klencki21"): "82",
    ("NS-NS", "3.0", "Claeys14"):  "120",
    ("NS-NS", "1.0", "ThisWork"):  "1.2",
    ("NS-NS", "1.0", "Klencki21"): "1.2",
    ("NS-NS", "1.0", "Claeys14"):  "250",
    ("NS-NS", "0.5", "ThisWork"):  "0.1",
    ("NS-NS", "0.5", "Klencki21"): "0.1",
    # ("NS-NS", "0.5", "Claeys14"): omitted — below plot floor (<0.1 Gpc^-3 yr^-1) at z=0
}

DCO_LABEL = {"BH-BH": "BBH", "NS-BH": "BHNS", "NS-NS": "BNS"}
ALPHA_TAG = {"5.0": "a5", "3.0": "a3", "1.0": "a1", "0.5": "a05"}
BINDING_NOTE = {
    "ThisWork":  "self-consistent PARSEC binding-energy prescription (solid line)",
    "Klencki21": "Klencki et al. (2021) binding-energy prescription (dotted line)",
    "Claeys14":  "Claeys et al. (2014) binding-energy prescription (dashed line)",
}


def submodel_key(co, alpha, be):
    return f"Sgalletta26-{DCO_LABEL[co]}-{ALPHA_TAG[alpha]}-{be}"


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
        formation_channel="isolated-binary-evolution",
        study_key=STUDY_KEY, label=LABEL, first_author="Sgalletta",
        year="2026", month="05", ads_url="", arxiv_url=ARXIV_URL,
        code=CODE, plotting_style="range", rate_type="",
    )

    ibe_rows = []
    for (co, alpha, be), rate in RATES.items():
        sm = submodel_key(co, alpha, be)
        ibe_rows.append(dict(
            common,
            compact_object_type=co,
            rate_Gpc3yr=rate,
            submodel=sm,
            **{"submodel string": sm},
            alpha_CE=alpha,
            binding_energy=be,
            notes=(
                f"Local merger rate density R(z~0) [Gpc^-3 yr^-1] for "
                f"{DCO_LABEL[co]} mergers with alpha_CE={alpha} and "
                f"{BINDING_NOTE[be]}. Read from Figure 8 (z~0, far-left "
                f"edge) of Sgalletta et al. (2026) arXiv:2605.06807 by "
                f"pixel colour-scan at 300 DPI; approximate precision "
                f"~factor 2. SEVN code (galaxyRate framework)."
            ),
        ))

    append_csv(IBE_CSV, ibe_columns, ibe_rows)
    print(f"Appended {len(ibe_rows)} rows to {IBE_CSV}")


if __name__ == "__main__":
    main()
