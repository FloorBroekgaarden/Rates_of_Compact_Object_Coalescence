#!/usr/bin/env python3
"""
Convert Data_Mandel_and_Broekgaarden_2021 CSVs from wide/column-per-study format
to a tidy long format organised by formation channel.

Old format (per DCO type per channel):
  - Metadata in rows 0-7 (year, month, ADS URL, ArXiv URL, first author,
    label, code, plotting-style integer)
  - Each study occupies two adjacent columns: rate | notes
  - One row per rate value; multiple rows per study (e.g. lower / central / upper)

New format (one file per channel, all DCO types combined):
  - One row per rate estimate
  - Columns: compact_object_type, formation_channel, study_key, label,
    first_author, year, month, ads_url, arxiv_url, code, plotting_style,
    rate_Gpc3yr, rate_type, submodel, notes

Run from the project root:
    python convert_to_tidy_format.py
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────────
DATA_DIR = Path("Data_Mandel_and_Broekgaarden_2021")
OUT_DIR  = Path("Data_Mandel_and_Broekgaarden_2026")

# ── Plotting-style integer → descriptive string ────────────────────────────────
# Original codes (from the old Jupyter notebook):
#  1  only upper limit(s)
#  2  only lower limit(s)
#  3  interval without centre value
#  4  interval with centre value (90 % credible interval)
#  5  range of simulation values
#  6  range, last value is an upper limit
#  7  range, first value is a lower limit
#  8  two credible intervals + two centre values
#  9  range, first value is the fiducial
# 10  range + lower limit via axis edge
# 11  range, first two values are fiducial
# 12  single point estimate
# 13  range, first three values are fiducial
# 14  range + upper limit via axis edge
# 15  range, upper three values are upper limits
# 16  two upper limits
# 17  range, first value is an upper limit
# 18  range + first value is upper limit + top two also upper limits
# 19  range + lower limit via axis edge (variant)
# 20  upper limit (triangle variant)
PLOTTING_STYLE_MAP: dict[int, str] = {
    1:  "upper_limit",
    2:  "lower_limit",
    3:  "range",
    4:  "credible_interval",
    5:  "range",
    6:  "range_with_upper_limit",
    7:  "range_with_lower_limit",
    8:  "credible_interval",
    9:  "range",
    10: "range_with_lower_limit",
    11: "range",
    12: "single_value",
    13: "range",
    14: "range_with_upper_limit",
    15: "range_with_upper_limit",
    16: "upper_limit",
    17: "range_with_upper_limit",
    18: "range_with_upper_limit",
    19: "range_with_lower_limit",
    20: "upper_limit",
}

# Note keywords that identify a limit type (matched against lower-cased notes)
_LOWER_KW   = ("lower limit", "lower bound", "lower")
_UPPER_KW   = ("upper limit", "upper bound", "upper")
_CENTRAL_KW = ("center", "central", "median", "centre")

# Notes strings that are *only* a limit tag, not also a submodel name
_LIMIT_ONLY = {
    "lower", "lower limit", "lower bound",
    "upper", "upper limit", "upper bound",
    "center", "central", "median", "centre",
    "error",          # used in sGRB file as a label for error-bar values
}

OUTPUT_COLUMNS = [
    "compact_object_type",
    "formation_channel",
    "study_key",
    "label",
    "first_author",
    "year",
    "month",
    "ads_url",
    "arxiv_url",
    "code",
    "plotting_style",
    "rate_Gpc3yr",
    "rate_type",
    "submodel",
    "notes",
]


# ── String helpers ─────────────────────────────────────────────────────────────

def _str(val) -> str:
    if pd.isna(val):
        return ""
    s = str(val).strip()
    return "" if s == "nan" else s


def _int(val):
    s = _str(val)
    if not s:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def _float(val):
    s = _str(val)
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


# ── Parsing helpers ────────────────────────────────────────────────────────────

def parse_rate_type(notes_raw: str, ps: str) -> str:
    """Derive rate_type from notes string and plotting style."""
    if ps == "single_value":
        return "single"
    if ps == "upper_limit":
        return "upper"
    if ps == "lower_limit":
        return "lower"

    notes = _str(notes_raw).lower()
    if not notes:
        return ""

    for k in _CENTRAL_KW:
        if k in notes:
            return "central"
    for k in _LOWER_KW:
        if notes.startswith(k):
            return "lower"
    for k in _UPPER_KW:
        if notes.startswith(k):
            return "upper"

    return ""  # the notes describe a submodel variant, not a limit type


def parse_submodel(notes_raw: str, ps: str) -> str:
    """Return a submodel label when the notes describe a model variant."""
    if ps in ("upper_limit", "lower_limit", "single_value"):
        return ""

    notes = _str(notes_raw)
    if not notes or notes.lower() in _LIMIT_ONLY:
        return ""

    # Strip leading limit keywords if followed by more text
    n_lower = notes.lower()
    for k in (*_CENTRAL_KW, *_LOWER_KW, *_UPPER_KW):
        if n_lower.startswith(k) and len(n_lower) <= len(k) + 3:
            return ""   # e.g. "lower " — just a limit label with trailing space

    return notes


def make_study_key(label: str, code: str) -> str:
    """Create a short machine-readable key from the display label + code."""
    # Extract year from parenthetical, e.g. "(2015a)" → "2015a"
    year_m = re.search(r'\((\d{4}[a-z]?)\)', label)
    year_part = year_m.group(1) if year_m else ""

    # First-author last name: strip "et al.", split on " and ", commas, parens
    author_str = re.sub(r'\bet\s+al\.?\b', '', label, flags=re.IGNORECASE)
    author_str = re.split(r'\s+and\s+|\s*,\s*|\s*\(', author_str)[0].strip()
    author_part = re.sub(r"[^A-Za-z]", "", author_str)   # letters only

    key = f"{author_part}_{year_part}" if year_part else author_part

    code_s = _str(code)
    if code_s and code_s.upper() not in ("NA", "N/A", ""):
        code_clean = re.sub(r"[^A-Za-z0-9]", "", code_s)
        key = f"{key}_{code_clean}"

    return key


# ── Core conversion ────────────────────────────────────────────────────────────

def convert_csv(path: Path, dco_type: str, channel: str) -> pd.DataFrame:
    """Parse one old-format CSV; return a tidy DataFrame."""
    raw = pd.read_csv(path, header=None, dtype=str)

    if raw.shape[0] < 10:
        print(f"  WARNING: {path.name} has <10 rows — skipping.", file=sys.stderr)
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    # Row layout (0-based):
    #  0  ADS year
    #  1  ADS month
    #  2  ADS abstract link
    #  3  ArXiv URL
    #  4  First Author
    #  5  label string  (used as column header in old plotting code)
    #  6  code
    #  7  plotting-style integer
    #  8  sub-header ("rate [Gpc^-3 yr^-1]" / "notes" / "")
    #  9+ rate data rows
    meta = raw.iloc[:8, :]
    data = raw.iloc[9:, :].reset_index(drop=True)
    n_cols = raw.shape[1]

    rows_out: list[dict] = []
    key_count: dict[str, int] = defaultdict(int)

    col = 1   # column 0 is always the empty row-label column
    while col < n_cols:
        label = _str(meta.iat[5, col])
        if not label:
            col += 2
            continue

        year      = _str(meta.iat[0, col]).replace(".0", "")
        month     = _str(meta.iat[1, col]).replace(".0", "")
        ads_url   = _str(meta.iat[2, col])
        arxiv_url = _str(meta.iat[3, col])
        author    = _str(meta.iat[4, col])
        code      = _str(meta.iat[6, col])
        ps_int    = _int(meta.iat[7, col])
        ps_str    = PLOTTING_STYLE_MAP.get(ps_int, "range") if ps_int is not None else "range"

        # Normalise code
        code_out = "" if code.upper() in ("NA", "N/A") else code

        # Unique study_key within this file (across DCO-type merges the
        # compact_object_type column disambiguates same-key rows)
        base_key = make_study_key(label, code_out)
        key_count[base_key] += 1
        study_key = base_key if key_count[base_key] == 1 else f"{base_key}_v{key_count[base_key]}"

        notes_col = col + 1 if (col + 1) < n_cols else None

        for row_i in range(len(data)):
            rate = _float(data.iat[row_i, col])
            if rate is None:
                continue

            notes_raw = _str(data.iat[row_i, notes_col]) if notes_col is not None else ""

            rows_out.append({
                "compact_object_type": dco_type,
                "formation_channel":   channel,
                "study_key":           study_key,
                "label":               label,
                "first_author":        author,
                "year":                year,
                "month":               month,
                "ads_url":             ads_url,
                "arxiv_url":           arxiv_url,
                "code":                code_out,
                "plotting_style":      ps_str,
                "rate_Gpc3yr":         rate,
                "rate_type":           parse_rate_type(notes_raw, ps_str),
                "submodel":            parse_submodel(notes_raw, ps_str),
                "notes":               notes_raw,
            })

        col += 2

    return pd.DataFrame(rows_out, columns=OUTPUT_COLUMNS)


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    if not DATA_DIR.exists():
        sys.exit(f"ERROR: input directory not found: {DATA_DIR}")

    OUT_DIR.mkdir(exist_ok=True)

    channel_dfs: dict[str, list[pd.DataFrame]] = defaultdict(list)

    for csv_path in sorted(DATA_DIR.glob("*.csv")):
        m = re.match(r"^(BH-BH|NS-BH|NS-NS)_rates_(.+)$", csv_path.stem)
        if not m:
            print(f"Skipping unrecognised filename: {csv_path.name}")
            continue

        dco_type, channel = m.group(1), m.group(2)
        print(f"  Converting {csv_path.name} …")
        df = convert_csv(csv_path, dco_type, channel)
        if not df.empty:
            channel_dfs[channel].append(df)

    print()
    for channel, dfs in sorted(channel_dfs.items()):
        combined = pd.concat(dfs, ignore_index=True)

        # Convert year/month float-strings ("6.0") to integer-strings ("6")
        for col_name in ("year", "month"):
            combined[col_name] = (
                pd.to_numeric(combined[col_name], errors="coerce")
                .astype("Int64")          # nullable int preserves NaN
                .astype(str)
                .replace("<NA>", "")      # nullable NA → empty string
            )

        out_path = OUT_DIR / f"{channel}.csv"
        combined.to_csv(out_path, index=False)
        n_studies = combined.groupby(["compact_object_type", "study_key"]).ngroups
        print(f"  → {out_path.name:45s}  {len(combined):4d} rows, {n_studies:3d} studies")

    print(f"\nDone. Output written to {OUT_DIR}/")


if __name__ == "__main__":
    main()
