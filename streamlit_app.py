import streamlit as st
import pandas as pd
import folium
import re
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSs5tRlFEqLz6J-Ubg8Kh3CkYokxMR-bl9VKWCNNSAV4H6KvNDRyGqDTssxh6dbxUpH0NXJyT8Tq430/pub?gid=393036172&single=true&output=csv"

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

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

df["Latitud (LAT.)"] = pd.to_numeric(df["Latitud (LAT.)"], errors="coerce")
df["Longitud (LONG.)"] = pd.to_numeric(df["Longitud (LONG.)"], errors="coerce")

df = df.dropna(subset=["Latitud (LAT.)", "Longitud (LONG.)"])

col1, col2 = st.columns(2)

with col1:
    sucursales = ["(All)"] + sorted(df["SUCURSAL:"].dropna().unique().tolist())
    sel_suc = st.selectbox("Lọc theo Sucursal:", sucursales)

with col2:
    tipos = ["(All)"] + sorted(df["Tipo de usuario:"].dropna().unique().tolist())
    sel_tipo = st.selectbox("Lọc theo AC/AD:", tipos)

df_map = df.copy()
if sel_suc != "(All)":
    df_map = df_map[df_map["SUCURSAL:"] == sel_suc]
if sel_tipo != "(All)":
    df_map = df_map[df_map["Tipo de usuario:"] == sel_tipo]

st.write(f"### 🧭 Số điểm hiển thị: {len(df_map)}")

m = folium.Map(
    location=[df_map["Latitud (LAT.)"].mean(), df_map["Longitud (LONG.)"].mean()],
    zoom_start=6,
)

for _, row in df_map.iterrows():
    fid1 = get_drive_id(row.get("EVIDENCIA PORTA CHIPS", ""))
    fid2 = get_drive_id(row.get("EVIDENCIA DE LA IMPLEMENTAR", ""))
    fid3 = get_drive_id(row.get("Evidencia de la foto de BIPAY", ""))

    popup = f"""
    <b>Sucursal:</b> {row['SUCURSAL:']}<br>
    <b>Tipo usuario:</b> {row['Tipo de usuario:']}<br>
    <b>Usuario:</b> {row['Usuario: AC/AD']}<br>
    <b>Chips:</b> {row['Cantidad de chips entregados']}<br><br>
    <div style="max-height:380px; overflow-y:auto;">
        {img_block(fid1)}
        {img_block(fid2)}
        {img_block(fid3)}
    </div>
    """

    folium.Marker(
        location=[row["Latitud (LAT.)"], row["Longitud (LONG.)"]],
        popup=popup
    ).add_to(m)

st_folium(m, height=850, width=1500)

# ============================
# BẢNG DƯỚI MAP
# ============================

df_display = df_map[[
    "SUCURSAL:",
    "Tipo de usuario:",
    "Usuario: AC/AD",
    "Cantidad de chips entregados",
    "EVIDENCIA PORTA CHIPS",
    "EVIDENCIA DE LA IMPLEMENTAR",
    "Evidencia de la foto de BIPAY"
]].copy()

df_display.columns = [
    "Sucursal",
    "Tipo de usuario",
    "Usuario",
    "Chips entregados",
    "Porta Chips Img",
    "Implementar Img",
    "BIPAY Img"
]

st.dataframe(df_display, use_container_width=True)
