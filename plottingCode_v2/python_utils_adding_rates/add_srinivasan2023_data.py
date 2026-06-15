#!/usr/bin/env python3
from __future__ import annotations
"""
Add Srinivasan et al. (2023) (arXiv:2303.04017) BBH local merger rates,
extracted from Figure 5, to the tidy dataset.

240 rates = 40 BPS (binary population synthesis, COSMIC) model variations
(x-axis of Fig. 5, described in Table A1) x 6 SFR/MZR models (KK04_Ma16,
PP04_Ma16, M09, KK04, PP04, T04).

Appends:
  - 240 rows to isolated-binary-evolution.csv
  - 234 "BPS model" relationship edges (default -> each of the other 39
    BPS models, for each of the 6 SFR/MZR models), parameter families
    derived from Table A1
  - 200 "star formation history" relationship edges (KK04_Ma16 -> each of
    the other 5 SFR/MZR models, for each of the 40 BPS models), mirroring
    how Neijssel et al. (2019) SFRD variations are encoded
to isolated-binary-evolution_relationships.csv.
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"
REL_CSV  = DATA_DIR / "isolated-binary-evolution_relationships.csv"
SRC_CSV  = DATA_DIR / "individual_extracted_data" / "Srinivasan_2023_fig5_BBH_rates.csv"

STUDY_KEY  = "Srinivasan_2023_COSMIC"
LABEL      = "Srinivasan et al. (2023)"
ARXIV_URL  = "https://arxiv.org/abs/2303.04017"
COLOR_CODE = "17"

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

# Descriptions of the 6 SFR/MZR models, from Srinivasan et al. (2023) Sec. 2/3.
SFR_MZR_INFO = {
    "KK04_Ma16": "Ma et al. (2016) fit for Kobulnicky & Kewley (2004) MZR (paper default)",
    "PP04_Ma16": "Ma et al. (2016) fit for Pettini & Pagel (2004) MZR",
    "M09":       "Chruslinska & Nelemans (2019) fit for Mannucci et al. (2009) MZR",
    "KK04":      "Chruslinska & Nelemans (2019) fit for Kobulnicky & Kewley (2004) MZR",
    "PP04":      "Chruslinska & Nelemans (2019) fit for Pettini & Pagel (2004) MZR",
    "T04":       "Chruslinska & Nelemans (2019) fit for Tremonti et al. (2004) MZR",
}
SFR_MZR_REF = "KK04_Ma16"

LAMBDA_TEXT = {
    "0": "variable (Claeys et al. 2014), without extra ionization",
    "1": "variable (Claeys et al. 2014), with full ionization",
}

# Per-flag metadata: how each Table A1 flag maps onto IBE columns and
# onto a relationship-edge parameter family/parameter.
FLAG_META = {
    "alpha": dict(
        family="CE efficiency (alpha)", rel_param="alpha_CE",
        from_value="1", to_value=lambda v: v,
    ),
    "lambda": dict(
        family="CE binding energy (lambda)", rel_param="lambda_CE",
        from_value="0",
        to_value=lambda v: "lambda=1 (Claeys et al. 2014, full ionization)" if v == "1"
                            else f"lambda={v}",
    ),
    "qcrit": dict(
        family="CE onset critical mass ratio (q_crit)", rel_param="MT_stability",
        from_value="default",
        to_value=lambda v: {
            "0": "qcflag=0 (Hurley et al. 2002)",
            "1": "qcflag=1 (Hjellming and Webbink 1987 for GB/AGB donors, else Hurley et al. 2002)",
            "3": "qcflag=3 (Hjellming and Webbink 1987 for GB/AGB donors, else Claeys et al. 2014)",
            "4": "qcflag=4 (Belczynski et al. 2008)",
        }[v],
    ),
    "vBH": dict(
        family="BH natal-kick scaling (v_BH)", rel_param="bhflag",
        from_value="default",
        to_value=lambda v: {
            "2": "bhflag=2 (kick scaled by linear-momentum conservation)",
            "3": "bhflag=3 (kick not scaled by fallback)",
        }[v],
    ),
    "MNS-BH": dict(
        family="BH remnant-mass prescription (M_NS-BH)", rel_param="RMP",
        from_value="default",
        to_value=lambda v: {
            "4": "F12 delayed",
            "2": "Belczynski et al. (2008)",
        }[v],
    ),
    "CE_Merger": dict(
        family="CE merger without core-envelope boundary", rel_param="ce_mergeflag",
        from_value="default",
        to_value=lambda v: "ce_mergeflag=0 (no merger)",
    ),
    "Eorb_i": dict(
        family="CE initial orbital energy", rel_param="ceflag",
        from_value="default",
        to_value=lambda v: "ceflag=0 (core mass, Hurley et al. 2002 Eq. 70)",
    ),
    "MLedd": dict(
        family="Eddington-limit wind metallicity dependence (ML_edd)", rel_param="eddlimflag",
        from_value="default",
        to_value=lambda v: "eddlimflag=1 (Giacobbo et al. 2018)",
    ),
    "beta": dict(
        family="wind velocity factor (beta)", rel_param="beta_MT",
        from_value="-1",
        to_value=lambda v: "7" if v == "7.0" else v,
    ),
    "vKick": dict(
        family="natal-kick model (v_Kick)", rel_param="kickflag",
        from_value="default",
        to_value=lambda v: {
            "-1": "kickflag=-1 (Giacobbo and Mapelli 2020, Eq. 1)",
            "-2": "kickflag=-2 (Giacobbo and Mapelli 2020, Eq. 2)",
            "-3": "kickflag=-3 (Bray and Eldridge 2016, Eq. 1)",
        }[v],
    ),
    "sigma": dict(
        family="SN natal-kick dispersion (sigma)", rel_param="sigma_kick",
        from_value="default",
        to_value=lambda v: v,
    ),
    "PISN": dict(
        family="(P)PISN prescription", rel_param="PISN_prescription",
        from_value="default",
        to_value=lambda v: {
            "-3": "pisn=-3 (Woosley 2019)",
            "-1": "pisn=-1 (Spera and Mapelli 2017)",
            "0":  "pisn=0 (none)",
        }[v],
    ),
    "TideST": dict(
        family="tide prescription (Tide_ST)", rel_param="ST_tide",
        from_value="default",
        to_value=lambda v: "ST_tide=0 (Hurley et al. 2002)",
    ),
}


def submodel_string(idx: int, sfr_model: str) -> str:
    return f"S23-M{idx:02d}-{sfr_model}"


def build_ibe_row(src: dict) -> dict:
    idx = int(src["bps_model_index"])
    bps_model = src["bps_model"]
    sfr_model = src["sfr_mzr_model"]
    rate = src["rate_Gpc3yr"]

    params = []
    if src["param1_flag"]:
        params.append((src["param1_flag"], src["param1_value"]))
    if src["param2_flag"]:
        params.append((src["param2_flag"], src["param2_value"]))

    row = {c: "" for c in IBE_COLUMNS}
    row.update(dict(
        compact_object_type="BH-BH",
        formation_channel="isolated-binary-evolution",
        study_key=STUDY_KEY,
        label=LABEL,
        first_author="Srinivasan",
        year="2023",
        arxiv_url=ARXIV_URL,
        code="COSMIC",
        plotting_style="range",
        rate_Gpc3yr=rate,
        submodel=bps_model,
        **{"submodel string": submodel_string(idx, sfr_model)},
        **{"submodel change 2": "star formation history"},
        **{"sfrd-1": sfr_model},
        **{"sfrd-2": SFR_MZR_INFO[sfr_model]},
        stellar_tracks="SSE",
        alpha_CE="1",
        lambda_CE=LAMBDA_TEXT["0"],
        beta_MT="-1",
    ))

    # defaults for the bps-axis "what changed" description
    if not params:
        row["submodel change 1"] = "fiducial"
        change_desc = "fiducial COSMIC/BPS configuration (Table A1 default: alpha=1, lambda=0)"
    elif len(params) == 1:
        flag, value = params[0]
        meta = FLAG_META[flag]
        row["submodel change 1"] = meta["family"]
        change_desc = f"BPS variation: {meta['family']} -> {meta['to_value'](value)}"
        if flag == "alpha":
            row["alpha_CE"] = value
        elif flag == "lambda":
            row["lambda_CE"] = LAMBDA_TEXT[value]
        elif flag == "beta":
            row["beta_MT"] = meta["to_value"](value)
        elif flag == "sigma":
            row["sigma_kick"] = value
            row["sigma_stripped_SN"] = value
        elif flag == "MNS-BH":
            row["RMP"] = meta["to_value"](value)
        elif flag == "PISN":
            row["PISN_prescription"] = meta["to_value"](value)
        elif flag == "qcrit":
            row["MT_stability"] = meta["to_value"](value)
    else:
        (flag1, v1), (flag2, v2) = params
        assert {flag1, flag2} == {"alpha", "lambda"}, params
        a = v1 if flag1 == "alpha" else v2
        l = v1 if flag1 == "lambda" else v2
        if l == FLAG_META["lambda"]["from_value"]:
            # lambda is unchanged from its Table A1 default (0): this is a
            # pure CE-efficiency (alpha) variation, not a joint variation.
            meta = FLAG_META["alpha"]
            row["submodel change 1"] = meta["family"]
            change_desc = f"BPS variation: {meta['family']} -> {meta['to_value'](a)}"
            row["alpha_CE"] = a
        else:
            row["submodel change 1"] = "CE efficiency & binding energy (alpha & lambda)"
            change_desc = f"BPS variation: alpha=1->{a}, lambda=0->{l}"
            row["alpha_CE"] = a
            row["lambda_CE"] = LAMBDA_TEXT[l]

    row["notes"] = f"{change_desc}; SFR/MZR model: {sfr_model} ({SFR_MZR_INFO[sfr_model]})"
    return row


def build_bps_axis_edges(src_by_model: dict) -> list[dict]:
    """default (model 0) -> each of the other 39 BPS models, per SFR/MZR model."""
    rows = []
    sfr_models = list(SFR_MZR_INFO.keys())
    for idx in range(1, 40):
        model0 = src_by_model[0]
        modeli = src_by_model[idx]
        params = []
        if modeli[sfr_models[0]]["param1_flag"]:
            params.append((modeli[sfr_models[0]]["param1_flag"], modeli[sfr_models[0]]["param1_value"]))
        if modeli[sfr_models[0]]["param2_flag"]:
            params.append((modeli[sfr_models[0]]["param2_flag"], modeli[sfr_models[0]]["param2_value"]))

        if len(params) == 1:
            flag, value = params[0]
            meta = FLAG_META[flag]
            parameter_family = meta["family"]
            parameter = meta["rel_param"]
            from_value = meta["from_value"]
            to_value = meta["to_value"](value)
            travel_label = to_value
        else:
            (flag1, v1), (flag2, v2) = params
            a = v1 if flag1 == "alpha" else v2
            l = v1 if flag1 == "lambda" else v2
            if l == FLAG_META["lambda"]["from_value"]:
                # lambda is unchanged from its Table A1 default (0): this is
                # a pure CE-efficiency (alpha) variation, not a joint one.
                meta = FLAG_META["alpha"]
                parameter_family = meta["family"]
                parameter = meta["rel_param"]
                from_value = meta["from_value"]
                to_value = meta["to_value"](a)
                travel_label = to_value
            else:
                parameter_family = "CE efficiency & binding energy (alpha & lambda)"
                parameter = "alpha_CE & lambda_CE"
                from_value = "alpha=1, lambda=0"
                to_value = f"alpha={a}, lambda={l}"
                travel_label = to_value

        for sfr_model in sfr_models:
            rows.append(dict(
                study_key=STUDY_KEY, label=LABEL, code="COSMIC",
                from_submodel=submodel_string(0, sfr_model),
                to_submodel=submodel_string(idx, sfr_model),
                parameter_family=parameter_family,
                parameter=parameter,
                travel_label=travel_label,
                from_value=from_value,
                to_value=to_value,
                from_rate_Gpc3yr=model0[sfr_model]["rate_Gpc3yr"],
                to_rate_Gpc3yr=modeli[sfr_model]["rate_Gpc3yr"],
                study_color_code=COLOR_CODE,
            ))
    return rows


def build_sfr_axis_edges(src_by_model: dict) -> list[dict]:
    """KK04_Ma16 -> each of the other 5 SFR/MZR models, per BPS model."""
    rows = []
    others = [m for m in SFR_MZR_INFO if m != SFR_MZR_REF]
    for idx in range(0, 40):
        ref_rate = src_by_model[idx][SFR_MZR_REF]["rate_Gpc3yr"]
        for sfr_model in others:
            rows.append(dict(
                study_key=STUDY_KEY, label=LABEL, code="COSMIC",
                from_submodel=submodel_string(idx, SFR_MZR_REF),
                to_submodel=submodel_string(idx, sfr_model),
                parameter_family="star formation history",
                parameter="SFRD_model",
                travel_label=SFR_MZR_INFO[sfr_model],
                from_value=SFR_MZR_REF,
                to_value=sfr_model,
                from_rate_Gpc3yr=ref_rate,
                to_rate_Gpc3yr=src_by_model[idx][sfr_model]["rate_Gpc3yr"],
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
    assert len(src_rows) == 240

    src_by_model = {i: {} for i in range(40)}
    for r in src_rows:
        idx = int(r["bps_model_index"])
        src_by_model[idx][r["sfr_mzr_model"]] = r

    ibe_rows = [build_ibe_row(r) for r in src_rows]
    bps_edges = build_bps_axis_edges(src_by_model)
    sfr_edges = build_sfr_axis_edges(src_by_model)

    append_csv(IBE_CSV, IBE_COLUMNS, ibe_rows)
    append_csv(REL_CSV, REL_COLUMNS, bps_edges + sfr_edges)

    print(f"Appended {len(ibe_rows)} rows to {IBE_CSV}")
    print(f"Appended {len(bps_edges)} BPS-axis + {len(sfr_edges)} SFR-axis "
          f"= {len(bps_edges) + len(sfr_edges)} rows to {REL_CSV}")


if __name__ == "__main__":
    main()
