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

VOLUNTEER_DATA = {
    'Advo-Kids':[0,4,0],'Ocmulgee':[0,3,2],'Central Ga':[0,0,0],
    'Towaliga':[3,6,7],'Houston':[2,4,0],'TLC':[2,3,1],
    'Troup':[0,1,0],'Coweta':[0,2,1],
    'Atlanta':[16,2,19],'Henry':[0,3,0],"Children's Voice":[0,5,6],
    'Clayton':[5,1,0],'DeKalb':[3,5,4],'Gwinnett':[9,7,0],
    'Cobb':[5,8,0],'Rockdale':[5,4,0],'Forsyth':[6,6,0],'Alcovy':[5,1,0],
    'Piedmont':[0,2,7],'Athens':[0,10,18],'Enotah':[0,5,1],
    'Hall-Dawson':[10,4,0],'NE CASA':[3,2,6],'Mountain':[0,0,1],
    'NW GA':[0,7,0],'Cherokee':[9,1,14],'Paulding':[4,5,6],
    'Appalachian':[2,7,2],'Floyd':[0,4,0],'Polk & Haralson':[1,2,3],
    'Murray/Whitfield':[0,0,1],'Lookout Mountain':[7,0,0],
    'Atlantic Area':[3,1,1],'Glynn':[10,0,4],'Augusta':[11,9,4],
    'Ogeechee':[3,0,1],'Savannah':[7,14,11],'SE CASA':[4,0,0],
    'Lowndes & Echols':[1,5,0],'CASA SW':[2,0,1],'SOWEGA':[5,6,0],
    'Chattahoochee':[0,0,8],'CASA Kids':[4,0,4],'Alapaha':[4,2,0],
    'Coastal Plain':[0,9,0],'Dougherty':[4,3,3],
}

# ── DATA LOADING ──────────────────────────────────────────────────────────────
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
    combined['FYQuarter'] = combined['YearMonth'].apply(get_fy_quarter)
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
    c2a,c2b = st.columns(2)
    with c2a:
        fig2a = px.pie(src_counts, values='Count', names='Source',
                       color_discrete_sequence=CHART_COLORS, hole=0.45)
        fig2a.update_traces(textposition='outside', textinfo='label+percent',
                            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>")
        style_fig(fig2a, 360)
        fig2a.update_layout(showlegend=False)
        st.plotly_chart(fig2a, use_container_width=True)
    with c2b:
        fig2b = go.Figure(go.Bar(x=src_counts['Count'], y=src_counts['Source'], orientation='h',
            marker_color=[RED if i==0 else DKBLUE if i==1 else LTBLUE for i in range(len(src_counts))],
            text=src_counts['Count'], textposition='outside',
            hovertemplate="<b>%{y}</b><br>Count: %{x}<extra></extra>"))
        style_fig(fig2b, 360)
        fig2b.update_layout(yaxis=dict(autorange='reversed', gridcolor="rgba(0,0,0,0)"), showlegend=False)
        st.plotly_chart(fig2b, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Chart 3: County map
    st.markdown("<div class='sec-head'>🗺️ 3. Inquiries by County & Affiliate</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-body'>", unsafe_allow_html=True)
    county_counts = filtered['County'].value_counts().reset_index()
    county_counts.columns = ['County','Count']
    county_counts['Affiliate'] = county_counts['County'].map(COUNTY_TO_AFF).fillna('Other')
    county_counts['Lat'] = county_counts['County'].map(lambda c: COUNTY_COORDS.get(c,(None,None))[0])
    county_counts['Lon'] = county_counts['County'].map(lambda c: COUNTY_COORDS.get(c,(None,None))[1])
    map_data = county_counts.dropna(subset=['Lat','Lon'])

    c3a,c3b = st.columns([3,2])
    with c3a:
        fig_map = px.scatter_mapbox(map_data, lat='Lat', lon='Lon', size='Count',
            color='Affiliate', hover_name='County',
            hover_data={'Count':True,'Affiliate':True,'Lat':False,'Lon':False},
            size_max=45, zoom=6, center={"lat":32.5,"lon":-83.5},
            color_discrete_sequence=CHART_COLORS, mapbox_style="carto-positron")
        fig_map.update_layout(height=420, margin=dict(l=0,r=0,t=0,b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="v",x=0.01,y=0.99,bgcolor="rgba(255,255,255,.85)",
                        bordercolor=MIDGRAY,borderwidth=1,font=dict(size=9)))
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

    qtr_sel = st.selectbox("Filter by Quarter:", ["All Quarters", "Q1 — Jul–Sep 2025", "Q2 — Oct–Dec 2025", "Q3 — Jan–Mar 2026"])
    qtr_idx = {"All Quarters":None,"Q1 — Jul–Sep 2025":0,"Q2 — Oct–Dec 2025":1,"Q3 — Jan–Mar 2026":2}[qtr_sel]

    def get_vol(aff):
        v = VOLUNTEER_DATA.get(aff, [0,0,0])
        return sum(v) if qtr_idx is None else v[qtr_idx]

    st.markdown("<div class='sec-head'>🗺️ Volunteers Sworn In — by Affiliate (Bubble Map)</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-body'>", unsafe_allow_html=True)

    # Build affiliate bubble positions (use county centroids for affiliate HQ counties)
    AFF_COORDS = {
        'Atlanta':(33.749,-84.388),'Savannah':(32.028,-81.107),'Augusta':(33.374,-82.076),
        'Cherokee':(34.239,-84.479),'Carroll':(33.581,-85.078),'Gwinnett':(33.962,-84.002),
        'Athens':(33.961,-83.377),'Hall-Dawson':(34.311,-83.818),'Cobb':(33.938,-84.578),
        'Paulding':(33.927,-84.864),'Forsyth':(34.226,-84.133),'Coweta':(33.357,-84.760),
        'Glynn':(31.221,-81.517),'Rockdale':(33.657,-84.021),'Northwest':(34.503,-84.877),
        'Lookout Mountain':(34.743,-85.300),'DeKalb':(33.775,-84.232),'Houston':(32.465,-83.652),
        'CASA Kids':(32.169,-83.777),'SOWEGA':(31.462,-83.523),"Children's Voice":(34.138,-83.562),
        'NE CASA':(34.115,-82.849),'Appalachian':(34.870,-84.321),'Piedmont':(33.268,-84.289),
        'Dougherty':(31.535,-84.169),'Chattahoochee':(32.460,-84.988),'Towaliga':(33.073,-84.290),
        'Lowndes & Echols':(30.832,-83.279),'Coastal Plain':(31.063,-82.415),'Atlantic Area':(31.837,-81.455),
        'Henry':(33.448,-84.152),'Alcovy':(33.553,-83.847),'SE CASA':(31.550,-82.845),
        'Advo-Kids':(32.461,-82.913),'TLC':(33.357,-84.760),'Ocmulgee':(32.838,-83.694),
        'Alapaha':(31.295,-82.882),'Enotah':(34.629,-83.532),'Polk & Haralson':(34.002,-85.173),
        'Ogeechee':(32.409,-81.775),'CASA SW':(30.855,-83.929),'Murray/Whitfield':(34.797,-84.977),
        'NW GA':(34.262,-85.214),'Mountain':(34.629,-83.532),'Floyd':(34.262,-85.214),
        'Central Ga':(33.073,-83.250),'Troup':(33.037,-85.030),'Clayton':(33.557,-84.359),
    }

    vol_map_data = []
    for aff, coords in AFF_COORDS.items():
        v = get_vol(aff)
        if v > 0:
            vol_map_data.append({'Affiliate':aff,'Count':v,'Lat':coords[0],'Lon':coords[1]})
    vol_df = pd.DataFrame(vol_map_data)

    c2a, c2b = st.columns([3,2])
    with c2a:
        if not vol_df.empty:
            fig_vmap = px.scatter_mapbox(vol_df, lat='Lat', lon='Lon', size='Count',
                hover_name='Affiliate', hover_data={'Count':True,'Lat':False,'Lon':False},
                size_max=50, zoom=6, center={"lat":32.5,"lon":-83.5},
                color='Count', color_continuous_scale=[[0,LGRAY],[0.3,'#FF9090'],[0.6,RED],[1.0,'#7A0818']],
                mapbox_style="carto-positron")
            fig_vmap.update_layout(height=430, margin=dict(l=0,r=0,t=0,b=0),
                paper_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
            st.plotly_chart(fig_vmap, use_container_width=True)
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
            v = VOLUNTEER_DATA.get(aff,[0,0,0])
            rows.append({'Region':region,'Affiliate':aff,'Q1':v[0],'Q2':v[1],'Q3':v[2],'Total':sum(v)})
    reg_df = pd.DataFrame(rows)
    st.dataframe(reg_df.style.bar(subset=['Total'],color=RED+"88"), use_container_width=True, height=500)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — QUARTERLY ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Page 3 — Quarterly Analysis":

    st.markdown(f"""<div class="casa-header">
        <h1>⚖️ CASA Georgia — Quarterly Analysis</h1>
        <p>Inquiries vs. volunteers sworn in &nbsp;|&nbsp; FY2025 & FY2026 by fiscal quarter</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div class='note-box'>Fiscal year quarters: <strong>Q1 = Jul–Sep &nbsp;|&nbsp; Q2 = Oct–Dec &nbsp;|&nbsp; Q3 = Jan–Mar &nbsp;|&nbsp; Q4 = Apr–Jun</strong><br>FY2025 = 4 quarters complete &nbsp;·&nbsp; FY2026 = 3 quarters available &nbsp;·&nbsp; Amber bars = no matching inquiry data</div>", unsafe_allow_html=True)

    # KPIs
    k1,k2,k3,k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Sworn In (7 qtrs)</div><div class="kpi-value">1,140</div><div class="kpi-sub">FY2025 Q1 through FY2026 Q3</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card blue"><div class="kpi-label">Matched Inquiries</div><div class="kpi-value">1,313</div><div class="kpi-sub">5 fully-matched quarters</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Best Sworn-in Qtr</div><div class="kpi-value">181</div><div class="kpi-sub">FY2025 Q4 (Apr–Jun 2025)</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-card blue"><div class="kpi-label">Most Inquiries</div><div class="kpi-value">382</div><div class="kpi-sub">FY2026 Q3 (Jan–Mar 2026)</div></div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # Chart: Inquiries vs Sworn In
    st.markdown("<div class='sec-head'>📊 Inquiries vs. Volunteers Sworn In — by Quarter</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-body'>", unsafe_allow_html=True)

    QTR_LABELS = ['FY25 Q1<br>Jul–Sep 24','FY25 Q2<br>Oct–Dec 24','FY25 Q3<br>Jan–Mar 25',
                  'FY25 Q4<br>Apr–Jun 25','FY26 Q1<br>Jul–Sep 25','FY26 Q2<br>Oct–Dec 25','FY26 Q3<br>Jan–Mar 26']
    INQ_DATA  = [0, 77, 294, 0, 285, 255, 382]
    SWN_DATA  = [159,174,141,181,173,179,133]
    NO_DATA   = [True,False,False,True,False,False,False]
    INQ_COLORS= [GOLD+"88" if nd else DKBLUE+"DD" for nd in NO_DATA]

    fig_q = go.Figure()
    fig_q.add_trace(go.Bar(name='Inquiries', x=QTR_LABELS, y=INQ_DATA,
        marker_color=INQ_COLORS, marker_line_width=0,
        text=[str(v) if v>0 else 'No data' for v in INQ_DATA], textposition='outside',
        hovertemplate="<b>%{x}</b><br>Inquiries: %{y}<extra></extra>"))
    fig_q.add_trace(go.Bar(name='Sworn In', x=QTR_LABELS, y=SWN_DATA,
        marker_color=RED+"DD", marker_line_width=0,
        text=SWN_DATA, textposition='outside',
        hovertemplate="<b>%{x}</b><br>Sworn In: %{y}<extra></extra>"))
    style_fig(fig_q, 350)
    fig_q.update_layout(barmode='group', bargap=0.25, bargroupgap=0.05,
        legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
    st.plotly_chart(fig_q, use_container_width=True)

    # Conversion table
    conv_data = {
        'Quarter':    ['FY2025 Q1','FY2025 Q2','FY2025 Q3','FY2025 Q4','FY2026 Q1','FY2026 Q2','FY2026 Q3','FY2026 Q4'],
        'Period':     ['Jul–Sep 2024','Oct–Dec 2024','Jan–Mar 2025','Apr–Jun 2025','Jul–Sep 2025','Oct–Dec 2025','Jan–Mar 2026','Apr–Jun 2026'],
        'Inquiries':  ['No data','77 (Dec only)','294','No data','285','255','382','175 (Apr+May only)'],
        'Sworn In':   ['159','174','141','181','173','179','133','Not yet available'],
        'Conversion': ['—','Partial','48%','—','61%','70%','35%','—'],
    }
    conv_df = pd.DataFrame(conv_data)
    st.dataframe(conv_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Affiliate breakdown
    st.markdown("<div class='sec-head'>🏢 New Volunteers Sworn In by Affiliate — by Quarter</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-body'>", unsafe_allow_html=True)

    qtr_filter = st.selectbox("Select quarter:", ["All FY2026 Quarters","Q1 — Jul–Sep 2025","Q2 — Oct–Dec 2025","Q3 — Jan–Mar 2026"])
    qi = {"All FY2026 Quarters":None,"Q1 — Jul–Sep 2025":0,"Q2 — Oct–Dec 2025":1,"Q3 — Jan–Mar 2026":2}[qtr_filter]

    vol_rows = []
    for region, affs in REGIONS:
        for aff in affs:
            v = VOLUNTEER_DATA.get(aff,[0,0,0])
            count = sum(v) if qi is None else v[qi]
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
