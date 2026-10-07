import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Alat Valuasi Saham Otomatis", layout="centered")

st.title("📈 Alat Valuasi Saham Otomatis")
st.markdown("---")

# Input Kode Saham
kode = st.text_input("Masukkan Kode Saham (contoh: BBRI, BMRI, ASII, BBCA):", "BBRI").upper()
ticker = f"{kode}.JK"

if kode:
    with st.spinner('Sedang mengambil data emiten...'):
        saham = yf.Ticker(ticker)
        info = saham.info

    # Ambil data dengan fallback yang aman agar tidak 0 atau error
    harga = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose", 0)
    eps = info.get("trailingEps", 0)
    bvps = info.get("bookValue", 0)
    per = info.get("trailingPE", 0)
    
    # Penanganan Dividend Yield yang lebih aman
    div_yield = info.get("dividendYield", 0)
    if div_yield:
        div_yield_persen = (div_yield * 100) if div_yield < 1 else div_yield
    else:
        div_yield_persen = 0.0

    # Validasi jika data fundamental tidak ditemukan sama sekali
    if harga == 0 and bvps == 0:
        st.error(f"Data untuk emiten **{kode}** tidak ditemukan. Pastikan penulisan kode benar.")
    else:
        st.subheader(f"📊 Ringkasan Fundamental: {kode}")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Harga Saat Ini", value=f"Rp{harga:,.0f}")
            st.metric(label="EPS (TTM)", value=f"Rp{eps:,.2f}")
        with col2:
            st.metric(label="BVPS (Book Value)", value=f"Rp{bvps:,.2f}")
            st.metric(label="PER Saat Ini", value=f"{per:.2f}x" if per else "N/A")

        st.metric(label="Dividend Yield", value=f"{div_yield_persen:.2f}%")
        st.markdown("---")

        # --- KALKULATOR VALUASI PRESISI ---
        st.subheader("🎯 Kalkulator Valuasi & Harga Wajar")
        
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            pbv_target = st.number_input("Target PBV (x):", value=1.0, step=0.1)
            harga_wajar_pbv = bvps * pbv_target
            st.write(f"Harga Wajar (PBV): **Rp{harga_wajar_pbv:,.2f}**")

        with col_v2:
            # Gunakan EPS wajar, jika negatif set minimal 0 agar kalkulasi tidak ngawur
            eps_asumsi = eps if eps > 0 else 0
            per_target = st.number_input("Target PER (x):", value=15.0, step=1.0)
            harga_wajar_per = eps_asumsi * per_target
            st.write(f"Harga Wajar (PER): **Rp{harga_wajar_per:,.2f}**")

        # Pembobotan Harga Wajar (50% PBV & 50% PER agar seimbang)
        if eps_asumsi > 0:
            rata_harga_wajar = (harga_wajar_pbv * 0.5) + (harga_wajar_per * 0.5)
        else:
            rata_harga_wajar = harga_wajar_pbv # Jika EPS negatif/0, andalkan PBV saja

        # Margin of Safety (MoS)
        mos_persen = st.slider("Diskon Margin of Safety (%):", min_value=0, max_value=50, value=20, step=5)
        harga_beli_ideal = rata_harga_wajar * (1 - (mos_persen / 100))

        st.markdown("---")
        st.metric(label=f"Harga Beli Ideal (dengan MoS {mos_persen}%)", value=f"Rp{harga_beli_ideal:,.2f}")

        # Status Keputusan Investasi
        if harga > harga_beli_ideal:
            st.error(f"**Status {kode}: OVERVALUED / MAHAL** (Harga pasar di atas harga ideal)")
        else:
            st.success(f"**Status {kode}: UNDERVALUED / MURAH** (Layak masuk dalam daftar akumulasi)")

        st.markdown("---")

        # --- GRAFIK HISTORIS HARGA ---
        st.subheader("📉 Grafik Tren Harga (1 Tahun Terakhir)")
        try:
            hist = saham.history(period="1y")
            if not hist.empty:
                st.line_chart(hist['Close'])
            else:
                st.info("Data grafik historis belum tersedia untuk emiten ini.")
        except Exception:
            st.warning("Gagal memuat grafik historis.")
