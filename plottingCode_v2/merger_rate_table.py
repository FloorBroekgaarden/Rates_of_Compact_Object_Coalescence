import json
import uuid
import pandas as pd
import numpy as np
from IPython.display import display, HTML

# ── Constants ────────────────────────────────────────────────────────────────
LIMIT_GWTC5 = {
    "BH-BH": 49.4,
    "NS-BH": 32.8,
    "NS-NS": 154.7,
}
LIMIT_GWTC5_DEFAULT = 49.4
LIMIT_BOCO = 20.0

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

DCO_COLORS = {
    "NS-NS":   ("#c678dd", "rgba(198,120,221,0.15)", "rgba(198,120,221,0.4)"),
    "NS-BH":   ("#61afef", "rgba(97,175,239,0.15)",  "rgba(97,175,239,0.4)"),
    "BH-BH":   ("#e5c07b", "rgba(229,192,123,0.15)", "rgba(229,192,123,0.4)"),
    "unknown": ("#6b7897", "rgba(107,120,151,0.15)", "rgba(107,120,151,0.4)"),
}

DCO_ALIASES = {
    "BH-NS": "NS-BH",
    "BHNS":  "NS-BH",
    "BNS":   "NS-NS",
    "BBH":   "BH-BH",
}

def make_merger_rate_table(
    df,
    studies_df          = None,       # optional: studies catalog with study_key + arxiv_url
    label_col           = "label",
    family_col          = "parameter_family",
    parameter_col       = "parameter",
    travel_label_col    = "travel_label",
    from_value_col      = "from_value",
    to_value_col        = "to_value",
    from_rate_col       = "from_rate_Gpc3yr",
    to_rate_col         = "to_rate_Gpc3yr",
    dco_type_col        = "compact_object_type",
    arxiv_url_col       = "arxiv_url",
    study_key_col       = "study_key",
    limit_gwtc5         = LIMIT_GWTC5,
    limit_boco          = LIMIT_BOCO,
    panel_display_names = PANEL_DISPLAY_NAMES,
    title               = "DCO Merger Rate — Model Relationships",
    subtitle            = "Single-parameter variations across BPS studies · rates in Gpc⁻³ yr⁻¹",
    output_file         = None,
):
    """
    Build and display an interactive HTML merger-rate table inside Jupyter.

    Parameters
    ----------
    df : pd.DataFrame
        Relationships dataframe.
    studies_df : pd.DataFrame, optional
        Studies catalog containing study_key and arxiv_url. If provided and
        df doesn't already have arxiv_url, it will be joined on study_key.
    """
    if not isinstance(limit_gwtc5, dict):
        limit_gwtc5 = {"BH-BH": limit_gwtc5, "NS-BH": limit_gwtc5, "NS-NS": limit_gwtc5}

    uid = "mrt_" + uuid.uuid4().hex[:8]

    # ── Join arxiv_url from studies_df if needed ──────────────────────────────
    data = df.copy()
    if arxiv_url_col not in data.columns:
        if studies_df is not None and study_key_col in data.columns and arxiv_url_col in studies_df.columns:
            url_map = (
                studies_df[[study_key_col, arxiv_url_col]]
                .drop_duplicates(subset=[study_key_col])
            )
            data = data.merge(url_map, on=study_key_col, how="left")
        else:
            data[arxiv_url_col] = ""

    # ── Prepare columns ───────────────────────────────────────────────────────
    data[from_rate_col] = pd.to_numeric(data[from_rate_col], errors="coerce")
    data[to_rate_col]   = pd.to_numeric(data[to_rate_col],   errors="coerce")
    data = data.dropna(subset=[from_rate_col, to_rate_col])
    data = data[data[from_rate_col] > 0]
    data = data[data[to_rate_col]   > 0]
    data["_factor"] = data[from_rate_col] / data[to_rate_col]

    rows = []
    for _, r in data.iterrows():
        raw_dco = str(r[dco_type_col]) if dco_type_col in data.columns and pd.notna(r.get(dco_type_col)) else "unknown"
        dco = DCO_ALIASES.get(raw_dco, raw_dco)
        if dco not in ("NS-NS", "NS-BH", "BH-BH"):
            dco = "unknown"

        url = str(r[arxiv_url_col]) if pd.notna(r.get(arxiv_url_col)) else ""
        if url in ("nan", "None", ""):
            url = ""

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
            "dco_type":         dco,
            "lim_gwtc5":        float(limit_gwtc5.get(dco, LIMIT_GWTC5_DEFAULT)),
            "arxiv_url":        url,
        })

    rows_json          = json.dumps(rows)
    display_names_json = json.dumps(panel_display_names)
    dco_colors_json    = json.dumps(DCO_COLORS)
    limit_gwtc5_json   = json.dumps(limit_gwtc5)

    html = f"""
<div id="{uid}">
<style>
#{uid} {{
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
#{uid} h2 {{
  font-size: 16px; font-weight: 600; letter-spacing: .02em;
  color: #e8ecf4; margin-bottom: 3px;
}}
#{uid} .mrt-subtitle {{
  font-size: 11.5px; color: var(--muted); margin-bottom: 18px;
}}
#{uid} .mrt-controls {{
  display: flex; flex-wrap: wrap; gap: 12px 24px;
  margin-bottom: 14px; align-items: flex-start;
}}
#{uid} .mrt-cg {{ display: flex; flex-direction: column; gap: 4px; }}
#{uid} .mrt-clabel {{
  font-size: 10px; font-weight: 700; letter-spacing: .08em;
  text-transform: uppercase; color: var(--muted);
}}
#{uid} .mrt-btn-row {{ display: flex; flex-wrap: wrap; gap: 4px; }}
#{uid} button {{
  background: var(--tag-bg); border: 1px solid var(--border);
  color: var(--text); border-radius: 4px; padding: 3px 10px;
  font-size: 11.5px; font-family: var(--font-body); cursor: pointer;
  transition: background .1s, border-color .1s, color .1s; white-space: nowrap;
}}
#{uid} button:hover {{ border-color: var(--accent); color: #fff; }}
#{uid} button.mrt-active {{
  background: var(--accent); border-color: var(--accent);
  color: #fff; font-weight: 600;
}}
#{uid} button.mrt-active.mrt-lim-gwtc5 {{
  background: var(--accent2); border-color: var(--accent2);
}}
#{uid} button.mrt-active.mrt-lim-boco {{
  background: var(--accent3); border-color: var(--accent3); color: #0e1117;
}}
#{uid} .mrt-divider {{
  width: 1px; background: var(--border); align-self: stretch; margin: 0 4px;
}}
#{uid} .mrt-stats {{
  font-size: 11.5px; color: var(--muted); margin-bottom: 8px;
}}
#{uid} .mrt-stats span {{ color: var(--text); font-weight: 600; }}
#{uid} .mrt-wrap {{
  overflow-x: auto; border: 1px solid var(--border); border-radius: 6px;
}}
#{uid} table {{
  width: 100%; border-collapse: collapse; font-size: 12px;
}}
#{uid} thead tr {{
  background: var(--surface); border-bottom: 1px solid var(--border);
}}
#{uid} th {{
  padding: 7px 11px; text-align: left; font-size: 10px; font-weight: 700;
  letter-spacing: .07em; text-transform: uppercase; color: var(--muted);
  white-space: nowrap; cursor: pointer; user-select: none;
}}
#{uid} th:hover {{ color: var(--accent); }}
#{uid} th .sa {{ margin-left: 3px; opacity: .4; font-size: 10px; }}
#{uid} th.mrt-sorted .sa {{ opacity: 1; color: var(--accent); }}
#{uid} tbody tr {{ border-bottom: 1px solid var(--border); transition: background .07s; }}
#{uid} tbody tr:last-child {{ border-bottom: none; }}
#{uid} tbody tr:hover {{ background: var(--surface); }}
#{uid} td {{ padding: 6px 11px; vertical-align: middle; white-space: nowrap; }}
#{uid} .c-label  {{ font-family: var(--font-mono); font-size: 11px; color: #c4c9d6; max-width: 220px; white-space: normal; word-break: break-word; }}
#{uid} .c-family {{ max-width: 170px; white-space: normal; }}
#{uid} .c-param  {{ font-family: var(--font-mono); font-size: 11px; color: #a8b1c7; }}
#{uid} .c-travel {{ font-family: var(--font-mono); font-size: 11px; }}
#{uid} .c-rate   {{ font-family: var(--font-mono); font-size: 11.5px; text-align: right; }}
#{uid} .c-factor {{ font-family: var(--font-mono); font-size: 11.5px; text-align: right; font-weight: 600; }}
#{uid} .c-dco    {{ text-align: center; }}
#{uid} .ftag {{
  display: inline-block; background: var(--tag-bg);
  border: 1px solid var(--border); border-radius: 3px;
  padding: 1px 6px; font-size: 11px; color: var(--text); white-space: nowrap;
}}
#{uid} .r-high {{ color: var(--accent2); }}
#{uid} .r-mid  {{ color: var(--text); }}
#{uid} .r-low  {{ color: var(--accent3); }}
#{uid} .f-high {{ color: var(--accent2); }}
#{uid} .f-mid  {{ color: var(--text); }}
#{uid} .f-low  {{ color: var(--accent3); }}
#{uid} .badge {{
  display: inline-block; border-radius: 3px; padding: 1px 5px;
  font-size: 9.5px; font-weight: 700; margin-left: 4px; vertical-align: middle;
}}
#{uid} .b-gwtc5 {{ background: rgba(224,108,117,.18); color: var(--accent2); border: 1px solid rgba(224,108,117,.4); }}
#{uid} .b-boco  {{ background: rgba(152,195,121,.15); color: var(--accent3); border: 1px solid rgba(152,195,121,.4); }}
#{uid} .dco-pill {{
  display: inline-block; border-radius: 3px; padding: 1px 7px;
  font-size: 10.5px; font-weight: 700; font-family: var(--font-mono); white-space: nowrap;
}}
#{uid} .arrow {{ color: var(--muted); margin: 0 3px; }}
#{uid} .c-label a {{
  color: inherit; text-decoration: none;
  border-bottom: 1px dashed var(--muted);
  transition: color .1s, border-color .1s;
}}
#{uid} .c-label a:hover {{ color: var(--accent); border-color: var(--accent); }}
#{uid} .mrt-empty {{
  text-align: center; padding: 36px 20px; color: var(--muted); font-size: 12.5px;
}}
</style>

<h2>{title}</h2>
<p class="mrt-subtitle">{subtitle}</p>

<div class="mrt-controls">
  <div class="mrt-cg">
    <div class="mrt-clabel">DCO type</div>
    <div class="mrt-btn-row" id="{uid}_dco_btns"></div>
  </div>
  <div class="mrt-divider"></div>
  <div class="mrt-cg">
    <div class="mrt-clabel">Rate filter (to_rate &lt; limit)</div>
    <div class="mrt-btn-row">
      <button id="{uid}_ball"   class="mrt-active"    onclick="{uid}_setLimit('all')">Show all</button>
      <button id="{uid}_bgwtc5" class="mrt-lim-gwtc5" onclick="{uid}_setLimit('gwtc5')">GWTC-5 upper limit</button>
      <button id="{uid}_bboco"  class="mrt-lim-boco"  onclick="{uid}_setLimit('boco')">&lt; 20 Gpc\u207b\u00b3 yr\u207b\u00b9</button>
    </div>
  </div>
  <div class="mrt-divider"></div>
  <div class="mrt-cg">
    <div class="mrt-clabel">Parameter family</div>
    <div class="mrt-btn-row" id="{uid}_fam_btns"></div>
  </div>
</div>

<div class="mrt-stats" id="{uid}_stats"></div>

<div class="mrt-wrap">
  <table id="{uid}_table">
    <thead><tr>
      <th onclick="{uid}_sort('dco_type')"         data-col="dco_type">        Type                   <span class="sa">\u2195</span></th>
      <th onclick="{uid}_sort('label')"            data-col="label">           Study / label           <span class="sa">\u2195</span></th>
      <th onclick="{uid}_sort('parameter_family')" data-col="parameter_family">Parameter family        <span class="sa">\u2195</span></th>
      <th onclick="{uid}_sort('parameter')"        data-col="parameter">       Parameter               <span class="sa">\u2195</span></th>
      <th onclick="{uid}_sort('travel_label')"     data-col="travel_label">    Change                  <span class="sa">\u2195</span></th>
      <th onclick="{uid}_sort('from_rate')"        data-col="from_rate">       From rate               <span class="sa">\u2195</span></th>
      <th onclick="{uid}_sort('to_rate')"          data-col="to_rate">         To rate                 <span class="sa">\u2195</span></th>
      <th onclick="{uid}_sort('factor')"           data-col="factor">          Reduction factor        <span class="sa">\u2195</span></th>
    </tr></thead>
    <tbody id="{uid}_tbody"></tbody>
  </table>
  <div class="mrt-empty" id="{uid}_empty" style="display:none">No rows match the current filters.</div>
</div>
</div>

<script>
(function() {{
  const ROWS       = {rows_json};
  const NAMES      = {display_names_json};
  const DCO_COLORS = {dco_colors_json};
  const LIM_GWTC5  = {limit_gwtc5_json};
  const LIM_BOCO   = {limit_boco};
  const ROOT       = document.getElementById('{uid}');

  function q(id) {{ return document.getElementById(id); }}
  function dn(k) {{ return NAMES[k] || k; }}

  const DCO_ORDER   = ["NS-NS", "NS-BH", "BH-BH", "unknown"];
  const presentDCOs = DCO_ORDER.filter(t => ROWS.some(r => r.dco_type === t));
  const dcoTypes    = ['all', ...presentDCOs];
  const families    = ['all', ...new Set(ROWS.map(r => r.parameter_family))];

  let curLimit  = 'all';
  let curFamily = 'all';
  let curDCO    = 'all';
  let sortCol   = 'factor';
  let sortAsc   = false;

  // ── DCO buttons ───────────────────────────────────────────────────────────
  const dcoContainer = q('{uid}_dco_btns');
  dcoTypes.forEach(t => {{
    const btn = document.createElement('button');
    if (t === 'all') {{
      btn.textContent = 'All types';
      btn.classList.add('mrt-active');
    }} else {{
      const lim = LIM_GWTC5[t];
      btn.textContent = lim !== undefined ? `${{t}} (GWTC-5 \u2264 ${{lim}})` : t;
      const c = DCO_COLORS[t];
      if (c) {{ btn.style.borderColor = c[0]; btn.style.color = c[0]; }}
    }}
    btn.dataset.dco = t;
    btn.onclick = () => {{ curDCO = t; render(); }};
    dcoContainer.appendChild(btn);
  }});

  // ── Family buttons ────────────────────────────────────────────────────────
  const fbContainer = q('{uid}_fam_btns');
  families.forEach(fam => {{
    const btn = document.createElement('button');
    btn.textContent = fam === 'all' ? 'All families' : dn(fam);
    btn.dataset.fam = fam;
    if (fam === curFamily) btn.classList.add('mrt-active');
    btn.onclick = () => {{ curFamily = fam; render(); }};
    fbContainer.appendChild(btn);
  }});

  // ── Filter & sort ─────────────────────────────────────────────────────────
  function filter(data) {{
    return data.filter(d => {{
      if (curDCO    !== 'all'   && d.dco_type         !== curDCO)     return false;
      if (curLimit  === 'gwtc5' && d.to_rate          >= d.lim_gwtc5) return false;
      if (curLimit  === 'boco'  && d.to_rate          >= LIM_BOCO)    return false;
      if (curFamily !== 'all'   && d.parameter_family !== curFamily)  return false;
      return true;
    }});
  }}

  function sortRows(data) {{
    return [...data].sort((a, b) => {{
      let va = a[sortCol], vb = b[sortCol];
      if (typeof va === 'string') {{ va = va.toLowerCase(); vb = vb.toLowerCase(); }}
      if (va < vb) return sortAsc ? -1 :  1;
      if (va > vb) return sortAsc ?  1 : -1;
      return 0;
    }});
  }}

  function rCls(v, lim) {{ return v > lim ? 'r-high' : v > LIM_BOCO ? 'r-mid' : 'r-low'; }}
  function fCls(v)      {{ return v >= 5 ? 'f-high' : v >= 2 ? 'f-mid' : 'f-low'; }}
  function fmt(v)       {{ return v >= 100 ? v.toFixed(0) : v >= 10 ? v.toFixed(1) : v.toFixed(2); }}

  function limitBadge(d) {{
    if (d.to_rate < LIM_BOCO)    return '<span class="badge b-boco">&lt;20</span>';
    if (d.to_rate < d.lim_gwtc5) return '<span class="badge b-gwtc5">GWTC-5</span>';
    return '';
  }}

  function dcoPill(t) {{
    const c = DCO_COLORS[t] || DCO_COLORS['unknown'];
    return `<span class="dco-pill" style="color:${{c[0]}};background:${{c[1]}};border:1px solid ${{c[2]}}">${{t}}</span>`;
  }}

  function render() {{
    const visible = sortRows(filter(ROWS));

    // DCO buttons
    dcoContainer.querySelectorAll('button').forEach(btn => {{
      const isActive = btn.dataset.dco === curDCO;
      btn.classList.toggle('mrt-active', isActive);
      const t = btn.dataset.dco;
      const c = DCO_COLORS[t];
      if (t !== 'all' && c) {{
        btn.style.background  = isActive ? c[0] : '';
        btn.style.borderColor = c[0];
        btn.style.color       = isActive ? '#0e1117' : c[0];
        btn.style.fontWeight  = isActive ? '700' : '';
      }}
    }});

    ['all','gwtc5','boco'].forEach(k => {{
      q('{uid}_b' + k).classList.toggle('mrt-active', curLimit === k);
    }});

    fbContainer.querySelectorAll('button').forEach(btn => {{
      btn.classList.toggle('mrt-active', btn.dataset.fam === curFamily);
    }});

    ROOT.querySelectorAll('th[data-col]').forEach(th => {{
      th.classList.toggle('mrt-sorted', th.dataset.col === sortCol);
      th.querySelector('.sa').textContent =
        th.dataset.col === sortCol ? (sortAsc ? '\u2191' : '\u2193') : '\u2195';
    }});

    q('{uid}_stats').innerHTML =
      `Showing <span>${{visible.length}}</span> of <span>${{ROWS.length}}</span> relationships`;

    const tbody = q('{uid}_tbody');
    tbody.innerHTML = '';
    visible.forEach(d => {{
      const tr = document.createElement('tr');
      const labelCell = d.arxiv_url
        ? `<a href="${{d.arxiv_url}}" target="_blank" rel="noopener">${{d.label}}</a>`
        : d.label;
      tr.innerHTML = `
        <td class="c-dco">${{dcoPill(d.dco_type)}}</td>
        <td class="c-label">${{labelCell}}${{limitBadge(d)}}</td>
        <td class="c-family"><span class="ftag">${{dn(d.parameter_family)}}</span></td>
        <td class="c-param">${{d.parameter}}</td>
        <td class="c-travel">${{d.from_value}}<span class="arrow">\u2192</span>${{d.to_value}}</td>
        <td class="c-rate ${{rCls(d.from_rate, d.lim_gwtc5)}}">${{fmt(d.from_rate)}}</td>
        <td class="c-rate ${{rCls(d.to_rate,   d.lim_gwtc5)}}">${{fmt(d.to_rate)}}</td>
        <td class="c-factor ${{fCls(d.factor)}}">\u00d7${{fmt(d.factor)}}</td>
      `;
      tbody.appendChild(tr);
    }});

    q('{uid}_empty').style.display = visible.length === 0 ? 'block' : 'none';
    q('{uid}_table').style.display = visible.length === 0 ? 'none'  : '';
  }}

  window['{uid}_setLimit'] = k   => {{ curLimit = k;  render(); }};
  window['{uid}_sort']     = col => {{
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
