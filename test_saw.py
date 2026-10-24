import pandas as pd
from saw import *

JENIS_JURNAL = ["cost", "cost", "benefit", "benefit", "benefit"]
JENIS_BENAR = ["benefit"] * 5


def test_replikasi_jurnal():
    _, h = hitung_saw(MATRIKS_JURNAL, BOBOT_JURNAL, JENIS_JURNAL)
    v = dict(zip(h["Supplier"], h["Nilai Preferensi (V)"]))
    assert v == {"Ijub": 97.5, "Ilham": 88.0, "Feri": 79.5, "Zal": 77.5, "Zikra": 48.5}
    assert h.iloc[0]["Supplier"] == "Ijub"


def test_skor_dari_data_mentah_cocok_tabel_jurnal_kecuali_jarak_zikra():
    skor = hitung_skor(DATA_JURNAL)
    selisih = (skor.values != MATRIKS_JURNAL.values)
    assert selisih.sum() == 1
    assert skor.loc["Zikra", "C2"] == 4 and MATRIKS_JURNAL.loc["Zikra", "C2"] == 5


def test_mode_koreksi():
    _, h = hitung_saw(hitung_skor(DATA_JURNAL), BOBOT_JURNAL, JENIS_BENAR)
    v = dict(zip(h["Supplier"], h["Nilai Preferensi (V)"]))
    assert v == {"Ijub": 92.5, "Feri": 84.5, "Ilham": 78.0, "Zal": 72.5, "Zikra": 60.0}


def test_validasi():
    assert validasi(DATA_JURNAL) == []
    assert validasi(DATA_JURNAL.head(1))
    d = DATA_JURNAL.copy(); d.loc[1, "Supplier"] = "Zal"
    assert validasi(d)
