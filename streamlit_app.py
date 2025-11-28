import streamlit as st
import pandas as pd
import folium
import re
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

# ============================
# LINK CSV CHUẨN
# ============================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSs5tRlFEqLz6J-Ubg8Kh3CkYokxMR-bl9VKWCNNSAV4H6KvNDRyGqDTssxh6dbxUpH0NXJyT8Tq430/pub?gid=393036172&single=true&output=csv"

@st.cache_data
def load_data():
    return pd.read_csv(CSV_URL)

df = load_data()
st.write(df.head(5))

df[['Longitud (LONG.)','Latitud (LAT.) ']].dropna().head(10)

# DEBUG — IN CỘT THỰC TẾ
# st.write(df.columns.tolist())

# ============================
# MAPPING CỘT THEO INDEX
# ============================
col_marca = df.columns[0]
col_sucursal = df.columns[1]
col_tipo_usuario = df.columns[2]
col_tipo_negocio = df.columns[3]
col_usuario = df.columns[4]
col_codigo = df.columns[5]
col_long = df.columns[6]
col_lat = df.columns[7]
col_img1 = df.columns[8]
col_img2 = df.columns[9]
col_img3 = df.columns[10]
col_chips = df.columns[11]

# ============================
# ÉP FLOAT CHO LAT / LON
# ============================
df[col_lat] = pd.to_numeric(df[col_lat], errors="coerce")
df[col_long] = pd.to_numeric(df[col_long], errors="coerce")
df = df.dropna(subset=[col_lat, col_long])

# ============================
# FILTER UI
# ============================
with st.sidebar:
    sel_suc = st.selectbox("Sucursal:", ["(All)"] + sorted(df[col_sucursal].dropna().unique()))
    sel_tipo = st.selectbox("Tipo usuario:", ["(All)"] + sorted(df[col_tipo_usuario].dropna().unique()))

df_map = df.copy()
if sel_suc != "(All)":
    df_map = df_map[df_map[col_sucursal] == sel_suc]
if sel_tipo != "(All)":
    df_map = df_map[df_map[col_tipo_usuario] == sel_tipo]

st.write(f"### Số điểm hiển thị: {len(df_map)}")

# ============================
# GET DRIVE ID
# ============================
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

# ============================
# MAP
# ============================
m = folium.Map(
    location=[df[col_lat].mean(), df[col_long].mean()],
    zoom_start=6
)

for _, r in df_map.iterrows():

    fid1 = get_drive_id(r[col_img1])
    fid2 = get_drive_id(r[col_img2])
    fid3 = get_drive_id(r[col_img3])

    popup = f"""
    <b>Sucursal:</b> {r[col_sucursal]}<br>
    <b>Tipo:</b> {r[col_tipo_usuario]}<br>
    <b>Usuario:</b> {r[col_usuario]}<br>
    <b>Chips:</b> {r[col_chips]}<br><br>
    {img_block(fid1)}
    {img_block(fid2)}
    {img_block(fid3)}
    """

    folium.Marker(
        location=[r[col_lat], r[col_long]],
        popup=popup
    ).add_to(m)

st_folium(m, height=850, width=1500)

# ============================
# BẢNG DƯỚI MAP
# ============================
df_display = pd.DataFrame({
    "Sucursal": df_map[col_sucursal],
    "Tipo usuario": df_map[col_tipo_usuario],
    "Usuario": df_map[col_usuario],
    "Chips entregados": df_map[col_chips],
})

st.dataframe(df_display, use_container_width=True)
