#!/usr/bin/env python3
"""
Update isolated-binary-evolution.csv — Pass 3.

Covers: van Son 2023, Pellouin 2025, Mennekens 2014.
Adds arXiv URLs for all three.
Also adds final parameter notes for remaining incomplete entries.
"""

import pandas as pd
from pathlib import Path

IBE_CSV = Path("Data_Mandel_and_Broekgaarden_2026/isolated-binary-evolution.csv")
df = pd.read_csv(IBE_CSV, dtype=str).fillna("")


def update_study(df, sk, d):
    mask = df["study_key"] == sk
    if mask.sum() == 0:
        print(f"WARNING: {sk} not found")
        return df
    for col, val in d.items():
        if col not in df.columns:
            df[col] = ""
        df.loc[mask, col] = val
    return df


def set_param(df, sk, col, val, note):
    mask = df["study_key"] == sk
    if mask.sum() == 0:
        return df
    nc = col + "_note"
    if col not in df.columns:
        df[col] = ""
    if nc not in df.columns:
        df[nc] = ""
    df.loc[mask, col] = val
    df.loc[mask, nc] = note
    return df


# ── 1. Mennekens & Vanbeveren (2014) ─────────────────────────────────────────
# arXiv:1307.0959, A&A 564 A134, accepted March 2014, published April 2014
SK = "Mennekens_2014_Brusselscode"
df = update_study(df, SK, {
    "year":      "2014",
    "month":     "4",
    "arxiv_url": "https://arxiv.org/abs/1307.0959",
    "parameter_family": "CE efficiency / natal kick / mass transfer efficiency / remnant mass prescription / star formation history",
    "parameter":        "α_CE, σ_kick, β, SFR model, fallback model, initial conditions",
})
df = set_param(df, SK, "sigma_kick",
    "450 (standard); also 265 km/s tested",
    "kick velocity distribution linked to observed pulsar velocity distribution, described with χ² distribution with average velocity 450 km/s; alternative: 265 km/s")
df = set_param(df, SK, "alpha_CE",
    "0.1, 0.5, 1.0, or 5×",
    "α_CE is efficiency of transfer of orbital energy into CE escape energy (0 < α_CE < 1); values 0.1, 0.5, 1.0, and 5× multiplier tested across 23 models")
df = set_param(df, SK, "lambda_CE",
    "Dewi & Tauris (2000) for M<10 M⊙; Xu & Li (2010) for M>10 M⊙",
    "for stars below 10 M⊙ we implement results of Dewi & Tauris (2000), and for more massive stars those for Z=0.02 of Xu & Li (2010)")
df = set_param(df, SK, "CE_prescription",
    "Webbink (1984) alpha-lambda; Dewi & Tauris / Xu & Li lambda",
    "energy balance CE described by Webbink (1984); λ from Dewi & Tauris (2000) (M<10 M⊙) and Xu & Li (2010) (M>10 M⊙)")
df = set_param(df, SK, "beta_MT",
    "0.1, 0.5, or 1.0 (case Br); 1.0 (case A)",
    "case A is treated conservatively (β=1); for case Br: β=0.1, 0.5, or 1.0 (fraction accreted by gainer)")
df = set_param(df, SK, "RMP",
    "Woosley & Weaver (1995) model B; direct collapse for M_ZAMS≥40 M⊙",
    "final CO-core to Fe-core via model B of Woosley & Weaver (1995); stars with initial mass ≥40 M⊙ collapse directly into BH")

# ── 2. van Son et al. (2023) — stable MT channel ─────────────────────────────
# arXiv:2209.13609, "No peaks without valleys: The stable mass transfer channel for GW sources"
# 9 authors: van Son, de Mink, Renzo, Justham, Zapartas, Breivik, Callister, Farr, Conroy
# Published ApJ 948 105 (2023)
SK = "vanSon_2023_COMPAS"
df = update_study(df, SK, {
    "year":      "2023",
    "month":     "4",    # ApJ 948 published April 2023
    "arxiv_url": "https://arxiv.org/abs/2209.13609",
    "parameter_family": "mass transfer efficiency / mass transfer stability",
    "parameter":        "β_acc (MT accretion efficiency), ζ_eff (donor response), q_crit, f_core, SN prescription fmix",
})
df = set_param(df, SK, "sigma_kick",
    "BH: fallback from Fryer et al. (2012) delayed model",
    "BH kicks according to the 'fallback' model from Fryer et al. (2012), where we adopt the proto-NS masses from the DELAYED model")
df = set_param(df, SK, "beta_MT",
    "0.5 (fiducial); 0.0-1.0 (varied)",
    "fraction β_acc of the transferred mass will be accreted by the companion star; first MT: β=0.5 (fiducial); second MT: β=0 (Eddington limited)")
df = set_param(df, SK, "CE_prescription",
    "No CE — stable MT channel only",
    "every mass transfer episode throughout the binary evolution is dynamically stable, and no common envelope occurs; study focuses exclusively on the stable MT channel")
df = set_param(df, SK, "MT_stability",
    "stable only (no CE events)",
    "mass transfer is assumed stable as long as ζ_RL ≤ ζ_⋆; the stable MT channel requires all mass transfer phases to be dynamically stable")
df = set_param(df, SK, "RMP",
    "Fryer et al. (2012) delayed",
    "primary: 'Delayed' model from Fryer et al. (2012) with linear approximation aSN=-0.9, bSN=13.9 M⊙, Mthresh=14.8 M⊙; also Fryer et al. (2022) with fmix variation tested")
df = set_param(df, SK, "Eddington_limited",
    "yes (second mass transfer phase)",
    "during the second mass transfer phase β=0 due to Eddington limited accretion onto the compact object")
df = set_param(df, SK, "stellar_tracks",
    "COMPAS (Hurley et al. 2002); stable MT channel only",
    "COMPAS rapid population synthesis; focus on systems where all three mass transfer phases are dynamically stable")

# ── 3. Pellouin et al. (2025) ─────────────────────────────────────────────────
# arXiv:2411.04563, "Evolutionary tracks of binary neutron star progenitors across cosmic times"
# 3 authors: Pellouin, Dvorkin, Lehoucq
# Published A&A 693 A283 (Jan 2025), accepted Nov 2024
SK = "Pellouin_2025_COSMIC"
df = update_study(df, SK, {
    "year":      "2025",
    "month":     "1",    # A&A 693 Jan 2025
    "arxiv_url": "https://arxiv.org/abs/2411.04563",
    "parameter_family": "initial conditions / CE criterion / star formation history",
    "parameter":        "CE merge flag (cemergeflag), critical mass ratio (qcflag), SFRD model (Vangioni 2015)",
})
df = set_param(df, SK, "sigma_kick",
    "265",
    "for core-collapse SNe, we assume that the natal kicks follow a Maxwellian distribution with a kick velocity dispersion σ_k=265 km⋅s⁻¹")
df = set_param(df, SK, "sigma_stripped_SN",
    "20",
    "for electron-capture SNe, ultra-stripped SNe and accretion-induced collapse (AIC) events, we assume reduced kicks with dispersion σ_k,low=20 km⋅s⁻¹")
df = set_param(df, SK, "alpha_CE",
    "1",
    "in this study, we fix αCE=1 (we do not include external energy terms); variable λ depending on stellar type")
df = set_param(df, SK, "lambda_CE",
    "variable, stellar type dependent",
    "α_CE=1 and a variable λ that depends on the stellar type; stellar companions without a clear core-envelope boundary automatically lead to a merger")
df = set_param(df, SK, "CE_prescription",
    "Webbink (1984) alpha-lambda; α_CE=1, variable λ",
    "α_CE=1, no external energy terms included; λ variable depending on stellar type; stars without clear core-envelope boundary → CE merger")
df = set_param(df, SK, "RMP",
    "Fryer et al. (2012) rapid + Giacobbo & Mapelli (2020) updates",
    "we infer the remnant mass following the rapid mechanism for the SN explosion (Fryer et al. 2012), with updates from Giacobbo & Mapelli (2020); leads to mass gap between NSs and BHs")
df = set_param(df, SK, "stellar_tracks",
    "COSMIC v3.4.0 (BSE/SSE, Hurley et al. 2000/2002) + Vangioni 2015 SFRD",
    "COSMIC version 3.4.0; stellar evolution via SSE; binary interactions via BSE; SFRD from Vangioni et al. (2015); metallicity log-normal with σ=0.2")

# ── 4. ArXiv URL fixes for newly found papers ─────────────────────────────────
df = update_study(df, "Mennekens_2014_Brusselscode", {"arxiv_url": "https://arxiv.org/abs/1307.0959"})
df = update_study(df, "vanSon_2023_COMPAS",          {"arxiv_url": "https://arxiv.org/abs/2209.13609"})
df = update_study(df, "Pellouin_2025_COSMIC",         {"arxiv_url": "https://arxiv.org/abs/2411.04563"})

# ── 5. Missing year/month corrections ─────────────────────────────────────────
# Mennekens 2014: A&A 564 → April 2014 (but "accepted March 2014" per paper text)
df = update_study(df, "Mennekens_2014_Brusselscode", {"year": "2014", "month": "4"})

# Santoliquido 2020: ApJ 898 152 → Aug 2020
df = update_study(df, "Santoliquido_2020_MOBSE", {"year": "2020", "month": "8"})

# Artale 2019 uses TNG and EAGLE in same paper (MNRAS 487 1675, Aug 2019)
for sk in ["Artale_2019_MOBSE", "Artale_2019_MOBSEEAGLE"]:
    df = update_study(df, sk, {"year": "2019", "month": "8"})

# Dominik 2015: ApJ 806 263 → Jun 2015
df = update_study(df, "Dominik_2015_StarTrack", {"year": "2015", "month": "6"})

# Boco 2019: ApJ 881 157 → Aug 2019
df = update_study(df, "Boco_2019_SEVN", {"year": "2019", "month": "8"})

# Zevin 2020: ApJL 899 L1 → Aug 2020 (GW190814 paper)
df = update_study(df, "Zevin_2020_COSMIC", {"year": "2020", "month": "8"})

# Tang 2020: MNRAS 493 L6 → Mar 2020
df = update_study(df, "Tang_2020_BPASS", {"year": "2020", "month": "3"})

# Belczynski 2020: A&A 636 A104 → Apr 2020
df = update_study(df, "Belczynski_2020_StarTrack", {"year": "2020", "month": "4"})

# Ghodla 2021: MNRAS 511 (Feb 2022 issue, submitted May 2021)
df = update_study(df, "Ghodla_2021_BPASS", {"year": "2022", "month": "2"})

# Chu 2021: MNRAS 509 (Jan 2022 issue)
df = update_study(df, "Chu_2021_BSE", {"year": "2022", "month": "1"})

# Mapelli 2021: A&A 653 A23 → Sep 2021
df = update_study(df, "Mapelli_2021_MOBSE", {"year": "2021", "month": "9"})

# Santoliquido 2021: ApJ 921 (Oct 2021? Let's use 10)
df = update_study(df, "Santoliquido_2021_MOBSE", {"year": "2021", "month": "10"})

# ── 6. Add model-level descriptions for some remaining studies ────────────────

# Mennekens 2014 — mark fiducial (model M1 = standard model)
# The paper has 23 models; the "standard model" typically M1 in Brussels code
mask = (df["study_key"] == "Mennekens_2014_Brusselscode") & (df["submodel"].isin(["", "M1"]))
df.loc[mask, "notes"] = "23 models varying: SFR, CE efficiency, MT efficiency, kick velocity, fallback, binary period distribution, LBV scenario, BH kicks"

# van Son 2023 — add submodel descriptions
for subm_pattern, note in [
    ("fiducial", "Fiducial stable-MT: β_acc=0.5, ζ_eff=4.5, Fryer delayed RMP"),
]:
    mask = (df["study_key"] == "vanSon_2023_COMPAS") & (df["submodel"].str.contains(subm_pattern, na=False))
    df.loc[mask, "notes"] = note

# General note for all van Son 2023 models
mask = df["study_key"] == "vanSon_2023_COMPAS"
df.loc[mask & (df["notes"] == ""), "notes"] = (
    "Stable MT channel: no CE events; varies β_acc (0-1), ζ_eff (3.5-6.5), q_crit, f_core, f_disk, RMP parameters (25 models)"
)

# Pellouin 2025 — note about 3 dominant evolutionary tracks
mask = df["study_key"] == "Pellouin_2025_COSMIC"
df.loc[mask & (df["notes"] == ""), "notes"] = (
    "COSMIC v3.4.0; identifies 3 dominant NS-NS evolutionary tracks; varies CE merge flag and critical mass ratio; fiducial: α_CE=1, σ=265 km/s, Fryer rapid RMP"
)

# ── 7. Save ───────────────────────────────────────────────────────────────────
df.to_csv(IBE_CSV, index=False)
print(f"Saved {len(df)} rows, {len(df.columns)} columns to {IBE_CSV}")

# Verification
print("\nArXiv URL check:")
for sk in ["Mennekens_2014_Brusselscode", "vanSon_2023_COMPAS", "Pellouin_2025_COSMIC"]:
    r = df[df.study_key == sk].iloc[0]
    print(f"  {sk}: arxiv={r.arxiv_url}")

print("\nPhysics param check:")
rows = [
    ("Mennekens_2014_Brusselscode", ["sigma_kick", "alpha_CE", "beta_MT"]),
    ("vanSon_2023_COMPAS",          ["CE_prescription", "beta_MT", "MT_stability"]),
    ("Pellouin_2025_COSMIC",        ["sigma_kick", "alpha_CE", "RMP"]),
]
for sk, cols in rows:
    r = df[df.study_key == sk].iloc[0]
    vals = {c: str(getattr(r, c, ""))[:60] for c in cols}
    print(f"  {sk}: {vals}")

print("\nAll 53 study_keys with parameter_family:")
missing = []
for sk in df["study_key"].unique():
    r = df[df.study_key == sk].iloc[0]
    if not r.get("parameter_family", ""):
        missing.append(sk)
if missing:
    print(f"  Still missing parameter_family for: {missing}")
else:
    print("  All studies have parameter_family ✓")
