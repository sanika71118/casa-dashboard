# CASA Georgia — Volunteer Inquiries Dashboard

A Streamlit dashboard showing volunteer inquiry trends across Georgia CASA affiliates.

## Project Structure

```
casa_dashboard/
│
├── app.py                  ← Main dashboard (all the code lives here)
├── requirements.txt        ← Python packages needed
├── README.md               ← This file
│
└── data/                   ← DROP ALL YOUR EXCEL FILES HERE
    ├── Dec_2024_Inquiries.xlsx
    ├── Jan_2025_inquiries.xlsx
    ├── ... (all monthly files)
    └── volunteers.xlsx     ← Your separate volunteers file (when ready)
```

---

## Setup Instructions (One-time)

### Step 1 — Install Python
If you don't have Python: https://www.python.org/downloads/
Download Python 3.11 or newer. During install, check **"Add Python to PATH"**.

### Step 2 — Install packages
Open a terminal (search "Command Prompt" on Windows or "Terminal" on Mac) and run:
```
pip install streamlit pandas plotly openpyxl
```

### Step 3 — Run locally
Navigate to the project folder and run:
```
cd casa_dashboard
streamlit run app.py
```
The dashboard opens in your browser at http://localhost:8501

---

## Deploying to Streamlit Cloud (Free — Get a Public Link)

### Step 1 — Create a GitHub account
Go to https://github.com and sign up (free).

### Step 2 — Create a new repository
- Click the **+** button → **New repository**
- Name it: `casa-dashboard`
- Set to **Private** (recommended for data privacy)
- Click **Create repository**

### Step 3 — Upload your files
- Click **uploading an existing file**
- Upload: `app.py`, `requirements.txt`
- Create a folder called `data` and upload all your Excel files into it

### Step 4 — Deploy on Streamlit Cloud
- Go to https://share.streamlit.io
- Sign in with your GitHub account
- Click **New app**
- Choose your `casa-dashboard` repo
- Main file path: `app.py`
- Click **Deploy**
- In ~2 minutes you get a link like: `https://casa-dashboard-xyz.streamlit.app`

### Step 5 — Share the link
Send the link to your colleagues — they just click it, no install needed!

---

## Adding New Monthly Data

Every month when you get a new Excel file:

**If hosted on Streamlit Cloud (GitHub):**
1. Go to your GitHub repo
2. Click on the `data` folder
3. Click **Add file → Upload files**
4. Upload the new Excel file
5. Click **Commit changes**
6. Dashboard auto-refreshes within seconds ✅

**If running locally:**
1. Drop the new Excel file into the `/data` folder
2. Refresh the dashboard in your browser ✅

---

## Adding the Volunteers File (Section 4)

When you're ready to add volunteer data:
1. Name the file: `volunteers.xlsx`
2. Drop it in the `/data` folder
3. Send me the file and I'll build out Section 4 fully

---

## Dashboard Sections

| Section | Description |
|---------|-------------|
| 📅 1. Inquiries by Month | Bar chart with trend line per month |
| 📢 2. Inquiries by Source | Donut chart + horizontal bar |
| 🗺️ 3. Map by County & Affiliate | Bubble map + affiliate ranking |
| 🌟 4. New Volunteers | Ready for your volunteers file |

---

## Sidebar Filters

- **Select All Months** — shows everything
- **Choose specific months** — select one or multiple months to compare
- All 4 dashboard sections update instantly when you change the filter

---

## Theme

CASA Georgia brand colors:
- 🔴 Red: `#C8102E`
- 🔵 Dark Blue: `#002855`
