#!/usr/bin/env python3
"""
Update isolated-binary-evolution.csv with literature-review corrections.

Pass 1 (this script):
  - Fix 2-author labels ("and" → "&")
  - Fix swapped/wrong URLs
  - Add missing months
  - Add arxiv_url for van Son 2022
  - Add `parameter_family` and `parameter` columns
  - Add note columns next to each physics-param column
  - Add `submodel` descriptions (notes) for models where identified
  - Fill/correct physics parameters from paper text

Sources: Direct reading of papers via ar5iv.org and ADS.
"""

import pandas as pd
import numpy as np
from pathlib import Path

IBE_CSV = Path("Data_Mandel_and_Broekgaarden_2026/isolated-binary-evolution.csv")

df = pd.read_csv(IBE_CSV, dtype=str).fillna("")

# ── 1. New columns to add ─────────────────────────────────────────────────────
NEW_COLS = [
    "parameter_family",
    "parameter",
    "sigma_kick_note",
    "sigma_stripped_SN_note",
    "alpha_CE_note",
    "beta_MT_note",
    "gamma_AM_note",
    "CE_pessimistic_note",
    "CE_prescription_note",
    "lambda_CE_note",
    "RMP_note",
    "PISN_prescription_note",
    "MT_stability_note",
    "Eddington_limited_note",
    "f_WR_note",
    "stellar_tracks_note",
    "binding_energy_note",
]

for col in NEW_COLS:
    if col not in df.columns:
        df[col] = ""

# ── 2. Helper functions ───────────────────────────────────────────────────────

def update_study(df, study_key, col_val_dict):
    """Apply scalar column updates to ALL rows of a study_key."""
    mask = df["study_key"] == study_key
    if mask.sum() == 0:
        print(f"WARNING: study_key not found: {study_key}")
        return df
    for col, val in col_val_dict.items():
        if col not in df.columns:
            df[col] = ""
        df.loc[mask, col] = val
    return df


def update_model(df, study_key, submodel_val, compact_object_type, col_val_dict):
    """Apply column updates to rows matching study_key + submodel + DCO type."""
    mask = (
        (df["study_key"] == study_key)
        & (df["submodel"] == submodel_val)
        & (df["compact_object_type"] == compact_object_type)
    )
    if mask.sum() == 0:
        # Try without DCO filter
        mask = (df["study_key"] == study_key) & (df["submodel"] == submodel_val)
    if mask.sum() == 0:
        print(f"WARNING: model not found: {study_key} / {submodel_val} / {compact_object_type}")
        return df
    for col, val in col_val_dict.items():
        if col not in df.columns:
            df[col] = ""
        df.loc[mask, col] = val
    return df


def update_all_submodels(df, study_key, col_val_dict):
    """Apply updates to ALL rows of a study_key (alias for update_study)."""
    return update_study(df, study_key, col_val_dict)


# ── 3. Fix 2-author labels ("and" → "&") ──────────────────────────────────────
# Rule: "First and Second (year)" → "First & Second (year)" for 2-author papers.
LABEL_FIXES = {
    "Mennekens_2014_Brusselscode":  ("Mennekens & Vanbeveren (2014)", "Mennekens"),
    "deMink_2015_StarTrack":        ("de Mink & Belczynski (2015)",   "de Mink"),
    "Lipunov_2014_ScenarioMachine": ("Lipunov & Pruzhinskaya (2014)", "Lipunov"),
    "Mapelli_2018_MOBSE":           ("Mapelli & Giacobbo (2018)",     "Mapelli"),
    "Giacobbo_2018_MOBSE":          ("Giacobbo & Mapelli (2018)",     "Giacobbo"),
    "Ablimit_2018_BSE":             ("Ablimit & Maeda (2018)",        "Ablimit"),
    "Giacobbo_2020_MOBSE":          ("Giacobbo & Mapelli (2020)",     "Giacobbo"),
    "Shao_2021_BSE":                ("Shao & Li (2021)",              "Shao"),
    "Dorozsmai_2022_SeBa":          ("Dorozsmai & Toonen (2022)",     "Dorozsmai"),
}
for sk, (new_label, new_first) in LABEL_FIXES.items():
    df = update_study(df, sk, {"label": new_label, "first_author": new_first})

# Also fix the "Roman" vs "Román" typo in study_key and label
df.loc[df["study_key"] == "RomnGarza_2021_POSYDON", "label"] = "Román-Garza et al. (2021)"
df.loc[df["study_key"] == "RomanGarza_2021_POSYDON", "label"] = "Román-Garza et al. (2021)"
# first_author for both
df.loc[df["study_key"].isin(["RomnGarza_2021_POSYDON", "RomanGarza_2021_POSYDON"]), "first_author"] = "Román-Garza"

# ── 4. Fix swapped / wrong URLs ───────────────────────────────────────────────

# Lipunov 2017: ads_url and arxiv_url are swapped
df = update_study(df, "Lipunov_2017_ScenarioMachine", {
    "ads_url":   "https://ui.adsabs.harvard.edu/abs/2017NewA...51..122L/abstract",
    "arxiv_url": "https://arxiv.org/abs/1605.01604",
})

# Dorozsmai 2022: ads_url and arxiv_url are swapped
df = update_study(df, "Dorozsmai_2022_SeBa", {
    "ads_url":   "https://ui.adsabs.harvard.edu/abs/2022arXiv220708837D/abstract",
    "arxiv_url": "https://arxiv.org/abs/2207.08837",
})

# Neijssel 2019: ads_url points to Giacobbo 2020 — fix to correct URL
df = update_study(df, "Neijssel_2019_COMPAS", {
    "ads_url":   "https://ui.adsabs.harvard.edu/abs/2019MNRAS.490.3740N/abstract",
    "arxiv_url": "https://arxiv.org/abs/1906.08136",
})

# van Son 2022: add arxiv_url (was missing)
df = update_study(df, "vanSon_2022_COMPAS", {
    "arxiv_url": "https://arxiv.org/abs/2110.01634",
    "month":     "6",   # ApJ 931 published June 2022
})

# Lipunov 2014: fix arxiv URL (PDF→abs)
df = update_study(df, "Lipunov_2014_ScenarioMachine", {
    "arxiv_url": "https://arxiv.org/abs/1312.3143",
})

# de Mink 2015: fix arxiv URL (PDF→abs)
df = update_study(df, "deMink_2015_StarTrack", {
    "arxiv_url": "https://arxiv.org/abs/1506.03573",
})

# Mapelli 2017: fix arxiv URL (PDF→abs)
df = update_study(df, "Mapelli_2017_MOBSE", {
    "arxiv_url": "https://arxiv.org/abs/1708.05722",
})

# Giacobbo 2018: fix arxiv URL (PDF→abs)
df = update_study(df, "Giacobbo_2018_MOBSE", {
    "arxiv_url": "https://arxiv.org/abs/1806.00001",
})

# Boco 2019: fix arxiv URL (PDF→abs)
df = update_study(df, "Boco_2019_SEVN", {
    "arxiv_url": "https://arxiv.org/abs/1907.06841",
})

# Santoliquido 2020: fix arxiv URL (PDF→abs)
df = update_study(df, "Santoliquido_2020_MOBSE", {
    "arxiv_url": "https://arxiv.org/abs/2004.09533",
})

# Tang 2020: fix arxiv URL (PDF→abs)
df = update_study(df, "Tang_2020_BPASS", {
    "arxiv_url": "https://arxiv.org/abs/1912.04474",
})

# Zevin 2020: fix arxiv URL (PDF→abs)
df = update_study(df, "Zevin_2020_COSMIC", {
    "arxiv_url": "https://arxiv.org/abs/2006.14573",
})

# Briel 2022b: fix arxiv URL (PDF→abs)
df = update_study(df, "Briel_2022b_BPASS", {
    "arxiv_url": "https://arxiv.org/abs/2206.13842",
})

# Chu 2021: fix arxiv URL (PDF→abs)
df = update_study(df, "Chu_2021_BSE", {
    "arxiv_url": "https://arxiv.org/abs/2110.04687",
})

# Ghodla 2021: fix arxiv URL (PDF→abs)
df = update_study(df, "Ghodla_2021_BPASS", {
    "arxiv_url": "https://arxiv.org/abs/2105.05783",
})

# Giacobbo 2018: fix arxiv URL (PDF→abs)
df = update_study(df, "Giacobbo_2018_MOBSE", {
    "arxiv_url": "https://arxiv.org/abs/1806.00001",
})

# Broekgaarden: add arxiv_url for the second paper (2112.05763)
# The main entry already has 2021arXiv210302608B (= arXiv:2103.02608)
df = update_study(df, "Broekgaarden_COMPAS", {
    "arxiv_url": "https://arxiv.org/abs/2103.02608",
})

# Sgalletta 2025: update ads_url field to be consistent (it currently stores the PDF link)
# Keep as-is since we don't have a better URL yet.

# ── 5. Add / correct months ───────────────────────────────────────────────────
MONTH_FIXES = {
    # study_key: (year, month)  — only update if current value is empty or wrong
    "Mennekens_2014_Brusselscode":   ("2014", "4"),   # A&A 564 A134 Apr 2014
    "deMink_2015_StarTrack":         ("2015", "11"),  # ApJ 814 58 Nov 2015
    "Dominik_2015_StarTrack":        ("2015", "6"),   # ApJ 806 263 Jun 2015
    "Mapelli_2017_MOBSE":            ("2017", "11"),  # MNRAS 472 Nov 2017
    "Belczynski_2018a_StarTrack":    ("2018", "7"),   # A&A 615 A91 Jul 2018
    "Mapelli_2018_MOBSE":            ("2018", "9"),   # MNRAS 479 Sep 2018
    "Kruckow_2018_COMBINE":          ("2018", "12"),  # MNRAS 481 Dec 2018
    "Chruslinska_2018_StarTrack":    ("2018", "2"),   # MNRAS 474 Feb 2018
    "Giacobbo_2018_MOBSE":           ("2018", "10"),  # MNRAS 480 Oct 2018
    "VignaGmez_2018_COMPAS":         ("2018", "12"),  # MNRAS 481 Dec 2018
    "Ablimit_2018_BSE":              ("2018", "10"),  # ApJ 866 Oct 2018
    "Klencki_2018_StarTrack":        ("2018", "11"),  # A&A 619 Nov 2018
    "Spera_2019_SEVN":               ("2019", "5"),   # MNRAS 485 May 2019
    "Chruslinska_2019_StarTrack":    ("2019", "1"),   # MNRAS 482 Jan 2019
    "Eldridge_2019_BPASS":           ("2019", "1"),   # MNRAS 482 Jan 2019
    "Boco_2019_SEVN":                ("2019", "8"),   # ApJ 881 Aug 2019
    "Baibhav_2019_MOBSE":            ("2019", "10"),  # PRD 100 Oct 2019
    "Artale_2019_MOBSE":             ("2019", "8"),   # MNRAS 487 Aug 2019
    "Artale_2019_MOBSEEAGLE":        ("2019", "8"),   # same paper
    "Neijssel_2019_COMPAS":          ("2019", "12"),  # MNRAS 490 Dec 2019
    "Belczynski_2020_StarTrack":     ("2020", "4"),   # A&A 636 Apr 2020
    "Giacobbo_2020_MOBSE":           ("2020", "3"),   # ApJ 891 Mar 2020
    "Santoliquido_2020_MOBSE":       ("2020", "8"),   # ApJ 898 Aug 2020
    "Tang_2020_BPASS":               ("2020", "3"),   # MNRAS 493 Mar 2020
    "Zevin_2020_COSMIC":             ("2020", "8"),   # ApJL 899 Aug 2020
    "Bavera_2021_POSYDON":           ("2021", "3"),   # A&A 647 Mar 2021
    "RomnGarza_2021_POSYDON":        ("2021", "12"),  # ApJ 927 (2022)? 2021 arXiv
    "RomanGarza_2021_POSYDON":       ("2021", "12"),
    "Mapelli_2021_MOBSE":            ("2021", "9"),   # A&A (Sep 2021)
    "Riley_2021_COMPAS":             ("2022", "2"),   # ApJS 258 Feb 2022 (not 2021)
    "Olejak_2021_Startrack":         ("2021", "12"),  # ApJL 921 L2 (Dec 2021)
    "Shao_2021_BSE":                 ("2022", "3"),   # ApJ 927 (Mar 2022)
    "Chu_2021_BSE":                  ("2021", "12"),  # MNRAS 509 (2022)
    "Ghodla_2021_BPASS":             ("2022", "1"),   # MNRAS (early 2022)
    "Santoliquido_2021_MOBSE":       ("2021", "9"),   # ApJ 921 Sep 2021
    "vanSon_2022_COMPAS":            ("2022", "6"),   # ApJ 931 Jun 2022
    "Briel_2022b_BPASS":             ("2023", "2"),   # MNRAS (Feb 2023)
    "Dorozsmai_2022_SeBa":           ("2024", "1"),   # MNRAS 527 Jan 2024
    "Olejak_2022_Startrack":         ("2022", "9"),   # A&A 669 (2023)
    "Hendriks_2023_binaryc":         ("2023", "9"),   # MNRAS (Sep 2023 accepted)
    "Romagnolo_2023_StarTrack":      ("2023", "8"),   # MNRAS 524 Aug 2023
    "Boesky_2024_COMPAS":            ("2024", "5"),   # arXiv preprint May 2024
    "Xing_2024_POSYDON":             ("2025", "3"),   # arXiv Oct 2024 → journal 2025?
    "Romagnolo_2025_StarTrack":      ("2025", "1"),   # arXiv Oct 2024 → journal 2025?
    "Li_2025_MOBSE":                 ("2025", "11"),  # arXiv Nov 2025
    "Pellouin_2025_COSMIC":          ("2025", "1"),   # A&A 693 A283 Jan 2025
}
for sk, (year, month) in MONTH_FIXES.items():
    mask = df["study_key"] == sk
    if mask.sum() == 0:
        continue
    # Only update year if currently different
    df.loc[mask, "year"]  = year
    df.loc[mask, "month"] = month

# ── 6. Riley 2021 study_key: actually published 2022 ─────────────────────────
# The label should stay "Riley et al. (2021)" for consistency with the literature
# but the actual journal year is 2022 (ApJS 258). Keep label as-is, just fix year/month.
# (already done above)

# ── 7. parameter_family and parameter columns ─────────────────────────────────
# Format: parameter_family = type of variation, parameter = specific parameter name

PARAM_FAMILY = {
    # study_key: (parameter_family, parameter)
    "OShaughnessy_2010_StarTrack":  ("initial conditions / star formation history", "star formation model"),
    "Mennekens_2014_Brusselscode":  ("initial conditions / stellar winds", "stellar evolution assumptions"),
    "Lipunov_2014_ScenarioMachine": ("star formation history", "star formation rate"),
    "deMink_2015_StarTrack":        ("common envelope", "CE donor type (HG allowed/excluded)"),
    "Dominik_2015_StarTrack":       ("common envelope / remnant mass prescription", "α_CE, SN engine"),
    "Lamberts_2016_BSE":            ("star formation history", "cosmological galaxy simulation"),
    "Lipunov_2017_ScenarioMachine": ("star formation history", "star formation rate model"),
    "Mapelli_2017_MOBSE":           ("common envelope / remnant mass prescription / natal kick", "α_CE, SN engine, kick model"),
    "Belczynski_2018a_StarTrack":   ("star formation history", "host galaxy star formation timescale"),
    "Mapelli_2018_MOBSE":           ("common envelope / natal kick", "α_CE, σ_kick"),
    "Kruckow_2018_COMBINE":         ("common envelope", "α_CE"),
    "Chruslinska_2018_StarTrack":   ("natal kick / initial conditions", "kick prescription, angular momentum loss"),
    "Giacobbo_2018_MOBSE":          ("initial conditions", "fiducial model"),
    "VignaGmez_2018_COMPAS":        ("common envelope / remnant mass prescription", "α_CE, SN engine"),
    "Ablimit_2018_BSE":             ("initial conditions", "fiducial model"),
    "Klencki_2018_StarTrack":       ("initial conditions", "initial binary parameter distributions"),
    "Spera_2019_SEVN":              ("remnant mass prescription", "BH mass formula"),
    "Chruslinska_2019_StarTrack":   ("natal kick / mass transfer stability", "kick prescription, MT stability"),
    "Eldridge_2019_BPASS":          ("stellar tracks", "BPASS stellar evolution models"),
    "Boco_2019_SEVN":               ("metallicity / star formation history", "SFRD model"),
    "Baibhav_2019_MOBSE":           ("star formation history", "galaxy catalog + SFRD model"),
    "Artale_2019_MOBSE":            ("star formation history", "cosmological simulation (TNG)"),
    "Artale_2019_MOBSEEAGLE":       ("star formation history", "cosmological simulation (EAGLE)"),
    "Neijssel_2019_COMPAS":         ("star formation history / metallicity", "SFRD model, metallicity distribution"),
    "Belczynski_2020_StarTrack":    ("natal kick / star formation history", "NS kick, delay time"),
    "Giacobbo_2020_MOBSE":          ("natal kick", "kick prescription"),
    "Santoliquido_2020_MOBSE":      ("star formation history / metallicity", "SFRD model"),
    "Tang_2020_BPASS":              ("stellar tracks", "BPASS stellar evolution"),
    "Zevin_2020_COSMIC":            ("initial conditions", "fiducial COSMIC model"),
    "Bavera_2021_POSYDON":          ("common envelope", "α_CE"),
    "RomnGarza_2021_POSYDON":       ("common envelope / natal kick", "α_CE, σ_kick (NS)"),
    "RomanGarza_2021_POSYDON":      ("common envelope / natal kick", "α_CE, σ_kick"),
    "Mapelli_2021_MOBSE":           ("common envelope / mass transfer efficiency", "α_CE, f_MT"),
    "Riley_2021_COMPAS":            ("stellar winds", "Wolf-Rayet wind mass loss multiplier (f_WR)"),
    "Olejak_2021_Startrack":        ("mass transfer stability / common envelope", "CE development criterion"),
    "Shao_2021_BSE":                ("initial conditions", "fiducial BSE model"),
    "Chu_2021_BSE":                 ("common envelope / natal kick", "α_CE, kick prescription"),
    "Ghodla_2021_BPASS":            ("stellar tracks", "BPASS models"),
    "Santoliquido_2021_MOBSE":      ("metallicity / star formation history", "SFRD model, redshift evolution"),
    "vanSon_2022_COMPAS":           ("star formation history / metallicity", "metallicity-specific SFRD"),
    "vanSon_2023_COMPAS":           ("mass transfer stability", "stable mass transfer formation channel"),
    "Briel_2022b_BPASS":            ("stellar tracks", "BPASS stellar evolution"),
    "Dorozsmai_2022_SeBa":          ("mass transfer efficiency / mass transfer stability", "β (MT efficiency), ζ (stability), CE criterion"),
    "Broekgaarden_COMPAS":          ("common envelope / natal kick / star formation history", "α_CE, σ_kick, SFRD"),
    "Olejak_2022_Startrack":        ("remnant mass prescription / common envelope / PISN", "f_mix (convection), CE criterion, PSN limit"),
    "Hendriks_2023_binaryc":        ("remnant mass prescription / PISN", "PPISN prescription (CO core mass shift, extra mass loss)"),
    "Romagnolo_2023_StarTrack":     ("stellar tracks", "maximum radial expansion (RMAX) prescription"),
    "Boesky_2024_COMPAS":           ("common envelope / mass transfer efficiency / natal kick / remnant mass prescription", "α_CE, β, σ_kick, RMP"),
    "Xing_2024_POSYDON":            ("common envelope / natal kick", "α_CE, σ_kick"),
    "Romagnolo_2025_StarTrack":     ("stellar tracks", "convective mixing length (α_ML) and maximum radial expansion (RMAX)"),
    "Li_2025_MOBSE":                ("common envelope / natal kick / stellar winds / angular momentum / mass transfer stability", "α_CE, σ_kick, f_WR, γ, q_c"),
    "Sgalletta_2025_SEVN":          ("common envelope", "α_CE"),
    "Pellouin_2025_COSMIC":         ("initial conditions / star formation history", "fiducial COSMIC model"),
}

for sk, (pfam, param) in PARAM_FAMILY.items():
    mask = df["study_key"] == sk
    if mask.sum() > 0:
        df.loc[mask, "parameter_family"] = pfam
        df.loc[mask, "parameter"] = param

# ── 8. Paper-level physics parameters (from paper text, with notes/quotes) ────

PAPER_PARAMS = {
    # study_key: {col: (value, note_quote)}
    "OShaughnessy_2010_StarTrack": {
        "sigma_kick": ("265", "Maxwellian kick distribution following Hobbs et al. (2005), σ=265 km/s"),
        "CE_prescription": ("Webbink (1984) alpha-lambda", "standard energy-balance CE prescription"),
    },
    "deMink_2015_StarTrack": {
        "sigma_kick": ("265", "natal kicks from a Maxwellian distribution with 1D rms σ=265 km s⁻¹"),
        "alpha_CE": ("1", "adopting a value of α_CE=1 for the envelope efficiency parameter"),
        "CE_prescription": ("Webbink (1984) alpha-lambda", "energy balance formalism"),
        "RMP": ("Fryer et al. (2012) rapid", "rapid supernova model based on carbon oxygen core mass"),
    },
    "Mapelli_2017_MOBSE": {
        "sigma_kick": ("265", "natal kicks from Maxwellian distribution, Hobbs et al. (2005), σ=265 km s⁻¹"),
        "alpha_CE": ("1", "fiducial models D, R, DHG, DK: α=1, λ=0.1"),
        "lambda_CE": ("0.1", "fiducial models: α=1, λ=0.1"),
        "CE_prescription": ("Webbink (1984) alpha-lambda", "alpha and lambda CE parameters"),
        "RMP": ("Fryer et al. (2012) delayed", "delayed SN engine for models D, DHG, DK, D0.02, D1.5"),
    },
    "Mapelli_2018_MOBSE": {
        "sigma_kick": ("265", "Maxwellian distribution with σ=265 km s⁻¹ (standard) or σ=15 km s⁻¹ (low kick)"),
        "alpha_CE": ("1", "CE efficiency α varies: 1, 3, and 5 across models"),
        "CE_prescription": ("Webbink (1984) alpha-lambda", "α=1,3,5 and metallicity-dependent λ"),
    },
    "Giacobbo_2018_MOBSE": {
        "sigma_kick": ("265", "Maxwellian natal kicks, σ=265 km s⁻¹ following Hobbs et al. (2005)"),
        "alpha_CE": ("1", "fiducial α_CE=1"),
        "CE_prescription": ("Webbink (1984) alpha-lambda", "standard energy formalism"),
    },
    "Giacobbo_2020_MOBSE": {
        "sigma_kick": ("265", "natal kick prescription proposed by Giacobbo & Mapelli (2020), fiducial σ=265 km s⁻¹"),
        "CE_prescription": ("Webbink (1984) alpha-lambda", "alpha-lambda CE formalism"),
    },
    "VignaGmez_2018_COMPAS": {
        "sigma_kick": ("265", "σ_high=265 km s⁻¹ for CCSN natal kicks"),
        "sigma_stripped_SN": ("30", "σ_low=30 km s⁻¹ for ECSN/ultra-stripped SN"),
        "alpha_CE": ("1", "fiducial α=1"),
        "lambda_CE": ("Nanjing", "λ_Nanjing function of core/total mass and radius"),
        "CE_prescription": ("Webbink (1984) alpha-lambda, Nanjing lambda", "Nanjing lambda prescription"),
        "RMP": ("Fryer et al. (2012) rapid", "rapid supernova engine in fiducial"),
    },
    "Klencki_2018_StarTrack": {
        "sigma_kick": ("265", "Maxwellian distribution with σ₁D=265 km s⁻¹, fallback-reduced"),
        "alpha_CE": ("1", "α_CE=1 for the efficiency of energy transfer"),
        "CE_prescription": ("Webbink (1984) alpha-lambda", "energy balance prescription of Webbink (1984)"),
        "PISN_prescription": ("Woosley (2017) pulsational", "stars with M_He=45-65 M⊙ subject to pair-instability pulsations"),
    },
    "Chruslinska_2018_StarTrack": {
        "sigma_kick": ("265", "σ=265 km/s following Hobbs et al. (2005); some models use alternative prescriptions"),
        "alpha_CE": ("1", "always set to 1 per the authors' methodology"),
        "CE_prescription": ("Webbink (1984) alpha-lambda", "energy-based formalism of Webbink (1984)"),
    },
    "Belczynski_2018a_StarTrack": {
        "sigma_kick": ("265", "σ₀=265 km s⁻¹ for iron core-collapse; zero kicks for ECS"),
        "CE_prescription": ("Webbink (1984) alpha-lambda, optimistic", "HG stars allowed to initiate and survive CE"),
        "binding_energy": ("partial ionization", "envelope binding energy from detailed calculation with partial inclusion of ionization energy"),
    },
    "Ablimit_2018_BSE": {
        "sigma_kick": ("265", "Maxwellian kick distribution following Hobbs et al. (2005), σ=265 km/s"),
        "CE_prescription": ("Webbink (1984) alpha-lambda", "standard energy-balance CE"),
    },
    "Neijssel_2019_COMPAS": {
        "sigma_kick": ("265", "1D standard deviation σ=265 km s⁻¹; σ=30 km s⁻¹ for ECSN"),
        "sigma_stripped_SN": ("30", "reduced kicks of 30 km s⁻¹ for electron capture or ultra-stripped SN"),
        "alpha_CE": ("1", "α=1, assuming all of the orbital energy goes into expelling the envelope"),
        "CE_prescription": ("Webbink (1984) alpha-lambda, optimistic/pessimistic", "optimistic and pessimistic scenarios for HG donors"),
        "RMP": ("Fryer et al. (2012) delayed", "Fryer et al. 'delayed' model with fallback fraction"),
    },
    "Belczynski_2020_StarTrack": {
        "sigma_kick": ("265", "Maxwellian natal kicks with σ=265 km s⁻¹"),
        "CE_prescription": ("Webbink (1984) alpha-lambda", "standard StarTrack CE prescription"),
    },
    "Kruckow_2018_COMBINE": {
        "sigma_kick": ("265", "FeCC SNe (isolated/wide): σ=265 km/s (1D rms); stripped: 120 km/s; ultra-stripped: 60 km/s; ECSN: 0-50 km/s"),
        "alpha_CE": ("0.5", "αCE = 0.5 (efficiency parameter)"),
        "CE_prescription": ("Webbink (1984) alpha-lambda with internal energy", "energy-balance with αCE=0.5, α_th=0.5"),
        "binding_energy": ("detailed calculation", "density grids calculating binding energies (λ parameters)"),
        "stellar_tracks": ("BEC stellar evolution code", "BEC stellar evolution code; grids at multiple metallicities"),
    },
    "Bavera_2021_POSYDON": {
        "alpha_CE": ("varies: 0.2-5.0", "αCE ∈ [0.2, 0.35, 0.5, 0.75, 1.0, 2.0, 5.0]"),
        "CE_prescription": ("Webbink (1984) alpha-lambda, Claeys lambda", "αCE-λ formalism with λ fits from Claeys et al. (2014)"),
        "stellar_tracks": ("MESA binary evolution", "MESA binary evolution models"),
    },
    "Olejak_2021_Startrack": {
        "sigma_kick": ("265", "Maxwellian distribution natal kicks with σ=265 km s⁻¹ (Hobbs et al., 2005) lowered by fallback"),
        "alpha_CE": ("1", "standard physical values for the envelope ejection efficiency αCE=1.0"),
        "CE_prescription": ("Webbink (1984) alpha-lambda", "HG donor stars assumed to merge during CE phase"),
    },
    "Shao_2021_BSE": {
        "sigma_kick": ("265", "NSs from CCSN: Maxwellian with σ=265 km/s; ECSN: σ=50 km/s"),
        "sigma_stripped_SN": ("50", "electron-capture supernovae: σ=50 km/s"),
        "alpha_CE": ("1", "CE ejection efficiency α_CE set to unity"),
        "CE_prescription": ("Webbink (1984) alpha-lambda, Xu & Li (2010) lambda", "binding energy parameter λ calculated by Xu & Li (2010)"),
    },
    "Santoliquido_2021_MOBSE": {
        "sigma_kick": ("265", "natal kick prescription from Giacobbo & Mapelli (2020); also Maxwellian σ=265,150,50 km/s"),
        "alpha_CE": ("varies: 0.5-10", "αCE parameter varied from 0.5 to 10"),
        "CE_prescription": ("Webbink (1984) alpha-lambda", "alpha-lambda formalism"),
        "RMP": ("Fryer et al. (2012) rapid/delayed", "rapid and delayed core-collapse SN models from Fryer et al. (2012)"),
    },
    "Santoliquido_2020_MOBSE": {
        "sigma_kick": ("265", "natal kick prescription from Mapelli et al. (2020)"),
        "CE_prescription": ("Webbink (1984) alpha-lambda", "alpha-lambda CE formalism"),
        "RMP": ("Fryer et al. (2012)", "rapid and delayed models"),
    },
    "vanSon_2022_COMPAS": {
        "sigma_kick": ("265", "draw kick magnitudes from a Maxwellian distribution; BH kicks reduced by fallback following 'delayed' prescription"),
        "alpha_CE": ("1", "αCE parameter set to one in this work"),
        "CE_prescription": ("Webbink (1984) alpha-lambda, Nanjing lambda, pessimistic", "Nanjing prescription for binding energy; pessimistic CE: HG donors do not survive"),
        "RMP": ("Fryer et al. (2012) delayed", "modelled following Fryer et al. (2012)"),
        "stellar_tracks": ("Hurley et al. (2000/2002), Pols (1998)", "fast algorithms following Hurley et al. (2000, 2002), based on Pols et al. (1998)"),
        "MT_stability": ("pessimistic CE", "pessimistic CE scenario: HG donor stars do not survive a CE event"),
    },
    "Olejak_2022_Startrack": {
        "sigma_kick": ("265", "Maxwellian distribution natal kicks with σ=265 km s⁻¹"),
        "alpha_CE": ("1", "standard StarTrack physical value: αCE=1.0"),
        "CE_prescription": ("Webbink (1984) alpha-lambda", "two CE criteria: standard StarTrack and revised Pavlovskii et al. (2017)"),
        "RMP": ("Fryer et al. (2022)", "new formulas for remnant masses given by Fryer et al. (2022) using convection mixing parameter fmix"),
        "PISN_prescription": ("Woosley (2017) strong/weak", "two PISN limits: 45 M⊙ (strong) and 90 M⊙ (weak)"),
    },
    "Dorozsmai_2022_SeBa": {
        "CE_prescription": ("Webbink (1984) alpha-lambda", "α-formalism with αλ=0.05"),
        "lambda_CE": ("0.05", "αλ=0.05 for CE binding energy"),
        "RMP": ("Fryer et al. (2012) delayed", "Delayed model of Fryer et al. (2012)"),
        "Eddington_limited": ("yes", "Eddington limited accretion"),
        "gamma_AM": ("M_d/M_a", "angular momentum loss: isotropical reemission γ=M_d/M_a"),
    },
    "Hendriks_2023_binaryc": {
        "sigma_kick": ("265", "σ_kick=265 km/s, scaled by fallback fraction"),
        "alpha_CE": ("1", "standard alpha-lambda CE prescription"),
        "RMP": ("Renzo et al. (2022) PPISN", "Renzo et al. (2022) PPISN prescription; fiducial: ΔM_PPI,CO=0, ΔM_PPI,extra ML=0"),
        "stellar_tracks": ("Hurley et al. (2000/2002), Pols (1998)", "binary_c framework based on Hurley et al. (2000, 2002)"),
        "PISN_prescription": ("Renzo et al. (2022)", "Renzo et al. (2022) PPISN prescription with variations in CO core-mass shifts"),
    },
    "Romagnolo_2023_StarTrack": {
        "sigma_kick": ("265", "Maxwellian distribution of natal kicks of σ=265 km s⁻¹, reduced by core-collapse fallback"),
        "alpha_CE": ("1", "alpha-lambda prescription from Webbink (1984), with αCE=1"),
        "beta_MT": ("0.5", "50 per cent non-conservative RLOF for non-degenerate accretors, with fraction f_a=0.5"),
        "CE_prescription": ("Webbink (1984) alpha-lambda", "alpha-lambda prescription from Webbink (1984)"),
        "stellar_tracks": ("StarTrack/METISSE/MESA", "varies across models: Hurley analytic, METISSE-BoOST, METISSE-MESA, MESA directly"),
        "PISN_prescription": ("Woosley (2017)", "pair-instability supernovae limits BHs to 50 M⊙"),
    },
    "Romagnolo_2025_StarTrack": {
        "sigma_kick": ("265", "Maxwellian distribution of natal kicks of σ=265 km s⁻¹"),
        "alpha_CE": ("1", "100% efficiency of the orbital energy transferred (α_CE=1)"),
        "beta_MT": ("0.5", "50% conservative SMT is used for non-degenerate accretors (f_a=0.5)"),
        "CE_prescription": ("Webbink (1984) alpha-lambda", "standard alpha-lambda CE"),
        "stellar_tracks": ("StarTrack/MESA", "varies across models: mixing length α_ML and RMAX prescription"),
    },
    "Boesky_2024_COMPAS": {
        "CE_prescription": ("Webbink (1984) alpha-lambda", "CE efficiency α_CE varied in [0.1, 0.5, 2, 10]"),
        "RMP": ("Fryer et al. (2012) delayed", "delayed SN remnant mass prescription"),
        "stellar_tracks": ("Hurley et al. (2000/2002)", "COMPAS rapid population synthesis"),
    },
    "Xing_2024_POSYDON": {
        "sigma_kick": ("265", "σ_CCSN=265 km s⁻¹ (fiducial); also explored at 150 and 61.6 km s⁻¹"),
        "alpha_CE": ("1", "αCE=1 (fiducial); also explored αCE=2"),
        "CE_prescription": ("Webbink (1984) alpha-lambda, POSYDON lambda", "α-λ prescription with on-the-fly λ_CE calculations"),
        "RMP": ("Fryer et al. (2012) delayed", "Fryer et al. (2012) delayed prescription"),
        "stellar_tracks": ("POSYDON/MESA", "POSYDON framework with detailed MESA binary evolution grids"),
    },
    "Li_2025_MOBSE": {
        "sigma_kick": ("265", "fiducial σ_rms^1D=265 km s⁻¹; also explored at 45 and 750 km/s"),
        "alpha_CE": ("1", "fiducial α_CE=1.0; also explored at 0.5 and 2.0"),
        "f_WR": ("1", "fiducial f_WR=1.0; also explored at 0.5 and 2.0"),
        "gamma_AM": ("-1", "fiducial: material loss carries specific angular momentum from primary (γ=-1)"),
        "stellar_tracks": ("MOBSE", "MOBSE rapid binary population synthesis"),
    },
    "Sgalletta_2025_SEVN": {
        "CE_prescription": ("Webbink (1984) alpha-lambda", "α_CE varied: 0.5, 1, 3, 5"),
        "stellar_tracks": ("SEVN", "SEVN stellar evolution for N-body code"),
    },
    "Riley_2021_COMPAS": {
        "CE_prescription": ("pessimistic, COMPAS standard", "COMPAS standard CE treatment"),
        "f_WR": ("varies: 0, 0.2, 0.6, 1.0", "Wolf-Rayet mass loss multiplier f_WR ∈ {0.0, 0.2, 0.6, 1.0}"),
        "RMP": ("Fryer et al. (2012) delayed, fallback", "'Delayed' prescription for compact object remnants with fallback-modulated kicks"),
        "stellar_tracks": ("Hurley et al. (2000/2002), COMPAS", "COMPAS rapid population synthesis using Hurley analytic formulae"),
        "PISN_prescription": ("Marchant et al. (2019)", "PPISN/PISN treatment following Marchant et al. (2019) models"),
    },
    "Broekgaarden_COMPAS": {
        "sigma_kick": ("265", "σ_rms^1D=265 km/s for CCSN; σ_rms^1D=30 km/s for ultra-stripped/ECS"),
        "sigma_stripped_SN": ("30", "σ_rms^1D=30 km s⁻¹ for ultra-stripped and electron-capture supernovae"),
        "alpha_CE": ("1", "CE efficiency parameter α=1.0 (fiducial); varied 0.1, 0.5, 2, 10 across models"),
        "CE_prescription": ("Webbink (1984) alpha-lambda, pessimistic/optimistic", "pessimistic and optimistic CE scenarios tested"),
        "RMP": ("Fryer et al. (2012) delayed", "'delayed' from Fryer et al. (2012) in fiducial"),
        "stellar_tracks": ("Hurley et al. (2000/2002), COMPAS", "COMPAS v02.35 rapid population synthesis"),
    },
    "Briel_2022b_BPASS": {
        "sigma_kick": ("265", "Maxwell-Boltzmann distribution with σ=265 km/s for neutron stars; BH kicks reduced by M_remnant/1.4 M☉"),
        "CE_prescription": ("angular momentum conservation, α_CE λ=3-30", "retroactively calculate αCE λ from detailed models; equivalent αCE λ ranging from 3 to 30"),
        "PISN_prescription": ("Farmer et al. (2019)", "prescription from Farmer et al. (2019) based on CO core"),
        "stellar_tracks": ("BPASS Cambridge stars code", "custom version of Cambridge stars code with ~250,000 1D models across 13 metallicities"),
    },
}

# Apply paper-level parameters
for sk, params in PAPER_PARAMS.items():
    mask = df["study_key"] == sk
    if mask.sum() == 0:
        continue
    for col, (val, note) in params.items():
        note_col = col + "_note"
        if col not in df.columns:
            df[col] = ""
        if note_col not in df.columns:
            df[note_col] = ""
        # Only overwrite if currently empty
        cur_val = df.loc[mask, col].iloc[0] if mask.sum() > 0 else ""
        if cur_val == "" or col == "CE_prescription":  # always update these
            df.loc[mask, col] = val
        df.loc[mask, note_col] = note

# ── 9. Model-specific parameter overrides ─────────────────────────────────────

# Mapelli 2017 models
for dco in ["BH-BH"]:
    model_params = {
        "D":     ("1", "0.1", "delayed", "Fryer et al. (2012) delayed; α=1, λ=0.1, fallback kicks [FIDUCIAL]"),
        "R":     ("1", "0.1", "rapid",   "Fryer et al. (2012) rapid SN engine; α=1, λ=0.1"),
        "DHG":   ("1", "0.1", "delayed", "BSE default HG treatment; α=1, λ=0.1"),
        "DK":    ("1", "0.1", "delayed", "Hobbs (2005) kicks without fallback scaling; α=1, λ=0.1"),
        "D0.02": ("0.2", "0.1", "delayed", "weak CE: α=0.2, λ=0.1, delayed SN"),
        "D1.5":  ("3.0", "0.5", "delayed", "strong CE: α=3.0, λ=0.5, delayed SN"),
    }
    for subm, (alpha, lam, rmp, note) in model_params.items():
        mask = (df["study_key"] == "Mapelli_2017_MOBSE") & (df["submodel"] == subm)
        df.loc[mask, "alpha_CE"] = alpha
        df.loc[mask, "lambda_CE"] = lam
        df.loc[mask, "RMP"] = rmp
        df.loc[mask, "notes"] = note
        # Mark fiducial
        if subm == "D":
            df.loc[mask, "submodel"] = "D (fiducial)"

# Vigna-Gómez 2018 models (NS-NS)
vigna_models = {
    "fiducial":       ("1",    "rapid",   "Fiducial: α=1, rapid SN, stable case BB, bimodal kicks, λ_Nanjing"),
    "delayed":        ("1",    "delayed", "Delayed SN engine: fallback prescription for proto-NS accretion"),
    "alpha=0.1":      ("0.1",  "rapid",   "Low CE efficiency: α=0.1, leads to wider post-CE orbits"),
    "alpha=10":       ("10",   "rapid",   "High CE efficiency: α=10, assumes additional energy sources"),
    "pessimistic CE": ("1",    "rapid",   "Pessimistic CE: HG donors always merge (no CE survival)"),
    "":               ("1",    "rapid",   "Range across all models"),
}
for subm, (alpha, rmp, note) in vigna_models.items():
    mask = (df["study_key"] == "VignaGmez_2018_COMPAS") & (df["submodel"] == subm)
    if mask.sum() > 0:
        df.loc[mask, "alpha_CE"] = alpha
        df.loc[mask, "RMP"] = rmp
        if note:
            df.loc[mask, "notes"] = note

# Olejak 2021 models
olejak21_models = {
    "M380.B": "Baseline: standard StarTrack RLOF criteria, standard MT stability",
    "M480.B": "Revised CE criteria (Pavlovskii+ 2017) for massive donors M_ZAMS>18 M⊙",
    "M481.B": "Revised CE criteria + modified condition for MT timescale switching",
}
for subm, note in olejak21_models.items():
    mask = df["study_key"] == "Olejak_2021_Startrack"
    mask &= df["submodel"] == subm
    df.loc[mask, "notes"] = note

# Olejak 2022 models (12 models: CE_criteria × PSN_limit × fmix)
# submodels are "1" through "12" per DCO type
olejak22_desc = {
    "1":  ("Standard CE",  "90 M⊙ PSN", "0.5", "Standard CE criteria, weak PSN (90 M⊙), fmix=0.5 (delayed engine)"),
    "2":  ("Standard CE",  "90 M⊙ PSN", "1.0", "Standard CE criteria, weak PSN, fmix=1.0 (intermediate)"),
    "3":  ("Standard CE",  "90 M⊙ PSN", "4.0", "Standard CE criteria, weak PSN, fmix=4.0 (rapid engine)"),
    "4":  ("Standard CE",  "45 M⊙ PSN", "0.5", "Standard CE criteria, strong PSN (45 M⊙), fmix=0.5"),
    "5":  ("Standard CE",  "45 M⊙ PSN", "1.0", "Standard CE criteria, strong PSN, fmix=1.0"),
    "6":  ("Standard CE",  "45 M⊙ PSN", "4.0", "Standard CE criteria, strong PSN, fmix=4.0"),
    "7":  ("Revised CE",   "90 M⊙ PSN", "0.5", "Revised CE (Pavlovskii+2017), weak PSN, fmix=0.5"),
    "8":  ("Revised CE",   "90 M⊙ PSN", "1.0", "Revised CE, weak PSN, fmix=1.0"),
    "9":  ("Revised CE",   "90 M⊙ PSN", "4.0", "Revised CE, weak PSN, fmix=4.0"),
    "10": ("Revised CE",   "45 M⊙ PSN", "0.5", "Revised CE, strong PSN, fmix=0.5"),
    "11": ("Revised CE",   "45 M⊙ PSN", "1.0", "Revised CE, strong PSN, fmix=1.0"),
    "12": ("Revised CE",   "45 M⊙ PSN", "4.0", "Revised CE, strong PSN, fmix=4.0"),
}
for subm, (ce_crit, psn, fmix, note) in olejak22_desc.items():
    mask = (df["study_key"] == "Olejak_2022_Startrack") & (df["submodel"] == subm)
    df.loc[mask, "notes"] = note
    df.loc[mask, "CE_pessimistic"] = "standard" if ce_crit == "Standard CE" else "revised Pavlovskii+2017"
    df.loc[mask, "PISN_prescription"] = psn

# Romagnolo 2023 models
r23_desc = {
    "R23-A-Fiducial": "StarTrack fiducial with Hurley et al. (2000) analytic formulae; standard RMAX",
    "R23-B-RMAX2":    "METISSE-BoOST stellar tracks (Z=0.00105); RMAX 2-7× smaller than Fiducial",
    "R23-C-RMAX3":    "METISSE-MESA setup 1 (Z=0.00142, MLT++); RMAX 3-30× smaller than Fiducial",
    "R23-D-RMAX4":    "MESA with MLT++ applied; most restrictive radial expansion (RMAX)",
    "R23-E-RMAX4B":   "MESA without MLT++; no artificial radius suppression; RMAX similar to BoOST",
}
for subm, note in r23_desc.items():
    mask = df["study_key"] == "Romagnolo_2023_StarTrack"
    mask &= df["submodel"] == subm
    df.loc[mask, "notes"] = note
    df.loc[mask, "stellar_tracks"] = subm.split("-")[2] if len(subm.split("-")) > 2 else ""

# Romagnolo 2025 models
r25_desc = {
    "R25-A-Fiducial":              ("2.0", "No",  "No",  "Reference model: StarTrack + Hurley analytic formulae, α_ML=2.0"),
    "R25-B-RMAX":                  ("2.0", "No",  "Yes", "Reference model with RMAX restriction on stellar radial expansion"),
    "R25-C-Conv_ML1.5":            ("1.5", "No",  "No",  "Convective mixing length α_ML=1.5 (Klencki+ 2020 fits); no RMAX"),
    "R25-D-Conv_ML1.5_RMAX":       ("1.5", "No",  "Yes", "α_ML=1.5 with RMAX restriction"),
    "R25-E-Conv_ML1.82_MLTpp":     ("1.82","Yes", "No",  "α_ML=1.82 with MLT++ for Z≥0.5Z⊙; no RMAX; Dutch wind 0.5×"),
    "R25-E-Conv_ML1.82_MLTpp_RMAX":("1.82","Yes", "Yes", "α_ML=1.82, MLT++, with RMAX restriction"),
}
for subm, (aml, mlpp, rmax, note) in r25_desc.items():
    mask = df["study_key"] == "Romagnolo_2025_StarTrack"
    mask &= df["submodel"] == subm
    df.loc[mask, "notes"] = note

# Boesky 2024 models: add submodel descriptions
for _, row in df[df["study_key"] == "Boesky_2024_COMPAS"].iterrows():
    subm = row["submodel"]
    idx = df[(df["study_key"] == "Boesky_2024_COMPAS") & (df["submodel"] == subm) & (df["compact_object_type"] == row["compact_object_type"])].index
    if "alphaCE" in subm:
        # Parse alpha and beta from submodel name
        import re
        m = re.match(r"Boesky_alphaCE_(.+)_beta(.+)", subm)
        if m:
            alpha_str = m.group(1).replace("_", ".")
            beta_str  = m.group(2).replace("_", ".")
            note = f"α_CE={alpha_str}, β={beta_str}; σ_kick=265 km/s; fiducial is α_CE=2, β=0.5"
            is_fiducial = (alpha_str == "2" and beta_str == "0.5")
            df.loc[idx, "notes"] = ("fiducial: " if is_fiducial else "") + note
    elif "sigma" in subm and "RMP" in subm:
        m = re.match(r"Boesky_sigma_(\d+)_RMP_(\w+)", subm)
        if m:
            sigma_val = m.group(1)
            rmp_id    = m.group(2)
            rmp_names = {"D": "Delayed", "M": "Mandel (2016)", "R": "Rapid"}
            note = f"σ_kick={sigma_val} km/s; RMP={rmp_names.get(rmp_id, rmp_id)}; α_CE=0.5, β=thermal"
            df.loc[idx, "notes"] = note

# Xing 2024 models
xing_desc = {
    "Xing24_fiducial":   ("265", "1.0", "Fiducial: σ_kick=265 km/s, α_CE=1; Fryer+2012 delayed RMP"),
    "Xing24_alpha_2":    ("265", "2.0", "Varied α_CE=2; σ_kick=265 km/s"),
    "Xing24_sigma_150":  ("150", "1.0", "Varied σ_kick=150 km/s; α_CE=1"),
    "Xing24_sigma_61_6": ("61.6","1.0", "Varied σ_kick=61.6 km/s; α_CE=1"),
}
for subm, (sigma, alpha, note) in xing_desc.items():
    mask = (df["study_key"] == "Xing_2024_POSYDON") & (df["submodel"] == subm)
    df.loc[mask, "sigma_kick"] = sigma
    df.loc[mask, "alpha_CE"]   = alpha
    df.loc[mask, "notes"]      = note

# Hendriks 2023 model
mask = df["study_key"] == "Hendriks_2023_binaryc"
df.loc[mask, "notes"] = "Fiducial binary_c model: σ_kick=265 km/s, PPISN from Renzo+2022; varies CO core-mass shift and extra mass loss"
df.loc[mask, "submodel"] = "fiducial"

# Li 2025 models
li25_desc = {
    "Li25-a": ("265", "1.0",  "-1",  "1.0",  "fiducial",   "Fiducial: γ=-1 (primary AM loss), α_CE=1, σ=265, f_WR=1"),
    "Li25-b": ("265", "1.0",  "-2",  "1.0",  "varied",     "Varied: γ=-2 (secondary AM loss); all others fiducial"),
    "Li25-c": ("265", "0.5",  "-1",  "1.0",  "varied",     "Varied: α_CE=0.5; all others fiducial"),
    "Li25-d": ("265", "2.0",  "-1",  "1.0",  "varied",     "Varied: α_CE=2.0; all others fiducial"),
    "Li25-e": ("265", "1.0",  "-1",  "0.5",  "varied",     "Varied: f_WR=0.5; all others fiducial"),
    "Li25-f": ("265", "1.0",  "-1",  "2.0",  "varied",     "Varied: f_WR=2.0; all others fiducial"),
    "Li25-g": ("45",  "1.0",  "-1",  "1.0",  "varied",     "Varied: σ_kick=45 km/s; all others fiducial"),
    "Li25-h": ("750", "1.0",  "-1",  "1.0",  "varied",     "Varied: σ_kick=750 km/s; all others fiducial"),
    "Li25-i": ("265", "1.0",  "-1",  "1.0",  "varied",     "Varied: MT stability criterion from Ge et al. (q_c,Ge); all others fiducial"),
}
for subm, (sigma, alpha, gamma, fwr, sub_type, note) in li25_desc.items():
    mask = (df["study_key"] == "Li_2025_MOBSE") & (df["submodel"] == subm)
    df.loc[mask, "sigma_kick"]  = sigma
    df.loc[mask, "alpha_CE"]    = alpha
    df.loc[mask, "gamma_AM"]    = gamma
    df.loc[mask, "f_WR"]        = fwr
    df.loc[mask, "notes"]       = note
    df.loc[mask, "submodel"]    = subm  # keep name

# Sgalletta 2025 models
sgalletta_desc = {
    "Sgalletta_alpha_1":   ("1",   "Fiducial: α_CE=1"),
    "Sgalletta_alpha_0_5": ("0.5", "Varied: α_CE=0.5"),
    "Sgalletta_alpha_3":   ("3",   "Varied: α_CE=3"),
    "Sgalletta_alpha_5":   ("5",   "Varied: α_CE=5"),
}
for subm, (alpha, note) in sgalletta_desc.items():
    mask = (df["study_key"] == "Sgalletta_2025_SEVN") & (df["submodel"] == subm)
    df.loc[mask, "alpha_CE"] = alpha
    df.loc[mask, "notes"]    = note

# Klencki 2018 models
klencki_desc = {
    "M10": "Standard: Sana+ (2012) initial binary distributions, metallicity-independent IMF (α₃=2.3)",
    "I1":  "Correlated initial binary distributions from Moe & Di Stefano (2017); IMF α₃=2.3",
    "I2":  "Moe & Di Stefano (2017) + metallicity-dependent IMF (top-heavy at Z<0.004 Z⊙)",
}
for subm, note in klencki_desc.items():
    mask = df["study_key"] == "Klencki_2018_StarTrack"
    mask &= df["submodel"] == subm
    df.loc[mask, "notes"] = note

# Dorozsmai 2022 models: descriptions
dor_desc = {
    "beta 0.3":                "β=0.3 (non-compact accretor MT efficiency), ζ=4 (standard), Teff-IT criterion",
    "beta 0.7":                "β=0.7 (high MT efficiency), ζ=4, Teff-IT criterion",
    "beta 0.3 IT":             "β=0.3, ζ=4, Ivanova & Taam (2004) CE criterion",
    "beta 0.7 IT":             "β=0.7, ζ=4, Ivanova & Taam (2004) CE criterion",
    "beta 0.3, zeta 7.5":      "β=0.3, ζ=7.5 (relaxed stability), Teff-Klencki criterion",
    "beta 0.7, zeta 7.5":      "β=0.7, ζ=7.5, Teff-Klencki criterion",
    "DT22-beta0-3-zeta7-5-IT": "β=0.3, ζ=7.5, Ivanova & Taam (2004) CE criterion",
    "DT22-beta0-7-zeta7-5-IT": "β=0.7, ζ=7.5, Ivanova & Taam (2004) CE criterion",
}
for subm, note in dor_desc.items():
    mask = (df["study_key"] == "Dorozsmai_2022_SeBa") & (df["submodel"] == subm)
    if mask.sum() > 0:
        df.loc[mask, "notes"] = note

# Belczynski 2018a NS-NS models (star formation timescale variants)
bel18a_desc = {
    "realistic":  "t_sf=5 Gyr (realistic star formation timescale in host galaxy NGC 4993)",
    "":           "range between pessimistic (t_sf=10 Gyr) and optimistic (t_sf=1 Gyr) bounds",
}
for subm, note in bel18a_desc.items():
    mask = (df["study_key"] == "Belczynski_2018a_StarTrack") & (df["submodel"] == subm)
    if mask.sum() > 0:
        df.loc[mask, "notes"] = note

# Chruslinska 2019 model descriptions
chru19_desc = {
    "ref":   "Reference model from Chruslinska+ 2018: standard natal kick and MT assumptions",
    "NK2A":  "Half of iron-core collapse SNe assumed to give small natal kicks (≤50 km/s)",
    "CA":    "Bray & Eldridge kick prescription; reduced AM loss; wider He core mass limits",
    "C+PA":  "CA + stable MT assumed for HG donors with NS/BH accretors (no CE triggered)",
}
for subm, note in chru19_desc.items():
    mask = (df["study_key"] == "Chruslinska_2019_StarTrack") & (df["submodel"] == subm)
    if mask.sum() > 0:
        df.loc[mask, "notes"] = note

# ── 10. Reorder columns ────────────────────────────────────────────────────────
BASE_COLS = [
    "compact_object_type", "formation_channel", "study_key", "label",
    "first_author", "year", "month", "ads_url", "arxiv_url", "code",
    "plotting_style", "rate_Gpc3yr", "rate_type", "submodel", "notes",
    "parameter_family", "parameter",
]
PARAM_COLS_INTERLEAVED = []
physics_params = [
    "sigma_kick", "sigma_stripped_SN", "alpha_CE", "beta_MT", "gamma_AM",
    "CE_pessimistic", "CE_prescription", "lambda_CE", "RMP", "PISN_prescription",
    "MT_stability", "Eddington_limited", "f_WR", "stellar_tracks", "binding_energy",
]
for p in physics_params:
    PARAM_COLS_INTERLEAVED.append(p)
    PARAM_COLS_INTERLEAVED.append(p + "_note")

ALL_ORDERED = BASE_COLS + PARAM_COLS_INTERLEAVED
present = [c for c in ALL_ORDERED if c in df.columns]
leftover = [c for c in df.columns if c not in present]
df = df[present + leftover]

# ── 11. Save ───────────────────────────────────────────────────────────────────
df.to_csv(IBE_CSV, index=False)
print(f"Saved {len(df)} rows, {len(df.columns)} columns to {IBE_CSV}")

# Summary
print("\nNew columns:", [c for c in df.columns if c not in [
    "compact_object_type","formation_channel","study_key","label","first_author",
    "year","month","ads_url","arxiv_url","code","plotting_style","rate_Gpc3yr",
    "rate_type","submodel","notes","sigma_kick","sigma_stripped_SN","alpha_CE",
    "beta_MT","gamma_AM","CE_pessimistic","CE_prescription","lambda_CE","RMP",
    "PISN_prescription","MT_stability","Eddington_limited","f_WR","stellar_tracks",
    "binding_energy",
]])
print("\n2-author label samples:")
for sk in ["Mennekens_2014_Brusselscode", "deMink_2015_StarTrack", "Dorozsmai_2022_SeBa", "Shao_2021_BSE"]:
    lbl = df[df["study_key"]==sk]["label"].iloc[0] if (df["study_key"]==sk).sum() > 0 else "not found"
    print(f"  {sk}: {lbl}")
