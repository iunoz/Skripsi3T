import streamlit as st


BACKGROUND_TEXT = """
Tingkat Pengangguran Terbuka (TPT) merupakan salah satu indikator penting untuk mengukur
kondisi ketenagakerjaan di suatu wilayah. Meskipun secara nasional TPT menunjukkan tren
perbaikan, penurunannya tidak terjadi secara merata di seluruh kabupaten/kota. Variasi ini
diduga berkaitan dengan perbedaan kondisi sosial, ekonomi, dan pendidikan di masing-masing
wilayah, terutama pada daerah tertinggal, terdepan, dan terluar (3T) yang memiliki dinamika
ketenagakerjaan berbeda dari wilayah lain. Aplikasi ini memodelkan TPT pada 127
kabupaten/kota daerah 3T periode 2021 - 2025 menggunakan Regresi LASSO yang diselesaikan
dengan algoritma LARS, untuk mengidentifikasi indikator yang paling berpengaruh sekaligus
menyediakan simulasi prediksi TPT bagi masyarakat maupun pemerintah.
"""

TPT_OVERVIEW_TEXT = """
TPT adalah persentase jumlah penganggur terhadap jumlah angkatan kerja, yaitu penduduk usia
15 tahun ke atas yang tidak bekerja dan sedang mencari pekerjaan, mempersiapkan usaha, merasa
tidak mungkin mendapat pekerjaan, atau sudah diterima bekerja tetapi belum mulai bekerja.
Data TPT diperoleh dari Survei Angkatan Kerja Nasional (Sakernas) oleh Badan Pusat Statistik.
Pada Agustus 2025, TPT Indonesia tercatat sebesar 4,85 persen atau sekitar 7,46 juta orang.
Menariknya, Provinsi Nusa Tenggara Timur yang memiliki daerah tertinggal terbanyak justru
mencatat TPT 3,31 persen, jauh di bawah Jawa Barat yang mencapai 6,77 persen.
"""

REGIONS_3T = [
    (
        "Daerah Tertinggal",
        "Kabupaten yang wilayah dan masyarakatnya kurang berkembang dibandingkan daerah lain "
        "dalam skala nasional. Daerah tertinggal ditetapkan melalui Peraturan Presiden Nomor 63 "
        "Tahun 2020 berdasarkan perekonomian, sumber daya manusia, sarana prasarana, keuangan "
        "daerah, aksesibilitas, dan karakteristik daerah.",
    ),
    (
        "Daerah Terdepan",
        "Kabupaten/kota yang berkaitan langsung dengan kawasan perbatasan negara, yaitu yang "
        "memuat Pusat Kegiatan Strategis Nasional (PKSN) atau Kecamatan Perbatasan Prioritas "
        "(KPP), atau termasuk Kawasan Afirmasi berlabel \"Daerah Terdepan\" pada Perpres "
        "Nomor 12 Tahun 2025.",
    ),
    (
        "Daerah Terluar",
        "Kabupaten/kota yang memiliki minimal satu Pulau-Pulau Kecil Terluar (PPKT), yaitu pulau "
        "dengan luas kurang dari 2.000 km² yang menjadi titik terluar penentu batas wilayah laut "
        "Indonesia, berdasarkan Keputusan Presiden Nomor 6 Tahun 2017.",
    ),
]

MODULES = [
    ("pages/prediksi.py", "Prediksi"),
    ("pages/evaluasi.py", "Evaluasi"),
    ("pages/peta.py", "Peta"),
    ("pages/tentang.py", "Tentang Program"),
]


st.markdown("# Beranda", text_alignment="center", anchors=False)
st.space("medium")

title, text = st.columns([1, 3], vertical_alignment="center", gap="large")
with title:
    st.markdown("### Latar Belakang", text_alignment="center", anchors=False)
with text, st.container(key="garis_kiri"):
    st.markdown(BACKGROUND_TEXT, text_alignment="justify")
st.space("large")

text, title = st.columns([3, 1], vertical_alignment="center", gap="large")
with text, st.container(key="garis_kanan"):
    st.markdown(TPT_OVERVIEW_TEXT, text_alignment="justify")
with title:
    st.markdown("### Gambaran Umum TPT", text_alignment="center", anchors=False)
st.space("large")

st.markdown("### Apa itu Daerah 3T?", text_alignment="center", anchors=False)
for column, (name, description) in zip(st.columns(3), REGIONS_3T):
    with column, st.container(border=True, key=f"kartu_3t_{name.split()[-1].lower()}"):
        st.markdown(f"##### {name}", text_alignment="center", anchors=False)
        st.markdown(description)
st.space("large")

st.markdown("### Modul Aplikasi", text_alignment="center", anchors=False)
for column, (page, label) in zip(st.columns(4), MODULES):
    with column, st.container(key=f"kartu_modul_{page.split('/')[-1][:-3]}"):
        st.page_link(page, label=label, width="stretch")
