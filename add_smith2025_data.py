#!/usr/bin/env python3
from __future__ import annotations
"""
Add Smith & Kaplinghat (2025) (arXiv:2412.13318) BBH local merger rates to the
tidy dataset.

Smith & Kaplinghat (2025) use the SEVN population synthesis code, combined
with an empirically constrained galaxy stellar mass function, mass-metallicity
relation, and star-forming main sequence, to predict the volumetric BH-BH
merger rate density vs. redshift. They consider two IMF models:
  - constant-slope IMF (alpha=2.3, beta=0.0)
  - running-slope IMF  (alpha=2.3, beta=0.3), which flattens at higher masses
each evaluated for three delay-time-distribution (DTD) power-law indices,
P(tau) ~ tau^-gamma, with gamma = 0.5, 0.85, 1.0.

Local (z~0) BH-BH merger rates, read off Fig. 8:
  constant-slope IMF: gamma=0.5 -> 66, gamma=0.85 -> 36, gamma=1.0 -> 22
  running-slope  IMF: gamma=0.5 -> 78, gamma=0.85 -> 43, gamma=1.0 -> 27
  (all in Gpc^-3 yr^-1)

Appends:
  - 6 rows to isolated-binary-evolution.csv, with plotting_style="range" so
    that all 6 values are drawn.
  - 7 relationship edges to isolated-binary-evolution_relationships.csv:
      - 4 "DTD slope (gamma)" edges (gamma: 0.5 -> 0.85 -> 1.0, one chain per IMF)
      - 3 "IMF" edges (constant-slope -> running-slope, one per gamma value)
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"
REL_CSV  = DATA_DIR / "isolated-binary-evolution_relationships.csv"

STUDY_KEY  = "Smith_2025_SEVN"
LABEL_IBE  = "Smith and Kaplinghat (2025)"
LABEL_REL  = r"Smith \& Kaplinghat (2025)"
ARXIV_URL  = "https://arxiv.org/abs/2412.13318"
COLOR_CODE = "20"

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

FIG8_NOTE = ("Local (z~0) BH-BH merger rate, read from Fig. 8 of "
              "Smith & Kaplinghat (2025)")

IMF_INFO = {
    "const": dict(
        desc="constant-slope IMF (alpha=2.3, beta=0.0)",
        value=r"constant-slope ($\alpha=2.3,\,\beta=0.0$)",
    ),
    "run": dict(
        desc="running-slope IMF (alpha=2.3, beta=0.3), which flattens at higher masses",
        value=r"running-slope ($\alpha=2.3,\,\beta=0.3$)",
    ),
}

GAMMA_ORDER = ["0.5", "0.85", "1.0"]

RATES = {
    ("const", "0.5"):  "66",
    ("const", "0.85"): "36",
    ("const", "1.0"):  "22",
    ("run",   "0.5"):  "78",
    ("run",   "0.85"): "43",
    ("run",   "1.0"):  "27",
}


def submodel_string(imf_key: str, gamma: str) -> str:
    return f"S25-IMF{imf_key}-g{gamma}"


def build_ibe_row(imf_key: str, gamma: str) -> dict:
    row = {c: "" for c in IBE_COLUMNS}
    imf = IMF_INFO[imf_key]
    sm = submodel_string(imf_key, gamma)
    notes = (
        f"SEVN BPS model with {imf['desc']}; "
        f"DTD power-law index gamma={gamma} (P(tau) ~ tau^-gamma); "
        f"{FIG8_NOTE}."
    )
    row.update(dict(
        compact_object_type="BH-BH",
        formation_channel="isolated-binary-evolution",
        study_key=STUDY_KEY,
        label=LABEL_IBE,
        first_author="Smith",
        year="2025",
        arxiv_url=ARXIV_URL,
        code="SEVN",
        plotting_style="range",
        rate_Gpc3yr=RATES[(imf_key, gamma)],
        submodel=sm,
        **{"submodel string": sm},
        notes=notes,
        **{"submodel change 1": "IMF (constant-slope vs running-slope)",
           "submodel change 2": "DTD power-law index (gamma)"},
        stellar_tracks="SEVN",
    ))
    return row


def build_edges() -> list[dict]:
    edges = []

    # DTD slope chains (gamma: 0.5 -> 0.85 -> 1.0), one chain per IMF.
    for imf_key in ("const", "run"):
        for g_from, g_to in zip(GAMMA_ORDER[:-1], GAMMA_ORDER[1:]):
            edges.append(dict(
                study_key=STUDY_KEY, label=LABEL_REL, code="SEVN",
                from_submodel=submodel_string(imf_key, g_from),
                to_submodel=submodel_string(imf_key, g_to),
                parameter_family="delay-time distribution (DTD slope)",
                parameter="DTD_gamma",
                travel_label=r"$\gamma_{\rm DTD}\uparrow$",
                from_value=g_from, to_value=g_to,
                from_rate_Gpc3yr=RATES[(imf_key, g_from)],
                to_rate_Gpc3yr=RATES[(imf_key, g_to)],
                study_color_code=COLOR_CODE,
            ))

    # IMF chains (constant-slope -> running-slope), one per gamma value.
    for gamma in GAMMA_ORDER:
        edges.append(dict(
            study_key=STUDY_KEY, label=LABEL_REL, code="SEVN",
            from_submodel=submodel_string("const", gamma),
            to_submodel=submodel_string("run", gamma),
            parameter_family="initial conditions",
            parameter="IMF",
            travel_label="running-slope IMF",
            from_value=IMF_INFO["const"]["value"],
            to_value=IMF_INFO["run"]["value"],
            from_rate_Gpc3yr=RATES[("const", gamma)],
            to_rate_Gpc3yr=RATES[("run", gamma)],
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
    ibe_rows = [build_ibe_row(imf_key, gamma)
                for imf_key in ("const", "run")
                for gamma in GAMMA_ORDER]
    edges = build_edges()

    append_csv(IBE_CSV, IBE_COLUMNS, ibe_rows)
    append_csv(REL_CSV, REL_COLUMNS, edges)

    print(f"Appended {len(ibe_rows)} rows to {IBE_CSV}")
    print(f"Appended {len(edges)} relationship edges to {REL_CSV}")


if __name__ == "__main__":
    main()
