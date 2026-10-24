import pandas as pd
import streamlit as st

import saw

st.set_page_config(page_title="SPK Pemilihan Supplier (SAW)", page_icon="🍌", layout="wide")

JENIS_JURNAL = ["cost", "cost", "benefit", "benefit", "benefit"]
JENIS_KOREKSI = ["benefit"] * 5
MODE_JURNAL = "Replikasi jurnal (skor & aturan asli)"
MODE_KOREKSI = "Hitung dari data mentah (versi koreksi)"

# ---------------------------------------------------------------- sidebar
st.sidebar.header("Pengaturan")
mode = st.sidebar.radio(
    "Mode perhitungan", [MODE_JURNAL, MODE_KOREKSI],
    help="Replikasi jurnal memakai skor dan aturan persis seperti di jurnal. "
         "Versi koreksi menghitung skor dari data mentah dan memperlakukan semua skor sebagai benefit.")

st.sidebar.subheader("Bobot kriteria (%)")
bobot = []
for i, nama in enumerate(saw.KRITERIA):
    bobot.append(st.sidebar.number_input(
        f"{saw.KODE[i]} - {nama}", min_value=0.0, max_value=100.0,
        value=float(saw.BOBOT_JURNAL[i]), step=5.0, key=f"w{i}"))
total = sum(bobot)
if abs(total - 100) > 1e-9:
    st.sidebar.warning(f"Total bobot {total:g}%. Bobot akan dinormalisasi agar jumlahnya 100%.")
bobot_pakai = [b / total * 100 for b in bobot] if total > 0 else None
if st.sidebar.button("Kembalikan bobot ke jurnal"):
    for i in range(5):
        st.session_state[f"w{i}"] = float(saw.BOBOT_JURNAL[i])
    st.rerun()

# ---------------------------------------------------------------- header
st.title("SPK Pemilihan Supplier Pisang Terbaik")
st.caption("Metode Simple Additive Weighting (SAW) - kasus UMKM Pisang Lumpur, "
           "berdasarkan Sapriadi, Dari, & Ilmawati (2025), TeknoIS 15(2).")

tab_data, tab_hasil, tab_langkah, tab_catatan = st.tabs(
    ["1. Data", "2. Hasil keputusan", "3. Langkah hitung", "4. Catatan jurnal"])

# ---------------------------------------------------------------- data
with tab_data:
    if mode == MODE_JURNAL:
        st.subheader("Matriks nilai (Tabel 8 jurnal)")
        st.write("Mode ini memakai skor 1-5 persis seperti jurnal. "
                 "C1 (Harga) dan C2 (Jarak) diperlakukan sebagai **cost**, sisanya **benefit**.")
        skor = saw.MATRIKS_JURNAL.copy()
        jenis = JENIS_JURNAL
        st.dataframe(skor, width="stretch")
        st.caption("Data mentah supplier ada di bawah sebagai rujukan.")
        st.dataframe(saw.DATA_JURNAL, width="stretch", hide_index=True)
        data_ok = True
    else:
        st.subheader("Data supplier")
        st.write("Ubah nilai, tambah baris, atau hapus baris sesuai kebutuhan. "
                 "Skor 1-5 dihitung otomatis dari data ini.")
        if "data" not in st.session_state:
            st.session_state["data"] = saw.DATA_JURNAL.copy()
        if st.button("Kembalikan data ke contoh jurnal"):
            st.session_state["data"] = saw.DATA_JURNAL.copy()
            st.session_state.pop("editor", None)
            st.rerun()
        data = st.data_editor(
            st.session_state["data"], key="editor", num_rows="dynamic",
            width="stretch", hide_index=True,
            column_config={
                "Supplier": st.column_config.TextColumn(required=True),
                "Harga (Rp/kg)": st.column_config.NumberColumn(min_value=1, step=100, format="%d", required=True),
                "Jarak (km)": st.column_config.NumberColumn(min_value=0.0, step=0.1, format="%.1f", required=True),
                "Ukuran": st.column_config.SelectboxColumn(options=list(saw.SKALA_UKURAN), required=True),
                "Pembayaran": st.column_config.SelectboxColumn(options=list(saw.SKALA_PEMBAYARAN), required=True),
                "Pelayanan": st.column_config.SelectboxColumn(options=list(saw.SKALA_PELAYANAN), required=True),
            })
        data = data.reset_index(drop=True)
        errors = saw.validasi(data)
        for e in errors:
            st.error(e)
        data_ok = not errors
        if data_ok:
            skor = saw.hitung_skor(data)
            jenis = JENIS_KOREKSI
            st.subheader("Skor hasil konversi (1-5)")
            st.dataframe(skor, width="stretch")
        with st.expander("Lihat tabel konversi skor"):
            st.markdown(
                "**Harga:** < Rp6.000 = 5; Rp6.000-8.000 = 4; Rp8.100-10.000 = 3; "
                "Rp10.100-12.000 = 2; > Rp12.000 = 1  \n"
                "**Jarak:** < 5 km = 5; 5-10 km = 4; 10,1-15 km = 3; 15,1-20 km = 2; > 20 km = 1  \n"
                "**Ukuran, Pembayaran, Pelayanan:** skala 1-5 dari yang terburuk ke terbaik.  \n"
                "Nilai di antara dua rentang jurnal (mis. Rp8.050) dimasukkan ke rentang di bawahnya.")

can_calc = data_ok and bobot_pakai is not None
if bobot_pakai is None:
    st.warning("Total bobot masih 0. Isi bobot di panel kiri.")

# ---------------------------------------------------------------- hasil
if can_calc:
    r, hasil = saw.hitung_saw(skor, bobot_pakai, jenis)
    terbaik = hasil.iloc[0]
    pemenang = list(hasil.loc[hasil["Peringkat"] == 1, "Supplier"])

with tab_hasil:
    if not can_calc:
        st.info("Lengkapi data pada tab Data terlebih dahulu.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Supplier terbaik", " / ".join(pemenang))
        c2.metric("Nilai preferensi", f"{terbaik['Nilai Preferensi (V)']:.2f}")
        if len(hasil) > 1:
            c3.metric("Selisih dengan peringkat 2",
                      f"{terbaik['Nilai Preferensi (V)'] - hasil.iloc[1]['Nilai Preferensi (V)']:.2f}")
        if len(pemenang) > 1:
            st.warning("Ada nilai yang sama di peringkat 1. Pertimbangkan kriteria lain sebelum memutuskan.")
        else:
            st.success(f"Rekomendasi: **{pemenang[0]}** dipilih sebagai pemasok utama.")
        tampil = hasil.copy()
        tampil["Nilai Preferensi (V)"] = tampil["Nilai Preferensi (V)"].round(2)
        st.dataframe(tampil, width="stretch", hide_index=True)
        st.bar_chart(hasil.set_index("Supplier")["Nilai Preferensi (V)"])
        st.download_button("Unduh hasil (CSV)", tampil.to_csv(index=False).encode("utf-8"),
                           file_name="hasil_saw_supplier.csv", mime="text/csv")
        st.caption("Aplikasi ini membantu keputusan, bukan menggantikan penilaian pemilik usaha.")

# ---------------------------------------------------------------- langkah
with tab_langkah:
    if not can_calc:
        st.info("Lengkapi data pada tab Data terlebih dahulu.")
    else:
        st.markdown("**Rumus normalisasi:** benefit  r = x / max(x); cost  r = min(x) / x  \n"
                    "**Nilai preferensi:** V = jumlah dari (bobot x r)")
        jen = pd.DataFrame({"Kriteria": saw.KRITERIA, "Jenis": jenis,
                            "Bobot dipakai (%)": [round(b, 2) for b in bobot_pakai]}, index=saw.KODE)
        st.markdown("**1. Jenis dan bobot kriteria**")
        st.dataframe(jen, width="stretch")
        st.markdown("**2. Matriks keputusan (skor)**")
        st.dataframe(skor, width="stretch")
        st.markdown("**3. Matriks ternormalisasi (R)**")
        st.dataframe(r.round(3), width="stretch")
        st.markdown("**4. Nilai preferensi (V) dan peringkat**")
        st.dataframe(hasil.round(2), width="stretch", hide_index=True)

# ---------------------------------------------------------------- catatan
with tab_catatan:
    st.subheader("Perbandingan hasil jurnal dan versi koreksi")
    st.markdown(
        "Perhitungan di jurnal bisa direproduksi persis (Ijub 97,5), tetapi ada dua hal yang perlu dicatat:\n\n"
        "1. **Harga dan jarak diperlakukan sebagai cost**, padahal skornya sudah dibalik "
        "(harga murah dan jarak dekat sudah diberi skor tinggi). Akibatnya normalisasi min/x "
        "membalik penilaian untuk dua kriteria ini.\n"
        "2. **Skor jarak Zikra** di jurnal 5, padahal jaraknya 5,7 km yang menurut Tabel 4 jurnal "
        "bernilai 4.\n\n"
        "Tabel di bawah memakai bobot jurnal (30/10/25/15/20) agar bisa dibandingkan langsung.")
    _, h_j = saw.hitung_saw(saw.MATRIKS_JURNAL, saw.BOBOT_JURNAL, JENIS_JURNAL)
    _, h_k = saw.hitung_saw(saw.hitung_skor(saw.DATA_JURNAL), saw.BOBOT_JURNAL, JENIS_KOREKSI)
    banding = h_j.merge(h_k, on="Supplier", suffixes=(" jurnal", " koreksi"))
    banding = banding[["Supplier", "Nilai Preferensi (V) jurnal", "Peringkat jurnal",
                       "Nilai Preferensi (V) koreksi", "Peringkat koreksi"]].round(2)
    st.dataframe(banding.sort_values("Peringkat jurnal"), width="stretch", hide_index=True)
    st.caption("Ijub tetap peringkat 1 pada kedua cara, tetapi urutan di bawahnya berubah "
               "(Feri naik ke peringkat 2, Ilham turun).")
