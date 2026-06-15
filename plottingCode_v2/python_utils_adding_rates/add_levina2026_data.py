#!/usr/bin/env python3
from __future__ import annotations
"""
Add Levina et al. (2026) (arXiv:2601.20202) "From cosmological simulations to
binary black hole mergers: The impact of using analytical star formation
history models on gravitational-wave source populations" BBH local merger
rates to the tidy dataset.

Levina et al. (2026) couple the metallicity-specific cosmic star formation
rate density S(Z,z), measured directly from three IllustrisTNG cosmological-
simulation volumes/resolutions (TNG50-1, TNG100-1, TNG300-1), to the COMPAS
population-synthesis simulations of van Son et al. (2022) to predict the BBH
merger rate density. Table 2 gives the local (z~=0) BBH merger rate density
R_sim(z) obtained directly from each simulation's S(Z,z):
  TNG50-1:  58.92 Gpc^-3 yr^-1
  TNG100-1: 42.91 Gpc^-3 yr^-1
  TNG300-1: 29.34 Gpc^-3 yr^-1

The "submodel" difference between the three entries is the SFRD model, i.e.
which IllustrisTNG simulation volume/resolution was used to compute S(Z,z).

Appends:
  - 3 rows to isolated-binary-evolution.csv (BH-BH, plotting_style="range").
  - 2 relationship edges (TNG50-1 -> TNG100-1 -> TNG300-1) to
    isolated-binary-evolution_relationships.csv, under
    parameter_family="star formation history", parameter="SFRD_model"
    (-> "Star formation history" panel in parameter_impact_rate.ipynb).
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"
REL_CSV  = DATA_DIR / "isolated-binary-evolution_relationships.csv"

STUDY_KEY  = "Levina_2026_COMPAS"
LABEL      = "Levina et al. (2026)"
ARXIV_URL  = "https://arxiv.org/abs/2601.20202"
COLOR_CODE = "23"

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

TABLE2_NOTE = ("Local (z~0) BH-BH merger rate density R_sim(z), from Table 2 of "
               "Levina et al. (2026), computed using the simulation-based "
               "metallicity-specific star formation rate density S(Z,z) from "
               "IllustrisTNG, coupled to the van Son et al. (2022) COMPAS "
               "population-synthesis simulations.")

# (TNG box, R_sim(z) BH-BH rate [Gpc^-3 yr^-1])
TABLE2 = [
    ("TNG50-1",  "58.92"),
    ("TNG100-1", "42.91"),
    ("TNG300-1", "29.34"),
]

SFRD_DESC = {
    "TNG50-1":  "IllustrisTNG TNG50-1 simulation-based S(Z,z) (highest resolution, ~50 Mpc box)",
    "TNG100-1": "IllustrisTNG TNG100-1 simulation-based S(Z,z) (intermediate resolution, ~100 Mpc box)",
    "TNG300-1": "IllustrisTNG TNG300-1 simulation-based S(Z,z) (lowest resolution, ~300 Mpc box)",
}


def submodel_string(tng_box: str) -> str:
    return f"Levina26-{tng_box}"


def build_ibe_row(tng_box: str, rate: str) -> dict:
    row = {c: "" for c in IBE_COLUMNS}
    row.update(dict(
        compact_object_type="BH-BH",
        formation_channel="isolated-binary-evolution",
        study_key=STUDY_KEY,
        label=LABEL,
        first_author="Levina",
        year="2026",
        month="1",
        arxiv_url=ARXIV_URL,
        code="COMPAS",
        plotting_style="range",
        rate_Gpc3yr=rate,
        submodel=tng_box,
        **{"submodel string": submodel_string(tng_box)},
        notes=TABLE2_NOTE,
        **{"submodel change 1": "SFRD model (IllustrisTNG simulation resolution/volume: TNG50-1, TNG100-1, TNG300-1)"},
        **{"sfrd-1": SFRD_DESC[tng_box]},
    ))
    return row


def build_edges(rates: dict) -> list[dict]:
    edges = []
    chain = ["TNG50-1", "TNG100-1", "TNG300-1"]
    for from_box, to_box in zip(chain[:-1], chain[1:]):
        edges.append(dict(
            study_key=STUDY_KEY, label=LABEL, code="COMPAS",
            from_submodel=submodel_string(from_box), to_submodel=submodel_string(to_box),
            parameter_family="star formation history", parameter="SFRD_model",
            travel_label=to_box,
            from_value=from_box, to_value=to_box,
            from_rate_Gpc3yr=rates[from_box], to_rate_Gpc3yr=rates[to_box],
            study_color_code=COLOR_CODE,
        ))
    return edges


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
    assert len(TABLE2) == 3

    ibe_rows = [build_ibe_row(box, rate) for box, rate in TABLE2]
    rates = {box: rate for box, rate in TABLE2}
    edges = build_edges(rates)

    append_csv(IBE_CSV, IBE_COLUMNS, ibe_rows)
    append_csv(REL_CSV, REL_COLUMNS, edges)

    print(f"Appended {len(ibe_rows)} rows to {IBE_CSV}")
    print(f"Appended {len(edges)} relationship edges to {REL_CSV}")


if __name__ == "__main__":
    main()
