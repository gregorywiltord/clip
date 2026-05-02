# Video Clipping Application

A powerful, free and open-source video clipping tool with AI-powered analysis. Upload videos, analyze them for interesting segments, and create perfect clips automatically.

## Features

- 🎬 **Video Upload**: Upload local videos or download from URLs (YouTube, Vimeo, etc.)
- 🤖 **AI Analysis**: Automatically analyze videos to find trending and interesting segments
- ✂️ **Smart Clipping**: Create clips from recommended segments or custom time ranges
- 🎯 **Scene Detection**: Detect scene changes and visual motion
- 🔊 **Audio Analysis**: Analyze audio energy levels to find engaging moments
- 🌐 **Web Interface**: Easy-to-use web interface
- 🐳 **Docker Ready**: Deploy easily with Docker or Coolify

## Tech Stack

- **Backend**: FastAPI (Python)
- **Video Processing**: MoviePy, OpenCV
- **Scene Detection**: PySceneDetect
- **Audio Analysis**: Librosa
- **Video Download**: yt-dlp
- **Frontend**: HTML/CSS/JavaScript

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access the application at http://localhost:8000
```

### Option 2: Manual Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Access the application at http://localhost:8000
```

## Deployment to Coolify

1. **Push your code to a Git repository** (GitHub, GitLab, etc.)

2. **In Coolify**:
   - Create a new application
   - Select your Git repository
   - Choose the "video clipping" folder as the root directory
   - Set the build type to "Docker"
   - Add port mapping: `8000:8000`
   - Deploy!

3. **Environment Variables** (optional):
   - `UPLOAD_DIR`: Directory for uploaded videos (default: `/app/uploads`)
   - `OUTPUT_DIR`: Directory for output clips (default: `/app/output`)
   - `TEMP_DIR`: Directory for temporary files (default: `/app/temp`)

## Usage

### 1. Upload or Download a Video

- **Upload**: Click "Upload Video" tab and drag & drop a video file
- **Download**: Click "Download from URL" tab and paste a video URL

### 2. Analyze the Video

- Go to "Video Library"
- Click "Analyze" on your video
- Wait for the AI analysis to complete (may take several minutes)

### 3. Create Clips

- **Recommended Clips**: Click "Create Clip" on any recommended segment
- **Custom Clips**: Click "Clip" and set your desired time range

### 4. Download Clips

- Clips are saved in the `output/` directory
- Access them via the web interface or directly from the server

## API Endpoints

### Upload & Download
- `POST /upload` - Upload a video file
- `POST /download` - Download video from URL

### Analysis
- `POST /analyze` - Analyze video for interesting segments
- `GET /videos` - List all uploaded videos

### Clipping
- `POST /clip` - Create a clip from a video
- `GET /clip/{clip_id}` - Download a created clip

### Management
- `DELETE /video/{video_id}` - Delete a video
- `GET /health` - Health check endpoint

## Project Structure

```
video clipping/
├── main.py              # FastAPI application
├── video_analyzer.py    # Video analysis logic
├── video_clipper.py     # Video clipping logic
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
├── templates/
│   └── index.html      # Web interface
├── uploads/            # Uploaded videos
├── output/             # Generated clips
└── temp/               # Temporary files
```

## How It Works

### Video Analysis

The application uses multiple techniques to find interesting segments:

1. **Audio Analysis**: Detects high-energy audio segments (loud moments, music peaks)
2. **Visual Analysis**: Detects motion and scene changes using computer vision
3. **Scene Detection**: Identifies scene boundaries using content detection
4. **Combined Scoring**: Ranks segments based on combined audio and visual activity

### Clipping Process

1. Load the video using MoviePy
2. Extract the specified time range
3. Encode the clip with optimal settings
4. Save to the output directory

## Performance Considerations

- **Large Videos**: Processing time depends on video length and resolution
- **System Resources**: Ensure sufficient CPU and RAM for video processing
- **Storage**: Videos and clips can take significant disk space
- **Concurrent Processing**: The application handles multiple requests asynchronously

## Troubleshooting

### Common Issues

**Issue**: "Video analysis takes too long"
- **Solution**: This is normal for long videos. Be patient or try shorter videos first.

**Issue**: "Out of memory"
- **Solution**: Increase available RAM or process smaller video segments.

**Issue**: "Docker build fails"
- **Solution**: Ensure Docker has sufficient resources and all dependencies are available.

**Issue**: "yt-dlp download fails"
- **Solution**: The video URL might be restricted or the service might have changed.

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Adding New Features

The modular structure makes it easy to add new features:

1. **New Analysis Methods**: Add to `video_analyzer.py`
2. **New Clipping Options**: Add to `video_clipper.py`
3. **New API Endpoints**: Add to `main.py`
4. **UI Changes**: Modify `templates/index.html`

## License

This project is free and open-source, released under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the API documentation
- Open an issue on GitHub

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Video processing powered by [MoviePy](https://zulko.github.io/moviepy/)
- Scene detection by [PySceneDetect](https://www.scenedetect.com/)
- Video download via [yt-dlp](https://github.com/yt-dlp/yt-dlp)