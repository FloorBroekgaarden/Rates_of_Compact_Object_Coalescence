#!/usr/bin/env python3
from __future__ import annotations
"""
Add van Son et al. (2022) "No peaks without valleys" (SMT-only channel,
arXiv:2209.13609) local merger rates to the tidy dataset.

Source: Table 2 (core mass fraction f_core, mass-transfer stability zeta_eff,
mass-transfer efficiency beta_acc) and Table 3 (SN remnant-mass mixing f_mix,
circumbinary-disk angular-momentum loss f_disk), excluding the combined
R_0.2 column (BBH + BHNS only).  Fiducial model (Table 1): zeta_eff=6.0,
beta_acc=0.5, f_core=0.34, f_disk=0.

1. Appends 54 rows (27 axis-points x {BH-BH, NS-BH}) to
   isolated-binary-evolution.csv.
2. Appends 22 BH-BH parameter-relationship edges (one chain per axis) to
   isolated-binary-evolution_relationships.csv, by direct append so as not
   to disturb other in-progress edits to that file.
"""
from pathlib import Path
import csv

DATA_DIR  = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV   = DATA_DIR / "isolated-binary-evolution.csv"
RELS_CSV  = DATA_DIR / "isolated-binary-evolution_relationships.csv"

STUDY_KEY = "vanSon_2022_SMT_COMPAS"
LABEL     = "van Son (2022) SMT only"
ARXIV_URL = "https://arxiv.org/abs/2209.13609"

RMP_FIDUCIAL = r"Fryer (2012) delayed ($a_{\rm SN}=-0.9$, $b_{\rm SN}=13.9\,M_\odot$, $M_{\rm thresh}=14.8\,M_\odot$)"

# ── Axis definitions: (axis_key, parameter_family, parameter, travel_label,
#    list of (value, R_BBH02, R_BHNS02, is_fiducial)) ─────────────────────────
AXES = {
    "f_core": dict(
        family="remnant mass prescription", parameter="f_core",
        travel_label=r"$f_{\rm core} \uparrow$",
        points=[
            (0.27,  3.5,  0.7, False),
            (0.31, 10.0,  2.7, False),
            (0.34, 25.8,  7.4, True),
            (0.374, 53.9, 11.7, False),
            (0.408, 87.3, 15.5, False),
        ],
    ),
    "zeta_eff": dict(
        family="mass transfer stability", parameter="zeta_stability",
        travel_label=r"$\zeta_{\rm eff} \uparrow$",
        points=[
            (3.5,  0.9,  0.0, False),
            (4.5,  4.6,  0.3, False),
            (5.5, 16.7,  3.3, False),
            (6.0, 25.3,  6.5, True),
            (6.5, 35.9, 13.0, False),
        ],
    ),
    "beta_acc": dict(
        family="mass transfer efficiency", parameter="beta_MT",
        travel_label=r"$\beta \uparrow$",
        points=[
            (0.0,  10.1, 3.9, False),
            (0.25, 17.0, 6.6, False),
            (0.5,  25.3, 6.5, True),
            (0.75, 34.0, 0.1, False),
            (1.0,  39.6, 0.0, False),
        ],
    ),
    "fmix": dict(
        family="remnant mass prescription", parameter="fmix",
        travel_label=r"$f_{\rm mix} \uparrow$",
        points=[
            (0.5, 4.2, 0.6, False),
            (0.7, 4.1, 0.6, False),
            (1.0, 5.5, 0.7, False),
            (1.4, 6.8, 0.9, False),
            (2.0, 8.0, 0.8, False),
            (2.8, 9.2, 0.9, False),
            (4.0, 9.7, 1.1, False),
        ],
    ),
    "f_disk": dict(
        family="angular momentum", parameter="f_disk",
        travel_label=r"$f_{\rm disk} \uparrow$",
        points=[
            (0.0,    26.0, 7.1, True),
            (0.25, 118.4, 4.5, False),
            (0.5,   12.0, 1.1, False),
            (0.75,   0.1, 0.4, False),
            (1.0,    0.0, 0.3, False),
        ],
    ),
}

NOTES = {
    "f_core":   r"Table 2: $f_{\rm core}$ varied; other params at fiducial ($\zeta_{\rm eff}=6.0$, $\beta_{\rm acc}=0.5$, $f_{\rm disk}=0$).",
    "zeta_eff": r"Table 2: $\zeta_{\rm eff}$ (and corresponding $q_{\rm crit}$) varied; other params at fiducial ($f_{\rm core}=0.34$, $\beta_{\rm acc}=0.5$, $f_{\rm disk}=0$).",
    "beta_acc": r"Table 2: $\beta_{\rm acc}$ varied (first MT phase only; $\beta_{\rm acc}=0$ for second MT); other params at fiducial ($f_{\rm core}=0.34$, $\zeta_{\rm eff}=6.0$, $f_{\rm disk}=0$).",
    "fmix":     r"Table 3: SN remnant-mass mixing fraction $f_{\rm mix}$ (Fryer et al. 2022 prescription) varied.",
    "f_disk":   r"Table 3: fraction of non-conservative MT lost via a circumbinary disk, $f_{\rm disk}$, varied; other params at fiducial ($f_{\rm core}=0.34$, $\zeta_{\rm eff}=6.0$, $\beta_{\rm acc}=0.5$).",
}


def fmt(v: float) -> str:
    """Format a parameter value, dropping trailing '.0' for integer-valued floats."""
    return f"{v:g}"


def submodel_name(axis: str, value: float, is_fiducial: bool) -> str:
    tag = "_fiducial" if is_fiducial else ""
    return f"vanSon_{axis}_{fmt(value)}{tag}"


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
    "parameter_family", "parameter", "travel_label", "from_value", "to_value",
    "from_rate_Gpc3yr", "to_rate_Gpc3yr", "study_color_code",
]


def build_ibe_rows():
    rows = []
    for axis, spec in AXES.items():
        for value, r_bbh, r_bhns, is_fiducial in spec["points"]:
            sub = submodel_name(axis, value, is_fiducial)
            for co_type, rate in (("BH-BH", r_bbh), ("NS-BH", r_bhns)):
                row = {c: "" for c in IBE_COLUMNS}
                row.update({
                    "compact_object_type": co_type,
                    "formation_channel": "isolated-binary-evolution",
                    "study_key": STUDY_KEY,
                    "label": LABEL,
                    "first_author": "van Son",
                    "year": "2022",
                    "arxiv_url": ARXIV_URL,
                    "code": "COMPAS",
                    "plotting_style": "range",
                    "rate_Gpc3yr": fmt(rate),
                    "submodel": sub,
                    "submodel string": sub,
                    "notes": NOTES[axis],
                    "submodel change 1": "fiducial" if is_fiducial else axis,
                    "Eddington_limited": "TRUE",
                    "stellar_tracks": "SSE",
                    "beta_MT": fmt(value) if axis == "beta_acc" else "0.5",
                    "MT_stability": fmt(value) if axis == "zeta_eff" else "6.0",
                    "RMP": (rf"Fryer (2022), $f_{{\rm mix}}={fmt(value)}$"
                            if axis == "fmix" else RMP_FIDUCIAL),
                })
                rows.append(row)
    return rows


def build_rel_rows():
    rows = []
    for axis, spec in AXES.items():
        pts = spec["points"]
        for (v1, r1, _, fid1), (v2, r2, _, fid2) in zip(pts, pts[1:]):
            rows.append({
                "study_key": STUDY_KEY,
                "label": LABEL,
                "code": "COMPAS",
                "from_submodel": submodel_name(axis, v1, fid1),
                "to_submodel": submodel_name(axis, v2, fid2),
                "parameter_family": spec["family"],
                "parameter": spec["parameter"],
                "travel_label": spec["travel_label"],
                "from_value": fmt(v1),
                "to_value": fmt(v2),
                "from_rate_Gpc3yr": fmt(r1),
                "to_rate_Gpc3yr": fmt(r2),
                "study_color_code": "16",
            })
    return rows


def append_csv(path: Path, columns: list[str], rows: list[dict]):
    # Ensure the existing file ends with a newline before appending.
    with open(path, "rb") as f:
        f.seek(-1, 2)
        needs_newline = f.read(1) != b"\n"
    with open(path, "a", newline="") as f:
        if needs_newline:
            f.write("\n")
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        for row in rows:
            writer.writerow(row)


if __name__ == "__main__":
    ibe_rows = build_ibe_rows()
    rel_rows = build_rel_rows()

    append_csv(IBE_CSV, IBE_COLUMNS, ibe_rows)
    append_csv(RELS_CSV, REL_COLUMNS, rel_rows)

    print(f"Appended {len(ibe_rows)} rows to {IBE_CSV}")
    print(f"Appended {len(rel_rows)} rows to {RELS_CSV}")
