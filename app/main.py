import os
from inference_sdk import InferenceHTTPClient
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from database import collection
from models import TrafficAnalysis
import base64

# Note: Keep your API Key secure! Consider using environment variables
# SET-UP
load_dotenv() 
API_KEY = os.getenv ("ROBOFLOW_API_KEY")
app = FastAPI()
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key= API_KEY 
)

@app.post("/upload-gambar/")
async def upload_gambar(file: UploadFile = File(...)):
    content = await file.read()
    base64_image = base64.b64encode(content).decode("utf-8")

    # 1. Collecting data from roboflow
    result = CLIENT.run_workflow(
        workspace_name="15240640s-workspace",
        workflow_id="find-car-vehicle-and-more", 
        images={"image": base64_image}
    )
    
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


    new_entry = await collection.insert_one(analysis_data)   

    analysis_data["_id"] = str(analysis_data["_id"]) 
    return {"id": str(new_entry.inserted_id), "analysis": analysis_data}

@app.get("/analysis")
async def get_all_analysis():
    # Mengambil 100 data terbaru dari MongoDB
    cursor = collection.find().sort("timestamp", -1).limit(100)
    logs = await cursor.to_list(length=100)
    for log in logs:
        log["_id"] = str(log["_id"]) # Convert ObjectId ke string agar JSON aman
    return logs