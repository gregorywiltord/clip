from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import uuid
import shutil
from pathlib import Path
from typing import List, Optional
import asyncio

from video_analyzer import VideoAnalyzer
from video_clipper import VideoClipper

app = FastAPI(title="Video Clipping API")

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
TEMP_DIR = Path("temp")

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Serve static files
app.mount("/output", StaticFiles(directory="output"), name="output")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize analyzers and clippers
analyzer = VideoAnalyzer()
clipper = VideoClipper()

class VideoURLRequest(BaseModel):
    url: str
    analyze: bool = True

class ClipRequest(BaseModel):
    video_id: str
    start_time: float
    end_time: float

class AnalysisRequest(BaseModel):
    video_id: str

@app.get("/")
async def root():
    """Serve the web interface"""
    try:
        html_path = Path("templates/index.html")
        if html_path.exists():
            return HTMLResponse(content=html_path.read_text())
        else:
            return JSONResponse(
                status_code=404,
                content={"error": "Web interface not found"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error serving web interface: {str(e)}"}
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Upload a video file for analysis and clipping"""
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

        return {
            "video_id": video_id,
            "filename": file.filename,
            "status": "uploaded",
            "message": "Video uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/download")
async def download_video(request: VideoURLRequest, background_tasks: BackgroundTasks):
    """Download video from URL"""
    try:
        video_id = str(uuid.uuid4())
        video_dir = UPLOAD_DIR / video_id
        video_dir.mkdir(exist_ok=True)

        # Download video using yt-dlp
        output_path = video_dir / "video.mp4"

        def download_task():
            import yt_dlp
            ydl_opts = {
                'outtmpl': str(output_path),
                'format': 'best[ext=mp4]/best'
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([request.url])

        background_tasks.add_task(download_task)

        return {
            "video_id": video_id,
            "status": "downloading",
            "message": "Video download started"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_video(request: AnalysisRequest):
    """Analyze video to find interesting segments"""
    try:
        video_dir = UPLOAD_DIR / request.video_id
        if not video_dir.exists():
            raise HTTPException(status_code=404, detail="Video not found")

        # Find video file
        video_files = list(video_dir.glob("*.mp4")) + list(video_dir.glob("*.mkv")) + list(video_dir.glob("*.avi"))
        if not video_files:
            raise HTTPException(status_code=404, detail="No video file found")

        video_path = video_files[0]

        # Analyze video
        analysis_result = analyzer.analyze_video(str(video_path))

        return {
            "video_id": request.video_id,
            "analysis": analysis_result,
            "status": "analyzed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clip")
async def create_clip(request: ClipRequest, background_tasks: BackgroundTasks):
    """Create a clip from the video"""
    try:
        video_dir = UPLOAD_DIR / request.video_id
        if not video_dir.exists():
            raise HTTPException(status_code=404, detail="Video not found")

        # Find video file
        video_files = list(video_dir.glob("*.mp4")) + list(video_dir.glob("*.mkv")) + list(video_dir.glob("*.avi"))
        if not video_files:
            raise HTTPException(status_code=404, detail="No video file found")

        video_path = video_files[0]

        # Generate clip ID
        clip_id = str(uuid.uuid4())
        output_path = OUTPUT_DIR / f"{clip_id}.mp4"

        # Create clip in background
        def clip_task():
            clipper.create_clip(str(video_path), str(output_path), request.start_time, request.end_time)

        background_tasks.add_task(clip_task)

        return {
            "clip_id": clip_id,
            "video_id": request.video_id,
            "status": "processing",
            "message": "Clip creation started"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/clip/{clip_id}")
async def get_clip(clip_id: str):
    """Get a created clip"""
    clip_path = OUTPUT_DIR / f"{clip_id}.mp4"

    if not clip_path.exists():
        raise HTTPException(status_code=404, detail="Clip not found")

    return FileResponse(clip_path, media_type="video/mp4")

@app.get("/videos")
async def list_videos():
    """List all uploaded videos"""
    videos = []
    for video_dir in UPLOAD_DIR.iterdir():
        if video_dir.is_dir():
            video_files = list(video_dir.glob("*.mp4")) + list(video_dir.glob("*.mkv")) + list(video_dir.glob("*.avi"))
            if video_files:
                videos.append({
                    "video_id": video_dir.name,
                    "filename": video_files[0].name,
                    "path": str(video_files[0])
                })

    return {"videos": videos}

@app.get("/clips")
async def list_clips():
    """List all created clips"""
    clips = []
    for clip_file in OUTPUT_DIR.glob("*.mp4"):
        clip_id = clip_file.stem
        file_size = clip_file.stat().st_size

        # Try to get metadata from filename or file
        scene_based = False
        scene_number = None
        start_time = None
        end_time = None

        # Try to read metadata from a companion JSON file if it exists
        metadata_file = OUTPUT_DIR / f"{clip_id}.json"
        if metadata_file.exists():
            import json
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    scene_based = metadata.get('scene_based', False)
                    scene_number = metadata.get('scene_number')
                    start_time = metadata.get('start_time')
                    end_time = metadata.get('end_time')
            except:
                pass

        # Get video duration using ffprobe
        duration = 0
        try:
            import subprocess
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', str(clip_file)],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                duration = float(result.stdout.strip())
        except:
            pass

        clips.append({
            "clip_id": clip_id,
            "filename": clip_file.name,
            "file_size": file_size,
            "duration": duration,
            "status": "completed",
            "download_url": f"/clip/{clip_id}",
            "scene_based": scene_based,
            "scene_number": scene_number,
            "start_time": start_time,
            "end_time": end_time
        })

    return {"clips": clips}

@app.delete("/clip/{clip_id}")
async def delete_clip(clip_id: str):
    """Delete a clip from the server"""
    try:
        clip_path = OUTPUT_DIR / f"{clip_id}.mp4"
        metadata_path = OUTPUT_DIR / f"{clip_id}.json"

        deleted = False
        if clip_path.exists():
            clip_path.unlink()
            deleted = True

        if metadata_path.exists():
            metadata_path.unlink()

        if deleted:
            return {"message": "Clip deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Clip not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/video/{video_id}")
async def delete_video(video_id: str):
    """Delete a video and its clips"""
    try:
        video_dir = UPLOAD_DIR / video_id
        if video_dir.exists():
            shutil.rmtree(video_dir)

        return {"message": "Video deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)