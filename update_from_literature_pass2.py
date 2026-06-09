#!/usr/bin/env python3
"""
Update isolated-binary-evolution.csv with literature data collected in session 2.

Covers papers: OShaughnessy 2010, Lipunov 2014, Dominik 2015, Lamberts 2016,
Eldridge 2019, Spera 2019, Baibhav 2019, Artale 2019, Boco 2019, Zevin 2020,
Belczynski 2020, Santoliquido 2020, Tang 2020, Mapelli 2021, Santoliquido 2021,
Román-Garza 2021, Chu 2021, Ghodla 2021, Ablimit 2018.

Also adds arXiv URL fixes and model-level notes for various papers.
"""

import re
import pandas as pd
from pathlib import Path

IBE_CSV = Path("Data_Mandel_and_Broekgaarden_2026/isolated-binary-evolution.csv")
df = pd.read_csv(IBE_CSV, dtype=str).fillna("")

# ── Helper functions ──────────────────────────────────────────────────────────

def update_study(df, study_key, col_val_dict):
    mask = df["study_key"] == study_key
    if mask.sum() == 0:
        print(f"WARNING: study_key not found: {study_key}")
        return df
    for col, val in col_val_dict.items():
        if col not in df.columns:
            df[col] = ""
        df.loc[mask, col] = val
    return df


def set_param(df, study_key, col, val, note):
    """Set a parameter value + its _note column for all rows of a study."""
    mask = df["study_key"] == study_key
    if mask.sum() == 0:
        return df
    note_col = col + "_note"
    if col not in df.columns:
        df[col] = ""
    if note_col not in df.columns:
        df[note_col] = ""
    df.loc[mask, col] = val
    df.loc[mask, note_col] = note
    return df


# ── 1. OShaughnessy et al. (2010) ─────────────────────────────────────────────
# 3 authors: O'Shaughnessy, Kalogera, Belczynski → "O'Shaughnessy et al. (2010)" ✓
# ApJ 716 615 (Jun 2010)
SK = "OShaughnessy_2010_StarTrack"
df = update_study(df, SK, {"year": "2010", "month": "6"})
df = set_param(df, SK, "sigma_kick",
    "bimodal Maxwellian",
    "superposition of two independent Maxwellians; StarTrack standard bimodal kick distribution")
df = set_param(df, SK, "CE_prescription",
    "Webbink (1984) alpha-lambda",
    "StarTrack models orbital decay in common-envelope evolution with a single factor αλ")
df = set_param(df, SK, "RMP",
    "Belczynski et al. (2008)",
    "compact remnants more massive than 2.5 M⊙ assumed to form black holes; initial mass from tabulated core mass estimates")

# ── 2. Lipunov & Pruzhinskaya (2014) ─────────────────────────────────────────
# 2 authors → already fixed label to "Lipunov & Pruzhinskaya (2014)"
# MNRAS 440 1193 (2014 May)
SK = "Lipunov_2014_ScenarioMachine"
df = update_study(df, SK, {"year": "2014", "month": "5"})
df = set_param(df, SK, "sigma_kick",
    "100-150",
    "for a kick velocity of 100–150 km s⁻¹ an average NS merger rate is 1/500–1/2000 yr⁻¹ per galaxy")
df = set_param(df, SK, "CE_prescription",
    "Scenario Machine default",
    "common-envelope parameter listed as an uncertain hidden parameter; no explicit α_CE value given")

# ── 3. Dominik et al. (2015) ─────────────────────────────────────────────────
# 9 authors (Dominik, Berti, O'Shaughnessy, Mandel, Belczynski, Fryer, Holz, Bulik, Pannarale)
# ApJ 806 263 (Jun 2015)
SK = "Dominik_2015_StarTrack"
df = update_study(df, SK, {
    "year": "2015", "month": "6",
    "arxiv_url": "https://arxiv.org/abs/1405.7016",
})
df = set_param(df, SK, "sigma_kick",
    "265",
    "Maxwellian distribution of natal kicks for NSs with 1-D root mean square velocity σ=265 km/s")
df = set_param(df, SK, "alpha_CE",
    "1",
    "Nanjing (Xu & Li 2010) λ coefficient in the CE energy balance prescription of Webbink (1984)")
df = set_param(df, SK, "lambda_CE",
    "Nanjing (Xu & Li 2010)",
    "precise value of λ depends on the evolutionary stage of the donor; Xu & Li (2010) prescription")
df = set_param(df, SK, "CE_prescription",
    "Webbink (1984) alpha-lambda, Nanjing lambda, pessimistic",
    "standard model does not allow for CE events with HG donors (pessimistic)")
df = set_param(df, SK, "RMP",
    "Fryer et al. (2012) rapid and delayed",
    "Rapid and Delayed SN engines; v_k=V_max(1-f_fb)")

# Model-level notes for Dominik 2015
dom15_models = {
    "standard":             "Standard StarTrack model: pessimistic CE (no HG CE), σ=265 km/s, rapid SN engine",
    "optimistic_ce":        "Optimistic CE: HG donors allowed to survive CE phase",
    "delayed_sn":           "Delayed SN engine instead of rapid; produces higher-mass BHs",
    "high_bh_kicks":        "High BH natal kicks: same σ=265 km/s without fallback reduction",
}
for subm, note in dom15_models.items():
    mask = (df["study_key"] == SK) & (df["submodel"] == subm)
    if mask.sum() > 0:
        df.loc[mask, "notes"] = note

# ── 4. Lamberts et al. (2016) ────────────────────────────────────────────────
# 4 authors: Lamberts, Garrison-Kimmel, Clausen, Hopkins → "Lamberts et al. (2016)"
# MNRAS 463 L31 (Nov 2016)
SK = "Lamberts_2016_BSE"
df = update_study(df, SK, {"year": "2016", "month": "11"})
df = set_param(df, SK, "sigma_kick",
    "265",
    "kicks drawn from a Maxwellian distribution of width 265 km s⁻¹, reduced according to fallback (Dominik et al. 2013)")
df = set_param(df, SK, "alpha_CE",
    "1",
    "for stars beyond the Hertzsprung gap, we take the common envelope efficiency to be unity")
df = set_param(df, SK, "CE_prescription",
    "Webbink (1984) alpha-lambda, BSE default binding energy",
    "efficiency=1; envelope binding energies from BSE-default, evolutionary-state-dependent formulae")
df = set_param(df, SK, "RMP",
    "Belczynski et al. (2008)",
    "updated remnant mass prescriptions taken from Belczynski et al. (2008)")
df = set_param(df, SK, "stellar_tracks",
    "BSE (Hurley et al. 2002) + FIRE cosmological sim",
    "mass-metallicity relation from Ma et al. (2016) using FIRE high-resolution cosmological zoom-in simulations")

# ── 5. Eldridge et al. (2019) ────────────────────────────────────────────────
# 3 authors: Eldridge, Stanway, Tang → "Eldridge et al. (2019)" ✓
# MNRAS 482 870 (Jan 2019) — accepted 2018 October 3
SK = "Eldridge_2019_BPASS"
df = update_study(df, SK, {"year": "2019", "month": "1"})
df = set_param(df, SK, "sigma_kick",
    "265",
    "we use a Maxwell-Boltzmann distribution with a velocity of 265 km s⁻¹ (Hobbs et al. 2005)")
df = set_param(df, SK, "CE_prescription",
    "BPASS energy conservation; effective α_CE λ = 2-100",
    "remove the envelope as quickly as possible, also remove its binding energy from the binary orbit; effective αCE λ ranging from 100 (small q) to ~2 (q≈1)")
df = set_param(df, SK, "stellar_tracks",
    "BPASS v2.2 (Moe & Di Stefano 2017 initial distributions)",
    "custom detailed theoretical stellar evolution tracks at 13 metallicities; BPASS v2.2 uses Moe & Di Stefano (2017) binary parameters")
df = set_param(df, SK, "PISN_prescription",
    "Farmer et al. (2019)",
    "PISN prescription from Farmer et al. (2019)")
# Models
for subm, note in [
    ("v2.2_Hobbs",      "BPASS v2.2 + Hobbs et al. (2005) kick prescription (fiducial)"),
    ("v2.1_Hobbs",      "BPASS v2.1 + Hobbs et al. (2005) kicks; older stellar models"),
    ("v2.2_BrayEldridge","BPASS v2.2 + Bray & Eldridge (2018) mass-dependent kick prescription"),
]:
    mask = (df["study_key"] == SK) & (df["submodel"] == subm)
    if mask.sum() > 0:
        df.loc[mask, "notes"] = note

# ── 6. Spera et al. (2019) ───────────────────────────────────────────────────
# 6 authors: Spera, Mapelli, Giacobbo, Trani, Bressan, Costa → "Spera et al. (2019)" ✓
# MNRAS 485 889 (May 2019)
SK = "Spera_2019_SEVN"
df = update_study(df, SK, {"year": "2019", "month": "5"})
df = set_param(df, SK, "sigma_kick",
    "265",
    "V_kick=(1-f_fb)W_kick, where W_kick is randomly drawn from the Maxwellian distribution derived by Hobbs et al. (2005)")
df = set_param(df, SK, "alpha_CE",
    "1",
    "(α,λ)=(1,0.1) for common envelope phase; formalism follows Webbink (1984)")
df = set_param(df, SK, "lambda_CE",
    "0.1",
    "(α,λ)=(1,0.1) for common envelope phase; Webbink (1984), de Kool (1992), Ivanova et al. (2013)")
df = set_param(df, SK, "CE_prescription",
    "Webbink (1984) alpha-lambda",
    "Webbink (1984), de Kool (1992), Ivanova et al. (2013)")
df = set_param(df, SK, "RMP",
    "multiple: Fryer et al. (2012) rapid/delayed, Belczynski et al. (2010) StarTrack, O'Connor & Ott (2011), Ertl et al. (2016)",
    "rapid core-collapse (default), delayed, StarTrack, compactness parameter O'Connor & Ott, two-parameter Ertl et al.")
df = set_param(df, SK, "PISN_prescription",
    "Spera & Mapelli (2017)",
    "PISNe and PPISNe included in SEVN following the prescriptions discussed in Spera & Mapelli (2017)")
df = set_param(df, SK, "stellar_tracks",
    "SEVN + PARSEC/PADOVA stellar tracks",
    "SEVN stellar evolution with PARSEC/PADOVA stellar evolution tracks")

# ── 7. Baibhav et al. (2019) ─────────────────────────────────────────────────
# 7 authors: Baibhav, Berti, Gerosa, Mapelli, Giacobbo, Bouffanais, Di Carlo
# PRD 100 064060 (Sep 2019)
SK = "Baibhav_2019_MOBSE"
df = update_study(df, SK, {"year": "2019", "month": "9"})
df = set_param(df, SK, "sigma_kick",
    "265 or 15",
    "kicks extracted from a Maxwellian distribution with root-mean-square speed σ_CCSN=265 km/s (standard) or 15 km/s (low-kick models)")
df = set_param(df, SK, "alpha_CE",
    "1, 3, or 5",
    "common envelope phase treated using αλ formalism; α ∈ {1, 3, 5} tested")
df = set_param(df, SK, "lambda_CE",
    "Claeys et al. (2014)",
    "λ computed using the prescriptions derived in Claeys et al. (2014)")
df = set_param(df, SK, "CE_prescription",
    "Webbink (1984) alpha-lambda, Claeys lambda",
    "αλ formalism; α quantifies efficiency of energy transfer; λ from Claeys et al. (2014)")
df = set_param(df, SK, "RMP",
    "Fryer et al. (2012) rapid",
    "MOBSE predicts NS masses from 1.1 to 2 M⊙; BH kicks reduced via fallback v_BH=(1-f_fb)v_NS")
# Model labels
baibhav_models = {
    "α1":    ("1",  "265", "α=1, σ=265 km/s (standard kicks)"),
    "α3":    ("3",  "265", "α=3, σ=265 km/s"),
    "α5":    ("5",  "265", "α=5, σ=265 km/s"),
    "CC15α1":("1",  "15",  "α=1, σ=15 km/s (low kick)"),
    "CC15α3":("3",  "15",  "α=3, σ=15 km/s"),
    "CC15α5":("5",  "15",  "α=5, σ=15 km/s"),
}
for subm, (alpha, sigma, note) in baibhav_models.items():
    mask = (df["study_key"] == SK) & (df["submodel"] == subm)
    if mask.sum() > 0:
        df.loc[mask, "alpha_CE"] = alpha
        df.loc[mask, "sigma_kick"] = sigma
        df.loc[mask, "notes"] = note

# ── 8. Artale et al. (2019) — EAGLE and TNG ───────────────────────────────────
# 9 authors (Artale, Mapelli, Giacobbo, Sabha, Spera, Santoliquido, Bressan, ...)
# MNRAS 487 1675 (Aug 2019)
for SK in ["Artale_2019_MOBSE", "Artale_2019_MOBSEEAGLE"]:
    df = update_study(df, SK, {"year": "2019", "month": "8"})
    df = set_param(df, SK, "sigma_kick",
        "15",
        "low SN kicks using a Maxwellian curve with root mean square σ=15 km s⁻¹ (CC15α5 model from Giacobbo & Mapelli 2018)")
    df = set_param(df, SK, "alpha_CE",
        "5",
        "high efficiency of common-envelope ejection (α=5) in the CC15α5 MOBSE model")
    df = set_param(df, SK, "CE_prescription",
        "Webbink (1984) alpha-lambda, Claeys lambda",
        "CC15α5 model from Giacobbo & Mapelli (2018): αλ formalism, α=5, λ from Claeys et al. (2014)")
    df = set_param(df, SK, "RMP",
        "Fryer et al. (2012) rapid",
        "rapid core-collapse SN model from Fryer et al. (2012); direct collapse for M_CO>~11 M⊙")

# Distinguish the cosmological simulation for each
df = set_param(df, "Artale_2019_MOBSE", "stellar_tracks",
    "MOBSE + IllustrisTNG cosmological simulation",
    "MOBSE binary population synthesis combined with IllustrisTNG cosmological simulation (TNG300-1)")
df = set_param(df, "Artale_2019_MOBSEEAGLE", "stellar_tracks",
    "MOBSE + EAGLE cosmological simulation",
    "MOBSE binary population synthesis combined with EAGLE cosmological simulation (RecalL0025N0752 run)")

# ── 9. Boco et al. (2019) ────────────────────────────────────────────────────
# 6 authors: Boco, Lapi, Goswami, Perrotta, Baccigalupi, Danese → "Boco et al. (2019)" ✓
# ApJ 881 157 (Aug 2019)
SK = "Boco_2019_SEVN"
df = update_study(df, SK, {"year": "2019", "month": "8"})
df = set_param(df, SK, "RMP",
    "Spera & Mapelli (2017) delayed",
    "metallicity-dependent relationships m_•(m_⋆,Z) from Spera & Mapelli (2017) using delayed SN engine with (P)PSNe included")
df = set_param(df, SK, "PISN_prescription",
    "Spera & Mapelli (2017) (P)PSNe",
    "(P)PSNe included with log-normal dispersion σ_log m_•=0.1 dex following Spera & Mapelli (2017)")
df = set_param(df, SK, "stellar_tracks",
    "SEVN + Spera & Mapelli (2017) stellar evolution",
    "SEVN code with Spera & Mapelli (2017) stellar evolution tracks and mass prescriptions")
# Boco 2019 varies delay time distribution and SFRD — note this in parameter_family
df = update_study(df, SK, {
    "parameter_family": "star formation history / metallicity / delay time distribution",
    "parameter": "delay time distribution exponent, SFRD, IMF",
})

# ── 10. Zevin et al. (2020) ──────────────────────────────────────────────────
# 4 authors: Zevin, Spera, Berry, Kalogera → "Zevin et al. (2020)" ✓
# ApJL 899 L1 (Aug 2020)
SK = "Zevin_2020_COSMIC"
df = update_study(df, SK, {"year": "2020", "month": "8"})
df = set_param(df, SK, "sigma_kick",
    "265 (bimodal) or Giacobbo & Mapelli (2020)",
    "iron core-collapse SNe kicks drawn from Maxwellian with σ=265 km s⁻¹; ECSN and ultra-stripped SNe: σ=20 km s⁻¹")
df = set_param(df, SK, "sigma_stripped_SN",
    "20",
    "electron-capture SNe and ultra-stripped SNe given weaker kicks, σ=20 km s⁻¹")
df = set_param(df, SK, "alpha_CE",
    "1 or 5",
    "CE efficiency parameterized as in Webbink (1984) and de Kool (1990); tested α=1.0 and α=5.0")
df = set_param(df, SK, "lambda_CE",
    "Claeys et al. (2014)",
    "variable prescription for the envelope binding energy factor λ (Claeys et al., 2014)")
df = set_param(df, SK, "CE_prescription",
    "Webbink (1984) alpha-lambda, optimistic/pessimistic",
    "CE efficiency from Webbink (1984); optimistic (HG donors survive) and pessimistic (HG donors merge)")
df = set_param(df, SK, "RMP",
    "Fryer et al. (2012) rapid and delayed",
    "both Rapid and Delayed SN prescriptions from Fryer et al. (2012) tested; also modified to cap neutronization at 10% iron-core mass")
df = set_param(df, SK, "stellar_tracks",
    "COSMIC (BSE, Hurley et al. 2002)",
    "COSMIC population synthesis code using Hurley et al. (2002) BSE formulae")
# 32 models: initial conditions × α_CE × CE survival × RMP × kicks
df = update_study(df, SK, {
    "parameter_family": "initial conditions / CE efficiency / natal kick / remnant mass prescription",
    "parameter": "initial binary distributions (Sana vs Moe), α_CE, CE optimistic/pessimistic, RMP, kick prescription",
})

# ── 11. Belczynski et al. (2020) ─────────────────────────────────────────────
# 41 authors — "Belczynski et al. (2020)" ✓
# A&A 636 A104 (Apr 2020)
SK = "Belczynski_2020_StarTrack"
df = update_study(df, SK, {
    "year": "2020", "month": "4",
    "arxiv_url": "https://arxiv.org/abs/1706.07053",
    "parameter_family": "angular momentum transport / remnant mass prescription / natal kick / stellar winds / star formation history",
    "parameter": "AM transport (Geneva/MESA/Fuller), PPSN prescription, σ_kick, stellar wind efficiency, metallicity evolution",
})
df = set_param(df, SK, "sigma_kick",
    "265, 130, or 70",
    "high NS kicks σ=265 km s⁻¹ with fallback; small BH/NS kicks σ=70 km s⁻¹; intermediate σ=130 km s⁻¹")
df = set_param(df, SK, "CE_prescription",
    "Webbink (1984) alpha-lambda, 5% or 10% Bondi-Hoyle accretion in CE",
    "5% Bondi-Hoyle accretion onto NS/BH in CE (models M30+); 10% Bondi-Hoyle in earlier models")
df = set_param(df, SK, "RMP",
    "direct collapse with metallicity-dependent PPSN",
    "MBH=(1-f_neu)Mstar; PPSN models use metallicity-dependent He-core mass relationships; rapid mass-gap SN engine")
df = set_param(df, SK, "PISN_prescription",
    "Woosley & Heger (2021) and variants; strong/moderate/weak PPSN mass loss",
    "PPSN mass loss: strong, moderate, weak; metallicity-dependent He-core mass relationships (equations 7-9)")
df = set_param(df, SK, "stellar_tracks",
    "StarTrack + Geneva/MESA/Fuller angular momentum transport",
    "three AM transport models: Geneva (mild), MESA (efficient), Fuller et al. (super-efficient rotation)")
# 14 model notes
belc20_models = {
    "M10": "Fiducial-like: AM transport=Geneva (mild), moderate PPSN, high kicks σ=265, efficient BH accretion, Madau & Dickinson (2014) SFRD",
    "M13": "AM=Geneva, moderate PPSN, high kicks σ=265, inefficient BH accretion",
    "M20": "AM=MESA (efficient), moderate PPSN, high kicks σ=265, efficient BH accretion",
    "M23": "AM=MESA, moderate PPSN, high kicks σ=265, inefficient BH accretion",
    "M25": "AM=MESA, strong PPSN, high kicks σ=265",
    "M26": "AM=MESA, weak PPSN (no PPSN), high kicks σ=265",
    "M30": "AM=MESA, moderate PPSN, small kicks σ=70 km/s",
    "M33": "AM=MESA, moderate PPSN, intermediate kicks σ=130 km/s",
    "M35": "AM=MESA, moderate PPSN, σ=265, reduced stellar winds (×0.7)",
    "M40": "AM=Fuller (super-efficient), moderate PPSN, high kicks σ=265",
    "M43": "AM=Fuller, moderate PPSN, σ=265, inefficient BH accretion",
    "M50": "AM=MESA, moderate PPSN, σ=265, Madau & Fragos (2017) SFRD",
    "M60": "AM=MESA, moderate PPSN, σ=265, BH spin from natal kicks",
    "M70": "AM=MESA, moderate PPSN, σ=265, Wolf-Rayet mass loss reduced",
}
for subm, note in belc20_models.items():
    mask = (df["study_key"] == SK) & (df["submodel"] == subm)
    if mask.sum() > 0:
        df.loc[mask, "notes"] = note

# ── 12. Santoliquido et al. (2020) ───────────────────────────────────────────
# 9 authors: Santoliquido, Mapelli, Bouffanais, Giacobbo, Di Carlo, Rastello, Artale, Ballone
# ApJ 898 152 (Aug 2020)
SK = "Santoliquido_2020_MOBSE"
df = update_study(df, SK, {"year": "2020", "month": "8"})
df = set_param(df, SK, "sigma_kick",
    "15",
    "natal kicks randomly drawn from a Maxwellian velocity distribution, σ=15 km s⁻¹ for neutron stars (CC15α5 MOBSE model)")
df = set_param(df, SK, "alpha_CE",
    "5",
    "we assume α=5, as suggested by recent studies (CC15α5 model)")
df = set_param(df, SK, "CE_prescription",
    "Webbink (1984) alpha-lambda, Claeys lambda",
    "αλ formalism; α=5, λ from Claeys et al. (2014)")
df = set_param(df, SK, "RMP",
    "Fryer et al. (2012); PISN Woosley",
    "stars with He core 64-135 M⊙ disrupted by pair instability; He 32-64 M⊙ → PPISN; direct collapse for M_CO>11 M⊙")
df = set_param(df, SK, "stellar_tracks",
    "MOBSE + Madau & Fragos (2017) SFRD",
    "SFRD: Madau & Fragos (2017) fitting formula; metallicity: De Cia et al. (2018) damped Ly-α, rescaled to Z(z=0)=(1.04±0.14)Z⊙")

# ── 13. Tang et al. (2020) ───────────────────────────────────────────────────
# 4 authors: Tang, Eldridge, Stanway, Bray → "Tang et al. (2020)" ✓
# MNRAS 493 L6 (Mar 2020)
SK = "Tang_2020_BPASS"
df = update_study(df, SK, {"year": "2020", "month": "3"})
df = set_param(df, SK, "sigma_kick",
    "265 (Hobbs) or Bray & Eldridge (2018)",
    "Hobbs et al. (2005) Maxwell-Boltzmann σ=265 km/s; or Bray & Eldridge (2018) vkick2D=100-20+30(Mejecta/Mremnant)-170")
df = set_param(df, SK, "stellar_tracks",
    "BPASS v2.1 or v2.2 (Moe & Di Stefano 2017)",
    "BPASS v2.1 (flat q, log P distributions) or v2.2 (Moe & Di Stefano 2017 binary parameter distributions)")
df = set_param(df, SK, "CE_prescription",
    "BPASS energy conservation",
    "BPASS removes envelope binding energy from orbital energy; no explicit α_CE parameter stated")
# Models
for subm, note in [
    ("v2.1_Hobbs",       "BPASS v2.1 + Hobbs kicks (σ=265 km/s)"),
    ("v2.2_Hobbs",       "BPASS v2.2 + Hobbs kicks (σ=265 km/s), Moe & Di Stefano 2017 initial distributions"),
    ("v2.2_BrayEldridge","BPASS v2.2 + Bray & Eldridge (2018) mass-dependent kick prescription"),
]:
    mask = (df["study_key"] == SK) & (df["submodel"] == subm)
    if mask.sum() > 0:
        df.loc[mask, "notes"] = note

# ── 14. Mapelli et al. (2021) ────────────────────────────────────────────────
# 6 authors: Mapelli, Santoliquido, Bouffanais, Arca Sedda, Artale, Ballone
# A&A 653 A23 (Sep 2021)
SK = "Mapelli_2021_MOBSE"
df = update_study(df, SK, {"year": "2021", "month": "9"})
df = set_param(df, SK, "alpha_CE",
    "1, 5, or 10",
    "we parametrize common envelope evolution with the parameter α; here we consider α=1, 5, 10")
df = set_param(df, SK, "beta_MT",
    "0.1, 0.5, or 1.0",
    "accretion rate ṁ_a = {fMT|ṁ_d| if non-degenerate accretor; min(fMT|ṁ_d|,ṁ_Edd) otherwise}; fMT ∈ (0,1]")
df = set_param(df, SK, "CE_prescription",
    "Webbink (1984) alpha-lambda",
    "large values of α mean the envelope is easily ejected; tested α=1, 5, 10")
df = set_param(df, SK, "RMP",
    "Fryer et al. (2012); PPISN αP correction",
    "stars undergo PPISN (32≤mHe≤64); final mass ≈ 0.95 × total merging BH mass; αP≤1 pulsation parameter")
df = set_param(df, SK, "PISN_prescription",
    "PPISN with αP mass reduction",
    "stars with 32≤mHe≤64 M⊙ undergo pulsational pair instability; mBH=αP × mno,PPI")
df = set_param(df, SK, "stellar_tracks",
    "MOBSE + Giacobbo & Mapelli (2020) kick prescription",
    "MOBSE code; natal kicks from Giacobbo & Mapelli (2020) prescription (equation 7, relativistic)")
# Model notes (9 primary models: α×fMT)
for alpha in ["1", "5", "10"]:
    for fmt in ["01", "05", "1"]:
        subm = f"A{alpha}F{fmt}"
        note = f"α_CE={alpha}, f_MT={fmt.replace('0', '0.')}0 (MT efficiency)"
        mask = (df["study_key"] == SK) & (df["submodel"] == subm)
        if mask.sum() > 0:
            df.loc[mask, "alpha_CE"] = alpha
            df.loc[mask, "beta_MT"] = fmt.replace("01", "0.1").replace("05", "0.5")
            df.loc[mask, "notes"] = note

# ── 15. Santoliquido et al. (2021) ───────────────────────────────────────────
# 5 authors: Santoliquido, Mapelli, Giacobbo, Bouffanais, Artale
# ApJ 921 (Sep 2021)
SK = "Santoliquido_2021_MOBSE"
df = update_study(df, SK, {"year": "2021", "month": "9"})
df = set_param(df, SK, "sigma_kick",
    "265 (fiducial); also 150, 50",
    "f_H05 drawn from Maxwellian with σ₁D=265 km s⁻¹ (Hobbs et al., 2005); also σ=150 and 50 km/s tested")
df = set_param(df, SK, "alpha_CE",
    "varies: 0.5-10 (32 models)",
    "α_CE can assume values from 0.5 to 10; λ_CE derived as described in Claeys et al. (2014)")
df = set_param(df, SK, "lambda_CE",
    "Claeys et al. (2014)",
    "λ_CE derived following Claeys et al. (2014)")
df = set_param(df, SK, "CE_prescription",
    "Webbink (1984) alpha-lambda, Claeys lambda",
    "αλ formalism with λ from Claeys et al. (2014); α ∈ {0.5,1,2,3,5,7,10}")
df = set_param(df, SK, "stellar_tracks",
    "MOBSE + Madau & Fragos (2017) SFRD",
    "SFRD: Madau & Fragos (2017) ψ(z)=0.01(1+z)^2.6/[1+((1+z)/3.2)^6.2] M⊙ Mpc⁻³ yr⁻¹")
df = update_study(df, SK, {
    "parameter_family": "CE efficiency / natal kick / remnant mass prescription / mass transfer efficiency / initial conditions",
    "parameter": "α_CE, σ_kick, SN model (rapid/delayed), f_MT, IMF slope",
})

# ── 16. Román-Garza et al. (2021) ────────────────────────────────────────────
# 13 authors — "Román-Garza et al. (2021)" ✓
# ApJ 927 (published 2022 Mar): ApJS published 2022?
# arXiv:2012.02274 → ApJL? Accept date unclear; published ~2022 Mar
for SK in ["RomnGarza_2021_POSYDON", "RomanGarza_2021_POSYDON"]:
    df = update_study(df, SK, {"year": "2022", "month": "3"})
    df = set_param(df, SK, "sigma_kick",
        "265",
        "σ_FeCCSN=265 km/s for Fe core-collapse SN; σ_ECSN=20 km/s for electron-capture SN")
    df = set_param(df, SK, "sigma_stripped_SN",
        "20",
        "σ_ECSN=20 km/s for kicks imparted on NS formed from ECSN")
    df = set_param(df, SK, "alpha_CE",
        "1",
        "α_CE=1 and λ_CE fits from Claeys et al. (2014) without taking into account the ionization energy of the envelope")
    df = set_param(df, SK, "lambda_CE",
        "Claeys et al. (2014)",
        "λ_CE fits from Claeys et al. (2014) without including ionization energy")
    df = set_param(df, SK, "CE_prescription",
        "Webbink (1984) alpha-lambda, Claeys lambda",
        "α_CE=1, λ from Claeys et al. (2014)")
    df = set_param(df, SK, "RMP",
        "Sukhbold et al. (2016) N20 engine; also Fryer Rapid/Delayed",
        "primary: N20 engine of Sukhbold et al. (2016) with nearest-neighbor classification; also Rapid and Delayed tested")
    df = set_param(df, SK, "stellar_tracks",
        "POSYDON framework (MESA binary evolution grids)",
        "POSYDON allows coupling of parametric population synthesis codes with models for different evolutionary phases")
    df = update_study(df, SK, {
        "parameter_family": "remnant mass prescription / natal kick",
        "parameter": "SN engine (N20/Rapid/Delayed), ECSN kick model, NS radius",
    })

# ── 17. Chu et al. (2021) ────────────────────────────────────────────────────
# 3 authors: Chu, Yu, Lu → "Chu et al. (2021)" ✓
# MNRAS 509 (Jan 2022 issue)
SK = "Chu_2021_BSE"
df = update_study(df, SK, {"year": "2022", "month": "1"})
df = set_param(df, SK, "sigma_kick",
    "190 (standard); also 30 km/s (low) and bimodal 190/30",
    "we take standard value of σ_k=190 km s⁻¹ (Hansen & Phinney 1997); also σ_k=30 km s⁻¹ (low-kick) and bimodal models")
df = set_param(df, SK, "alpha_CE",
    "0.1, 1.0, or 10.0 (α-formalism); or γ-formalism",
    "α-formalism: αCE=0.1, 1.0, 10.0 with λ=0.5; γ-formalism: J_i-J_f/J_i=γ(m1-m1c)/(m1+m2) with γ=1.1,1.3,1.5,1.7")
df = set_param(df, SK, "lambda_CE",
    "0.5",
    "λ=0.5 in α-formalism models")
df = set_param(df, SK, "CE_prescription",
    "Webbink (1984) alpha-lambda (λ=0.5) or gamma angular momentum formalism",
    "α-formalism or γ-formalism; α ∈ {0.1,1,10}, γ ∈ {1.1,1.3,1.5,1.7}; β_eject=0.6,0.8,0.9")
df = set_param(df, SK, "RMP",
    "mNS = 0.89 + 0.23mc,SN",
    "mNS=0.89+0.23mc,SN where mc,SN is CO-core mass at supernova explosion")
df = set_param(df, SK, "beta_MT",
    "0.6-0.9",
    "β=mNS,1+mNS,2/(mNS,1+mHe) = 0.9, 0.8, 0.6 (heavily-stripped, stripped, slightly-stripped)")
df = update_study(df, SK, {
    "parameter_family": "common envelope / natal kick / mass transfer stability",
    "parameter": "α_CE or γ_AM, σ_kick, mass ejection fraction β",
})

# ── 18. Ghodla et al. (2021) ────────────────────────────────────────────────
# 5 authors: Ghodla, van Zeist, Eldridge, Stevance, Stanway → "Ghodla et al. (2021)" ✓
# MNRAS (accepted ~2022)
SK = "Ghodla_2021_BPASS"
df = update_study(df, SK, {"year": "2022", "month": "1"})
df = set_param(df, SK, "sigma_kick",
    "265 (Hobbs) or Bray & Eldridge (2018)",
    "Maxwell-Boltzmann distribution with 1-dimensional rms speed of 265 km/s (Hobbs et al. 2005); alternative: Bray & Eldridge (2018) vkick=100(M_ejecta/M_remnant)-170(1.4/M_remnant)")
df = set_param(df, SK, "CE_prescription",
    "BPASS energy conservation",
    "BPASS implicit CE treatment; no explicit α_CE stated; prior BPASS work referenced")
df = set_param(df, SK, "stellar_tracks",
    "BPASS v2.2 + updated MT rejuvenation",
    "updated rejuvenation during mass transfer onto secondary stars; improved GW merger time calculation via full Peters (1964) orbital evolution")
df = set_param(df, SK, "RMP",
    "multiple: Standard binding energy, AlwaysNS, MCO,final, Fryer et al. (2012) rapid",
    "4 remnant mass schemes tested: Standard (binding energy), AlwaysNS (all 1.4 M⊙), MCO,final (CO core mass), FryerRapid (Fryer+2012)")
df = update_study(df, SK, {
    "parameter_family": "remnant mass prescription / natal kick",
    "parameter": "RMP scheme (Standard/AlwaysNS/MCO,final/FryerRapid), kick prescription (Hobbs/Bray)",
})

# ── 19. Ablimit & Maeda (2018) ───────────────────────────────────────────────
# 2 authors → "Ablimit & Maeda (2018)" ✓ (already fixed in pass 1)
# ApJ 866 151 (Oct 2018)
SK = "Ablimit_2018_BSE"
df = update_study(df, SK, {"year": "2018", "month": "10"})
df = set_param(df, SK, "sigma_kick",
    "190 or 265",
    "kick velocity inversely proportional to remnant mass: υ_k(BH)=(3M⊙/MBH)υ_k(NS); σ_k=190 km s⁻¹ (Hansen & Phinney 1997) or 265 km s⁻¹ (Hobbs 2005)")
df = set_param(df, SK, "alpha_CE",
    "1 (standard); or Davis et al. (2012) mass-ratio dependent",
    "αCE=1 for standard cases; alternatively log10(αCE)=ϵ0+ϵ1 log10(q) from Davis et al. (2012)")
df = set_param(df, SK, "CE_prescription",
    "Webbink (1984) alpha-lambda",
    "standard energy-balance CE; αCE=1 or mass-ratio dependent (Davis et al. 2012)")
df = set_param(df, SK, "RMP",
    "Fryer et al. (2012) rapid",
    "Mrem=0.9(Mproto+Mfb) from Fryer et al. (2012) rapid SN mechanism")
df = update_study(df, SK, {
    "parameter_family": "common envelope / natal kick / mass transfer stability",
    "parameter": "α_CE, σ_kick, critical mass ratio (q_cr), λ",
})

# ── 20. Artale 2019 — also add arxiv URL fix ─────────────────────────────────
for SK in ["Artale_2019_MOBSE", "Artale_2019_MOBSEEAGLE"]:
    df = update_study(df, SK, {"arxiv_url": "https://arxiv.org/abs/1903.00083"})

# ── 21. Mennekens & Vanbeveren (2014) — note arXiv unknown ───────────────────
# A&A 564 A134 (Apr 2014): 2 authors → "Mennekens & Vanbeveren (2014)" ✓ (fixed in pass 1)
SK = "Mennekens_2014_Brusselscode"
df = update_study(df, SK, {"year": "2014", "month": "4"})
# Basic parameters from Brussels code
df = set_param(df, SK, "CE_prescription",
    "Brussels code CE prescription",
    "Brussels code: CE treatment based on energy balance; specific α values not widely published separately")
df = set_param(df, SK, "stellar_tracks",
    "Brussels code stellar evolution",
    "Brussels code (Vanbeveren et al.) detailed stellar evolution with mass-transfer and CE prescriptions")

# ── 22. Lipunov 2017 — add basic parameters ───────────────────────────────────
# 3 authors → "Lipunov et al. (2017)" actually? Need to check from paper
# Already labeled correctly. Just add some parameter notes.
SK = "Lipunov_2017_ScenarioMachine"
df = set_param(df, SK, "CE_prescription",
    "Scenario Machine default",
    "Scenario Machine CE prescription; based on energy balance (Webbink 1984 formalism)")
df = set_param(df, SK, "stellar_tracks",
    "Scenario Machine (MSU code)",
    "Scenario Machine population synthesis code developed at Moscow State University (Lipunov et al.)")

# ── Save ───────────────────────────────────────────────────────────────────────
df.to_csv(IBE_CSV, index=False)
print(f"Saved {len(df)} rows, {len(df.columns)} columns to {IBE_CSV}")

# Verify a few new entries
print("\nSample checks:")
checks = [
    ("Dominik_2015_StarTrack",   ["alpha_CE", "lambda_CE", "sigma_kick"]),
    ("Baibhav_2019_MOBSE",       ["sigma_kick", "alpha_CE"]),
    ("Zevin_2020_COSMIC",        ["alpha_CE", "CE_prescription"]),
    ("Belczynski_2020_StarTrack",["sigma_kick", "RMP"]),
    ("Mapelli_2021_MOBSE",       ["alpha_CE", "beta_MT"]),
    ("Chu_2021_BSE",             ["sigma_kick", "alpha_CE", "CE_prescription"]),
    ("Ghodla_2021_BPASS",        ["sigma_kick", "RMP"]),
]
for sk, cols in checks:
    r = df[df.study_key == sk]
    if len(r) == 0:
        print(f"  {sk}: NOT FOUND")
        continue
    r = r.iloc[0]
    vals = {c: getattr(r, c, "?")[:60] if isinstance(getattr(r, c, ""), str) else getattr(r, c, "?") for c in cols}
    print(f"  {sk}: {vals}")
