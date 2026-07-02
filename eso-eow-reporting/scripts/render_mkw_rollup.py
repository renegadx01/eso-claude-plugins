# render_mkw_rollup.py — formatting locked 2026.06.12. Styling/rules are the standard.
# CHANGE (2026.06.19): the Milestone Timeline (Section 4) is now built INLINE on every
# run from the persistent milestone store (eow_milestones.py), not a pre-baked PNG.
# It draws all OPEN milestones (carry over week to week until completed) and HARD-FAILS
# if the open set is empty, so a rollup can never ship without Section 4.
# Timeline = deadlines/milestones ONLY (no actions/tasks). Bands in ../assets/.

# -*- coding: utf-8 -*-
import base64, html, os
from datetime import date, timedelta
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from weasyprint import HTML
from eow_milestones import load_all_stores, timeline_points
import eow_hours as EH
import eow_paths

# ---- week + store -----------------------------------------------------------
WEEK_END = date(2026, 6, 12)          # set to the week-ending each run
# Real runs: point BASE_DIR at the shared EOW folder. The rollup reads EVERY
# per-person store under <BASE_DIR>/stores/milestones_*.json and merges them.
# The skill ships only a fictional sample store there for the format reference.
BASE_DIR = "."

def b64(p): return "data:image/png;base64,"+base64.b64encode(open(p,"rb").read()).decode()
def e(t): return html.escape(str(t),quote=False)

# ---- inline timeline build (replaces the old baked rollup_tl_0612.png) ------
INK="#1a1a1a";GRAY="#9a9a9a";LIME="#c9d646"

def build_timeline(points, week_end, out="rollup_tl.png"):
    # Hard guard: open milestones always exist by firm rule. Empty => data problem.
    assert points, ("TIMELINE EMPTY: no OPEN milestones in the store. Open milestones "
                    "carry over until completed and should never be empty — fix the "
                    "store; do not ship a rollup without Section 4.")
    ms = sorted(points, key=lambda m: m[0])
    MIN_GAP=8
    last={1:None,-1:None}; lvl={1:0,-1:0}; side=1; placed=[]
    for d,lab,key in ms:
        s=side
        if last[s] is not None and (d-last[s]).days < MIN_GAP: lvl[s]+=1
        else: lvl[s]=1
        level=s*(0.95+1.05*(lvl[s]-1))
        placed.append((d,lab,key,level)); last[s]=d; side=-side
    maxlev=max(abs(l) for *_,l in placed)

    fig,ax=plt.subplots(figsize=(11,2.7+0.5*maxlev),dpi=200)
    ax.axhline(0,color=INK,lw=1.4,zorder=1)
    for d,lab,key,level in placed:
        # Connector: lime + heavier for KEY milestones, gray + thin for the rest.
        ax.vlines([d],0,level,color=(LIME if key else GRAY),lw=1.9 if key else 1.0,zorder=2)
        if key:
            # Layered ring + filled lime dot so key milestones read instantly.
            ax.plot([d],[0],"o",color="none",ms=22,markeredgecolor=LIME,markeredgewidth=2.4,zorder=3)
            ax.plot([d],[0],"o",color=LIME,ms=13,markeredgecolor=INK,markeredgewidth=1.4,zorder=4)
        else:
            ax.plot([d],[0],"o",color=INK,ms=6,markeredgewidth=0,zorder=4)
        label=("\u2605 " if key else "")+d.strftime("%-m/%-d")+"\n"+lab
        ann=ax.annotate(label,xy=(d,level),ha="center",
                    va="bottom" if level>0 else "top",fontsize=9.2 if key else 8.3,
                    fontweight="bold" if key else "normal",color=INK,linespacing=1.3,zorder=6)
        if key:
            # Soft lime highlight box behind the key label.
            ann.set_bbox(dict(boxstyle="round,pad=0.32",facecolor="#eef3ce",
                              edgecolor=LIME,linewidth=0.9))
    ax.set_ylim(-(maxlev+1.3),(maxlev+1.3))
    # window auto-fits this week's open set instead of a hardcoded range
    ax.set_xlim(week_end, max(d for d,_,_ in ms)+timedelta(days=5))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=10))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-m/%-d"))
    ax.tick_params(axis="x",labelsize=8,length=3,colors=INK);ax.get_yaxis().set_visible(False)
    for sp in ["left","top","right","bottom"]: ax.spines[sp].set_visible(False)
    plt.tight_layout();plt.savefig(out,transparent=True,bbox_inches="tight");plt.close(fig)
    return out

HEADER=b64("header_band.png");FOOTER=b64("footer_band.png")
TL_PATH=build_timeline(timeline_points(load_all_stores(BASE_DIR)), WEEK_END)
assert os.path.exists(TL_PATH), "timeline PNG missing — render aborted"
TL=b64(TL_PATH)

# ---- week data (unchanged: only this stuff changes week to week) ------------
PHASES=["PD","SD","DD","CD","CA"]
def phase_badge(ph):
    if not ph: return ""
    if ph in PHASES:
        ci=PHASES.index(ph)
        return '<span class="phasebar">'+''.join(f'<span class="seg {"done" if i<ci else ("cur" if i==ci else "todo")}">{p}</span>' for i,p in enumerate(PHASES))+'</span>'
    return f'<span class="intbadge">{e(ph)}</span>'
def bpill(b):
    c={"On Track":"green","Monitor":"yellow","Concern":"red","Critical":"red"}.get(b,"gray");return f'<span class="pill {c}">{e(b)}</span>'
def chip(p):
    c={"Urgent":"red","This week":"yellow","When available":"green","FYI":"gray"}.get(p,"gray");return f'<span class="chip {c}">{e(p)}</span>'

# ============================================================================
# SAMPLE WEEK DATA BELOW — FORMAT REFERENCE ONLY (fictional, wk 06/12/2026).
# To build a REAL rollup, REPLACE every data block (actions, cal, dash, watch,
# wins, team, people_hours) with the consolidated values from the uploaded
# individual reports, then set SAMPLE_DATA = False. Do not ship the sample.
# ============================================================================
SAMPLE_DATA = True

# Section 1 is SPLIT: Action Required (priority-sorted) + FYI/Awareness (no priority).
# actions: (priority, project, ask, requested_by, time/by)  — priority in {Urgent, This week, When available}
actions=[("This week","Project Alpha","Decide the roof type — option A vs option B (with the PM).","Sample Employee","~30 min · by Mon 6/15"),
 ("When available","Internal Tooling","15-min review of the rollout, plus a short discussion on direction and how time is allocated to it.","Sample Employee","~45 min · before rollout (wk 6/15)"),
 ("When available","Project Beta","Confirm who owns Project Beta going forward.","Sample Employee","a few min")]
# fyis: (project, note, from)  — awareness only, no priority, no time/by
fyis=[("Internal Ops","Interested in becoming secondary IT support for on-site troubleshooting when the lead is unavailable.","Sample Employee")]
cal=[("Mon 6/15","Project Alpha","Roof-type decision with the PM.","~30 min"),
 ("Wk 6/15","Internal Tooling","Review the rollout + direction discussion.","~45 min")]
dash=[("Project Alpha","DD","Heavy","On Track","Permit set — wk 7/13"),
 ("Internal Tooling","Internal","Light","N/A","Team rollout — wk 6/15"),
 ("Project Beta","PD","Hold · until county OK","On Track","Submit to county 6/15  ⚑"),
 ("Project Gamma","PD","Hold · until HOA docs","On Track","SD on-site meeting 6/25"),
 ("Internal Ops","Internal","Maintenance","N/A","Ongoing — no discrete milestone")]
watch=[("Project Gamma","HOA ARC / CC&R documents not yet received — needed before the 6/25 Schematic Design meeting; fallback is asking the owner directly."),
 ("Internal Tooling","Competing project priorities could deprioritize the rollout, though it stands to save significant time."),
 ("⚑ To confirm","Project Beta — verify a prior submittal didn't already go to county; confirm who owns Project Beta now.")]
wins=[("Operations / Tooling","Rolled out the first team workflow project — usable by the team immediately.")]
team=[("Sample Employee","Next week (~43–45 hrs): ~20 Project Alpha, 8–10 Internal Tooling, Project Delta SD 4, Project Epsilon 4, Gamma 1, Project Zeta 6.")]
# Section 8 is per PERSON (reported total, utilization, next-week allocated, over/under 40).
# (person, role, reported_total, next_week_pace[list of (project,pace)])
people_hours=[("Sample Employee","Associate",42,
  [("Project Alpha",6),("Internal Tooling",3),("Internal Ops",2),("Project Beta",1),("Project Gamma",1)])]

H=lambda *cols:"<tr>"+"".join(f"<th>{c}</th>" for c in cols)+"</tr>"
PRIO_ORDER={"Urgent":0,"This week":1,"When available":2}
actions_sorted=sorted(actions,key=lambda row:PRIO_ORDER.get(row[0],9))
ra="".join(f"<tr><td class='ctr'>{chip(p)}</td><td class='b'>{e(pr)}</td><td>{e(a)}</td><td>{e(r)}</td><td class='nw'>{e(t)}</td></tr>" for (p,pr,a,r,t) in actions_sorted)
if not ra: ra="<tr><td colspan='5' class='muted'>No actions this week.</td></tr>"
rf="".join(f"<tr><td class='b'>{e(pr)}</td><td>{e(n)}</td><td class='nw'>{e(fr)}</td></tr>" for (pr,n,fr) in fyis)
if not rf: rf="<tr><td colspan='3' class='muted'>No FYIs this week.</td></tr>"
rc="".join(f"<tr><td class='b nw'>{e(w)}</td><td>{e(pr)}</td><td>{e(a)}</td><td class='nw'>{e(t)}</td></tr>" for (w,pr,a,t) in cal)
rd="".join(f"<tr><td class='b'>{e(pr)}</td><td>{phase_badge(ph)}</td><td>{e(pc)}</td><td class='ctr'>{bpill(bu)}</td><td>{e(nm)}</td></tr>" for (pr,ph,pc,bu,nm) in dash)
rw="".join(f"<tr><td class='b nw'>{e(a)}</td><td>{e(w)}</td></tr>" for (a,w) in watch)
rwi="".join(f"<tr><td class='b nw'>{e(a)}</td><td>{e(w)}</td></tr>" for (a,w) in wins)
rt="".join(f"<tr><td class='b nw'>{e(a)}</td><td>{e(w)}</td></tr>" for (a,w) in team)
rh=""; team_rep=0.0; team_alloc=0.0
for (nm,role,rep,npace) in people_hours:
    A=EH.allocate(npace, role, nm); alloc=A["total"]
    team_rep+=rep; team_alloc+=alloc
    util=EH.utilization(rep)
    over=round(alloc-EH.BASE,1)
    ou = f"⚑ +{over:g} over" if over>0 else (f"{-over:g} slack" if over<0 else "fully allocated")
    util_cell = f"{util}%" + (" ⚑" if EH.reported_overflow(rep) else "")
    rh+=(f"<tr><td class='b'>{e(nm)}</td><td class='nw'>{rep:g}</td><td class='nw'>{e(util_cell)}</td>"
         f"<td class='nw'>{alloc:g}</td><td>{e(ou)}</td></tr>")

CSS="""
@page{size:Letter;margin:2.65cm 1.45cm 1.95cm 1.45cm;}
#hdr{position:fixed;top:-2.2cm;left:0;right:0;}#ftr{position:fixed;bottom:-1.55cm;left:0;right:0;}
#hdr img,#ftr img{width:100%;display:block;}
*{box-sizing:border-box;}
body{font-family:'Mabry Pro','Helvetica Neue',Arial,sans-serif;color:#1a1a1a;font-size:9pt;line-height:1.36;margin:0;}
h1{font-size:15pt;margin:0 0 2px 0;}
.sub{font-size:8.2pt;color:#6f6f6f;font-style:italic;margin:0 0 6px 0;}
.flag{background:#fbf4e6;border:.6px solid #ecd9a8;border-radius:4px;padding:4px 9px;font-size:8.2pt;margin:0 0 12px 0;}
h2{font-size:10.2pt;text-transform:uppercase;letter-spacing:.5px;margin:15px 0 5px 0;padding-bottom:3px;border-bottom:1.4px solid #1a1a1a;font-weight:800;color:#111;}
h3.sub2{font-size:8.7pt;text-transform:uppercase;letter-spacing:.4px;margin:9px 0 3px 0;font-weight:800;color:#444;}
table{width:100%;border-collapse:collapse;margin-bottom:4px;break-inside:avoid;}
th{background:#efefef;text-align:left;font-size:7.8pt;text-transform:uppercase;letter-spacing:.3px;padding:5px 7px;border:.6px solid #cfcfcf;color:#111;}
td{padding:5px 7px;border:.6px solid #d9d9d9;vertical-align:top;color:#474747;}
td.b{font-weight:700;color:#1a1a1a;} .ctr{text-align:center;} .nw{white-space:nowrap;} .muted{color:#9a9a9a;}
.chip{display:inline-block;padding:2px 8px;border-radius:9px;font-weight:700;font-size:7.4pt;}
.chip.yellow{background:#fbe9c9;}.chip.gray{background:#efefef;}.chip.red{background:#f5d5ce;}.chip.green{background:#dce9d5;}
.pill{display:inline-block;padding:2px 9px;border-radius:9px;font-size:7.6pt;font-weight:600;}
.pill.green{background:#dce9d5;}.pill.yellow{background:#fbe9c9;}.pill.red{background:#f5d5ce;}.pill.gray{background:#efefef;}
.phasebar{display:inline-flex;gap:2px;}.seg{font-size:6.6pt;font-weight:700;padding:2px 4px;border-radius:3px;min-width:16px;text-align:center;}
.seg.done{background:#1a1a1a;color:#fff;}.seg.cur{background:#c9d646;color:#1a1a1a;}.seg.todo{background:#ededed;color:#bdbdbd;}
.intbadge{font-size:6.8pt;font-weight:700;background:#e7ecd6;color:#5b6b22;border-radius:3px;padding:2px 6px;}
.tl{width:100%;margin:5px 0;} .beyond{font-size:7.8pt;font-style:italic;color:#6f6f6f;}
"""
DOC=f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div id="hdr"><img src="{HEADER}"></div><div id="ftr"><img src="{FOOTER}"></div>
<h1>EOW ROLLUP — EXECUTIVE OVERVIEW</h1>
<p class="sub">Week ending {WEEK_END.strftime('%m/%d/%Y')} &nbsp;·&nbsp; Prepared for MKW &nbsp;·&nbsp; Source: EOW Roadmap Report from Sample Employee</p>
<div class="flag">⚑ This rollup reflects <b>one sample report only</b> — the rest of the team's EOW reports are not yet submitted. Sections will fill in as they come in.</div>
<h2>1. MKW Actions</h2>
<h3 class="sub2">Action Required</h3>
<table>{H('Priority','Project','Ask','Requested by','Time / By')}{ra}</table>
<h3 class="sub2">FYI / Awareness</h3>
<table>{H('Project','Note','From')}{rf}</table>
<p class="beyond">Time / By (Action Required only) is the time Maggie spends acting — not the requester's staffing hours (those are in Section 8). FYIs need no action.</p>
<h2>2. MKW Calendar &mdash; derived from the sample report</h2>
<table>{H('When','Project','What Maggie does','Time')}{rc}</table>
<h2>3. Project Status Dashboard</h2>
<table>{H('Project','Phase','Pace','Budget','Next Milestone')}{rd}</table>
<h2>4. Milestone Timeline</h2>
<img class="tl" src="{TL}">
<h2>5. Watch Items &amp; Flags</h2>
<table>{H('Area','Item')}{rw}</table>
<h2>6. Wins This Week</h2>
<table>{rwi}</table>
<h2>7. Team Snapshot</h2>
<table>{H('Person','Focus next week')}{rt}</table>
<h2>8. Hours Reconciliation</h2>
<table>{H('Person','Reported (this wk)','Utilization','Allocated (next wk)','Over / Under 40')}{rh}
<tr><td class='b'>Team total</td><td class='nw'><b>{team_rep:g}</b></td><td></td><td class='nw'><b>{team_alloc:g}</b></td><td></td></tr></table>
<p class="beyond">Reported = actual hours this week. Utilization = reported / 40 (⚑ = over actual time, flagged to MKW). Allocated = next-week auto-allocation from pace; numbers kept, never scaled.</p>
</body></html>"""
_suffix = "_SAMPLE_DO_NOT_SEND" if SAMPLE_DATA else ""
if SAMPLE_DATA:
    print("WARNING: SAMPLE_DATA is True — this renders the FORMAT SAMPLE, not a real rollup. "
          "Replace the data blocks with the uploaded reports and set SAMPLE_DATA=False.")
open(f"mkw_rollup{_suffix}.html","w",encoding="utf-8").write(DOC)
# Real runs land the rollup in the SAME week folder as the reports it consolidated;
# sample runs stay in the working dir so they never touch a real week folder.
_out_dir = "." if SAMPLE_DATA else eow_paths.ensure_week_folder(BASE_DIR, eow_paths.week_monday(WEEK_END))
_out_pdf = os.path.join(_out_dir, f"EOW_MKW_Rollup_{WEEK_END.strftime('%m.%d.%Y')}{_suffix}.pdf")
HTML(string=DOC,base_url=".").write_pdf(_out_pdf)
print("rollup rendered ->", _out_pdf)
