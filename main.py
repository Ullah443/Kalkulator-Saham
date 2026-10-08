import google.generativeai as genai
from PIL import Image
import streamlit as st

# ==========================================
# KONFIGURASI API KEY & HALAMAN
# ==========================================
# API Key sudah terpasang secara otomatis
GOOGLE_API_KEY = (
    "AQ.Ab8RN6JF-A1YoSEYz06vAgSIM24dpIuk79imwAwfCa3HxpXYUg"
)

genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(
    page_title="Kalkulator Swing Trading & Analisis Saham", layout="centered"
)

st.title("📈 Kalkulator Swing Trading & AI Assistant")
st.markdown(
    "Aplikasi analisis swing trading dengan target rasio **Risk/Reward 1:2**"
    " (Stop Loss 5% & Take Profit 10%), dilengkapi fitur ekstraksi"
    " *screenshot* dan ringkasan berita fundamental."
)

st.divider()

# ==========================================
# BAGIAN 1: UPLOAD SCREENSHOT & OCR AI
# ==========================================
st.subheader("📸 1. Ekstraksi Harga dari Screenshot (Opsional)")
uploaded_file = st.file_uploader(
    "Unggah screenshot chart trading Anda", type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
  image = Image.open(uploaded_file)
  st.image(image, caption="Screenshot Berhasil Diunggah", use_column_width=True)

  if st.button("🔍 Baca Harga dari Screenshot"):
    with st.spinner("Sedang menganalisis gambar dengan AI..."):
      try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([
            image,
            "Ekstrak angka harga saham utama yang tertera pada gambar ini"
            " (contoh: 3130 atau 3010). Berikan HANYA angka murninya saja"
            " tanpa teks atau simbol mata uang.",
        ])

        result_text = response.text.strip()
        cleaned_text = "".join(
            c for c in result_text if c.isdigit() or c == "."
        )

        if cleaned_text:
          detected_price = float(cleaned_text)
          st.success(f"Harga Berhasil Terdeteksi: Rp{detected_price:,.0f}")
          st.session_state["entry_price"] = detected_price
        else:
          st.warning(
              "Gagal membaca angka dengan jelas. Silakan masukkan secara"
              " manual."
          )
      except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca gambar: {e}")

st.divider()

# ==========================================
# BAGIAN 2: KALKULATOR SWING TRADING
# ==========================================
st.subheader("📊 2. Kalkulator Risiko & Imbal Hasil")

# Mengambil nilai entry dari hasil OCR atau default BBRI (3130)
default_entry = st.session_state.get("entry_price", 3130.0)

col1, col2 = st.columns(2)
with col1:
  entry_price = st.number_input(
      "Rencana Harga Beli (Entry)",
      value=float(default_entry),
      step=10.0,
      format="%.2f",
  )
with col2:
  capital = st.number_input(
      "Total Modal / Dana (Rp)",
      value=10000000.0,
      step=500000.0,
      format="%.0f",
  )

st.markdown("### Pengaturan Persentase (Target Rasio 1:2)")
col3, col4 = st.columns(2)
with col3:
  # Default diset ke 5% untuk Stop Loss
  sl_pct = st.slider(
      "Stop Loss (%)", min_value=1.0, max_value=10.0, value=5.0, step=0.5
  )
with col4:
  # Default diset ke 10% agar rasionya 1:2
  tp_pct = st.slider(
      "Take Profit (%)", min_value=2.0, max_value=20.0, value=10.0, step=0.5
  )

# Kalkulasi Matematis
sl_price = entry_price * (1 - sl_pct / 100)
tp_price = entry_price * (1 + tp_pct / 100)
risk_per_share = entry_price - sl_price
reward_per_share = tp_price - entry_price
ratio = reward_per_share / risk_per_share if risk_per_share > 0 else 0

st.divider()
st.subheader("💡 Hasil Perhitungan & Rekomendasi Harga")

res_col1, res_col2, res_col3 = st.columns(3)
with res_col1:
  st.metric(
      label="Batas Cut Loss (Stop Loss)",
      value=f"Rp{sl_price:,.2f}",
      delta=f"-{sl_pct}%",
      delta_color="inverse",
  )
with res_col2:
  st.metric(
      label="Target Jual (Take Profit)",
      value=f"Rp{tp_price:,.2f}",
      delta=f"+{tp_pct}%",
  )
with res_col3:
  st.metric(label="Risk / Reward Ratio", value=f"1 : {ratio:.2f}")

st.info(
    "💡 **Catatan Swing Trading:** Pastikan *slider* Stop Loss berada di angka"
    " **5%** dan Take Profit di angka **10%** agar Anda selalu mendapatkan"
    " rasio keuntungan 1:2 yang ideal."
)

st.divider()

# ==========================================
# BAGIAN 3: RINGKASAN BERITA & FUNDAMENTAL
# ==========================================
st.subheader("📰 3. Ringkasan Berita & Fundamental Emiten")

ticker_input = st.text_input(
    "Masukkan Kode Saham (contoh: BBRI.JK):", value="BBRI.JK"
)

if st.button("🔍 Cek Berita & Sentimen Terbaru"):
  with st.spinner(
      f"Menganalisis berita dan fundamental untuk {ticker_input}..."
  ):
    try:
      model = genai.GenerativeModel("gemini-1.5-flash")
      response = model.generate_content(
          f"Berikan ringkasan analisis fundamental singkat dan sentimen"
          f" berita terbaru untuk saham {ticker_input} di Bursa Efek"
          f" Indonesia (BEI). Fokus pada prospek jangka pendek untuk swing"
          f" trading dan poin-poin penting bagi investor."
      )

      st.markdown("### 📊 Hasil Analisis Berita & Fundamental:")
      st.write(response.text)

    except Exception as e:
      st.error(f"Gagal mengambil data berita: {e}")
