import streamlit as st
import pandas as pd
import folium
import re
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRSN9y26MSLRftqr2_On7MEOJ4h4L1o1I_ZXsHfoF1F0qY7Mjnx0bX3A7sxJ7Hz_f02E-gkMxY1t9M_/pub?gid=393036172&single=true&output=csv"


def get_drive_id(url):
    if isinstance(url, str):
        if "open?id=" in url:
            return url.split("open?id=")[1]
        m = re.search(r'/file/d/([^/]+)/', url)
        if m:
            return m.group(1)
        if "uc?export=view&id=" in url:
            return url.split("uc?export=view&id=")[1]
    return ""


@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

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

st.write(f"### 🗺 Số điểm hiển thị trên bản đồ: {len(df_map)}")

m = folium.Map(location=[df_map["lat"].mean(), df_map["lon"].mean()], zoom_start=6)


for _, row in df_map.iterrows():

    imgs = []
    for field in ['fotoporta','fotoimplement','fotobipay']:
        fid = get_drive_id(row.get(field,''))
        if fid:
            imgs.append(fid)

    slides = ""
    for fid in imgs:
        slides += f'<div class="mySlides"><a target="_blank" href="https://drive.google.com/uc?export=view&id={fid}"><img src="https://drive.google.com/thumbnail?id={fid}" style="width: 260px; border:1px solid #ccc;"></a></div>'

    popup = f"""
    <b>Sucursal:</b> {row['sucursal']}<br>
    <b>Tipo:</b> {row['tipouser']}<br>
    <b>Usuario:</b> {row['usercode']}<br>
    <b>Bodega:</b> {row['bodegacode']}<br>
    <b>Chips:</b> {row['chips']}<br><br>

    <div style="position:relative; width:260px; height:340px;">
        {slides}
        <a style="cursor:pointer; position:absolute; top:50%; left:0;" onclick="plusSlides(-1)">&#10094;</a>
        <a style="cursor:pointer; position:absolute; top:50%; right:0;" onclick="plusSlides(1)">&#10095;</a>
    </div>

    <script>
    var slideIndex = 1;
    var slides = document.getElementsByClassName('mySlides');
    showSlides(slideIndex);

    function plusSlides(n) {{
        showSlides(slideIndex += n);
    }}

    function showSlides(n) {{
        if (n > slides.length) {{slideIndex = 1}} 
        if (n < 1) {{slideIndex = slides.length}}
        for (var i = 0; i < slides.length; i++) {{
            slides[i].style.display = "none"; 
        }}
        slides[slideIndex-1].style.display = "block"; 
    }}
    </script>
    """

    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(popup, max_width=320),
        tooltip=row["sucursal"]
    ).add_to(m)


st_folium(m, height=750, width=1500)

