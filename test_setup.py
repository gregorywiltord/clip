"""
Simple test script to verify the video clipping application setup
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False

    try:
        import moviepy
        print("✅ MoviePy imported successfully")
    except ImportError as e:
        print(f"❌ MoviePy import failed: {e}")
        return False

    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False

    try:
        import scenedetect
        print("✅ PySceneDetect imported successfully")
    except ImportError as e:
        print(f"❌ PySceneDetect import failed: {e}")
        return False

    try:
        import librosa
        print("✅ Librosa imported successfully")
    except ImportError as e:
        print(f"❌ Librosa import failed: {e}")
        return False

    try:
        import yt_dlp
        print("✅ yt-dlp imported successfully")
    except ImportError as e:
        print(f"❌ yt-dlp import failed: {e}")
        return False

    return True

def test_directories():
    """Test if required directories exist"""
    print("\nTesting directories...")
    required_dirs = ['uploads', 'output', 'temp', 'templates']

    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ Directory '{dir_name}' exists")
        else:
            print(f"❌ Directory '{dir_name}' does not exist")
            return False

    return True

def test_files():
    """Test if required files exist"""
    print("\nTesting files...")
    required_files = [
        'main.py',
        'video_analyzer.py',
        'video_clipper.py',
        'requirements.txt',
        'Dockerfile',
        'docker-compose.yml',
        'templates/index.html'
    ]

    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"✅ File '{file_name}' exists")
        else:
            print(f"❌ File '{file_name}' does not exist")
            return False

    return True

def test_analyzer():
    """Test video analyzer initialization"""
    print("\nTesting video analyzer...")
    try:
        from video_analyzer import VideoAnalyzer
        analyzer = VideoAnalyzer()
        print("✅ VideoAnalyzer initialized successfully")
        return True
    except Exception as e:
        print(f"❌ VideoAnalyzer initialization failed: {e}")
        return False

def test_clipper():
    """Test video clipper initialization"""
    print("\nTesting video clipper...")
    try:
        from video_clipper import VideoClipper
        clipper = VideoClipper()
        print("✅ VideoClipper initialized successfully")
        return True
    except Exception as e:
        print(f"❌ VideoClipper initialization failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Video Clipping Application - Setup Test")
    print("=" * 50)
    print()

    tests = [
        test_imports,
        test_directories,
        test_files,
        test_analyzer,
        test_clipper
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)

    print()
    print("=" * 50)
    print("Test Results")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if all(results):
        print("✅ All tests passed! Your setup is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())