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

def get_drive_id(url: str) -> str:
    if not isinstance(url, str):
        return ""
    url = url.strip()
    if "open?id=" in url:
        return url.split("open?id=")[1]
    m = re.search(r"/file/d/([^/]+)/", url)
    return m.group(1) if m else ""

def img_block(fid: str):
    if not fid:
        return ""
    return f'<img src="https://drive.google.com/thumbnail?id={fid}" width="200"><br>'

# ép dạng số
df["Latitud (LAT.)"] = pd.to_numeric(df["Latitud (LAT.)"], errors="coerce")
df["Longitud (LONG.)"] = pd.to_numeric(df["Longitud (LONG.)"], errors="coerce")
df = df.dropna(subset=["Latitud (LAT.)", "Longitud (LONG.)"])

def getval(row, col):
    return row[col] if col in row else ""

col1, col2 = st.columns(2)

with col1:
    suc = ["(All)"] + sorted(df["SUCURSAL:"].dropna().unique().tolist())
    sel_suc = st.selectbox("Sucursal:", suc)

with col2:
    tipo = ["(All)"] + sorted(df["Tipo de usuario:"].dropna().unique().tolist())
    sel_tipo = st.selectbox("Tipo de usuario:", tipo)

df_map = df.copy()
if sel_suc != "(All)":
    df_map = df_map[df_map["SUCURSAL:"] == sel_suc]
if sel_tipo != "(All)":
    df_map = df_map[df_map["Tipo de usuario:"] == sel_tipo]

st.write("### Số điểm:", len(df_map))

m = folium.Map(
    location=[df_map["Latitud (LAT.)"].mean(), df_map["Longitud (LONG.)"].mean()],
    zoom_start=6,
)

for _, row in df_map.iterrows():

    fid1 = get_drive_id(getval(row, "EVIDENCIA PORTA CHIPS"))
    fid2 = get_drive_id(getval(row, "EVIDENCIA DE LA IMPLEMENTAR"))
    fid3 = get_drive_id(getval(row, "Evidencia de la foto de BIPAY"))

    popup = f"""
    <b>Sucursal:</b> {getval(row, 'SUCURSAL:')}<br>
    <b>Tipo:</b> {getval(row, 'Tipo de usuario:')}<br>
    <b>Usuario:</b> {getval(row, 'Usuario: AC/AD')}<br>
    <b>Código:</b> {getval(row, 'Rellenar el Código')}<br>
    <b>Chips:</b> {getval(row, 'Cantidad de chips entregados')}<br><br>
    {img_block(fid1)}
    {img_block(fid2)}
    {img_block(fid3)}
    """

    folium.Marker(
        location=[row["Latitud (LAT.)"], row["Longitud (LONG.)"]],
        popup=popup
    ).add_to(m)

st_folium(m, height=850, width=1500)

df_display = pd.DataFrame({
    "Sucursal": df_map["SUCURSAL:"],
    "Tipo usuario": df_map["Tipo de usuario:"],
    "Usuario": df_map["Usuario: AC/AD"],
    "Código": df_map["Rellenar el Código"],
    "Chips": df_map["Cantidad de chips entregados"],
})

st.dataframe(df_display, use_container_width=True)
