import streamlit as st
import pandas as pd
import folium
import re
from streamlit_folium import st_folium
# from folium.plugins import MarkerCluster  # không dùng cluster nữa

st.set_page_config(layout="wide")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRSN9y26MSLRftqr2_On7MEOJ4h4L1o1I_ZXsHfoF1F0qY7Mjnx0bX3A7sxJ7Hz_f02E-gkMxY1t9M_/pub?gid=393036172&single=true&output=csv"

# ============================
# LẤY DRIVE IMAGE ID
# ============================
def get_drive_id(url: str) -> str:
    if not isinstance(url, str):
        return ""
    url = url.strip()

    if "open?id=" in url:
        return url.split("open?id=")[1]

    m = re.search(r"/file/d/([^/]+)/", url)
    if m:
        return m.group(1)

    if "uc?export=view&id=" in url:
        return url.split("uc?export=view&id=")[1]

    return ""

def img_block(fid: str) -> str:
    if not fid:
        return ""
    thumb = f"https://drive.google.com/thumbnail?id={fid}"
    full = f"https://drive.google.com/uc?export=view&id={fid}"
    return f"""
        <div style="margin-bottom:6px; text-align:center;">
          <a href="{full}" target="_blank">
            <img src="{thumb}"
                 style="width:240px; max-height:180px; object-fit:cover; border:1px solid #ccc;">
          </a>
        </div>
    """

def safe(x):
    return "" if pd.isna(x) else str(x)

# ============================
# TẢI CSV
# ============================
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()
    return df

df = load_data()
