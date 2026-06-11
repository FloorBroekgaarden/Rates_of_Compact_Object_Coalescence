#!/usr/bin/env python3
"""
Add a "submodel string" column to isolated-binary-evolution.csv.

For most rows this is just a copy of "submodel" (already a unique identifier,
e.g. "Boesky_sigma_750_RMP_M"). For Neijssel et al. (2019) BH-BH rows, the
"submodel" column only says "pessimistic"/"optimistic" — not unique enough to
distinguish the 19 SFRD configurations per CE branch. We derive a unique name
from the sfrd-1/2/3 columns + the CE pessimistic/optimistic flag.
"""
from pathlib import Path
import pandas as pd

IBE_CSV = Path("Data_Mandel_and_Broekgaarden_2026/isolated-binary-evolution.csv")
df = pd.read_csv(IBE_CSV, dtype=str).fillna("")

# Default: submodel string = submodel
df["submodel string"] = df["submodel"]

# ── Neijssel et al. (2019) BH-BH: derive unique names from SFRD + CE flag ────
SFR_CODE = {
    "Madau SFR":          "Madau",
    "Strolger (2004) SFR": "Strolger",
}
MZ_CODE = {
    "Ma (2004) MZ":              "Ma",
    "Langer (2006) MZ":          "Langer",
    "Langer (2006) + offset MZ": "LangerOff",
}
GSMF_CODE = {
    "Panter (2004) GSMF":                  "Panter",
    "Furlong (2015) single Schechter GSMF": "FurlSingle",
    "Furlong (2015) double Schechter GSMF": "FurlDouble",
}
CE_CODE = {"pessimistic": "pess", "optimistic": "opt"}

mask = (df["study_key"] == "Neijssel_2019_COMPAS") & (df["compact_object_type"] == "BH-BH")
n_updated = 0
for idx, row in df[mask].iterrows():
    ce = CE_CODE[row["submodel"]]
    sfrd1 = row["sfrd-1"].strip()
    if sfrd1 == "preferred":
        name = "Neijssel_pess_fiducial" if ce == "pess" else "Neijssel_opt_preferred"
    else:
        sfr  = SFR_CODE[sfrd1]
        mz   = MZ_CODE[row["sfrd-2"].strip()]
        gsmf = GSMF_CODE[row["sfrd-3"].strip()]
        name = f"Neijssel_{ce}_{sfr}_{mz}_{gsmf}"
    df.loc[idx, "submodel string"] = name
    n_updated += 1

# Move "submodel string" to sit right after "submodel"
cols = list(df.columns)
cols.remove("submodel string")
i = cols.index("submodel") + 1
cols = cols[:i] + ["submodel string"] + cols[i:]
df = df[cols]

df.to_csv(IBE_CSV, index=False)
print(f"Updated {n_updated} Neijssel BH-BH rows with derived submodel strings.")
print(f"Saved {len(df)} rows, {len(df.columns)} columns to {IBE_CSV}")

# Sanity check: print the unique submodel strings for Neijssel BH-BH
neij = df[mask][["submodel", "submodel string", "rate_Gpc3yr"]]
print(f"\n{neij['submodel string'].nunique()} unique submodel strings for Neijssel BH-BH:")
print(neij.to_string())
