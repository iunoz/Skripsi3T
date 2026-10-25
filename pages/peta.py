import json
import pandas as pd
import pydeck as pdk
import streamlit as st

from base import FILE_TPT_DATA, FILE_GEOJSON


# rgb
COLOR_LOW = [62, 158, 91]
COLOR_MEDIUM = [242, 194, 48]
COLOR_HIGH = [217, 72, 59]
COLOR_NON_3T = [217, 210, 197]

PERIOD_LIST = [2021, 2022, 2023, 2024, 2025]


# teks peta
TOOLTIP_TEXT = """
<b>{name}</b><br/>
{province}<br/>
{description}
"""


@st.cache_data  # file cukup dibaca sekali, tidak setiap kali halaman dimuat ulang
def load_tpt_data():
    return pd.read_csv(FILE_TPT_DATA)


@st.cache_resource  # file peta cukup dibaca sekali dan disimpan tanpa disalin ulang
def load_geojson():
    with open(FILE_GEOJSON, encoding="utf-8") as file:
        return json.load(file)


def format_percent(value):
    text = f"{value:.2f}"
    text = text.replace(".", ",")
    return text + "%"


@st.cache_data  # kuartil cukup dihitung sekali
def compute_quartiles(tpt_data):
    # q1 dan q3 dihitung dari seluruh data TPT 2021–2025,
    quartiles = {
        "q1": tpt_data["TPT"].quantile(0.25),
        "q3": tpt_data["TPT"].quantile(0.75),
    }
    return quartiles


def get_category(tpt_value, quartiles):
    if tpt_value < quartiles["q1"]:
        return "Rendah"
    if tpt_value <= quartiles["q3"]:
        return "Sedang"
    return "Tinggi"


def get_color(category):
    if category == "Rendah":
        return COLOR_LOW
    if category == "Sedang":
        return COLOR_MEDIUM
    return COLOR_HIGH


def prepare_map_regions(tpt_by_region, quartiles):
    # membuat daftar wilayah baru yang sudah diberi warna dan keterangan TPT
    geojson = load_geojson()

    region_list = []
    for region in geojson["features"]:
        properties = region["properties"]

        if properties["is_3t"]:
            tpt_value = tpt_by_region[properties["nama_dataset"]]
            category = get_category(tpt_value, quartiles)
            color = get_color(category)
            description = "TPT " + format_percent(tpt_value) + " (" + category + ")"
        else:
            color = COLOR_NON_3T
            description = "Bukan daerah 3T"

        new_region = {
            "type": "Feature",
            "geometry": region["geometry"],
            "properties": {
                "name": properties["nama"],
                "province": properties["provinsi"],
                "description": description,
                "color": color,
            },
        }
        region_list.append(new_region)

    return {"type": "FeatureCollection", "features": region_list}


def build_map(colored_geojson):
    region_layer = pdk.Layer(
        "GeoJsonLayer",
        data=colored_geojson,
        get_fill_color="properties.color",  
        get_line_color=[255, 255, 255],     # garis batas wilayah 
        line_width_min_pixels=0.5,
        pickable=True,                      # wilayah dpt menampilkan tooltip
        auto_highlight=True,                # wilayah yang nampilin tooltip menjadi lebih terang
    )

    # posisi awal kamera dpt menangkap seluruh Indonesia terlihat
    initial_view = pdk.ViewState(
        latitude=-2.5,
        longitude=118,
        zoom=3.7,
    )

    return pdk.Deck(
        layers=[region_layer],
        initial_view_state=initial_view,
        map_style=None,  # tanpa peta dasar, hanya batas wilayah
        tooltip={"html": TOOLTIP_TEXT},
    )


def show_tpt_list(five_rows_table):
    for row in five_rows_table.to_dict("records"):
        number_column, name_column, value_column = st.columns(
            [1, 6, 3],
            vertical_alignment="center",
        )
        with number_column:
            st.markdown(str(row["No"]))
        with name_column:
            st.markdown(row["Kabupaten_Kota"])
        with value_column:
            st.markdown("**" + format_percent(row["TPT"]) + "**", text_alignment="right")



tpt_data = load_tpt_data()
quartiles = compute_quartiles(tpt_data)

# teks keterangan warna
q1_text = format_percent(quartiles["q1"])
q3_text = format_percent(quartiles["q3"])
low_label = "Rendah (< " + q1_text + ")"
medium_label = "Sedang (" + q1_text + " - " + q3_text + ")"
high_label = "Tinggi (> " + q3_text + ")"

# judul halaman
st.markdown("# Peta TPT Kabupaten/Kota 3T", text_alignment="center", anchors=False)

st.space("medium")

map_column, info_column = st.columns([3, 1])

# pilihan periode di kolom kanan (dibuat lebih dulu karena nilainya dipakai oleh peta)
with info_column:
    selected_period = st.selectbox(
        "Periode",
        options=PERIOD_LIST,
        index=4,  # set ke periode terakhir (2025)
        key="pilih_periode",  # dipakai style.css untuk mengatur tampilan dropdown
    )

# data TPT untuk periode yang dipilih
period_tpt = tpt_data[tpt_data["Periode"] == selected_period]
tpt_by_region = period_tpt.set_index("Kabupaten_Kota")["TPT"].to_dict()

# kartu peta di kolom kiri
with map_column:
    with st.container(key="kartu_peta"):
        colored_geojson = prepare_map_regions(tpt_by_region, quartiles)
        st.pydeck_chart(
            build_map(colored_geojson),
            height="stretch",  # peta mengisi sisa tinggi kartu, sehingga sama tinggi dengan kolom kanan
        )

        # keterangan warna di bawah peta
        with st.container(key="legenda_peta", horizontal=True, gap="large"):
            st.markdown("**Keterangan**")
            with st.container(key="legenda_rendah", width="content"):
                st.markdown(low_label)
            with st.container(key="legenda_sedang", width="content"):
                st.markdown(medium_label)
            with st.container(key="legenda_tinggi", width="content"):
                st.markdown(high_label)
            with st.container(key="legenda_bukan_3t", width="content"):
                st.markdown("Bukan Daerah 3T")

# kartu lima TPT tertinggi dan terendah di kolom kanan
with info_column:
    st.space("small")

    top_five = period_tpt.sort_values("TPT", ascending=False).head(5)
    top_five.insert(0, "No", range(1, 6))

    with st.container(key="kartu_tpt_tertinggi"):
        st.markdown("##### 5 TPT tertinggi", anchors=False)
        show_tpt_list(top_five)

    st.space("small")

    bottom_five = period_tpt.sort_values("TPT", ascending=True).head(5)
    bottom_five.insert(0, "No", range(1, 6))

    with st.container(key="kartu_tpt_terendah"):
        st.markdown("##### 5 TPT terendah", anchors=False)
        show_tpt_list(bottom_five)
