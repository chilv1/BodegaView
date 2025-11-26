import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

# ============================
#  URL GOOGLE SHEETS CSV
# ============================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRSN9y26MSLRftqr2_On7MEOJ4h4L1o1I_ZXsHfoF1F0qY7Mjnx0bX3A7sxJ7Hz_f02E-gkMxY1t9M_/pub?gid=393036172&single=true&output=csv"


# ============================
#  HÀM CONVERT LINK ẢNH DRIVE
# ============================
def drive_to_image(url):
    try:
        if "id=" in url:
            file_id = url.split("id=")[1]
            return f"https://drive.google.com/uc?export=view&id={file_id}"
    except:
        pass
    return ""

@st.cache_data
def load_data():
    return pd.read_csv(CSV_URL)

df = load_data()

# ============================
#  CHUẨN HÓA CỘT
# ============================
df = df.rename(columns={
    "Latitud (LAT.)": "lat",
    "Longitud (LONG.)": "lon",
    "SUCURSAL:": "Sucursal",
    "Tipo de usuario:": "TipoUser",
    "EVIDENCIA PORTA CHIPS": "FotoPorta",
    "EVIDENCIA DE LA IMPLEMENTAR": "FotoImplement",
    "Evidencia de la foto de BIPAY": "FotoBipay",
    "Cantidad de chips entregados": "Chips",
    "Código de usuario AC/AD": "UserCode",
    "Código de la bodega (AB, NB, PDV)": "BodegaCode",
})

# Chuyển lat / lon thành số
df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lon"] = pd.to_numeric(df["lon"], errors="coerce")

df = df.dropna(subset=["lat", "lon"])

st.write(f"📍 Tổng số điểm dữ liệu: {len(df)}")

# ============================
#  FILTER UI
# ============================
col1, col2 = st.columns(2)

with col1:
    lista_sucursal = ["(All)"] + sorted(df["Sucursal"].dropna().unique().tolist())
    selected_suc = st.selectbox("Lọc theo Sucursal", lista_sucursal)

with col2:
    lista_tipo = ["(All)"] + sorted(df["TipoUser"].dropna().unique().tolist())
    selected_tipo = st.selectbox("Lọc theo user AC/AD", lista_tipo)


# ============================
#  APPLY FILTERS
# ============================

df_map = df.copy()

if selected_suc != "(All)":
    df_map = df_map[df_map["Sucursal"] == selected_suc]

if selected_tipo != "(All)":
    df_map = df_map[df_map["TipoUser"] == selected_tipo]


# ============================
#  VẼ BẢN ĐỒ
# ============================

m = folium.Map(location=[df["lat"].mean(), df["lon"].mean()], zoom_start=6)

for _, row in df_map.iterrows():

    foto1 = drive_to_image(row["FotoPorta"])
    foto2 = drive_to_image(row["FotoImplement"])
    foto3 = drive_to_image(row["FotoBipay"])

    popup = f"""
    <b>Sucursal:</b> {row['Sucursal']}<br>
    <b>Tipo User:</b> {row['TipoUser']}<br>
    <b>User Code:</b> {row['UserCode']}<br>
    <b>Bodega Code:</b> {row['BodegaCode']}<br>
    <b>Chips entregados:</b> {row['Chips']}<br>
    <hr>
    <img src="{foto1}" width="250"><br>
    <img src="{foto2}" width="250"><br>
    <img src="{foto3}" width="250">
    """

    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(popup, max_width=300),
        tooltip=row["Sucursal"]
    ).add_to(m)


st_folium(m, height=700, width=1500)

# ============================
#  HIỂN THỊ BẢNG
# ============================
st.write("### 📄 Dữ liệu chi tiết (sau filter):")
st.dataframe(df_map)
