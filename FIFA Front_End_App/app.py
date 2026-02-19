import json
from pathlib import Path
import base64
import requests

import pandas as pd
import streamlit as st
import plotly.express as px

DATA_DIR = Path(__file__).parent / "data"
ASSETS_DIR = Path(__file__).parent / "assets"  # optional, for your own logo later
COUNTRIES_PATH = DATA_DIR / "countries_mock.json"
GDP_PATH = DATA_DIR / "gdp_10y_mock.csv"


@st.cache_data
def load_countries():
    with open(COUNTRIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_gdp():
    df = pd.read_csv(GDP_PATH)
    df["year"] = df["year"].astype(int)
    df["gdp_usd"] = df["gdp_usd"].astype(float)
    return df


def fmt_money(x):
    if x is None:
        return "—"
    x = float(x)
    absx = abs(x)
    if absx >= 1e12:
        return f"${x/1e12:.2f}T"
    if absx >= 1e9:
        return f"${x/1e9:.2f}B"
    if absx >= 1e6:
        return f"${x/1e6:.2f}M"
    return f"${x:,.0f}"


def fmt_pct(x):
    if x is None:
        return "—"
    return f"{float(x):.1f}%"


def _img_to_base64(path: Path) -> str:
    data = path.read_bytes()
    return base64.b64encode(data).decode("utf-8")


def _bytes_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def set_page_background(image_path: Path | None):
    """Sets a full-page background image via CSS. If image_path is None or missing, does nothing."""
    if image_path is None or not image_path.exists():
        return

    b64 = _img_to_base64(image_path)
    ext = image_path.suffix.lower().lstrip(".")
    if ext == "jpg":
        ext = "jpeg"

    st.markdown(
        f"""
        <style>
          /* Full app background */
          .stApp {{
            background: url("data:image/{ext};base64,{b64}") no-repeat center center fixed;
            background-size: cover;
          }}

          /* Slight dark overlay for readability */
          .stApp:before {{
            content: "";
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.60);
            pointer-events: none;
            z-index: 0;
          }}

          /* Ensure main content stays above overlay */
          section.main > div {{
            position: relative;
            z-index: 1;
          }}

          /* Make the body/container background transparent */
          .block-container {{
            background: transparent !important;
          }}

          /* Landing hero text styling */
          .landing-title {{
            font-size: 54px;
            line-height: 1.05;
            font-weight: 750;
            letter-spacing: -0.02em;
            margin: 0 0 18px 0;
            color: rgba(255,255,255,0.95);
            text-shadow: 0 10px 30px rgba(0,0,0,0.35);
          }}

          .landing-label {{
            font-size: 14px;
            letter-spacing: 0.02em;
            color: rgba(255,255,255,0.78);
            margin: 0 0 8px 0;
          }}

          /* Tighten Streamlit selectbox */
          div[data-baseweb="select"] > div {{
            border-radius: 14px !important;
          }}

          /* Optional logo placement (top-right) */
          .corner-logo {{
            position: fixed;
            top: 18px;
            right: 18px;
            width: 110px;
            z-index: 2;
            filter: drop-shadow(0 10px 30px rgba(0,0,0,0.35));
          }}

          /* Right-side panel divider + spacing (dashboard) */
          .right-panel {{
            border-left: 2px solid rgba(255,255,255,0.22);
            padding-left: 24px;
            margin-left: 6px;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def fetch_flag_png_iso2(iso2: str) -> bytes | None:
    """Fetches a flag PNG for an ISO2 code from a public CDN. Returns raw bytes or None."""
    if not iso2:
        return None
    code = iso2.strip().lower()
    if len(code) != 2:
        return None

    # flagcdn uses lowercase ISO2, e.g., https://flagcdn.com/w640/us.png
    url = f"https://flagcdn.com/w640/{code}.png"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; StreamlitApp/1.0; +https://streamlit.io)",
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    }

    try:
        r = requests.get(url, timeout=12, headers=headers)
        if r.status_code == 200 and r.content:
            return r.content
        return None
    except Exception:
        return None


def set_page_background_bytes(image_bytes: bytes | None, ext: str = "png"):
    """Sets a full-page background image via CSS from raw bytes."""
    if not image_bytes:
        return

    b64 = _bytes_to_base64(image_bytes)
    ext = (ext or "png").lower().lstrip(".")
    if ext == "jpg":
        ext = "jpeg"

    st.markdown(
        f"""
        <style>
          /* Full app background */
          .stApp {{
            background: url("data:image/{ext};base64,{b64}") no-repeat center center fixed;
            background-size: cover;
          }}

          /* Slight dark overlay for readability */
          .stApp:before {{
            content: "";
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.60);
            pointer-events: none;
            z-index: 0;
          }}

          /* Ensure main content stays above overlay */
          section.main > div {{
            position: relative;
            z-index: 1;
          }}

          /* Make the body/container background transparent */
          .block-container {{
            background: transparent !important;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ----------------- Styling (minimalist + elegant) -----------------
st.set_page_config(page_title="World Cup Host Feasibility", layout="wide")

st.markdown(
    """
<style>
/* Hide Streamlit default chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Page padding */
.block-container {padding-top: 2.5rem; padding-bottom: 2.5rem;}

/* Hero title */
.hero-title {
  font-size: 44px;
  line-height: 1.05;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 10px 0;
}

/* Hero subtitle */
.hero-sub {
  font-size: 16px;
  opacity: 0.80;
  margin: 0 0 22px 0;
}

.centered {
  display: flex;
  justify-content: center;
}

.kpi-card {
  border-radius: 18px;
  padding: 16px 16px;
  border: 1px solid rgba(0,0,0,0.06);
  background: rgba(255,255,255,0.7);
}
</style>
""",
    unsafe_allow_html=True,
)

GLOBE_SVG = """
<svg width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="60" cy="60" r="48" stroke="rgba(0,0,0,0.16)" stroke-width="2"/>
  <ellipse cx="60" cy="60" rx="22" ry="48" stroke="rgba(0,0,0,0.12)" stroke-width="2"/>
  <ellipse cx="60" cy="60" rx="48" ry="18" stroke="rgba(0,0,0,0.10)" stroke-width="2"/>
  <path d="M12 60H108" stroke="rgba(0,0,0,0.12)" stroke-width="2"/>
  <path d="M60 12V108" stroke="rgba(0,0,0,0.06)" stroke-width="2" stroke-dasharray="4 6"/>
</svg>
"""

TOURNAMENT_MARK = """
<svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M8 6h10v4c0 2.2-1.8 4-4 4h-2c-2.2 0-4-1.8-4-4V6Z" stroke="rgba(0,0,0,0.55)" stroke-width="1.6" stroke-linejoin="round"/>
  <path d="M10 18h6" stroke="rgba(0,0,0,0.55)" stroke-width="1.6" stroke-linecap="round"/>
  <path d="M11 14v4" stroke="rgba(0,0,0,0.55)" stroke-width="1.6" stroke-linecap="round"/>
  <path d="M15 14v4" stroke="rgba(0,0,0,0.55)" stroke-width="1.6" stroke-linecap="round"/>
</svg>
"""


# ----------------- App state -----------------
if "selected_country" not in st.session_state:
    st.session_state.selected_country = None

countries = load_countries()
gdp_df = load_gdp()
country_names = [c["name"] for c in countries]

def render_landing():
    # Background should be the globe image (full screen)
    # Prefer assets/globe_background.(png/jpg/jpeg). Fallback to assets/globe.png.
    bg = None
    for name in ["globe_background.jpg", "globe_background.jpeg", "globe_background.png", "globe.png"]:
        p = ASSETS_DIR / name
        if p.exists():
            bg = p
            break

    set_page_background(bg)

    # Top-right FIFA logo (if present)
    logo_path = ASSETS_DIR / "fifa_logo.png"
    if logo_path.exists():
        b64_logo = _img_to_base64(logo_path)
        st.markdown(
            f"""
            <img class="corner-logo" src="data:image/png;base64,{b64_logo}" />
            """,
            unsafe_allow_html=True,
        )

    # Centered landing content (no separate label line)
    st.markdown(
        """
        <div style="min-height:60vh; display:flex; align-items:center; justify-content:center;">
          <div style="width:min(1100px, 92vw); margin: 0 auto; text-align: center;">
            <div class="landing-title">Explore who can host — and what it costs.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Dropdown directly under the title
    st.markdown("<div style='display:flex; justify-content:center; margin-top:-120px;'>", unsafe_allow_html=True)
    chosen = st.selectbox(
        "",
        ["Select your country…"] + country_names,
        index=0,
        label_visibility="collapsed"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if chosen != "Select your country…":
        st.session_state.selected_country = chosen
        st.rerun()


def render_dashboard(selected_name: str):
    st.title("World Cup Host Feasibility Explorer")

    # Top bar
    top_left, top_right = st.columns([1, 1], vertical_alignment="center")
    with top_left:
        st.write(" ")
        new_sel = st.selectbox("Country", country_names, index=country_names.index(selected_name))
        if new_sel != selected_name:
            st.session_state.selected_country = new_sel
            st.rerun()
    with top_right:
        if st.button("Back to landing"):
            st.session_state.selected_country = None
            st.rerun()

    country = next(c for c in countries if c["name"] == selected_name)

    # Optional: country-specific background using a locally stored flag image.
    # Add one of these files and a matching code in your JSON (recommended):
    #   assets/flags/US.png  with country["flag_code"] == "US"
    #   assets/flags/JP.png  with country["flag_code"] == "JP"
    flag_code = country.get("flag_code") or country.get("iso2")
    if flag_code:
        # 1) Prefer local asset if you have it
        flag_path = ASSETS_DIR / "flags" / f"{flag_code}.png"
        if flag_path.exists():
            set_page_background(flag_path)
        else:
            # 2) Otherwise fetch from a CDN (cached) so you don't need 193 files
            flag_bytes = fetch_flag_png_iso2(flag_code)
            if flag_bytes:
                set_page_background_bytes(flag_bytes, ext="png")
            else:
                st.caption(f"(Flag background not loaded — could not fetch https://flagcdn.com/w640/{flag_code.lower()}.png)")
    else:
        st.caption("(No ISO2/flag_code found for this country in countries_mock.json — add iso2 like 'US'.)")

    # Strong readability layer for dashboard content (ensures visibility on any flag)
    st.markdown(
        """
        <style>
          /* Solid main content panel */
          section.main > div > div.block-container {
            background: rgba(255,255,255,0.96) !important;
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 18px;
            padding: 28px 28px 18px 28px;
            box-shadow: 0 18px 70px rgba(0,0,0,0.22);
          }

          /* Ensure all dashboard text is dark */
          section.main h1, section.main h2, section.main h3, section.main h4,
          section.main p, section.main li, section.main label, section.main span {
            color: rgba(15,15,15,0.95) !important;
          }

          /* Metric blocks more distinct */
          div[data-testid="stMetric"] {
            background: rgba(255,255,255,0.98) !important;
            padding: 14px 16px !important;
            border-radius: 14px !important;
            border: 1px solid rgba(0,0,0,0.06) !important;
          }

          /* Force metric text colors (some Streamlit versions don't expose stMetricLabel testids reliably) */
          div[data-testid="stMetric"] * {
            color: rgba(15,15,15,0.95) !important;
            opacity: 1 !important;
          }

          /* Extra safety for known metric testids */
          div[data-testid="stMetricLabel"],
          div[data-testid="stMetricValue"],
          div[data-testid="stMetricDelta"],
          div[data-testid="stMetricLabel"] *,
          div[data-testid="stMetricValue"] *,
          div[data-testid="stMetricDelta"] * {
            color: rgba(15,15,15,0.95) !important;
            opacity: 1 !important;
          }

          /* Right-side panel slightly separated */
          .right-panel {
            border-left: 2px solid rgba(0,0,0,0.12);
            padding-left: 28px;
            margin-left: 10px;
            background: transparent;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1.4], gap="large")

    with left:
        st.subheader("Country Snapshot")

        c1, c2 = st.columns(2)
        c1.metric("Population", f'{country["population"]:,}')
        c2.metric("Capital", country["capital"])

        c3, c4 = st.columns(2)
        c3.metric("GDP (current USD)", fmt_money(country["gdp_usd"]))
        c4.metric("GDP per capita", fmt_money(country["gdp_per_capita_usd"]))

        st.markdown("### Key context (placeholder)")
        st.write("Add airport capacity, hotels, transit, tax, infrastructure indices, etc.")

        st.markdown("### GDP trend")
        series = gdp_df[gdp_df["country"] == selected_name].sort_values("year")
        if series.empty:
            st.warning("No GDP series found for this country.")
        else:
            fig = px.line(series, x="year", y="gdp_usd", markers=True, title=None)
            fig.update_layout(yaxis_title="GDP (USD)", xaxis_title="Year")
            st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown('<div class="right-panel">', unsafe_allow_html=True)
        st.subheader("World Cup Hosting Feasibility")

        st.markdown("### Headline FIFA hosting outputs")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Projected GDP lift", fmt_pct(country.get("wc_gdp_lift_pct")))
        m2.metric("Estimated host cost", fmt_money(country.get("wc_host_cost_usd")))
        m3.metric("Estimated net impact", fmt_money(country.get("wc_net_impact_usd")))
        m4.metric("Feasibility score", f'{country.get("feasibility_score", 0):.0f} / 100')

        st.markdown("### Tradeoffs (placeholder)")
        t1, t2, t3 = st.columns(3)
        t1.info("**Infrastructure readiness**\n\n(placeholder) stadium + transit readiness")
        t2.warning("**Fiscal / delivery risk**\n\n(placeholder) debt capacity, cost overrun risk")
        t3.success("**Legacy upside**\n\n(placeholder) tourism, soft power, FDI")

        st.markdown("</div>", unsafe_allow_html=True)


# ----------------- Router -----------------
if st.session_state.selected_country is None:
    render_landing()
else:
    render_dashboard(st.session_state.selected_country)