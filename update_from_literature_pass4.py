#!/usr/bin/env python3
"""
Pass 4 — final gap-filling and Sgalletta arXiv URL.
"""
import pandas as pd
from pathlib import Path

IBE_CSV = Path("Data_Mandel_and_Broekgaarden_2026/isolated-binary-evolution.csv")
df = pd.read_csv(IBE_CSV, dtype=str).fillna("")


def up(df, sk, d):
    mask = df["study_key"] == sk
    if not mask.any():
        print(f"WARNING: {sk} not found")
        return df
    for col, val in d.items():
        if col not in df.columns:
            df[col] = ""
        df.loc[mask, col] = val
    return df


def sp(df, sk, col, val, note):
    mask = df["study_key"] == sk
    if not mask.any():
        return df
    nc = col + "_note"
    if col not in df.columns: df[col] = ""
    if nc not in df.columns: df[nc] = ""
    df.loc[mask, col] = val
    df.loc[mask, nc] = note
    return df


# ── Sgalletta 2025 ──────────────────────────────────────────────────────────
# arXiv:2410.21401, A&A 698 A144, June 2025
df = up(df, "Sgalletta_2025_SEVN", {
    "arxiv_url": "https://arxiv.org/abs/2410.21401",
    "year":  "2025",
    "month": "6",
    # Fix ADS URL (was A&A PDF link):
    "ads_url": "https://ui.adsabs.harvard.edu/abs/2025A%26A...698A.144S/abstract",
})
df = sp(df, "Sgalletta_2025_SEVN", "CE_prescription",
    "Webbink (1984) alpha-lambda",
    "α_CE varied ∈ {0.5, 1, 3, 5}; standard α-λ energy balance CE formalism")
df = sp(df, "Sgalletta_2025_SEVN", "stellar_tracks",
    "SEVN + PARSEC stellar evolution tracks + Madau & Fragos (2017) SFRD",
    "SEVN population synthesis with PARSEC/PADOVA stellar evolution tracks; metallicity-dependent SFR from Madau & Fragos (2017)")
df = sp(df, "Sgalletta_2025_SEVN", "RMP",
    "Fryer et al. (2012); PISN Spera & Mapelli (2017)",
    "compact object remnant masses from SEVN following Spera & Mapelli (2017); PISN treatment included")

# ── OShaughnessy 2010 — add alpha_CE ────────────────────────────────────────
df = sp(df, "OShaughnessy_2010_StarTrack", "alpha_CE",
    "αλ single factor",
    "StarTrack models orbital decay in common-envelope evolution with a single factor αλ; specific value not quoted in this paper")

# ── Lipunov 2017 ScenarioMachine — fill sigma and alpha ────────────────────
# The 2017 paper is follow-up of 2014; Scenario Machine uses different parameterization
df = sp(df, "Lipunov_2017_ScenarioMachine", "sigma_kick",
    "varies (Scenario Machine default)",
    "Scenario Machine default natal kick prescription; velocity from observed pulsar velocity distribution")
df = sp(df, "Lipunov_2017_ScenarioMachine", "alpha_CE",
    "varies (Scenario Machine default)",
    "Scenario Machine CE prescription; α_CE not explicitly quoted in this paper")

# ── Chruslinska 2019 — fill sigma and alpha (same StarTrack as 2018) ────────
df = sp(df, "Chruslinska_2019_StarTrack", "sigma_kick",
    "varies by model (NK2A: reduced kicks; CA: Bray & Eldridge 2018)",
    "reference model (ref): σ=265 km/s; NK2A: half of CCSNe give small kicks ≤50 km/s; CA: Bray & Eldridge (2018) prescription")
df = sp(df, "Chruslinska_2019_StarTrack", "alpha_CE",
    "1",
    "StarTrack CE efficiency α=1; same as Chruslinska et al. (2018) reference model")

# ── Giacobbo 2020 — fill alpha_CE ───────────────────────────────────────────
# Giacobbo & Mapelli 2020 (ApJ 891) updated kick prescription; CE same as 2018
df = sp(df, "Giacobbo_2020_MOBSE", "alpha_CE",
    "1",
    "fiducial α_CE=1 following Giacobbo & Mapelli (2018) prescription; λ from Claeys et al. (2014)")
df = sp(df, "Giacobbo_2020_MOBSE", "lambda_CE",
    "Claeys et al. (2014)",
    "λ computed using the prescriptions of Claeys et al. (2014)")
df = sp(df, "Giacobbo_2020_MOBSE", "CE_prescription",
    "Webbink (1984) alpha-lambda, Claeys lambda",
    "α_CE=1, λ from Claeys et al. (2014); αλ formalism of Webbink (1984)")

# ── Eldridge 2019 / Tang 2020 / Ghodla 2021 / Briel 2022b — BPASS alpha ────
# BPASS doesn't use a simple alpha_CE; the effective value spans a wide range
for sk, eff_range in [
    ("Eldridge_2019_BPASS",  "effectively α_CE λ = 2-100"),
    ("Tang_2020_BPASS",      "effectively α_CE λ = 2-100"),
    ("Ghodla_2021_BPASS",    "effectively α_CE λ = 2-100"),
    ("Briel_2022b_BPASS",    "effectively α_CE λ = 3-30"),
]:
    df = sp(df, sk, "alpha_CE",
        eff_range,
        f"BPASS uses energy conservation CE; effective αλ inferred retroactively: {eff_range}")

# ── Bavera 2021 — POSYDON: no fixed sigma_kick ──────────────────────────────
# POSYDON uses detailed MESA binary evolution; kicks handled differently
df = sp(df, "Bavera_2021_POSYDON", "sigma_kick",
    "N/A (POSYDON detailed MESA models)",
    "POSYDON framework uses detailed MESA binary evolution grids; natal kick prescription not as a simple Maxwellian σ in this work")

# ── Mapelli 2021 — Giacobbo & Mapelli (2020) kicks ─────────────────────────
df = sp(df, "Mapelli_2021_MOBSE", "sigma_kick",
    "Giacobbo & Mapelli (2020) prescription",
    "natal kicks from Giacobbo & Mapelli (2020) prescription (equation 7); relativistic kick v_kick=(v_m2+v_perp2+2v_m v_perp cosξ+v_par2)^0.5")

# ── Riley 2021 COMPAS — fill sigma and alpha ────────────────────────────────
df = sp(df, "Riley_2021_COMPAS", "sigma_kick",
    "265",
    "COMPAS standard: σ_rms^1D=265 km s⁻¹ for CCSN; σ=30 km s⁻¹ for ECS/ultra-stripped")
df = sp(df, "Riley_2021_COMPAS", "alpha_CE",
    "1",
    "COMPAS standard pessimistic CE: α_CE=1; no HG CE survival in pessimistic scenario")

# ── Belczynski 2020 — alpha_CE (14 models, no specific α quoted) ────────────
df = sp(df, "Belczynski_2020_StarTrack", "alpha_CE",
    "see CE_prescription; no explicit α_CE quoted",
    "StarTrack CE uses Bondi-Hoyle accretion (5% or 10%) during CE instead of standard α efficiency; specific α not parameterized in this way")

# ── Boco 2019 — fill sigma and alpha ────────────────────────────────────────
# Boco 2019 uses SEVN indirectly (Spera & Mapelli 2017 prescriptions)
# The paper uses a semi-analytic approach not SEVN directly
df = sp(df, "Boco_2019_SEVN", "sigma_kick",
    "N/A (semi-analytic; Spera & Mapelli 2017)",
    "Boco et al. (2019) uses a semi-analytic approach based on delay time distributions from Spera & Mapelli (2017); natal kicks embedded in that framework")
df = sp(df, "Boco_2019_SEVN", "alpha_CE",
    "N/A (semi-analytic approach)",
    "paper uses delay time distributions rather than direct binary evolution; CE α not separately parametrized")

# ── Lipunov 2014 — fill alpha ────────────────────────────────────────────────
df = sp(df, "Lipunov_2014_ScenarioMachine", "alpha_CE",
    "varies (Scenario Machine default)",
    "common-envelope parameter listed as uncertain hidden parameter in Scenario Machine; no specific α_CE value stated")

# ── Belczynski 2018a — fill alpha_CE ────────────────────────────────────────
# StarTrack optimistic CE paper about NGC 4993 host galaxy
df = sp(df, "Belczynski_2018a_StarTrack", "alpha_CE",
    "1",
    "StarTrack standard CE with α_CE=1; HG donors allowed to initiate and survive CE (optimistic)")

# ── Dorozsmai 2022 — fill alpha_CE from αλ combined value ───────────────────
# Already has lambda_CE=0.05; the paper quotes αλ=0.05 as combined parameter
df = sp(df, "Dorozsmai_2022_SeBa", "alpha_CE",
    "αλ=0.05 (product)",
    "SeBa uses combined αλ=0.05 as CE efficiency×binding energy parameter; this is a product, not α alone")
df = sp(df, "Dorozsmai_2022_SeBa", "sigma_kick",
    "Verbunt et al. (2017) bimodal",
    "kick velocities from Verbunt, Igoshev & Cator (2017) bimodal distribution for NSs; BH kicks scaled by mass")

# ── Save ────────────────────────────────────────────────────────────────────
df.to_csv(IBE_CSV, index=False)
print(f"Saved {len(df)} rows, {len(df.columns)} columns to {IBE_CSV}")

# Final coverage stats
studies = df.drop_duplicates("study_key").set_index("study_key")
print(f"\nFinal coverage ({len(studies)} studies):")
for col in ["arxiv_url", "sigma_kick", "alpha_CE", "CE_prescription", "RMP", "parameter_family"]:
    n = (studies[col] != "").sum() if col in studies.columns else 0
    print(f"  {col:25s}: {n:2d}/{len(studies)}")
