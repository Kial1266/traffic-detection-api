import os
from datetime import datetime, timezone

import cv2
import requests
from ultralytics import YOLO

API_URL = os.getenv("TRAFFIC_API_URL", "http://localhost:8000/api/v1/traffic-logs")
VIDEO_PATH = os.getenv("VIDEO_PATH", "sample.mp4")
MODEL_PATH = os.getenv("YOLO_MODEL", "yolov8n.pt")
FRAME_STRIDE = int(os.getenv("FRAME_STRIDE", "30"))

YOLO_CLASSES = [2, 3, 5, 7]


def build_payload(frame_index: int, jumlah_kendaraan: int) -> dict:
    congestion_status = "Macet" if jumlah_kendaraan > 10 else "Lancar"
    return {
        "waktu_frame": frame_index,
        "jumlah_kendaraan": jumlah_kendaraan,
        "status": congestion_status,
    }


def main() -> None:
    model = YOLO(MODEL_PATH)
    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        raise RuntimeError(f"Unable to open video source: {VIDEO_PATH}")

    try:
        frame_index = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame_index += 1
            if frame_index % FRAME_STRIDE != 0:
                continue

            results = model.predict(frame, classes=YOLO_CLASSES, verbose=False)[0]
            jumlah_kendaraan = len(results.boxes) if results.boxes is not None else 0

            payload = build_payload(frame_index, jumlah_kendaraan)

            try:
                response = requests.post(API_URL, json=payload, timeout=5)
                response.raise_for_status()
            except requests.RequestException as exc:
                print(f"Failed to post traffic log: {exc}")
    finally:
        cap.release()


if __name__ == "__main__":
    main()
