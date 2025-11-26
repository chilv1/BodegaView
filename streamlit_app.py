import streamlit as st
import pandas as pd
import folium
import re
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRSN9y26MSLRftqr2_On7MEOJ4h4L1o1I_ZXsHfoF1F0qY7Mjnx0bX3A7sxJ7Hz_f02E-gkMxY1t9M_/pub?gid=393036172&single=true&output=csv"


# ============================
# HÀM CONVERT DRIVE IMAGE CHỈNH XÁC
# ============================
def drive_to_image_direct(url):
    if not isinstance(url, str):
        return "https://via.placeholder.com/240?text=no+image"

    # nếu dạng:   https://drive.google.com/file/d/<ID>/view
    m = re.search(r"drive.google.com/file/d/([^/]+)/view", url)
    if m:
        file_id = m.group(1)
        return f"https://drive.google.com/uc?export=view&id={file_id}"

    # nếu dạng:   https://drive.google.com/open?id=<ID>
    if "open?id=" in url:
        file_id = url.split("open?id=")[1]
        return f"https://drive.google.com/uc?export=view&id={file_id}"

    return url


# ============================
# LOAD DATA
# ============================
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

# rename
df.rename(columns={
    "latitud (lat.)": "lat",
    "longitud (long.)": "lon",
    "sucursal:": "sucursal",
    "tipo de usuario:": "tipouser",
    "evidencia porta chips": "fotoporta",
    "evidencia de la implementar": "fotoimplement",
    "evidencia de la foto de bipay": "fotobipay",
    "cantidad de chips entregados": "chips",
    "código de usuario ac/ad": "usercode",
    "código de la bodega (ab, nb, pdv)": "bodegacode",
}, inplace=True)


df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
df = df.dropna(subset=["lat", "lon"])

# ============================
# FILTER
# ============================
col1, col2 = st.columns(2)

with col1:
    suc_list = ["(All)"] + sorted(df["sucursal"].dropna().unique().tolist())
    sel_suc = st.selectbox("Lọc theo Sucursal", suc_list)

with col2:
    tipo_list = ["(All)"] + sorted(df["tipouser"].dropna().unique().tolist())
    sel_tipo = st.selectbox("Lọc theo AC/AD", tipo_list)

df_map = df.copy()

if sel_suc != "(All)":
    df_map = df_map[df_map["sucursal"] == sel_suc]

if sel_tipo != "(All)":
    df_map = df_map[df_map["tipouser"] == sel_tipo]


# ============================
# MAP
# ============================
st.write(f"### 🗺 Số điểm hiển thị trên bản đồ: {len(df_map)}")

m = folium.Map(location=[df_map["lat"].mean(), df_map["lon"].mean()], zoom_start=7)

for _, row in df_map.iterrows():

    img1 = drive_to_image_direct(row.get('fotoporta', ''))
    img2 = drive_to_image_direct(row.get('fotoimplement', ''))
    img3 = drive_to_image_direct(row.get('fotobipay', ''))

    popup = f"""
    <b>Sucursal:</b> {row['sucursal']}<br>
    <b>Tipo:</b> {row['tipouser']}<br>
    <b>Usuario:</b> {row['usercode']}<br>
    <b>Bodega:</b> {row['bodegacode']}<br>
    <b>Chips:</b> {row['chips']}<br><br>

    <img src="{img1}" width="260"><br>
    <img src="{img2}" width="260"><br>
    <img src="{img3}" width="260"><br>
    """

    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(popup, max_width=300),
        tooltip=row["sucursal"]
    ).add_to(m)

st_folium(m, height=750, width=1500)


# ============================
# TABLE
# ============================
df_display = df_map.astype(str)
st.dataframe(df_display, use_container_width=True)
