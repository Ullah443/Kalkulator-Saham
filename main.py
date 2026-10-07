import streamlit as st
import yfinance as yf

st.title("Alat Valuasi Saham Otomatis")

# Input Kode Saham
kode = st.text_input("Masukkan Kode Saham (contoh: BBRI, TMPO):", "BBRI").upper()
ticker = f"{kode}.JK"  # Kode bursa Indonesia (.JK)

if kode:
    saham = yf.Ticker(ticker)
    info = saham.info

    # Tarik Data Otomatis dari Yahoo Finance
    harga = info.get("currentPrice", info.get("previousClose", 0))
    eps = info.get("trailingEps", 0)
    bvps = info.get("bookValue", 0)

    st.write(f"**Harga Saat Ini:** Rp{harga:,.0f}")
    st.write(f"**EPS TTM:** Rp{eps:,.2f}")
    st.write(f"**BVPS:** Rp{bvps:,.2f}")

    # Form Target PBV
    pbv_target = st.number_input("PBV Target (x):", value=1.0)
    harga_wajar = bvps * pbv_target

    st.metric(label="Harga Wajar (PBV)", value=f"Rp{harga_wajar:,.2f}")

    # Indikator Status Warna
    if harga > harga_wajar:
        st.error(f"**{kode}: OVERVALUED (Mahal)**")
    else:
        st.success(f"**{kode}: UNDERVALUED (Murah)**")
