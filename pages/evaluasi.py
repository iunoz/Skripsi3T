import json
import altair as alt
import pandas as pd
import streamlit as st

from base import FILE_MODEL


VARIABLE_NAMES = {
    "RLS": "Rata-rata Lama Sekolah",
    "HLS": "Harapan Lama Sekolah",
    "log_PDRB_Kapita": "PDRB per Kapita",
    "UMK": "Upah Minimum Kabupaten/Kota",
    "Pengeluaran_Kapita": "Pengeluaran per Kapita Disesuaikan",
    "TPAK": "Tingkat Partisipasi Angkatan Kerja",
    "log_Kepadatan_Penduduk": "Kepadatan Penduduk",
    "log_Jumlah_Penduduk": "Jumlah Penduduk",
    "log_Penduduk_Miskin": "Jumlah Penduduk Miskin",
}

CURVE_NOTE = """
Kurva menunjukkan rata-rata MSE validasi Group 5-Fold Cross Validation 
untuk setiap lambda sebagai pembanding.
"""

COEFFICIENT_NOTE = """
Angka sangat kecil ditulis seperti 4,42e-07 = 0,000000442. 
Variabel dengan koefisien nol tereliminasi dari model.
"""


@st.cache_resource  # file cukup dibaca sekali, tidak setiap kali halaman dimuat ulang
def load_model():
    with open(FILE_MODEL, encoding="utf-8") as file:
        return json.load(file)


def replace_dot_with_comma(text):
    return text.replace(".", ",")


def build_cv_curve(model):
    curve = model["kurva_validasi"]

    # tabel titik-titik kurva utk setiap lambda beserta rata-rata MSE-nya
    curve_table = pd.DataFrame({
        "Lambda": curve["lambda"],
        "MSE": curve["mse_rata_rata"],
    })

    # tabel berisi satu baris saja, yaitu lambda terpilih 
    selected_lambda_table = pd.DataFrame({
        "Lambda": [model["lambda_cv_terbaik"]],
    })

    # garis coklat artinya rata-rata MSE di 5 fold untuk setiap lambda 
    mse_line = alt.Chart(curve_table).mark_line(color="#8B5E3C").encode(
        x=alt.X(
            "Lambda",
            scale=alt.Scale(type="log"),  # sumbu lambda memakai skala log
            title="Lambda (skala log)",
        ),
        y=alt.Y(
            "MSE",
            scale=alt.Scale(zero=False),  # sumbu y tidak harus dimulai dari nol
            title="Rata-rata MSE validasi",
        ),
    )

    # garis tegak putus-putus di posisi lambda terpilih
    selected_lambda_line = alt.Chart(selected_lambda_table).mark_rule(
        color="#2B2B2B",
        strokeDash=[4, 4],  # 4 piksel garis, 4 piksel kosong
    ).encode(
        x="Lambda",
    )

    # kedua garis digabung menjadi satu grafik
    chart = mse_line + selected_lambda_line
    chart = chart.properties(height=380)
    return chart


def format_original_beta(coefficient):
    # koefisien nol cukup ditulis 0
    if coefficient == 0:
        return "0"

    # angka sangat kecil (misal UMK) memakai notasi ilmiah agar tidak tertulis 0,0000
    if abs(coefficient) < 0.001:
        return replace_dot_with_comma(f"{coefficient:.2e}")

    return replace_dot_with_comma(f"{coefficient:.4f}")


def build_coefficient_table(model):
    # isi setiap kolom tabel, diisi satu per satu di perulangan
    variables = []
    standard_betas = []
    original_betas = []
    statuses = []

    # satu baris untuk setiap variabel, urut dari pengaruh terbesar
    for variable_name in model["urutan_pengaruh"]:
        standard_coefficient = model["koefisien_standar"][variable_name]
        original_coefficient = model["koefisien_asli"][variable_name]

        variables.append(VARIABLE_NAMES[variable_name])
        standard_betas.append(replace_dot_with_comma(f"{standard_coefficient:.3f}"))
        original_betas.append(format_original_beta(original_coefficient))

        # status ditulis di dalam list karena kolomnya memakai MultiselectColumn
        if standard_coefficient == 0:
            statuses.append(["Tereliminasi"])
        else:
            statuses.append(["Lolos seleksi"])

    table = pd.DataFrame({
        "Variabel": variables,
        "Beta_Standar": standard_betas,
        "Beta_Asli": original_betas,
        "Status": statuses,
    })
    return table



model = load_model()
test_metrics = model["metrik_uji"]

st.markdown("# Evaluasi Model", text_alignment="center", anchors=False)

st.space("medium")

column_1, column_2, column_3, column_4 = st.columns(4)

with column_1:
    with st.container(key="kartu_r2"):
        st.markdown("**R-Squared**", text_alignment="center")
        r2_value = replace_dot_with_comma(f"{test_metrics['R2']:.2f}")
        st.markdown("## " + r2_value, text_alignment="center", anchors=False)

with column_2:
    with st.container(key="kartu_rmse"):
        st.markdown("**RMSE**", text_alignment="center")
        rmse_value = replace_dot_with_comma(f"{test_metrics['RMSE']:.2f}")
        st.markdown("## " + rmse_value, text_alignment="center", anchors=False)

with column_3:
    with st.container(key="kartu_mae"):
        st.markdown("**MAE**", text_alignment="center")
        mae_value = replace_dot_with_comma(f"{test_metrics['MAE']:.2f}")
        st.markdown("## " + mae_value, text_alignment="center", anchors=False)

with column_4:
    with st.container(key="kartu_lambda"):
        st.markdown("**Lambda Terpilih**", text_alignment="center")
        # lambda nilainya kecil, jadi ditampilkan empat angka di belakang koma
        lambda_value = replace_dot_with_comma(f"{model['lambda_cv_terbaik']:.4f}")
        st.markdown("## " + lambda_value, text_alignment="center", anchors=False)

# st.caption("R-Squared, RMSE, dan MAE dihitung dari data uji (20% kabupaten/kota).")

st.space("small")

left_column, right_column = st.columns(2)

with left_column:
    with st.container(key="kartu_validasi_silang"):
        st.markdown("##### Validasi Silang", anchors=False)
        st.altair_chart(build_cv_curve(model))
        st.caption(CURVE_NOTE)

with right_column:
    with st.container(key="kartu_koefisien"):
        st.markdown("##### Koefisien akhir model", anchors=False)

        st.dataframe(
            build_coefficient_table(model),
            column_config={
                "Variabel": st.column_config.TextColumn("Variabel", width="large"),
                "Beta_Standar": st.column_config.TextColumn("β Standar"),
                "Beta_Asli": st.column_config.TextColumn("β Asli"),
                "Status": st.column_config.MultiselectColumn(
                    "Status",
                    options=["Lolos seleksi", "Tereliminasi"],
                    color=["green", "gray"],  # warna label sesuai urutan options
                ),
            },
            hide_index=True,  # sembunyikan indeks bawaan pandas
        )

        st.caption(COEFFICIENT_NOTE)
