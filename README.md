# SPK Pemilihan Supplier Pisang (SAW)

Aplikasi Streamlit untuk memilih supplier terbaik dengan metode Simple Additive Weighting,
berdasarkan kasus UMKM Pisang Lumpur pada jurnal Sapriadi, Dari, & Ilmawati (2025), TeknoIS 15(2).

## Menjalankan di komputer
    pip install -r requirements.txt
    streamlit run app.py

## Deploy ke Streamlit Community Cloud
1. Buat repositori GitHub baru, lalu unggah isi folder ini (app.py, saw.py, requirements.txt).
2. Buka https://share.streamlit.io dan masuk dengan akun GitHub.
3. Pilih "Create app", pilih repositori dan branch, isi Main file path dengan `app.py`.
4. Klik Deploy. Aplikasi akan punya alamat publik.

## Struktur
- `app.py`   : tampilan Streamlit
- `saw.py`   : perhitungan SAW (tanpa Streamlit)
- `test_saw.py` : pengujian; jalankan dengan `pytest`
