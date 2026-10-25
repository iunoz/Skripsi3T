import streamlit as st

st.set_page_config(page_title="Prediksi TPT 3T", layout="wide")
st.logo("assets/logo.svg", size="large")

with open("assets/style.css", encoding="utf-8") as file:
    st.html(f"<style>{file.read()}</style>")

page = st.navigation(
    [
        st.Page("pages/beranda.py", title="Beranda", default=True),
        st.Page("pages/prediksi.py", title="Prediksi"),
        st.Page("pages/evaluasi.py", title="Evaluasi"),
        st.Page("pages/peta.py", title="Peta"),
        st.Page("pages/tentang.py", title="Tentang Program"),
    ],
    position="top",
)
page.run()
