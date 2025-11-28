import streamlit as st
import pandas as pd
import folium
import re
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSs5tRlFEqLz6J-Ubg8Kh3CkYokxMR-bl9VKWCNNSAV4H6KvNDRyGqDTssxh6dbxUpH0NXJyT8Tq430/pub?gid=393036172&single=true&output=csv"

@st.cache_data
def load_data():
    return pd.read_csv(CSV_URL)

df = load_data()

# ===== CHỌN CỘT CHÍNH XÁC =====
col_sucursal = 'SUCURSAL:'
col_tipo = 'Tipo de usuario:'
col_usuario = 'Ac_kenedyho_jun'
col_lon = 'Longitud (LONG.)'
col_lat = 'Latitud (LAT.) '
col_chips = 'Cantidad de chips entregados'

# ép dạng số
df[col_lat] = pd.to_numeric(df[col_lat], errors="coerce")
df[col_lon] = pd.to_numeric(df[col_lon], errors="coerce")

# tạo df_map chỉ gồm các điểm có tọa độ thực
df_map = df.dropna(subset=[col_lat, col_lon]).copy()

# map auto căn giữa Peru thay vì 0,0
if len(df_map) > 0:
    avg_lat = df_map[col_lat].mean()
    avg_lon = df_map[col_lon].mean()
else:
    avg_lat = -12.0464   # Lima
