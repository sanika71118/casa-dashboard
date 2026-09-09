import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os, glob, json, urllib.request

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CASA Georgia Dashboard",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ── THEME ─────────────────────────────────────────────────────────────────────
RED       = "#C8102E"
DKBLUE    = "#002855"
LTBLUE    = "#1D4E89"
GOLD      = "#F5A623"
WHITE     = "#FFFFFF"
LGRAY     = "#F4F6F9"
MIDGRAY   = "#D0D5DD"
CHART_COLORS = [RED, DKBLUE, LTBLUE, "#E84B61", "#3A6EA8", "#8B1A2C",
                "#1A3A5C", GOLD, "#2ECC71", "#9B59B6", "#E67E22",
                "#1ABC9C", "#16A085", "#8E44AD", "#D35400"]

# ── SOURCE RANK PALETTE ───────────────────────────────────────────────────────
# Top 5 sources each get a distinct hue; the remainder shares one gray.
# The same map drives the donut and the bar, so a color = one specific source.
TOP5_COLORS = [RED, DKBLUE, GOLD, LTBLUE, "#00857C"]
TAIL_COLOR  = "#AEB7C4"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
.stApp {{background-color:{LGRAY}}}
[data-testid="stSidebar"] {{background:linear-gradient(180deg,{DKBLUE} 0%,{LTBLUE} 100%)}}
[data-testid="stSidebar"] * {{color:{WHITE} !important}}
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{background-color:{RED} !important}}
.casa-header {{background:linear-gradient(90deg,{DKBLUE},{RED});padding:18px 28px;border-radius:12px;margin-bottom:20px}}
.casa-header h1 {{color:{WHITE};font-size:26px;font-weight:700;font-family:Georgia,serif;margin:0}}
.casa-header p {{color:rgba(255,255,255,.85);margin:4px 0 0 0;font-size:13px}}
.kpi-card {{background:{WHITE};border-radius:10px;padding:16px 20px;border-left:5px solid {RED};box-shadow:0 2px 6px rgba(0,40,85,.09);margin-bottom:6px}}
.kpi-card.blue {{border-left-color:{DKBLUE}}}
.kpi-label {{color:{DKBLUE};font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px}}
.kpi-value {{color:{RED};font-size:34px;font-weight:800;line-height:1}}
.kpi-card.blue .kpi-value {{color:{DKBLUE}}}
.kpi-sub {{color:#667085;font-size:11px;margin-top:3px}}
.sec-head {{background:{DKBLUE};color:{WHITE};padding:9px 16px;border-radius:8px 8px 0 0;font-size:14px;font-weight:700;margin-top:12px}}
.sec-body {{background:{WHITE};border-radius:0 0 10px 10px;padding:14px;box-shadow:0 2px 6px rgba(0,40,85,.07);margin-bottom:6px}}
.divider {{height:3px;background:linear-gradient(90deg,{RED},{DKBLUE});border-radius:2px;margin:16px 0}}
.note-box {{background:#FFF8E7;border-left:3px solid {GOLD};padding:8px 12px;border-radius:0 6px 6px 0;font-size:11px;color:#7A5500;margin-bottom:10px;line-height:1.6}}
footer,#MainMenu,header {{visibility:hidden}}
</style>
""", unsafe_allow_html=True)

# ── MAPPINGS ──────────────────────────────────────────────────────────────────
from casa_mappings import COUNTY_TO_AFF, REGIONS, COUNTY_COORDS, GA_COUNTY_FIPS

# ── VOLUNTEER DATA — loaded from Excel file in /data ─────────────────────────
# Name your sworn-in file: volunteers_sworn_in.xlsx and drop it in /data
# Expected columns: Counties | FY XXXX - Nth Qtr | ...
# Add new FY columns to the Excel and the dashboard picks them up automatically

@st.cache_data
def load_volunteer_data():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    # Look for a file with "volunteer" or "sworn" in the name
    candidates = glob.glob(os.path.join(data_dir, "*volunteer*sworn*.xlsx")) + \
                 glob.glob(os.path.join(data_dir, "*sworn*.xlsx")) + \
                 glob.glob(os.path.join(data_dir, "*volunteer*in*.xlsx"))
    if not candidates:
        return {}, []
    path = candidates[0]
    df = pd.read_excel(path, sheet_name=0)
    # Drop TOTALS row
    df = df[df.iloc[:,0].astype(str).str.upper() != 'TOTALS'].copy()
    df = df.dropna(subset=[df.columns[0]])
    affiliate_col = df.columns[0]
    qtr_cols = [c for c in df.columns if c != affiliate_col]
    # Build {affiliate: [q1, q2, q3, ...]} dict
    vol = {}
    for _, row in df.iterrows():
        aff = str(row[affiliate_col]).strip()
        vals = [int(row[c]) if pd.notna(row[c]) else 0 for c in qtr_cols]
        vol[aff] = vals
    return vol, qtr_cols

VOLUNTEER_DATA, VOL_QTR_COLS = load_volunteer_data()

# Quarter label builder — maps column names to readable labels
def col_to_label(col):
    # e.g. "FY 2026 - 1st Qtr" → "FY26 Q1"
    import re
    m = re.search(r'(\d{4}).*?(\d)[snrt][tdh]', col)
    if m:
        fy = m.group(1)[2:]
        q  = m.group(2)
        return f"FY{fy} Q{q}"
    return col

VOL_QTR_LABELS = [col_to_label(c) for c in VOL_QTR_COLS]

# Fallback if no file found — use last known data
if not VOLUNTEER_DATA:
    VOLUNTEER_DATA = {
        'Advo-Kids':[0,4,0,3,0,1,4],'Alapaha':[4,2,0,2,0,2,0],
        'Alcovy':[5,1,0,3,3,3,0],'Appalachian':[2,7,2,3,4,1,1],
        'Athens-Oconee':[0,10,18,1,5,8,1],'Atlanta':[16,2,19,23,26,18,11],
        'Atlantic':[3,1,1,1,3,0,5],'Augusta':[11,9,4,15,6,15,14],
        'Carroll':[4,11,5,3,10,9,4],'CASA Kids':[4,0,4,0,5,9,0],
        'Central Ga':[0,0,0,0,0,0,7],'Chattahoochee':[0,0,8,0,1,9,1],
        'Cherokee':[9,1,14,9,2,11,3],"Children's Voice":[0,5,6,5,0,5,0],
        'Clayton':[5,1,0,0,1,0,0],'Coastal Plain':[0,9,0,1,0,5,3],
        'Cobb':[5,8,0,14,6,4,0],'Coweta':[0,2,1,8,12,3,0],
        'Dekalb':[3,5,4,5,6,0,0],'Dougherty':[4,3,3,0,1,0,8],
        'Enotah':[0,5,1,0,2,0,2],'Floyd':[0,4,0,2,4,1,1],
        'Forsyth':[6,6,0,4,2,0,11],'Glynn':[10,0,4,3,5,2,0],
        'Gwinnett':[9,7,0,4,15,5,4],'Hall-Dawson':[10,4,0,11,1,6,8],
        'Henry':[0,3,0,3,2,3,7],'Houston':[2,4,0,7,8,1,0],
        'Lookout':[7,0,0,4,5,1,6],'Lowndes':[1,5,0,4,0,8,0],
        'Murray/Whit':[0,0,1,1,0,2,2],'Northeast':[3,2,6,1,3,4,2],
        'Northern':[0,0,1,0,0,1,6],'Northwest':[0,7,0,9,0,7,0],
        'Ocmulgee':[0,3,2,0,0,5,0],'Ogeechee':[3,0,1,3,0,2,0],
        'Paulding':[4,5,6,0,5,3,7],'Piedmont':[0,2,7,0,0,4,7],
        'Polk /Haralson':[1,2,3,0,0,3,0],'Rockdale':[5,4,0,5,5,4,0],
        'Savannah':[7,14,11,12,8,9,7],'Southeast Georgia':[4,0,0,2,3,3,0],
        'SOWEGA':[5,6,0,6,3,1,1],'SW Georgia':[2,0,1,2,3,1,0],
        'TLC':[2,3,1,1,4,0,0],'Towaliga':[3,6,7,0,3,0,0],'Troup':[0,1,0,1,1,0,0],
    }
    VOL_QTR_COLS  = ['FY 2025 - 1st Qtr','FY 2025 - 2nd Qtr','FY 2025 - 3rd Qtr',
                     'FY 2025 - 4th Qtr','FY 2026 - 1st Qtr','FY 2026 - 2nd Qtr','FY 2026 - 3rd Qtr']
    VOL_QTR_LABELS = ['FY25 Q1','FY25 Q2','FY25 Q3','FY25 Q4','FY26 Q1','FY26 Q2','FY26 Q3']
# ── Reconcile sworn-in affiliate names with the CAPTA affiliate names ─────────
AFF_ALIAS = {
    'Atlantic':       'Atlantic Area',
    'Central Ga':     'Central Georgia',
    'Cherokee':       'Cherokee CASA',
    'Dekalb':         'DeKalb',
    'Lookout':        'Lookout Mt.',
    'Lowndes':        'Lowndes & Echols',
    'Murray/Whit':    'Murray/Whitfield',
    'Northeast':      'Northeast Georgia',
    'Northwest':      'Northwest Ga',
    'Polk /Haralson': 'Polk/Haralson',
    'Savannah':       'Savannah-Chatham',
    'SW Georgia':     'Southwest Georgia',
}
VOLUNTEER_DATA = {
    AFF_ALIAS.get(k.replace('*', '').strip(), k.replace('*', '').strip()): v
    for k, v in VOLUNTEER_DATA.items()
}

_known = set(COUNTY_TO_AFF.values())
_unmatched = sorted(set(VOLUNTEER_DATA) - _known)
if _unmatched:
    st.sidebar.warning("Sworn-in affiliates not recognised: " + ", ".join(_unmatched))
@st.cache_data
def load_ga_geojson():
    import urllib.request, json
    url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            all_geo = json.loads(r.read())
        ga_features = [f for f in all_geo['features'] if f['id'].startswith('13')]
        return {'type':'FeatureCollection','features':ga_features}
    except Exception:
        return None


@st.cache_data
def load_data():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    all_files = glob.glob(os.path.join(data_dir, "*.xlsx")) + glob.glob(os.path.join(data_dir, "*.csv"))
    all_files = [f for f in all_files if "volunteers" not in f.lower() and "sworn" not in f.lower()]
    all_dfs = []
    for path in all_files:
        try:
            if path.endswith('.csv'):
                df = pd.read_csv(path)
            else:
                xl = pd.ExcelFile(path)
                df = pd.read_excel(path, sheet_name=xl.sheet_names[0])
            df['_source_file'] = os.path.basename(path)
            all_dfs.append(df)
        except Exception as e:
            st.warning(f"Could not read {os.path.basename(path)}: {e}")
    if not all_dfs:
        return pd.DataFrame()
    combined = pd.concat(all_dfs, ignore_index=True)
    col_map = {}
    for c in combined.columns:
        if 'County Preference' in str(c): col_map[c] = 'County'
        elif 'How Did You Hear' in str(c): col_map[c] = 'Source'
        elif 'Entry Date' in str(c): col_map[c] = 'EntryDate'
    combined.rename(columns=col_map, inplace=True)
    combined['EntryDate'] = pd.to_datetime(combined['EntryDate'], errors='coerce')
    combined = combined.dropna(subset=['EntryDate'])
    combined['Year']           = combined['EntryDate'].dt.year
    combined['Month']          = combined['EntryDate'].dt.month
    combined['YearMonth']      = combined['EntryDate'].dt.to_period('M').astype(str)
    combined['MonthLabel']     = combined['EntryDate'].dt.strftime('%b %Y')

    # ── Normalize source names across old and new file formats ────────────────
    combined['Source'] = combined['Source'].fillna('Unknown')

    # Reclassify "Other - give details in box below" using the details column
    details_col = None
    for c in combined.columns:
        if 'detail' in str(c).lower() or ('comment' in str(c).lower() and 'how' in str(c).lower()):
            details_col = c
            break

    def classify_other(text):
        if pd.isna(text):
            return 'Other'
        t = str(text).lower().strip()
        if any(x in t for x in ['google','online','search','website','internet','web','researching','looked up','volunteermatch','volunteer match','idealist','just serve','justserve','email','e-mail','browsing','came across','found it online']):
            return 'Online Search'
        if any(x in t for x in ['friend','colleague','coworker','co-worker','sister','brother','mother','father','husband','wife','family','neighbor','classmate','mentor','sorority','alumni','alumna','kappa','fraternity','partner','spouse','relative','aunt','uncle','cousin','nephew','niece','boss','supervisor','daughter','son','a friend','my friend','from a friend','word of mouth','people','someone told','told me','recommended','i know someone','i know volunteers','i know people','know volunteer','know a casa']):
            return 'Personal Referral'
        if any(x in t for x in ['former volunteer','previous volunteer','was a casa','was a volunteer','volunteered before','past volunteer','used to volunteer','used to be','previously volunteer','former casa','i was a casa','served as a casa','i am a casa','i volunteered for','volunteer in ','volunteering in','volunteer years','used to do it','casa in ohio','casa in hawaii','casa in ny','casa in louisiana','casa in maryland','casa in florida','casa in texas','casa of','used to work','previously worked','history with casa','experience with casa','transfer','was an approved','interned for casa','i use to be','i used to be','been involved','did florida ad item','started the process']):
            return 'Past Experience'
        if any(x in t for x in ['facebook','instagram','tiktok','twitter','social media','fb post','fb ad','ad popped','youtube','linkedin','tik tok','camp to belong','#save']):
            return 'Social Media'
        if any(x in t for x in ['tv','television','news','newscast','dr phil','broadcast','news report','news break','news first','anf','atlanta news','novel','book','documentary']):
            return 'TV'
        if any(x in t for x in ['work','employer','dfcs','dfas','dcfs','caseworker','social worker','court','judge','legal','lawyer','attorney','paralegal','human services','school','university','college','class','professor','training','internship','dfacs','impact training','criminal justice','degree','graduate','education','fletc','united way','department of','state representative','program director','licensed social']):
            return 'Workplace'
        if any(x in t for x in ['church','faith','ministry','pastor','religious','congregation','temple','mosque','community','fostering together','foster']):
            return 'Church'
        if any(x in t for x in ['flyer','flier','trifold','brochure','handout','newspaper','magazine','henry herald','print','newsletter','posting on']):
            return 'Print/Newspaper'
        if any(x in t for x in ['billboard','airport','yard sign','banner','advertisement']):
            return 'Billboard'
        if any(x in t for x in ['radio','podcast']):
            return 'Radio'
        if any(x in t for x in ['speaking','presentation','conference','seminar','panel','summit']):
            return 'Speaking Engagement'
        if any(x in t for x in ['heard','learned','became aware','always wanted','passion','interest','looking for ways','looking for volunteer','been looking','came across','i know','advocate','through volunteer','other volunteer','a fellow volunteer','through people','through others']):
            return 'Personal Referral'
        return 'Other'

    # Apply reclassification to rows where source was "Other - give details..."
    if details_col:
        other_mask = combined['Source'].str.contains('Other - give details', na=False) | (combined['Source'] == 'Unknown')
        combined.loc[other_mask, 'Source'] = combined.loc[other_mask, details_col].apply(classify_other)

    src = combined['Source'].str.strip()
    src_map = {
        'Other - give details in box below': 'Other',
        'Other - Give Details Below':        'Other',
        'Online Search':                     'Online Search',
        'Website':                           'Online Search',
        'Personal Referral':                 'Personal Referral',
        'Past Experience':                   'Past Experience',
        'Social Media':                      'Social Media',
        'Workplace':                         'Workplace',
        'Workplace/University':              'Workplace',
        'TV':                                'TV',
        'Print':                             'Print/Newspaper',
        'Newspaper':                         'Print/Newspaper',
        'Flier':                             'Print/Newspaper',
        'Billboard':                         'Billboard',
        'Radio':                             'Radio',
        'Church':                            'Church',
        'Special Event':                     'Special Event',
        'Speaking Engagement':               'Speaking Engagement',
        "Don't Recall":                      "Don't Recall",
        'Yard Sign':                         'Yard Sign',
        'Podcast':                           'Podcast',
        'Car Magnet':                        'Billboard',
        'Unknown':                           'Other',
    }
    combined['Source'] = combined['Source'].map(src_map).fillna(combined['Source'])

    # ── Affiliate — blank county → "No County Selected" not "Unassigned" ─────
    combined['Affiliate'] = combined['County'].map(COUNTY_TO_AFF)
    combined['Affiliate'] = combined['Affiliate'].fillna(
        combined['County'].apply(lambda c: 'No County Selected' if pd.isna(c) or str(c).strip() in ['', 'nan', 'SELECT COUNTY BELOW', 'Georgia CASA'] else 'Other')
    )
    def get_fy_quarter(ym):
        m = int(ym.split('-')[1])
        return 'Q1' if m in [7,8,9] else 'Q2' if m in [10,11,12] else 'Q3' if m in [1,2,3] else 'Q4'

    def get_fy_year(ym):
        # FY runs Jul→Jun. Jul-Dec belong to the NEXT calendar year's FY.
        # e.g. Jul 2023 → FY2024, Jan 2024 → FY2024, Jul 2024 → FY2025
        y = int(ym.split('-')[0])
        m = int(ym.split('-')[1])
        return y + 1 if m >= 7 else y

    combined['FYQuarter'] = combined['YearMonth'].apply(get_fy_quarter)
    combined['FYYear']    = combined['YearMonth'].apply(get_fy_year)
    combined['FYLabel']   = combined.apply(lambda r: f"FY{str(r['FYYear'])[2:]} {r['FYQuarter']}", axis=1)
    return combined

df = load_data()
if df.empty:
    st.error("No data found. Add Excel files to the /data folder.")
    st.stop()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:10px 0 16px'>
        <div style='font-size:32px'>⚖️</div>
        <div style='font-size:18px;font-weight:800;color:white;font-family:Georgia,serif'>CASA Georgia</div>
        <div style='font-size:10px;color:rgba(255,255,255,.65);margin-top:2px'>Volunteer Inquiries Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    page = st.radio("📄 **Navigate**", ["Page 1 — Inquiries", "Page 2 — Volunteer Map", "Page 3 — Quarterly Analysis"], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("<div style='font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:rgba(255,255,255,.5)'>Filter by Month</div>", unsafe_allow_html=True)
    month_options = sorted(df['YearMonth'].unique())
    month_labels  = {m: pd.Period(m,'M').strftime('%B %Y') for m in month_options}
    # Current fiscal year, derived from the data — no hardcoded dates
    current_fy  = int(df['FYYear'].max())
    fy_months   = sorted(df[df['FYYear'] == current_fy]['YearMonth'].unique())

    # FY filter buttons
    st.markdown("<div style='font-size:10px;color:rgba(255,255,255,.6);margin-bottom:4px'>Quick select:</div>", unsafe_allow_html=True)
    fy_col1, fy_col2 = st.columns(2)
    with fy_col1:
        if st.button(f"FY{current_fy}", use_container_width=True, key="fy26btn"):
            st.session_state['month_selection'] = 'current_fy'
    with fy_col2:
        if st.button("All FYs", use_container_width=True, key="allbtn"):
            st.session_state['month_selection'] = 'all'

    # Default to the current FY on first load
    if 'month_selection' not in st.session_state:
        st.session_state['month_selection'] = 'current_fy'

    select_all = st.checkbox("All Months", value=(st.session_state['month_selection'] == 'all'))
    if select_all:
        st.session_state['month_selection'] = 'all'
        selected_months = month_options
    else:
        default_months = fy_months if st.session_state['month_selection'] == 'current_fy' else month_options[-3:]
        selected_months = st.multiselect("Choose months:", options=month_options,
                                          format_func=lambda x: month_labels[x],
                                          default=[m for m in default_months if m in month_options])

    if not selected_months:
        st.warning("Select at least one month.")
        st.stop()

    st.markdown("---")
    st.markdown(f"""<div style='font-size:11px;color:rgba(255,255,255,.7)'>
        📁 {len(df['_source_file'].unique())} files loaded<br>
        📊 {len(df):,} total records<br>
        📅 {month_labels[month_options[0]]} → {month_labels[month_options[-1]]}
    </div>""", unsafe_allow_html=True)
    st.markdown("""<div style='font-size:10px;color:rgba(255,255,255,.4);margin-top:12px;text-align:center'>
        Add new months: drop .xlsx<br>into the /data folder
    </div>""", unsafe_allow_html=True)

filtered = df[df['YearMonth'].isin(selected_months)]
period_label = f"{month_labels[selected_months[0]]} – {month_labels[selected_months[-1]]}" if len(selected_months) > 1 else month_labels[selected_months[0]]

def style_fig(fig, height=340):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial,sans-serif", color=DKBLUE),
        margin=dict(l=20,r=20,t=30,b=20), height=height,
        legend=dict(orientation="h",yanchor="bottom",y=-0.3,xanchor="center",x=0.5),
        xaxis=dict(gridcolor="#E8ECF0",linecolor=MIDGRAY),
        yaxis=dict(gridcolor="#E8ECF0",linecolor=MIDGRAY),
    )
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — INQUIRIES DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "Page 1 — Inquiries":

    st.markdown(f"""<div class="casa-header">
        <h1>⚖️ CASA Georgia — Volunteer Inquiries</h1>
        <p>Period: <strong>{period_label}</strong> &nbsp;|&nbsp; {len(filtered):,} inquiries</p>
    </div>""", unsafe_allow_html=True)

    # KPIs
    k1,k2,k3,k4 = st.columns(4)
    # For KPIs exclude entries with no county selected
    assigned = filtered[~filtered['Affiliate'].isin(['No County Selected','Other'])]
    top_src    = filtered['Source'].value_counts().idxmax() if not filtered.empty else "—"
    top_src_n  = filtered['Source'].value_counts().iloc[0] if not filtered.empty else 0
    top_county = assigned['County'].value_counts().idxmax() if not assigned.empty else "—"
    top_county_n = assigned['County'].value_counts().iloc[0] if not assigned.empty else 0
    top_aff    = assigned['Affiliate'].value_counts().idxmax() if not assigned.empty else "—"
    top_aff_n  = assigned['Affiliate'].value_counts().iloc[0] if not assigned.empty else 0

    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Inquiries</div><div class="kpi-value">{len(filtered):,}</div><div class="kpi-sub">Across {len(selected_months)} month(s)</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card blue"><div class="kpi-label">Top Source</div><div class="kpi-value" style="font-size:20px;padding-top:5px">{top_src}</div><div class="kpi-sub">{top_src_n} inquiries</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Top County</div><div class="kpi-value" style="font-size:20px;padding-top:5px">{top_county}</div><div class="kpi-sub">{top_county_n} inquiries</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-card blue"><div class="kpi-label">Top Affiliate</div><div class="kpi-value" style="font-size:16px;padding-top:6px">{top_aff}</div><div class="kpi-sub">{top_aff_n} inquiries</div></div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # Chart 1: Monthly
    st.markdown("<div class='sec-head'>📅 1. Total Inquiries by Month</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-body'>", unsafe_allow_html=True)
    monthly = filtered.groupby(['YearMonth','MonthLabel']).size().reset_index(name='Count').sort_values('YearMonth')
    if not monthly.empty:
        peak_month = monthly.loc[monthly['Count'].idxmax(), 'MonthLabel']
        peak_val   = monthly['Count'].max()
        low_month  = monthly.loc[monthly['Count'].idxmin(), 'MonthLabel']
        low_val    = monthly['Count'].min()
        avg_val    = round(monthly['Count'].mean())
        trend_dir  = "increasing" if monthly['Count'].iloc[-1] > monthly['Count'].iloc[0] else "decreasing"
        st.markdown(f"""<div class='note-box'>
            💡 <strong>What this tells you:</strong> Each bar shows how many people reached out about volunteering that month.
            The dotted line shows the trend. <strong>{peak_month}</strong> had the highest interest with <strong>{peak_val}</strong> inquiries,
            while <strong>{low_month}</strong> was the lowest with <strong>{low_val}</strong>.
            The average is <strong>{avg_val} inquiries/month</strong> and the overall trend is <strong>{trend_dir}</strong>.
            &nbsp;|&nbsp; <span style="color:#C8102E;font-weight:700">■ Red</span> = Growth plan era (FY2024+) &nbsp;
            <span style="color:#D4607A;font-weight:700">■ Rose</span> = Pre-growth plan
        </div>""", unsafe_allow_html=True)
    fig1 = go.Figure()
    # Color each bar: CASA red = growth plan (FY24+), light rose = pre-growth
    def bar_color(ym):
        y, m = int(ym.split('-')[0]), int(ym.split('-')[1])
        fy = y+1 if m >= 7 else y
        return RED if fy >= 2024 else "#F4A0A8"
    bar_colors = [bar_color(ym) for ym in monthly['YearMonth']]
    fig1.add_trace(go.Bar(
        x=monthly['MonthLabel'], y=monthly['Count'],
        marker_color=bar_colors,
        marker_line_color=[DKBLUE if c==RED else "#C8607A" for c in bar_colors],
        marker_line_width=0.5,
        text=monthly['Count'], textposition='outside',
        textfont=dict(color=DKBLUE, size=11, family="Arial Black"),
        hovertemplate="<b>%{x}</b><br>Inquiries: %{y}<extra></extra>"))
    fig1.add_trace(go.Scatter(x=monthly['MonthLabel'], y=monthly['Count'],
        mode='lines+markers', line=dict(color=DKBLUE, width=2, dash='dot'),
        marker=dict(color=DKBLUE, size=5), hoverinfo='skip'))
    style_fig(fig1, 300)
    fig1.update_layout(showlegend=False, bargap=0.3)
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

            # Chart 2: Source
    st.markdown("<div class='sec-head'>📢 2. Inquiries by Source</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-body'>", unsafe_allow_html=True)

    src_counts = filtered['Source'].value_counts().reset_index()
    src_counts.columns = ['Source', 'Count']

    # ── Build ONE top-5 table + shared color map used by both charts ──────────
    top5       = src_counts.head(5)[['Source', 'Count']].copy()
    tail_count = int(src_counts.iloc[5:]['Count'].sum())

    plot_df = top5
    if tail_count > 0:
        plot_df = pd.concat(
            [top5, pd.DataFrame([{'Source': 'All other sources', 'Count': tail_count}])],
            ignore_index=True)

    SRC_COLOR = {s: TOP5_COLORS[i] for i, s in enumerate(top5['Source'])}
    SRC_COLOR['All other sources'] = TAIL_COLOR
    plot_colors = [SRC_COLOR[s] for s in plot_df['Source']]

    total_src    = int(src_counts['Count'].sum())
    top_src_name = src_counts.iloc[0]['Source']
    top_src_pct  = round(src_counts.iloc[0]['Count'] / total_src * 100)
    second_src   = src_counts.iloc[1]['Source'] if len(src_counts) > 1 else "—"
    top5_pct     = round(top5['Count'].sum() / total_src * 100)
    n_other      = len(src_counts) - 5

    st.markdown(f"""<div class='note-box'>
        💡 <strong>What this tells you:</strong> Most people who inquire about volunteering hear about CASA
        through <strong>{top_src_name}</strong> ({top_src_pct}% of all inquiries), with
        <strong>{second_src}</strong> second. These top 5 channels drive <strong>{top5_pct}%</strong> of all
        interest — the remaining {n_other} sources are grouped in gray. This helps CASA focus marketing:
        invest more in what is already driving the most interest. Open the table below for the full list.
    </div>""", unsafe_allow_html=True)

    c2a, c2b = st.columns(2)

    with c2a:
        fig2a = px.pie(plot_df, values='Count', names='Source', hole=0.55,
                       color='Source', color_discrete_map=SRC_COLOR,
                       category_orders={'Source': list(plot_df['Source'])})
        fig2a.update_traces(
            sort=False,
            textposition='inside', insidetextorientation='horizontal',
            texttemplate="<b>%{percent}</b>",
            marker=dict(line=dict(color=WHITE, width=2)),
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>")
        fig2a.add_annotation(
            text=f"<b>{total_src:,}</b><br><span style='font-size:11px'>inquiries</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=22, color=DKBLUE, family="Arial"))
        fig2a.update_layout(
            height=360, paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=20, b=10),
            legend=dict(orientation="v", x=1.01, y=0.5, xanchor="left",
                        font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
            showlegend=True,
            font=dict(family="Arial,sans-serif", color=DKBLUE))
        st.plotly_chart(fig2a, use_container_width=True)

    with c2b:
        fig2b = go.Figure(go.Bar(
            x=plot_df['Count'], y=plot_df['Source'], orientation='h',
            marker_color=plot_colors,
            text=plot_df['Count'], textposition='outside', cliponaxis=False,
            textfont=dict(size=12, color=DKBLUE, family="Arial Black"),
            hovertemplate="<b>%{y}</b><br>Count: %{x}<extra></extra>"))
        style_fig(fig2b, 360)
        fig2b.update_layout(
            bargap=0.35,
            yaxis=dict(autorange='reversed', gridcolor="rgba(0,0,0,0)",
                       tickfont=dict(size=12)),
            xaxis=dict(gridcolor="#E8ECF0"),
            showlegend=False,
            margin=dict(l=20, r=70, t=30, b=20))
        st.plotly_chart(fig2b, use_container_width=True)

    with st.expander("🔍 All sources — full breakdown"):
        full = src_counts.copy()
        full['% of total'] = (full['Count'] / total_src * 100).round(1).astype(str) + '%'
        full.index = range(1, len(full) + 1)
        st.dataframe(full.style.bar(subset=['Count'], color=RED + "88"),
                     use_container_width=True, height=300)

    st.markdown("</div>", unsafe_allow_html=True)

    # Chart 3: County map
    st.markdown("<div class='sec-head'>🗺️ 3. Inquiries by County & Affiliate</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-body'>", unsafe_allow_html=True)
    county_counts = filtered['County'].value_counts().reset_index()
    county_counts.columns = ['County','Count']
    county_counts['Affiliate'] = county_counts['County'].map(COUNTY_TO_AFF).fillna('Other')
    # Remove unassigned/unknown entries from map display
    county_counts = county_counts[~county_counts['Affiliate'].isin(['Other','Unassigned','No County Selected'])]
    county_counts['Lat'] = county_counts['County'].map(lambda c: COUNTY_COORDS.get(c,(None,None))[0])
    county_counts['Lon'] = county_counts['County'].map(lambda c: COUNTY_COORDS.get(c,(None,None))[1])
    map_data = county_counts.dropna(subset=['Lat','Lon'])
    top_aff_map = map_data.groupby('Affiliate')['Count'].sum().idxmax() if not map_data.empty else "—"
    top_aff_map_n = map_data.groupby('Affiliate')['Count'].sum().max() if not map_data.empty else 0
    active_counties = len(map_data)
    st.markdown(f"""<div class='note-box'>
        💡 <strong>What this tells you:</strong> Each bubble on the map represents a Georgia county — bigger bubble means more inquiries from that area.
        Bubbles are color-coded by affiliate so you can instantly see which affiliate regions are most active.
        <strong>{top_aff_map}</strong> is currently the most active affiliate with <strong>{top_aff_map_n}</strong> inquiries
        across <strong>{active_counties}</strong> counties with activity. Use this to identify where CASA has strong interest
        and where outreach could be strengthened.
    </div>""", unsafe_allow_html=True)

    c3a,c3b = st.columns([3,2])
    with c3a:
        fig_map = px.scatter_map(map_data, lat='Lat', lon='Lon', size='Count',
            color='Affiliate', hover_name='County',
            hover_data={'Count':True,'Affiliate':True,'Lat':False,'Lon':False},
            size_max=42, zoom=6.4, center={"lat":32.65,"lon":-83.4},
            color_discrete_sequence=CHART_COLORS, map_style="carto-positron")
        fig_map.update_layout(height=420, margin=dict(l=0,r=0,t=0,b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="v",x=1.0,y=1.0,xanchor="left",
                        bgcolor="rgba(255,255,255,.95)",bordercolor=MIDGRAY,
                        borderwidth=1,font=dict(size=9),
                        title=dict(text="Affiliate",font=dict(size=10))))
        st.plotly_chart(fig_map, use_container_width=True)
    with c3b:
        view3 = st.radio("Show", ["Top 10", "Bottom 10"], horizontal=True,
                         key="p1_aff_view", label_visibility="collapsed")

        counts = (filtered[~filtered['Affiliate'].isin(['No County Selected', 'Other'])]
                  ['Affiliate'].value_counts())
        # include affiliates with zero inquiries — they matter most in Bottom 10
        counts = counts.reindex(sorted(set(COUNTY_TO_AFF.values())), fill_value=0)

        if view3 == "Top 10":
            sel = counts.sort_values(ascending=False).head(10)
            colors3 = [LTBLUE] * len(sel)
            title3 = "Top 10 affiliates — most inquiries"
        else:
            sel = counts.sort_values(ascending=True).head(10).iloc[::-1]
            colors3 = [RED] * len(sel)
            title3 = "Bottom 10 affiliates — fewest inquiries · needs attention"

        aff_counts = sel.reset_index()
        aff_counts.columns = ['Affiliate', 'Count']
        fig_aff = go.Figure(go.Bar(
            x=aff_counts['Count'], y=aff_counts['Affiliate'], orientation='h',
            marker_color=colors3,
            text=aff_counts['Count'], textposition='outside', cliponaxis=False,
            textfont=dict(size=11, color=DKBLUE),
            hovertemplate="<b>%{y}</b><br>Inquiries: %{x}<extra></extra>"))
        style_fig(fig_aff, 380)
        fig_aff.update_layout(
            title=dict(text=title3, font=dict(color=DKBLUE, size=12)),
            bargap=0.3,
            yaxis=dict(autorange='reversed', gridcolor="rgba(0,0,0,0)",
                       tickmode='linear', tickfont=dict(size=11)),
            showlegend=False, margin=dict(l=10, r=55, t=35, b=10))
        st.plotly_chart(fig_aff, use_container_width=True)
        

    if st.checkbox("🔍 Full county breakdown — click an affiliate to see its counties",
                   key="p1_breakdown"):
        ct = (filtered[filtered['Affiliate'] != 'No County Selected']
              .groupby(['Affiliate', 'County']).size().reset_index(name='Inquiries'))
        aff_tot = ct.groupby('Affiliate')['Inquiries'].sum().sort_values(ascending=False)

        for aff, tot in aff_tot.items():
            sub = (ct[ct['Affiliate'] == aff][['County', 'Inquiries']]
                   .sort_values('Inquiries', ascending=False)
                   .reset_index(drop=True))
            sub.index += 1
            label = f"{aff}  —  {tot} inquiries  ·  {len(sub)} count{'y' if len(sub)==1 else 'ies'}"
            with st.expander(label):
                st.dataframe(sub.style.bar(subset=['Inquiries'], color=RED + "88"),
                             use_container_width=True,
                             height=min(35 * len(sub) + 40, 420))

    
# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — VOLUNTEER MAP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Page 2 — Volunteer Map":
    st.markdown(f"""<div class="casa-header">
        <h1>⚖️ CASA Georgia — New Volunteers by Affiliate</h1>
        <p>Volunteers sworn in by affiliate region</p>
    </div>""", unsafe_allow_html=True)

    # Reserve the KPI row here — it is FILLED further down, once the quarter
    # filter exists, but it DRAWS at this position on the page.
    kpi_slot = st.container()
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ── Quarter filter ────────────────────────────────────────────────────────
    st.markdown("<div style='font-size:12px;font-weight:700;color:#002855;margin-bottom:4px'>Filter by Quarter (select one or more):</div>", unsafe_allow_html=True)

    def _qkey(lbl):
        fy, q = lbl.split()
        return (int(fy[2:]), int(q[1:]))
    QTR_ORDER = sorted(VOL_QTR_LABELS, key=_qkey)

    col_all, col_qtrs = st.columns([1, 4])
    with col_all:
        select_all_qtrs = st.checkbox("All", value=True, key="p2_all")
    with col_qtrs:
        if select_all_qtrs:
            selected_qtrs = QTR_ORDER
            st.multiselect("", QTR_ORDER, default=QTR_ORDER, key="p2_multi",
                           disabled=True, label_visibility="collapsed")
        else:
            selected_qtrs = st.multiselect(
                "", QTR_ORDER, default=[QTR_ORDER[-1]] if QTR_ORDER else [],
                key="p2_multi2", label_visibility="collapsed")
            if not selected_qtrs:
                selected_qtrs = QTR_ORDER

    selected_idxs = [VOL_QTR_LABELS.index(q) for q in selected_qtrs if q in VOL_QTR_LABELS]

    def get_vol(aff):
        v = VOLUNTEER_DATA.get(aff, [])
        if not v:
            return 0
        return sum(v[i] for i in selected_idxs if i < len(v))

    # ── Fill the reserved KPI slot ────────────────────────────────────────────
    with kpi_slot:
        vol_now     = {aff: get_vol(aff) for aff in VOLUNTEER_DATA}
        total_vol   = sum(vol_now.values())
        top_aff_v   = max(vol_now, key=vol_now.get) if vol_now else "—"
        top_aff_vn  = vol_now.get(top_aff_v, 0)
        active_affs = sum(1 for v in vol_now.values() if v > 0)

        inq_same_period = len(df[df['FYLabel'].isin(selected_qtrs)])
        ratio = round(total_vol / inq_same_period * 100) if inq_same_period else 0
        qtr_note = ("All quarters" if len(selected_qtrs) == len(QTR_ORDER)
                    else f"{len(selected_qtrs)} quarter(s) selected")

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Sworn In</div><div class="kpi-value">{total_vol:,}</div><div class="kpi-sub">{qtr_note}</div></div>', unsafe_allow_html=True)
        with k2:
            st.markdown(f'<div class="kpi-card blue"><div class="kpi-label">Active Affiliates</div><div class="kpi-value">{active_affs}</div><div class="kpi-sub">With at least 1 volunteer</div></div>', unsafe_allow_html=True)
        with k3:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Top Affiliate</div><div class="kpi-value" style="font-size:18px;padding-top:5px">{top_aff_v}</div><div class="kpi-sub">{top_aff_vn} sworn in</div></div>', unsafe_allow_html=True)
        with k4:
            st.markdown(f'<div class="kpi-card blue"><div class="kpi-label">Sworn In per 100 Inquiries</div><div class="kpi-value">{ratio}</div><div class="kpi-sub">{total_vol:,} sworn in · {inq_same_period:,} inquiries, same quarters</div></div>', unsafe_allow_html=True)

    # ── Map + ranking ─────────────────────────────────────────────────────────
    st.markdown("<div class='sec-head'>🗺️ Volunteers Sworn In — by County (Filled Map)</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-body'>", unsafe_allow_html=True)
    st.markdown("""<div class='note-box'>
        💡 <strong>What this tells you:</strong> The map shows Georgia counties shaded by how many new volunteers
        were sworn in — <strong>darker red = more volunteers</strong>, light pink = fewer, white = none yet.
        Counties share the count of their affiliate, so all counties in one affiliate region will have the same shade.
        Use the quarter filter above to see which regions were most active in a specific time period.
    </div>""", unsafe_allow_html=True)

    county_rows = []
    for county, fips in GA_COUNTY_FIPS.items():
        aff = COUNTY_TO_AFF.get(county)
        v = get_vol(aff) if aff else 0
        county_rows.append({'County': county, 'FIPS': fips,
                            'Affiliate': aff or 'No County Selected', 'Count': v})
    vol_county_df = pd.DataFrame(county_rows)

    c2a, c2b = st.columns([3, 2])
    with c2a:
        max_v = max(vol_county_df['Count'].max(), 1)
        ga_geojson = load_ga_geojson()
        if ga_geojson:
            fig_vmap = px.choropleth(
                vol_county_df, geojson=ga_geojson,
                locations='FIPS', color='Count',
                hover_name='County',
                hover_data={'FIPS': False, 'Affiliate': True, 'Count': True},
                color_continuous_scale=[[0, LGRAY], [0.15, '#FFD0D0'], [0.4, '#FF8888'],
                                        [0.7, RED], [1.0, '#7A0818']],
                range_color=(0, max_v),
            )
            fig_vmap.update_geos(fitbounds="locations", visible=False, scope="usa")
            fig_vmap.update_layout(height=430, margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                coloraxis_colorbar=dict(title="Sworn In", thickness=12, len=0.6))
            fig_vmap.update_traces(marker_line_color='white', marker_line_width=0.6,
                hovertemplate="<b>%{hovertext}</b><br>Affiliate: %{customdata[0]}<br>Sworn In: %{customdata[1]}<extra></extra>")
            st.plotly_chart(fig_vmap, use_container_width=True)
        else:
            st.info("Map unavailable — could not load county boundaries. The ranked list on the right still shows all data.")

    with c2b:
        view = st.radio("Show", ["Top 10", "Bottom 10"], horizontal=True,
                        key="p2_rank_view", label_visibility="collapsed")

        allv = sorted([(aff, get_vol(aff)) for aff in VOLUNTEER_DATA], key=lambda x: -x[1])

        if view == "Top 10":
            rows = allv[:10]
            colors = [LTBLUE] * len(rows)
            title = "Top 10 affiliates — most sworn in"
        else:
            rows = sorted(allv, key=lambda x: x[1])[:10][::-1]
            colors = [RED] * len(rows)
            title = "Bottom 10 affiliates — fewest sworn in · needs attention"

        rdf = pd.DataFrame(rows, columns=['Affiliate', 'Sworn In'])
        fig_rank = go.Figure(go.Bar(
            x=rdf['Sworn In'], y=rdf['Affiliate'], orientation='h',
            marker_color=colors,
            text=rdf['Sworn In'], textposition='outside', cliponaxis=False,
            textfont=dict(size=11, color=DKBLUE),
            hovertemplate="<b>%{y}</b><br>Sworn in: %{x}<extra></extra>"))
        style_fig(fig_rank, 390)
        fig_rank.update_layout(
            title=dict(text=title, font=dict(color=DKBLUE, size=12)),
            bargap=0.3,
            yaxis=dict(autorange='reversed', gridcolor="rgba(0,0,0,0)",
                       tickmode='linear', tickfont=dict(size=11)),
            showlegend=False, margin=dict(l=10, r=55, t=35, b=10))
        st.plotly_chart(fig_rank, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Region breakdown table ────────────────────────────────────────────────
    st.markdown("<div class='sec-head'>📊 Volunteers by Region — Detailed Breakdown</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-body'>", unsafe_allow_html=True)
    rows = []
    for region, affs in REGIONS:
        for aff in affs:
            v = VOLUNTEER_DATA.get(aff, [0] * len(VOL_QTR_LABELS))
            row = {'Region': region, 'Affiliate': aff}
            for i, lbl in enumerate(VOL_QTR_LABELS):
                row[lbl] = v[i] if i < len(v) else 0
            row['Total'] = sum(v)
            rows.append(row)
    reg_df = pd.DataFrame(rows)
    st.dataframe(reg_df.style.bar(subset=['Total'], color=RED + "88"),
                 use_container_width=True, height=500)
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — QUARTERLY TRENDS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Page 3 — Quarterly Analysis":
    st.markdown(f"""<div class="casa-header">
        <h1>⚖️ CASA Georgia — Quarterly Trends</h1>
        <p>How inquiries and sworn-in volunteers are moving over time</p>
    </div>""", unsafe_allow_html=True)

    import re

    # ── Build one quarterly fact table both charts read from ──────────────────
    def q_months(fy, q):
        y, m = {1: (fy - 1, 7), 2: (fy - 1, 10), 3: (fy, 1), 4: (fy, 4)}[q]
        return [f"{y}-{m + k:02d}" for k in range(3)]

    def q_shift(fy, q, back):          # move back N quarters
        n = fy * 4 + (q - 1) - back
        return n // 4, n % 4 + 1

    avail_months = set(df['YearMonth'].unique())

    sworn_idx = {}
    for i, lbl in enumerate(VOL_QTR_LABELS):
        m = re.match(r'FY(\d{2}) Q(\d)', lbl)
        if m:
            sworn_idx[(2000 + int(m.group(1)), int(m.group(2)))] = i

    inq_q = set()
    for ym in avail_months:
        y, mo = int(ym[:4]), int(ym[5:7])
        fy = y + 1 if mo >= 7 else y
        q = 1 if mo in (7, 8, 9) else 2 if mo in (10, 11, 12) else 3 if mo in (1, 2, 3) else 4
        inq_q.add((fy, q))

    rows = []
    for fy, q in sorted(inq_q | set(sworn_idx)):
        lbl = f"FY{str(fy)[2:]} Q{q}"
        months = q_months(fy, q)
        missing = [m for m in months if m not in avail_months]
        i = sworn_idx.get((fy, q))
        sworn = (sum(v[i] for v in VOLUNTEER_DATA.values() if i < len(v))
                 if i is not None else None)
        rows.append({
            'fy': fy, 'q': q, 'label': lbl,
            'period': f"{pd.Period(months[0],'M').strftime('%b')}–{pd.Period(months[-1],'M').strftime('%b %y')}",
            'inq': int((df['FYLabel'] == lbl).sum()),
            'sworn': sworn,
            'complete': len(missing) == 0,
            'missing': ", ".join(pd.Period(m, 'M').strftime('%b') for m in missing),
        })
    qdf = pd.DataFrame(rows)
    qlook = {(r.fy, r.q): r for r in qdf.itertuples()}

    # ── KPIs — year-over-year, not quarter-over-quarter ───────────────────────
    usable = qdf[(qdf['sworn'].notna()) & (qdf['complete'])]
    if usable.empty:
        st.warning("Not enough complete quarters to compute trends yet.")
        st.stop()
    last = usable.iloc[-1]
    py = qlook.get((int(last['fy']) - 1, int(last['q'])))

    def pct(now, then):
        if then is None or then == 0:
            return None
        return round((now - then) / then * 100)

    inq_yoy   = pct(last['inq'],   py.inq   if py else None)
    sworn_yoy = pct(last['sworn'], py.sworn if py and py.sworn is not None else None)

    def arrow(v):
        if v is None:
            return "no prior year"
        return f"{'▲' if v > 0 else '▼' if v < 0 else '■'} {abs(v)}% vs {last['label'][:4].replace('FY','FY')[:2]}{int(last['fy'])-1-2000} {last['label'][-2:]}"

    # trailing 4 quarters vs the 4 before that
    t4  = usable.tail(4)
    p4  = usable.iloc[-8:-4] if len(usable) >= 8 else pd.DataFrame()
    t4_sworn = int(t4['sworn'].sum())
    p4_sworn = int(p4['sworn'].sum()) if not p4.empty else None
    t4_yoy   = pct(t4_sworn, p4_sworn)

    # yield: sworn this quarter vs inquiries 2 quarters earlier
    LAG = 2
    def yield_for(fy, q):
        src = qlook.get(q_shift(fy, q, LAG))
        tgt = qlook.get((fy, q))
        if not src or not tgt or tgt.sworn is None or not src.inq or not src.complete:
            return None
        return round(tgt.sworn / src.inq * 100)

    y_now = yield_for(int(last['fy']), int(last['q']))

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-card blue"><div class="kpi-label">Inquiries — {last["label"]}</div><div class="kpi-value">{last["inq"]:,}</div><div class="kpi-sub">{arrow(inq_yoy)}</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card blue"><div class="kpi-label">Sworn In — {last["label"]}</div><div class="kpi-value">{int(last["sworn"]):,}</div><div class="kpi-sub">{arrow(sworn_yoy)}</div></div>', unsafe_allow_html=True)
    with k3:
        sub = f"vs {p4_sworn:,} prior 4 qtrs" if p4_sworn else "not enough history"
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Sworn In — Last 4 Quarters</div><div class="kpi-value">{t4_sworn:,}</div><div class="kpi-sub">{sub}{"" if t4_yoy is None else f" · {t4_yoy:+d}%"}</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Yield per 100 Inquiries</div><div class="kpi-value">{y_now if y_now is not None else "—"}</div><div class="kpi-sub">sworn in {last["label"]} vs inquiries 2 qtrs earlier</div></div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ── 1. The funnel over time ───────────────────────────────────────────────
    st.markdown("<div class='sec-head'>📊 1. Inquiries vs. Volunteers Sworn In — every quarter</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-body'>", unsafe_allow_html=True)
    st.markdown("""<div class='note-box'>
        💡 <strong>What this tells you:</strong> The pale bar is everyone who inquired that quarter; the solid navy bar
        sitting inside it is volunteers sworn in. The exposed pale portion is the gap — interest that has not (yet)
        become a sworn volunteer. Watch whether the navy is filling more of the pale bar over time.
        Bars are drawn for every quarter in your data, so pre-growth-plan quarters are visible for contrast.
    </div>""", unsafe_allow_html=True)

    show = qdf[(qdf['inq'] > 0) | (qdf['sworn'].notna())].copy()
    xlab = [f"{r.label}<br>{r.period}" for r in show.itertuples()]

    fig_q = go.Figure()
    fig_q.add_trace(go.Bar(
        name='Inquiries', x=xlab, y=show['inq'],
        marker_color="#C7D2E0", marker_line_width=0, width=0.62,
        text=show['inq'], textposition='outside', cliponaxis=False,
        textfont=dict(size=10, color="#5A6B80"),
        hovertemplate="<b>%{x}</b><br>Inquiries: %{y}<extra></extra>"))
    fig_q.add_trace(go.Bar(
        name='Sworn In', x=xlab, y=show['sworn'].fillna(0),
        marker_color=DKBLUE, marker_line_width=0, width=0.30,
        text=[("" if pd.isna(v) else int(v)) for v in show['sworn']],
        textposition='inside', insidetextanchor='middle',
        textfont=dict(size=10, color=WHITE),
        hovertemplate="<b>%{x}</b><br>Sworn In: %{y}<extra></extra>"))
    style_fig(fig_q, 420)
    fig_q.update_layout(
        barmode='overlay', bargap=0.28,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(type='category', gridcolor="#E8ECF0", linecolor=MIDGRAY,
                   tickfont=dict(size=9)))
    st.plotly_chart(fig_q, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── 2. Same quarter, year over year ───────────────────────────────────────
    st.markdown("<div class='sec-head'>📈 2. Same Quarter, Year Over Year</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-body'>", unsafe_allow_html=True)
    st.markdown("""<div class='note-box'>
        💡 <strong>Why this chart matters most:</strong> Volunteer recruitment is seasonal, so comparing Q2 to Q1
        mostly measures the calendar. Comparing <strong>Q1 to last year's Q1</strong> is a fair comparison.
        Each cluster is one fiscal quarter; darker bars are more recent years. Rising bars left-to-right within
        a cluster means real growth, not a seasonal bump.
    </div>""", unsafe_allow_html=True)

    metric = st.radio("Metric", ["Sworn In", "Inquiries"], horizontal=True,
                      key="p3_yoy_metric", label_visibility="collapsed")
    col = 'sworn' if metric == "Sworn In" else 'inq'
    yoy = qdf[qdf[col].notna()]
    fys = sorted(yoy['fy'].unique())
    shades = ["#BBC9DB", "#7B95B5", "#3E6591", DKBLUE][-len(fys):] if len(fys) <= 4 \
             else ["#D3DCE7", "#BBC9DB", "#93AAC7", "#6C8CB0", "#3E6591", DKBLUE][-len(fys):]

    fig_yoy = go.Figure()
    for shade, fy in zip(shades, fys):
        sub = yoy[yoy['fy'] == fy].set_index('q')[col].reindex([1, 2, 3, 4])
        fig_yoy.add_trace(go.Bar(
            name=f"FY{fy}", x=["Q1<br>Jul–Sep", "Q2<br>Oct–Dec", "Q3<br>Jan–Mar", "Q4<br>Apr–Jun"],
            y=sub.values, marker_color=shade, marker_line_width=0,
            text=[("" if pd.isna(v) else int(v)) for v in sub.values],
            textposition='outside', cliponaxis=False, textfont=dict(size=10, color=DKBLUE),
            hovertemplate="<b>FY" + str(fy) + " %{x}</b><br>" + metric + ": %{y}<extra></extra>"))
    style_fig(fig_yoy, 380)
    fig_yoy.update_layout(
        barmode='group', bargap=0.25, bargroupgap=0.06,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(type='category', gridcolor="#E8ECF0", linecolor=MIDGRAY))
    st.plotly_chart(fig_yoy, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── 3. Yield trend ────────────────────────────────────────────────────────
    st.markdown("<div class='sec-head'>🎯 3. Yield — Volunteers Sworn In per 100 Inquiries</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-body'>", unsafe_allow_html=True)
    st.markdown(f"""<div class='note-box'>
        💡 <strong>What this tells you:</strong> Each point is volunteers sworn in that quarter divided by inquiries
        <strong>{LAG} quarters earlier</strong> — roughly the same people, allowing for application, training and
        swearing-in. A rising line means the pipeline is converting interest better.
        <strong>This is not a true conversion rate:</strong> many volunteers are recruited by affiliates directly and
        never appear in the inquiry form, so the figure can exceed 100. Read the direction, not the level.
    </div>""", unsafe_allow_html=True)

    yv = [(r.label, yield_for(r.fy, r.q)) for r in qdf.itertuples()]
    yv = [(l, v) for l, v in yv if v is not None]
    if len(yv) >= 2:
        fig_y = go.Figure(go.Scatter(
            x=[l for l, _ in yv], y=[v for _, v in yv],
            mode='lines+markers+text', line=dict(color=DKBLUE, width=2.5),
            marker=dict(color=DKBLUE, size=8),
            text=[v for _, v in yv], textposition='top center',
            textfont=dict(size=10, color=DKBLUE),
            hovertemplate="<b>%{x}</b><br>%{y} sworn in per 100 inquiries<extra></extra>"))
        avg = round(sum(v for _, v in yv) / len(yv))
        fig_y.add_hline(y=avg, line=dict(color=MIDGRAY, width=1, dash='dash'),
                        annotation_text=f"average {avg}", annotation_position="right",
                        annotation_font=dict(size=10, color="#667085"))
        style_fig(fig_y, 320)
        fig_y.update_layout(xaxis=dict(type='category', gridcolor="#E8ECF0"),
                            yaxis=dict(gridcolor="#E8ECF0", rangemode='tozero'),
                            showlegend=False)
        st.plotly_chart(fig_y, use_container_width=True)
    else:
        st.info(f"Need at least {LAG + 2} consecutive quarters of both datasets to plot a yield trend.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── 4. The numbers ────────────────────────────────────────────────────────
    st.markdown("<div class='sec-head'>📋 4. Quarter-by-Quarter Detail</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-body'>", unsafe_allow_html=True)
    tbl = []
    for r in qdf.itertuples():
        py = qlook.get((r.fy - 1, r.q))
        iy = pct(r.inq, py.inq if py else None)
        sy = pct(r.sworn, py.sworn if py and py.sworn is not None and r.sworn is not None else None)
        tbl.append({
            'Quarter':   r.label,
            'Period':    r.period,
            'Inquiries': f"{r.inq}" + ("" if r.complete else f" ({r.missing} missing)"),
            'Inq. YoY':  "—" if iy is None else f"{iy:+d}%",
            'Sworn In':  "—" if r.sworn is None else f"{int(r.sworn)}",
            'Sworn YoY': "—" if sy is None else f"{sy:+d}%",
            'Yield /100': "—" if yield_for(r.fy, r.q) is None else f"{yield_for(r.fy, r.q)}",
        })
    st.dataframe(pd.DataFrame(tbl), use_container_width=True, hide_index=True, height=420)
    st.markdown("</div>", unsafe_allow_html=True)
