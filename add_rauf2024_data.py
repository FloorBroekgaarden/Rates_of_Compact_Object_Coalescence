#!/usr/bin/env python3
from __future__ import annotations
"""
Add Rauf et al. (2024) (arXiv:2406.11885) BBH local merger rates, read from
Figure 3 at redshift 0, to the tidy dataset.

Figure 3 reproduces the volumetric BBH merger rate vs. redshift from Rauf
et al. (2023), recreated with the effective-factor rescaling method, for
four COMPAS remnant-mass-prescription (RMP) / Wolf-Rayet wind-factor (f_WR)
variants. Fiducial model (Table 1): RMP = Mandel & Muller (2020), f_WR = 1.

Local (z=0) rates, read off the median (solid-line) curve of Fig. 3:
  - Mandel & Muller (2020)            (fiducial)   ~ 39   Gpc^-3 yr^-1
  - Mandel & Muller (2020), f_WR=0.2                ~ 47   Gpc^-3 yr^-1
  - Fryer et al. (2012)                             ~ 290  Gpc^-3 yr^-1
  - Schneider et al. (2021)                         ~ 4.7  Gpc^-3 yr^-1

Appends:
  - 4 rows to isolated-binary-evolution.csv, with plotting_style="range" so
    that all 4 values are drawn (a single study_key with plotting_style=
    "single_value" would only plot one point per draw_study() in plot_rates.py)
  - 3 relationship edges (fiducial -> each of the other 3 models): two
    "remnant mass prescription" (RMP) edges and one "stellar winds" (f_WR)
    edge, to isolated-binary-evolution_relationships.csv.
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"
REL_CSV  = DATA_DIR / "isolated-binary-evolution_relationships.csv"

STUDY_KEY  = "Rauf_2024_COMPAS"
LABEL      = "Rauf et al. (2024)"
ARXIV_URL  = "https://arxiv.org/abs/2406.11885"
COLOR_CODE = "19"

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

FIG3_NOTE = ("Local (z=0) BBH merger rate, read from the median (solid line) "
             "of Fig. 3 of Rauf et al. (2024)")


def base_row(**overrides) -> dict:
    row = {c: "" for c in IBE_COLUMNS}
    row.update(dict(
        compact_object_type="BH-BH",
        formation_channel="isolated-binary-evolution",
        study_key=STUDY_KEY,
        label=LABEL,
        first_author="Rauf",
        year="2024",
        month="6",
        arxiv_url=ARXIV_URL,
        code="COMPAS",
        plotting_style="range",
        f_WR="1",
    ))
    row.update(overrides)
    return row


MODELS = {
    "fiducial": base_row(
        submodel="Rauf24-MandelMuller2020",
        **{"submodel string": "Rauf24-MandelMuller2020"},
        rate_Gpc3yr="39",
        RMP="Mandel & Muller (2020) stochastic",
        **{"submodel change 1": "fiducial"},
        notes=f"Fiducial COMPAS/Shark model (remnant-mass prescription: "
              f"Mandel & Muller 2020, f_WR=1); {FIG3_NOTE}.",
    ),
    "fryer2012": base_row(
        submodel="Rauf24-Fryer2012",
        **{"submodel string": "Rauf24-Fryer2012"},
        rate_Gpc3yr="290",
        RMP="Fryer et al. (2012) delayed",
        **{"submodel change 1": "remnant mass prescription"},
        notes=f"BPS variation: remnant mass prescription -> Fryer et al. (2012) delayed; "
              f"{FIG3_NOTE}.",
    ),
    "mm_fwr02": base_row(
        submodel="Rauf24-MandelMuller2020-fWR0.2",
        **{"submodel string": "Rauf24-MandelMuller2020-fWR0.2"},
        rate_Gpc3yr="47",
        RMP="Mandel & Muller (2020) stochastic",
        f_WR="0.2",
        **{"submodel change 1": "stellar winds (f_WR)"},
        notes=f"BPS variation: Wolf-Rayet wind multiplier f_WR: 1 -> 0.2; {FIG3_NOTE}.",
    ),
    "schneider2021": base_row(
        submodel="Rauf24-Schneider2021",
        **{"submodel string": "Rauf24-Schneider2021"},
        rate_Gpc3yr="4.7",
        RMP="Schneider et al. (2021)",
        **{"submodel change 1": "remnant mass prescription"},
        notes=f"BPS variation: remnant mass prescription -> Schneider et al. (2021); "
              f"{FIG3_NOTE}.",
    ),
}


def build_edges() -> list[dict]:
    fid = MODELS["fiducial"]
    edges = []

    edges.append(dict(
        study_key=STUDY_KEY, label=LABEL, code="COMPAS",
        from_submodel=fid["submodel string"], to_submodel=MODELS["fryer2012"]["submodel string"],
        parameter_family="remnant mass prescription", parameter="RMP",
        travel_label="Fryer et al. (2012) delayed",
        from_value=fid["RMP"], to_value=MODELS["fryer2012"]["RMP"],
        from_rate_Gpc3yr=fid["rate_Gpc3yr"], to_rate_Gpc3yr=MODELS["fryer2012"]["rate_Gpc3yr"],
        study_color_code=COLOR_CODE,
    ))
    edges.append(dict(
        study_key=STUDY_KEY, label=LABEL, code="COMPAS",
        from_submodel=fid["submodel string"], to_submodel=MODELS["schneider2021"]["submodel string"],
        parameter_family="remnant mass prescription", parameter="RMP",
        travel_label="Schneider et al. (2021)",
        from_value=fid["RMP"], to_value=MODELS["schneider2021"]["RMP"],
        from_rate_Gpc3yr=fid["rate_Gpc3yr"], to_rate_Gpc3yr=MODELS["schneider2021"]["rate_Gpc3yr"],
        study_color_code=COLOR_CODE,
    ))
    edges.append(dict(
        study_key=STUDY_KEY, label=LABEL, code="COMPAS",
        from_submodel=fid["submodel string"], to_submodel=MODELS["mm_fwr02"]["submodel string"],
        parameter_family="stellar winds", parameter="f_WR",
        travel_label=r"$f_{\rm WR}\downarrow$",
        from_value=fid["f_WR"], to_value=MODELS["mm_fwr02"]["f_WR"],
        from_rate_Gpc3yr=fid["rate_Gpc3yr"], to_rate_Gpc3yr=MODELS["mm_fwr02"]["rate_Gpc3yr"],
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
    ibe_rows = list(MODELS.values())
    edges = build_edges()

    append_csv(IBE_CSV, IBE_COLUMNS, ibe_rows)
    append_csv(REL_CSV, REL_COLUMNS, edges)

    print(f"Appended {len(ibe_rows)} rows to {IBE_CSV}")
    print(f"Appended {len(edges)} relationship edges to {REL_CSV}")


if __name__ == "__main__":
    main()
