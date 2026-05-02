from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import shutil
from pathlib import Path
from typing import List
import json

app = FastAPI(title="Video Clipping API - Simple Version")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Serve static files
app.mount("/output", StaticFiles(directory="output"), name="output")

# In-memory storage for demo
videos_db = {}
clips_db = {}

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface"""
    try:
        with open("templates/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
        <head><title>Video Clipping Tool</title></head>
        <body>
            <h1>Video Clipping Tool</h1>
            <p>Template file not found. Please ensure templates/index.html exists.</p>
        </body>
        </html>
        """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0-simple"}

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Upload a video file (demo version)"""
    try:
        # Generate unique ID
        video_id = str(uuid.uuid4())

        # Create video directory
        video_dir = UPLOAD_DIR / video_id
        video_dir.mkdir(exist_ok=True)

        # Save uploaded file
        file_path = video_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Store in database
        videos_db[video_id] = {
            "video_id": video_id,
            "filename": file.filename,
            "path": str(file_path),
            "status": "uploaded",
            "file_size": os.path.getsize(file_path)
        }

        return {
            "video_id": video_id,
            "filename": file.filename,
            "status": "uploaded",
            "message": "Video uploaded successfully (demo mode - full processing requires additional dependencies)",
            "file_size": videos_db[video_id]["file_size"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/download")
async def download_video(request: dict):
    """Download video from URL (demo version)"""
    try:
        video_id = str(uuid.uuid4())

        # Store in database (demo - no actual download)
        videos_db[video_id] = {
            "video_id": video_id,
            "filename": "downloaded_video.mp4",
            "status": "demo",
            "message": "Demo mode - actual download requires yt-dlp"
        }

        return {
            "video_id": video_id,
            "status": "demo",
            "message": "Demo mode - actual video download requires yt-dlp installation"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_video(request: dict):
    """Analyze video (demo version)"""
    try:
        video_id = request.get("video_id")

        if video_id not in videos_db:
            raise HTTPException(status_code=404, detail="Video not found")

        # Demo analysis results
        analysis_result = {
            "duration": 120.0,  # Demo: 2 minutes
            "audio_analysis": {
                "high_energy_segments": [
                    {"start": 10.0, "end": 25.0},
                    {"start": 45.0, "end": 60.0},
                    {"start": 90.0, "end": 105.0}
                ],
                "avg_energy": 0.5,
                "max_energy": 0.9
            },
            "visual_analysis": {
                "high_motion_segments": [
                    {"timestamp": 15.0, "motion_score": 0.8},
                    {"timestamp": 50.0, "motion_score": 0.7},
                    {"timestamp": 95.0, "motion_score": 0.9}
                ],
                "avg_motion": 0.5,
                "max_motion": 0.9
            },
            "scene_analysis": {
                "scenes": [
                    {"start": 0.0, "end": 30.0, "duration": 30.0},
                    {"start": 30.0, "end": 60.0, "duration": 30.0},
                    {"start": 60.0, "end": 90.0, "duration": 30.0},
                    {"start": 90.0, "end": 120.0, "duration": 30.0}
                ],
                "scene_count": 4
            },
            "interesting_segments": [
                {"start": 10.0, "end": 25.0, "score": 3},
                {"start": 45.0, "end": 60.0, "score": 2},
                {"start": 90.0, "end": 105.0, "score": 3}
            ],
            "recommended_clips": [
                {
                    "start": 8.0,
                    "end": 27.0,
                    "reason": "High activity segment (score: 3)",
                    "estimated_quality": 60
                },
                {
                    "start": 43.0,
                    "end": 62.0,
                    "reason": "High activity segment (score: 2)",
                    "estimated_quality": 40
                },
                {
                    "start": 88.0,
                    "end": 107.0,
                    "reason": "High activity segment (score: 3)",
                    "estimated_quality": 60
                }
            ]
        }

        return {
            "video_id": video_id,
            "analysis": analysis_result,
            "status": "analyzed",
            "message": "Demo analysis - actual analysis requires moviepy, opencv, and scenedetect"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clip")
async def create_clip(request: dict):
    """Create a clip (demo version)"""
    try:
        video_id = request.get("video_id")
        start_time = request.get("start_time")
        end_time = request.get("end_time")

        if video_id not in videos_db:
            raise HTTPException(status_code=404, detail="Video not found")

        # Generate clip ID
        clip_id = str(uuid.uuid4())

        # Store in database (demo - no actual clipping)
        clips_db[clip_id] = {
            "clip_id": clip_id,
            "video_id": video_id,
            "start_time": start_time,
            "end_time": end_time,
            "status": "demo",
            "message": "Demo mode - actual clipping requires moviepy and ffmpeg"
        }

        return {
            "clip_id": clip_id,
            "video_id": video_id,
            "status": "demo",
            "message": "Demo mode - actual video clipping requires moviepy and ffmpeg installation"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/clip/{clip_id}")
async def get_clip(clip_id: str):
    """Get a created clip (demo version)"""
    if clip_id not in clips_db:
        raise HTTPException(status_code=404, detail="Clip not found")

    clip_info = clips_db[clip_id]
    if clip_info["status"] == "demo":
        raise HTTPException(
            status_code=400,
            detail="Demo clip - actual video generation requires moviepy and ffmpeg"
        )

    clip_path = OUTPUT_DIR / f"{clip_id}.mp4"
    if not clip_path.exists():
        raise HTTPException(status_code=404, detail="Clip file not found")

    return FileResponse(clip_path, media_type="video/mp4")

@app.get("/videos")
async def list_videos():
    """List all uploaded videos"""
    videos = []
    for video_id, video_info in videos_db.items():
        videos.append({
            "video_id": video_id,
            "filename": video_info.get("filename", "Unknown"),
            "status": video_info.get("status", "unknown"),
            "file_size": video_info.get("file_size", 0)
        })

    return {"videos": videos}

@app.delete("/video/{video_id}")
async def delete_video(video_id: str):
    """Delete a video"""
    try:
        if video_id in videos_db:
            del videos_db[video_id]

        video_dir = UPLOAD_DIR / video_id
        if video_dir.exists():
            shutil.rmtree(video_dir)

        return {"message": "Video deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🎬 Video Clipping Application - Simple Demo Version")
    print("📍 Running at http://localhost:8000")
    print("📝 Note: This is a demo version. Full functionality requires:")
    print("   - moviepy (video processing)")
    print("   - opencv-python (computer vision)")
    print("   - scenedetect (scene detection)")
    print("   - yt-dlp (video download)")
    print("   - librosa (audio analysis)")
    print("🚀 Install with: pip install -r requirements.txt")
    uvicorn.run(app, host="0.0.0.0", port=8000)