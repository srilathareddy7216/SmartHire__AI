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
  --match:#2F5BFF; --match-soft:#E7ECFF;         /* vivid mid-dark blue (primary) */
  --amber:#FF7A1A; --amber-soft:#FFEEDD;         /* bright reddish-yellow accent */
  --signal:#FF4FA3; --signal-soft:#FDE7F1;       /* vivid pink accent */
  --danger:#F0555F; --danger-soft:#FDE8E9;       /* soft red */
  --light-blue:#5FCBFF;                          /* extra bright accent for glows */
  --muted:#6B7290;
  --tier-hi:#1FA971; --tier-hi-soft:#E4F7EE;
  --tier-mid:#2F5BFF; --tier-mid-soft:#E7ECFF;
  --tier-lo:#FF7A1A; --tier-lo-soft:#FFEEDD;
}

html, body, [class*="css"]  { font-family:'Inter', sans-serif; }
.stApp { background: var(--paper); }
h1,h2,h3,h4 { font-family:'Space Grotesk', sans-serif !important; color: var(--ink); letter-spacing:-0.01em; }
p, li, span, label, div { color: var(--ink); }

#MainMenu, footer, header {visibility:hidden;}
.block-container{ padding-top:1.4rem; padding-bottom:3.5rem; max-width:1280px;}

/* ---------- Top page title (centered, main content) ---------- */
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
.sh-topbar-sub{
  font-family:'Inter',sans-serif; color:var(--muted); font-size:0.98rem; margin-top:0.3rem;
}
.sh-topbar-rule{
  width:64px; height:4px; margin:0.9rem 0 0 0; border-radius:999px;
  background: linear-gradient(90deg, var(--match), var(--signal));
}

/* highlight page headings with a blue accent underline */
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

/* ---------- Job match card (legacy, still used elsewhere if needed) ---------- */
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

/* ---------- NEW: Job recommendation card — "orbit badge" style ---------- */
.jr-card{
  position:relative;
  background:var(--card); border:1px solid var(--line);
  border-radius:18px; padding:1.4rem 1.35rem 1.15rem 1.35rem; margin-bottom:1.3rem;
  box-shadow: 0 1px 3px rgba(18,23,43,0.04);
  transition: box-shadow .18s ease, transform .18s ease, border-color .18s ease;
  overflow:visible; height:100%;
}
.jr-card::before{
  content:""; position:absolute; top:0; left:0; right:0; height:4px;
  border-radius:18px 18px 0 0;
  background: linear-gradient(90deg, var(--tier-color1), var(--tier-color2));
}
.jr-card:hover{
  box-shadow:0 14px 30px rgba(18,23,43,0.10); transform:translateY(-3px);
  border-color:#D5DAEA;
}

.jr-orbit{
  position:absolute; top:-14px; right:16px;
  width:54px; height:54px; border-radius:50%;
  display:flex; align-items:center; justify-content:center; flex-direction:column;
  background: var(--tier-soft);
  border: 3px solid var(--card);
  box-shadow: 0 4px 12px rgba(18,23,43,0.12);
}
.jr-orbit .pct{
  font-family:'JetBrains Mono',monospace; font-weight:700; font-size:0.88rem; color:var(--tier-color1);
  line-height:1;
}
.jr-orbit .sign{
  font-size:0.55rem; color:var(--tier-color1); font-weight:700; margin-top:1px;
}

.jr-avatar-row{ display:flex; align-items:flex-start; gap:0.7rem; margin:0.2rem 2.6rem 0.7rem 0; }
.jr-avatar{
  width:38px; height:38px; border-radius:11px; flex:0 0 auto;
  display:flex; align-items:center; justify-content:center;
  font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.0rem; color:#fff;
  background: linear-gradient(135deg, var(--tier-color1), var(--tier-color2));
}
.jr-title-block{ min-width:0; }
.jr-title{
  font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.0rem;
  color:var(--ink); line-height:1.28; margin:0 0 0.15rem 0;
}
.jr-company{
  font-size:0.83rem; color:var(--muted); font-weight:500; margin:0;
}

.jr-loc{
  display:flex; align-items:center; gap:0.35rem; margin:0.55rem 0 0.9rem 0;
  font-size:0.82rem; color:var(--muted);
}
.jr-loc-icon{ opacity:0.8; }

.jr-footer{
  display:flex; align-items:center; justify-content:space-between; gap:0.5rem;
  margin-bottom:0.6rem;
}
.jr-id-tag{
  font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:var(--muted);
  background:#F3F5FB; border:1px dashed var(--line); padding:0.2rem 0.55rem; border-radius:7px;
}
.jr-tier-label{
  font-family:'Space Grotesk',sans-serif; font-size:0.72rem; font-weight:700;
  color:var(--tier-color1); text-transform:uppercase; letter-spacing:0.03em;
}

.jr-track{
  width:100%; height:6px; border-radius:999px; background:#EEF0F7; overflow:hidden; position:relative;
}
.jr-fill{
  height:100%; border-radius:999px;
  background: linear-gradient(90deg, var(--tier-color1), var(--tier-color2));
  position:relative;
}
.jr-fill::after{
  content:""; position:absolute; right:-2px; top:50%; transform:translateY(-50%);
  width:9px; height:9px; border-radius:50%; background:var(--tier-color1);
  box-shadow: 0 0 0 3px var(--tier-soft);
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

/* ---------- Sidebar (LIGHT) ---------- */
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

/* progress bar */
.stProgress > div > div > div > div{ background: var(--match); }

hr{ border-color: var(--line); }
</style>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)


def main_header() -> str:
    return """
    <div class="sh-topbar">
      <div class="sh-topbar-badge">💼</div>
      <div class="sh-topbar-text">
        <div class="sh-topbar-title">SmartHire</div>
        <div class="sh-topbar-sub">Resume-to-Job Matching &amp; Career Guidance Engine</div>
        <div class="sh-topbar-rule"></div>
      </div>
    </div>
    """


def sidebar_brand() -> str:
    return """
    <div class="sh-brand">
      <div class="sh-brand-badge">💼</div>
      <div>
        <div class="sh-brand-name">SmartHire</div>
        <div class="sh-brand-tag">Resume → Job Matching Engine</div>
      </div>
    </div>
    """


def match_ring_svg(pct: float, color: str = "#1FA971", size: int = 76) -> str:
    """Return an inline SVG circular progress ring showing pct (0-100)."""
    pct = max(0, min(100, pct))
    r = (size - 10) / 2
    c = size / 2
    circumference = 2 * 3.14159265 * r
    offset = circumference * (1 - pct / 100)
    return f"""
    <div class="ring-wrap">
      <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
        <circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="#EDEFF6" stroke-width="7"/>
        <circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="{color}" stroke-width="7"
                stroke-linecap="round" stroke-dasharray="{circumference:.2f}"
                stroke-dashoffset="{offset:.2f}" transform="rotate(-90 {c} {c})"/>
      </svg>
      <div class="ring-label">{pct:.0f}%</div>
    </div>
    """


def stat_card(number: str, label: str) -> str:
    return f'<div class="sh-stat"><div class="n">{number}</div><div class="l">{label}</div></div>'


def _tier_for(pct: float):
    """Return (color1, color2, soft-bg, label) for a match percentage tier."""
    if pct >= 80:
        return "#1FA971", "#5FCBFF", "#E4F7EE", "Strong fit"
    elif pct >= 60:
        return "#2F5BFF", "#8A6CFF", "#E7ECFF", "Good fit"
    else:
        return "#FF7A1A", "#FF4FA3", "#FFEEDD", "Worth a look"


def job_recommendation_card(title: str, company: str, location: str, job_id, match_pct: float) -> str:
    """'Orbit badge' style job recommendation card — a floating circular match
    score badge, a gradient company-initial avatar, and a gradient progress
    rail with a leading dot, color-coded by match tier."""
    pct = max(0, min(100, match_pct))
    company = company or "—"
    location = location or "—"
    initial = (company[:1] or "?").upper()
    color1, color2, soft, tier_label = _tier_for(pct)

    style_vars = (
        f'--tier-color1:{color1}; --tier-color2:{color2}; --tier-soft:{soft};'
    )

    return f"""
    <div class="jr-card" style="{style_vars}">
      <div class="jr-orbit">
        <div class="pct">{pct:.0f}%</div>
        <div class="sign">MATCH</div>
      </div>
      <div class="jr-avatar-row">
        <div class="jr-avatar">{initial}</div>
        <div class="jr-title-block">
          <p class="jr-title">{title}</p>
          <p class="jr-company">{company}</p>
        </div>
      </div>
      <div class="jr-loc">
        <span class="jr-loc-icon">📍</span>
        <span>{location}</span>
      </div>
      <div class="jr-footer">
        <span class="jr-id-tag">#{job_id}</span>
        <span class="jr-tier-label">{tier_label}</span>
      </div>
      <div class="jr-track">
        <div class="jr-fill" style="width:{pct:.0f}%;"></div>
      </div>
    </div>
    """