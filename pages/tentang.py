import pandas as pd
import streamlit as st

from base import FILE_3T_LIST


ABOUT_MODEL_TEXT = """
Regresi LASSO (Least Absolute Shrinkage and Selection Operator) merupakan regresi linear dengan 
penalti L1 pada besar koefisien. Penalti ini membuat koefisien variabel yang kurang berpengaruh 
menyusut hingga tepat nol, sehingga model sekaligus melakukan seleksi variabel. Hasilnya adalah 
persamaan yang lebih sederhana karena hanya memuat indikator yang benar-benar berkaitan dengan TPT.

Koefisien LASSO diselesaikan dengan algoritma LARS (Least Angle Regression). LARS memasukkan variabel 
ke dalam model satu per satu sesuai korelasinya dengan residual, sehingga seluruh jalur solusi untuk 
setiap nilai lambda dapat dihitung secara efisien.
"""

# teks cara kerja model dibagi per langkah, ditampilkan satu per satu dengan tombol < dan >
# r di depan teks agar tanda \ pada rumus tidak dibaca sebagai karakter khusus python
HOW_MODEL_WORKS_INTRO = r"""
Algoritma LARS dimulai dari $\hat{\mu} = 0$ (seluruh koefisien bernilai nol), lalu mengulang
langkah-langkah berikut.
"""

STEP_1_TEXT = r"""
**Langkah 1. Menghitung korelasi**

Data distandarisasi (Z-score) dan TPT dikurangi rata-ratanya, lalu dihitung korelasi setiap
prediktor dengan galat model saat ini:

$$\hat{c} = X'(y - \hat{\mu})$$
"""

STEP_2_TEXT = r"""
**Langkah 2. Mencari korelasi mutlak terbesar**

$$\hat{C} = \max_j \{|\hat{c}_j|\}$$
"""

STEP_3_TEXT = r"""
**Langkah 3. Membentuk himpunan aktif**

Himpunan aktif $A$ berisi prediktor dengan korelasi mutlak terbesar:

$$X_A = (\cdots \; s_j x_j \; \cdots)_{j \in A}$$

dengan $s_j = \text{sign}(\hat{c}_j)$, $G_A = X_A' X_A$, dan $A_A = (1_A' G_A^{-1} 1_A)^{-1/2}$.
"""

STEP_4_TEXT = r"""
**Langkah 4. Menghitung vektor equiangular**

Vektor equiangular membagi sudut kolom-kolom $X_A$ menjadi sama besar (kurang dari 90 derajat):

$$u_A = X_A w_A \quad \text{dengan} \quad w_A = A_A G_A^{-1} 1_A$$
"""

STEP_5_TEXT = r"""
**Langkah 5. Menghitung vektor produk**

$$a = X' u_A$$
"""

STEP_6_TEXT = r"""
**Langkah 6. Memperbarui model**

Model diperbarui dengan $\hat{\mu}_{A+} = \hat{\mu}_A + \hat{\gamma} u_A$, dengan panjang langkah:

$$\hat{\gamma} = \min_{j \in A^c}{}^{+} \left\{ \frac{\hat{C} - \hat{c}_j}{A_A - a_j}, \frac{\hat{C} + \hat{c}_j}{A_A + a_j} \right\}$$

Tanda $\min^{+}$ berarti nilai positif terkecil dari prediktor $j$ di luar $A$. Prediktor yang
mencapai nilai tersebut masuk ke $A$.
"""

STEP_7_TEXT = r"""
**Langkah 7. Mengulangi**

Langkah 1 sampai 6 diulang hingga semua prediktor terseleksi. Agar hasil LARS sama dengan
solusi LASSO, ditambahkan satu aturan: jika koefisien suatu variabel aktif berganti tanda,
variabel tersebut dikeluarkan dari $A$.
"""

STEP_8_TEXT = r"""
Lambda dengan rata-rata MSE terkecil pada Group 5-Fold Cross Validation dipilih sebagai 
lambda optimal, lalu model akhir dievaluasi dengan R², RMSE, dan MAE.
"""

TOTAL_STEPS = 8


ANSWER_TPT = """
TPT adalah persentase jumlah penganggur terhadap jumlah angkatan kerja. Penganggur adalah
penduduk usia 15 tahun ke atas yang tidak bekerja dan sedang mencari pekerjaan, mempersiapkan
usaha, merasa tidak mungkin mendapat pekerjaan, atau sudah diterima bekerja tetapi belum mulai bekerja.
"""

ANSWER_METHOD = """
Indikator sosial, ekonomi, dan pendidikan cenderung saling berkorelasi, sehingga regresi linear 
biasa menghasilkan koefisien yang tidak stabil. LASSO mengatasinya dengan menyusutkan koefisien 
sekaligus memilih variabel yang paling berpengaruh. LARS dipakai karena mampu menghitung seluruh 
jalur solusi LASSO secara efisien, sehingga pemilihan lambda terbaik lebih mudah dilakukan.
"""

ANSWER_INDICATORS = """
- **Pendidikan:** Rata-rata Lama Sekolah (RLS) dan Harapan Lama Sekolah (HLS)
- **Ekonomi dan ketenagakerjaan:** PDRB per kapita, Upah Minimum Kabupaten/Kota (UMK),
  pengeluaran per kapita disesuaikan, dan Tingkat Partisipasi Angkatan Kerja (TPAK)
- **Kependudukan:** kepadatan penduduk, jumlah penduduk, dan jumlah penduduk miskin
"""

ANSWER_3T = """
Daerah 3T adalah daerah tertinggal, terdepan, dan terluar. Daerah tertinggal adalah kabupaten
yang kurang berkembang dibandingkan daerah lain dalam skala nasional, daerah terdepan berkaitan
langsung dengan kawasan perbatasan negara, dan daerah terluar memiliki pulau kecil terluar yang
menjadi penentu batas wilayah laut Indonesia.
"""

ANSWER_SELECTION = """
Penalti L1 pada LASSO menekan koefisien setiap variabel. Semakin besar lambda, semakin banyak
koefisien yang menyusut hingga tepat nol dan variabel tersebut keluar dari persamaan. Variabel
yang terbuang tidak berarti sama sekali tidak berhubungan dengan TPT, tetapi kontribusinya
terlalu kecil atau sudah terwakili oleh variabel lain yang berkorelasi dengannya.
"""

ANSWER_VARIABLES = """
- **Variabel dependen (Y):** Tingkat Pengangguran Terbuka (TPT) dalam persen
- **Variabel independen (X):** sembilan variabel dari indikator sosial, ekonomi,
  dan pendidikan (lihat jawaban dari pertanyaan *Apa saja indikator yang digunakan?*)
"""


DATA_SOURCE_TEXT = """
Data yang digunakan adalah data sekunder berbentuk data panel 127 kabupaten/kota di daerah 3T
selama lima periode (2022 - 2025).  

Penentuan kabupaten/kota yang termasuk daerah 3T mengacu pada ketetapan pemerintah berikut:
- **Tertinggal:** Peraturan Presiden Nomor 63 Tahun 2020 tentang Penetapan Daerah Tertinggal
  Tahun 2020 - 2024
- **Terdepan:** Kabupaten/kota yang memuat Pusat Kegiatan Strategis Nasional (PKSN) atau 
  Kecamatan Perbatasan Prioritas (KPP), atau termasuk Kawasan Afirmasi berlabel “Daerah Terdepan” 
  pada Lampiran IV Peraturan Presiden Nomor 12 Tahun 2025 tentang RPJMN 2025 - 2029
- **Terluar:** Kabupaten/kota yang memiliki pulau kecil terluar menurut Keputusan Presiden
  Nomor 6 Tahun 2017 tentang Penetapan Pulau-Pulau Kecil Terluar
"""


@st.cache_data  # file cukup dibaca sekali, tidak setiap kali halaman dimuat ulang
def load_3t_list():
    table = pd.read_csv(FILE_3T_LIST)

    category_list = []
    for row in table.to_dict("records"):
        categories = []
        if row["Tertinggal"] == 1:
            categories.append("Tertinggal")
        if row["Terdepan"] == 1:
            categories.append("Terdepan")
        if row["Terluar"] == 1:
            categories.append("Terluar")
        category_list.append(categories)

    table["Kategori_3T"] = category_list

    # nomor urut dimulai dari 1
    table.insert(0, "No", range(1, len(table) + 1))

    return table


left_column, middle_column, right_column = st.columns([1, 2, 1], vertical_alignment="center")

with middle_column:
    with st.container(key="judul_tentang"):
        st.markdown("# Tentang Program", text_alignment="center", anchors=False)

with right_column:
    with st.container(horizontal_alignment="right"):
        selected_section = st.segmented_control(
            "Pilih bagian",
            options=["Model & FAQ", "Daerah 3T & Sumber Data"],
            default="Model & FAQ",
            required=True,                 
            label_visibility="collapsed",  
        )

st.space("large")


if selected_section == "Model & FAQ":

    left_column, right_column = st.columns(2)

    with left_column:
        with st.container(key="kartu_tentang_model"):
            st.markdown("#### Tentang Model", text_alignment="center", anchors=False)
            st.markdown(ABOUT_MODEL_TEXT, text_alignment="justify")

    with right_column:
        with st.container(key="kartu_cara_kerja_model"):
            st.markdown("#### Cara Kerja Model", text_alignment="center", anchors=False)
            # nomor langkah yang sedang ditampilkan disimpan agar tidak hilang saat halaman dimuat ulang
            if "langkah_lars" not in st.session_state:
                st.session_state["langkah_lars"] = 1
            current_step = st.session_state["langkah_lars"]

            # kotak isi langkah dengan tinggi tetap, agar ukuran kartu sama di setiap langkah
            with st.container(
                height=250,   # tinggi kotak dalam piksel; ubah angka ini bila tulisan terpotong
                border=False,
                key="isi_langkah_lars",
            ):
                # isi langkah yang sedang dipilih (kalimat pembuka hanya muncul di langkah pertama)
                if current_step == 1:
                    st.markdown(HOW_MODEL_WORKS_INTRO, text_alignment="justify")
                    st.markdown(STEP_1_TEXT, text_alignment="justify")
                if current_step == 2:
                    st.markdown(STEP_2_TEXT, text_alignment="justify")
                if current_step == 3:
                    st.markdown(STEP_3_TEXT, text_alignment="justify")
                if current_step == 4:
                    st.markdown(STEP_4_TEXT, text_alignment="justify")
                if current_step == 5:
                    st.markdown(STEP_5_TEXT, text_alignment="justify")
                if current_step == 6:
                    st.markdown(STEP_6_TEXT, text_alignment="justify")
                if current_step == 7:
                    st.markdown(STEP_7_TEXT, text_alignment="justify")
                if current_step == 8:
                    st.markdown(STEP_8_TEXT, text_alignment="justify")

            # baris tombol: < di kiri, nomor langkah di tengah, > di kanan
            previous_column, step_number_column, next_column = st.columns(
                [1, 3, 1],
                vertical_alignment="center",
            )
            with previous_column:
                previous_clicked = st.button(
                    "<",
                    key="langkah_sebelumnya",
                    disabled=current_step == 1,  # tidak bisa mundur dari langkah pertama
                )
            with step_number_column:
                st.markdown(f"Langkah {current_step} dari {TOTAL_STEPS}", text_alignment="center")
            with next_column:
                with st.container(horizontal_alignment="right"):
                    next_clicked = st.button(
                        ">",
                        key="langkah_selanjutnya",
                        disabled=current_step == TOTAL_STEPS,  # tidak bisa maju dari langkah terakhir
                    )

            # pindah langkah lalu muat ulang halaman agar isi langkah ikut berganti
            if previous_clicked:
                st.session_state["langkah_lars"] = current_step - 1
                st.rerun()
            if next_clicked:
                st.session_state["langkah_lars"] = current_step + 1
                st.rerun()

    st.space("large")

    # faq
    st.markdown("### Pertanyaan yang Sering Ditanyakan (FAQ)", text_alignment="center", anchors=False)

    with st.container(key="faq"):

        # baris pertama
        column_1, column_2, column_3 = st.columns(3)
        with column_1:
            with st.expander("Apa itu Tingkat Pengangguran Terbuka?"):
                st.markdown(ANSWER_TPT)
        with column_2:
            with st.expander("Mengapa menggunakan metode LARS-LASSO?"):
                st.markdown(ANSWER_METHOD)
        with column_3:
            with st.expander("Apa saja indikator yang digunakan?"):
                st.markdown(ANSWER_INDICATORS)

        # baris kedua
        column_1, column_2, column_3 = st.columns(3)
        with column_1:
            with st.expander("Apa itu Daerah 3T?"):
                st.markdown(ANSWER_3T)
        with column_2:
            with st.expander("Kenapa variabel bisa terseleksi?"):
                st.markdown(ANSWER_SELECTION)
        with column_3:
            with st.expander("Variabel apa saja yang digunakan?"):
                st.markdown(ANSWER_VARIABLES)


if selected_section == "Daerah 3T & Sumber Data":

    list_3t = load_3t_list()

    # kartu tabel daftar kabupaten/kota 3T
    with st.container(key="kartu_daftar_3t"):
        st.markdown("#### Daftar Kabupaten/Kota Daerah 3T", anchors=False)
        st.dataframe(
            list_3t,
            column_order=["No", "Kabupaten_Kota", "Provinsi", "Kategori_3T"], 
            column_config={
                "No": st.column_config.NumberColumn("No", width="small"),
                "Kabupaten_Kota": st.column_config.TextColumn("Kabupaten/Kota"),
                "Provinsi": st.column_config.TextColumn("Provinsi"),
                "Kategori_3T": st.column_config.MultiselectColumn(
                    "Kategori 3T",
                    options=["Tertinggal", "Terdepan", "Terluar"],
                    color="#EADBC8",
                ),
            },
            hide_index=True,  # sembunyikan indeks bawaan pandas (sudah ada kolom No)
            height=420,      
        )

    st.space("medium")

    # kartu sumber data
    with st.container(key="kartu_sumber_data"):
        title_column, label_column = st.columns([2, 1], vertical_alignment="center")

        with title_column:
            st.markdown("#### Sumber Data", anchors=False)

        with label_column:
            with st.container(horizontal=True, horizontal_alignment="right"):
                st.badge("**Periode:** 2022-2025", color="gray")
                st.badge("**Tingkat:** Kabupaten/Kota", color="gray")

        st.markdown(DATA_SOURCE_TEXT, text_alignment="justify")
