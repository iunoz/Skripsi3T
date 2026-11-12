import json
import os
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

from base import FILE_TPT_DATA, FILE_GEOJSON, STATIC_FOLDER, STATIC_URL


# rgb
COLOR_LOW = [62, 158, 91]
COLOR_MEDIUM = [242, 194, 48]
COLOR_HIGH = [217, 72, 59]
COLOR_NON_3T = [217, 210, 197]

PERIOD_LIST = [2022, 2023, 2024, 2025]

# warna sorotan kolom periode terpilih di jendela detail wilayah
COLOR_SELECTED_PERIOD = "#EADBC8"

# variabel yang ditampilkan di jendela detail wilayah
# kolom berawalan log_ dikembalikan ke satuan asli dengan exp() sebelum ditampilkan
DETAIL_VARIABLES = [
    {"column": "TPT", "label": "Tingkat Pengangguran Terbuka", "unit": "%", "decimals": 2},
    {"column": "RLS", "label": "Rata-rata Lama Sekolah", "unit": "tahun", "decimals": 2},
    {"column": "HLS", "label": "Harapan Lama Sekolah", "unit": "tahun", "decimals": 2},
    {"column": "log_PDRB_Kapita", "label": "PDRB per Kapita", "unit": "ribu rupiah", "decimals": 0},
    {"column": "UMK", "label": "Upah Minimum Kabupaten/Kota", "unit": "rupiah", "decimals": 0},
    {"column": "Pengeluaran_Kapita", "label": "Pengeluaran per Kapita Disesuaikan", "unit": "ribu rupiah/tahun", "decimals": 0},
    {"column": "TPAK", "label": "Tingkat Partisipasi Angkatan Kerja", "unit": "%", "decimals": 2},
    {"column": "log_Kepadatan_Penduduk", "label": "Kepadatan Penduduk", "unit": "jiwa/km²", "decimals": 0},
    {"column": "log_Jumlah_Penduduk", "label": "Jumlah Penduduk", "unit": "jiwa", "decimals": 0},
    {"column": "log_Penduduk_Miskin", "label": "Jumlah Penduduk Miskin", "unit": "ribu jiwa", "decimals": 2},
]


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
    # q1 dan q3 dihitung dari seluruh data TPT 2022–2025,
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
                "dataset_name": properties["nama_dataset"],  # nama di data TPT, dipakai jendela detail
                "province": properties["provinsi"],
                "description": description,
                "color": color,
            },
        }
        region_list.append(new_region)

    return {"type": "FeatureCollection", "features": region_list}


@st.cache_data  # file peta setiap periode cukup dibuat sekali
def save_map_file(selected_period, tpt_by_region, quartiles):
    # peta berwarna disimpan ke folder static/ agar browser mengunduhnya sendiri,
    # tidak dikirim ulang dari python setiap kali halaman dijalankan
    colored_geojson = prepare_map_regions(tpt_by_region, quartiles)
    # akhiran _v2 agar browser tidak memakai file lama yang belum berisi dataset_name
    file_name = "peta_tpt_" + str(selected_period) + "_v2.json"

    os.makedirs(STATIC_FOLDER, exist_ok=True)
    with open(STATIC_FOLDER + "/" + file_name, "w", encoding="utf-8") as file:
        json.dump(
            colored_geojson,
            file,
            separators=(",", ":"),  # tanpa spasi agar ukuran file kecil
        )

    # alamat file yang dibaca browser, misalnya app/static/peta_tpt_2025.json
    return STATIC_URL + "/" + file_name


def build_map(map_file_url):
    region_layer = pdk.Layer(
        "GeoJsonLayer",
        id="wilayah",                       # nama layer, dipakai untuk membaca wilayah yang diklik
        data=map_file_url,                  # browser mengunduh file peta dari alamat ini
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


def format_number(value, decimals):
    # format angka Indonesia: titik untuk ribuan, koma untuk desimal (misal 3.166.460 atau 8,28)
    text = f"{value:,.{decimals}f}"
    text = text.replace(",", "#").replace(".", ",").replace("#", ".")
    return text


def build_detail_table(region_data):
    # tabel detail: baris = variabel, kolom = periode
    rows = []
    for variable in DETAIL_VARIABLES:
        row = {"Variabel": variable["label"], "Satuan": variable["unit"]}

        for period in PERIOD_LIST:
            period_row = region_data[region_data["Periode"] == period]
            if len(period_row) == 0:
                row[str(period)] = "-"
                continue

            value = period_row[variable["column"]].iloc[0]
            if variable["column"].startswith("log_"):
                value = np.exp(value)  # kembalikan ke satuan asli
            row[str(period)] = format_number(value, variable["decimals"])

        rows.append(row)

    return pd.DataFrame(rows)


@st.dialog("Detail Kabupaten/Kota", width="large")
def show_region_detail(region_properties, selected_period):
    st.markdown("### " + region_properties["name"], anchors=False)
    st.caption(region_properties["province"])

    dataset_name = region_properties.get("dataset_name")
    if not dataset_name:
        st.info("Wilayah ini bukan daerah 3T, sehingga tidak termasuk data penelitian.")
        return

    region_data = tpt_data[tpt_data["Kabupaten_Kota"] == dataset_name]
    detail_table = build_detail_table(region_data)

    # sorot kolom periode yang sedang dipilih di peta
    selected_column = str(selected_period)
    styled_table = detail_table.style.set_properties(
        subset=[selected_column],
        **{"background-color": COLOR_SELECTED_PERIOD, "font-weight": "bold"},
    )

    st.dataframe(
        styled_table,
        hide_index=True,
        column_config={
            selected_column: st.column_config.TextColumn(selected_column + " (dipilih)"),
        },
    )
    st.caption("Kolom berwarna adalah periode yang sedang dipilih di peta.")


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
        index=3,  # set ke periode terakhir (2025)
        key="pilih_periode",  # dipakai style.css untuk mengatur tampilan dropdown
    )

# data TPT untuk periode yang dipilih
period_tpt = tpt_data[tpt_data["Periode"] == selected_period]
tpt_by_region = period_tpt.set_index("Kabupaten_Kota")["TPT"].to_dict()

# kartu peta di kolom kiri
with map_column:
    with st.container(key="kartu_peta"):
        map_file_url = save_map_file(selected_period, tpt_by_region, quartiles)
        map_event = st.pydeck_chart(
            build_map(map_file_url),
            height="stretch",  # peta mengisi sisa tinggi kartu, sehingga sama tinggi dengan kolom kanan
            on_select="rerun",               # halaman dimuat ulang saat wilayah diklik
            selection_mode="single-object",  # hanya satu wilayah yang bisa dipilih
            key="peta_tpt",
        )

        # buka jendela detail saat wilayah diklik
        clicked_regions = map_event.selection.objects.get("wilayah", [])
        if clicked_regions:
            clicked_properties = clicked_regions[0]["properties"]
            # jendela hanya dibuka sekali per klik, tidak setiap kali halaman dimuat ulang
            # (misalnya saat periode diganti, jendela tidak muncul lagi)
            if st.session_state.get("wilayah_terakhir") != clicked_properties["name"]:
                st.session_state["wilayah_terakhir"] = clicked_properties["name"]
                show_region_detail(clicked_properties, selected_period)
        else:
            st.session_state["wilayah_terakhir"] = None

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
