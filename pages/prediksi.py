import json
import numpy as np
import streamlit as st

from base import FILE_MODEL



VARIABLE_SETTINGS = {
    "RLS": {
        "label": "Rata-rata Lama Sekolah",
        "unit": "tahun",
        "min": 1.0,
        "max": 13.0,
        "step": 0.1,
        "default": 7.8,
        "format": "%.1f",
        "multiplier": 1, # pengubah satuan tampilan ke satuan data (misal juta rupiah ke rupiah)
    },
    "HLS": {
        "label": "Harapan Lama Sekolah",
        "unit": "tahun",
        "min": 3.0,
        "max": 16.0,
        "step": 0.1,
        "default": 12.4,
        "format": "%.1f",
        "multiplier": 1,
    },
    "log_PDRB_Kapita": {
        "label": "PDRB per Kapita",
        "unit": "ribu rupiah",
        "min": 6000,
        "max": 900000,
        "step": 1000,
        "default": 41000,
        "format": "%d",
        "multiplier": 1,
    },
    "UMK": {
        "label": "Upah Minimum Kabupaten/Kota",
        "unit": "juta rupiah",
        "min": 1.90,
        "max": 5.10,
        "step": 0.01,
        "default": 3.14,
        "format": "%.2f",
        "multiplier": 1000000,  # data UMK dalam rupiah
    },
    "Pengeluaran_Kapita": {
        "label": "Pengeluaran per Kapita Disesuaikan",
        "unit": "ribu rupiah/tahun",
        "min": 3900,
        "max": 20000,
        "step": 10,
        "default": 8870,
        "format": "%d",
        "multiplier": 1,
    },
    "TPAK": {
        "label": "Tingkat Partisipasi Angkatan Kerja",
        "unit": "%",
        "min": 40.0,
        "max": 100.0,
        "step": 0.1,
        "default": 72.6,
        "format": "%.1f",
        "multiplier": 1,
    },
    "log_Kepadatan_Penduduk": {
        "label": "Kepadatan Penduduk",
        "unit": "jiwa/km²",
        "min": 1,
        "max": 1500,
        "step": 1,
        "default": 57,
        "format": "%d",
        "multiplier": 1,
    },
    "log_Jumlah_Penduduk": {
        "label": "Jumlah Penduduk",
        "unit": "ribu jiwa",
        "min": 20,
        "max": 2700,
        "step": 1,
        "default": 182,
        "format": "%d",
        "multiplier": 1000,  # data jumlah penduduk dalam jiwa
    },
    "log_Penduduk_Miskin": {
        "label": "Jumlah Penduduk Miskin",
        "unit": "ribu jiwa",
        "min": 1.0,
        "max": 260.0,
        "step": 0.1,
        "default": 25.1,
        "format": "%.1f",
        "multiplier": 1,
    },
}


@st.cache_data  # file cukup dibaca sekali, tidak setiap kali halaman dimuat ulang
def load_model():
    with open(FILE_MODEL, encoding="utf-8") as file:
        return json.load(file)


def replace_dot_with_comma(text):
    return text.replace(".", ",")


def copy_from_slider(variable_name):
    # slider digeser, maka kotak angka ikut berubah
    st.session_state["kotak_" + variable_name] = st.session_state["slider_" + variable_name]


def copy_from_box(variable_name):
    # kotak angka diisi, maka slider ikut berubah
    st.session_state["slider_" + variable_name] = st.session_state["kotak_" + variable_name]


def to_model_scale(variable_name, display_value):
    settings = VARIABLE_SETTINGS[variable_name]

    # ubah ke satuan data, misal 3,14 juta rupiah menjadi 3.140.000 rupiah
    value = display_value * settings["multiplier"]

    # model memakai data Versi 2, jadi variabel berawalan log_ harus di-log (ln) dulu
    if variable_name.startswith("log_"):
        value = np.log(value)

    return value


def show_variable_input(number, variable_name):
    settings = VARIABLE_SETTINGS[variable_name]
    slider_key = "slider_" + variable_name
    box_key = "kotak_" + variable_name

    # isi nilai awal hanya saat halaman pertama kali dibuka
    if slider_key not in st.session_state:
        st.session_state[slider_key] = settings["default"]
        st.session_state[box_key] = settings["default"]

    name_column, box_column, unit_column = st.columns(
        [5, 3, 2],
        vertical_alignment="center",
    )

    with name_column:
        st.markdown(":gray-badge[" + str(number) + "] **" + settings["label"] + "**")

    with box_column:
        st.number_input(
            settings["label"],
            min_value=settings["min"],
            max_value=settings["max"],
            step=settings["step"],
            format=settings["format"],
            key=box_key,
            on_change=copy_from_box,   # samakan slider setelah kotak diisi
            args=[variable_name],
            label_visibility="collapsed",
        )

    with unit_column:
        st.caption(settings["unit"])

    # slider di bawahnya
    st.slider(
        settings["label"],
        min_value=settings["min"],
        max_value=settings["max"],
        step=settings["step"],
        format=settings["format"],
        key=slider_key,
        on_change=copy_from_slider,  # samakan kotak angka setelah slider digeser
        args=[variable_name],
        label_visibility="collapsed",
    )

    return st.session_state[slider_key]



model = load_model()

# pisahkan variabel yang lolos seleksi (koefisien bukan nol) dan yang tereliminasi
selected_variables = []
eliminated_variables = []
for variable_name in model["urutan_pengaruh"]:
    if model["koefisien_asli"][variable_name] == 0:
        eliminated_variables.append(variable_name)
    else:
        selected_variables.append(variable_name)

selected_count = str(len(selected_variables))
total_count = str(len(model["prediktor"]))

st.markdown("# Simulasi Prediksi TPT", text_alignment="center", anchors=False)

st.space("medium")

input_column, result_column = st.columns([2, 1])

with input_column:
    with st.container(key="kartu_variabel"):
        st.markdown(
            "##### Variabel terpilih :gray[(" + selected_count + " dari " + total_count + ")]",
            anchors=False,
        )

        # setiap baris berisi dua variabel: nomor ganjil di kiri, nomor genap di kanan
        input_values = {}
        number = 0
        for variable_name in selected_variables:
            number = number + 1

            if number % 2 == 1:
                left_column, right_column = st.columns(2, gap="large")
                target_column = left_column
            else:
                target_column = right_column

            with target_column:
                with st.container(key="blok_" + variable_name):
                    input_values[variable_name] = show_variable_input(number, variable_name)

        # daftar variabel yang tidak lolos seleksi
        with st.container(key="bagian_tereliminasi", horizontal=True, vertical_alignment="center"):
            st.markdown("**Tidak lolos seleksi LASSO:**")
            for variable_name in eliminated_variables:
                st.badge(VARIABLE_SETTINGS[variable_name]["label"], color="gray")

# TPT hasil prediksi = intersep + jumlah (koefisien × nilai input)
predicted_tpt = model["intersep_asli"]
for variable_name in selected_variables:
    model_value = to_model_scale(variable_name, input_values[variable_name])
    predicted_tpt = predicted_tpt + model["koefisien_asli"][variable_name] * model_value

# hitung kontribusi setiap variabel untuk kartu kontribusi: koefisien × (nilai input − rata-rata data latih)
contributions = {}
for variable_name in selected_variables:
    model_value = to_model_scale(variable_name, input_values[variable_name])
    difference = model_value - model["rata_rata_x"][variable_name]
    contributions[variable_name] = model["koefisien_asli"][variable_name] * difference

# TPT tidak mungkin negatif
if predicted_tpt < 0:
    predicted_tpt = 0

with result_column:
    # kartu hasil prediksi
    with st.container(key="kartu_hasil_prediksi"):
        st.markdown("**TPT HASIL PREDIKSI**", text_alignment="center")
        prediction_text = replace_dot_with_comma(f"{predicted_tpt:.2f}")
        st.markdown("# " + prediction_text + "%", text_alignment="center", anchors=False)

    st.space("small")

    # kartu kontribusi tiap variabel
    with st.container(key="kartu_kontribusi"):
        st.markdown("##### Kontribusi tiap variabel", anchors=False)

        for variable_name in selected_variables:
            name_column, value_column = st.columns([3, 1], vertical_alignment="center")

            with name_column:
                st.markdown(VARIABLE_SETTINGS[variable_name]["label"])

            with value_column:
                value = contributions[variable_name]
                value_text = replace_dot_with_comma(f"{value:+.2f}")  # "+" agar tanda selalu tampil
                if value > 0:
                    st.markdown(":red[**" + value_text + "**]", text_alignment="right")
                elif value < 0:
                    st.markdown(":green[**" + value_text + "**]", text_alignment="right")
                else:
                    st.markdown("**" + value_text + "**", text_alignment="right")

