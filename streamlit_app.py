import streamlit as st
import pandas as pd
import folium
import re
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

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

# ============================
# Đổi tên cột về dạng lower-case để xử lý
# ============================
df.columns = [c.lower() for c in df.columns]

# ép dạng số cho lat/lon
df["latitud (lat.)"] = pd.to_numeric(df["latitud (lat.)"], errors="coerce")
df["longitud (long.)"] = pd.to_numeric(df["longitud (long.)"], errors="coerce")
df["cantidad de chips entregados"] = pd.to_numeric(df["cantidad de chips entregados"], errors="coerce").fillna(0).astype(int)

df = df.dropna(subset=["latitud (lat.)", "longitud (long.)"])

# ============================
# FILTER UI
# ============================
col1, col2 = st.columns(2)

with col1:
    suc_list = ["(All)"] + sorted(df["sucursal:"].dropna().unique().tolist())
    sel_suc = st.selectbox("Lọc theo Sucursal", suc_list)

with col2:
    tipo_list = ["(All)"] + sorted(df["tipo de usuario:"].dropna().unique().tolist())
    sel_tipo = st.selectbox("Lọc theo AC/AD", tipo_list)

df_map = df.copy()
if sel_suc != "(All)":
    df_map = df_map[df_map["sucursal:"] == sel_suc]
if sel_tipo != "(All)":
    df_map = df_map[df_map["tipo de usuario:"] == sel_tipo]

# ============================
# TẠO MAP
# ============================
st.write(f"### 🧭 Số điểm hiển thị trên bản đồ: {len(df_map)}")

m = folium.Map(location=[df_map["latitud (lat.)"].mean(), df_map["longitud (long.)"].mean()], zoom_start=6)
marker_cluster = MarkerCluster().add_to(m)

for _, row in df_map.iterrows():

    # === DRIVE IMAGES ===
    fid1 = get_drive_id(row.get("evidencia porta chips", ""))
    fid2 = get_drive_id(row.get("evidencia de la implementar", ""))
    fid3 = get_drive_id(row.get("evidencia de la foto de bipay", ""))

    # === FIELDS ĐÚNG TỪ CSV ===
    usuario_val = safe(row.get("código de usuario ac/ad", ""))
    bodega_val  = safe(row.get("código de la bodega (ab, nb, pdv)", ""))
    chips_val   = safe(row.get("cantidad de chips entregados", ""))

    # === ICON & COLOR ===
    color = "green" if row["tipo de usuario:"] == "AC" else "red"
    icon = "user" if row["tipo de usuario:"] == "AC" else "shopping-cart"

    popup = f"""
    <b>Sucursal:</b> {row['sucursal:']}<br>
    <b>Tipo:</b> {row['tipo de usuario:']}<br>
    <b>Usuario:</b> {usuario_val}<br>
    <b>Bodega:</b> {bodega_val}<br>
    <b>Chips:</b> {chips_val}<br><br>
    <div style="max-height:380px; overflow-y:auto; padding-right:4px;">
        {img_block(fid1)}
        {img_block(fid2)}
        {img_block(fid3)}
    </div>
    """

    folium.Marker(
        location=[row["latitud (lat.)"], row["longitud (long.)"]],
        popup=folium.Popup(popup, max_width=280),
        tooltip=f"{usuario_val}",
        icon=folium.Icon(color=color, icon=icon, prefix="fa"),
    ).add_to(marker_cluster)

st_folium(m, height=850, width=1500)

# ============================
# BẢNG DƯỚI MAP
# ============================
df_display = df_map[[
    "sucursal:", 
    "tipo de usuario:",
    "código de usuario ac/ad",
    "código de la bodega (ab, nb, pdv)",
    "cantidad de chips entregados",
    "latitud (lat.)",
    "longitud (long.)"
]].copy()

df_display.columns = ["Sucursal","Tipo","Usuario","Bodega","Chips","Lat","Lon"]

st.dataframe(df_display, use_container_width=True)
