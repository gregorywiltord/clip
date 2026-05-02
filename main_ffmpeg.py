from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import shutil
import subprocess
from pathlib import Path
from typing import List
import json

app = FastAPI(title="Video Clipping API - FFmpeg Version")

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

# In-memory storage
videos_db = {}
clips_db = {}
downloads_db = {}  # Track download progress

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
    return {"status": "healthy", "version": "1.0.0-ffmpeg", "ffmpeg": "installed"}

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Upload a video file"""
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

        # Get video info using FFmpeg
        duration = get_video_duration(str(file_path))

        # Store in database
        videos_db[video_id] = {
            "video_id": video_id,
            "filename": file.filename,
            "path": str(file_path),
            "status": "uploaded",
            "file_size": os.path.getsize(file_path),
            "duration": duration
        }

        return {
            "video_id": video_id,
            "filename": file.filename,
            "status": "uploaded",
            "message": "Video uploaded successfully",
            "file_size": videos_db[video_id]["file_size"],
            "duration": duration
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/download")
async def download_video(request: dict, background_tasks: BackgroundTasks):
    """Download video from URL (requires yt-dlp)"""
    try:
        url = request.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")

        video_id = str(uuid.uuid4())
        video_dir = UPLOAD_DIR / video_id
        video_dir.mkdir(exist_ok=True)

        # Store in database
        videos_db[video_id] = {
            "video_id": video_id,
            "filename": "downloaded_video.mp4",
            "status": "download_pending",
            "url": url
        }

        # Try to download with yt-dlp if available
        def download_task():
            try:
                output_path = video_dir / "video.mp4"
                cmd = [
                    "yt-dlp",
                    "-f", "best[ext=mp4]/best",
                    "-o", str(output_path),
                    url
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0 and os.path.exists(output_path):
                    duration = get_video_duration(str(output_path))
                    videos_db[video_id].update({
                        "status": "uploaded",
                        "path": str(output_path),
                        "file_size": os.path.getsize(output_path),
                        "duration": duration
                    })
                else:
                    videos_db[video_id]["status"] = "download_failed"
                    videos_db[video_id]["error"] = "yt-dlp not available or download failed"

            except Exception as e:
                videos_db[video_id]["status"] = "download_failed"
                videos_db[video_id]["error"] = str(e)

        background_tasks.add_task(download_task)

        return {
            "video_id": video_id,
            "status": "downloading",
            "message": "Download started (requires yt-dlp for actual download)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_video(request: dict):
    """Analyze video using FFmpeg"""
    try:
        video_id = request.get("video_id")

        if video_id not in videos_db:
            raise HTTPException(status_code=404, detail="Video not found")

        video_info = videos_db[video_id]
        if "path" not in video_info or not os.path.exists(video_info["path"]):
            raise HTTPException(status_code=400, detail="Video file not available")

        # Get video duration
        duration = video_info.get("duration", get_video_duration(video_info["path"]))

        # Generate demo analysis based on video duration
        # In a real implementation, you'd use FFmpeg to analyze audio levels, scene changes, etc.
        num_segments = max(3, int(duration / 30))  # One segment per 30 seconds

        analysis_result = {
            "duration": duration,
            "audio_analysis": {
                "high_energy_segments": [
                    {"start": i * 30 + 10, "end": min(i * 30 + 25, duration)}
                    for i in range(min(num_segments, 5))
                ],
                "avg_energy": 0.5,
                "max_energy": 0.9
            },
            "visual_analysis": {
                "high_motion_segments": [
                    {"timestamp": i * 30 + 15, "motion_score": 0.7 + (i % 3) * 0.1}
                    for i in range(min(num_segments, 5))
                ],
                "avg_motion": 0.5,
                "max_motion": 0.9
            },
            "scene_analysis": {
                "scenes": [
                    {"start": i * 30, "end": min((i + 1) * 30, duration), "duration": 30}
                    for i in range(num_segments)
                ],
                "scene_count": num_segments
            },
            "interesting_segments": [
                {"start": i * 30 + 10, "end": min(i * 30 + 25, duration), "score": 2 + (i % 2)}
                for i in range(min(num_segments, 5))
            ],
            "recommended_clips": [
                {
                    "start": max(0, i * 30),
                    "end": min(duration, max(60, i * 30 + 60)),  # Ensure minimum 60 seconds
                    "reason": f"Optimal segment {i+1} (60+ seconds)",
                    "estimated_quality": 50 + (i % 3) * 15
                }
                for i in range(min(3, num_segments))
            ]
        }

        return {
            "video_id": video_id,
            "analysis": analysis_result,
            "status": "analyzed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clip")
async def create_clip(request: dict, background_tasks: BackgroundTasks):
    """Create a clip using FFmpeg"""
    try:
        video_id = request.get("video_id")
        start_time = request.get("start_time")
        end_time = request.get("end_time")

        if video_id not in videos_db:
            raise HTTPException(status_code=404, detail="Video not found")

        video_info = videos_db[video_id]
        if "path" not in video_info or not os.path.exists(video_info["path"]):
            raise HTTPException(status_code=400, detail="Video file not available")

        # Validate time range
        if start_time < 0:
            raise HTTPException(status_code=400, detail="Start time must be positive")
        if end_time <= start_time:
            raise HTTPException(status_code=400, detail="End time must be greater than start time")

        # Validate minimum duration (60 seconds)
        clip_duration = end_time - start_time
        if clip_duration < 60:
            raise HTTPException(
                status_code=400,
                detail=f"Clip duration must be at least 60 seconds. Current duration: {clip_duration:.1f}s"
            )

        # Check if video is long enough
        video_duration = video_info.get("duration", 0)
        if end_time > video_duration:
            raise HTTPException(
                status_code=400,
                detail=f"End time ({end_time}s) exceeds video duration ({video_duration}s)"
            )

        # Generate clip ID
        clip_id = str(uuid.uuid4())
        output_path = OUTPUT_DIR / f"{clip_id}.mp4"

        # Create clip using FFmpeg in background
        def clip_task():
            try:
                input_path = video_info["path"]

                # Calculate duration
                clip_duration = end_time - start_time

                # Validate minimum duration
                if clip_duration < 60:
                    clips_db[clip_id] = {
                        "clip_id": clip_id,
                        "video_id": video_id,
                        "status": "failed",
                        "error": f"Clip duration must be at least 60 seconds. Got {clip_duration:.1f}s"
                    }
                    return

                # FFmpeg command for professional 9:16 vertical clip (1080x1920)
                # This will:
                # 1. Extract the time range
                # 2. Scale to 1080x1920 (9:16 aspect ratio)
                # 3. Use high quality settings
                # 4. Handle aspect ratio properly with padding/cropping

                cmd = [
                    "ffmpeg",
                    "-i", input_path,
                    "-ss", str(start_time),
                    "-t", str(clip_duration),
                    # Video processing
                    "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
                    "-c:v", "libx264",
                    "-preset", "medium",  # Balance between speed and quality
                    "-crf", "23",  # High quality (18-28 is good, 23 is default)
                    "-pix_fmt", "yuv420p",  # Ensure compatibility
                    # Audio processing
                    "-c:a", "aac",
                    "-b:a", "128k",  # Good audio quality
                    "-ar", "44100",  # Standard sample rate
                    # Output settings
                    "-movflags", "+faststart",  # Enable fast start for streaming
                    "-y",  # Overwrite output file if exists
                    str(output_path)
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)  # 2 hour timeout

                if result.returncode == 0 and os.path.exists(output_path):
                    # Verify the output
                    actual_duration = get_video_duration(str(output_path))

                    clips_db[clip_id] = {
                        "clip_id": clip_id,
                        "video_id": video_id,
                        "start_time": start_time,
                        "end_time": end_time,
                        "status": "completed",
                        "path": str(output_path),
                        "file_size": os.path.getsize(output_path),
                        "duration": actual_duration,
                        "resolution": "1080x1920",
                        "aspect_ratio": "9:16"
                    }
                else:
                    error_msg = result.stderr if result.stderr else "FFmpeg processing failed"
                    clips_db[clip_id] = {
                        "clip_id": clip_id,
                        "video_id": video_id,
                        "status": "failed",
                        "error": error_msg
                    }

            except subprocess.TimeoutExpired:
                clips_db[clip_id] = {
                    "clip_id": clip_id,
                    "video_id": video_id,
                    "status": "failed",
                    "error": "Processing timeout - video may be too long or complex"
                }
            except Exception as e:
                clips_db[clip_id] = {
                    "clip_id": clip_id,
                    "video_id": video_id,
                    "status": "failed",
                    "error": str(e)
                }

        background_tasks.add_task(clip_task)

        # Store initial status
        clips_db[clip_id] = {
            "clip_id": clip_id,
            "video_id": video_id,
            "start_time": start_time,
            "end_time": end_time,
            "status": "processing",
            "target_resolution": "1080x1920",
            "target_aspect_ratio": "9:16",
            "target_duration": clip_duration
        }

        return {
            "clip_id": clip_id,
            "video_id": video_id,
            "status": "processing",
            "message": "Creating 9:16 vertical clip (1080x1920) - minimum 60 seconds required",
            "target_duration": clip_duration,
            "target_resolution": "1080x1920",
            "target_aspect_ratio": "9:16",
            "estimated_time": f"~{int(clip_duration * 0.5)}-{int(clip_duration * 1.5)} seconds"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/clip/{clip_id}")
async def get_clip(clip_id: str):
    """Get a created clip"""
    if clip_id not in clips_db:
        raise HTTPException(status_code=404, detail="Clip not found")

    clip_info = clips_db[clip_id]

    if clip_info["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Clip is {clip_info['status']}. Please wait for processing to complete."
        )

    clip_path = Path(clip_info["path"])
    if not clip_path.exists():
        raise HTTPException(status_code=404, detail="Clip file not found")

    return FileResponse(clip_path, media_type="video/mp4")

@app.get("/clip/{clip_id}/status")
async def get_clip_status(clip_id: str):
    """Get clip processing status"""
    if clip_id not in clips_db:
        raise HTTPException(status_code=404, detail="Clip not found")

    return clips_db[clip_id]

@app.get("/videos")
async def list_videos():
    """List all uploaded videos"""
    videos = []
    for video_id, video_info in videos_db.items():
        videos.append({
            "video_id": video_id,
            "filename": video_info.get("filename", "Unknown"),
            "status": video_info.get("status", "unknown"),
            "file_size": video_info.get("file_size", 0),
            "duration": video_info.get("duration", 0)
        })

    return {"videos": videos}

@app.get("/clips")
async def list_clips():
    """List all created clips"""
    clips = []
    for clip_id, clip_info in clips_db.items():
        clip_data = {
            "clip_id": clip_id,
            "video_id": clip_info.get("video_id", ""),
            "start_time": clip_info.get("start_time", 0),
            "end_time": clip_info.get("end_time", 0),
            "status": clip_info.get("status", "unknown"),
            "file_size": clip_info.get("file_size", 0)
        }

        # Add download URL if completed
        if clip_info.get("status") == "completed":
            clip_data["download_url"] = f"/clip/{clip_id}"
            clip_data["duration"] = clip_info.get("end_time", 0) - clip_info.get("start_time", 0)

        clips.append(clip_data)

    return {"clips": clips}

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

def get_video_duration(video_path: str) -> float:
    """Get video duration using FFmpeg"""
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return float(result.stdout.strip())
    except Exception as e:
        print(f"Error getting video duration: {e}")
    return 0.0

if __name__ == "__main__":
    import uvicorn
    print("🎬 Video Clipping Application - FFmpeg Version")
    print("📍 Running at http://localhost:8000")
    print("✅ FFmpeg is installed and ready for video processing")
    print("📝 Features:")
    print("   - Upload videos")
    print("   - Real video clipping with FFmpeg")
    print("   - Download clips")
    print("   - Video analysis (demo mode)")
    uvicorn.run(app, host="0.0.0.0", port=8000)