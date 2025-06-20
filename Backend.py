#Summary:
#React frontend lets you upload and preview videos.
#Backend receives video, crops a centered square region from every frame, and sends back the processed video.
#Processed video is shown and downloadable from the frontend.

----------------------------------

#Install dependencies:

bash
pip install fastapi uvicorn python-multipart opencv-python-headless

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
import shutil
import tempfile
import os
import cv2
import numpy as np

app = FastAPI()

# Allow CORS for local frontend testing (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/process-video")
async def process_video(video: UploadFile = File(...)):
    # Validate uploaded file type
    if not video.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a video.")

    # Create a temp directory to save input/output
    temp_dir = tempfile.mkdtemp()

    input_path = os.path.join(temp_dir, "input_video.mp4")
    output_path = os.path.join(temp_dir, "processed_video.mp4")

    # Save uploaded video to disk
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    # Simple processing: crop center square of each frame
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise HTTPException(status_code=400, detail="Error opening video file.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define output video size (crop center square)
    side_length = min(width, height)
    x_start = (width - side_length) // 2
    y_start = (height - side_length) // 2

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (side_length, side_length))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Crop center square
        cropped_frame = frame[y_start : y_start + side_length, x_start : x_start + side_length]

        out.write(cropped_frame)

    cap.release()
    out.release()

    # Return processed video file as streaming response
    def iterfile():
        with open(output_path, mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(iterfile(), media_type="video/mp4")

# To run: uvicorn backend:app --reload

