#!/usr/bin/env python3
from __future__ import annotations
"""
Add van Son et al. (2023) (arXiv:2209.03385) BBH SFRD-model-variation local
merger rates to the tidy dataset.

van Son et al. (2023) compute BBH merger rate densities for a single COMPAS
binary population, reweighted by a family of metallicity-specific cosmic star
formation rate density S(Z,z) models. S(Z,z) is parameterized (following
Neijssel et al. 2019 / van Son et al. 2022) by a skewed log-normal metallicity
distribution with parameters mu_0, mu_z, omega_0, omega_z, alpha, multiplying
an overall SFR(z) normalization. From Figures 3 & 4, the total (CE + stable
mass-transfer channel) local (z~0.2) BBH merger rate density R_0.2 is given
for each one-parameter-at-a-time SFRD variation; values were transcribed by
the user into
"Data_Mandel_and_Broekgaarden_2026/individual_extracted_data/vanSon 2023 - raw.csv".

The existing fiducial row (study_key="vanSon_2023_COMPAS", submodel="van Son
(2023)", rate_Gpc3yr=58.9) corresponds to the "Fiducial (omega_0=1.13)" row of
that table and is reused as the anchor for the omega_0 chain below.

Appends:
  - 12 rows to isolated-binary-evolution.csv (BH-BH, plotting_style="range"),
    one per non-fiducial SFRD variation.
  - 7 relationship edges to isolated-binary-evolution_relationships.csv,
    under parameter_family="star formation history", parameter="SFRD_model"
    (-> "Star formation history" panel in parameter_impact_rate.ipynb):
      - omega_0 chain: Narrow -> Fiducial -> Wide (2 edges)
      - omega_z:        Flat -> Steep                (1 edge)
      - mu_0:           low -> high                  (1 edge)
      - mu_z:           Flat -> Steep                 (1 edge)
      - alpha:          Symmetric -> Skewed           (1 edge)
      - overall SFR(z): Madau & Fragos (2017) -> approx. upper limit (1 edge)
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"
REL_CSV  = DATA_DIR / "isolated-binary-evolution_relationships.csv"

STUDY_KEY  = "vanSon_2023_COMPAS"
LABEL      = "van Son et al. (2023)"
ARXIV_URL  = "https://arxiv.org/abs/2209.03385"
COLOR_CODE = "24"

FIDUCIAL_SUBMODEL = "van Son (2023)"  # existing row, rate_Gpc3yr = 58.9

REL_COLUMNS = [
    "study_key", "label", "code", "from_submodel", "to_submodel",
    "parameter_family", "parameter", "travel_label",
    "from_value", "to_value", "from_rate_Gpc3yr", "to_rate_Gpc3yr",
    "study_color_code",
]

NOTE_TMPL = (
    "Total (CE + stable mass-transfer channel) local (z~0.2) BH-BH merger "
    "rate density R_0.2 for the {desc} SFRD model variation, from "
    "Fig. 3/4 of van Son et al. (2023). CE channel: {ce} Gpc^-3 yr^-1 "
    "({ce_frac:.0%}); stable MT channel: {stable} Gpc^-3 yr^-1 ({stable_frac:.0%})."
)

# (submodel string, "submodel change 1", sfrd-1 description, notes desc,
#  CE rate, stable rate, total rate)
VARIATIONS = [
    ("vanSon23_omega0_0.70",
     "SFRD model: width of metallicity distribution (omega_0)",
     r"$\omega_0=0.70$ (narrow Z distribution)",
     r"width-of-metallicity-distribution ($\omega_0=0.70$, narrow)",
     "24.2", "6.3", "30.5"),
    ("vanSon23_omega0_2.00",
     "SFRD model: width of metallicity distribution (omega_0)",
     r"$\omega_0=2.00$ (wide Z distribution)",
     r"width-of-metallicity-distribution ($\omega_0=2.00$, wide)",
     "115", "53.1", "168.1"),
    ("vanSon23_omegaz_0.00",
     "SFRD model: redshift evolution of metallicity-distribution width (omega_z)",
     r"$\omega_z=0.00$ (flat width evolution)",
     r"redshift-evolution-of-width ($\omega_z=0.00$, flat)",
     "37.7", "12.4", "50.1"),
    ("vanSon23_omegaz_0.10",
     "SFRD model: redshift evolution of metallicity-distribution width (omega_z)",
     r"$\omega_z=0.10$ (steep width evolution)",
     r"redshift-evolution-of-width ($\omega_z=0.10$, steep)",
     "47.3", "24.1", "71.4"),
    ("vanSon23_mu0_0.007",
     "SFRD model: mean metallicity (mu_0)",
     r"$\mu_0=0.007$ (low mean metallicity)",
     r"mean-metallicity ($\mu_0=0.007$, low)",
     "144.1", "65.4", "209.5"),
    ("vanSon23_mu0_0.035",
     "SFRD model: mean metallicity (mu_0)",
     r"$\mu_0=0.035$ (high mean metallicity)",
     r"mean-metallicity ($\mu_0=0.035$, high)",
     "27.8", "11.1", "38.9"),
    ("vanSon23_muz_0.0",
     "SFRD model: redshift evolution of mean metallicity (mu_z)",
     r"$\mu_z=0.0$ (flat metallicity evolution)",
     r"redshift-evolution-of-mean-metallicity ($\mu_z=0.0$, flat)",
     "38.6", "14", "52.6"),
    ("vanSon23_muz_-0.5",
     "SFRD model: redshift evolution of mean metallicity (mu_z)",
     r"$\mu_z=-0.5$ (steep metallicity evolution)",
     r"redshift-evolution-of-mean-metallicity ($\mu_z=-0.5$, steep)",
     "74.8", "55.4", "130.2"),
    ("vanSon23_alpha_0.0",
     "SFRD model: skewness of metallicity distribution (alpha)",
     r"$\alpha=0.0$ (symmetric Z distribution)",
     r"skewness-of-metallicity-distribution ($\alpha=0.0$, symmetric)",
     "80.2", "38.6", "118.8"),
    ("vanSon23_alpha_-6",
     "SFRD model: skewness of metallicity distribution (alpha)",
     r"$\alpha=-6$ (skewed Z distribution)",
     r"skewness-of-metallicity-distribution ($\alpha=-6$, skewed)",
     "32.6", "12.2", "44.8"),
    ("vanSon23_SFR_MadauFragos2017",
     "SFRD model: overall SFR(z) history",
     r"Madau \& Fragos (2017) SFR(z)",
     r"overall-SFR(z)-history (Madau \& Fragos 2017)",
     "37.2", "17.3", "54.5"),
    ("vanSon23_SFR_UpperLimit",
     "SFRD model: overall SFR(z) history",
     "approximation to the upper-limit SFR(z)",
     "overall-SFR(z)-history (approx. to upper limit)",
     "114.4", "55.6", "170"),
]

# (from_submodel, to_submodel, from_value, to_value, travel_label,
#  from_rate, to_rate)
EDGES = [
    ("vanSon23_omega0_0.70", FIDUCIAL_SUBMODEL,
     r"$\omega_0=0.70$ (narrow Z distribution)", r"$\omega_0=1.13$ (fiducial)",
     r"$\omega_0=1.13$", "30.5", "58.9"),
    (FIDUCIAL_SUBMODEL, "vanSon23_omega0_2.00",
     r"$\omega_0=1.13$ (fiducial)", r"$\omega_0=2.00$ (wide Z distribution)",
     r"$\omega_0=2.00$", "58.9", "168.1"),
    ("vanSon23_omegaz_0.00", "vanSon23_omegaz_0.10",
     r"$\omega_z=0.00$ (flat width evolution)", r"$\omega_z=0.10$ (steep width evolution)",
     r"$\omega_z=0.10$", "50.1", "71.4"),
    ("vanSon23_mu0_0.007", "vanSon23_mu0_0.035",
     r"$\mu_0=0.007$ (low mean metallicity)", r"$\mu_0=0.035$ (high mean metallicity)",
     r"$\mu_0=0.035$", "209.5", "38.9"),
    ("vanSon23_muz_0.0", "vanSon23_muz_-0.5",
     r"$\mu_z=0.0$ (flat metallicity evolution)", r"$\mu_z=-0.5$ (steep metallicity evolution)",
     r"$\mu_z=-0.5$", "52.6", "130.2"),
    ("vanSon23_alpha_0.0", "vanSon23_alpha_-6",
     r"$\alpha=0.0$ (symmetric Z distribution)", r"$\alpha=-6$ (skewed Z distribution)",
     r"$\alpha=-6$", "118.8", "44.8"),
    ("vanSon23_SFR_MadauFragos2017", "vanSon23_SFR_UpperLimit",
     r"Madau \& Fragos (2017) SFR(z)", "approximation to the upper-limit SFR(z)",
     "upper-limit SFR(z)", "54.5", "170"),
]


def load_fiducial_row(columns: list[str]) -> dict:
    with open(IBE_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["study_key"] == STUDY_KEY and row["submodel"] == FIDUCIAL_SUBMODEL:
                return row
    raise RuntimeError("fiducial van Son (2023) row not found")


def build_ibe_rows(fiducial: dict, columns: list[str]) -> list[dict]:
    rows = []
    for submodel, change1, sfrd1, desc, ce, stable, total in VARIATIONS:
        ce_f, stable_f, total_f = float(ce), float(stable), float(total)
        row = dict(fiducial)
        row.update({
            "arxiv_url": ARXIV_URL,
            "rate_Gpc3yr": total,
            "submodel": submodel,
            "submodel string": submodel,
            "notes": NOTE_TMPL.format(
                desc=desc, ce=ce, stable=stable,
                ce_frac=ce_f / total_f, stable_frac=stable_f / total_f,
            ),
            "submodel change 1": change1,
            "submodel change 2": "",
            "sfrd-1": sfrd1,
        })
        rows.append({c: row.get(c, "") for c in columns})
    return rows


def build_edges() -> list[dict]:
    edges = []
    for from_sm, to_sm, from_val, to_val, travel, from_rate, to_rate in EDGES:
        edges.append(dict(
            study_key=STUDY_KEY, label=LABEL, code="COMPAS",
            from_submodel=from_sm, to_submodel=to_sm,
            parameter_family="star formation history", parameter="SFRD_model",
            travel_label=travel,
            from_value=from_val, to_value=to_val,
            from_rate_Gpc3yr=from_rate, to_rate_Gpc3yr=to_rate,
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
    assert len(VARIATIONS) == 12
    assert len(EDGES) == 7

    with open(IBE_CSV, newline="") as f:
        columns = csv.DictReader(f).fieldnames

    fiducial = load_fiducial_row(columns)
    ibe_rows = build_ibe_rows(fiducial, columns)
    edges = build_edges()

    append_csv(IBE_CSV, columns, ibe_rows)
    append_csv(REL_CSV, REL_COLUMNS, edges)

    print(f"Appended {len(ibe_rows)} rows to {IBE_CSV}")
    print(f"Appended {len(edges)} relationship edges to {REL_CSV}")


if __name__ == "__main__":
    main()
