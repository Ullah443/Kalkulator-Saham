import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Alat Valuasi Saham Otomatis", layout="centered")

st.title("📈 Alat Valuasi Saham Otomatis")
st.markdown("---")

kode = st.text_input("Masukkan Kode Saham (contoh: BBRI, BMRI, ASII, BBCA):", "BBRI").upper()
ticker = f"{kode}.JK"

if kode:
    saham = yf.Ticker(ticker)
    info = saham.info

    # Ambil data dengan lebih banyak opsi alternatif atribut
    harga = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose") or info.get("open", 0)
    eps = info.get("trailingEps") or info.get("epsTrailingTwelveMonths", 0)
    bvps = info.get("bookValue") or info.get("bookValuePerShare", 0)
    per = info.get("trailingPE") or info.get("forwardPE", 0)
    
    div_yield = info.get("dividendYield", 0)
    if div_yield:
        div_yield_persen = (div_yield * 100) if div_yield < 1 else div_yield
    else:
        div_yield_persen = 0.0

    # Tampilkan ringkasan langsung (tidak diblokir total meski ada yang kosong)
    st.subheader(f"📊 Ringkasan Fundamental: {kode}")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Harga Saat Ini", value=f"Rp{harga:,.0f}" if harga else "N/A")
        st.metric(label="EPS (TTM)", value=f"Rp{eps:,.2f}" if eps else "N/A")
    with col2:
        st.metric(label="BVPS (Book Value)", value=f"Rp{bvps:,.2f}" if bvps else "N/A")
        st.metric(label="PER Saat Ini", value=f"{per:.2f}x" if per else "N/A")

    st.metric(label="Dividend Yield", value=f"{div_yield_persen:.2f}%")
    st.markdown("---")

    # --- KALKULATOR VALUASI ---
    st.subheader("🎯 Kalkulator Valuasi & Harga Wajar")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        pbv_target = st.number_input("Target PBV (x):", value=1.0, step=0.1)
        harga_wajar_pbv = (bvps if bvps else 0) * pbv_target
        st.write(f"Harga Wajar (PBV): **Rp{harga_wajar_pbv:,.2f}**")

    with col_v2:
        eps_asumsi = eps if (eps and eps > 0) else 0
        per_target = st.number_input("Target PER (x):", value=15.0, step=1.0)
        harga_wajar_per = eps_asumsi * per_target
        st.write(f"Harga Wajar (PER): **Rp{harga_wajar_per:,.2f}**")

    # Hitung rata-rata wajar yang aman
    if bvps > 0 and eps_asumsi > 0:
        rata_harga_wajar = (harga_wajar_pbv * 0.5) + (harga_wajar_per * 0.5)
    elif bvps > 0:
        rata_harga_wajar = harga_wajar_pbv
    else:
        rata_harga_wajar = 0

    mos_persen = st.slider("Diskon Margin of Safety (%):", min_value=0, max_value=50, value=20, step=5)
    harga_beli_ideal = rata_harga_wajar * (1 - (mos_persen / 100))

    st.markdown("---")
    st.metric(label=f"Harga Beli Ideal (dengan MoS {mos_persen}%)", value=f"Rp{harga_beli_ideal:,.2f}")

    if harga and harga_beli_ideal > 0:
        if harga > harga_beli_ideal:
            st.error(f"**Status {kode}: OVERVALUED / MAHAL**")
        else:
            st.success(f"**Status {kode}: UNDERVALUED / MURAH**")

    st.markdown("---")

    # --- GRAFIK HISTORIS ---
    st.subheader("📉 Grafik Tren Harga (1 Tahun Terakhir)")
    try:
        hist = saham.history(period="1y")
        if not hist.empty:
            st.line_chart(hist['Close'])
        else:
            st.info("Data grafik historis belum tersedia.")
    except Exception:
        st.warning("Gagal memuat grafik historis.")
