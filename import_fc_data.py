#!/usr/bin/env python3
"""
Import new simulation models from the Rates_of_Formation_Channels repository into
Data_Mandel_and_Broekgaarden_2026/isolated-binary-evolution.csv.

Adds physics-parameter columns (alpha_CE, sigma_kick, …) for the new rows.
Existing rows from the 2021 review gain empty values for those columns.

Models whose study groups are already in the 2021 review data are skipped.

Run from the project root:
    python import_fc_data.py
Re-running is idempotent: studies already present are silently skipped.
To force a full re-import, delete the new rows first and re-run.
"""

import re
import sys
from io import StringIO
from pathlib import Path
import urllib.request

import pandas as pd

# ── Remote source ──────────────────────────────────────────────────────────────
BASE_URL = (
    "https://raw.githubusercontent.com/FloorBroekgaarden/"
    "Rates_of_Formation_Channels/main/fc_data/Data_formation_channels_intrinsic/"
)
# DCO type → rate-file name (file BH-NS corresponds to our "NS-BH")
RATE_FILES = {
    "BH-BH": "BH-BH_rates_review.csv",
    "NS-BH": "BH-NS_rates_review.csv",
    "NS-NS": "NS-NS_rates_review.csv",
}
RATE_COL   = "All intrinsic (z=0) [Gpc^-3 yr^-1]"
SPECS_FILE = "simulation_specs_detailed.csv"

# ── Output file ────────────────────────────────────────────────────────────────
OUT_DIR = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV = OUT_DIR / "isolated-binary-evolution.csv"

# ── Models to SKIP — already in the 2021 review data ─────────────────────────
SKIP_PATTERNS = [
    r"^B22-",        # Broekgaarden et al. 2022  → study_key Broekgaarden_COMPAS
    r"^B21-",        # Broekgaarden et al. 2021  → study_key Broekgaarden_COMPAS
    r"^RG21-",       # Riley et al. 2021         → study_key Riley_2021_COMPAS
    r"^DT22-",       # Dorozsmai & Toonen 2022   → study_key Dorozsmai_2022_SeBa
    r"^[Bb]riel",    # Briel et al. 2022b        → study_key Briel_2022b_BPASS
    r"^Olejak21",    # Olejak et al. 2021        → study_key Olejak_2021_Startrack
    r"^ShaoLi_",     # Shao & Li 2021            → study_key Shao_2021_BSE
    r"_Optimistic$", # R25/R23 optimistic-CE variants (link = "not used")
]
SKIP_LINKS = {"not used", "not_used"}

# ── Per-paper display metadata (keyed by label_author abbreviation) ───────────
# label_author → (human label, first_author, study_key)
PAPER_INFO = {
    "BO24":   ("Boesky et al. (2024)",    "Boesky",    "Boesky_2024_COMPAS"),
    "RO25":   ("Romagnolo et al. (2025)", "Romagnolo", "Romagnolo_2025_StarTrack"),
    "RO23":   ("Romagnolo et al. (2023)", "Romagnolo", "Romagnolo_2023_StarTrack"),
    "Hen23":  ("Hendriks et al. (2023)",  "Hendriks",  "Hendriks_2023_binaryc"),
    "Li25":   ("Li et al. (2025)",        "Li",        "Li_2025_MOBSE"),
    "Sg25":   ("Sgalletta et al. (2025)", "Sgalletta", "Sgalletta_2025_SEVN"),
    "PE25":   ("Pellouin et al. (2025)",  "Pellouin",  "Pellouin_2025_COSMIC"),
    "Xing24": ("Xing et al. (2024)",      "Xing",      "Xing_2024_POSYDON"),
    # van Son models (not in 2021 review) — label_author in file is "vSon22"/"vSon23"
    "vSon22":   ("van Son et al. (2022)", "van Son",   "vanSon_2022_COMPAS"),
    "vSon23":   ("van Son et al. (2023)", "van Son",   "vanSon_2023_COMPAS"),
    "VS22":     ("van Son et al. (2022)", "van Son",   "vanSon_2022_COMPAS"),
    "VS23":     ("van Son et al. (2023)", "van Son",   "vanSon_2023_COMPAS"),
    "vS22":     ("van Son et al. (2022)", "van Son",   "vanSon_2022_COMPAS"),
    "vS23":     ("van Son et al. (2023)", "van Son",   "vanSon_2023_COMPAS"),
    "vanSon22": ("van Son et al. (2022)", "van Son",   "vanSon_2022_COMPAS"),
    "vanSon23": ("van Son et al. (2023)", "van Son",   "vanSon_2023_COMPAS"),
}

# ── Column mapping: new CSV column ← simulation_specs column name ─────────────
PARAM_MAP = {
    "sigma_kick":            "sigma",
    "sigma_stripped_SN":     "sigma_strippedSN",
    "alpha_CE":              "alpha",
    "beta_MT":               "beta",
    "gamma_AM":              "gamma",
    "CE_pessimistic":        "CE optimistic/pessimistic",
    "CE_prescription":       "CE prescription",
    "lambda_CE":             "lambda",
    "RMP":                   "RMP",
    "PISN_prescription":     "PISN prescription",
    "MT_stability":          "stability",
    "Eddington_limited":     "Eddington limited accretion CO",
    "f_WR":                  "f_WR",
    "stellar_tracks":        "stellar_tracks",
    "binding_energy":        "binding energy",
}

BASE_COLS = [
    "compact_object_type", "formation_channel", "study_key", "label",
    "first_author", "year", "month", "ads_url", "arxiv_url", "code",
    "plotting_style", "rate_Gpc3yr", "rate_type", "submodel", "notes",
]
EXTRA_COLS = list(PARAM_MAP.keys())
ALL_COLS   = BASE_COLS + EXTRA_COLS


# ── Helpers ────────────────────────────────────────────────────────────────────

def _fetch(url: str) -> pd.DataFrame:
    try:
        with urllib.request.urlopen(url) as resp:
            content = resp.read().decode("utf-8")
    except Exception as exc:
        sys.exit(f"ERROR: could not fetch {url}\n  {exc}")
    return pd.read_csv(StringIO(content), dtype=str)


def _should_skip(model: str, link: str, label_auth: str = "") -> bool:
    if link.strip().lower() in SKIP_LINKS:
        return True
    if label_auth in ("nan", "NaN", "label_author", ""):
        return True  # no valid specs entry for this model
    return any(re.search(p, model) for p in SKIP_PATTERNS)


def _urls_from_link(link):
    """Split a single URL into (ads_url, arxiv_url)."""
    link = link.strip()
    if not link or link in SKIP_LINKS:
        return "", ""
    if "arxiv.org" in link.lower():
        # Normalise PDF links to abstract links
        clean = re.sub(r"/pdf/", "/abs/", link).rstrip("/")
        return "", clean
    return link, ""


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    # 1. Fetch simulation specs
    print("Fetching simulation_specs_detailed.csv …")
    specs = _fetch(BASE_URL + SPECS_FILE)
    specs.columns = specs.columns.str.strip()
    specs = specs.rename(columns={"link to paper": "link_to_paper"})
    # Rename any special-character column name variants
    specs.columns = [c.strip() for c in specs.columns]
    print(f"  {len(specs)} model specs loaded")
    all_auth = sorted(specs["label_author"].dropna().unique())
    print(f"  Unique label_author values: {all_auth}")

    # 2. Load existing isolated-binary-evolution.csv
    existing = pd.read_csv(IBE_CSV, dtype=str)
    print(f"\nExisting isolated-binary-evolution.csv: {len(existing)} rows")

    # Add new param columns to existing data (fill empty)
    for col in EXTRA_COLS:
        if col not in existing.columns:
            existing[col] = ""

    # Track which (DCO type, study_key) pairs already exist
    existing_keys = set(
        zip(existing["compact_object_type"], existing["study_key"])
    )

    new_rows = []
    unknown_authors = set()

    # 3. Process each DCO type
    for dco_type, rate_filename in RATE_FILES.items():
        print(f"\nProcessing {dco_type} ({rate_filename}) …")
        rates = _fetch(BASE_URL + rate_filename)
        rates.columns = rates.columns.str.strip()

        if RATE_COL not in rates.columns:
            print(f"  WARNING: '{RATE_COL}' not found. Available: {list(rates.columns)}")
            continue

        # Strip whitespace before joining — trailing spaces in rate file break exact match
        rates["model"] = rates["model"].str.strip()
        specs["model"]  = specs["model"].str.strip()
        merged = rates[["model", RATE_COL]].merge(specs, on="model", how="left")
        print(f"  {len(merged)} models in rate file")

        skipped_existing = skipped_pattern = added = 0

        for _, row in merged.iterrows():
            model      = str(row["model"]).strip()
            link       = str(row.get("link_to_paper", "")).strip()
            rate_s     = str(row.get(RATE_COL, "")).strip()
            label_auth = str(row.get("label_author", "")).strip()
            year_val   = str(row.get("year", "")).strip()
            code_val   = str(row.get("code", "")).strip()

            if _should_skip(model, link, label_auth):
                skipped_pattern += 1
                continue

            try:
                rate_f = float(rate_s)
            except (ValueError, TypeError):
                continue

            if label_auth in PAPER_INFO:
                label, first_author, study_key = PAPER_INFO[label_auth]
            else:
                # Fallback for any unrecognised label_author
                first_author = re.sub(r"\d", "", label_auth).strip() or label_auth
                code_clean   = re.sub(r"[^A-Za-z0-9]", "", code_val)
                study_key    = f"{first_author}_{year_val}_{code_clean}"
                label        = f"{first_author} et al. ({year_val})"
                unknown_authors.add(label_auth)

            if (dco_type, study_key) in existing_keys:
                skipped_existing += 1
                continue

            ads_url, arxiv_url = _urls_from_link(link)

            params: dict[str, str] = {}
            for new_col, spec_col in PARAM_MAP.items():
                val = str(row.get(spec_col, "")).strip()
                params[new_col] = "" if val in {"nan", "NaN", "None", ""} else val

            new_rows.append({
                "compact_object_type": dco_type,
                "formation_channel":   "isolated-binary-evolution",
                "study_key":           study_key,
                "label":               label,
                "first_author":        first_author,
                "year":                year_val,
                "month":               "",
                "ads_url":             ads_url,
                "arxiv_url":           arxiv_url,
                "code":                code_val,
                "plotting_style":      "range",
                "rate_Gpc3yr":         rate_f,
                "rate_type":           "",
                "submodel":            model,
                "notes":               "",
                **params,
            })
            # Track so we don't re-add sibling models from the same study
            # (existing_keys tracks the CSV; we add siblings freely — they share study_key)
            added += 1

        print(
            f"  skipped (pattern/link): {skipped_pattern}  "
            f"already in CSV: {skipped_existing}  "
            f"adding: {added}"
        )

    if unknown_authors:
        print(
            "\nWARNING: unknown label_author values (used fallback naming):\n  "
            + ", ".join(sorted(unknown_authors))
            + "\nAdd these to PAPER_INFO in import_fc_data.py for clean labels."
        )

    if not new_rows:
        print("\nNo new rows to add — all studies already present.")
        return

    new_df  = pd.DataFrame(new_rows)
    # Reorder columns
    extra_present = [c for c in EXTRA_COLS if c in new_df.columns]
    combined = pd.concat([existing, new_df], ignore_index=True)
    # Ensure consistent column order (BASE_COLS first, then EXTRA_COLS)
    final_cols = [c for c in ALL_COLS if c in combined.columns]
    leftover   = [c for c in combined.columns if c not in final_cols]
    combined   = combined[final_cols + leftover]

    combined.to_csv(IBE_CSV, index=False)
    print(f"\n✓  Added {len(new_rows)} new rows to {IBE_CSV}")
    print(f"   Total rows now: {len(combined)}")

    # Per-study summary
    print("\nNew studies added:")
    summary = new_df.groupby(["compact_object_type", "study_key"]).size().reset_index(name="n")
    for _, r in summary.iterrows():
        print(f"  {r['compact_object_type']:6s}  {r['study_key']:45s}  {r['n']:3d} models")


if __name__ == "__main__":
    main()
