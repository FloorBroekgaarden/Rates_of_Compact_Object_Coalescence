#!/usr/bin/env python3
from __future__ import annotations
"""
Add Smith et al. (2026) "Massquerade" (arXiv:2605.21580) BBH local merger
rates to the tidy dataset.

Smith et al. (2026) compare simulation outcomes for binary black hole merger
rates and mass distributions from two population-synthesis frameworks,
COMPAS and SEVN. Local (z~0) BH-BH merger rates, read from the black lines
of Fig. 1:
  - COMPAS model: ~90  Gpc^-3 yr^-1
  - SEVN model:   ~200 Gpc^-3 yr^-1

The "submodel" difference between the two entries is the population-synthesis
code (COMPAS vs SEVN).

Appends:
  - 2 rows to isolated-binary-evolution.csv, with plotting_style="range" so
    that both values are drawn.
  - 1 relationship edge (COMPAS -> SEVN) to
    isolated-binary-evolution_relationships.csv.
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"
REL_CSV  = DATA_DIR / "isolated-binary-evolution_relationships.csv"

STUDY_KEY  = "Smith_2026_Massquerade"
LABEL      = "Smith et al. (2026)"
ARXIV_URL  = "https://arxiv.org/abs/2605.21580"
COLOR_CODE = "21"

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

REL_COLUMNS = [
    "study_key", "label", "code", "from_submodel", "to_submodel",
    "parameter_family", "parameter", "travel_label",
    "from_value", "to_value", "from_rate_Gpc3yr", "to_rate_Gpc3yr",
    "study_color_code",
]

FIG1_NOTE = ("Local (z~0) BH-BH merger rate (black line), read from Fig. 1 of "
              "Smith et al. (2026)")


def base_row(**overrides) -> dict:
    row = {c: "" for c in IBE_COLUMNS}
    row.update(dict(
        compact_object_type="BH-BH",
        formation_channel="isolated-binary-evolution",
        study_key=STUDY_KEY,
        label=LABEL,
        first_author="Smith",
        year="2026",
        month="5",
        arxiv_url=ARXIV_URL,
        plotting_style="range",
        **{"submodel change 1": "population synthesis code (COMPAS vs SEVN)"},
    ))
    row.update(overrides)
    return row


MODELS = {
    "compas": base_row(
        code="COMPAS",
        rate_Gpc3yr="90",
        submodel="Massquerade-COMPAS",
        **{"submodel string": "Smith26-COMPAS"},
        notes=f"{FIG1_NOTE}, using the COMPAS population-synthesis code.",
        stellar_tracks="COMPAS",
    ),
    "sevn": base_row(
        code="SEVN",
        rate_Gpc3yr="200",
        submodel="Massquerade-SEVN",
        **{"submodel string": "Smith26-SEVN"},
        notes=f"{FIG1_NOTE}, using the SEVN population-synthesis code.",
        stellar_tracks="SEVN",
    ),
}


def build_edges() -> list[dict]:
    compas, sevn = MODELS["compas"], MODELS["sevn"]
    return [dict(
        study_key=STUDY_KEY, label=LABEL, code="COMPAS/SEVN",
        from_submodel=compas["submodel string"], to_submodel=sevn["submodel string"],
        parameter_family="population synthesis code",
        parameter="BPS_code",
        travel_label="SEVN",
        from_value="COMPAS", to_value="SEVN",
        from_rate_Gpc3yr=compas["rate_Gpc3yr"], to_rate_Gpc3yr=sevn["rate_Gpc3yr"],
        study_color_code=COLOR_CODE,
    )]


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
    ibe_rows = list(MODELS.values())
    edges = build_edges()

    append_csv(IBE_CSV, IBE_COLUMNS, ibe_rows)
    append_csv(REL_CSV, REL_COLUMNS, edges)

    print(f"Appended {len(ibe_rows)} rows to {IBE_CSV}")
    print(f"Appended {len(edges)} relationship edges to {REL_CSV}")


if __name__ == "__main__":
    main()
