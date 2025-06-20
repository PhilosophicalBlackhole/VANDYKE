#Summary:
#React frontend lets you upload and preview videos.
#Backend receives video, crops a centered square region from every frame, and sends back the processed video.
#Processed video is shown and downloadable from the frontend.

----------------------------------

#Install dependencies:

bash
pip install fastapi uvicorn python-multipart opencv-python-headless
