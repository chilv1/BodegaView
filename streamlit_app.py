import streamlit as st
import pandas as pd
import folium
import re
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRSN9y26MSLRftqr2_On7MEOJ4h4L1o1I_ZXsHfoF1F0qY7Mjnx0bX3A7sxJ7Hz_f02E-gkMxY1t9M_/pub?gid=393036172&single=true&output=csv"

# ============================================================
# LẤY DRIVE FILE ID TỪ NHIỀU DẠNG URL
# ============================================================
def get_drive_id(url: str) -> str:
    if not isinstance(url, str):
        return ""
    url = url.strip()

    # .../open?id=<ID>
    if "open?id=" in url:
        return url.split("open?id=")[1]

    # .../file/d/<ID>/view
    m = re.search(r"/file/d/([^/]+)/", url)
    if m:
        return m.group(1)

    # ...uc?export=view&id=<ID>
    if "uc?export=view&id=" in url:
        return url.split("uc?export=view&id=")[1]

    return ""


# ============================================================
# LOAD CSV
# ============================================================
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

# dùng index để tạo id duy nhất cho mỗi popup
for idx, row in df_map.reset_index(drop=True).iterrows():
    marker_id = f"m{idx}"

    img_ids = []
    for field in ["fotoporta", "fotoimplement", "fotobipay"]:
        fid = get_drive_id(row.get(field, ""))
        if fid:
            img_ids.append(fid)

    # tạo slide HTML, ban đầu display:none để JS bật lên đúng cái
    slides_html = ""
    for fid in img_ids:
        slides_html += f"""
        <div class="slide-{marker_id}" style="display:none;">
            <a target="_blank" href="https://drive.google.com/uc?export=view&id={fid}">
                <img src="https://drive.google.com/thumbnail?id={fid}"
                     style="width:260px; border:1px solid #ccc;">
            </a>
        </div>
        """

    popup = f"""
    <b>Sucursal:</b> {row['sucursal']}<br>
    <b>Tipo:</b> {row['tipouser']}<br>
    <b>Usuario:</b> {row['usercode']}<br>
    <b>Bodega:</b> {row['bodegacode']}<br>
    <b>Chips:</b> {row['chips']}<br><br>

    <div style="position:relative; width:260px; height:340px; overflow:hidden;">
        {slides_html}
        <a style="cursor:pointer; position:absolute; top:50%; left:0;
                  font-size:22px; font-weight:bold;
                  background:rgba(255,255,255,0.8); padding:2px 6px;
                  border-radius:4px;"
           onclick="plusSlides_{marker_id}(-1)">&#10094;</a>
        <a style="cursor:pointer; position:absolute; top:50%; right:0;
                  font-size:22px; font-weight:bold;
                  background:rgba(255,255,255,0.8); padding:2px 6px;
                  border-radius:4px;"
           onclick="plusSlides_{marker_id}(1)">&#10095;</a>
    </div>

    <script>
    var slideIndex_{marker_id} = 1;
    showSlides_{marker_id}(slideIndex_{marker_id});

    function plusSlides_{marker_id}(n) {{
        showSlides_{marker_id}(slideIndex_{marker_id} += n);
    }}

    function showSlides_{marker_id}(n) {{
        var i;
        var slides = document.getElementsByClassName("slide-{marker_id}");
        if (slides.length === 0) return;
        if (n > slides.length) {{ slideIndex_{marker_id} = 1; }}
        if (n < 1) {{ slideIndex_{marker_id} = slides.length; }}
        for (i = 0; i < slides.length; i++) {{
            slides[i].style.display = "none";
        }}
        slides[slideIndex_{marker_id}-1].style.display = "block";
    }}
    </script>
    """

    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(popup, max_width=320),
        tooltip=row["sucursal"],
    ).add_to(m)

st_folium(m, height=750, width=1500)

# ============================================================
# BẢNG DƯỚI MAP (HTML, tránh lỗi Arrow)
# ============================================================
df_display = df_map.applymap(lambda x: "" if pd.isna(x) else str(x))

st.markdown(
    """
<style>
table {
    width: 100%;
    border-collapse: collapse;
}
th, td {
    border: 1px solid #ccc;
    padding: 4px;
    font-size: 13px;
}
tr:nth-child(even) {background-color: #f7f7f7;}
</style>
""",
    unsafe_allow_html=True,
)

st.write(df_display.to_html(index=False, escape=False), unsafe_allow_html=True)
