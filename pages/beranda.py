import altair as alt
import pandas as pd
import streamlit as st

from base import FILE_TPT_DATA


BACKGROUND_TEXT = """
Kondisi ketenagakerjaan di Indonesia umumnya dipantau melalui Tingkat Pengangguran Terbuka
(TPT). Secara nasional TPT terus membaik, tetapi penurunannya tidak merata di seluruh
kabupaten/kota, terutama di daerah tertinggal, terdepan, dan terluar (3T) yang memiliki
dinamika ketenagakerjaan berbeda. Aplikasi ini memodelkan TPT 127 kabupaten/kota 3T periode
2022 - 2025 dengan Regresi LASSO berbasis algoritma LARS, untuk menemukan indikator yang
paling berpengaruh sekaligus menyediakan simulasi prediksi TPT.
"""

TPT_OVERVIEW_TEXT = """
TPT adalah persentase jumlah penganggur terhadap jumlah angkatan kerja, yaitu penduduk usia
15 tahun ke atas yang tidak bekerja dan sedang mencari pekerjaan, mempersiapkan usaha, merasa
tidak mungkin mendapat pekerjaan, atau sudah diterima bekerja tetapi belum mulai bekerja.
Pada Agustus 2025, TPT Indonesia tercatat sebesar 4,85 persen atau sekitar 7,46 juta orang.
Menariknya, Provinsi Nusa Tenggara Timur yang memiliki daerah tertinggal terbanyak justru
mencatat TPT 3,31 persen, jauh di bawah Jawa Barat yang mencapai 6,77 persen.
"""

TERTINGGAL_DESCRIPTION = """
Kabupaten yang wilayah dan masyarakatnya kurang berkembang dibandingkan daerah lain dalam skala
nasional. Daerah tertinggal ditetapkan melalui Peraturan Presiden Nomor 63 Tahun 2020.
"""

TERDEPAN_DESCRIPTION = """
Kabupaten/kota yang berkaitan langsung dengan kawasan perbatasan negara yang memuat Pusat Kegiatan
Strategis Nasional (PKSN) atau Kecamatan Perbatasan Prioritas (KPP), atau termasuk Kawasan Afirmasi
berlabel "Daerah Terdepan" pada Perpres Nomor 12 Tahun 2025.
"""

TERLUAR_DESCRIPTION = """
Kabupaten/kota yang memiliki minimal satu Pulau-Pulau Kecil Terluar (PPKT), yaitu pulau dengan luas
kurang dari 2.000 km² yang menjadi titik terluar penentu batas wilayah laut Indonesia, berdasarkan
Keputusan Presiden Nomor 6 Tahun 2017.
"""

PREDICTION_DESCRIPTION = """
Masukkan nilai variabel yang lolos seleksi LASSO dan lihat TPT hasil prediksi.
"""

EVALUATION_DESCRIPTION = """
R², RMSE, MAE, lambda terpilih, kurva validasi silang, dan koefisien akhir.
"""

MAP_DESCRIPTION = """
Peta kabupaten/kota 3T dengan warna sesuai besaran TPT.
"""

ABOUT_DESCRIPTION = """
Penjelasan lengkap penelitian, sumber data, dan metode.
"""


@st.cache_data  # file cukup dibaca sekali, tidak setiap kali halaman dimuat ulang
def load_average_tpt():
    tpt_data = pd.read_csv(FILE_TPT_DATA)

    # rata-rata TPT semua kabupaten/kota untuk setiap tahun
    average_tpt = tpt_data.groupby("Periode")["TPT"].mean().reset_index()

    # teks angka di atas titik grafik
    labels = []
    for value in average_tpt["TPT"]:
        label = f"{value:.2f}%".replace(".", ",")
        labels.append(label)
    average_tpt["Label"] = labels

    # tahun sebagai teks agar sumbu x tertulis 2021, bukan 2,021
    average_tpt["Tahun"] = average_tpt["Periode"].astype(str)
    return average_tpt


def show_tpt_area_chart(average_tpt):
    st.bar_chart(
        average_tpt,
        x="Tahun",
        y="TPT",
        x_label="Tahun",
        y_label="Rata-rata TPT (%)",
        color="#8B5E3C",  
        height=300,
    )


average_tpt = load_average_tpt()

st.markdown("# Beranda", text_alignment="center", anchors=False)
st.space("medium")

# Baris pertama: latar belakang di kiri, grafik rata-rata TPT di kanan
background_column, image_column = st.columns(2, vertical_alignment="center", gap="large")
with background_column, st.container(key="latar_belakang"):
    st.markdown("### Latar Belakang", anchors=False)
    st.markdown(BACKGROUND_TEXT, text_alignment="justify")
with image_column, st.container(key="image_beranda", horizontal_alignment="right"):
    st.image("assets/pencari_kerja_3t_kiri.svg")
st.space("large")

chart_column, overview_column = st.columns(2, vertical_alignment="center", gap="large")
with chart_column, st.container(key="kartu_grafik_tpt"):
    st.markdown("##### Rata-rata TPT Daerah 3T, 2022 - 2025", anchors=False, text_alignment="center")
    show_tpt_area_chart(average_tpt)
with overview_column, st.container(key="gambaran"):
    st.markdown("### Gambaran Umum TPT", anchors=False , text_alignment="right")
    st.markdown(TPT_OVERVIEW_TEXT, text_alignment="justify")
st.space("large")

st.markdown("### Apa itu Daerah 3T?", text_alignment="center", anchors=False)
underdeveloped_column, frontier_column, outermost_column = st.columns(3)

# Kartu Daerah Tertinggal
with underdeveloped_column, st.container(border=True, key="kartu_3t_tertinggal"):
    # ikon kotak cokelat muda di atas judul daerah
    with st.container(key="ikon_3t_tertinggal"):
        st.markdown(":material/holiday_village:", text_alignment="center")
    st.markdown("##### Daerah Tertinggal", text_alignment="center", anchors=False)
    st.markdown(TERTINGGAL_DESCRIPTION)

# Kartu Daerah Terdepan
with frontier_column, st.container(border=True, key="kartu_3t_terdepan"):
    with st.container(key="ikon_3t_terdepan"):
        st.markdown(":material/flag:", text_alignment="center")
    st.markdown("##### Daerah Terdepan", text_alignment="center", anchors=False)
    st.markdown(TERDEPAN_DESCRIPTION)

# Kartu Daerah Terluar
with outermost_column, st.container(border=True, key="kartu_3t_terluar"):
    with st.container(key="ikon_3t_terluar"):
        st.markdown(":material/beach_access:", text_alignment="center")
    st.markdown("##### Daerah Terluar", text_alignment="center", anchors=False)
    st.markdown(TERLUAR_DESCRIPTION)
st.space("large")

st.markdown("### Modul Aplikasi", text_alignment="center", anchors=False)
prediction_column, evaluation_column, map_column, about_column = st.columns(4)

# Kartu modul Prediksi
with prediction_column, st.container(key="kartu_modul_prediksi"):
    with st.container(key="ikon_modul_prediksi"):
        st.markdown(":material/tune:")
    st.markdown("##### Prediksi", anchors=False)
    st.markdown(PREDICTION_DESCRIPTION)
    with st.container(key="tautan_modul_prediksi"):
        st.page_link("pages/prediksi.py", label="Buka simulasi →")

# Kartu modul Evaluasi
with evaluation_column, st.container(key="kartu_modul_evaluasi"):
    with st.container(key="ikon_modul_evaluasi"):
        st.markdown(":material/analytics:")
    st.markdown("##### Evaluasi", anchors=False)
    st.markdown(EVALUATION_DESCRIPTION)
    with st.container(key="tautan_modul_evaluasi"):
        st.page_link("pages/evaluasi.py", label="Lihat evaluasi →")

# Kartu modul Peta
with map_column, st.container(key="kartu_modul_peta"):
    with st.container(key="ikon_modul_peta"):
        st.markdown(":material/map:")
    st.markdown("##### Peta", anchors=False)
    st.markdown(MAP_DESCRIPTION)
    with st.container(key="tautan_modul_peta"):
        st.page_link("pages/peta.py", label="Buka peta →")

# Kartu modul Tentang Program
with about_column, st.container(key="kartu_modul_tentang"):
    with st.container(key="ikon_modul_tentang"):
        st.markdown(":material/info:")
    st.markdown("##### Tentang Program", anchors=False)
    st.markdown(ABOUT_DESCRIPTION)
    with st.container(key="tautan_modul_tentang"):
        st.page_link("pages/tentang.py", label="Baca selengkapnya →")
