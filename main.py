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

    # Ambil data otomatis dari internet
    harga = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose") or info.get("open", 0)
    eps_auto = info.get("trailingEps") or info.get("epsTrailingTwelveMonths", 0)
    bvps_auto = info.get("bookValue") or info.get("bookValuePerShare", 0)
    per = info.get("trailingPE") or info.get("forwardPE", 0)
    
    div_yield = info.get("dividendYield", 0)
    if div_yield:
        div_yield_persen = (div_yield * 100) if div_yield < 1 else div_yield
    else:
        div_yield_persen = 0.0

    # Tampilkan ringkasan fundamental awal dari yfinance
    st.subheader(f"📊 Ringkasan Fundamental: {kode}")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Harga Saat Ini", value=f"Rp{harga:,.0f}" if harga else "N/A")
        st.metric(label="EPS Otomatis (TTM)", value=f"Rp{eps_auto:,.2f}" if eps_auto else "N/A")
    with col2:
        st.metric(label="BVPS Otomatis", value=f"Rp{bvps_auto:,.2f}" if bvps_auto else "N/A")
        st.metric(label="PER Saat Ini", value=f"{per:.2f}x" if per else "N/A")

    st.metric(label="Dividend Yield", value=f"{div_yield_persen:.2f}%")
    st.markdown("---")

    # --- KOTAK INPUT MANUAL (CADANGAN JIKA YFINANCE BELUM UPDATE) ---
    st.subheader("⚙️ Penyesuaian Data Fundamental")
    st.caption("Gunakan angka otomatis di atas, atau ketik ulang secara manual di bawah jika data belum update / kosong.")

    # Gunakan nilai otomatis sebagai angka bawaan (default) pada input manual
    bvps_input = st.number_input("BVPS (Book Value Per Share):", value=float(bvps_auto) if bvps_auto else 0.0, step=10.0)
    eps_input = st.number_input("EPS (Earning Per Share / Laba):", value=float(eps_auto) if eps_auto else 0.0, step=1.0)

    st.markdown("---")

    # --- KALKULATOR VALUASI & HARGA WAJAR ---
    st.subheader("🎯 Kalkulator Valuasi & Harga Wajar")

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        pbv_target = st.number_input("Target PBV (x):", value=1.0, step=0.1)
        harga_wajar_pbv = bvps_input * pbv_target
        st.write(f"Harga Wajar (PBV): **Rp{harga_wajar_pbv:,.2f}**")

    with col_v2:
        eps_asumsi = eps_input if eps_input > 0 else 0
        per_target = st.number_input("Target PER (x):", value=15.0, step=1.0)
        harga_wajar_per = eps_asumsi * per_target
        st.write(f"Harga Wajar (PER): **Rp{harga_wajar_per:,.2f}**")

    # Hitung rata-rata harga wajar
    if bvps_input > 0 and eps_asumsi > 0:
        rata_harga_wajar = (harga_wajar_pbv * 0.5) + (harga_wajar_per * 0.5)
    elif bvps_input > 0:
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
