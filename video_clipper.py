from moviepy import VideoFileClip
import os
from typing import Optional, Dict, List
import json
import subprocess

class VideoClipper:
    def __init__(self):
        self.default_codec = 'libx264'
        self.default_audio_codec = 'aac'
        self.default_aspect_ratio = '9:16'  # Vertical format for shorts
        self.default_resolution = (1080, 1920)  # 1080x1920 for 9:16

    def create_clip(self, input_path: str, output_path: str, start_time: float, end_time: float,
                   codec: Optional[str] = None, audio_codec: Optional[str] = None) -> bool:
        """
        Create a clip from a video file

        Args:
            input_path: Path to input video
            output_path: Path for output clip
            start_time: Start time in seconds
            end_time: End time in seconds
            codec: Video codec (default: libx264)
            audio_codec: Audio codec (default: aac)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load video
            video = VideoFileClip(input_path)

            # Validate time range
            if start_time < 0:
                start_time = 0
            if end_time > video.duration:
                end_time = video.duration
            if start_time >= end_time:
                raise ValueError("Start time must be less than end time")

            # Create clip
            clip = video.subclip(start_time, end_time)

            # Set codecs
            codec = codec or self.default_codec
            audio_codec = audio_codec or self.default_audio_codec

            # Write clip
            clip.write_videofile(
                output_path,
                codec=codec,
                audio_codec=audio_codec,
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )

            # Close clips
            clip.close()
            video.close()

            return True

        except Exception as e:
            print(f"Error creating clip: {e}")
            return False

    def create_multiple_clips(self, input_path: str, output_dir: str, segments: list) -> list:
        """
        Create multiple clips from a video

        Args:
            input_path: Path to input video
            output_dir: Directory for output clips
            segments: List of dicts with 'start' and 'end' times

        Returns:
            list: List of created clip paths
        """
        created_clips = []

        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Load video once
            video = VideoFileClip(input_path)

            for i, segment in enumerate(segments):
                start_time = segment['start']
                end_time = segment['end']

                # Validate time range
                if start_time < 0:
                    start_time = 0
                if end_time > video.duration:
                    end_time = video.duration
                if start_time >= end_time:
                    continue

                # Create clip
                clip = video.subclip(start_time, end_time)

                # Generate output path
                output_path = os.path.join(output_dir, f"clip_{i+1}.mp4")

                # Write clip
                clip.write_videofile(
                    output_path,
                    codec=self.default_codec,
                    audio_codec=self.default_audio_codec,
                    temp_audiofile=f'temp-audio-{i}.m4a',
                    remove_temp=True
                )

                created_clips.append(output_path)
                clip.close()

            video.close()
            return created_clips

        except Exception as e:
            print(f"Error creating multiple clips: {e}")
            return created_clips

    def create_gif(self, input_path: str, output_path: str, start_time: float, end_time: float,
                  fps: int = 10, scale: float = 0.5) -> bool:
        """
        Create a GIF from a video segment

        Args:
            input_path: Path to input video
            output_path: Path for output GIF
            start_time: Start time in seconds
            end_time: End time in seconds
            fps: Frames per second for GIF
            scale: Scale factor for resizing

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load video
            video = VideoFileClip(input_path)

            # Validate time range
            if start_time < 0:
                start_time = 0
            if end_time > video.duration:
                end_time = video.duration
            if start_time >= end_time:
                raise ValueError("Start time must be less than end time")

            # Create clip
            clip = video.subclip(start_time, end_time)

            # Resize if needed
            if scale != 1.0:
                clip = clip.resize(scale)

            # Write GIF
            clip.write_gif(output_path, fps=fps)

            # Close clips
            clip.close()
            video.close()

            return True

        except Exception as e:
            print(f"Error creating GIF: {e}")
            return False

    def get_video_info(self, video_path: str) -> dict:
        """
        Get information about a video file

        Args:
            video_path: Path to video file

        Returns:
            dict: Video information
        """
        try:
            video = VideoFileClip(video_path)

            info = {
                "duration": video.duration,
                "fps": video.fps,
                "size": video.size,
                "width": video.size[0],
                "height": video.size[1],
                "has_audio": video.audio is not None
            }

            video.close()
            return info

        except Exception as e:
            print(f"Error getting video info: {e}")
            return {"error": str(e)}

    def create_viral_clip(self, input_path: str, output_path: str, start_time: float,
                         end_time: float, viral_data: Optional[Dict] = None,
                         resolution: Optional[tuple] = None,
                         aspect_ratio: Optional[str] = None) -> Dict:
        """
        Create a viral-optimized clip with metadata

        Args:
            input_path: Path to input video
            output_path: Path for output clip
            start_time: Start time in seconds
            end_time: End time in seconds
            viral_data: Optional viral scoring data
            resolution: Optional resolution tuple (width, height)
            aspect_ratio: Optional aspect ratio string

        Returns:
            dict: Result with success status and metadata
        """
        try:
            # Use default resolution/aspect ratio if not provided
            if resolution is None:
                resolution = self.default_resolution
            if aspect_ratio is None:
                aspect_ratio = self.default_aspect_ratio

            # Load video
            video = VideoFileClip(input_path)

            # Validate time range
            if start_time < 0:
                start_time = 0
            if end_time > video.duration:
                end_time = video.duration
            if start_time >= end_time:
                raise ValueError("Start time must be less than end time")

            # Create clip
            clip = video.subclip(start_time, end_time)

            # Resize to target resolution with aspect ratio preservation
            target_width, target_height = resolution
            clip = clip.resize(height=target_height)

            # Crop or pad to exact resolution
            if clip.size[0] > target_width:
                # Crop center
                x_center = clip.size[0] / 2
                clip = clip.crop(x1=x_center - target_width/2, x2=x_center + target_width/2)
            elif clip.size[0] < target_width:
                # Pad with black
                from moviepy.video.fx.all import pad
                clip = pad(clip, (target_width, target_height), color=(0, 0, 0))

            # Set codecs
            codec = self.default_codec
            audio_codec = self.default_audio_codec

            # Write clip with optimal settings for social media
            clip.write_videofile(
                output_path,
                codec=codec,
                audio_codec=audio_codec,
                preset='medium',
                bitrate='8000k',  # High bitrate for quality
                threads=4,
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )

            # Close clips
            clip.close()
            video.close()

            # Get actual clip info
            actual_clip = VideoFileClip(output_path)
            actual_duration = actual_clip.duration
            actual_size = actual_clip.size
            actual_clip.close()

            # Prepare metadata
            metadata = {
                'success': True,
                'input_path': input_path,
                'output_path': output_path,
                'start_time': start_time,
                'end_time': end_time,
                'duration': actual_duration,
                'resolution': actual_size,
                'aspect_ratio': aspect_ratio,
                'codec': codec,
                'audio_codec': audio_codec,
                'file_size': os.path.getsize(output_path)
            }

            # Add viral data if provided
            if viral_data:
                metadata['viral_data'] = viral_data

            return metadata

        except Exception as e:
            print(f"Error creating viral clip: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_viral_clips_batch(self, input_path: str, output_dir: str,
                                viral_segments: List[Dict],
                                max_clips: int = 5) -> List[Dict]:
        """
        Create multiple viral clips from top segments

        Args:
            input_path: Path to input video
            output_dir: Directory for output clips
            viral_segments: List of viral segment data
            max_clips: Maximum number of clips to create

        Returns:
            list: List of created clip metadata
        """
        created_clips = []

        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Sort segments by viral score
            sorted_segments = sorted(
                viral_segments,
                key=lambda x: x.get('overall_viral_score', 0),
                reverse=True
            )

            # Create clips for top segments
            for i, segment in enumerate(sorted_segments[:max_clips]):
                start_time = segment.get('start_time', 0)
                end_time = segment.get('end_time', 0)

                # Generate output filename
                output_filename = f"viral_clip_{i+1}_{segment.get('overall_viral_score', 0):.2f}.mp4"
                output_path = os.path.join(output_dir, output_filename)

                # Create clip
                result = self.create_viral_clip(
                    input_path=input_path,
                    output_path=output_path,
                    start_time=start_time,
                    end_time=end_time,
                    viral_data=segment
                )

                if result.get('success'):
                    result['clip_number'] = i + 1
                    result['viral_rank'] = i + 1
                    result['filename'] = output_filename
                    created_clips.append(result)

            return created_clips

        except Exception as e:
            print(f"Error creating viral clips batch: {e}")
            return created_clips

    def optimize_clip_length(self, segment: Dict, target_duration: Optional[float] = None) -> Dict:
        """
        Optimize clip length for viral potential

        Args:
            segment: Segment data with start/end times
            target_duration: Optional target duration in seconds

        Returns:
            dict: Optimized start/end times
        """
        start_time = segment.get('start_time', 0)
        end_time = segment.get('end_time', 0)
        current_duration = end_time - start_time

        # Optimal lengths for viral content (in seconds)
        optimal_lengths = {
            'primary': (30, 45),    # Sweet spot for engagement
            'secondary': (15, 30),  # Punchy content
            'tertiary': (45, 60)    # Storytelling content
        }

        if target_duration:
            # Use specified target duration
            optimal_duration = target_duration
        else:
            # Find best optimal range
            if optimal_lengths['primary'][0] <= current_duration <= optimal_lengths['primary'][1]:
                # Already in optimal range
                return {
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': current_duration,
                    'optimization': 'already_optimal'
                }
            elif current_duration < optimal_lengths['primary'][0]:
                # Too short, extend to primary minimum
                optimal_duration = optimal_lengths['primary'][0]
            else:
                # Too long, trim to primary maximum
                optimal_duration = optimal_lengths['primary'][1]

        # Calculate new times (center the adjustment)
        duration_diff = optimal_duration - current_duration
        half_diff = duration_diff / 2

        new_start = max(0, start_time - half_diff)
        new_end = new_start + optimal_duration

        return {
            'start_time': new_start,
            'end_time': new_end,
            'duration': optimal_duration,
            'optimization': 'adjusted'
        }

    def attach_caption_metadata(self, clip_path: str, transcript: List[Dict],
                               output_path: Optional[str] = None) -> Dict:
        """
        Attach caption metadata to clip

        Args:
            clip_path: Path to clip file
            transcript: Transcript data for captions
            output_path: Optional path for metadata file

        Returns:
            dict: Caption metadata
        """
        try:
            # Get clip info
            clip = VideoFileClip(clip_path)
            clip_duration = clip.duration
            clip.close()

            # Filter transcript for clip duration
            clip_transcript = [
                seg for seg in transcript
                if seg.get('start', 0) >= 0 and seg.get('end', 0) <= clip_duration
            ]

            # Prepare caption metadata
            caption_metadata = {
                'clip_path': clip_path,
                'clip_duration': clip_duration,
                'transcript': clip_transcript,
                'caption_segments': [],
                'total_caption_segments': len(clip_transcript)
            }

            # Generate caption segments
            for seg in clip_transcript:
                caption_metadata['caption_segments'].append({
                    'start': seg.get('start', 0),
                    'end': seg.get('end', 0),
                    'text': seg.get('text', '').strip()
                })

            # Save metadata if output path provided
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(caption_metadata, f, indent=2)
                caption_metadata['metadata_path'] = output_path

            return caption_metadata

        except Exception as e:
            print(f"Error attaching caption metadata: {e}")
            return {'error': str(e)}

    def create_clip_with_captions(self, input_path: str, output_path: str,
                                 start_time: float, end_time: float,
                                 transcript: List[Dict],
                                 burn_in_captions: bool = False,
                                 caption_style: Optional[Dict] = None) -> Dict:
        """
        Create clip with optional burned-in captions

        Args:
            input_path: Path to input video
            output_path: Path for output clip
            start_time: Start time in seconds
            end_time: End time in seconds
            transcript: Transcript data for captions
            burn_in_captions: Whether to burn in captions
            caption_style: Optional caption style settings

        Returns:
            dict: Result with success status and metadata
        """
        try:
            # Create clip first
            result = self.create_viral_clip(
                input_path=input_path,
                output_path=output_path,
                start_time=start_time,
                end_time=end_time
            )

            if not result.get('success'):
                return result

            # Attach caption metadata
            metadata_path = output_path.replace('.mp4', '_metadata.json')
            caption_metadata = self.attach_caption_metadata(
                clip_path=output_path,
                transcript=transcript,
                output_path=metadata_path
            )

            result['caption_metadata'] = caption_metadata

            # Burn in captions if requested
            if burn_in_captions:
                from caption_generator import CaptionGenerator
                caption_gen = CaptionGenerator()

                # Generate SRT file
                srt_path = output_path.replace('.mp4', '.srt')
                caption_gen.generate_srt_captions(transcript, srt_path)

                # Apply caption style
                style = caption_style or {
                    'font_size': 24,
                    'font_color': 'white',
                    'outline_color': 'black',
                    'outline_width': 2
                }

                # Create video with burned-in captions
                burned_path = output_path.replace('.mp4', '_with_captions.mp4')
                burn_success = caption_gen.burn_in_captions(
                    video_path=output_path,
                    srt_path=srt_path,
                    output_path=burned_path,
                    **style
                )

                if burn_success:
                    result['burned_captions_path'] = burned_path
                    result['srt_path'] = srt_path
                else:
                    result['burn_error'] = 'Failed to burn in captions'

            return result

        except Exception as e:
            print(f"Error creating clip with captions: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_clip_metadata(self, clip_path: str) -> Dict:
        """
        Get comprehensive metadata for a clip

        Args:
            clip_path: Path to clip file

        Returns:
            dict: Clip metadata
        """
        try:
            clip = VideoFileClip(clip_path)

            metadata = {
                'path': clip_path,
                'duration': clip.duration,
                'fps': clip.fps,
                'size': clip.size,
                'width': clip.size[0],
                'height': clip.size[1],
                'has_audio': clip.audio is not None,
                'file_size': os.path.getsize(clip_path),
                'aspect_ratio': f"{clip.size[0]}:{clip.size[1]}"
            }

            # Calculate aspect ratio category
            aspect_ratio = clip.size[0] / clip.size[1]
            if 0.5 <= aspect_ratio <= 0.6:
                metadata['aspect_ratio_category'] = '9:16 (vertical/shorts)'
            elif 0.9 <= aspect_ratio <= 1.1:
                metadata['aspect_ratio_category'] = '1:1 (square)'
            elif 1.3 <= aspect_ratio <= 1.8:
                metadata['aspect_ratio_category'] = '16:9 (landscape)'
            else:
                metadata['aspect_ratio_category'] = 'custom'

            clip.close()

            return metadata

        except Exception as e:
            print(f"Error getting clip metadata: {e}")
            return {"error": str(e)}