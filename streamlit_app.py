import streamlit as st
import pandas as pd
import folium
import re
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRSN9y26MSLRftqr2_On7MEOJ4h4L1o1I_ZXsHfoF1F0qY7Mjnx0bX3A7sxJ7Hz_f02E-gkMxY1t9M_/pub?gid=393036172&single=true&output=csv"

# ============================================================
# HÀM XỬ LÝ LINK DRIVE -> LINK ẢNH TRỰC TIẾP
# ============================================================
def convert_drive_link(url):
    if not isinstance(url, str):
        return ""

    # Case 1: drive.google.com/file/d/<ID>/view
    m = re.search(r'drive\.google\.com/file/d/([^/]+)/', url)
    if m:
        file_id = m.group(1)
        return f"https://drive.usercontent.google.com/download?id={file_id}&export=view"

    # Case 2: drive.google.com/open?id=<ID>
    if "drive.google.com/open?id=" in url:
        file_id = url.split("open?id=")[1]
        return f"https://drive.usercontent.google.com/download?id={file_id}&export=view"

    # Case 3: uc?export=view&id=<ID>
    if "uc?export=view&id=" in url:
        file_id = url.split("uc?export=view&id=")[1]
        return f"https://drive.usercontent.google.com/download?id={file_id}&export=view"

    return url


# ============================================================
# LOAD CSV
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

# rename các cột
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


# ============================================================
# CONVERT THÀNH SỐ
# ============================================================
df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
df = df.dropna(subset=["lat", "lon"])

# ============================================================
# FILTER UI
# ============================================================
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


# ============================================================
# MAP
# ============================================================
st.write(f"### 🗺 Số điểm hiển thị trên bản đồ: {len(df_map)}")

m = folium.Map(location=[df_map["lat"].mean(), df_map["lon"].mean()], zoom_start=6)

for _, row in df_map.iterrows():

    img1 = convert_drive_link(row.get('fotoporta', ''))
    img2 = convert_drive_link(row.get('fotoimplement', ''))
    img3 = convert_drive_link(row.get('fotobipay', ''))

    popup = f"""
    <b>Sucursal:</b> {row['sucursal']}<br>
    <b>Tipo:</b> {row['tipouser']}<br>
    <b>Usuario:</b> {row['usercode']}<br>
    <b>Bodega:</b> {row['bodegacode']}<br>
    <b>Chips:</b> {row['chips']}<br><br>
    """

    if img1:
        popup += f'<img src="{img1}" width="260"><br>'
    if img2:
        popup += f'<img src="{img2}" width="260"><br>'
    if img3:
        popup += f'<img src="{img3}" width="260"><br>'

    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(popup, max_width=350),
        tooltip=row["sucursal"]
    ).add_to(m)

st_folium(m, height=750, width=1500)


# ============================================================
# DATAFRAME
# ============================================================
df_display = df_map.applymap(lambda x: str(x) if pd.notnull(x) else "")
st.dataframe(df_display, use_container_width=True)
