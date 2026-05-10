import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk  # Tambahkan library ini untuk menggambar garis
import datetime #
import math #
from streamlit_js_eval import get_geolocation

# Pengaturan halaman web
st.set_page_config(page_title="Kalkulator Kiblat", page_icon="🕋")

st.title("🕋 Kalkulator Arah Kiblat Digital")
st.write("Proyek Mata Kuliah: Teknologi Hisab Rukyat")
st.write("Aplikasi ini membantu mencari arah Ka'bah dari lokasi mana pun di bumi.")
st.markdown("---")

# --- FITUR 1: DETEKSI LOKASI (Disederhanakan agar tidak dobel) ---
st.subheader("📍 Tentukan Lokasi Anda")
loc = get_geolocation()

# --- BAGIAN PENGATURAN LOKASI ---
metode = st.radio("Pilih Metode Lokasi:", ["Otomatis (GPS)", "Manual (Input)"])

if metode == "Otomatis (GPS)":
    loc = get_geolocation()
    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        st.success(f"Lokasi Terdeteksi: {lat}, {lon}")
    else:
        st.warning("Menunggu GPS... Kalau lama, pastikan Izin Lokasi di browser sudah 'Allow'.")
        lat, lon = None, None
else:
    # Input manual supaya kalau GPS HP temenmu error, aplikasi tetep jalan
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("Lintang (Latitude):", value=-7.8579, format="%.4f")
    with col2:
        lon = st.number_input("Bujur (Longitude):", value=111.4933, format="%.4f")

# Bungkus rumus perhitungan kamu di dalam 'if' ini biar nggak error pas GPS belum masuk
if lat and lon:
    # --- LANJUTAN RUMUS PERHITUNGAN KAMU DI SINI ---
# --- LOGIKA PERHITUNGAN (Sesuai kode aslimu) ---
    lat_kaaba_deg = 21.4225
    lon_kaaba_deg = 39.8262
    lat_u = np.radians(lat_input)
    lon_u = np.radians(lon_input)
    lat_k = np.radians(lat_kaaba_deg)
    lon_k = np.radians(lon_kaaba_deg)
    delta_lon = lon_k - lon_u

# 1. Rumus Arah Kiblat
    num = np.sin(delta_lon)
    den = (np.cos(lat_u) * np.tan(lat_k)) - (np.sin(lat_u) * np.cos(delta_lon))
    qibla_rad = np.arctan2(num, den)
    qibla_deg = (np.degrees(qibla_rad) + 360) % 360

# 2. Rumus Jarak (Haversine Formula)
    dlon = lon_k - lon_u
    dlat = lat_k - lat_u
    a = np.sin(dlat/2)**2 + np.cos(lat_u) * np.cos(lat_k) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    jarak_km = 6371 * c 

# --- TAMPILAN HASIL ---
col1, col2 = st.columns([1, 1.2]) # col2 agak diperlebar untuk peta

with col1:
    st.markdown("### 📊 Hasil Analisis")
    st.metric(label="Arah Kiblat (Azimut)", value=f"{qibla_deg:.2f}°")
    st.metric(label="Jarak ke Ka'bah", value=f"{jarak_km:.2f} KM")
    
    if 270 <= qibla_deg <= 360:
        ket = "Barat Laut (North-West)"
    elif 180 <= qibla_deg < 270:
        ket = "Barat Daya (South-West)"
    else:
        ket = "Arah lainnya"
    st.info(f"Posisi Ka'bah berada di arah **{ket}** dari lokasi Anda.")

with col2:
    st.markdown("### 🗺️ Visualisasi Jalur")
    
    # 1. BUAT DULU DATANYA (Jangan sampai ketinggalan!)
    df_garis = pd.DataFrame([{
        "start": [lon_input, lat_input],
        "end": [39.8262, 21.4225] # Koordinat Ka'bah
    }])
    
    # 2. BARU GAMBAR PETANYA
    st.pydeck_chart(pdk.Deck(
        map_style=None, # Supaya peta dunianya muncul gratis & stabil
        initial_view_state=pdk.ViewState(
            latitude=lat_input,
            longitude=lon_input,
            zoom=1,
            pitch=0,
        ),
        layers=[
            # Layer Garis Merah
            pdk.Layer(
                'LineLayer',
                data=df_garis,
                get_source_position='start',
                get_target_position='end',
                get_color=[255, 0, 0, 200],
                get_width=5,
            ),
            # Layer Titik Biru di lokasi kamu
            pdk.Layer(
                'ScatterplotLayer',
                data=pd.DataFrame([{'lat': lat_input, 'lon': lon_input}]),
                get_position='[lon, lat]',
                get_color=[0, 128, 255],
                get_radius=200000,
            ),
        ],
    ))
# --- PANDUAN PRAKTEK KOMPAS HP (TIDAK DIUBAH) ---
st.divider()
st.subheader("🧭 Panduan Mengarahkan Kiblat")

col_manual, col_tips = st.columns(2)

with col_manual:
    st.markdown(f"""
    ### 🏃 Cara Mencari Arah:
    1. **Buka Aplikasi Kompas** di HP Anda.
    2. **Cari Angka {qibla_deg:.2f}°**: Putar posisi badan/HP Anda secara perlahan (searah jarum jam) dari arah Utara sampai jarum menunjuk ke angka tersebut.
    3. **Tentukan Garis Lurus**: Jika angka di kompas sudah pas, arah depan HP Anda itulah arah **Kiblat (Ka'bah)**.
    """)

with col_tips:
    st.markdown("""
    ### 📱 Tips Kompas HP:
    * **Posisi HP**: Letakkan HP di telapak tangan secara **mendatar/rata** (horizontal), bukan berdiri.
    * **Kalibrasi**: Jika arah terasa goyang, gerakkan HP Anda membentuk **angka 8** di udara untuk mengatur ulang sensor.
    * **Jauhkan Logam**: Pastikan Anda tidak dekat dengan besi besar, magnet casing, atau laptop karena bisa membuat sensor kompas 'error'.
    """)

st.markdown("---")
st.header("☀️ Bayang Kiblat Harian")

import datetime
import math

# 1. Ambil data hari ini
today = datetime.datetime.now()
day_of_year = today.timetuple().tm_yday

# 2. Data Astronomi (Deklinasi & Eq. of Time)
declination = 23.45 * math.sin(math.radians(360 / 365 * (day_of_year - 81)))
b = math.radians(360 / 364 * (day_of_year - 81))
e_time = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)

# 3. RUMUS MENCARI JAM SORE (Sudut Waktu Matahari di Azimut Kiblat)
# A = Azimut Kiblat (294.45), phi = Lintang, delta = Deklinasi
phi = lat_input
delta = declination
A_rad = math.radians(qibla_deg)
phi_rad = math.radians(phi)
delta_rad = math.radians(delta)

# Mencari sudut waktu (t)
cos_t = (math.tan(phi_rad) / math.tan(A_rad)) - (math.sin(delta_rad) / (math.cos(phi_rad) * math.sin(A_rad)))
# Kita ambil pendekatan jam sore yang bayangannya panjang
# HAPUS BAGIAN ERROR TADI, TERUS TEMPEL INI:

try:
    # 1. Konversi Lintang, Deklinasi, dan Azimut ke Radian
    phi_rad = math.radians(lat_input)
    delta_rad = math.radians(declination)
    A_rad = math.radians(qibla_deg)
    
    # 2. Rumus Sudut Waktu (t) untuk mencari JAM SORE
    cos_t = (math.tan(phi_rad) / math.tan(A_rad)) - (math.sin(delta_rad) / (math.cos(phi_rad) * math.sin(A_rad)))
    
    # 3. Hitung jam sore secara otomatis (WIB)
    t_hour = math.degrees(math.acos(cos_t)) / 15
    jam_sore_desimal = (12 + (105 - lon_input)/15 - e_time/60) + t_hour
    
    jam_s = int(jam_sore_desimal)
    menit_s = int((jam_sore_desimal - jam_s) * 60)
    detik_s = int((((jam_sore_desimal - jam_s) * 60) - menit_s) * 60)

    st.success(f"### 🕒 Waktu Bayang Kiblat: **{jam_s:02d}:{menit_s:02d}:{detik_s:02d} WIB**")
    
    st.write(f"""
    Jam **{jam_s:02d}:{menit_s:02d}** adalah jadwal asli saat matahari berada tepat di arah Ka'bah (**{qibla_deg:.2f}°**). 
    """)

except Exception:
    st.warning("Matahari tidak mencapai posisi tersebut sore ini. Pakai waktu Istiwa (tengah hari) saja ya!")
# Pesan Penutup
st.info(f"💡 **Info Falak:** Angka **{qibla_deg:.2f}°** adalah Azimut Sejati dari arah Utara. Di Indonesia, posisi ini biasanya berada di antara arah Barat dan Utara (Barat Laut).")

st.divider()
st.caption("Rumus: Spherical Trigonometry & Haversine Formula. Dibuat untuk tujuan edukasi Hisab Rukyat.")
