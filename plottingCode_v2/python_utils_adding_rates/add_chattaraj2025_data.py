#!/usr/bin/env python3
from __future__ import annotations
"""
Add Chattaraj et al. (2025) (arXiv:2508.00186) "Forming Double Neutron Stars
using Detailed Binary Evolution Models with POSYDON" NS-NS (DNS) local merger
rates, from Table 2 (last column, R(z=0)), to the tidy dataset.

Table 2 lists 25 POSYDON model populations, grouped by three common-envelope
(CE) treatments: "Two Phases StableMT" (MODEL01-14, the default), "Two Phases
Windloss" (MODEL15-18), and "One Phase" (MODEL19-25). Each model is defined by
alpha_CE, the core-envelope-boundary H-fraction (which sets lambda_CE), the
core-collapse/remnant-mass prescription (RMP), and the natal-kick prescription.
Rates are local (z=0) DNS merger rate densities at Solar metallicity.

Per the user's request, the label printed in plots for this study is
"Chattaraj (2025; solar metallicity)".

MODEL01 (alpha_CE=1, 30% H-fraction, Sukhbold 2016 RMP, Hobbs-Maxwellian
kicks, "Two Phases StableMT") matches the paper's stated default model and is
treated as the fiducial.

Appends:
  - 25 rows to isolated-binary-evolution.csv (NS-NS, plotting_style="range").
  - 9 "one-parameter-different-from-fiducial" relationship edges to
    isolated-binary-evolution_relationships.csv:
      - 1 CE efficiency (alpha_CE: 1 -> 3)                  : MODEL01 -> MODEL11
      - 3 remnant mass prescription (RMP)                    : MODEL01 -> MODEL03/05/07
      - 2 natal kick prescription                            : MODEL01 -> MODEL02/09
      - 2 CE treatment (post-CE mass-loss phase)             : MODEL01 -> MODEL15/21
      - 1 CE core-envelope boundary / lambda_CE (H-fraction) : MODEL02 -> MODEL10
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"
REL_CSV  = DATA_DIR / "isolated-binary-evolution_relationships.csv"

STUDY_KEY  = "Chattaraj_2025_POSYDON"
LABEL      = "Chattaraj (2025; solar metallicity)"
ARXIV_URL  = "https://arxiv.org/abs/2508.00186"
COLOR_CODE = "22"

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

TABLE2_NOTE = ("Local (z=0) DNS merger rate density at Solar metallicity, "
               "from Table 2 of Chattaraj et al. (2025)")

SN_RMP = {
    "S16":         "Sukhbold et al. (2016)",
    "PS20":        "Patton & Sukhbold (2020)",
    "F12-delayed": "Fryer et al. (2012) delayed",
    "F12-rapid":   "Fryer et al. (2012) rapid",
}

KICK_INFO = {
    "Hobbs-Maxwellian": dict(
        sigma_kick="265", sigma_stripped_SN="20",
        desc="Maxwellian natal kicks (Hobbs et al. 2005): "
             "sigma_CCSN=265 km/s, sigma_ECSN=20 km/s",
    ),
    "AsymEj": dict(
        sigma_kick="", sigma_stripped_SN="",
        desc="Asymmetric-ejecta (AsymEj) kicks (Janka 2017), "
             "applied to both CCSN and ECSN",
    ),
    "Low Maxwellian": dict(
        sigma_kick="20", sigma_stripped_SN="20",
        desc="Low-dispersion Maxwellian natal kicks: "
             "sigma_CCSN=20 km/s, sigma_ECSN=20 km/s",
    ),
    "Linear": dict(
        sigma_kick="", sigma_stripped_SN="",
        desc="Linear kick prescription (Richards et al. 2023), "
             "applied to both CCSN and ECSN",
    ),
}

CE_GROUP_INFO = {
    "Two Phases StableMT": "two-phase CE: post-CE mass loss via stable, "
                           "non-conservative mass transfer (default)",
    "Two Phases Windloss": "two-phase CE: post-CE mass loss via stellar winds",
    "One Phase":           "one-phase CE: no post-CE mass loss",
}

# (model_id, alpha_CE, H-fraction, SN model, kick model, %CCSN SN1, %CCSN SN2,
#  rate [Gpc^-3 yr^-1], CE group)
TABLE2 = [
    ("01", "1", "30%", "S16",         "Hobbs-Maxwellian", "70%", "53%", "1.19",   "Two Phases StableMT"),
    ("02", "1", "30%", "S16",         "AsymEj",           "99%", "81%", "54.94",  "Two Phases StableMT"),
    ("03", "1", "30%", "PS20",        "Hobbs-Maxwellian", "76%", "65%", "1.75",   "Two Phases StableMT"),
    ("04", "1", "30%", "PS20",        "AsymEj",           "99%", "81%", "36.16",  "Two Phases StableMT"),
    ("05", "1", "30%", "F12-delayed", "Hobbs-Maxwellian", "89%", "78%", "3.43",   "Two Phases StableMT"),
    ("06", "1", "30%", "F12-delayed", "AsymEj",           "99%", "86%", "153.67", "Two Phases StableMT"),
    ("07", "1", "30%", "F12-rapid",   "Hobbs-Maxwellian", "76%", "68%", "1.35",   "Two Phases StableMT"),
    ("08", "1", "30%", "F12-rapid",   "AsymEj",           "99%", "83%", "46.16",  "Two Phases StableMT"),
    ("09", "1", "30%", "S16",         "Low Maxwellian",   "99%", "87%", "359.43", "Two Phases StableMT"),
    ("10", "1", "1%",  "S16",         "AsymEj",           "99%", "82%", "12.33",  "Two Phases StableMT"),
    ("11", "3", "30%", "S16",         "Hobbs-Maxwellian", "89%", "55%", "5.22",   "Two Phases StableMT"),
    ("12", "3", "10%", "S16",         "AsymEj",           "99%", "81%", "155.85", "Two Phases StableMT"),
    ("13", "5", "1%",  "S16",         "AsymEj",           "99%", "80%", "700.54", "Two Phases StableMT"),
    ("14", "5", "1%",  "S16",         "Linear",           "99%", "78%", "117.69", "Two Phases StableMT"),
    ("15", "1", "30%", "S16",         "Hobbs-Maxwellian", "83%", "68%", "3.16",   "Two Phases Windloss"),
    ("16", "1", "30%", "S16",         "AsymEj",           "99%", "81%", "135.82", "Two Phases Windloss"),
    ("17", "3", "10%", "S16",         "AsymEj",           "99%", "82%", "411.65", "Two Phases Windloss"),
    ("18", "3", "10%", "F12-delayed", "Linear",           "99%", "88%", "335.68", "Two Phases Windloss"),
    ("19", "1", "30%", "F12-delayed", "Hobbs-Maxwellian", "75%", "86%", "7.52",   "One Phase"),
    ("20", "1", "30%", "PS20",        "Hobbs-Maxwellian", "64%", "82%", "2.83",   "One Phase"),
    ("21", "1", "30%", "S16",         "Hobbs-Maxwellian", "59%", "83%", "4.29",   "One Phase"),
    ("22", "1", "30%", "S16",         "AsymEj",           "98%", "88%", "276.61", "One Phase"),
    ("23", "3", "10%", "F12-delayed", "Linear",           "97%", "92%", "275.64", "One Phase"),
    ("24", "3", "10%", "S16",         "AsymEj",           "98%", "87%", "451.65", "One Phase"),
    ("25", "5", "1%",  "S16",         "Linear",           "99%", "77%", "117.96", "One Phase"),
]

FIDUCIAL_ID = "01"

# Models reachable from the fiducial (MODEL01) via a single one-parameter
# change -> the parameter family that single change belongs to.
SINGLE_CHANGE = {
    "11": "CE efficiency (alpha)",
    "03": "remnant mass prescription",
    "05": "remnant mass prescription",
    "07": "remnant mass prescription",
    "02": "natal kick prescription",
    "09": "natal kick prescription",
    "15": "CE treatment (post-CE mass loss)",
    "21": "CE treatment (post-CE mass loss)",
}


def submodel_string(model_id: str) -> str:
    return f"Chattaraj25-MODEL{model_id}"


def build_ibe_row(entry: tuple) -> dict:
    model_id, alpha, hfrac, sn, kick, pct1, pct2, rate, group = entry
    kick_info = KICK_INFO[kick]

    if model_id == FIDUCIAL_ID:
        change1 = "fiducial"
    else:
        change1 = SINGLE_CHANGE.get(model_id, "multi-parameter")

    notes = (
        f"POSYDON DNS model MODEL{model_id}: alpha_CE={alpha}, "
        f"core-envelope boundary={hfrac} H-fraction, "
        f"SN/remnant-mass model={SN_RMP[sn]}, "
        f"kick model={kick_info['desc']}, "
        f"CE treatment={group} ({CE_GROUP_INFO[group]}); "
        f"%CCSN (SN1/SN2)={pct1}/{pct2}; {TABLE2_NOTE}."
    )

    row = {c: "" for c in IBE_COLUMNS}
    row.update(dict(
        compact_object_type="NS-NS",
        formation_channel="isolated-binary-evolution",
        study_key=STUDY_KEY,
        label=LABEL,
        first_author="Chattaraj",
        year="2025",
        month="7",
        arxiv_url=ARXIV_URL,
        code="POSYDON",
        plotting_style="range",
        rate_Gpc3yr=rate,
        submodel=f"MODEL{model_id}",
        **{"submodel string": submodel_string(model_id)},
        notes=notes,
        **{"submodel change 1": change1},
        sigma_kick=kick_info["sigma_kick"],
        sigma_stripped_SN=kick_info["sigma_stripped_SN"],
        alpha_CE=alpha,
        CE_prescription=group,
        lambda_CE=f"{hfrac} H-mass-fraction core-envelope boundary",
        RMP=SN_RMP[sn],
        stellar_tracks="POSYDON",
    ))
    return row


def build_edges(rates: dict) -> list[dict]:
    edges = []

    # CE efficiency: alpha_CE 1 -> 3
    edges.append(dict(
        study_key=STUDY_KEY, label=LABEL, code="POSYDON",
        from_submodel=submodel_string("01"), to_submodel=submodel_string("11"),
        parameter_family="CE efficiency (alpha)", parameter="alpha_CE",
        travel_label=r"$\alpha_{\rm CE}=3$",
        from_value="1", to_value="3",
        from_rate_Gpc3yr=rates["01"], to_rate_Gpc3yr=rates["11"],
        study_color_code=COLOR_CODE,
    ))

    # Remnant mass prescription (RMP): S16 -> PS20 / F12-delayed / F12-rapid
    for to_id, sn in (("03", "PS20"), ("05", "F12-delayed"), ("07", "F12-rapid")):
        edges.append(dict(
            study_key=STUDY_KEY, label=LABEL, code="POSYDON",
            from_submodel=submodel_string("01"), to_submodel=submodel_string(to_id),
            parameter_family="remnant mass prescription", parameter="RMP",
            travel_label=SN_RMP[sn],
            from_value=SN_RMP["S16"], to_value=SN_RMP[sn],
            from_rate_Gpc3yr=rates["01"], to_rate_Gpc3yr=rates[to_id],
            study_color_code=COLOR_CODE,
        ))

    # Natal kick prescription: Hobbs-Maxwellian -> AsymEj / Low Maxwellian
    for to_id, kick, travel in (("02", "AsymEj", "AsymEj (Janka 2017)"),
                                 ("09", "Low Maxwellian", r"$\sigma_{\rm CCSN}=20$ km/s")):
        edges.append(dict(
            study_key=STUDY_KEY, label=LABEL, code="POSYDON",
            from_submodel=submodel_string("01"), to_submodel=submodel_string(to_id),
            parameter_family="natal kick prescription", parameter="kick_prescription",
            travel_label=travel,
            from_value="Hobbs-Maxwellian", to_value=kick,
            from_rate_Gpc3yr=rates["01"], to_rate_Gpc3yr=rates[to_id],
            study_color_code=COLOR_CODE,
        ))

    # CE treatment (post-CE mass-loss phase): Two Phases StableMT -> Windloss / One Phase
    for to_id, group, travel in (("15", "Two Phases Windloss", "Windloss"),
                                  ("21", "One Phase", "One Phase")):
        edges.append(dict(
            study_key=STUDY_KEY, label=LABEL, code="POSYDON",
            from_submodel=submodel_string("01"), to_submodel=submodel_string(to_id),
            parameter_family="CE treatment (post-CE mass loss)", parameter="HG_CE_treatment",
            travel_label=travel,
            from_value="Two Phases StableMT", to_value=group,
            from_rate_Gpc3yr=rates["01"], to_rate_Gpc3yr=rates[to_id],
            study_color_code=COLOR_CODE,
        ))

    # CE core-envelope boundary / lambda_CE (H-fraction): 30% -> 1%, at fixed
    # alpha_CE=1, SN=S16, kick=AsymEj (MODEL02 -> MODEL10)
    edges.append(dict(
        study_key=STUDY_KEY, label=LABEL, code="POSYDON",
        from_submodel=submodel_string("02"), to_submodel=submodel_string("10"),
        parameter_family="CE core-envelope boundary (H-fraction)", parameter="lambda_CE",
        travel_label="1% H-fraction",
        from_value="30% H-fraction", to_value="1% H-fraction",
        from_rate_Gpc3yr=rates["02"], to_rate_Gpc3yr=rates["10"],
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
    assert len(TABLE2) == 25

    ibe_rows = [build_ibe_row(entry) for entry in TABLE2]
    rates = {entry[0]: entry[7] for entry in TABLE2}
    edges = build_edges(rates)

    append_csv(IBE_CSV, IBE_COLUMNS, ibe_rows)
    append_csv(REL_CSV, REL_COLUMNS, edges)

    print(f"Appended {len(ibe_rows)} rows to {IBE_CSV}")
    print(f"Appended {len(edges)} relationship edges to {REL_CSV}")


if __name__ == "__main__":
    main()
