#!/usr/bin/env python3
from __future__ import annotations
"""
Add Zhu et al. (2024) (arXiv:2404.10596) COMPAS BHNS merger rate densities
from Table 1 (R_BHNS column, median values only -- the mgBHNS column and the
+/- credible-interval bounds are NOT used, per the user's request).

The 8 models form a 2D grid in (alpha_CE, sigma_kick):
  alpha_CE  in {1, 2, 5, 10}
  sigma_kick in {100, 265} km/s

  Model     R_BHNS [Gpc^-3 yr^-1]
  a1 s100   149
  a2 s100   153
  a5 s100    86
  a10 s100   67
  a1 s265    39
  a2 s265    37
  a5 s265    28
  a10 s265   25

This script:
  1. Appends 8 NS-BH rows to isolated-binary-evolution.csv.
  2. Appends relationship edges to isolated-binary-evolution_relationships.csv:
     - alpha_CE chains (1->2->5->10) for each sigma_kick value (2 x 3 = 6 edges)
     - sigma_kick edges (100->265) for each alpha_CE value (4 x 1 = 4 edges)
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"
REL_CSV  = DATA_DIR / "isolated-binary-evolution_relationships.csv"

STUDY_KEY  = "Zhu_2024_COMPAS"
LABEL      = "Zhu et al. (2024)"
ARXIV_URL  = "https://arxiv.org/abs/2404.10596"
CODE       = "COMPAS"
COLOR_CODE = "26"

ALPHA_VALUES = ["1", "2", "5", "10"]
SIGMA_VALUES = ["100", "265"]

RATES = {
    ("1", "100"): "149",
    ("2", "100"): "153",
    ("5", "100"): "86",
    ("10", "100"): "67",
    ("1", "265"): "39",
    ("2", "265"): "37",
    ("5", "265"): "28",
    ("10", "265"): "25",
}


def submodel(alpha, sigma) -> str:
    return f"Zhu24-aCE{alpha}-sigma{sigma}"


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
        compact_object_type="NS-BH", formation_channel="isolated-binary-evolution",
        study_key=STUDY_KEY, label=LABEL, first_author="Zhu",
        year="2024", month="4", ads_url="", arxiv_url=ARXIV_URL, code=CODE,
        plotting_style="range", rate_type="",
    )

    ibe_rows = []
    for alpha in ALPHA_VALUES:
        for sigma in SIGMA_VALUES:
            sm = submodel(alpha, sigma)
            ibe_rows.append(dict(
                common,
                rate_Gpc3yr=RATES[(alpha, sigma)],
                submodel=sm,
                **{"submodel string": sm},
                alpha_CE=alpha, sigma_kick=sigma,
                notes=(f"R_BHNS (median) from Table 1 of Zhu et al. (2024), "
                       f"model alpha_CE={alpha}, sigma_kick={sigma} km/s "
                       f"(COMPAS); the mgBHNS subset (RmgBHNS column) and "
                       f"the quoted +/- credible-interval bounds are not used."),
            ))
    append_csv(IBE_CSV, ibe_columns, ibe_rows)

    # --- relationship edges ----------------------------------------------
    with open(REL_CSV, newline="") as f:
        rel_columns = csv.DictReader(f).fieldnames

    edges = []

    # alpha_CE chains (1->2->5->10) for each sigma_kick
    for sigma in SIGMA_VALUES:
        for a_from, a_to in zip(ALPHA_VALUES[:-1], ALPHA_VALUES[1:]):
            edges.append(dict(
                study_key=STUDY_KEY, label=LABEL, code=CODE,
                from_submodel=submodel(a_from, sigma),
                to_submodel=submodel(a_to, sigma),
                parameter_family="common envelope efficiency", parameter="alpha_CE",
                travel_label=r"$\alpha_{\rm CE} \uparrow$",
                from_value=a_from, to_value=a_to,
                from_rate_Gpc3yr=RATES[(a_from, sigma)],
                to_rate_Gpc3yr=RATES[(a_to, sigma)],
                study_color_code=COLOR_CODE,
            ))

    # sigma_kick edges (100->265) for each alpha_CE
    for alpha in ALPHA_VALUES:
        edges.append(dict(
            study_key=STUDY_KEY, label=LABEL, code=CODE,
            from_submodel=submodel(alpha, "100"),
            to_submodel=submodel(alpha, "265"),
            parameter_family="natal kick", parameter="sigma_kick",
            travel_label=r"$\sigma_{\rm kick} \uparrow$",
            from_value="100", to_value="265",
            from_rate_Gpc3yr=RATES[(alpha, "100")],
            to_rate_Gpc3yr=RATES[(alpha, "265")],
            study_color_code=COLOR_CODE,
        ))

    append_csv(REL_CSV, rel_columns, edges)

    print(f"Appended {len(ibe_rows)} rows to {IBE_CSV}")
    print(f"Appended {len(edges)} edges to {REL_CSV}")


if __name__ == "__main__":
    main()
