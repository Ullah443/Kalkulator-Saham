import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Alat Valuasi & Swing Trading Saham", layout="centered")

st.title("📈 Alat Valuasi & Swing Trading Saham")
st.markdown("---")

# Input Kode Saham
kode = st.text_input("Masukkan Kode Saham (contoh: BBRI, BMRI, ASII, BBCA):", "BBRI").upper()
ticker = f"{kode}.JK"

if kode:
    saham = yf.Ticker(ticker)
    info = saham.info

    # Ambil data otomatis dari internet (Pastikan Harga Saat Ini terpanggil)
    harga = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose") or info.get("open", 0)
    eps_auto = info.get("trailingEps") or info.get("epsTrailingTwelveMonths", 0)
    bvps_auto = info.get("bookValue") or info.get("bookValuePerShare", 0)
    per = info.get("trailingPE") or info.get("forwardPE", 0)
    
    div_yield = info.get("dividendYield", 0)
    div_yield_persen = (div_yield * 100) if div_yield and div_yield < 1 else (div_yield if div_yield else 0.0)

    # --- TABS MENU UTAMA ---
    tab1, tab2 = st.tabs(["🎯 Valuasi Jangka Panjang", "⚡ Alat Swing Trading"])

    with tab1:
        # [BAGIAN INI TIDAK BERUBAH, TETAP SEPERTI KODE SEBELUMNYA]
        st.subheader(f"📊 Ringkasan Fundamental: {kode}")
        # ... (silakan salin kode ringkasan fundamental dari versi sebelumnya)

    with tab2:
        st.subheader(f"⚡ Analisis Teknikal & Swing Trading: {kode}")
        
        # Ambil data histori untuk indikator teknikal (periode 3 bulan)
        hist = saham.history(period="3mo")
        if not hist.empty:
            # Hitung RSI 14 hari (standar)
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
                    st.error("🔴 Kondisi: OVERBOUGHT / Jenuh Beli (Hati-hati Koreksi)")
                else:
                    st.warning("🟡 Kondisi: NORMAL / Sideways")

            with col_t2:
                st.metric(label="Support Terdekat (3 Bln)", value=f"Rp{support:,.0f}")
                st.metric(label="Resistance Terdekat (3 Bln)", value=f"Rp{resistance:,.0f}")

            st.markdown("---")
            st.subheader("🛡️ Kalkulator Risk-to-Reward & Stop Loss")
            
            # --- PERBAIKAN PENTING DI SINI ---
            # Gunakan harga pasar yang sudah diambil di atas sebagai default value
            # Pastikan 'harga' bukan 0 atau None sebelum dimasukkan ke input
            harga_pasar = float(harga) if harga else 0.0
            harga_masuk = st.number_input("Rencana Harga Beli (Entry):", value=harga_pasar, step=10.0)
            
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
        # Ambil data histori 1 tahun
        hist_1y = saham.history(period="1y")
        if not hist_1y.empty:
            # --- PERBAIKAN GRAFIK PENTING DI SINI ---
            # Ganti 'Close' dengan nama kolom yang benar untuk grafik sumbu y yang benar.
            # Biasanya st.line_chart secara otomatis menggunakan indeks (tanggal) sebagai sumbu x.
            # Jika gagal, gunakan st.line_chart(hist_1y[['Close']]) secara eksplisit.
            st.line_chart(hist_1y.rename(columns={'Close': 'Harga Penutupan'}))
        else:
            st.info("Data grafik historis belum tersedia.")
    except Exception:
        st.warning("Gagal memuat grafik historis.")
