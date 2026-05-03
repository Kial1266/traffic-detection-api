from inference_sdk import InferenceHTTPClient
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from database import collection
from models import TrafficAnalysis
import base64
import os

# Note: Keep your API Key secure! Consider using environment variables
# SET-UP
load_dotenv() 
API_KEY = os.getenv ("ROBOFLOW_API_KEY")
app = FastAPI()
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key= API_KEY 
)

# SETTING CORSE CHANGE 11:55 01/05/2026
origins = [
    "http://localhost:3000",    #To change react
    "http://127.0.0.1:3000",
    "http://localhost:5173",    # To change Vite/Vue
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allowed address
    allow_credentials=True,
    allow_methods=["*"],               # Allowed all HTTP METHODS (GET, POST, dll)
    allow_headers=["*"],               # Allowed all header to access
)

@app.post("/upload-gambar/")
async def upload_gambar(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, message="File must be an image "  )
    
    try:
        content = await file.read()
        base64_image = base64.b64encode(content).decode("utf-8")
    
        try:
        # 1. Collecting data from roboflow
            result = CLIENT.run_workflow(
            workspace_name="15240640s-workspace",
            workflow_id="find-car-vehicle-and-more", 
            images={"image": base64_image}
    )
        except Exception as e:
            print (f"Roboflow error: {e}")
            raise HTTPException(status_code=502, message= "Cannot Connect to Roboflow Server")

        predictions = result[0]["predictions"]["predictions"]
    
    # 2. Count density and weight
        IMAGE_AREA = 1280 * 720 
        total_area_occupied = 0
        cars = 0
        motorcycles = 0
        vehicles = 0
    
        for p in predictions:
            total_area_occupied += (p['width'] * p['height'])
            if p['class'] == 'car': cars += 1
            if p['class'] == 'motorcycle': motorcycles += 1
            if p['class'] == 'vehicle':  vehicles += 1

        density_percentage = round((total_area_occupied / IMAGE_AREA) * 100, 2)
        status = "Lancar"
        if density_percentage > 30: status = "Macet Parah"
        elif density_percentage > 10: status = "macet Aja"


        analysis_data = {
            "jumlah_kendaraan": len(predictions),
            "density_score": density_percentage,
            "status": status,
            "rincian": {"cars": cars, "motorcycles": motorcycles, "vehicles": vehicles},
            "raw_predictions": predictions
        }

# ERROR HANDLING DATABASE
        try:
                new_entry = await collection.insert_one(analysis_data)   
                analysis_data["_id"] = str(analysis_data["_id"]) 
                return {"id": str(new_entry.inserted_id), "analysis": analysis_data}
        except:
                print(f"Database Error: {e}")
                raise HTTPException(status_code=500, detail="Gagal menyimpan data ke database.")

        return {"status": "success", "data": analysis_data}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        # Menangkap error tak terduga lainnya
        print(f"Unexpected Error: {e}")
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal pada server.")

@app.get("/analysis")
async def get_all_analysis():
    # Mengambil 100 data terbaru dari MongoDB
    cursor = collection.find().sort("timestamp", -1).limit(10)
    logs = await cursor.to_list(length=10)
    for log in logs:
        log["_id"] = str(log["_id"]) # Convert ObjectId ke string agar JSON aman
    return logs
