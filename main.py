import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Alat Valuasi & Swing Trading Saham", layout="centered")

st.title("📈 Alat Valuasi & Swing Trading Saham")
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
    div_yield_persen = (div_yield * 100) if div_yield and div_yield < 1 else (div_yield if div_yield else 0.0)

    # --- TABS MENU UTAMA ---
    tab1, tab2 = st.tabs(["🎯 Valuasi Jangka Panjang", "⚡ Alat Swing Trading"])

    with tab1:
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

        st.subheader("⚙️ Penyesuaian Data Fundamental (Cadangan)")
        bvps_input = st.number_input("BVPS (Book Value Per Share):", value=float(bvps_auto) if bvps_auto else 0.0, step=10.0)
        eps_input = st.number_input("EPS (Earning Per Share / Laba):", value=float(eps_auto) if eps_auto else 0.0, step=1.0)

        st.markdown("---")
        st.subheader("🎯 Kalkulator Harga Wajar")

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

    with tab2:
        st.subheader(f"⚡ Analisis Teknikal & Swing Trading: {kode}")
        
        # Ambil data histori untuk indikator teknikal
        hist = saham.history(period="3mo")
        if not hist.empty:
            # Hitung RSI 14 hari
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]

            # Support & Resistance sederhana dari 3 bulan terakhir
            support = hist['Low'].min()
            resistance = hist['High'].max()

            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.metric(label="RSI (14 Hari)", value=f"{current_rsi:.2f}")
                if current_rsi < 30:
                    st.success("🟢 Kondisi: OVERSOLD (Potensi Pantulan Naik)")
                elif current_rsi > 70:
                    st.error("🔴 Kondisi: OVERVOLD / Jenuh Beli (Hati-hati Koreksi)")
                else:
                    st.warning("🟡 Kondisi: NORMAL / Sideways")

            with col_t2:
                st.metric(label="Support Terdekat (3 Bln)", value=f"Rp{support:,.0f}")
                st.metric(label="Resistance Terdekat (3 Bln)", value=f"Rp{resistance:,.0f}")

            st.markdown("---")
            st.subheader("🛡️ Kalkulator Risk-to-Reward & Stop Loss")
            
            harga_masuk = st.number_input("Rencana Harga Beli (Entry):", value=float(harga) if harga else 0.0, step=10.0)
            persen_stop_loss = st.slider("Risiko Rugi Maksimal (Stop Loss %):", min_value=1, max_value=10, value=3, step=1)
            persen_target = st.slider("Target Keuntungan (Take Profit %):", min_value=1, max_value=30, value=6, step=1)

            harga_SL = harga_masuk * (1 - (persen_stop_loss / 100))
            harga_TP = harga_masuk * (1 + (persen_target / 100))

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.write(f"🛑 Batas Cut Loss (SL): **Rp{harga_SL:,.2f}**")
            with col_s2:
                st.write(f"🎯 Target Jual (TP): **Rp{harga_TP:,.2f}**")

            risk_reward_ratio = persen_target / persen_stop_loss
            st.info(f"⚖️ Rasio Risiko vs Imbal Hasil (Risk/Reward Ratio): **1 : {risk_reward_ratio:.1f}** (Ideal minimal 1:2)")
        else:
            st.warning("Data historis tidak mencukupi untuk analisis teknikal.")

    st.markdown("---")
    st.subheader("📉 Grafik Tren Harga (1 Tahun Terakhir)")
    try:
        hist_1y = saham.history(period="1y")
        if not hist_1y.empty:
            st.line_chart(hist_1y['Close'])
        else:
            st.info("Data grafik historis belum tersedia.")
    except Exception:
        st.warning("Gagal memuat grafik historis.")
