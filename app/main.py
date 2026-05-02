from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import datetime

app = FastAPI(title="Traffic Detection API")

# Setup CORS agar frontend/dashboard nanti bisa akses API ini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Buat Skema Data yang cocok dengan output dari Colab
class TrafficLog(BaseModel):
    waktu_frame: int
    jumlah_kendaraan: int
    status: str

# 2. Buat Endpoint POST untuk menerima data
@app.post("/api/v1/traffic-logs")
async def receive_traffic_data(data: TrafficLog):
    # Dapatkan waktu saat ini
    waktu_sekarang = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Nanti di sini kita masukkan logika simpan ke Database (PostgreSQL/Supabase)
    # Untuk sementara, kita print dulu di terminal VSCode
    print(f"[{waktu_sekarang}] Data Diterima dari AI Worker: Frame {data.waktu_frame} | {data.jumlah_kendaraan} kendaraan | Status: {data.status}")
    
    return {
        "message": "Data berhasil diterima dan dicatat", 
        "data_masuk": data
    }

# Endpoint bantuan untuk cek apakah server hidup
@app.get("/")
async def root():
    return {"message": "Traffic Detection API is running!"}