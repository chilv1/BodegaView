import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRSN9y26MSLRftqr2_On7MEOJ4h4L1o1I_ZXsHfoF1F0qY7Mjnx0bX3A7sxJ7Hz_f02E-gkMxY1t9M_/pub?gid=393036172&single=true&output=csv"

# ============================  
# HÀM CONVERT ẢNH GOOGLE DRIVE  
# ============================  
def drive_to_image(url):
    if not isinstance(url, str):
        return ""
    if "id=" in url:
        return "https://drive.google.com/uc?export=view&id=" + url.split("id=")[1]
    return url

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

# HIỂN THỊ CÁC CỘT THỰC TẾ
st.write("Cột CSV thực tế:")
st.write(df.columns.tolist())

# ============================  
# RENAME CHUẨN THEO CSV  
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

# CHUYỂN LAT–LON THÀNH SỐ
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
    sel_tipo = st.selectbox("Lọc theo user AC/AD", tipo_list)

df_map = df.copy()

if sel_suc != "(All)":
    df_map = df_map[df_map["sucursal"] == sel_suc]

if sel_tipo != "(All)":
    df_map = df_map[df_map["tipouser"] == sel_tipo]

# ============================  
# MAP  
# ============================  
st.write(f"📍 Số điểm hiển thị trên map: {len(df_map)}")

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

    <img src="{foto1}" width="220"><br>
    <img src="{foto2}" width="220"><br>
    <img src="{foto3}" width="220"><br>
    """

    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(popup, max_width=300),
        tooltip=row["sucursal"]
    ).add_to(m)

st_folium(m, height=750, width=1500)

# ============================  
# HIỂN THỊ BẢNG  
# ============================  
st.write("### Dữ liệu chi tiết (filtered):")
st.dataframe(df_map)
