#!/usr/bin/env python3
from __future__ import annotations
"""
Split Li et al. (2025) (arXiv:2510.08231) BBH rates into their
isolated-binary-evolution (CE + stable mass transfer) and CHE
contributions.

The existing Li_2025_MOBSE rows in isolated-binary-evolution.csv (and the
corresponding edges in isolated-binary-evolution_relationships.csv) used
"total_rate" from Fig. 4 of Li et al. (2025), which is the SUM of the CHE
and isolated-binary (CE + stable MT) channels. This script:

  1. Removes those 9 isolated-binary-evolution.csv rows and 8 relationship
     edges (study_key="Li_2025_MOBSE").
  2. Re-adds the 9 rows with rate_Gpc3yr replaced by the
     "total_rate_without_CHE" column (CE + stable MT only) from
     "Data_Mandel_and_Broekgaarden_2026/individual_extracted_data/Li2025-Figure4_rates.csv",
     keeping all other fields (submodel, binary-physics parameters, etc.)
     unchanged.
  3. Re-adds the 8 relationship edges with from/to_rate_Gpc3yr updated to the
     same "total_rate_without_CHE" values.
  4. Adds 9 new rows to CHE.csv (old-format, 15-column schema) for the same
     9 models, using the "CHE_rate" column.
"""
from pathlib import Path
import csv

DATA_DIR    = Path("Data_Mandel_and_Broekgaarden_2026")
IBE_CSV     = DATA_DIR / "isolated-binary-evolution.csv"
REL_CSV     = DATA_DIR / "isolated-binary-evolution_relationships.csv"
CHE_CSV     = DATA_DIR / "CHE.csv"
LI_RAW_CSV  = DATA_DIR / "individual_extracted_data" / "Li2025-Figure4_rates.csv"

STUDY_KEY = "Li_2025_MOBSE"

CHE_COLUMNS = [
    "compact_object_type", "formation_channel", "study_key", "label",
    "first_author", "year", "month", "ads_url", "arxiv_url", "code",
    "plotting_style", "rate_Gpc3yr", "rate_type", "submodel", "notes",
]


def load_li_table() -> dict[str, dict]:
    # Header has two empty-named columns (index 0 and 2), so DictReader would
    # collide them; parse by position instead.
    table = {}
    with open(LI_RAW_CSV, newline="") as f:
        reader = csv.reader(f)
        next(reader)  # header
        for cols in reader:
            table[cols[0]] = {
                "model": cols[3],
                "CHE_rate": cols[8],
                "total_rate": cols[12],
                "total_rate_without_CHE": cols[13],
            }
    return table


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def write_csv(path: Path, columns: list[str], rows: list[dict]):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in columns})


def append_csv(path: Path, columns: list[str], rows: list[dict]):
    with open(path, "rb") as f:
        f.seek(-1, 2)
        needs_newline = f.read(1) != b"\n"
    with open(path, "a", newline="") as f:
        if needs_newline:
            f.write("\n")
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in columns})


def main():
    li_table = load_li_table()
    assert len(li_table) == 9

    # --- isolated-binary-evolution.csv ---
    ibe_columns, ibe_rows = read_csv(IBE_CSV)
    li_ibe_rows = [r for r in ibe_rows if r["study_key"] == STUDY_KEY]
    assert len(li_ibe_rows) == 9
    other_ibe_rows = [r for r in ibe_rows if r["study_key"] != STUDY_KEY]

    new_ibe_rows = []
    for row in li_ibe_rows:
        sm = row["submodel"]
        li = li_table[sm]
        new_rate = li["total_rate_without_CHE"]
        row = dict(row)
        row["notes"] = (
            f"Total rate from the isolated-binary (CE + stable mass-transfer) "
            f"channels only, from Fig. 4 of Li et al. (2025) "
            f"(total_rate_without_CHE = {new_rate}; total incl. CHE = "
            f"{li['total_rate']}; CHE channel = {li['CHE_rate']})."
        )
        row["rate_Gpc3yr"] = new_rate
        new_ibe_rows.append(row)

    write_csv(IBE_CSV, ibe_columns, other_ibe_rows + new_ibe_rows)

    # --- isolated-binary-evolution_relationships.csv ---
    rel_columns, rel_rows = read_csv(REL_CSV)
    li_rel_rows = [r for r in rel_rows if r["study_key"] == STUDY_KEY]
    assert len(li_rel_rows) == 8
    other_rel_rows = [r for r in rel_rows if r["study_key"] != STUDY_KEY]

    new_rel_rows = []
    for row in li_rel_rows:
        row = dict(row)
        row["from_rate_Gpc3yr"] = li_table[row["from_submodel"]]["total_rate_without_CHE"]
        row["to_rate_Gpc3yr"] = li_table[row["to_submodel"]]["total_rate_without_CHE"]
        new_rel_rows.append(row)

    write_csv(REL_CSV, rel_columns, other_rel_rows + new_rel_rows)

    # --- CHE.csv ---
    template = li_ibe_rows[0]
    che_rows = []
    for sm, li in li_table.items():
        che_rows.append({
            "compact_object_type": template["compact_object_type"],
            "formation_channel": "CHE",
            "study_key": STUDY_KEY,
            "label": template["label"],
            "first_author": template["first_author"],
            "year": template["year"],
            "month": template["month"],
            "ads_url": template["ads_url"],
            "arxiv_url": template["arxiv_url"],
            "code": template["code"],
            "plotting_style": "range",
            "rate_Gpc3yr": li["CHE_rate"],
            "rate_type": "",
            "submodel": li["model"],
            "notes": (
                f"CHE channel rate for the '{li['model']}' MOBSE model variation, "
                f"from Fig. 4 of Li et al. (2025) (CHE_rate column); corresponds "
                f"to submodel {sm} of the isolated-binary-evolution.csv entry for "
                f"this study."
            ),
        })

    append_csv(CHE_CSV, CHE_COLUMNS, che_rows)

    print(f"isolated-binary-evolution.csv: replaced {len(new_ibe_rows)} rows")
    print(f"isolated-binary-evolution_relationships.csv: replaced {len(new_rel_rows)} edges")
    print(f"CHE.csv: appended {len(che_rows)} rows")


if __name__ == "__main__":
    main()
