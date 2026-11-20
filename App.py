import os
from PIL import Image
import pandas as pd
import streamlit as st
from datetime import datetime
import altair as alt
from streamlit_autorefresh import st_autorefresh

LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.webp")
logo_img = Image.open(LOGO_PATH) if os.path.exists(LOGO_PATH) else None

# PAGE CONFIGURATION
st.set_page_config(
    page_title="AUSTON - SERVICE OPERATIONS DASHBOARD",
    page_icon=logo_img if logo_img else "🛠️",
    layout="wide"
)

# CUSTOM CSS FOR ALL-CAPS TYPOGRAPHY & COMPACT HEADER
st.markdown("""
    <style>
    /* Reduce top whitespace of the page */
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
    }
    html, body, [class*="css"] {
        font-weight: 600 !important;
        color: #111827 !important;
        text-transform: uppercase !important;
    }
    .header-title {
        font-size: 1.35rem !important;
        font-weight: 800 !important;
        color: #0F172A !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
        text-transform: uppercase !important;
    }
    .header-caption {
        font-size: 0.75rem !important;
        color: #64748B !important;
        font-weight: 600 !important;
        margin-top: 2px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.03em !important;
    }
    [data-testid="stMetricLabel"] {
        font-weight: 700 !important;
        color: #374151 !important;
        font-size: 0.95rem !important;
        text-transform: uppercase !important;
    }
    [data-testid="stMetricValue"] {
        font-weight: 800 !important;
        color: #000000 !important;
        font-size: 1.8rem !important;
    }
    .stMarkdown h3, .stMarkdown h2, .stMarkdown h1 {
        font-weight: 800 !important;
        color: #0F172A !important;
        text-transform: uppercase !important;
    }
    hr {
        margin-top: 0.6rem !important;
        margin-bottom: 0.8rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# GOOGLE SHEET CONFIGURATION
# Priority: Streamlit Secrets → hardcoded fallback
# ─────────────────────────────────────────────────────────────
try:
    SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]
except (KeyError, FileNotFoundError):
    SPREADSHEET_ID = "1BFFZWBHa35gZzQgTpP2NNIsMmYr06eWAb6jsXQJ1LVg"

# ─────────────────────────────────────────────────────────────
# SIDEBAR CONTROLS
# ─────────────────────────────────────────────────────────────
if logo_img:
    st.sidebar.image(logo_img, width=150)

st.sidebar.title("⚙️ DASHBOARD CONTROLS")

auto_refresh = st.sidebar.checkbox("REAL-TIME LIVE SYNC", value=True)

if auto_refresh:
    refresh_interval = st.sidebar.select_slider(
        "AUTO-REFRESH INTERVAL",
        options=[30, 60, 120, 300, 600],
        value=60,
        format_func=lambda x: f"{x}s" if x < 60 else f"{x // 60}m"
    )
    st_autorefresh(interval=refresh_interval * 1000, limit=None, key="service_sync")
    st.sidebar.caption(f"⏱️ AUTO-REFRESHING EVERY {refresh_interval}S")
    cache_ttl = refresh_interval
else:
    cache_ttl = 300
    st.sidebar.caption("🔴 LIVE SYNC DISABLED")

@st.cache_data(ttl=cache_ttl)
def load_data(sheet_name: str) -> pd.DataFrame:
    """FETCH SHEET TAB VIA PUBLIC EXPORT LINK WITH ERROR HANDLING."""
    url = (
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
        f"/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    )
    try:
        df = pd.read_csv(url)

        # Upper header names
        df.columns = [str(col).strip().upper() for col in df.columns]

        # Remove empty columns like Unnamed
        df = df.loc[:, ~df.columns.str.contains('^UNNAMED')]

        # Clean string values
        for col in df.columns:
            if df[col].dtype == object or pd.api.types.is_string_dtype(df[col]):
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace({'nan': None, 'None': None, '': None})

        # Parse date columns
        for col in df.columns:
            if "DATE" in col or "FOLLOW-UP" in col:
                df[col] = pd.to_datetime(df[col], format='mixed', errors='coerce')

        return df
    except Exception as e:
        st.sidebar.error(f"Error loading tab '{sheet_name}': {e}")
        return pd.DataFrame()

# LOAD SERVICE SHEETS
df_issues = load_data("CUSTOMER%20ISSUES")
df_visits = load_data("VISITS")

# IF SHEETS RETURN EMPTY, WARN USER
if df_issues.empty and df_visits.empty:
    st.error("⚠️ COULD NOT LOAD SERVICE DATA FROM GOOGLE SHEET.")
    st.info("Please verify that your Google Sheet link sharing is set to 'Anyone with the link can view'.")
    st.stop()

# DYNAMICALLY EXTRACT SERVICE ENGINEERS & PRODUCTS
all_engineers = set()
all_products = set()

for df_temp in [df_issues, df_visits]:
    if not df_temp.empty:
        if 'ENGINEER' in df_temp.columns:
            all_engineers.update(df_temp['ENGINEER'].dropna().unique())
        if 'PRODUCT' in df_temp.columns:
            all_products.update(df_temp['PRODUCT'].dropna().unique())

engineers_sorted = sorted([str(e).upper() for e in all_engineers if str(e).strip() != ""])
products_sorted = sorted([str(p).upper() for p in all_products if str(p).strip() != ""])

# SIDEBAR FILTERS
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 FILTERS")

selected_engineer = st.sidebar.selectbox("FILTER BY ENGINEER", ["ALL"] + engineers_sorted)
selected_product = st.sidebar.selectbox("FILTER BY PRODUCT", ["ALL"] + products_sorted)

def apply_filters(df):
    if df.empty:
        return df
    filtered_df = df.copy()
    if selected_engineer != "ALL" and 'ENGINEER' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['ENGINEER'].astype(str).str.upper() == selected_engineer]
    if selected_product != "ALL" and 'PRODUCT' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['PRODUCT'].astype(str).str.upper() == selected_product]
    return filtered_df

df_issues_f = apply_filters(df_issues)
df_visits_f = apply_filters(df_visits)

# COMPACT APP HEADER
if logo_img:
    col_logo, col_title, col_btn = st.columns([0.6, 6.5, 1.5])
    with col_logo:
        st.image(logo_img, width=52)
    with col_title:
        st.markdown('<div class="header-title">AUSTON — SERVICE OPERATIONS DASHBOARD</div><div class="header-caption">REAL-TIME TICKET TRACKING & FIELD SERVICE MANAGEMENT</div>', unsafe_allow_html=True)
    with col_btn:
        if st.button("🔄 FORCE SYNC"):
            st.cache_data.clear()
            st.rerun()
else:
    col_title, col_btn = st.columns([7, 1.5])
    with col_title:
        st.markdown('<div class="header-title">AUSTON — SERVICE OPERATIONS DASHBOARD</div><div class="header-caption">REAL-TIME TICKET TRACKING & FIELD SERVICE MANAGEMENT</div>', unsafe_allow_html=True)
    with col_btn:
        if st.button("🔄 FORCE SYNC"):
            st.cache_data.clear()
            st.rerun()

st.markdown("---")

# SERVICE KPIS
skpi1, skpi2, skpi3, skpi4 = st.columns(4)

total_issues = len(df_issues_f) if not df_issues_f.empty else 0
open_issues = len(df_issues_f[~df_issues_f['CURRENT STATUS'].astype(str).str.upper().isin(['RESOLVED', 'CLOSED'])]) if not df_issues_f.empty and 'CURRENT STATUS' in df_issues_f.columns else 0
resolved_issues = len(df_issues_f[df_issues_f['CURRENT STATUS'].astype(str).str.upper().isin(['RESOLVED', 'CLOSED'])]) if not df_issues_f.empty and 'CURRENT STATUS' in df_issues_f.columns else 0
completed_visits = len(df_visits_f[df_visits_f['VISIT STATUS'].astype(str).str.upper() == 'COMPLETED']) if not df_visits_f.empty and 'VISIT STATUS' in df_visits_f.columns else 0

res_rate = round((resolved_issues / total_issues * 100), 1) if total_issues > 0 else 0.0

skpi1.metric("TOTAL ISSUES LOGGED", total_issues)
skpi2.metric("OPEN ISSUES", open_issues)
skpi3.metric("RESOLUTION RATE", f"{res_rate}%")
skpi4.metric("VISITS COMPLETED", completed_visits)

st.markdown("---")

col_sv1, col_sv2 = st.columns([1, 1])

with col_sv1:
    st.subheader("👨‍🔧 SERVICE ENGINEER METRICS")
    serv_eng_data = []
    for eng in (engineers_sorted if engineers_sorted else ["NO ENGINEERS FOUND"]):
        vis_cnt = len(df_visits_f[df_visits_f['ENGINEER'].astype(str).str.upper() == eng]) if 'ENGINEER' in df_visits_f.columns else 0
        o_iss = len(df_issues_f[(df_issues_f['ENGINEER'].astype(str).str.upper() == eng) & (~df_issues_f['CURRENT STATUS'].astype(str).str.upper().isin(['RESOLVED', 'CLOSED']))]) if 'ENGINEER' in df_issues_f.columns and 'CURRENT STATUS' in df_issues_f.columns else 0
        r_iss = len(df_issues_f[(df_issues_f['ENGINEER'].astype(str).str.upper() == eng) & (df_issues_f['CURRENT STATUS'].astype(str).str.upper().isin(['RESOLVED', 'CLOSED']))]) if 'ENGINEER' in df_issues_f.columns and 'CURRENT STATUS' in df_issues_f.columns else 0

        serv_eng_data.append({
            "ENGINEER": eng,
            "VISITS COMPLETED": vis_cnt,
            "OPEN ISSUES": o_iss,
            "RESOLVED ISSUES": r_iss
        })
    st.dataframe(pd.DataFrame(serv_eng_data), use_container_width=True, hide_index=True)

with col_sv2:
    st.subheader("⚠️ ISSUES BY PRIORITY MATRIX")
    if not df_issues_f.empty and 'PRIORITY' in df_issues_f.columns:
        priority_counts = df_issues_f['PRIORITY'].astype(str).str.upper().value_counts().reset_index()
        priority_counts.columns = ['PRIORITY', 'COUNT']

        chart = alt.Chart(priority_counts).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
            x=alt.X('PRIORITY', sort=['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
            y='COUNT',
            color=alt.Color('PRIORITY', scale=alt.Scale(domain=['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'], range=['#2ECC71', '#F1C40F', '#E67E22', '#E74C3C'])),
            tooltip=['PRIORITY', 'COUNT']
        ).properties(height=220)
        st.altair_chart(chart, use_container_width=True)

st.markdown("---")

st.subheader("📋 ALL CUSTOMER ISSUES LOG")
if not df_issues_f.empty:
    st.dataframe(df_issues_f, use_container_width=True, hide_index=True)
else:
    st.info("NO CUSTOMER ISSUES DATA AVAILABLE.")
