# LOKASI FILE
# semua lokasi file yang dibaca aplikasi dikumpulkan di sini,
# halaman lain cukup menulis: from base import NAMA_FILE
# lokasi ditulis relatif dari folder utama (tempat main.py dijalankan)


# hasil notebook 03_Pemodelan (koefisien, lambda, metrik, kurva CV)
FILE_MODEL = "models/model_lasso_lars.json"

# data TPT bersih hasil notebook 02_Preprocessing (Versi 1)
FILE_TPT_DATA = "data/excel/preprocessed/data_clean.csv"

# daftar kabupaten/kota 3T beserta provinsi dan kategorinya
FILE_3T_LIST = "data/excel/preprocessed/daftar_3t.csv"

# versi ringan (±2,8 MB) dari notebook preprocessing_geojson bagian 7,
# bentuk wilayah sudah disederhanakan agar peta cepat dimuat di browser
FILE_GEOJSON = "data/geojson_web/kabkota_peta_web.geojson"
