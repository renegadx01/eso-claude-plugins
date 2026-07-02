# render_eow_individual.py — formatting locked 2026.06.12. Styling is the standard; only the week data block changes.
# Brand bands header_band.png/footer_band.png live in ../assets/.

# -*- coding: utf-8 -*-
import base64, html
from weasyprint import HTML
def b64(p): return "data:image/png;base64,"+base64.b64encode(open(p,"rb").read()).decode()
HEADER=b64("header_band.png"); FOOTER=b64("footer_band.png")
def e(t): return html.escape(str(t), quote=False)
PHASES=["PD","SD","DD","CD","CA"]
import eow_hours as EH
ROLE="Associate"   # sample person; sets the hours tier (scripts/capacity.json)

# ============================================================================
# SAMPLE WEEK DATA BELOW — FORMAT REFERENCE ONLY (fictional "Sample Employee",
# wk 06/12/2026). All names/projects here are made up. To produce a REAL report,
# REPLACE every data block below with the current person's interview answers and
# set SAMPLE_DATA = False. Do not ship the sample.
# ============================================================================
SAMPLE_DATA = True

projects=[
 {"name":"Project Alpha","phase":"DD","pace":"Heavy (6)","pace_unlock":None,"budget":"On Track","hrs":"32",
  "outcomes":["Coordinated with the structural consultant on the canopy detail and roof design.",
   "Advanced DD documentation — plans, exterior elevations, sections, and door/window schedules.",
   "Responded to the landscape consultant on the courtyard layout (sent plan and screenshots).",
   "Ordered the site utility test."],
  "look":["Continue documenting and layering detail into the set (ongoing).",
   "Doc-set check-in with the PM to define what “complete” looks like — Jun 16."],
  "look_para":None,
  "risk":None,
  "barriers":[("Roof documentation blocked pending the roof-type decision","PM","~30-min review and decision","6/15")],
  "mkw":{"kind":"action","ask":"Decide the roof type — option A vs option B.","time":"~30 min with the PM","by":"Mon 6/15","prio":"This week","owner":"PM"},
  "ms":"Permit set — week of 7/13"},

 {"name":"Internal Tooling","phase":"Internal","pace":"Light (3)","pace_unlock":None,"budget":"N/A","hrs":"8",
  "outcomes":["Landed an approach to connect the new workflow plugin for efficiency, with a clear path to roll it out to the team."],
  "look":None,
  "look_para":"Present the workflow (phase one) to the team the week of 6/15, refine it from their feedback, and begin extending the same approach to the next two areas.",
  "risk":"Competing project priorities could push this back, though it stands to save the team significant time.",
  "barriers":[],
  "mkw":{"kind":"action","ask":"A 15-min review of the rollout, plus a short discussion on direction and time allocation going forward.","time":"~45 min total","by":"Before the rollout (week of 6/15)","prio":"When available","owner":"PM"},
  "ms":"Team rollout — week of 6/15"},

 {"name":"Project Beta","phase":"PD","pace":"Hold (1)","pace_unlock":"County green-lights us (no zoning issue)","budget":"On Track","hrs":"0.5",
  "outcomes":["Confirmed impervious-cover rules under the code; shared in the project team chat."],
  "look":["Contact the consultant about the county-submission plan — after Jun 16.",
   "⚑ Verify whether a prior submittal already went in — status unknown."],
  "look_para":None,
  "risk":None,
  "barriers":[("On hold pending county zoning confirmation","County (self following up)","Submit to county, await zoning review","⚑ TBD — pending county")],
  "mkw":{"kind":"action","ask":"Confirm who owns Project Beta going forward.","time":"a few min","by":"When available","prio":"When available","owner":"PM"},
  "ms":"Submit to county — 6/15  ⚑ (verify prior submittal)"},

 {"name":"Project Gamma","phase":"PD","pace":"Hold (1)","pace_unlock":"HOA CC&R / ARC documents received (to confirm the ADU is feasible)","budget":"On Track","hrs":"0.5",
  "outcomes":["Called the HOA and requested the CC&R and ARC documents; reached the right contact, awaiting their callback."],
  "look":["Follow up with the HOA on the CC&R / ARC documents (self owns this chase) — next week.","Schematic Design on-site meeting with the client — Jun 25."],
  "look_para":None,
  "risk":None,
  "barriers":[("HOA CC&R / ARC documents not yet in hand — needed before the 6/25 SD meeting; fallback is asking the owner directly (not ideal)","Self","Follow up with HOA next week / obtain documents","This week")],
  "mkw":None,
  "ms":"Schematic Design on-site meeting — Jun 25"},

 {"name":"Internal Ops","phase":"Internal","pace":"Maintenance (2)","pace_unlock":None,"budget":"N/A","hrs":"1",
  "outcomes":["Connected a teammate to the modeling server (~45 min).",
   "Recovered own computer after a crash — fully resolved."],
  "look":["None."],
  "look_para":None,
  "risk":None,
  "barriers":[],
  "mkw":{"kind":"fyi","ask":"Interested in becoming secondary IT support for on-site troubleshooting when the lead is unavailable."},
  "ms":"Ongoing internal operations — no discrete milestone"},
]

# Sheet A — reported actuals this week: (project, reported_hrs, stated_pace)
reported=[("Project Alpha",32,"Heavy"),("Internal Tooling",8,"Light"),
 ("Internal Ops",1,"Maintenance"),("Project Beta",0.5,"Hold"),("Project Gamma",0.5,"Hold")]
# Last week's Sheet B allocation, by project (— if none on file). First week: none.
prior_alloc={}
# Sheet B — next-week pace per project (drives auto-allocation). Temp paces stay locked
# to their lever milestone, so Beta/Gamma remain on Hold this look-ahead.
next_pace=[("Project Alpha",6),("Internal Tooling",3),("Internal Ops",2),
 ("Project Beta",1),("Project Gamma",1)]
lever_status={"Project Beta":"Hold · lever: submit to county (open)",
 "Project Gamma":"Hold · lever: HOA CC&R/ARC docs (open)"}
wins="Rolled out the first team workflow project — usable by the team immediately."
watch="Project Gamma not receiving the ARC / CC&R documents before the 6/25 Schematic Design meeting."
focus=("~20 hrs Project Alpha documentation; 8–10 hrs Internal Tooling; "
 "Project Delta schematic design 4 hrs; Project Epsilon 4 hrs; Gamma 1 hr; Project Zeta 6 hrs.")

def phase_badge(ph):
    if not ph: return ""
    if ph in PHASES:
        ci=PHASES.index(ph)
        return '<span class="phasebar">'+''.join(
          f'<span class="seg {"done" if i<ci else ("cur" if i==ci else "todo")}">{p}</span>' for i,p in enumerate(PHASES))+'</span>'
    return f'<span class="intbadge">{e(ph)}</span>'
def bpill(b):
    if not b or b=="N/A": return ""
    c={"On Track":"green","Monitor":"yellow","Concern":"red","Critical":"red"}.get(b,"gray")
    return f'<span class="pill {c}">{e(b)}</span>'
def prio(p):
    c={"Urgent":"red","This week":"yellow","When available":"green","FYI":"gray"}.get(p,"gray")
    return f'<span class="pill {c}">{e(p)}</span>'

blocks=""
for pr in projects:
    pace=""
    if pr.get("pace"):
        pace=f'Pace: <b>{e(pr["pace"])}</b>'
        if pr.get("pace_unlock"): pace+=f' <span class="unlock">· unlocks when {e(pr["pace_unlock"])}</span>'
    pace_html=f'<span class="pace">{pace}</span>' if pace else ""
    outs="".join(f"<div class='ditem'>– {e(o)}</div>" for o in pr["outcomes"])
    if pr["look_para"]:
        look=f'<p class="body">{e(pr["look_para"])}</p>'
    else:
        look="".join(f"<div class='ditem'>– {e(o)}</div>" for o in pr["look"])
    if pr["barriers"]:
        brows="".join(f"<tr><td>{e(b)}</td><td>{e(o)}</td><td>{e(rp)}</td><td class='nw'>{e(d)}</td></tr>" for (b,o,rp,d) in pr["barriers"])
        barr=f"<table class='mini'><tr><th>Barrier</th><th>Owner</th><th>Resolution path</th><th>Target</th></tr>{brows}</table>"
    else:
        barr="<p class='muted'>None.</p>"
    risk=f'<div class="risk">{e(pr["risk"])}</div>' if pr["risk"] else ""
    # MKW items: None, a single dict, or a list of dicts. Each is kind "action" or "fyi".
    raw=pr["mkw"]
    items=[] if not raw else (raw if isinstance(raw,list) else [raw])
    if items:
        parts=[]
        for m in items:
            if m.get("kind")=="fyi":
                parts.append(f'<div class="mkw fyi"><div class="mkwhead">MKW — FYI</div><div>{e(m["ask"])}</div></div>')
            else:
                parts.append(f'<div class="mkw"><div class="mkwhead">MKW — ACTION</div><div>{e(m["ask"])}</div>'
                     f'<div class="mkwmeta">Maggie’s time: <b>{e(m["time"])}</b> &nbsp;·&nbsp; By: <b>{e(m["by"])}</b> &nbsp;·&nbsp; {prio(m["prio"])} &nbsp;·&nbsp; Owner: {e(m["owner"])}</div></div>')
        mkw="".join(parts)
    else:
        mkw='<div class="mkw none"><div class="mkwhead">MKW</div><div class="muted">Nothing for Maggie this week.</div></div>'
    blocks+=f"""
    <div class="proj">
      <div class="phead"><span class="pname">{e(pr['name'])}</span><span class="hrs">{e(pr['hrs'])} hrs</span></div>
      <div class="pbody">
        <div class="badges">{phase_badge(pr.get('phase'))} {pace_html} {bpill(pr.get('budget'))}</div>
        <div class="lbl">This Week — Outcomes</div>{outs}
        <div class="lbl">Look Ahead</div>{look}
        <div class="lbl">Barriers</div>{barr}
        {risk}
        {mkw}
        <div class="lbl">Next Milestone</div><p class="ms">{e(pr['ms'])}</p>
      </div>
    </div>"""

def _fmt(x): return f"{x:g}" if isinstance(x,(int,float)) else str(x)
# Sheet A rows
arows=""; rep_total=0.0; alloc_total=0.0; have_prior=False
for (n,hrs,stated) in reported:
    rep_total+=hrs
    if EH.is_overhead(ROLE):
        implied,ok,note="—",True,"overhead"   # Operations Manager: no pace, no implied-pace check
    else:
        implied,ok,note=EH.report_check(stated,hrs,ROLE)
    al=prior_alloc.get(n)
    if al is not None: have_prior=True; alloc_total+=al; var=f"{hrs-al:+g}"; al_disp=_fmt(al)
    else: var="—"; al_disp="—"
    chk="✓" if ok else "⚑ mismatch"
    arows+=(f"<tr><td class='proj-c'>{e(n)}</td><td>{e(stated)}</td><td class='nw'>{_fmt(hrs)}</td>"
            f"<td>{e(implied)}</td><td class='{'muted' if ok else ''}'>{e(chk)}</td>"
            f"<td class='nw'>{e(al_disp)}</td><td class='nw'>{e(var)}</td></tr>")
util=EH.utilization(rep_total); over_flag=EH.reported_overflow(rep_total,"Sample Employee")
util_line=f"Utilization: {_fmt(rep_total)} / 40 = {util}%" + (f" &nbsp; <b>⚑ over actual time — flag to MKW</b>" if over_flag else "")
alloc_total_disp=_fmt(alloc_total) if have_prior else "—"

# Sheet B rows (engine-driven)
B=EH.allocate(next_pace, ROLE, "Sample Employee")
brows=""
for (proj,hrs,pacename,_note) in B["rows"]:
    brows+=(f"<tr><td class='proj-c'>{e(proj)}</td><td>{e(pacename)}</td>"
            f"<td class='nw'>{_fmt(hrs)}</td><td class='muted'>{e(lever_status.get(proj,'—'))}</td></tr>")
cap_note=B["capacity_note"]

CSS="""
@page { size: Letter; margin: 2.65cm 1.45cm 1.95cm 1.45cm; }
#hdr{position:fixed;top:-2.2cm;left:0;right:0;} #ftr{position:fixed;bottom:-1.55cm;left:0;right:0;}
#hdr img,#ftr img{width:100%;display:block;}
*{box-sizing:border-box;}
body{font-family:'Mabry Pro','Helvetica Neue',Arial,sans-serif;color:#1a1a1a;font-size:9.2pt;line-height:1.4;margin:0;}
h1{font-size:15pt;margin:0 0 2px 0;}
.sub{font-size:8.4pt;color:#6f6f6f;font-style:italic;margin:0 0 12px 0;padding-bottom:8px;border-bottom:1.4px solid #1a1a1a;}
.proj{break-inside:auto;border:.7px solid #cfcfcf;margin-bottom:13px;}
.phead{background:#1a1a1a;color:#fff;display:flex;justify-content:space-between;align-items:center;padding:6px 12px;break-after:avoid;}
.pname{font-size:11.5pt;font-weight:700;letter-spacing:.3px;}
.pbody{padding:8px 12px 10px 12px;}
.body{margin:2px 0 4px 0;color:#474747;} .ditem{color:#474747;margin:1.5px 0;padding-left:12px;text-indent:-12px;}

.hrs{font-size:8pt;font-weight:700;color:#1a1a1a;background:#c9d646;border-radius:9px;padding:1px 10px;}
.badges{display:flex;align-items:center;gap:9px;margin-bottom:6px;flex-wrap:wrap;}
.pace{font-size:8.4pt;} .unlock{color:#6f6f6f;font-style:italic;font-size:8pt;}
.lbl{font-size:8pt;text-transform:uppercase;letter-spacing:.5px;color:#111;font-weight:800;margin:8px 0 2px 0;}
ul{margin:2px 0;padding-left:16px;} li{margin-bottom:1px;} p{margin:3px 0;}
.lookp{margin:2px 0;} .muted{color:#9a9a9a;}
.ms{font-weight:600;}
.risk{background:#fbf4e6;border:.6px solid #ecd9a8;border-radius:4px;padding:4px 9px;margin:6px 0;font-size:8.6pt;}
table.mini,table.hours{width:100%;border-collapse:collapse;margin:2px 0;}
table.mini th,table.hours th{background:#efefef;text-align:left;font-size:7.4pt;text-transform:uppercase;padding:3px 6px;border:.5px solid #cfcfcf;}
table.mini td,table.hours td{padding:3px 6px;border:.5px solid #ddd;vertical-align:top;font-size:8.6pt;} table.mini,.mkw,.risk{break-inside:avoid;} .ptitle{break-after:avoid;}
.nw{white-space:nowrap;} .proj-c{font-weight:700;}
.pill{display:inline-block;padding:2px 9px;border-radius:9px;font-size:7.8pt;font-weight:600;}
.pill.green{background:#dce9d5;}.pill.yellow{background:#fbe9c9;}.pill.red{background:#f5d5ce;}.pill.gray{background:#efefef;}
.phasebar{display:inline-flex;gap:2px;} .seg{font-size:6.8pt;font-weight:700;padding:2px 4px;border-radius:3px;min-width:17px;text-align:center;}
.seg.done{background:#1a1a1a;color:#fff;}.seg.cur{background:#c9d646;color:#1a1a1a;}.seg.todo{background:#ededed;color:#bdbdbd;}
.intbadge{font-size:7pt;font-weight:700;background:#e7ecd6;color:#5b6b22;border-radius:3px;padding:2px 7px;letter-spacing:.4px;}
.mkw{background:#faf3e3;border:.7px solid #ecd9a8;border-radius:4px;padding:6px 9px;margin:6px 0;}
.mkw.none{background:#f7f7f7;border-color:#e4e4e4;}
.mkw.fyi{background:#f2f2f2;border-color:#dcdcdc;} .mkw.fyi .mkwhead{color:#6f6f6f;}
.mkwhead{font-size:7.4pt;font-weight:700;letter-spacing:.4px;color:#8a6d1f;margin-bottom:2px;}
.mkw.none .mkwhead{color:#9a9a9a;} .mkwmeta{font-size:8.1pt;margin-top:3px;}
h2{font-size:10.4pt;text-transform:uppercase;letter-spacing:.4px;margin:15px 0 5px 0;padding-bottom:3px;border-bottom:1.4px solid #1a1a1a;}
.fwrap{break-inside:avoid;border:.7px solid #d9d9d9;border-radius:4px;padding:7px 11px;margin-bottom:8px;}
.fwrap .lbl{margin-top:0;}
"""
DOC=f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div id="hdr"><img src="{HEADER}"></div><div id="ftr"><img src="{FOOTER}"></div>
<h1>END OF WEEK REPORT</h1>
<p class="sub">Submitted by Sample Employee &nbsp;·&nbsp; Week ending 06/12/2026</p>
{blocks}
<h2>Sheet A — Hours Reported (this week)</h2>
<table class="hours"><tr><th>Project</th><th>Pace stated</th><th>Reported</th><th>Implied pace</th><th>Check</th><th>Alloc last wk</th><th>Variance</th></tr>
{arows}
<tr><td class="proj-c">Total</td><td></td><td class="nw"><b>{rep_total:g}</b></td><td></td><td></td><td class="nw">{alloc_total_disp}</td><td></td></tr>
</table>
<p class="sub" style="border:none;padding:0;margin:4px 0 12px 0;">{util_line}</p>
<h2>Sheet B — Hours Allocated, Next Week</h2>
<table class="hours"><tr><th>Project</th><th>Next-wk pace</th><th>Allocated</th><th>Temp — lever / status</th></tr>
{brows}
<tr><td class="proj-c">Total</td><td></td><td class="nw"><b>{B['total']:g}</b></td><td class="muted">{cap_note}</td></tr>
</table>
<h2>Wins / Watch / Focus</h2>
<div class="fwrap"><div class="lbl">Win this week</div><p>{e(wins)}</p></div>
<div class="fwrap"><div class="lbl">Watch / risk</div><p>{e(watch)}</p></div>
<div class="fwrap"><div class="lbl">Focus next week</div><p>{e(focus)}</p></div>
</body></html>"""
_suffix = "_SAMPLE_DO_NOT_SEND" if SAMPLE_DATA else ""
if SAMPLE_DATA:
    print("WARNING: SAMPLE_DATA is True — this renders the FORMAT SAMPLE, not a real report. "
          "Replace the data blocks with interview answers and set SAMPLE_DATA=False.")
open(f"eow_individual{_suffix}.html","w",encoding="utf-8").write(DOC)
HTML(string=DOC,base_url=".").write_pdf(f"EOW_Report_Employee_06.12.2026{_suffix}.pdf")
print("rendered", _suffix or "(real report)")
