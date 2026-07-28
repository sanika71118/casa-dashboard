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
COUNTY_TO_AFF = {
    'Bibb':'Ocmulgee','Monroe':'Ocmulgee','Jones':'Ocmulgee','Twiggs':'Ocmulgee','Wilkinson':'Ocmulgee',
    'Baldwin':'Central Ga','Putnam':'Central Ga','Jasper':'Central Ga','Johnson':'Central Ga',
    'Butts':'Towaliga','Lamar':'Towaliga','Upson':'Towaliga','Pike':'Towaliga',
    'Houston':'Houston','Peach':'Houston','Crawford':'Houston','Taylor':'Houston',
    'Spalding':'TLC','Schley':'TLC',
    'Troup':'Troup','Meriwether':'Troup','Heard':'Troup',
    'Coweta':'Coweta','Carroll':'Carroll',
    'Fulton':'Atlanta','Henry':'Henry','Fayette':'Henry','Clayton':'Clayton',
    'DeKalb':'DeKalb','Gwinnett':'Gwinnett','Cobb':'Cobb','Douglas':'Cobb',
    'Rockdale':'Rockdale','Forsyth':'Forsyth',
    'Newton':'Alcovy','Walton':'Alcovy','Barrow':'Alcovy','Morgan':'Alcovy',
    'Paulding':'Paulding','Cherokee':'Cherokee','Pickens':'Cherokee','Bartow':'Cherokee',
    'Hall':'Hall-Dawson','Dawson':'Hall-Dawson','Lumpkin':'Hall-Dawson',
    'Habersham':'Mountain','Stephens':'Mountain','Rabun':'Mountain','Towns':'Mountain',
    'White':'Mountain','Union':'Mountain','Gilmer':'Mountain',
    'Banks':'NE CASA','Franklin':'NE CASA','Hart':'NE CASA','Madison':'NE CASA',
    'Elbert':'NE CASA','Jackson':'NE CASA',
    'Clarke':'Athens','Oconee':'Athens','Oglethorpe':'Athens','Greene':'Athens',
    'Wilkes':'Athens','Lincoln':'Athens','Columbia':'Athens',
    'Haralson':'Polk & Haralson','Polk':'Polk & Haralson',
    'Floyd':'Floyd','Gordon':'NW GA','Chattooga':'NW GA',
    'Murray':'Murray/Whitfield','Whitfield':'Murray/Whitfield',
    'Walker':'Lookout Mountain','Catoosa':'Lookout Mountain','Dade':'Lookout Mountain',
    'Liberty':'Atlantic Area','Long':'Atlantic Area','McIntosh':'Atlantic Area',
    'Glynn':'Glynn','Camden':'Glynn','Brantley':'Glynn',
    'Richmond':'Augusta','Burke':'Augusta','McDuffie':'Augusta','Warren':'Augusta','Screven':'Augusta',
    'Bulloch':'Ogeechee','Candler':'Ogeechee','Evans':'Ogeechee',
    'Tattnall':'Ogeechee','Tatnall':'Ogeechee','Emanuel':'Ogeechee','Jenkins':'Ogeechee',
    'Chatham':'Savannah','Bryan':'Savannah','Effingham':'Savannah',
    'Appling':'SE CASA','Wayne':'SE CASA','Pierce':'SE CASA','Jeff Davis':'SE CASA',
    'Coffee':'SE CASA','Bacon':'SE CASA','Toombs':'SE CASA','Montgomery':'SE CASA',
    'Lowndes':'Lowndes & Echols','Echols':'Lowndes & Echols','Lanier':'Lowndes & Echols','Brooks':'Lowndes & Echols',
    'Thomas':'CASA SW','Decatur':'CASA SW','Grady':'CASA SW','Mitchell':'CASA SW','Seminole':'CASA SW',
    'Colquitt':'SOWEGA','Worth':'SOWEGA','Tift':'SOWEGA','Turner':'SOWEGA',
    'Ben  Hill':'SOWEGA','Irwin':'SOWEGA','Berrien':'SOWEGA','Cook':'SOWEGA',
    'Muscogee':'Chattahoochee','Harris':'Chattahoochee','Chattahoochee':'Chattahoochee',
    'Marion':'Chattahoochee','Webster':'Chattahoochee','Stewart':'Chattahoochee',
    'Dooly':'CASA Kids','Crisp':'CASA Kids','Wilcox':'CASA Kids','Pulaski':'CASA Kids',
    'Bleckley':'CASA Kids','Dodge':'CASA Kids','Laurens':'CASA Kids',
    'Telfair':'CASA Kids','Wheeler':'CASA Kids','Treutlen':'CASA Kids',
    'Atkinson':'Alapaha',
    'Ware':'Coastal Plain','Charlton':'Coastal Plain','Clinch':'Coastal Plain',
    'Dougherty':'Dougherty','Lee':'Dougherty','Terrell':'Dougherty','Calhoun':'Dougherty',
    'Baker':'Dougherty','Miller':'Dougherty','Early':'Dougherty','Clay':'Dougherty',
    'Randolph':'Dougherty','Quitman':'Dougherty',
}

REGIONS = [
    ('Central', ['Advo-Kids','Ocmulgee','Central Ga','Towaliga','Houston','TLC','Troup','Coweta']),
    ('Metro',   ['Atlanta','Henry',"Children's Voice",'Clayton','DeKalb','Gwinnett','Cobb','Rockdale','Forsyth','Alcovy']),
    ('NE',      ['Piedmont','Athens','Enotah','Hall-Dawson','NE CASA','Mountain']),
    ('NW',      ['NW GA','Cherokee','Paulding','Appalachian','Floyd','Polk & Haralson','Murray/Whitfield','Lookout Mountain']),
    ('Coastal', ['Atlantic Area','Glynn','Augusta','Ogeechee','Savannah','SE CASA']),
    ('South',   ['Lowndes & Echols','CASA SW','SOWEGA','Chattahoochee','CASA Kids','Alapaha','Coastal Plain','Dougherty']),
]

COUNTY_COORDS = {
    'Fulton':(33.749,-84.388),'DeKalb':(33.775,-84.232),'Cobb':(33.938,-84.578),
    'Gwinnett':(33.962,-84.002),'Clayton':(33.557,-84.359),'Henry':(33.448,-84.152),
    'Fayette':(33.412,-84.470),'Douglas':(33.698,-84.755),'Newton':(33.553,-83.847),
    'Rockdale':(33.657,-84.021),'Coweta':(33.357,-84.760),'Carroll':(33.581,-85.078),
    'Paulding':(33.927,-84.864),'Forsyth':(34.226,-84.133),'Cherokee':(34.239,-84.479),
    'Barrow':(33.998,-83.720),'Jackson':(34.138,-83.562),'Hall':(34.311,-83.818),
    'Clarke':(33.961,-83.377),'Oconee':(33.842,-83.433),'Baldwin':(33.073,-83.250),
    'Bibb':(32.838,-83.694),'Houston':(32.465,-83.652),'Chatham':(32.028,-81.107),
    'Muscogee':(32.460,-84.988),'Richmond':(33.374,-82.076),'Columbia':(33.537,-82.196),
    'Lowndes':(30.832,-83.279),'Dougherty':(31.535,-84.169),'Glynn':(31.221,-81.517),
    'Bulloch':(32.409,-81.775),'Liberty':(31.837,-81.455),'Bryan':(31.993,-81.433),
    'Effingham':(32.375,-81.336),'Bartow':(34.238,-84.839),'Floyd':(34.262,-85.214),
    'Walker':(34.743,-85.300),'Catoosa':(34.903,-85.120),'Whitfield':(34.797,-84.977),
    'Murray':(34.789,-84.745),'Dawson':(34.451,-84.165),'Gilmer':(34.691,-84.468),
    'Pickens':(34.469,-84.471),'Troup':(33.037,-85.030),'Meriwether':(32.952,-84.681),
    'Harris':(32.734,-84.904),'Spalding':(33.268,-84.289),'Monroe':(33.013,-83.918),
    'Morgan':(33.591,-83.494),'Walton':(33.782,-83.730),'Greene':(33.575,-83.159),
    'Oglethorpe':(33.868,-83.089),'Madison':(34.109,-83.211),'Elbert':(34.115,-82.849),
    'Hart':(34.353,-82.969),'Franklin':(34.377,-83.234),'Habersham':(34.629,-83.532),
    'Stephens':(34.566,-83.294),'White':(34.647,-83.734),'Lumpkin':(34.568,-83.973),
    'Fannin':(34.870,-84.321),'Towns':(34.922,-83.729),'Rabun':(34.891,-83.401),
    'Camden':(30.893,-81.616),'Ware':(31.063,-82.415),'Coffee':(31.550,-82.845),
    'Appling':(31.748,-82.309),'Pierce':(31.358,-82.207),'Wayne':(31.554,-81.913),
    'Brantley':(31.196,-81.983),'Charlton':(30.788,-82.138),'Clinch':(30.913,-82.700),
    'Atkinson':(31.295,-82.882),'Berrien':(31.272,-83.233),'Cook':(31.151,-83.428),
    'Tift':(31.462,-83.523),'Turner':(31.716,-83.628),'Wilcox':(31.968,-83.428),
    'Crisp':(31.897,-83.776),'Dooly':(32.169,-83.777),'Pulaski':(32.236,-83.470),
    'Bleckley':(32.423,-83.322),'Dodge':(32.171,-83.184),'Laurens':(32.461,-82.913),
    'Toombs':(32.120,-82.334),'Emanuel':(32.581,-82.298),'Candler':(32.404,-82.076),
    'Evans':(32.169,-81.883),'Tattnall':(32.045,-82.061),'Tatnall':(32.045,-82.061),
    'Treutlen':(32.403,-82.569),'Montgomery':(32.172,-82.531),'Jeff Davis':(31.806,-82.634),
    'Telfair':(31.900,-82.941),'Burke':(33.073,-81.979),'Screven':(32.743,-81.605),
    'McDuffie':(33.475,-82.477),'Lincoln':(33.789,-82.467),
    'Lee':(31.778,-84.141),'Decatur':(30.868,-84.578),'Grady':(30.874,-84.229),
    'Thomas':(30.855,-83.929),'Brooks':(30.835,-83.569),'Lanier':(31.036,-83.062),
    'Echols':(30.707,-82.900),'Colquitt':(31.177,-83.760),'Mitchell':(31.219,-84.187),
    'Calhoun':(31.535,-84.618),'Baker':(31.328,-84.449),'Miller':(31.167,-84.733),
    'Early':(31.327,-84.902),'Clay':(31.628,-85.001),'Randolph':(31.777,-84.751),
    'Quitman':(31.867,-85.019),'Webster':(32.044,-84.560),'Stewart':(32.077,-84.834),
    'Schley':(32.261,-84.310),'Macon':(32.355,-84.041),'Marion':(32.362,-84.527),
    'Talbot':(32.697,-84.535),'Chattahoochee':(32.354,-84.787),
    'Harris':(32.734,-84.904),'Haralson':(33.796,-85.212),'Polk':(34.002,-85.173),
    'Gordon':(34.503,-84.877),'Chattooga':(34.477,-85.354),'Dade':(34.858,-85.489),
    'Seminole':(30.941,-84.874),'Worth':(31.566,-83.853),
}

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
    all_files = glob.glob(os.path.join(data_dir, "*.xlsx"))
    all_files = [f for f in all_files if "volunteers" not in f.lower()]
    all_dfs = []
    for path in all_files:
        try:
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
    combined['Source']         = combined['Source'].fillna('Unknown')
    combined['Affiliate']      = combined['County'].map(COUNTY_TO_AFF).fillna('Unassigned')
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
    select_all = st.checkbox("All Months", value=True)
    if select_all:
        selected_months = month_options
    else:
        selected_months = st.multiselect("Choose months:", options=month_options,
                                          format_func=lambda x: month_labels[x],
                                          default=month_options[-3:])
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
    top_src    = filtered['Source'].value_counts().idxmax() if not filtered.empty else "—"
    top_src_n  = filtered['Source'].value_counts().iloc[0] if not filtered.empty else 0
    top_county = filtered['County'].value_counts().idxmax() if not filtered.empty else "—"
    top_county_n = filtered['County'].value_counts().iloc[0] if not filtered.empty else 0
    top_aff    = filtered['Affiliate'].value_counts().idxmax() if not filtered.empty else "—"
    top_aff_n  = filtered['Affiliate'].value_counts().iloc[0] if not filtered.empty else 0

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
        </div>""", unsafe_allow_html=True)
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=monthly['MonthLabel'], y=monthly['Count'],
        marker_color=RED, marker_line_color=DKBLUE, marker_line_width=1,
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
    src_counts.columns = ['Source','Count']
    top_src_name = src_counts.iloc[0]['Source'] if not src_counts.empty else "—"
    top_src_pct  = round(src_counts.iloc[0]['Count'] / src_counts['Count'].sum() * 100) if not src_counts.empty else 0
    second_src   = src_counts.iloc[1]['Source'] if len(src_counts) > 1 else "—"
    st.markdown(f"""<div class='note-box'>
        💡 <strong>What this tells you:</strong> Most people who inquire about volunteering hear about CASA through
        <strong>{top_src_name}</strong> ({top_src_pct}% of all inquiries). <strong>{second_src}</strong> is the second
        biggest channel. This helps CASA focus marketing — invest more in what is already driving the most interest.
    </div>""", unsafe_allow_html=True)
    c2a,c2b = st.columns(2)
    with c2a:
        top8 = src_counts.head(8).copy()
        other_count = src_counts.iloc[8:]['Count'].sum()
        if other_count > 0:
            top8 = pd.concat([top8, pd.DataFrame([{'Source':'Other sources','Count':other_count}])], ignore_index=True)
        fig2a = px.pie(top8, values='Count', names='Source',
                       color_discrete_sequence=CHART_COLORS, hole=0.45)
        fig2a.update_traces(
            textposition='inside', textinfo='percent',
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
            insidetextorientation='radial')
        fig2a.update_layout(
            height=380, paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10,r=10,t=30,b=10),
            legend=dict(orientation="v",x=1.01,y=0.5,xanchor="left",
                        font=dict(size=10),bgcolor="rgba(0,0,0,0)"),
            showlegend=True,
            font=dict(family="Arial,sans-serif",color=DKBLUE))
        st.plotly_chart(fig2a, use_container_width=True)
    with c2b:
        fig2b = go.Figure(go.Bar(x=src_counts['Count'], y=src_counts['Source'], orientation='h',
            marker_color=[RED if i==0 else DKBLUE if i==1 else LTBLUE for i in range(len(src_counts))],
            text=src_counts['Count'], textposition='outside',
            hovertemplate="<b>%{y}</b><br>Count: %{x}<extra></extra>"))
        style_fig(fig2b, 420)
        fig2b.update_layout(
            yaxis=dict(autorange='reversed',gridcolor="rgba(0,0,0,0)",tickfont=dict(size=10)),
            xaxis=dict(gridcolor="#E8ECF0"),
            showlegend=False, margin=dict(l=20,r=60,t=20,b=20))
        st.plotly_chart(fig2b, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Chart 3: County map
    st.markdown("<div class='sec-head'>🗺️ 3. Inquiries by County & Affiliate</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-body'>", unsafe_allow_html=True)
    county_counts = filtered['County'].value_counts().reset_index()
    county_counts.columns = ['County','Count']
    county_counts['Affiliate'] = county_counts['County'].map(COUNTY_TO_AFF).fillna('Other')
    # Remove unassigned/unknown entries from map display
    county_counts = county_counts[~county_counts['Affiliate'].isin(['Other','Unassigned'])]
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
        aff_counts = filtered['Affiliate'].value_counts().head(15).reset_index()
        aff_counts.columns = ['Affiliate','Count']
        fig_aff = go.Figure(go.Bar(x=aff_counts['Count'], y=aff_counts['Affiliate'], orientation='h',
            marker_color=RED, text=aff_counts['Count'], textposition='outside',
            hovertemplate="<b>%{y}</b><br>Inquiries: %{x}<extra></extra>"))
        style_fig(fig_aff, 420)
        fig_aff.update_layout(title=dict(text="Top Affiliates",font=dict(color=DKBLUE,size=12)),
            yaxis=dict(autorange='reversed',gridcolor="rgba(0,0,0,0)",tickfont=dict(size=10)),
            showlegend=False, margin=dict(l=10,r=30,t=40,b=10))
        st.plotly_chart(fig_aff, use_container_width=True)

    with st.expander("🔍 Full County Breakdown Table"):
        ct = filtered.groupby(['County','Affiliate']).size().reset_index(name='Inquiries').sort_values('Inquiries',ascending=False).reset_index(drop=True)
        ct.index += 1
        st.dataframe(ct.style.bar(subset=['Inquiries'],color=RED+"88"), use_container_width=True, height=300)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — VOLUNTEER MAP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Page 2 — Volunteer Map":

    st.markdown(f"""<div class="casa-header">
        <h1>⚖️ CASA Georgia — New Volunteers by Affiliate</h1>
        <p>Volunteers sworn in by affiliate region &nbsp;|&nbsp; FY2026 Q1–Q3</p>
    </div>""", unsafe_allow_html=True)

    # KPIs
    total_vol = sum(sum(v) for v in VOLUNTEER_DATA.values())
    top_aff_v = max(VOLUNTEER_DATA, key=lambda k: sum(VOLUNTEER_DATA[k]))
    top_aff_vn = sum(VOLUNTEER_DATA[top_aff_v])
    active_affs = sum(1 for v in VOLUNTEER_DATA.values() if sum(v) > 0)

    k1,k2,k3,k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Sworn In</div><div class="kpi-value">{total_vol:,}</div><div class="kpi-sub">FY2026 Q1–Q3</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card blue"><div class="kpi-label">Active Affiliates</div><div class="kpi-value">{active_affs}</div><div class="kpi-sub">With at least 1 volunteer</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Top Affiliate</div><div class="kpi-value" style="font-size:18px;padding-top:5px">{top_aff_v}</div><div class="kpi-sub">{top_aff_vn} sworn in</div></div>', unsafe_allow_html=True)
    with k4:
        total_inq = len(filtered)
        conv = round(total_vol / total_inq * 100) if total_inq > 0 else 0
        st.markdown(f'<div class="kpi-card blue"><div class="kpi-label">Overall Conversion</div><div class="kpi-value">{conv}%</div><div class="kpi-sub">Sworn in vs inquiries</div></div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    st.markdown("<div style='font-size:12px;font-weight:700;color:#002855;margin-bottom:4px'>Filter by Quarter (select one or more):</div>", unsafe_allow_html=True)
    col_all, col_qtrs = st.columns([1,4])
    with col_all:
        select_all_qtrs = st.checkbox("All", value=True, key="p2_all")
    with col_qtrs:
        if select_all_qtrs:
            selected_qtrs = VOL_QTR_LABELS
            st.multiselect("", VOL_QTR_LABELS, default=VOL_QTR_LABELS, key="p2_multi", disabled=True, label_visibility="collapsed")
        else:
            selected_qtrs = st.multiselect("", VOL_QTR_LABELS, default=[VOL_QTR_LABELS[-1]] if VOL_QTR_LABELS else [], key="p2_multi2", label_visibility="collapsed")
            if not selected_qtrs:
                selected_qtrs = VOL_QTR_LABELS

    selected_idxs = [VOL_QTR_LABELS.index(q) for q in selected_qtrs if q in VOL_QTR_LABELS]

    def get_vol(aff):
        v = VOLUNTEER_DATA.get(aff, [])
        if not v:
            return 0
        return sum(v[i] for i in selected_idxs if i < len(v))

    st.markdown("<div class='sec-head'>🗺️ Volunteers Sworn In — by County (Filled Map)</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-body'>", unsafe_allow_html=True)
    st.markdown(f"""<div class='note-box'>
        💡 <strong>What this tells you:</strong> The map shows Georgia counties shaded by how many new volunteers
        were sworn in — <strong>darker red = more volunteers</strong>, light pink = fewer, white = none yet.
        Counties share the count of their affiliate, so all counties in one affiliate region will have the same shade.
        Use the quarter filter above to see which regions were most active in a specific time period.
        This helps leadership quickly spot which parts of Georgia are growing their volunteer base.
    </div>""", unsafe_allow_html=True)

    GA_COUNTY_FIPS = {
        'Appling':'13001','Atkinson':'13003','Bacon':'13005','Baker':'13007','Baldwin':'13009',
        'Banks':'13011','Barrow':'13013','Bartow':'13015','Ben Hill':'13017','Berrien':'13019',
        'Bibb':'13021','Bleckley':'13023','Brantley':'13025','Brooks':'13027','Bryan':'13029',
        'Bulloch':'13031','Burke':'13033','Butts':'13035','Calhoun':'13037','Camden':'13039',
        'Candler':'13043','Carroll':'13045','Catoosa':'13047','Charlton':'13049','Chatham':'13051',
        'Chattahoochee':'13053','Chattooga':'13055','Cherokee':'13057','Clarke':'13059','Clay':'13061',
        'Clayton':'13063','Clinch':'13065','Cobb':'13067','Coffee':'13069','Colquitt':'13071',
        'Columbia':'13073','Cook':'13075','Coweta':'13077','Crawford':'13079','Crisp':'13081',
        'Dade':'13083','Dawson':'13085','Decatur':'13087','DeKalb':'13089','Dodge':'13091',
        'Dooly':'13093','Dougherty':'13095','Douglas':'13097','Early':'13099','Echols':'13101',
        'Effingham':'13103','Elbert':'13105','Emanuel':'13107','Evans':'13109','Fannin':'13111',
        'Fayette':'13113','Floyd':'13115','Forsyth':'13117','Franklin':'13119','Fulton':'13121',
        'Gilmer':'13123','Glascock':'13125','Glynn':'13127','Gordon':'13129','Grady':'13131',
        'Greene':'13133','Gwinnett':'13135','Habersham':'13137','Hall':'13139','Hancock':'13141',
        'Haralson':'13143','Harris':'13145','Hart':'13147','Heard':'13149','Henry':'13151',
        'Houston':'13153','Irwin':'13155','Jackson':'13157','Jasper':'13159','Jeff Davis':'13161',
        'Jefferson':'13163','Jenkins':'13165','Johnson':'13167','Jones':'13169','Lamar':'13171',
        'Lanier':'13173','Laurens':'13175','Lee':'13177','Liberty':'13179','Lincoln':'13181',
        'Long':'13183','Lowndes':'13185','Lumpkin':'13187','Macon':'13193','Madison':'13195',
        'Marion':'13197','McDuffie':'13189','McIntosh':'13191','Meriwether':'13199','Miller':'13201',
        'Mitchell':'13205','Monroe':'13207','Montgomery':'13209','Morgan':'13211','Murray':'13213',
        'Muscogee':'13215','Newton':'13217','Oconee':'13219','Oglethorpe':'13221','Paulding':'13223',
        'Peach':'13225','Pickens':'13227','Pierce':'13229','Pike':'13231','Polk':'13233',
        'Pulaski':'13235','Putnam':'13237','Quitman':'13239','Rabun':'13241','Randolph':'13243',
        'Richmond':'13245','Rockdale':'13247','Schley':'13249','Screven':'13251','Seminole':'13253',
        'Spalding':'13255','Stephens':'13257','Stewart':'13259','Sumter':'13261','Talbot':'13263',
        'Taliaferro':'13265','Tattnall':'13267','Taylor':'13269','Telfair':'13271','Terrell':'13273',
        'Thomas':'13275','Tift':'13277','Toombs':'13279','Towns':'13281','Treutlen':'13283',
        'Troup':'13285','Turner':'13287','Twiggs':'13289','Union':'13291','Upson':'13293',
        'Walker':'13295','Walton':'13297','Ware':'13299','Warren':'13301','Washington':'13303',
        'Wayne':'13305','Webster':'13307','Wheeler':'13309','White':'13311','Whitfield':'13313',
        'Wilcox':'13315','Wilkes':'13317','Wilkinson':'13319','Worth':'13321',
    }

    county_rows = []
    for county, fips in GA_COUNTY_FIPS.items():
        aff = COUNTY_TO_AFF.get(county)
        v = get_vol(aff) if aff else 0
        county_rows.append({'County':county, 'FIPS':fips, 'Affiliate':aff or 'Unassigned', 'Count':v})
    vol_county_df = pd.DataFrame(county_rows)

    c2a, c2b = st.columns([3,2])
    with c2a:
        max_v = max(vol_county_df['Count'].max(), 1)
        ga_geojson = load_ga_geojson()
        if ga_geojson:
            fig_vmap = px.choropleth(
                vol_county_df, geojson=ga_geojson,
                locations='FIPS', color='Count',
                hover_name='County',
                hover_data={'FIPS':False,'Affiliate':True,'Count':True},
                color_continuous_scale=[[0,LGRAY],[0.15,'#FFD0D0'],[0.4,'#FF8888'],[0.7,RED],[1.0,'#7A0818']],
                range_color=(0, max_v),
            )
            fig_vmap.update_geos(fitbounds="locations", visible=False, scope="usa")
            fig_vmap.update_layout(height=430, margin=dict(l=0,r=0,t=0,b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                coloraxis_colorbar=dict(title="Sworn In", thickness=12, len=0.6))
            fig_vmap.update_traces(marker_line_color='white', marker_line_width=0.6,
                hovertemplate="<b>%{hovertext}</b><br>Affiliate: %{customdata[0]}<br>Sworn In: %{customdata[1]}<extra></extra>")
            st.plotly_chart(fig_vmap, use_container_width=True)
        else:
            st.info("Map unavailable — could not load county boundaries. The ranked list on the right still shows all data.")
    with c2b:
        ranked = sorted([(aff, get_vol(aff)) for aff in VOLUNTEER_DATA], key=lambda x:-x[1])
        ranked = [(a,v) for a,v in ranked if v > 0]
        rdf = pd.DataFrame(ranked, columns=['Affiliate','Sworn In'])
        fig_rank = go.Figure(go.Bar(x=rdf['Sworn In'], y=rdf['Affiliate'], orientation='h',
            marker_color=[RED if i==0 else DKBLUE if i==1 else LTBLUE for i in range(len(rdf))],
            text=rdf['Sworn In'], textposition='outside',
            hovertemplate="<b>%{y}</b><br>Sworn in: %{x}<extra></extra>"))
        style_fig(fig_rank, 430)
        fig_rank.update_layout(yaxis=dict(autorange='reversed',gridcolor="rgba(0,0,0,0)",tickfont=dict(size=9)),
            showlegend=False, margin=dict(l=10,r=30,t=20,b=10))
        st.plotly_chart(fig_rank, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Region breakdown table
    st.markdown("<div class='sec-head'>📊 Volunteers by Region — Detailed Breakdown</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-body'>", unsafe_allow_html=True)
    rows = []
    for region, affs in REGIONS:
        for aff in affs:
            v = VOLUNTEER_DATA.get(aff, [0]*len(VOL_QTR_LABELS))
            row = {'Region':region,'Affiliate':aff}
            for i, lbl in enumerate(VOL_QTR_LABELS):
                row[lbl] = v[i] if i < len(v) else 0
            row['Total'] = sum(v)
            rows.append(row)
    reg_df = pd.DataFrame(rows)
    st.dataframe(reg_df.style.bar(subset=['Total'],color=RED+"88"), use_container_width=True, height=500)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — QUARTERLY ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Page 3 — Quarterly Analysis":

    st.markdown(f"""<div class="casa-header">
        <h1>⚖️ CASA Georgia — Quarterly Analysis</h1>
        <p>Inquiries vs. volunteers sworn in &nbsp;|&nbsp; by fiscal quarter</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div class='note-box'>Fiscal year quarters: <strong>Q1 = Jul–Sep &nbsp;|&nbsp; Q2 = Oct–Dec &nbsp;|&nbsp; Q3 = Jan–Mar &nbsp;|&nbsp; Q4 = Apr–Jun</strong> &nbsp;·&nbsp; All numbers calculated automatically from your data files.</div>", unsafe_allow_html=True)

    # ── Build quarterly data DYNAMICALLY from loaded files ───────────────────
    # Define all quarters we want to show (add more as needed)
    QTR_DEFS = [
        ('FY25 Q1', 'FY2025 Q1', ['2024-07','2024-08','2024-09'], 'Jul–Sep 24'),
        ('FY25 Q2', 'FY2025 Q2', ['2024-10','2024-11','2024-12'], 'Oct–Dec 24'),
        ('FY25 Q3', 'FY2025 Q3', ['2025-01','2025-02','2025-03'], 'Jan–Mar 25'),
        ('FY25 Q4', 'FY2025 Q4', ['2025-04','2025-05','2025-06'], 'Apr–Jun 25'),
        ('FY26 Q1', 'FY2026 Q1', ['2025-07','2025-08','2025-09'], 'Jul–Sep 25'),
        ('FY26 Q2', 'FY2026 Q2', ['2025-10','2025-11','2025-12'], 'Oct–Dec 25'),
        ('FY26 Q3', 'FY2026 Q3', ['2026-01','2026-02','2026-03'], 'Jan–Mar 26'),
        ('FY26 Q4', 'FY2026 Q4', ['2026-04','2026-05','2026-06'], 'Apr–Jun 26'),
    ]

    # Months we actually have inquiry data for
    available_months = set(df['YearMonth'].unique())

    # Get sworn-in total per quarter label from VOL_QTR_LABELS
    def get_sworn_for_qtr(short_label):
        # Match e.g. 'FY25 Q1' -> index in VOL_QTR_LABELS
        for i, lbl in enumerate(VOL_QTR_LABELS):
            if lbl == short_label:
                return sum(
                    (VOLUNTEER_DATA.get(aff, [])[i] if i < len(VOLUNTEER_DATA.get(aff, [])) else 0)
                    for aff in VOLUNTEER_DATA
                )
        return None  # No sworn-in data for this quarter

    QTR_LABELS, INQ_DATA, SWN_DATA, INQ_COLORS, HAS_INQ, TABLE_ROWS = [], [], [], [], [], []

    for short_lbl, full_lbl, months, period in QTR_DEFS:
        # Count inquiries from actual data
        months_present = [m for m in months if m in available_months]
        months_missing = [m for m in months if m not in available_months]
        inq_count = len(df[df['YearMonth'].isin(months)])

        # Sworn in
        sworn = get_sworn_for_qtr(short_lbl)

        # Only show quarter if we have either inquiries or sworn-in data
        if inq_count == 0 and sworn is None:
            continue

        has_inq = inq_count > 0
        HAS_INQ.append(has_inq)
        QTR_LABELS.append(f"{short_lbl}<br>{period}")
        INQ_DATA.append(inq_count)
        SWN_DATA.append(sworn if sworn is not None else 0)

        if not has_inq:
            INQ_COLORS.append("rgba(245,166,35,0.55)")  # amber = no data
        elif len(months_missing) > 0:
            INQ_COLORS.append("rgba(0,40,85,0.55)")      # faded = partial
        else:
            INQ_COLORS.append("rgba(0,40,85,0.88)")      # full blue = complete

        # Table row
        if not has_inq:
            inq_str = "No data"
            conv_str = "—"
        elif months_missing:
            missing_labels = [pd.Period(m,'M').strftime('%b') for m in months_missing]
            inq_str = f"{inq_count} ({', '.join(missing_labels)} missing)"
            conv_str = "Partial"
        else:
            inq_str = str(inq_count)
            conv_str = f"{round(sworn/inq_count*100)}%" if sworn and inq_count else "—"

        TABLE_ROWS.append({
            'Quarter': full_lbl,
            'Period':  period.replace('–','–'),
            'Inquiries': inq_str,
            'Sworn In': str(sworn) if sworn is not None else "Not yet available",
            'Conversion': conv_str,
        })

    # KPIs — now calculated from real data
    total_sworn_all = sum(sum(v) for v in VOLUNTEER_DATA.values())
    total_inq_matched = sum(c for c,h in zip(INQ_DATA,HAS_INQ) if h)
    best_sworn_val = max((s for s in SWN_DATA if s > 0), default=0)
    best_sworn_lbl = QTR_LABELS[SWN_DATA.index(best_sworn_val)].replace('<br>',' ') if best_sworn_val else "—"
    most_inq_val = max(INQ_DATA) if INQ_DATA else 0
    most_inq_lbl = QTR_LABELS[INQ_DATA.index(most_inq_val)].replace('<br>',' ') if most_inq_val else "—"

    k1,k2,k3,k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Sworn In</div><div class="kpi-value">{total_sworn_all:,}</div><div class="kpi-sub">All quarters in file</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card blue"><div class="kpi-label">Total Inquiries</div><div class="kpi-value">{total_inq_matched:,}</div><div class="kpi-sub">Quarters with full data</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Best Sworn-in Qtr</div><div class="kpi-value">{best_sworn_val}</div><div class="kpi-sub">{best_sworn_lbl}</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-card blue"><div class="kpi-label">Most Inquiries</div><div class="kpi-value">{most_inq_val:,}</div><div class="kpi-sub">{most_inq_lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # Chart: Inquiries vs Sworn In
    st.markdown("<div class='sec-head'>📊 Inquiries vs. Volunteers Sworn In — by Quarter</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-body'>", unsafe_allow_html=True)

    st.markdown("""<div class='note-box'>
        💡 <strong>What this tells you:</strong>
        The <strong style="color:#002855">dark blue bars</strong> show how many people expressed interest in volunteering that quarter.
        The <strong style="color:#C8102E">red bars</strong> show how many actually completed training and were sworn in.
        The gap between the two bars is your <strong>pipeline</strong> — people who inquired but haven't been sworn in yet.
        A smaller gap means your affiliate is doing a great job converting interest into active volunteers.
        <strong>Amber bars = no inquiry file available for that quarter. Faded blue = partial data.</strong>
    </div>""", unsafe_allow_html=True)

    # Two separate traces: one for "has data" bars and one for "no data" bars
    # This ensures the legend shows the right color
    fig_q = go.Figure()

    # Inquiry bars
    fig_q.add_trace(go.Bar(
        name='Inquiries',
        x=QTR_LABELS, y=INQ_DATA,
        marker_color=INQ_COLORS, marker_line_width=0,
        text=[str(v) if v > 0 else 'No data' for v in INQ_DATA],
        textposition='outside',
        hovertemplate="<b>%{x}</b><br>Inquiries: %{y}<extra></extra>",
        legendrank=1
    ))

    # Sworn-in bars — only if we have data
    if any(v > 0 for v in SWN_DATA):
        fig_q.add_trace(go.Bar(
            name='Sworn In',
            x=QTR_LABELS, y=SWN_DATA,
            marker_color="rgba(200,16,46,0.88)", marker_line_width=0,
            text=[str(v) if v > 0 else '—' for v in SWN_DATA],
            textposition='outside',
            hovertemplate="<b>%{x}</b><br>Sworn In: %{y}<extra></extra>",
            legendrank=2
        ))
    else:
        st.info("💡 Upload your sworn-in Excel to the data folder to see the Sworn In bars here.")

    style_fig(fig_q, 420)
    fig_q.update_layout(
        barmode='group', bargap=0.2, bargroupgap=0.05,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(size=12), itemsizing='constant',
            bgcolor="rgba(0,0,0,0)"
        ),
        # Force x-axis to treat labels as categories not numbers
        xaxis=dict(type='category', gridcolor="#E8ECF0", linecolor=MIDGRAY,
                   tickfont=dict(size=10))
    )
    fig_q.add_annotation(
        text="⚠️ Amber = no inquiry data available for that quarter",
        xref="paper", yref="paper", x=0, y=-0.18,
        showarrow=False, font=dict(size=10, color="#B8860B"), align="left"
    )
    st.plotly_chart(fig_q, use_container_width=True)

    # Conversion table — built dynamically
    conv_df = pd.DataFrame(TABLE_ROWS)
    st.dataframe(conv_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Affiliate breakdown
    st.markdown("<div class='sec-head'>🏢 New Volunteers Sworn In by Affiliate — by Quarter</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-body'>", unsafe_allow_html=True)

    st.markdown("<div style='font-size:12px;font-weight:700;color:#002855;margin-bottom:4px'>Filter by Quarter (select one or more):</div>", unsafe_allow_html=True)
    col_all3, col_qtrs3 = st.columns([1,4])
    with col_all3:
        select_all_qtrs3 = st.checkbox("All", value=True, key="p3_all")
    with col_qtrs3:
        if select_all_qtrs3:
            selected_qtrs3 = VOL_QTR_LABELS
            st.multiselect("", VOL_QTR_LABELS, default=VOL_QTR_LABELS, key="p3_multi", disabled=True, label_visibility="collapsed")
        else:
            selected_qtrs3 = st.multiselect("", VOL_QTR_LABELS, default=[VOL_QTR_LABELS[-1]] if VOL_QTR_LABELS else [], key="p3_multi2", label_visibility="collapsed")
            if not selected_qtrs3:
                selected_qtrs3 = VOL_QTR_LABELS

    selected_idxs3 = [VOL_QTR_LABELS.index(q) for q in selected_qtrs3 if q in VOL_QTR_LABELS]

    vol_rows = []
    for region, affs in REGIONS:
        for aff in affs:
            v = VOLUNTEER_DATA.get(aff, [])
            count = sum(v[i] for i in selected_idxs3 if i < len(v))
            vol_rows.append({'Region':region,'Affiliate':aff,'Count':count})
    vol_sorted = pd.DataFrame(vol_rows).sort_values('Count',ascending=False)
    vol_sorted = vol_sorted[vol_sorted['Count']>0]

    fig_aff = go.Figure(go.Bar(
        x=vol_sorted['Count'], y=vol_sorted['Affiliate'], orientation='h',
        marker_color=[RED if i==0 else DKBLUE if i==1 else LTBLUE for i in range(len(vol_sorted))],
        text=vol_sorted['Count'], textposition='outside',
        customdata=vol_sorted['Region'],
        hovertemplate="<b>%{y}</b><br>Region: %{customdata}<br>Sworn In: %{x}<extra></extra>"
    ))
    style_fig(fig_aff, max(300, len(vol_sorted)*20))
    fig_aff.update_layout(yaxis=dict(autorange='reversed',gridcolor="rgba(0,0,0,0)",tickfont=dict(size=10)),
        showlegend=False, margin=dict(l=10,r=50,t=20,b=10))
    st.plotly_chart(fig_aff, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
