import google.generativeai as genai
from PIL import Image
import streamlit as st

# Pastikan Anda sudah menyimpan GEMINI_API_KEY di Streamlit Secrets
# genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.subheader("📸 Ekstraksi Harga Otomatis dari Screenshot")

# Widget untuk upload gambar
uploaded_file = st.file_uploader(
    "Pilih screenshot aplikasi trading Anda...", type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
  image = Image.open(uploaded_file)
  st.image(image, caption="Screenshot Berhasil Diunggah", use_column_width=True)

  if st.button("🔍 Baca Harga dari Screenshot"):
    with st.spinner("Sedang menganalisis gambar..."):
      try:
        # Menggunakan Gemini Flash untuk membaca angka harga di gambar
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([
            image,
            "Ekstrak angka harga saham utama yang tertera pada gambar ini"
            " (contoh: 3130 atau 3010). Berikan HANYA angka murninya saja tanpa"
            " teks atau simbol mata uang.",
        ])

        # Membersihkan hasil teks dari AI
        result_text = response.text.strip()
        price_detected = float(
            result_text.replace(",", "").replace("Rp", "").strip()
        )

        st.success(f"Harga terdeteksi: Rp{price_detected:,.0f}")

        # Masukkan otomatis ke session state untuk kalkulator
        st.session_state["auto_entry"] = price_detected

      except Exception as e:
        st.error(f"Gagal mendeteksi harga: {e}")

# Menggunakan nilai hasil ekstraksi untuk form/kalkulator
default_price = st.session_state.get("auto_entry", 3010.0)
entry_price = st.number_input(
    "Rencana Harga Beli (Entry):", value=float(default_price), step=10.0
)
