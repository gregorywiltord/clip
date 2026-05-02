import cv2
import numpy as np
from moviepy import VideoFileClip
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from typing import List, Dict, Optional
import tempfile
import os
from content_analyzer import ContentAnalyzer
from viral_scorer import ViralScorer

# Try to import optional dependencies
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("Warning: librosa not available. Audio analysis features will be limited.")

try:
    import whisper
    import soundfile as sf
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Warning: whisper not available. Speech recognition features will be limited.")

class VideoAnalyzer:
    def __init__(self):
        self.motion_threshold = 25.0
        self.audio_threshold_percentile = 75
        self.content_analyzer = ContentAnalyzer()
        self.viral_scorer = ViralScorer()
        self.whisper_model = None  # Lazy load Whisper model

    def analyze_video(self, video_path: str) -> Dict:
        """Comprehensive video analysis"""
        try:
            # Load video
            video = VideoFileClip(video_path)
            duration = video.duration

            # Analyze different aspects
            audio_analysis = self.analyze_audio(video)
            visual_analysis = self.analyze_visual(video_path)
            scene_analysis = self.analyze_scenes(video_path)

            # Combine analyses
            interesting_segments = self.find_interesting_segments(
                audio_analysis,
                visual_analysis,
                scene_analysis,
                duration
            )

            return {
                "duration": duration,
                "audio_analysis": audio_analysis,
                "visual_analysis": visual_analysis,
                "scene_analysis": scene_analysis,
                "interesting_segments": interesting_segments,
                "recommended_clips": self.generate_recommendations(interesting_segments, duration)
            }

        except Exception as e:
            print(f"Error analyzing video: {e}")
            return {
                "error": str(e),
                "interesting_segments": [],
                "recommended_clips": []
            }

    def analyze_audio(self, video) -> Dict:
        """Analyze audio for energy levels"""
        try:
            if not video.audio:
                return {"high_energy_segments": [], "avg_energy": 0}

            # Get audio data
            audio_array = video.audio.to_soundarray()

            # Calculate audio energy
            if len(audio_array.shape) > 1:
                audio_energy = np.mean(np.abs(audio_array), axis=1)
            else:
                audio_energy = np.abs(audio_array)

            # Find high-energy segments
            threshold = np.percentile(audio_energy, self.audio_threshold_percentile)
            high_energy_indices = np.where(audio_energy > threshold)[0]

            # Convert to time segments
            segments = []
            if len(high_energy_indices) > 0:
                current_segment = [high_energy_indices[0]]
                for i in range(1, len(high_energy_indices)):
                    if high_energy_indices[i] - high_energy_indices[i-1] <= 5:  # Within 5 frames
                        current_segment.append(high_energy_indices[i])
                    else:
                        # End current segment
                        start_time = current_segment[0] / video.audio.fps
                        end_time = current_segment[-1] / video.audio.fps
                        segments.append({"start": start_time, "end": end_time})
                        current_segment = [high_energy_indices[i]]

                # Add last segment
                if current_segment:
                    start_time = current_segment[0] / video.audio.fps
                    end_time = current_segment[-1] / video.audio.fps
                    segments.append({"start": start_time, "end": end_time})

            return {
                "high_energy_segments": segments,
                "avg_energy": float(np.mean(audio_energy)),
                "max_energy": float(np.max(audio_energy))
            }

        except Exception as e:
            print(f"Error analyzing audio: {e}")
            return {"high_energy_segments": [], "error": str(e)}

    def analyze_visual(self, video_path: str) -> Dict:
        """Analyze visual changes and motion"""
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            prev_frame = None
            motion_scores = []
            frame_timestamps = []

            frame_count = 0
            sample_rate = max(1, int(fps / 2))  # Sample every 0.5 seconds

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % sample_rate == 0:
                    # Convert to grayscale
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    if prev_frame is not None:
                        # Calculate frame difference
                        diff = cv2.absdiff(prev_frame, gray)
                        motion_score = np.mean(diff)

                        motion_scores.append(motion_score)
                        timestamp = frame_count / fps
                        frame_timestamps.append(timestamp)

                    prev_frame = gray

                frame_count += 1

            cap.release()

            # Find high-motion segments
            if motion_scores:
                threshold = np.percentile(motion_scores, 75)
                high_motion_segments = []

                for i, score in enumerate(motion_scores):
                    if score > threshold:
                        high_motion_segments.append({
                            "timestamp": frame_timestamps[i],
                            "motion_score": float(score)
                        })

                return {
                    "high_motion_segments": high_motion_segments,
                    "avg_motion": float(np.mean(motion_scores)),
                    "max_motion": float(np.max(motion_scores))
                }

            return {"high_motion_segments": [], "avg_motion": 0}

        except Exception as e:
            print(f"Error analyzing visual: {e}")
            return {"high_motion_segments": [], "error": str(e)}

    def analyze_scenes(self, video_path: str) -> Dict:
        """Detect scene changes"""
        try:
            video_manager = VideoManager([video_path])
            scene_manager = SceneManager()
            scene_manager.add_detector(ContentDetector(threshold=30.0))

            video_manager.start()
            scene_manager.detect_scenes(frame_source=video_manager)
            scene_list = scene_manager.get_scene_list()

            scenes = []
            for scene in scene_list:
                start_time = scene[0].get_seconds()
                end_time = scene[1].get_seconds()
                scenes.append({
                    "start": start_time,
                    "end": end_time,
                    "duration": end_time - start_time
                })

            video_manager.release()

            return {
                "scenes": scenes,
                "scene_count": len(scenes)
            }

        except Exception as e:
            print(f"Error analyzing scenes: {e}")
            return {"scenes": [], "error": str(e)}

    def find_interesting_segments(self, audio_analysis, visual_analysis, scene_analysis, duration: float) -> List[Dict]:
        """Find interesting segments by combining all analyses"""
        interesting_segments = []

        # Combine high audio and high motion segments
        audio_segments = audio_analysis.get("high_energy_segments", [])
        visual_segments = visual_analysis.get("high_motion_segments", [])

        # Score segments based on combined audio and visual activity
        segment_scores = {}

        # Score audio segments
        for segment in audio_segments:
            key = f"{segment['start']:.1f}-{segment['end']:.1f}"
            segment_scores[key] = segment_scores.get(key, 0) + 1

        # Score visual segments (convert point segments to ranges)
        for point in visual_segments:
            timestamp = point["timestamp"]
            # Create a small window around the point
            start = max(0, timestamp - 2)
            end = min(duration, timestamp + 2)
            key = f"{start:.1f}-{end:.1f}"
            segment_scores[key] = segment_scores.get(key, 0) + 1

        # Convert scores to segments
        for key, score in segment_scores.items():
            if score >= 2:  # Only keep segments with multiple indicators
                start, end = map(float, key.split('-'))
                interesting_segments.append({
                    "start": start,
                    "end": end,
                    "score": score
                })

        # Sort by score
        interesting_segments.sort(key=lambda x: x["score"], reverse=True)

        return interesting_segments[:10]  # Return top 10 segments

    def generate_recommendations(self, interesting_segments: List[Dict], duration: float) -> List[Dict]:
        """Generate recommended clips from interesting segments"""
        recommendations = []

        for segment in interesting_segments:
            # Extend segment to make it a proper clip (min 15 seconds, max 60 seconds)
            start = max(0, segment["start"] - 5)
            end = min(duration, segment["end"] + 5)

            clip_duration = end - start
            if clip_duration < 15:
                end = min(duration, start + 15)
            elif clip_duration > 60:
                end = start + 60

            recommendations.append({
                "start": start,
                "end": end,
                "reason": f"High activity segment (score: {segment['score']})",
                "estimated_quality": min(100, segment['score'] * 20)
            })

        return recommendations[:5]  # Return top 5 recommendations

    def load_whisper_model(self, model_size: str = "base"):
        """Lazy load Whisper model for speech recognition"""
        if self.whisper_model is None:
            print(f"Loading Whisper model ({model_size})...")
            self.whisper_model = whisper.load_model(model_size)
            print("Whisper model loaded successfully")
        return self.whisper_model

    def transcribe_audio(self, video_path: str, model_size: str = "base") -> Dict:
        """
        Transcribe audio from video using Whisper

        Args:
            video_path: Path to video file
            model_size: Whisper model size ('base', 'small', 'medium', 'large')

        Returns:
            Dictionary with transcription results
        """
        try:
            if not WHISPER_AVAILABLE:
                return {
                    "error": "Whisper not available. Please install openai-whisper package.",
                    "segments": []
                }

            # Load Whisper model
            model = self.load_whisper_model(model_size)

            # Extract audio from video
            video = VideoFileClip(video_path)
            if not video.audio:
                return {"error": "No audio track found", "segments": []}

            # Create temporary audio file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_audio_path = temp_audio.name
                video.audio.write_audiofile(temp_audio_path, verbose=False, logger=None)

            # Transcribe audio
            result = model.transcribe(temp_audio_path, word_timestamps=True)

            # Clean up temporary file
            os.unlink(temp_audio_path)
            video.close()

            # Process segments
            segments = []
            for segment in result['segments']:
                segments.append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip(),
                    'words': segment.get('words', [])
                })

            return {
                'text': result['text'],
                'language': result['language'],
                'segments': segments,
                'duration': result.get('duration', 0)
            }

        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return {"error": str(e), "segments": []}

    def detect_speech_segments(self, video_path: str, min_confidence: float = 0.7) -> List[Dict]:
        """
        Detect segments with clear speech

        Args:
            video_path: Path to video file
            min_confidence: Minimum confidence threshold for speech detection

        Returns:
            List of speech segments with confidence scores
        """
        try:
            # Transcribe audio
            transcription = self.transcribe_audio(video_path)

            if 'error' in transcription:
                return []

            # Filter segments by confidence
            speech_segments = []
            for segment in transcription['segments']:
                # Calculate confidence based on word timestamps
                words = segment.get('words', [])
                if words:
                    avg_confidence = np.mean([w.get('probability', 0.5) for w in words])
                else:
                    avg_confidence = 0.5

                if avg_confidence >= min_confidence:
                    speech_segments.append({
                        'start': segment['start'],
                        'end': segment['end'],
                        'text': segment['text'],
                        'confidence': avg_confidence
                    })

            return speech_segments

        except Exception as e:
            print(f"Error detecting speech segments: {e}")
            return []

    def calculate_speech_confidence(self, segment: Dict) -> float:
        """
        Calculate speech clarity confidence for a segment

        Args:
            segment: Segment dictionary with 'words' key

        Returns:
            Confidence score (0.0 to 1.0)
        """
        words = segment.get('words', [])
        if not words:
            return 0.5

        confidences = [w.get('probability', 0.5) for w in words]
        return float(np.mean(confidences))

    def analyze_audio_quality(self, video_path: str) -> Dict:
        """
        Comprehensive audio quality analysis

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with audio quality metrics
        """
        try:
            # Load video
            video = VideoFileClip(video_path)
            if not video.audio:
                return {"error": "No audio track found", "quality_score": 0.0}

            # Get audio data
            audio_array = video.audio.to_soundarray()
            fps = video.audio.fps

            # Calculate various quality metrics
            if len(audio_array.shape) > 1:
                audio_mono = np.mean(audio_array, axis=1)
            else:
                audio_mono = audio_array

            # RMS energy (signal strength)
            rms_energy = np.sqrt(np.mean(audio_mono ** 2))

            # Signal-to-noise ratio estimation
            noise_floor = np.percentile(np.abs(audio_mono), 10)
            signal_level = np.percentile(np.abs(audio_mono), 90)
            snr_estimate = 20 * np.log10(signal_level / (noise_floor + 1e-10))

            # Dynamic range
            dynamic_range = np.max(audio_mono) - np.min(audio_mono)

            # Clipping detection
            clipping_ratio = np.sum(np.abs(audio_mono) > 0.95) / len(audio_mono)

            # Zero crossing rate (indicates frequency content)
            zero_crossings = np.sum(np.diff(np.sign(audio_mono)) != 0) / len(audio_mono)

            # Calculate overall quality score
            quality_score = 0.0

            # RMS energy score (optimal range: 0.1 to 0.3)
            if 0.1 <= rms_energy <= 0.3:
                quality_score += 0.25
            elif rms_energy > 0:
                quality_score += 0.15

            # SNR score (higher is better, above 20dB is good)
            if snr_estimate > 20:
                quality_score += 0.25
            elif snr_estimate > 10:
                quality_score += 0.15
            elif snr_estimate > 0:
                quality_score += 0.05

            # Dynamic range score
            if dynamic_range > 0.5:
                quality_score += 0.2
            elif dynamic_range > 0.3:
                quality_score += 0.1

            # Clipping penalty
            if clipping_ratio < 0.01:
                quality_score += 0.15
            elif clipping_ratio < 0.05:
                quality_score += 0.05

            # Zero crossing rate (indicates speech presence)
            if 0.1 <= zero_crossings <= 0.3:
                quality_score += 0.15
            elif zero_crossings > 0:
                quality_score += 0.05

            quality_score = min(quality_score, 1.0)

            video.close()

            return {
                'quality_score': quality_score,
                'rms_energy': float(rms_energy),
                'snr_estimate': float(snr_estimate),
                'dynamic_range': float(dynamic_range),
                'clipping_ratio': float(clipping_ratio),
                'zero_crossing_rate': float(zero_crossings),
                'has_audio': True
            }

        except Exception as e:
            print(f"Error analyzing audio quality: {e}")
            return {"error": str(e), "quality_score": 0.0}

    def detect_noise_segments(self, video_path: str, noise_threshold: float = 0.8) -> List[Dict]:
        """
        Detect segments with high noise levels

        Args:
            video_path: Path to video file
            noise_threshold: Threshold for noise detection

        Returns:
            List of noisy segments to avoid
        """
        try:
            # Load video
            video = VideoFileClip(video_path)
            if not video.audio:
                return []

            # Get audio data
            audio_array = video.audio.to_soundarray()
            fps = video.audio.fps

            if len(audio_array.shape) > 1:
                audio_mono = np.mean(audio_array, axis=1)
            else:
                audio_mono = audio_array

            # Calculate noise level using high-frequency content
            from scipy import signal
            frequencies, times, spectrogram = signal.spectrogram(audio_mono, fs=fps)

            # High-frequency energy (potential noise)
            high_freq_energy = np.mean(spectrogram[int(len(frequencies) * 0.7):], axis=0)

            # Find noisy segments
            noisy_segments = []
            current_segment = None

            for i, energy in enumerate(high_freq_energy):
                timestamp = times[i]

                if energy > noise_threshold:
                    if current_segment is None:
                        current_segment = {'start': timestamp, 'end': timestamp}
                    else:
                        current_segment['end'] = timestamp
                else:
                    if current_segment is not None:
                        # End current segment
                        duration = current_segment['end'] - current_segment['start']
                        if duration >= 1.0:  # Only keep segments >= 1 second
                            noisy_segments.append(current_segment)
                        current_segment = None

            # Add last segment if it exists
            if current_segment is not None:
                duration = current_segment['end'] - current_segment['start']
                if duration >= 1.0:
                    noisy_segments.append(current_segment)

            video.close()

            return noisy_segments

        except Exception as e:
            print(f"Error detecting noise segments: {e}")
            return []

    def calculate_speech_music_ratio(self, video_path: str) -> Dict:
        """
        Calculate speech-to-music ratio in audio

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with speech and music ratios
        """
        try:
            if not LIBROSA_AVAILABLE:
                return {
                    "error": "librosa not available",
                    "speech_ratio": 0.5,
                    "music_ratio": 0.5,
                    "dominant": "unknown"
                }

            # Load video
            video = VideoFileClip(video_path)
            if not video.audio:
                return {"error": "No audio track found", "speech_ratio": 0.0, "music_ratio": 0.0}

            # Get audio data
            audio_array = video.audio.to_soundarray()
            fps = video.audio.fps

            if len(audio_array.shape) > 1:
                audio_mono = np.mean(audio_array, axis=1)
            else:
                audio_mono = audio_array

            # Use librosa for audio feature extraction
            y, sr = librosa.resample(audio_mono, orig_fps=fps, target_sr=22050)

            # Extract features
            # Spectral centroid (higher for music, lower for speech)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

            # Zero crossing rate (higher for speech)
            zcr = librosa.feature.zero_crossing_rate(y)[0]

            # MFCCs (good for speech detection)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

            # Calculate speech probability based on features
            speech_frames = 0
            music_frames = 0

            for i in range(len(spectral_centroids)):
                # Speech typically has lower spectral centroid and higher zero crossing rate
                is_speech = (spectral_centroids[i] < np.median(spectral_centroids) and
                           zcr[i] > np.median(zcr))

                if is_speech:
                    speech_frames += 1
                else:
                    music_frames += 1

            total_frames = speech_frames + music_frames
            if total_frames > 0:
                speech_ratio = speech_frames / total_frames
                music_ratio = music_frames / total_frames
            else:
                speech_ratio = 0.5
                music_ratio = 0.5

            video.close()

            return {
                'speech_ratio': float(speech_ratio),
                'music_ratio': float(music_ratio),
                'dominant': 'speech' if speech_ratio > music_ratio else 'music'
            }

        except Exception as e:
            print(f"Error calculating speech/music ratio: {e}")
            return {"error": str(e), "speech_ratio": 0.0, "music_ratio": 0.0}

    def analyze_viral_potential(self, video_path: str, model_size: str = "base") -> Dict:
        """
        Comprehensive viral potential analysis

        Args:
            video_path: Path to video file
            model_size: Whisper model size

        Returns:
            Complete viral analysis with scores and recommendations
        """
        try:
            # Get basic video info
            video = VideoFileClip(video_path)
            duration = video.duration

            # Transcribe audio
            transcription = self.transcribe_audio(video_path, model_size)

            if 'error' in transcription:
                video.close()
                return {
                    "error": "Transcription failed",
                    "viral_segments": [],
                    "recommendations": []
                }

            # Analyze content for viral characteristics
            content_analysis = self.content_analyzer.analyze_full_transcript(
                transcription['segments']
            )

            # Analyze audio quality
            audio_quality = self.analyze_audio_quality(video_path)

            # Analyze visual engagement
            visual_analysis = self.analyze_visual(video_path)

            # Detect speech segments
            speech_segments = self.detect_speech_segments(video_path)

            # Calculate speech/music ratio
            speech_music_ratio = self.calculate_speech_music_ratio(video_path)

            # Combine all data for viral scoring
            viral_segments_data = []

            for content_segment in content_analysis['content_segments']:
                # Find corresponding speech segment
                speech_segment = None
                for seg in speech_segments:
                    if (abs(seg['start'] - content_segment.start_time) < 1.0 and
                        abs(seg['end'] - content_segment.end_time) < 1.0):
                        speech_segment = seg
                        break

                # Calculate speech clarity
                speech_clarity = 0.5
                if speech_segment:
                    speech_clarity = speech_segment.get('confidence', 0.5)

                # Get audio quality score
                audio_quality_score = audio_quality.get('quality_score', 0.5)

                # Get visual engagement score
                visual_score = 0.5
                if visual_analysis.get('high_motion_segments'):
                    # Find visual score for this time range
                    for motion in visual_analysis['high_motion_segments']:
                        timestamp = motion['timestamp']
                        if content_segment.start_time <= timestamp <= content_segment.end_time:
                            visual_score = min(1.0, motion.get('motion_score', 0) / 50.0)
                            break

                # Create segment data for viral scoring
                segment_data = {
                    'start_time': content_segment.start_time,
                    'end_time': content_segment.end_time,
                    'duration': content_segment.end_time - content_segment.start_time,
                    'text': content_segment.text,
                    'speech_clarity': speech_clarity,
                    'hook_quality': content_segment.hook_score,
                    'punchline_impact': content_segment.punchline_score,
                    'educational_value': content_segment.educational_score,
                    'emotional_engagement': content_segment.emotional_score,
                    'audio_quality': audio_quality_score,
                    'visual_engagement': visual_score,
                    'caption_readiness': content_segment.caption_readiness
                }

                viral_segments_data.append(segment_data)

            # Calculate viral scores
            viral_segments = self.viral_scorer.batch_score_segments(viral_segments_data)

            # Generate viral report
            viral_report = self.viral_scorer.generate_viral_report(viral_segments, top_n=10)

            video.close()

            return {
                'duration': duration,
                'transcription': transcription,
                'content_analysis': content_analysis,
                'audio_quality': audio_quality,
                'visual_analysis': visual_analysis,
                'speech_music_ratio': speech_music_ratio,
                'viral_segments': viral_segments,
                'viral_report': viral_report
            }

        except Exception as e:
            print(f"Error analyzing viral potential: {e}")
            return {
                "error": str(e),
                "viral_segments": [],
                "viral_report": {
                    "summary": {"total_segments": 0, "average_viral_score": 0.0},
                    "top_segments": [],
                    "recommendations": []
                }
            }