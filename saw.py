"""Mesin hitung SPK pemilihan supplier dengan metode SAW.

Dibuat berdasarkan kasus UMKM Pisang Lumpur pada jurnal:
Sapriadi, Dari, & Ilmawati (2025), TeknoIS vol. 15 no. 2.
Fungsi di sini murni perhitungan (tanpa Streamlit) supaya mudah diuji.
"""
import numpy as np
import pandas as pd

KRITERIA = ["Harga", "Jarak", "Ukuran", "Pembayaran", "Pelayanan"]
KODE = ["C1", "C2", "C3", "C4", "C5"]
BOBOT_JURNAL = [30, 10, 25, 15, 20]  # dalam persen

# Skala nilai kategori (Tabel 5 dan 6 jurnal). Tabel ukuran tidak ada di jurnal;
# nilainya disimpulkan dari data jurnal (Sangat Kecil=1, Sedang=3, Besar=4,
# Sangat Besar=5), sehingga "Kecil" diisi 2.
SKALA_UKURAN = {"Sangat Kecil": 1, "Kecil": 2, "Sedang": 3, "Besar": 4, "Sangat Besar": 5}
SKALA_PEMBAYARAN = {"Tidak Fleksibel": 1, "Kurang Fleksibel": 2, "Cukup Fleksibel": 3,
                    "Fleksibel": 4, "Sangat Fleksibel": 5}
SKALA_PELAYANAN = {"Sangat Buruk": 1, "Buruk": 2, "Cukup Baik": 3, "Baik": 4, "Sangat Baik": 5}

# Data asli jurnal (Tabel 1)
DATA_JURNAL = pd.DataFrame({
    "Supplier": ["Zal", "Feri", "Zikra", "Ijub", "Ilham"],
    "Harga (Rp/kg)": [8500, 7000, 6500, 10000, 9000],
    "Jarak (km)": [7.1, 10.4, 5.7, 6.0, 11.0],
    "Ukuran": ["Sedang", "Sedang", "Sangat Kecil", "Sangat Besar", "Besar"],
    "Pembayaran": ["Cukup Fleksibel", "Fleksibel", "Tidak Fleksibel", "Sangat Fleksibel", "Fleksibel"],
    "Pelayanan": ["Baik", "Sangat Baik", "Cukup Baik", "Sangat Baik", "Baik"],
})

# Matriks nilai persis seperti Tabel 8 jurnal (untuk mode replikasi)
MATRIKS_JURNAL = pd.DataFrame(
    [[3, 4, 3, 3, 4], [4, 3, 3, 4, 5], [4, 5, 1, 1, 3], [3, 4, 5, 5, 5], [3, 3, 4, 4, 4]],
    index=DATA_JURNAL["Supplier"], columns=KODE)


def skor_harga(h):
    """Tabel 3 jurnal. Harga lebih murah -> skor lebih tinggi."""
    if h < 6000: return 5
    if h <= 8000: return 4
    if h <= 10000: return 3
    if h <= 12000: return 2
    return 1


def skor_jarak(j):
    """Tabel 4 jurnal. Jarak lebih dekat -> skor lebih tinggi."""
    if j < 5: return 5
    if j <= 10: return 4
    if j <= 15: return 3
    if j <= 20: return 2
    return 1


def hitung_skor(data: pd.DataFrame) -> pd.DataFrame:
    """Ubah data mentah supplier menjadi skor 1-5 per kriteria."""
    skor = pd.DataFrame({
        "C1": data["Harga (Rp/kg)"].map(skor_harga),
        "C2": data["Jarak (km)"].map(skor_jarak),
        "C3": data["Ukuran"].map(SKALA_UKURAN),
        "C4": data["Pembayaran"].map(SKALA_PEMBAYARAN),
        "C5": data["Pelayanan"].map(SKALA_PELAYANAN),
    })
    skor.index = data["Supplier"].values
    return skor.astype(int)


def normalisasi(skor: pd.DataFrame, jenis) -> pd.DataFrame:
    """Rumus 1 jurnal: benefit = x/max, cost = min/x."""
    r = pd.DataFrame(index=skor.index, columns=skor.columns, dtype=float)
    for kode, j in zip(skor.columns, jenis):
        kolom = skor[kode].astype(float)
        r[kode] = kolom / kolom.max() if j == "benefit" else kolom.min() / kolom
    return r


def hitung_saw(skor: pd.DataFrame, bobot_persen, jenis):
    """Kembalikan (matriks normalisasi, tabel hasil berperingkat)."""
    w = np.array(bobot_persen, dtype=float)
    r = normalisasi(skor, jenis)
    v = r.values @ w
    hasil = pd.DataFrame({"Supplier": skor.index, "Nilai Preferensi (V)": v})
    hasil["Peringkat"] = hasil["Nilai Preferensi (V)"].rank(ascending=False, method="min").astype(int)
    hasil = hasil.sort_values("Peringkat").reset_index(drop=True)
    return r, hasil


def validasi(data: pd.DataFrame):
    """Daftar pesan kesalahan untuk data supplier (kosong jika aman)."""
    err = []
    if len(data) < 2:
        err.append("Minimal ada 2 supplier untuk dibandingkan.")
        return err
    if data["Supplier"].isna().any() or (data["Supplier"].astype(str).str.strip() == "").any():
        err.append("Nama supplier tidak boleh kosong.")
    elif data["Supplier"].duplicated().any():
        err.append("Nama supplier tidak boleh kembar.")
    if data.drop(columns=["Supplier"]).isna().any().any():
        err.append("Masih ada kolom yang kosong. Lengkapi semua data supplier.")
    elif (data["Harga (Rp/kg)"] <= 0).any() or (data["Jarak (km)"] < 0).any():
        err.append("Harga harus lebih dari 0 dan jarak tidak boleh negatif.")
    return err
