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

# ============================
# TẢI CSV
# ============================
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

# Đổi tên cột
df.rename(columns={
    "latitud (lat.)": "lat",
    "longitud (long.)": "lon",
    "sucursal:": "sucursal",
    "tipo de usuario:": "tipouser",
    "cantidadd e chips entregados": "chips",
    "cantidad de chips entregados": "chips",
    "código de usuario ac/ad": "usercode",
    "código de la bodega (ab, nb, pdv)": "bodegacode",
    "evidencia porta chips": "fotoporta",
    "evidencia de la implementar": "fotoimplement",
    "evidencia de la foto de bipay": "fotobipay"
}, inplace=True)

df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
df["chips"] = pd.to_numeric(df["chips"], errors="coerce").fillna(0).astype(int)

df = df.dropna(subset=["lat", "lon"])

# ============================
# FILTER UI
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
# TẠO MAP
# ============================
st.write(f"### 🧭 Số điểm hiển thị trên bản đồ: {len(df_map)}")

m = folium.Map(location=[df_map["lat"].mean(), df_map["lon"].mean()], zoom_start=6)
marker_cluster = MarkerCluster().add_to(m)

# tạo ID cho từng điểm
df_map["row_id"] = df_map.index

for _, row in df_map.iterrows():
    fid1 = get_drive_id(row.get("fotoporta", ""))
    fid2 = get_drive_id(row.get("fotoimplement", ""))
    fid3 = get_drive_id(row.get("fotobipay", ""))

    color = "green" if row["tipouser"] == "AC" else "red"
    icon = "user" if row["tipouser"] == "AC" else "shopping-cart"

    popup = f"""
    <b>Sucursal:</b> {row['sucursal']}<br>
    <b>Tipo:</b> {row['tipouser']}<br>
    <b>Usuario:</b> {row['usercode']}<br>
    <b>Bodega:</b> {row['bodegacode']}<br>
    <b>Chips:</b> {row['chips']}<br><br>

    <b><u>(Click marker sẽ highlight dòng bên dưới)</u></b><br><br>

    <div style="max-height:380px; overflow-y:auto; padding-right:4px;">
        {img_block(fid1)}
        {img_block(fid2)}
        {img_block(fid3)}
    </div>
    """

    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(popup, max_width=280),
        tooltip=f"{row['usercode']}",
        icon=folium.Icon(color=color, icon=icon, prefix="fa"),
    ).add_to(marker_cluster)

clicked = st_folium(m, height=750, width=1500)

# ============================
# TẠO BẢNG DƯỚI MAP
# ============================
df_display = df_map[["row_id","sucursal","tipouser","usercode","bodegacode","chips","lat","lon"]].copy()
df_display = df_display.applymap(lambda x: "" if pd.isna(x) else str(x))

# CSS highlight hàng
st.markdown("""
<style>
tr.highlight { background-color: yellow !important; }
</style>
""", unsafe_allow_html=True)

st.write(df_display.to_html(index=False, escape=False), unsafe_allow_html=True)

