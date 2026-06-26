#!/usr/bin/env python3
from __future__ import annotations
"""
Fix-up for Srinivasan et al. (2023) BPS models 7, 9, 10, 12, 14, 16, 18, 19:
these vary alpha_CE only (lambda_CE stays at its Table A1 default of 0), but
add_srinivasan2023_data.py originally mis-tagged them as joint "alpha &
lambda" variations (since param1/param2 flags were both set in Table A1,
even though the lambda flag's value equals its default).

Re-tags the affected rows as pure "CE efficiency (alpha)" variations:
  - 48 isolated-binary-evolution.csv rows (8 BPS models x 6 SFR/MZR models)
  - 48 isolated-binary-evolution_relationships.csv BPS-axis edges
"""
from pathlib import Path
import csv

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"
REL_CSV  = DATA_DIR / "isolated-binary-evolution_relationships.csv"
SRC_CSV  = DATA_DIR / "individual_extracted_data" / "Srinivasan_2023_fig5_BBH_rates.csv"

SFR_MZR_INFO = {
    "KK04_Ma16": "Ma et al. (2016) fit for Kobulnicky & Kewley (2004) MZR (paper default)",
    "PP04_Ma16": "Ma et al. (2016) fit for Pettini & Pagel (2004) MZR",
    "M09":       "Chruslinska & Nelemans (2019) fit for Mannucci et al. (2009) MZR",
    "KK04":      "Chruslinska & Nelemans (2019) fit for Kobulnicky & Kewley (2004) MZR",
    "PP04":      "Chruslinska & Nelemans (2019) fit for Pettini & Pagel (2004) MZR",
    "T04":       "Chruslinska & Nelemans (2019) fit for Tremonti et al. (2004) MZR",
}


def alpha_only_models() -> dict[int, str]:
    """BPS model index -> alpha_CE value, for models where lambda_CE is
    unchanged (==0, its default) and only alpha_CE varies."""
    src_rows = list(csv.DictReader(open(SRC_CSV)))
    result = {}
    for r in src_rows:
        idx = int(r["bps_model_index"])
        if idx in result:
            continue
        params = []
        if r["param1_flag"]:
            params.append((r["param1_flag"], r["param1_value"]))
        if r["param2_flag"]:
            params.append((r["param2_flag"], r["param2_value"]))
        if len(params) == 2 and {f for f, v in params} == {"alpha", "lambda"}:
            lam = [v for f, v in params if f == "lambda"][0]
            a = [v for f, v in params if f == "alpha"][0]
            if lam == "0":
                result[idx] = a
    return result


def fix_ibe(alpha_for_idx: dict[int, str]) -> int:
    with open(IBE_CSV, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    n_fixed = 0
    for row in rows:
        if row["study_key"] != "Srinivasan_2023_COSMIC":
            continue
        parts = row["submodel string"].split("-")  # e.g. ["S23", "M07", "KK04_Ma16"]
        idx = int(parts[1][1:])
        if idx not in alpha_for_idx:
            continue
        sfr_model = parts[2]
        a = alpha_for_idx[idx]
        assert row["submodel change 1"] == "CE efficiency & binding energy (alpha & lambda)", row
        row["submodel change 1"] = "CE efficiency (alpha)"
        row["notes"] = (
            f"BPS variation: CE efficiency (alpha) -> {a}; "
            f"SFR/MZR model: {sfr_model} ({SFR_MZR_INFO[sfr_model]})"
        )
        n_fixed += 1

    with open(IBE_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return n_fixed


def fix_rel(alpha_for_idx: dict[int, str]) -> int:
    with open(REL_CSV, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    n_fixed = 0
    for row in rows:
        if row["study_key"] != "Srinivasan_2023_COSMIC":
            continue
        if row["parameter"] != "alpha_CE & lambda_CE":
            continue
        parts = row["to_submodel"].split("-")  # e.g. ["S23", "M07", "KK04_Ma16"]
        idx = int(parts[1][1:])
        if idx not in alpha_for_idx:
            continue
        a = alpha_for_idx[idx]
        row["parameter_family"] = "CE efficiency (alpha)"
        row["parameter"] = "alpha_CE"
        row["from_value"] = "1"
        row["to_value"] = a
        row["travel_label"] = a
        n_fixed += 1

    with open(REL_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return n_fixed


def main():
    alpha_for_idx = alpha_only_models()
    assert set(alpha_for_idx) == {7, 9, 10, 12, 14, 16, 18, 19}, alpha_for_idx

    n_ibe = fix_ibe(alpha_for_idx)
    n_rel = fix_rel(alpha_for_idx)

    print(f"Fixed {n_ibe} rows in {IBE_CSV}")
    print(f"Fixed {n_rel} rows in {REL_CSV}")
    assert n_ibe == 48
    assert n_rel == 48


if __name__ == "__main__":
    main()
