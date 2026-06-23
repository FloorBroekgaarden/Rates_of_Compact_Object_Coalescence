import json
import pandas as pd
import numpy as np
from IPython.display import display, HTML

# ── Constants ────────────────────────────────────────────────────────────────
LIMIT_GWTC5 = 49.4
LIMIT_BOCO  = 20.0

PANEL_DISPLAY_NAMES = {
    "common envelope efficiency (alpha_CE)":           "CE efficiency (α_CE)",
    "CE optimistic/pessimistic":                        "CE pessimistic/optimistic",
    "mass transfer efficiency":                         "MT efficiency (β)",
    "mass transfer stability":                          "MT stability",
    "natal kick":                                       "Natal kicks (σ_kick)",
    "remnant mass prescription":                        "Remnant mass prescription",
    "stellar tracks":                                   "Stellar evolution tracks",
    "star formation history":                           "Star formation history",
    "initial conditions":                               "Initial conditions",
    "angular momentum":                                 "Angular momentum",
    "stellar winds":                                    "Stellar winds",
    "binding energy lambda":                            "Binding energy (λ)",
    "convective envelope criteria":                     "Convective envelope criteria",
    "CE efficiency & binding energy (alpha & lambda)":  "α·λ (CE eff. & binding energy)",
    "other CE physics":                                 "Other CE physics",
    "tidal effects":                                    "Tidal effects",
}

def make_merger_rate_table(
    df,
    label_col           = "label",
    family_col          = "parameter_family",
    parameter_col       = "parameter",
    travel_label_col    = "travel_label",
    from_value_col      = "from_value",
    to_value_col        = "to_value",
    from_rate_col       = "from_rate_Gpc3yr",
    to_rate_col         = "to_rate_Gpc3yr",
    limit_gwtc5         = LIMIT_GWTC5,
    limit_boco          = LIMIT_BOCO,
    panel_display_names = PANEL_DISPLAY_NAMES,
    title               = "NS-NS Merger Rate — Model Relationships",
    subtitle            = "Single-parameter variations across BPS studies · rates in Gpc⁻³ yr⁻¹",
    output_file         = None,   # optional: path to save HTML file
):
    """
    Build and display an interactive HTML merger-rate table inside Jupyter.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain the columns named by the *_col arguments.
    output_file : str or None
        If given, also write the HTML to this path.
    """

    # ── Prepare data ──────────────────────────────────────────────────────────
    keep = [label_col, family_col, parameter_col, travel_label_col,
            from_value_col, to_value_col, from_rate_col, to_rate_col]
    data = df[keep].copy()
    data[from_rate_col] = pd.to_numeric(data[from_rate_col], errors="coerce")
    data[to_rate_col]   = pd.to_numeric(data[to_rate_col],   errors="coerce")
    data = data.dropna(subset=[from_rate_col, to_rate_col])
    data = data[data[from_rate_col] > 0]
    data = data[data[to_rate_col]   > 0]
    data["_factor"] = data[from_rate_col] / data[to_rate_col]

    rows = []
    for _, r in data.iterrows():
        rows.append({
            "label":            str(r[label_col]),
            "parameter_family": str(r[family_col]),
            "parameter":        str(r[parameter_col]),
            "travel_label":     str(r[travel_label_col]),
            "from_value":       str(r[from_value_col]),
            "to_value":         str(r[to_value_col]),
            "from_rate":        float(r[from_rate_col]),
            "to_rate":          float(r[to_rate_col]),
            "factor":           float(r["_factor"]),
        })

    rows_json           = json.dumps(rows)
    display_names_json  = json.dumps(panel_display_names)

    # ── HTML/CSS/JS ───────────────────────────────────────────────────────────
    html = f"""
<div id="mrt-root">
<style>
#mrt-root {{
  --bg:        #0e1117;
  --surface:   #161b25;
  --border:    #252d3d;
  --accent:    #5b8dee;
  --accent2:   #e06c75;
  --accent3:   #98c379;
  --text:      #cdd3de;
  --muted:     #6b7897;
  --tag-bg:    #1e2638;
  --font-mono: "JetBrains Mono","Fira Mono","Courier New",monospace;
  --font-body: "Inter","Segoe UI",sans-serif;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-body);
  font-size: 13px;
  line-height: 1.5;
  padding: 20px 24px 40px;
  border-radius: 8px;
  margin-top: 10px;
}}
#mrt-root h2 {{
  font-size: 16px; font-weight: 600; letter-spacing: .02em;
  color: #e8ecf4; margin-bottom: 3px;
}}
#mrt-root .mrt-subtitle {{
  font-size: 11.5px; color: var(--muted); margin-bottom: 18px;
}}
#mrt-root .mrt-controls {{
  display: flex; flex-wrap: wrap; gap: 10px 20px;
  margin-bottom: 14px; align-items: flex-start;
}}
#mrt-root .mrt-cg {{ display: flex; flex-direction: column; gap: 4px; }}
#mrt-root .mrt-clabel {{
  font-size: 10px; font-weight: 700; letter-spacing: .08em;
  text-transform: uppercase; color: var(--muted);
}}
#mrt-root .mrt-btn-row {{ display: flex; flex-wrap: wrap; gap: 4px; }}
#mrt-root button {{
  background: var(--tag-bg); border: 1px solid var(--border);
  color: var(--text); border-radius: 4px; padding: 3px 10px;
  font-size: 11.5px; font-family: var(--font-body); cursor: pointer;
  transition: background .1s, border-color .1s, color .1s; white-space: nowrap;
}}
#mrt-root button:hover {{ border-color: var(--accent); color: #fff; }}
#mrt-root button.mrt-active {{
  background: var(--accent); border-color: var(--accent);
  color: #fff; font-weight: 600;
}}
#mrt-root button.mrt-active.mrt-lim-gwtc5 {{
  background: var(--accent2); border-color: var(--accent2);
}}
#mrt-root button.mrt-active.mrt-lim-boco {{
  background: var(--accent3); border-color: var(--accent3); color: #0e1117;
}}
#mrt-root .mrt-stats {{
  font-size: 11.5px; color: var(--muted); margin-bottom: 8px;
}}
#mrt-root .mrt-stats span {{ color: var(--text); font-weight: 600; }}
#mrt-root .mrt-wrap {{
  overflow-x: auto; border: 1px solid var(--border); border-radius: 6px;
}}
#mrt-root table {{
  width: 100%; border-collapse: collapse; font-size: 12px;
}}
#mrt-root thead tr {{
  background: var(--surface); border-bottom: 1px solid var(--border);
}}
#mrt-root th {{
  padding: 7px 11px; text-align: left; font-size: 10px; font-weight: 700;
  letter-spacing: .07em; text-transform: uppercase; color: var(--muted);
  white-space: nowrap; cursor: pointer; user-select: none;
}}
#mrt-root th:hover {{ color: var(--accent); }}
#mrt-root th .sa {{ margin-left: 3px; opacity: .4; font-size: 10px; }}
#mrt-root th.mrt-sorted .sa {{ opacity: 1; color: var(--accent); }}
#mrt-root tbody tr {{ border-bottom: 1px solid var(--border); transition: background .07s; }}
#mrt-root tbody tr:last-child {{ border-bottom: none; }}
#mrt-root tbody tr:hover {{ background: var(--surface); }}
#mrt-root td {{ padding: 6px 11px; vertical-align: middle; white-space: nowrap; }}
#mrt-root .c-label  {{ font-family: var(--font-mono); font-size: 11px; color: #c4c9d6; max-width: 200px; white-space: normal; word-break: break-word; }}
#mrt-root .c-family {{ max-width: 170px; white-space: normal; }}
#mrt-root .c-param  {{ font-family: var(--font-mono); font-size: 11px; color: #a8b1c7; }}
#mrt-root .c-travel {{ font-family: var(--font-mono); font-size: 11px; }}
#mrt-root .c-rate   {{ font-family: var(--font-mono); font-size: 11.5px; text-align: right; }}
#mrt-root .c-factor {{ font-family: var(--font-mono); font-size: 11.5px; text-align: right; font-weight: 600; }}
#mrt-root .ftag {{
  display: inline-block; background: var(--tag-bg);
  border: 1px solid var(--border); border-radius: 3px;
  padding: 1px 6px; font-size: 11px; color: var(--text); white-space: nowrap;
}}
#mrt-root .r-high {{ color: var(--accent2); }}
#mrt-root .r-mid  {{ color: var(--text); }}
#mrt-root .r-low  {{ color: var(--accent3); }}
#mrt-root .f-high {{ color: var(--accent2); }}
#mrt-root .f-mid  {{ color: var(--text); }}
#mrt-root .f-low  {{ color: var(--accent3); }}
#mrt-root .badge {{
  display: inline-block; border-radius: 3px; padding: 1px 5px;
  font-size: 9.5px; font-weight: 700; margin-left: 4px; vertical-align: middle;
}}
#mrt-root .b-gwtc5 {{ background: rgba(224,108,117,.18); color: var(--accent2); border: 1px solid rgba(224,108,117,.4); }}
#mrt-root .b-boco  {{ background: rgba(152,195,121,.15); color: var(--accent3); border: 1px solid rgba(152,195,121,.4); }}
#mrt-root .arrow   {{ color: var(--muted); margin: 0 3px; }}
#mrt-root .mrt-empty {{
  text-align: center; padding: 36px 20px; color: var(--muted); font-size: 12.5px;
}}
</style>

<h2>{title}</h2>
<p class="mrt-subtitle">{subtitle}</p>

<div class="mrt-controls">
  <div class="mrt-cg">
    <div class="mrt-clabel">Rate filter (to_rate must be below)</div>
    <div class="mrt-btn-row">
      <button id="mrt-ball"   class="mrt-active"         onclick="mrtSetLimit('all')">Show all</button>
      <button id="mrt-bgwtc5" class="mrt-lim-gwtc5"      onclick="mrtSetLimit('gwtc5')">GWTC-5 ≤ {limit_gwtc5}</button>
      <button id="mrt-bboco"  class="mrt-lim-boco"       onclick="mrtSetLimit('boco')">Boco ≤ {limit_boco}</button>
    </div>
  </div>
  <div class="mrt-cg">
    <div class="mrt-clabel">Parameter family</div>
    <div class="mrt-btn-row" id="mrt-fam-btns"></div>
  </div>
</div>

<div class="mrt-stats" id="mrt-stats"></div>

<div class="mrt-wrap">
  <table id="mrt-table">
    <thead><tr>
      <th onclick="mrtSort('label')"            data-col="label">          Study / label         <span class="sa">↕</span></th>
      <th onclick="mrtSort('parameter_family')" data-col="parameter_family">Parameter family      <span class="sa">↕</span></th>
      <th onclick="mrtSort('parameter')"        data-col="parameter">      Parameter              <span class="sa">↕</span></th>
      <th onclick="mrtSort('travel_label')"     data-col="travel_label">   Change                 <span class="sa">↕</span></th>
      <th onclick="mrtSort('from_rate')"        data-col="from_rate">      From rate              <span class="sa">↕</span></th>
      <th onclick="mrtSort('to_rate')"          data-col="to_rate">        To rate                <span class="sa">↕</span></th>
      <th onclick="mrtSort('factor')"           data-col="factor">         Reduction factor       <span class="sa">↕</span></th>
    </tr></thead>
    <tbody id="mrt-tbody"></tbody>
  </table>
  <div class="mrt-empty" id="mrt-empty" style="display:none">No rows match the current filters.</div>
</div>
</div>

<script>
(function() {{
  const ROWS  = {rows_json};
  const NAMES = {display_names_json};
  const LIM_GWTC5 = {limit_gwtc5};
  const LIM_BOCO  = {limit_boco};

  function dn(k) {{ return NAMES[k] || k; }}

  const families = ['all', ...new Set(ROWS.map(r => r.parameter_family))];

  let curLimit  = 'all';
  let curFamily = 'all';
  let sortCol   = 'factor';
  let sortAsc   = false;

  // Build family buttons
  const fbContainer = document.getElementById('mrt-fam-btns');
  families.forEach(fam => {{
    const btn = document.createElement('button');
    btn.textContent = fam === 'all' ? 'All families' : dn(fam);
    btn.dataset.fam = fam;
    if (fam === curFamily) btn.classList.add('mrt-active');
    btn.onclick = () => {{ curFamily = fam; render(); }};
    fbContainer.appendChild(btn);
  }});

  function filter(data) {{
    return data.filter(d => {{
      if (curLimit === 'gwtc5' && d.to_rate >= LIM_GWTC5) return false;
      if (curLimit === 'boco'  && d.to_rate >= LIM_BOCO)  return false;
      if (curFamily !== 'all'  && d.parameter_family !== curFamily) return false;
      return true;
    }});
  }}

  function sort(data) {{
    return [...data].sort((a, b) => {{
      let va = a[sortCol], vb = b[sortCol];
      if (typeof va === 'string') {{ va = va.toLowerCase(); vb = vb.toLowerCase(); }}
      if (va < vb) return sortAsc ? -1 :  1;
      if (va > vb) return sortAsc ?  1 : -1;
      return 0;
    }});
  }}

  function rCls(v)  {{ return v > LIM_GWTC5 ? 'r-high' : v > LIM_BOCO ? 'r-mid' : 'r-low'; }}
  function fCls(v)  {{ return v >= 5 ? 'f-high' : v >= 2 ? 'f-mid' : 'f-low'; }}
  function fmt(v)   {{ return v >= 100 ? v.toFixed(0) : v >= 10 ? v.toFixed(1) : v.toFixed(2); }}

  function badges(d) {{
    if (d.to_rate < LIM_BOCO)   return '<span class="badge b-boco">Boco</span>';
    if (d.to_rate < LIM_GWTC5)  return '<span class="badge b-gwtc5">GWTC-5</span>';
    return '';
  }}

  function render() {{
    const visible = sort(filter(ROWS));

    // limit buttons
    ['all','gwtc5','boco'].forEach(k => {{
      const btn = document.getElementById('mrt-b' + k);
      btn.classList.toggle('mrt-active', curLimit === k);
    }});

    // family buttons
    fbContainer.querySelectorAll('button').forEach(btn => {{
      btn.classList.toggle('mrt-active', btn.dataset.fam === curFamily);
    }});

    // sort arrows
    document.querySelectorAll('#mrt-root th[data-col]').forEach(th => {{
      th.classList.toggle('mrt-sorted', th.dataset.col === sortCol);
      const arrow = th.querySelector('.sa');
      arrow.textContent = th.dataset.col === sortCol ? (sortAsc ? '↑' : '↓') : '↕';
    }});

    // stats
    document.getElementById('mrt-stats').innerHTML =
      `Showing <span>${{visible.length}}</span> of <span>${{ROWS.length}}</span> relationships`;

    // rows
    const tbody = document.getElementById('mrt-tbody');
    tbody.innerHTML = '';
    visible.forEach(d => {{
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td class="c-label">${{d.label}}${{badges(d)}}</td>
        <td class="c-family"><span class="ftag">${{dn(d.parameter_family)}}</span></td>
        <td class="c-param">${{d.parameter}}</td>
        <td class="c-travel">${{d.from_value}}<span class="arrow">→</span>${{d.to_value}}</td>
        <td class="c-rate ${{rCls(d.from_rate)}}">${{fmt(d.from_rate)}}</td>
        <td class="c-rate ${{rCls(d.to_rate)}}">${{fmt(d.to_rate)}}</td>
        <td class="c-factor ${{fCls(d.factor)}}">&times;${{fmt(d.factor)}}</td>
      `;
      tbody.appendChild(tr);
    }});

    const empty = document.getElementById('mrt-empty');
    const table = document.getElementById('mrt-table');
    empty.style.display = visible.length === 0 ? 'block' : 'none';
    table.style.display = visible.length === 0 ? 'none'  : '';
  }}

  window.mrtSetLimit = function(k) {{ curLimit = k; render(); }};
  window.mrtSort     = function(col) {{
    if (sortCol === col) sortAsc = !sortAsc;
    else {{ sortCol = col; sortAsc = false; }}
    render();
  }};

  render();
}})();
</script>
"""

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"<!DOCTYPE html><html><head><meta charset='UTF-8'></head><body>{html}</body></html>")
        print(f"Saved to {output_file}")

    display(HTML(html))
