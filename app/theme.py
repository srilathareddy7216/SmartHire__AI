"""
SmartHire visual identity — light, high-contrast, spacious.
"""
import streamlit as st

CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">

<style>
:root{
  --ink:#1E2A54; --paper:#F5F8FF; --card:#FFFFFF; --line:#E1E7F7;
  --match:#2F5BFF; --match-soft:#E7ECFF;
  --amber:#FF7A1A; --amber-soft:#FFEEDD;
  --signal:#FF4FA3; --signal-soft:#FDE7F1;
  --danger:#F0555F; --danger-soft:#FDE8E9;
  --light-blue:#5FCBFF;
  --muted:#6B7290;
}

html, body, [class*="css"]  { font-family:'Inter', sans-serif; }
.stApp { background: var(--paper); }
h1,h2,h3,h4 { font-family:'Space Grotesk', sans-serif !important; color: var(--ink); letter-spacing:-0.01em; }
p, li, span, label, div { color: var(--ink); }

#MainMenu, footer, header {visibility:hidden;}
.block-container{ padding-top:1.4rem; padding-bottom:3.5rem; max-width:1280px;}

/* ---------- Top page title ---------- */
.sh-topbar{
  display:flex; align-items:center; justify-content:center; gap:1.3rem;
  padding:0.4rem 0 2rem 0;
}
.sh-topbar-badge{
  width:74px; height:74px; border-radius:20px; flex:0 0 auto;
  background: linear-gradient(135deg, var(--match) 0%, var(--signal) 100%);
  display:flex; align-items:center; justify-content:center; font-size:2.2rem;
  box-shadow: 0 12px 30px rgba(47,91,255,0.4), 0 0 0 6px rgba(47,91,255,0.08);
}
.sh-topbar-text{ text-align:left; }
.sh-topbar-title{
  font-family:'Space Grotesk',sans-serif; font-weight:800; font-size:3.1rem;
  letter-spacing:-0.03em; margin:0; line-height:1.05;
  background: linear-gradient(90deg, var(--match) 0%, var(--signal) 100%);
  -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
  filter: drop-shadow(0 6px 18px rgba(47,91,255,0.22));
}
.sh-topbar-sub{ font-family:'Inter',sans-serif; color:var(--muted); font-size:0.98rem; margin-top:0.3rem; }
.sh-topbar-rule{
  width:64px; height:4px; margin:0.9rem 0 0 0; border-radius:999px;
  background: linear-gradient(90deg, var(--match), var(--signal));
}

h2{ display:inline-block; padding-bottom:0.35rem; border-bottom:3px solid var(--match); }

/* ---------- Hero ---------- */
.sh-hero{
  background: linear-gradient(135deg, #EAF2FF 0%, #FDEAF2 100%);
  border:1px solid var(--line);
  border-radius:22px; padding:2.8rem 3rem; color:var(--ink); margin-bottom:1.8rem;
  position:relative; overflow:hidden;
}
.sh-hero::after{
  content:""; position:absolute; right:-60px; top:-60px; width:280px; height:280px;
  border-radius:50%; background:radial-gradient(circle, rgba(95,203,255,0.45), transparent 70%);
}
.sh-hero::before{
  content:""; position:absolute; left:-40px; bottom:-70px; width:220px; height:220px;
  border-radius:50%; background:radial-gradient(circle, rgba(255,79,163,0.25), transparent 70%);
}
.sh-hero .eyebrow{
  display:inline-block; font-family:'JetBrains Mono',monospace; font-size:0.72rem;
  letter-spacing:0.12em; text-transform:uppercase; background:#fff;
  border:1px solid var(--line);
  padding:0.32rem 0.75rem; border-radius:999px; margin-bottom:1.1rem; color:#2743B8;
}
.sh-hero h1{ color:var(--ink) !important; font-size:2.6rem; margin:0 0 0.7rem 0; line-height:1.12;}
.sh-hero p.sub{ color:#4A4F68; font-size:1.05rem; max-width:660px; margin:0; }

/* ---------- Cards ---------- */
.sh-card{
  background:var(--card); border:1px solid var(--line); border-radius:16px;
  padding:1.4rem 1.6rem; margin-bottom:1.1rem;
  box-shadow: 0 1px 3px rgba(18,23,43,0.03);
}
.sh-card.flush{ padding:0; overflow:hidden; }
.sh-stat{
  background:var(--card); border:1px solid var(--line); border-radius:16px;
  padding:1.2rem 1.4rem;
  box-shadow: 0 1px 3px rgba(18,23,43,0.03);
}
.sh-stat .n{ font-family:'JetBrains Mono',monospace; font-weight:700; font-size:1.8rem; color:var(--ink);}
.sh-stat .l{ font-size:0.83rem; color:var(--muted); margin-top:0.2rem;}

/* ---------- Legacy job card ---------- */
.job-card{
  background:var(--card); border:1px solid var(--line); border-radius:16px;
  padding:1.3rem 1.5rem; margin-bottom:0.9rem; display:flex; gap:1.2rem; align-items:flex-start;
  transition: box-shadow .15s ease, transform .15s ease;
}
.job-card:hover{ box-shadow:0 8px 22px rgba(18,23,43,0.07); transform:translateY(-1px); border-color:#D5DAEA; }
.job-card .jc-title{ font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:1.1rem; margin:0;}
.job-card .jc-meta{ color:var(--muted); font-size:0.86rem; margin:0.18rem 0 0.65rem 0;}
.chip{
  display:inline-block; font-size:0.75rem; padding:0.24rem 0.65rem; border-radius:999px;
  margin:0 0.3rem 0.3rem 0; font-family:'Inter',sans-serif; font-weight:500;
}
.chip.have{ background:var(--match-soft); color:#2743B8; }
.chip.missing{ background:var(--danger-soft); color:#B23B3B; }
.chip.tag{ background:#EEF0F7; color:var(--muted); }
.chip.cluster{ background:var(--signal-soft); color:#B23B70; }

/* ---------- Job recommendation card ---------- */
.jr-card{
  position:relative;
  background:#fff; border:1px solid var(--line);
  border-radius:20px; padding:1.6rem 1.5rem 1.4rem 1.5rem; margin:0.6rem 0 1.4rem 0;
  box-shadow: 0 2px 8px rgba(18,23,43,0.05);
  transition: box-shadow .18s ease, transform .18s ease;
  min-height:230px;
}
.jr-card:hover{ box-shadow:0 16px 34px rgba(18,23,43,0.12); transform:translateY(-4px); }
.jr-strip{ position:absolute; top:0; left:0; right:0; height:6px; border-radius:20px 20px 0 0; }
.jr-head{ display:flex; align-items:flex-start; justify-content:space-between; gap:0.7rem; margin-top:0.35rem; }
.jr-avatar{
  width:46px; height:46px; border-radius:13px; flex:0 0 auto;
  display:flex; align-items:center; justify-content:center; font-size:1.35rem;
  box-shadow: 0 6px 16px rgba(18,23,43,0.14);
}
.jr-badge{
  flex:0 0 auto; min-width:64px; height:64px; border-radius:50%;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  box-shadow: 0 6px 16px rgba(18,23,43,0.16); border:3px solid #fff;
}
.jr-badge .pct{ font-family:'JetBrains Mono',monospace; font-weight:800; font-size:1.0rem; color:#fff; line-height:1; }
.jr-badge .sign{ font-size:0.52rem; color:#fff; font-weight:700; letter-spacing:0.03em; margin-top:1px; }
.jr-title{
  font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.08rem;
  color:var(--ink); line-height:1.3; margin:0.75rem 0 0.2rem 0;
}
.jr-company{ font-size:0.86rem; color:var(--muted); font-weight:600; margin:0 0 0.55rem 0; }
.jr-loc{ display:flex; align-items:center; gap:0.4rem; font-size:0.83rem; color:var(--muted); margin-bottom:1rem; }
.jr-divider{ height:1px; background:var(--line); margin:0.4rem 0 0.9rem 0; }
.jr-footer{ display:flex; align-items:center; justify-content:space-between; gap:0.5rem; margin-bottom:0.7rem; }
.jr-id-tag{
  font-family:'JetBrains Mono',monospace; font-size:0.74rem; color:var(--muted);
  background:#F3F5FB; border:1px solid var(--line); padding:0.25rem 0.6rem; border-radius:8px;
}
.jr-tier{
  font-family:'Space Grotesk',sans-serif; font-size:0.76rem; font-weight:700;
  padding:0.25rem 0.65rem; border-radius:999px; display:flex; align-items:center; gap:0.3rem;
}
.jr-track{ width:100%; height:8px; border-radius:999px; background:#EEF0F7; overflow:hidden; }
.jr-fill{ height:100%; border-radius:999px; }

/* ---------- Fit-score panel ---------- */
.fit-panel{
  display:flex; gap:2rem; align-items:center; flex-wrap:wrap;
  background:#fff; border:1px solid var(--line); border-radius:20px;
  padding:1.8rem; margin-bottom:1rem;
  box-shadow: 0 2px 10px rgba(18,23,43,0.05);
}
.fit-gauge-wrap{ position:relative; width:180px; height:180px; flex:0 0 auto; }
.fit-gauge-center{
  position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center;
}
.fit-gauge-pct{ font-family:'JetBrains Mono',monospace; font-weight:800; font-size:2.1rem; line-height:1; }
.fit-gauge-label{ font-size:0.72rem; color:var(--muted); font-weight:600; margin-top:0.3rem; text-transform:uppercase; letter-spacing:0.05em; }
.fit-info{ flex:1; min-width:260px; }
.fit-job-title{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.25rem; margin:0 0 0.2rem 0; }
.fit-job-company{ color:var(--muted); font-size:0.92rem; margin-bottom:1.1rem; }
.fit-feature-row{ display:flex; align-items:center; gap:0.7rem; margin-bottom:0.8rem; }
.fit-feature-icon{
  width:34px; height:34px; border-radius:10px; flex:0 0 auto;
  display:flex; align-items:center; justify-content:center; font-size:1.05rem;
}
.fit-feature-body{ flex:1; min-width:0; }
.fit-feature-top{ display:flex; justify-content:space-between; font-size:0.83rem; margin-bottom:0.25rem; }
.fit-feature-label{ font-weight:600; color:var(--ink); }
.fit-feature-val{ font-family:'JetBrains Mono',monospace; font-weight:700; }
.fit-feature-track{ width:100%; height:7px; border-radius:999px; background:#EEF0F7; overflow:hidden; }
.fit-feature-fill{ height:100%; border-radius:999px; }
.fit-note{
  margin-top:0.4rem; font-size:0.8rem; color:var(--muted); background:#F7F8FC;
  border-left:3px solid var(--match); padding:0.6rem 0.9rem; border-radius:8px;
}

/* ---------- Match ring ---------- */
.ring-wrap{ position:relative; width:76px; height:76px; flex:0 0 auto; }
.ring-label{
  position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
  font-family:'JetBrains Mono',monospace; font-weight:700; font-size:0.95rem; color:var(--ink);
}

/* ---------- Badges ---------- */
.badge{
  display:inline-block; padding:0.4rem 0.9rem; border-radius:999px; font-weight:600;
  font-size:0.85rem; font-family:'Space Grotesk',sans-serif;
}
.badge.match{ background:var(--match-soft); color:#2743B8; }
.badge.signal{ background:var(--signal-soft); color:#B23B70; }
.badge.amber{ background:var(--amber-soft); color:#9A5300; }

/* ---------- Section title ---------- */
.sh-eyebrow{
  font-family:'JetBrains Mono',monospace; font-size:0.72rem; letter-spacing:0.1em;
  text-transform:uppercase; color:var(--match); margin-bottom:0.3rem; display:block;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, #FFFFFF 0%, #EEF3FF 100%);
  border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] * { color: var(--ink) !important; }
section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] .stCaption { color: var(--muted) !important; }
section[data-testid="stSidebar"] .stRadio label{ font-family:'Space Grotesk',sans-serif; font-weight:500; padding:0.25rem 0; }
section[data-testid="stSidebar"] hr{ border-color: var(--line); }

.sh-brand{ display:flex; align-items:center; gap:0.7rem; padding:0.4rem 0 1.4rem 0; }
.sh-brand-badge{
  width:44px; height:44px; border-radius:13px; flex:0 0 auto;
  background: linear-gradient(135deg, var(--match), var(--signal));
  display:flex; align-items:center; justify-content:center; font-size:1.35rem;
  box-shadow: 0 4px 14px rgba(31,169,113,0.28);
}
.sh-brand-name{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.2rem; color:var(--ink); line-height:1.1;}
.sh-brand-tag{ font-size:0.72rem; color:var(--muted); margin-top:0.15rem;}

/* ---------- Buttons ---------- */
.stButton>button, .stDownloadButton>button{
  background:var(--match); color:#fff; border-radius:10px; border:none;
  font-family:'Space Grotesk',sans-serif; font-weight:600; padding:0.6rem 1.4rem;
}
.stButton>button:hover, .stDownloadButton>button:hover{ background:#178A5D; color:#fff; }

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"]{ gap: 6px; }
.stTabs [data-baseweb="tab"]{
  font-family:'Space Grotesk',sans-serif; font-weight:600; border-radius:10px 10px 0 0;
}

.stProgress > div > div > div > div{ background: var(--match); }
hr{ border-color: var(--line); }
</style>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)


def main_header() -> str:
    return (
        '<div class="sh-topbar">'
        '<div class="sh-topbar-badge">🎓</div>'
        '<div class="sh-topbar-text">'
        '<div class="sh-topbar-title">SmartHire</div>'
        '<div class="sh-topbar-sub">Resume-to-Job Matching &amp; Career Guidance Engine</div>'
        '<div class="sh-topbar-rule"></div>'
        '</div>'
        '</div>'
    )


def sidebar_brand() -> str:
    return (
        '<div class="sh-brand">'
        '<div class="sh-brand-badge">🎓</div>'
        '<div>'
        '<div class="sh-brand-name">SmartHire</div>'
        '<div class="sh-brand-tag">Resume → Job Matching Engine</div>'
        '</div>'
        '</div>'
    )


def match_ring_svg(pct: float, color: str = "#1FA971", size: int = 76) -> str:
    pct = max(0, min(100, pct))
    r = (size - 10) / 2
    c = size / 2
    circumference = 2 * 3.14159265 * r
    offset = circumference * (1 - pct / 100)
    svg = (
        f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
        + f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="#EDEFF6" stroke-width="7"/>'
        + f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="{color}" stroke-width="7" '
        + 'stroke-linecap="round" '
        + f'stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{offset:.2f}" '
        + f'transform="rotate(-90 {c} {c})"/>'
        + '</svg>'
    )
    return (
        '<div class="ring-wrap">'
        + svg
        + f'<div class="ring-label">{pct:.0f}%</div>'
        + '</div>'
    )


def stat_card(number: str, label: str) -> str:
    return f'<div class="sh-stat"><div class="n">{number}</div><div class="l">{label}</div></div>'


# ---------------------------------------------------------------------------
# Tier system — shared by job cards + fit panel. Colors are hardcoded hex
# (not CSS vars) so they always render regardless of pseudo-element quirks.
# ---------------------------------------------------------------------------
def _tier_for(pct: float):
    """Returns (color1, color2, soft-bg, text-color, icon, label)"""
    if pct >= 75:
        return "#1FA971", "#12C48B", "#E4F7EE", "#0F7A50", "🌟", "Excellent fit"
    elif pct >= 50:
        return "#2F5BFF", "#5B7FFF", "#E7ECFF", "#2743B8", "👍", "Good fit"
    elif pct >= 25:
        return "#FF7A1A", "#FFA24D", "#FFEEDD", "#9A5300", "🔎", "Worth a look"
    else:
        return "#F0555F", "#FF7D85", "#FDE8E9", "#B23B3B", "🧩", "Low overlap"


COMPANY_ICON_PALETTE = ["#2F5BFF", "#FF4FA3", "#1FA971", "#FF7A1A", "#6C5CE7", "#00B8D9"]


def _company_color(company: str) -> str:
    idx = sum(ord(c) for c in (company or "?")) % len(COMPANY_ICON_PALETTE)
    return COMPANY_ICON_PALETTE[idx]


def job_recommendation_card(title: str, company: str, location: str, job_id, match_pct: float) -> str:
    """Colorful job recommendation card — gradient top strip, tier-colored
    circular match badge, gradient company avatar icon, and a matching
    progress rail. All colors are inline hex so they always render."""
    pct = max(0, min(100, match_pct))
    company = company or "—"
    location = location or "—"
    c1, c2, soft, text_color, icon, tier_label = _tier_for(pct)
    avatar_color = _company_color(company)

    return (
        '<div class="jr-card">'
        + f'<div class="jr-strip" style="background:linear-gradient(90deg, {c1}, {c2});"></div>'
        + '<div class="jr-head">'
        + f'<div class="jr-avatar" style="background:linear-gradient(135deg, {avatar_color}, {c2});">💼</div>'
        + f'<div class="jr-badge" style="background:linear-gradient(135deg, {c1}, {c2});">'
        + f'<div class="pct">{pct:.0f}%</div>'
        + '<div class="sign">MATCH</div>'
        + '</div>'
        + '</div>'
        + f'<p class="jr-title">{title}</p>'
        + f'<p class="jr-company">🏢 {company}</p>'
        + f'<div class="jr-loc">📍 {location}</div>'
        + '<div class="jr-divider"></div>'
        + '<div class="jr-footer">'
        + f'<span class="jr-id-tag">🆔 #{job_id}</span>'
        + f'<span class="jr-tier" style="background:{soft}; color:{text_color};">{icon} {tier_label}</span>'
        + '</div>'
        + '<div class="jr-track">'
        + f'<div class="jr-fill" style="width:{pct:.0f}%; background:linear-gradient(90deg, {c1}, {c2});"></div>'
        + '</div>'
        + '</div>'
    )


def fit_gauge_svg(pct: float, size: int = 180) -> str:
    """Bigger, tier-colored circular gauge used in the Shortlisting Fit tab."""
    pct = max(0, min(100, pct))
    c1, c2, soft, text_color, icon, tier_label = _tier_for(pct)
    r = (size - 22) / 2
    c = size / 2
    circumference = 2 * 3.14159265 * r
    offset = circumference * (1 - pct / 100)
    gradient_id = "fitgrad"
    svg = (
        f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
        + f'<defs><linearGradient id="{gradient_id}" x1="0%" y1="0%" x2="100%" y2="100%">'
        + f'<stop offset="0%" stop-color="{c1}"/><stop offset="100%" stop-color="{c2}"/>'
        + '</linearGradient></defs>'
        + f'<circle cx="{c}" cy="{c}" r="{r}" fill="{soft}" stroke="#EDEFF6" stroke-width="1"/>'
        + f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="#EDEFF6" stroke-width="14"/>'
        + f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="url(#{gradient_id})" stroke-width="14" '
        + 'stroke-linecap="round" '
        + f'stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{offset:.2f}" '
        + f'transform="rotate(-90 {c} {c})"/>'
        + '</svg>'
    )
    return (
        '<div class="fit-gauge-wrap">'
        + svg
        + '<div class="fit-gauge-center">'
        + f'<div class="fit-gauge-pct" style="color:{c1};">{pct:.0f}%</div>'
        + f'<div class="fit-gauge-label">{icon} {tier_label}</div>'
        + '</div>'
        + '</div>'
    )


def fit_feature_row(icon: str, label: str, pct: float, color: str) -> str:
    pct = max(0, min(100, pct))
    return (
        '<div class="fit-feature-row">'
        + f'<div class="fit-feature-icon" style="background:{color}22; color:{color};">{icon}</div>'
        + '<div class="fit-feature-body">'
        + '<div class="fit-feature-top">'
        + f'<span class="fit-feature-label">{label}</span>'
        + f'<span class="fit-feature-val" style="color:{color};">{pct:.1f}%</span>'
        + '</div>'
        + '<div class="fit-feature-track">'
        + f'<div class="fit-feature-fill" style="width:{pct:.0f}%; background:{color};"></div>'
        + '</div>'
        + '</div>'
        + '</div>'
    )


def fit_panel(job_title: str, company: str, fit_pct: float, features: list[tuple]) -> str:
    """Full attractive fit-score panel: big tier-colored gauge on the left,
    job info + colorful feature bars on the right.
    `features` = list of (icon, label, pct, color) tuples.
    """
    gauge = fit_gauge_svg(fit_pct)
    rows = "".join(fit_feature_row(icon, label, pct, color) for icon, label, pct, color in features)
    return (
        '<div class="fit-panel">'
        + gauge
        + '<div class="fit-info">'
        + f'<p class="fit-job-title">🎯 {job_title}</p>'
        + f'<p class="fit-job-company">🏢 {company}</p>'
        + rows
        + '<div class="fit-note">⚠️ This model is trained with weak supervision — treat the percentage as a directional signal, not a hiring guarantee.</div>'
        + '</div>'
        + '</div>'
    )