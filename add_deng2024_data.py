#!/usr/bin/env python3
from __future__ import annotations
"""
Add Deng et al. (2024) (arXiv:2402.04658) Galactic DNS (NS-NS) merger rates,
from Appendix A / Table 2 (the model grid behind Fig. 6), to the tidy dataset.

324 models = 3 MT models (I, II, III) x [4 SN models (A, B, C, E) x 4 kick
combinations (k20150, k20300, k40150, k40300) + 1 SN model (D, stochastic)
x 2 kick combinations (k20, k40)] x 6 alpha_CE values (0.1, 0.5, 1, 2, 5, 10).

Appends:
  - 324 rows to isolated-binary-evolution.csv
  - 270 "alpha_CE" relationship-edge chains (0.1 -> 0.5 -> 1 -> 2 -> 5 -> 10,
    5 edges per (MT, SN, kick) combination x 54 combinations)
    to isolated-binary-evolution_relationships.csv.
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"
REL_CSV  = DATA_DIR / "isolated-binary-evolution_relationships.csv"
SRC_CSV  = DATA_DIR / "individual_extracted_data" / "DNS_merger_rates_Fig6_Deng2024.csv"

STUDY_KEY  = "Deng_2024_BSE"
LABEL      = "Deng et al. (2024)"
ARXIV_URL  = "https://arxiv.org/abs/2402.04658"
COLOR_CODE = "18"

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

# Mass-transfer (accretion-efficiency) models, Sec. 2.1.1.
MT_INFO = {
    "I":   "rotation-modulated accretion (Shao & Li 2014): "
           "M2dot = M1dot x (1 - Omega2/Omega_crit)",
    "II":  "half of the transferred mass is accreted by the secondary",
    "III": "near-fully conservative (Hurley et al. 2002): "
           "M2dot = M1dot x min(10 tau_KH,2 / tau_Mdot, 1)",
}
MT_BETA = {"I": "rotation-modulated accretion (Shao & Li 2014)", "II": "0.5", "III": "~1"}
MT_QCRIT = {"I": "q_crit ~ 6", "II": "q_crit ~ 2.5", "III": "q_crit ~ 2.2"}

# SN explosion models, Sec. 2.1.2.
SN_INFO = {
    "A": "Fryer et al. (2012) rapid CCSN; ECSN for M_He,core = 1.83-2.25 Msun",
    "B": "Fryer et al. (2012) rapid CCSN; ECSN for M_He,core = 1.83-2.75 Msun",
    "C": "Fryer et al. (2012) delayed CCSN; ECSN for M_He,core = 1.83-2.25 Msun",
    "D": "Mandel & Muller (2020) stochastic CCSN; ECSN for M_He,core = 1.83-2.25 Msun",
    "E": "Fryer et al. (2012) rapid CCSN; ECSN for M_He,core = 1.83-2.25 Msun; "
         "ultra-stripped SN (USSN) for Case-BB-stripped progenitors, "
         "kick from Andrews & Zezas (2019)",
}
SN_RMP = {
    "A": "Fryer et al. (2012) rapid",
    "B": "Fryer et al. (2012) rapid",
    "C": "Fryer et al. (2012) delayed",
    "D": "Mandel & Muller (2020) stochastic",
    "E": "Fryer et al. (2012) rapid",
}

# Natal-kick combinations, Sec. 2.1.2: sigma_ECSN / sigma_CCSN (km/s, Maxwellian).
KICK_INFO = {
    "k20150": dict(ecsn="20", ccsn="150",
                    text="Maxwellian natal kicks: sigma_ECSN = 20, sigma_CCSN = 150 km/s"),
    "k20300": dict(ecsn="20", ccsn="300",
                    text="Maxwellian natal kicks: sigma_ECSN = 20, sigma_CCSN = 300 km/s"),
    "k40150": dict(ecsn="40", ccsn="150",
                    text="Maxwellian natal kicks: sigma_ECSN = 40, sigma_CCSN = 150 km/s"),
    "k40300": dict(ecsn="40", ccsn="300",
                    text="Maxwellian natal kicks: sigma_ECSN = 40, sigma_CCSN = 300 km/s"),
    "k20":    dict(ecsn="20", ccsn="",
                    text="Maxwellian ECSN kick sigma_ECSN = 20 km/s; "
                         "CCSN kick from Mandel & Muller (2020) stochastic SN model"),
    "k40":    dict(ecsn="40", ccsn="",
                    text="Maxwellian ECSN kick sigma_ECSN = 40 km/s; "
                         "CCSN kick from Mandel & Muller (2020) stochastic SN model"),
}

ALPHA_ORDER = ["0.1", "0.5", "1", "2", "5", "10"]


def submodel_string(mt: str, sn: str, kick: str, alpha: str) -> str:
    return f"D24-MT{mt}-SN{sn}-{kick}-a{alpha}"


def build_ibe_row(src: dict) -> dict:
    mt, sn, kick, alpha = src["MT"], src["SN"], src["kick"], src["alpha_CE"]

    row = {c: "" for c in IBE_COLUMNS}
    notes = (
        f"MT model {mt} ({MT_INFO[mt]}); "
        f"SN model {sn} ({SN_INFO[sn]}); "
        f"{KICK_INFO[kick]['text']}; alpha_CE = {alpha}"
    )
    row.update(dict(
        compact_object_type="NS-NS",
        formation_channel="isolated-binary-evolution",
        study_key=STUDY_KEY,
        label=LABEL,
        first_author="Deng",
        year="2024",
        arxiv_url=ARXIV_URL,
        code="BSE",
        plotting_style="range",
        rate_Gpc3yr=src["merger_rate_Gpc^-3_yr^-1"],
        submodel=src["model"],
        **{"submodel string": submodel_string(mt, sn, kick, alpha)},
        notes=notes,
        sigma_kick=KICK_INFO[kick]["ccsn"],
        sigma_stripped_SN=KICK_INFO[kick]["ecsn"],
        alpha_CE=alpha,
        beta_MT=MT_BETA[mt],
        **{"gamma_AM": "specific angular momentum of accretor (isotropic re-emission)"},
        CE_prescription="standard",
        lambda_CE="Xu & Li (2010a,b); Wang et al. (2016)",
        RMP=SN_RMP[sn],
        MT_stability=f"{MT_QCRIT[mt]} (Shao & Li 2014, Fig. 1)",
        Eddington_limited="TRUE",
        stellar_tracks="SSE",
    ))
    return row


def build_alpha_axis_edges(src_by_combo: dict) -> list[dict]:
    """For each (MT, SN, kick) combination, chain edges along alpha_CE:
    0.1 -> 0.5 -> 1 -> 2 -> 5 -> 10."""
    rows = []
    for (mt, sn, kick), by_alpha in src_by_combo.items():
        for a_from, a_to in zip(ALPHA_ORDER[:-1], ALPHA_ORDER[1:]):
            rows.append(dict(
                study_key=STUDY_KEY, label=LABEL, code="BSE",
                from_submodel=submodel_string(mt, sn, kick, a_from),
                to_submodel=submodel_string(mt, sn, kick, a_to),
                parameter_family="common envelope efficiency (alpha_CE)",
                parameter="alpha_CE",
                travel_label=r"$\alpha_{\rm CE} \uparrow$",
                from_value=a_from,
                to_value=a_to,
                from_rate_Gpc3yr=by_alpha[a_from]["merger_rate_Gpc^-3_yr^-1"],
                to_rate_Gpc3yr=by_alpha[a_to]["merger_rate_Gpc^-3_yr^-1"],
                study_color_code=COLOR_CODE,
            ))
    return rows


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
    src_rows = list(csv.DictReader(open(SRC_CSV)))
    assert len(src_rows) == 324

    src_by_combo = {}
    for r in src_rows:
        key = (r["MT"], r["SN"], r["kick"])
        src_by_combo.setdefault(key, {})[r["alpha_CE"]] = r
    assert len(src_by_combo) == 54
    for key, by_alpha in src_by_combo.items():
        assert set(by_alpha) == set(ALPHA_ORDER), (key, sorted(by_alpha))

    ibe_rows = [build_ibe_row(r) for r in src_rows]
    alpha_edges = build_alpha_axis_edges(src_by_combo)

    append_csv(IBE_CSV, IBE_COLUMNS, ibe_rows)
    append_csv(REL_CSV, REL_COLUMNS, alpha_edges)

    print(f"Appended {len(ibe_rows)} rows to {IBE_CSV}")
    print(f"Appended {len(alpha_edges)} alpha_CE-axis edges to {REL_CSV}")


if __name__ == "__main__":
    main()
