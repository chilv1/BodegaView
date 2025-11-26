import streamlit as st
import pandas as pd
import folium
import re
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRSN9y26MSLRftqr2_On7MEOJ4h4L1o1I_ZXsHfoF1F0qY7Mjnx0bX3A7sxJ7Hz_f02E-gkMxY1t9M_/pub?gid=393036172&single=true&output=csv"

# ============================
# CONVERT LINK DRIVE SANG ẢNH
# ============================
def drive_to_image(url):
    if not isinstance(url, str):
        return "https://via.placeholder.com/220?text=no+image"
    
    # Case 1: open?id=
    if "open?id=" in url:
        file_id = url.split("open?id=")[1]
        return f"https://drive.google.com/uc?export=view&id={file_id}"

    # Case 2: file/d/xxxxxx/
    m = re.search(r'/file/d/(.*?)/', url)
    if m:
        file_id = m.group(1)
        return f"https://drive.google.com/uc?export=view&id={file_id}"

    # Case 3: uc?id=
    if "uc?id=" in url:
        file_id = url.split("uc?id=")[1]
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

st.write("### 🧾 Các cột thực tế trong CSV:")
st.write(df.columns.tolist())

# ============================
# RENAME CHUẨN
# ============================
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


# ============================
# CLEAN & CONVERT
# ============================
df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
df = df.dropna(subset=["lat", "lon"])

# ============================
# FILTER UI
# ============================
st.write("### 🔍 Bộ lọc dữ liệu:")

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
# DRAW MAP
# ============================
st.write(f"### 🗺 Số điểm hiển thị trên bản đồ: {len(df_map)}")

m = folium.Map(location=[df_map["lat"].mean(), df_map["lon"].mean()], zoom_start=6)

for _, row in df_map.iterrows():
    foto1 = drive_to_image(row.get("fotoporta", ""))
    foto2 = drive_to_image(row.get("fotoimplement", ""))
    foto3 = drive_to_image(row.get("fotobipay", ""))

    popup = f"""
    <b>Sucursal:</b> {row['sucursal']}<br>
    <b>Tipo:</b> {row['tipouser']}<br>
    <b>Usuario:</b> {row['usercode']}<br>
    <b>Bodega:</b> {row['bodegacode']}<br>
    <b>Chips entregados:</b> {row['chips']}<br><br>

    <img src="{foto1}" width="220" onerror="this.src='https://via.placeholder.com/220?text=no+image';"><br>
    <img src="{foto2}" width="220" onerror="this.src='https://via.placeholder.com/220?text=no+image';"><br>
    <img src="{foto3}" width="220" onerror="this.src='https://via.placeholder.com/220?text=no+image';"><br>
    """

    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(popup, max_width=300),
        tooltip=row["sucursal"]
    ).add_to(m)

st_folium(m, height=750, width=1500)


# ============================
# TABLE VIEW (NO ERROR)
# ============================
st.write("### 📄 Dữ liệu dạng bảng sau khi lọc:")

df_map_display = df_map.copy()
df_map_display = df_map_display.astype(str)
st.dataframe(df_map_display, use_container_width=True)
