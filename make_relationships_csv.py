#!/usr/bin/env python3
"""
Generate Data_Mandel_and_Broekgaarden_2026/isolated-binary-evolution_relationships.csv

Each row encodes ONE pairwise single-parameter relationship between two named
sub-models of the same study: what changed, in which direction, and the BH-BH
merger rate for each endpoint.

Column schema (see suggestions at bottom of file):
  study_key          – links to main isolated-binary-evolution.csv
  label              – display label  (e.g. "Boesky et al. (2024)")
  code               – simulation code  (e.g. "COMPAS")
  from_submodel      – submodel identifier of the "from" endpoint
  to_submodel        – submodel identifier of the "to" endpoint
  parameter_family   – broad category  (e.g. "common envelope")
  parameter          – specific parameter  (e.g. "alpha_CE", "sigma_kick")
  travel_label       – LaTeX annotation  (e.g. "$\\alpha_{\\rm CE} \\uparrow$")
  from_value         – parameter value at from_submodel
  to_value           – parameter value at to_submodel
  from_rate_Gpc3yr   – median BH-BH rate of from_submodel  [Gpc^-3 yr^-1]
  to_rate_Gpc3yr     – median BH-BH rate of to_submodel
  study_color_code   – integer colour code per study  (for plotting)
"""

from pathlib import Path
import pandas as pd

DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV  = DATA_DIR / "isolated-binary-evolution.csv"
OUT_CSV  = DATA_DIR / "isolated-binary-evolution_relationships.csv"

# ── Load BH-BH rates, aggregate to one median per (study_key, submodel) ──────
raw = pd.read_csv(IBE_CSV, dtype=str).fillna("")
raw["rate"] = pd.to_numeric(raw["rate_Gpc3yr"], errors="coerce")
bhbh_named = raw[(raw["compact_object_type"] == "BH-BH") & (raw["submodel"] != "")]
_rates = (
    bhbh_named.groupby(["study_key", "submodel"])["rate"]
    .median()
    .to_dict()
)

def R(sk: str, sub: str):
    """Median BH-BH rate for (study_key, submodel), or '' if not found."""
    v = _rates.get((sk, sub))
    return round(float(v), 3) if v is not None and v == v else ""


# ── Helper: append one relationship row ──────────────────────────────────────
rows = []

def add(sk, lbl, code, frm, to, pfam, param, tlabel, fval, tval, color):
    rows.append({
        "study_key":        sk,
        "label":            lbl,
        "code":             code,
        "from_submodel":    frm,
        "to_submodel":      to,
        "parameter_family": pfam,
        "parameter":        param,
        "travel_label":     tlabel,
        "from_value":       fval,
        "to_value":         tval,
        "from_rate_Gpc3yr": R(sk, frm),
        "to_rate_Gpc3yr":   R(sk, to),
        "study_color_code": color,
    })


# ══════════════════════════════════════════════════════════════════════════════
# 1.  Sgalletta et al. (2025)  –  α_CE varied: 0.5 / 1 / 3 / 5
# ══════════════════════════════════════════════════════════════════════════════
SK, LBL, CODE, C = "Sgalletta_2025_SEVN", "Sgalletta et al. (2025)", "SEVN", 1

# α_CE chain: 0.5 → 1 (fiducial) → 3 → 5
add(SK, LBL, CODE,
    "Sgalletta_alpha_0_5", "Sgalletta_alpha_1",
    "common envelope", "alpha_CE",
    r"$\alpha_{\rm CE} \uparrow$", 0.5, 1.0, C)

add(SK, LBL, CODE,
    "Sgalletta_alpha_1", "Sgalletta_alpha_3",
    "common envelope", "alpha_CE",
    r"$\alpha_{\rm CE} \uparrow$", 1.0, 3.0, C)

add(SK, LBL, CODE,
    "Sgalletta_alpha_3", "Sgalletta_alpha_5",
    "common envelope", "alpha_CE",
    r"$\alpha_{\rm CE} \uparrow$", 3.0, 5.0, C)


# ══════════════════════════════════════════════════════════════════════════════
# 2.  Mapelli et al. (2017)  –  CE efficiency, RMP, natal kicks
#     αλ products: D0.02=0.02 · D=0.10 · D1.5=1.5  (α×λ combined)
# ══════════════════════════════════════════════════════════════════════════════
SK, LBL, CODE, C = "Mapelli_2017_MOBSE", "Mapelli et al. (2017)", "MOBSE", 2

# CE efficiency chain  (αλ: 0.02 → 0.10 → 1.50)
add(SK, LBL, CODE,
    "D0.02", "D (fiducial)",
    "common envelope", "alpha_CE_lambda",
    r"$\alpha\lambda \uparrow$", 0.02, 0.10, C)

add(SK, LBL, CODE,
    "D (fiducial)", "D1.5",
    "common envelope", "alpha_CE_lambda",
    r"$\alpha\lambda \uparrow$", 0.10, 1.50, C)

# Remnant mass prescription (SN engine)
add(SK, LBL, CODE,
    "D (fiducial)", "R",
    "remnant mass prescription", "supernova_engine",
    r"rapid SN", "delayed", "rapid", C)

# CE criterion (HG donor treatment)
add(SK, LBL, CODE,
    "D (fiducial)", "DHG",
    "common envelope", "HG_CE_treatment",
    r"HG CE on", "no HG CE", "HG CE", C)

# Natal kicks for BHs
add(SK, LBL, CODE,
    "D (fiducial)", "DK",
    "natal kick", "sigma_BH",
    r"$\sigma_{\rm BH} \downarrow$", "~150 km/s (fallback)", "15 km/s (disrupted)", C)


# ══════════════════════════════════════════════════════════════════════════════
# 3.  Olejak et al. (2021)  –  MT stability / CE criterion
# ══════════════════════════════════════════════════════════════════════════════
SK, LBL, CODE, C = "Olejak_2021_Startrack", "Olejak et al. (2021)", "StarTrack", 3

add(SK, LBL, CODE,
    "M380.B", "M480.B",
    "mass transfer stability", "CE_criterion",
    r"revised CE", "standard RLOF", "Pavlovskii+2017", C)

add(SK, LBL, CODE,
    "M480.B", "M481.B",
    "mass transfer stability", "MT_timescale_switch",
    r"MT switch on", "no switch", "switch added", C)


# ══════════════════════════════════════════════════════════════════════════════
# 4.  Olejak et al. (2022)  –  RMP (fmix) × PISN (PSN strength) × CE criterion
#     Model grid:
#       fmix  : 0.5=delayed (1,4,7,10) | 1.0=intermediate (2,5,8,11) | 4.0=rapid (3,6,9,12)
#       PSN   : weak 90 M⊙ (1-3, 7-9) | strong 45 M⊙ (4-6, 10-12)
#       CE    : standard (1-6)          | Pavlovskii+2017 revised (7-12)
# ══════════════════════════════════════════════════════════════════════════════
SK, LBL, CODE, C = "Olejak_2022_Startrack", "Olejak et al. (2022)", "StarTrack", 4
_m = {i: str(i) for i in range(1, 13)}  # model number → submodel string

# fmix chain: delayed → intermediate → rapid  (for each PSN × CE combination)
_fmix_chains = [(1,2,3),(4,5,6),(7,8,9),(10,11,12)]
for a, b, c_ in _fmix_chains:
    add(SK, LBL, CODE, _m[a], _m[b], "remnant mass prescription", "fmix",
        r"$f_{\rm mix} \uparrow$", 0.5, 1.0, C)
    add(SK, LBL, CODE, _m[b], _m[c_], "remnant mass prescription", "fmix",
        r"$f_{\rm mix} \uparrow$", 1.0, 4.0, C)

# PISN strength: weak (90 M⊙) → strong (45 M⊙)
_pisn_pairs = [(1,4),(2,5),(3,6),(7,10),(8,11),(9,12)]
for a, b in _pisn_pairs:
    add(SK, LBL, CODE, _m[a], _m[b], "remnant mass prescription", "PISN_mass_threshold",
        r"stronger PISN", "90 $M_\odot$", "45 $M_\odot$", C)

# CE criterion: standard → Pavlovskii+2017
_ce_pairs = [(1,7),(2,8),(3,9),(4,10),(5,11),(6,12)]
for a, b in _ce_pairs:
    add(SK, LBL, CODE, _m[a], _m[b], "common envelope", "CE_criterion",
        r"revised CE", "standard", "Pavlovskii+2017", C)


# ══════════════════════════════════════════════════════════════════════════════
# 5.  Chruslinska et al. (2019)  –  natal kick × MT stability
# ══════════════════════════════════════════════════════════════════════════════
SK, LBL, CODE, C = "Chruslinska_2019_StarTrack", "Chruslinska et al. (2019)", "StarTrack", 5

# ref → CA: natal kick prescription changed (Hobbs → Bray & Eldridge 2018)
add(SK, LBL, CODE,
    "ref", "CA",
    "natal kick", "kick_prescription",
    r"B\&E kicks", "Hobbs (2005)", "Bray\&Eldridge (2018)", C)

# ref → NK2A: reduced natal kicks (half CCSNe get small kicks)
add(SK, LBL, CODE,
    "ref", "NK2A",
    "natal kick", "kick_prescription",
    r"NK2A kicks", "Hobbs (2005)", "NK2A reduced", C)

# CA → C+PA: add Pavlovskii MT stability (HG donors → no CE)
add(SK, LBL, CODE,
    "CA", "C+PA",
    "mass transfer stability", "HG_MT_stability",
    r"stable HG MT", "CE for HG", "stable MT (Pavlovskii)", C)


# ══════════════════════════════════════════════════════════════════════════════
# 6.  Eldridge et al. (2019)  –  BPASS stellar tracks / uncertainty
# ══════════════════════════════════════════════════════════════════════════════
SK, LBL, CODE, C = "Eldridge_2019_BPASS", "Eldridge et al. (2019)", "BPASS", 6

add(SK, LBL, CODE,
    "Table 1", "Table 2",
    "stellar tracks", "BPASS_rate_method",
    r"Table 2", "Table 1 method", "Table 2 method", C)

add(SK, LBL, CODE,
    "Table 1", "with uncertainty",
    "stellar tracks", "stellar_uncertainty",
    r"+ uncertainty", "no uncertainty", "with stellar uncertainty", C)


# ══════════════════════════════════════════════════════════════════════════════
# 7.  Neijssel et al. (2019)  –  star formation history / SFRD model
# ══════════════════════════════════════════════════════════════════════════════
SK, LBL, CODE, C = "Neijssel_2019_COMPAS", "Neijssel et al. (2019)", "COMPAS", 7

# B = BOSSA (Langer & Norman 2006; fiducial COMPAS)  |  A = power-law SFRD
add(SK, LBL, CODE,
    "B", "A",
    "star formation history", "SFRD_model",
    r"power-law SFR", "BOSSA SFR", "power-law SFR", C)


# ══════════════════════════════════════════════════════════════════════════════
# 8.  Klencki et al. (2018)  –  initial binary distributions / IMF
# ══════════════════════════════════════════════════════════════════════════════
SK, LBL, CODE, C = "Klencki_2018_StarTrack", "Klencki et al. (2018)", "StarTrack", 8

# M10 → I1: initial binary distributions (Sana+2012 → Moe & Di Stefano 2017)
add(SK, LBL, CODE,
    "M10", "I1",
    "initial conditions", "initial_binary_distributions",
    r"Moe\&DiStefano", "Sana+(2012)", "Moe\&DiStefano (2017)", C)

# I1 → I2: metallicity-dependent IMF added
add(SK, LBL, CODE,
    "I1", "I2",
    "initial conditions", "IMF",
    r"Z-dep IMF", r"$\alpha_3=2.3$", r"Z-dep $\alpha_3$", C)


# ══════════════════════════════════════════════════════════════════════════════
# 9.  Belczynski et al. (2020)  –  angular momentum transport (BH spin)
#     A = default StarTrack (no BH–BH spin-orbit coupling)
#     B = with magnetic spin-down / spin-orbit coupling
# ══════════════════════════════════════════════════════════════════════════════
SK, LBL, CODE, C = "Belczynski_2020_StarTrack", "Belczynski et al. (2020)", "StarTrack", 9

add(SK, LBL, CODE,
    "A", "B",
    "angular momentum", "BH_spin_coupling",
    r"spin coupling on", "no coupling (default)", "magnetic spin-down", C)


# ══════════════════════════════════════════════════════════════════════════════
# 10.  Romagnolo et al. (2023)  –  stellar max-radius prescription
#      All five RMAX models compared pairwise (same parameter, different value)
# ══════════════════════════════════════════════════════════════════════════════
SK, LBL, CODE, C = "Romagnolo_2023_StarTrack", "Romagnolo et al. (2023)", "StarTrack", 10
_r23_subs = [
    ("R23-A-Fiducial",  "fiducial SSE"),
    ("R23-B-RMAX2",     "RMAX METISSE boost"),
    ("R23-C-RMAX3",     "RMAX METISSE MESA"),
    ("R23-D-RMAX4",     "RMAX MESA MLT++"),
    ("R23-E-RMAX4B",    "RMAX MESA no-MLT++"),
]
# All pairwise comparisons along the max-radius axis
for i, (sub_a, val_a) in enumerate(_r23_subs):
    for sub_b, val_b in _r23_subs[i+1:]:
        add(SK, LBL, CODE,
            sub_a, sub_b,
            "stellar tracks", "max_stellar_radius",
            r"$R_{\rm max}$ change", val_a, val_b, C)


# ══════════════════════════════════════════════════════════════════════════════
# 11.  Romagnolo et al. (2025)  –  max-radius × convection criterion
# ══════════════════════════════════════════════════════════════════════════════
SK, LBL, CODE, C = "Romagnolo_2025_StarTrack", "Romagnolo et al. (2025)", "StarTrack", 11

# Max-radius pairs (same convection model, +RMAX):
_rmax_pairs = [
    ("R25-A-Fiducial",         "R25-B-RMAX",               "SSE (no RMAX)",   "SSE+RMAX"),
    ("R25-C-Conv_ML1.5",       "R25-D-Conv_ML1.5_RMAX",    "Klencki (no RMAX)", "Klencki+RMAX"),
    ("R25-E-Conv_ML1.82_MLTpp","R25-E-Conv_ML1.82_MLTpp_RMAX","MESA (no RMAX)", "MESA+RMAX"),
]
for frm, to_, fv, tv in _rmax_pairs:
    add(SK, LBL, CODE, frm, to_,
        "stellar tracks", "max_stellar_radius",
        r"$R_{\rm max}$ limited", fv, tv, C)

# Convection model pairs (same RMAX flag, different convection):
_conv_triples = [
    ("R25-A-Fiducial",      "R25-C-Conv_ML1.5",       "R25-E-Conv_ML1.82_MLTpp"),
    ("R25-B-RMAX",          "R25-D-Conv_ML1.5_RMAX",  "R25-E-Conv_ML1.82_MLTpp_RMAX"),
]
_conv_vals = ["SSE", "Klencki ML1.5", "MESA ML1.82"]
for trip in _conv_triples:
    for i, (sub_a, val_a) in enumerate(zip(trip, _conv_vals)):
        for sub_b, val_b in zip(trip[i+1:], _conv_vals[i+1:]):
            add(SK, LBL, CODE, sub_a, sub_b,
                "stellar tracks", "convection_criterion",
                r"conv. criterion change", val_a, val_b, C)


# ══════════════════════════════════════════════════════════════════════════════
# 12.  Boesky et al. (2024)  –  α_CE × β grid  +  σ_kick × RMP grid
# ══════════════════════════════════════════════════════════════════════════════
SK, LBL, CODE, C = "Boesky_2024_COMPAS", "Boesky et al. (2024)", "COMPAS", 12

_alphas = [0.1, 0.5, 2, 10]
_betas  = [0.25, 0.5, 0.75]
_alphas_str = {"0.1": "0_1", "0.5": "0_5", "2": "2", "10": "10"}
_betas_str  = {"0.25": "0_25", "0.5": "0_5", "0.75": "0_75"}

def _bname(a, b):
    """Sub-model name for CE+beta grid."""
    as_ = str(a).replace(".", "_") if a not in (2, 10) else str(int(a) if a==int(a) else a)
    bs_ = str(b).replace(".", "_")
    return f"Boesky_alphaCE_{as_}_beta{bs_}"

# Fix name function:
def bname(a, b):
    a_map = {0.1:"0_1", 0.5:"0_5", 2:"2", 10:"10"}
    b_map = {0.25:"0_25", 0.5:"0_5", 0.75:"0_75"}
    return f"Boesky_alphaCE_{a_map[a]}_beta{b_map[b]}"

# β chains (for each fixed α_CE: 0.25 → 0.5 → 0.75)
for a in _alphas:
    add(SK, LBL, CODE, bname(a,0.25), bname(a,0.5),
        "common envelope", "beta_MT", r"$\beta \uparrow$", 0.25, 0.50, C)
    add(SK, LBL, CODE, bname(a,0.5), bname(a,0.75),
        "common envelope", "beta_MT", r"$\beta \uparrow$", 0.50, 0.75, C)

# α_CE chains (for each fixed β: 0.1 → 0.5 → 2 → 10)
for b in _betas:
    add(SK, LBL, CODE, bname(0.1,b), bname(0.5,b),
        "common envelope", "alpha_CE", r"$\alpha_{\rm CE} \uparrow$", 0.1, 0.5, C)
    add(SK, LBL, CODE, bname(0.5,b), bname(2,b),
        "common envelope", "alpha_CE", r"$\alpha_{\rm CE} \uparrow$", 0.5, 2, C)
    add(SK, LBL, CODE, bname(2,b), bname(10,b),
        "common envelope", "alpha_CE", r"$\alpha_{\rm CE} \uparrow$", 2, 10, C)

# σ_kick × RMP grid
_sigmas = [30, 265, 750]
_rmps   = ["D", "R", "M"]  # Delayed, Rapid, Müller+Mandel (rapid+fallback)

def sname(s, rmp):
    return f"Boesky_sigma_{s}_RMP_{rmp}"

# σ_kick chains (for each RMP: 30 → 265 → 750)
for rmp in _rmps:
    add(SK, LBL, CODE, sname(30,rmp), sname(265,rmp),
        "natal kick", "sigma_kick",
        r"$\sigma_{\rm kick} \uparrow$", 30, 265, C)
    add(SK, LBL, CODE, sname(265,rmp), sname(750,rmp),
        "natal kick", "sigma_kick",
        r"$\sigma_{\rm kick} \uparrow$", 265, 750, C)

# RMP comparisons (for each σ: D ↔ R ↔ M)
for s in _sigmas:
    add(SK, LBL, CODE, sname(s,"D"), sname(s,"R"),
        "remnant mass prescription", "supernova_engine",
        r"rapid SN", "Delayed", "Rapid", C)
    add(SK, LBL, CODE, sname(s,"D"), sname(s,"M"),
        "remnant mass prescription", "supernova_engine",
        r"MM SN", "Delayed", "Müller+Mandel", C)
    add(SK, LBL, CODE, sname(s,"R"), sname(s,"M"),
        "remnant mass prescription", "supernova_engine",
        r"MM SN", "Rapid", "Müller+Mandel", C)


# ══════════════════════════════════════════════════════════════════════════════
# 13.  Li et al. (2025)  –  multiple parameters, all spoke from Li25-a (fiducial)
# ══════════════════════════════════════════════════════════════════════════════
SK, LBL, CODE, C = "Li_2025_MOBSE", "Li et al. (2025)", "MOBSE", 13

_li_spokes = [
    ("Li25-b", "angular momentum", "gamma_AM",  r"$\gamma \downarrow$",    -1.0, -2.0),
    ("Li25-c", "common envelope",  "alpha_CE",  r"$\alpha_{\rm CE}\downarrow$", 1.0, 0.5),
    ("Li25-d", "common envelope",  "alpha_CE",  r"$\alpha_{\rm CE}\uparrow$",   1.0, 2.0),
    ("Li25-e", "stellar winds",    "f_WR",      r"$f_{\rm WR}\downarrow$",  1.0, 0.5),
    ("Li25-f", "stellar winds",    "f_WR",      r"$f_{\rm WR}\uparrow$",    1.0, 2.0),
    ("Li25-g", "natal kick",       "sigma_kick",r"$\sigma\downarrow$",      265, 45),
    ("Li25-h", "natal kick",       "sigma_kick",r"$\sigma\uparrow$",        265, 750),
    ("Li25-i", "mass transfer stability","q_crit",r"$q_{\rm crit}$ change", "default", "Ge+2020"),
]
for to_sub, pfam, param, tlabel, fv, tv in _li_spokes:
    add(SK, LBL, CODE, "Li25-a", to_sub, pfam, param, tlabel, fv, tv, C)


# ══════════════════════════════════════════════════════════════════════════════
# 14.  Dorozsmai & Toonen (2022)  –  4-parameter grid (β × ζ × γ × T_eff)
#
#     Grid layout  (submodel name → coordinates):
#       β  ∈ {0.3, 0.7}         (MT accretion efficiency)
#       ζ  ∈ {4 (default), 7.5} (MT stability threshold ξ_{ad,rad})
#       γ  ∈ {2.5 (default), 1} (CE angular-momentum prescription)
#       T  ∈ {K (Kelvin), IT}   (Roche-lobe-overflow criterion)
# ══════════════════════════════════════════════════════════════════════════════
SK, LBL, CODE, C = "Dorozsmai_2022_SeBa", "Dorozsmai \& Toonen (2022)", "SeBa", 14

# Map (β, ζ, γ, T) → submodel name
_dt_grid = {
    (0.3, 4.0, 2.5, "K"):  "beta 0.3",
    (0.7, 4.0, 2.5, "K"):  "beta 0.7",
    (0.3, 4.0, 2.5, "IT"): "beta 0.3 IT",
    (0.7, 4.0, 2.5, "IT"): "beta 0.7 IT",
    (0.3, 7.5, 2.5, "K"):  "beta 0.3, zeta 7.5",
    (0.7, 7.5, 2.5, "K"):  "beta 0.7, zeta 7.5",
    (0.3, 7.5, 2.5, "IT"): "DT22-beta0-3-zeta7-5-IT",
    (0.7, 7.5, 2.5, "IT"): "DT22-beta0-7-zeta7-5-IT",
    (0.3, 4.0, 1.0, "K"):  "DT22-beta0-3-gamma1",
    (0.7, 4.0, 1.0, "K"):  "DT22-beta0-7-gamma1",
    (0.3, 4.0, 1.0, "IT"): "DT22-beta0-3-gamma1-IT",
    (0.7, 4.0, 1.0, "IT"): "DT22-beta0-7-gamma1-IT",
    (0.3, 7.5, 1.0, "K"):  "DT22-beta0-3-gamma1-zeta7-5",
    (0.7, 7.5, 1.0, "K"):  "DT22-beta0-7-gamma1-zeta7-5",
    (0.3, 7.5, 1.0, "IT"): "DT22-beta0-3-gamma1-zeta7-5-IT",
    (0.7, 7.5, 1.0, "IT"): "DT22-beta0-7-gamma1-zeta7-5-IT",
}

_betas_dt = [0.3, 0.7]
_zetas_dt = [4.0, 7.5]
_gammas_dt = [2.5, 1.0]
_teff_dt = ["K", "IT"]

# β: 0.3 → 0.7  (vary β, hold ζ, γ, T fixed)
for z in _zetas_dt:
    for g in _gammas_dt:
        for t in _teff_dt:
            add(SK, LBL, CODE,
                _dt_grid[(0.3,z,g,t)], _dt_grid[(0.7,z,g,t)],
                "mass transfer", "beta_MT",
                r"$\beta \uparrow$", 0.3, 0.7, C)

# ζ: 4.0 → 7.5  (vary ζ, hold β, γ, T fixed)
for b in _betas_dt:
    for g in _gammas_dt:
        for t in _teff_dt:
            add(SK, LBL, CODE,
                _dt_grid[(b,4.0,g,t)], _dt_grid[(b,7.5,g,t)],
                "mass transfer stability", "zeta_stability",
                r"$\xi \uparrow$", 4.0, 7.5, C)

# γ: 2.5 → 1.0  (vary γ, hold β, ζ, T fixed)
for b in _betas_dt:
    for z in _zetas_dt:
        for t in _teff_dt:
            add(SK, LBL, CODE,
                _dt_grid[(b,z,2.5,t)], _dt_grid[(b,z,1.0,t)],
                "common envelope", "gamma_CE",
                r"$\gamma \downarrow$", 2.5, 1.0, C)

# T_eff: K → IT  (vary T, hold β, ζ, γ fixed)
for b in _betas_dt:
    for z in _zetas_dt:
        for g in _gammas_dt:
            add(SK, LBL, CODE,
                _dt_grid[(b,z,g,"K")], _dt_grid[(b,z,g,"IT")],
                "mass transfer stability", "RLOF_criterion",
                r"IT criterion", "Kelvin (K)", "implicit T (IT)", C)


# ══════════════════════════════════════════════════════════════════════════════
# 15.  Mennekens & Vanbeveren (2014)  –  multi-parameter grid
#      Models 12, 16, 17, 18 present in BH-BH data.
#      Note: specific per-model parameter changes require Table 1 of paper;
#            relationships listed here are approximate / to be verified.
# ══════════════════════════════════════════════════════════════════════════════
SK, LBL, CODE, C = "Mennekens_2014_Brusselscode", "Mennekens \& Vanbeveren (2014)", "Brussels code", 15

# Provisional chain ordered by rate: 18 → 17 → 12 → 16
# TODO: verify exact parameter changes from Table 1 of Mennekens & Vanbeveren (2014)
_mn_chain = [("18","17"),("17","12"),("12","16")]
for frm, to_ in _mn_chain:
    add(SK, LBL, CODE, frm, to_,
        "multi-parameter", "multi-parameter",
        r"model variation", "see paper", "see paper", C)


# ══════════════════════════════════════════════════════════════════════════════
# Write CSV
# ══════════════════════════════════════════════════════════════════════════════
df_out = pd.DataFrame(rows)

# Quick sanity check: report any submodel names where rate lookup failed
missing = df_out[df_out["from_rate_Gpc3yr"] == ""][["study_key","from_submodel"]].drop_duplicates()
if not missing.empty:
    print("WARNING — rate lookup failed for these (check submodel names):")
    print(missing.to_string(index=False))
missing2 = df_out[df_out["to_rate_Gpc3yr"] == ""][["study_key","to_submodel"]].drop_duplicates()
if not missing2.empty:
    print(missing2.to_string(index=False))

df_out.to_csv(OUT_CSV, index=False)
print(f"\nWrote {len(df_out)} rows to {OUT_CSV}")
print(f"Studies covered: {df_out['study_key'].nunique()}")
print(f"\nRows per study:")
print(df_out.groupby(["study_key","label"])["parameter_family"].count()
           .rename("n_rels").to_string())
