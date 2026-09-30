import pandas as pd
import streamlit as st
from datetime import datetime
import altair as alt

# PAGE CONFIGURATION
st.set_page_config(
    page_title="AUSTON ROBOT - SALES & SERVICE DASHBOARD",
    page_icon="🤖",
    layout="wide"
)

# CUSTOM CSS FOR ALL-CAPS TYPOGRAPHY
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-weight: 600 !important;
        color: #111827 !important;
        text-transform: uppercase !important;
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
    </style>
""", unsafe_allow_html=True)

# GOOGLE SHEET CONFIGURATION
SPREADSHEET_ID = "1BFFZWBHa35gZzQgTpP2NNIsMmYr06eWAb6jsXQJ1LVg"

st.sidebar.title("⚙️ DASHBOARD CONTROLS")
auto_refresh = st.sidebar.checkbox("REAL-TIME LIVE SYNC", value=True)
cache_ttl = 0 if auto_refresh else 10

@st.cache_data(ttl=cache_ttl)
def load_data(sheet_name: str) -> pd.DataFrame:
    """FETCH SHEET TAB VIA PUBLIC EXPORT LINK WITH ERROR HANDLING."""
    # Using pub?output=csv format for reliable fetching
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url)
        
        # Upper header names
        df.columns = [str(col).strip().upper() for col in df.columns]
        
        # Remove empty columns like Unnamed
        df = df.loc[:, ~df.columns.str.contains('^UNNAMED')]

        # Clean string values
        for col in df.select_dtypes(include='object').columns:
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

# LOAD OPERATIONAL SHEETS
df_enquiries = load_data("ENQUIRIES")
df_issues = load_data("CUSTOMER%20ISSUES")
df_visits = load_data("VISITS")
df_orders = load_data("ORDERS")

# IF SHEETS RETURN EMPTY, WARN USER
if df_enquiries.empty and df_issues.empty and df_visits.empty and df_orders.empty:
    st.error("⚠️ COULD NOT LOAD DATA FROM GOOGLE SHEET.")
    st.info("Please verify that your Google Sheet link sharing is set to 'Anyone with the link can view'.")
    st.stop()

# DYNAMICALLY EXTRACT ALL ACTUAL ENGINEERS & PRODUCTS
all_engineers = set()
all_products = set()

for df_temp in [df_enquiries, df_issues, df_visits, df_orders]:
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

df_enquiries_f = apply_filters(df_enquiries)
df_issues_f = apply_filters(df_issues)
df_visits_f = apply_filters(df_visits)
df_orders_f = apply_filters(df_orders)

# APP HEADER
col_title, col_btn = st.columns([4, 1])
with col_title:
    st.title("🤖 AUSTON ROBOT — OPERATIONS DASHBOARD")
    st.caption("REAL-TIME SALES PIPELINE & SERVICE MANAGEMENT SYSTEM")
with col_btn:
    st.write("")
    if st.button("🔄 FORCE SYNC DATA"):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# SEPARATED VIEW TABS (SALES VS SERVICE)
tab_sales, tab_service = st.tabs(["📈 SALES DASHBOARD", "🛠️ SERVICE DASHBOARD"])

# ==========================================
# 1. SALES DASHBOARD
# ==========================================
with tab_sales:
    st.header("📈 SALES & ENQUIRY PERFORMANCE")
    
    # SALES KPIS
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    
    tot_enq = len(df_enquiries_f) if not df_enquiries_f.empty else 0
    open_enq = len(df_enquiries_f[~df_enquiries_f['ENQUIRY STATUS'].astype(str).str.upper().isin(['WON', 'LOST'])]) if not df_enquiries_f.empty and 'ENQUIRY STATUS' in df_enquiries_f.columns else 0
    quotes_sent = len(df_enquiries_f[df_enquiries_f['QUOTATION STATUS'].astype(str).str.upper().isin(['SUBMITTED', 'ACCEPTED', 'REVISED'])]) if not df_enquiries_f.empty and 'QUOTATION STATUS' in df_enquiries_f.columns else 0
    exp_orders = len(df_enquiries_f[df_enquiries_f['EXPECTED ORDER'].astype(str).str.upper() == 'YES']) if not df_enquiries_f.empty and 'EXPECTED ORDER' in df_enquiries_f.columns else 0
    orders_rec = len(df_orders_f) if not df_orders_f.empty else 0
    
    today = pd.to_datetime(datetime.now().date())
    overdue_fu = len(df_enquiries_f[df_enquiries_f['NEXT FOLLOW-UP'] < today]) if not df_enquiries_f.empty and 'NEXT FOLLOW-UP' in df_enquiries_f.columns else 0

    kpi1.metric("TOTAL ENQUIRIES", tot_enq)
    kpi2.metric("OPEN ENQUIRIES", open_enq)
    kpi3.metric("QUOTES SENT", quotes_sent)
    kpi4.metric("EXP. ORDERS", exp_orders)
    kpi5.metric("ORDERS RECEIVED", orders_rec)
    kpi6.metric("OVERDUE FOLLOW-UPS", overdue_fu)

    st.markdown("---")

    col_s1, col_s2 = st.columns([1, 1])

    with col_s1:
        st.subheader("👨‍🔧 SALES ENGINEER ACTIVITY")
        sales_eng_data = []
        for eng in (engineers_sorted if engineers_sorted else ["NO ENGINEERS FOUND"]):
            e_enq = len(df_enquiries_f[df_enquiries_f['ENGINEER'].astype(str).str.upper() == eng]) if 'ENGINEER' in df_enquiries_f.columns else 0
            e_ord = len(df_orders_f[df_orders_f['ENGINEER'].astype(str).str.upper() == eng]) if 'ENGINEER' in df_orders_f.columns else 0
            sales_eng_data.append({
                "ENGINEER": eng,
                "ENQUIRIES LOGGED": e_enq,
                "ORDERS CLOSED": e_ord
            })
        st.dataframe(pd.DataFrame(sales_eng_data), use_container_width=True, hide_index=True)

        st.subheader("📦 PRODUCT SALES DISTRIBUTION")
        prod_sales_data = []
        for prod in (products_sorted if products_sorted else ["NO PRODUCTS FOUND"]):
            p_enq = len(df_enquiries_f[df_enquiries_f['PRODUCT'].astype(str).str.upper() == prod]) if 'PRODUCT' in df_enquiries_f.columns else 0
            p_ord = len(df_orders_f[df_orders_f['PRODUCT'].astype(str).str.upper() == prod]) if 'PRODUCT' in df_orders_f.columns else 0
            prod_sales_data.append({"PRODUCT": prod, "ENQUIRIES": p_enq, "ORDERS": p_ord})
        st.dataframe(pd.DataFrame(prod_sales_data), use_container_width=True, hide_index=True)

    with col_s2:
        st.subheader("📊 PIPELINE STAGE BREAKDOWN")
        stages = ["NEW", "CONTACTED", "DISCUSSION", "QUOTATION", "NEGOTIATION", "EXPECTED ORDER", "WON", "LOST"]
        p_counts = {}
        if 'ENQUIRY STATUS' in df_enquiries_f.columns and not df_enquiries_f.empty:
            counts = df_enquiries_f['ENQUIRY STATUS'].astype(str).str.upper().value_counts()
            for stage in stages:
                p_counts[stage] = counts.get(stage, 0)
        else:
            p_counts = {stage: 0 for stage in stages}

        df_p = pd.DataFrame(list(p_counts.items()), columns=["STAGE", "COUNT"])
        st.bar_chart(df_p.set_index("STAGE"))

    st.subheader("📋 RECENT ENQUIRIES & FOLLOW-UP TRACKER")
    if not df_enquiries_f.empty:
        st.dataframe(df_enquiries_f, use_container_width=True, hide_index=True)
    else:
        st.info("NO ENQUIRY DATA AVAILABLE.")


# ==========================================
# 2. SERVICE DASHBOARD
# ==========================================
with tab_service:
    st.header("🛠️ SERVICE OPERATIONS & CSAT TRACKER")
    
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

    st.subheader("📋 ALL CUSTOMER ISSUES LOG")
    if not df_issues_f.empty:
        st.dataframe(df_issues_f, use_container_width=True, hide_index=True)
    else:
        st.info("NO CUSTOMER ISSUES DATA AVAILABLE.")