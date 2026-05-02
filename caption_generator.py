"""
Caption Generator for Video Clips
Generates complete caption files and burned-in captions:
- SRT subtitle files
- VTT subtitle files
- Burned-in captions (hardcoded into video)
- Caption metadata export
"""

import os
import re
import json
import subprocess
from typing import List, Dict, Optional
from pathlib import Path
from datetime import timedelta


class CaptionGenerator:
    """Generates captions in multiple formats"""

    def __init__(self):
        self.caption_line_length = 42  # Maximum characters per line
        self.caption_lines = 2  # Maximum lines per caption
        self.min_caption_duration = 1.0  # Minimum seconds per caption
        self.max_caption_duration = 7.0  # Maximum seconds per caption

    def format_timestamp(self, seconds: float, format_type: str = 'srt') -> str:
        """
        Format timestamp for caption files

        Args:
            seconds: Time in seconds
            format_type: 'srt' or 'vtt'

        Returns:
            Formatted timestamp string
        """
        if format_type == 'srt':
            # SRT format: 00:00:00,000
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        elif format_type == 'vtt':
            # WebVTT format: 00:00:00.000
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
        else:
            raise ValueError(f"Unknown format type: {format_type}")

    def parse_timestamp(self, timestamp: str, format_type: str = 'srt') -> float:
        """
        Parse timestamp string to seconds

        Args:
            timestamp: Timestamp string
            format_type: 'srt' or 'vtt'

        Returns:
            Time in seconds
        """
        if format_type == 'srt':
            # Parse SRT format: 00:00:00,000
            match = re.match(r'(\d+):(\d+):(\d+),(\d+)', timestamp)
            if match:
                hours, minutes, secs, millis = map(int, match.groups())
                return hours * 3600 + minutes * 60 + secs + millis / 1000
        elif format_type == 'vtt':
            # Parse WebVTT format: 00:00:00.000
            match = re.match(r'(\d+):(\d+):(\d+)\.(\d+)', timestamp)
            if match:
                hours, minutes, secs, millis = map(int, match.groups())
                return hours * 3600 + minutes * 60 + secs + millis / 1000
        return 0.0

    def break_text_for_captions(self, text: str) -> List[str]:
        """
        Break text into caption-friendly chunks

        Args:
            text: Text to break down

        Returns:
            List of text chunks suitable for captions
        """
        # Remove extra whitespace
        text = ' '.join(text.split())

        # If text is short enough, return as is
        if len(text) <= self.caption_line_length:
            return [text]

        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0

        for word in words:
            word_length = len(word)

            # Check if adding this word would exceed line length
            if current_length + word_length + 1 > self.caption_line_length:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_length = 0

            current_chunk.append(word)
            current_length += word_length + 1  # +1 for space

        # Add remaining words
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def generate_caption_segments(self, transcript: List[Dict]) -> List[Dict]:
        """
        Generate caption-ready segments from transcript

        Args:
            transcript: List of transcript segments with 'start', 'end', and 'text' keys

        Returns:
            List of caption segments with timing and text
        """
        caption_segments = []

        for segment in transcript:
            text = segment.get('text', '').strip()
            if not text:
                continue

            start_time = segment.get('start', 0.0)
            end_time = segment.get('end', 0.0)
            duration = end_time - start_time

            # Break text into caption-friendly chunks
            text_chunks = self.break_text_for_captions(text)

            if not text_chunks:
                continue

            # Calculate timing for each chunk
            chunk_duration = duration / len(text_chunks)

            for i, chunk in enumerate(text_chunks):
                chunk_start = start_time + (i * chunk_duration)
                chunk_end = chunk_start + chunk_duration

                # Ensure minimum duration
                if chunk_end - chunk_start < self.min_caption_duration:
                    chunk_end = chunk_start + self.min_caption_duration

                caption_segments.append({
                    'start': chunk_start,
                    'end': chunk_end,
                    'text': chunk
                })

        return caption_segments

    def generate_srt_captions(self, transcript: List[Dict], output_path: str) -> bool:
        """
        Generate SRT subtitle file

        Args:
            transcript: List of transcript segments
            output_path: Path to save SRT file

        Returns:
            True if successful, False otherwise
        """
        try:
            caption_segments = self.generate_caption_segments(transcript)

            with open(output_path, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(caption_segments, 1):
                    start_time = self.format_timestamp(segment['start'], 'srt')
                    end_time = self.format_timestamp(segment['end'], 'srt')

                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{segment['text']}\n\n")

            return True

        except Exception as e:
            print(f"Error generating SRT captions: {e}")
            return False

    def generate_vtt_captions(self, transcript: List[Dict], output_path: str) -> bool:
        """
        Generate WebVTT subtitle file

        Args:
            transcript: List of transcript segments
            output_path: Path to save VTT file

        Returns:
            True if successful, False otherwise
        """
        try:
            caption_segments = self.generate_caption_segments(transcript)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("WEBVTT\n\n")

                for segment in caption_segments:
                    start_time = self.format_timestamp(segment['start'], 'vtt')
                    end_time = self.format_timestamp(segment['end'], 'vtt')

                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{segment['text']}\n\n")

            return True

        except Exception as e:
            print(f"Error generating VTT captions: {e}")
            return False

    def burn_in_captions(self, video_path: str, srt_path: str, output_path: str,
                        font_size: int = 24, font_color: str = "white",
                        outline_color: str = "black", outline_width: int = 2) -> bool:
        """
        Create video with burned-in captions

        Args:
            video_path: Path to input video
            srt_path: Path to SRT subtitle file
            output_path: Path to save output video
            font_size: Font size for captions
            font_color: Color of caption text
            outline_color: Color of text outline
            outline_width: Width of text outline

        Returns:
            True if successful, False otherwise
        """
        try:
            # FFmpeg command for burning in captions
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", f"subtitles={srt}:force_style='Fontsize={font_size},PrimaryColour=&H{self._color_to_hex(font_color)},OutlineColour=&H{self._color_to_hex(outline_color)},Outline={outline_width},BorderStyle=1'",
                "-c:a", "copy",
                "-y",
                output_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)

            if result.returncode == 0 and os.path.exists(output_path):
                return True
            else:
                print(f"FFmpeg error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("Caption burning timeout")
            return False
        except Exception as e:
            print(f"Error burning in captions: {e}")
            return False

    def _color_to_hex(self, color_name: str) -> str:
        """Convert color name to hex format for FFmpeg"""
        color_map = {
            'white': 'FFFFFF',
            'black': '000000',
            'red': 'FF0000',
            'green': '00FF00',
            'blue': '0000FF',
            'yellow': 'FFFF00',
            'cyan': '00FFFF',
            'magenta': 'FF00FF'
        }
        return color_map.get(color_name.lower(), 'FFFFFF')

    def export_caption_metadata(self, transcript: List[Dict], output_path: str,
                                formats: List[str] = ['json', 'srt', 'vtt']) -> Dict[str, bool]:
        """
        Export caption metadata in multiple formats

        Args:
            transcript: List of transcript segments
            output_path: Base path for output files (without extension)
            formats: List of formats to export

        Returns:
            Dictionary with success status for each format
        """
        results = {}

        caption_segments = self.generate_caption_segments(transcript)

        # Export JSON
        if 'json' in formats:
            json_path = f"{output_path}.json"
            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(caption_segments, f, indent=2)
                results['json'] = True
            except Exception as e:
                print(f"Error exporting JSON: {e}")
                results['json'] = False

        # Export SRT
        if 'srt' in formats:
            srt_path = f"{output_path}.srt"
            results['srt'] = self.generate_srt_captions(transcript, srt_path)

        # Export VTT
        if 'vtt' in formats:
            vtt_path = f"{output_path}.vtt"
            results['vtt'] = self.generate_vtt_captions(transcript, vtt_path)

        return results

    def optimize_caption_timing(self, caption_segments: List[Dict]) -> List[Dict]:
        """
        Optimize caption timing for better readability

        Args:
            caption_segments: List of caption segments

        Returns:
            Optimized caption segments
        """
        optimized_segments = []

        for i, segment in enumerate(caption_segments):
            start_time = segment['start']
            end_time = segment['end']
            duration = end_time - start_time

            # Adjust duration based on text length
            text_length = len(segment['text'])
            optimal_duration = max(self.min_caption_duration,
                                  min(self.max_caption_duration,
                                      text_length * 0.08))  # 80ms per character

            # Adjust end time
            if duration < optimal_duration:
                end_time = start_time + optimal_duration
            elif duration > self.max_caption_duration:
                end_time = start_time + self.max_caption_duration

            # Ensure no overlap with next segment
            if i < len(caption_segments) - 1:
                next_start = caption_segments[i + 1]['start']
                if end_time > next_start - 0.1:  # 100ms gap
                    end_time = next_start - 0.1

            optimized_segments.append({
                'start': start_time,
                'end': end_time,
                'text': segment['text']
            })

        return optimized_segments

    def merge_short_captions(self, caption_segments: List[Dict],
                            max_merge_duration: float = 3.0) -> List[Dict]:
        """
        Merge very short captions with adjacent ones

        Args:
            caption_segments: List of caption segments
            max_merge_duration: Maximum duration for merged caption

        Returns:
            Merged caption segments
        """
        if not caption_segments:
            return []

        merged_segments = []
        current_segment = caption_segments[0].copy()

        for next_segment in caption_segments[1:]:
            current_duration = current_segment['end'] - current_segment['start']
            next_duration = next_segment['end'] - next_segment['start']

            # Check if current segment is very short and can be merged
            if (current_duration < self.min_caption_duration and
                next_segment['start'] - current_segment['end'] < 0.5 and
                current_duration + next_duration <= max_merge_duration):

                # Merge segments
                current_segment['end'] = next_segment['end']
                current_segment['text'] += ' ' + next_segment['text']
            else:
                # Add current segment and start new one
                merged_segments.append(current_segment)
                current_segment = next_segment.copy()

        # Add the last segment
        merged_segments.append(current_segment)

        return merged_segments

    def generate_captions_for_clip(self, transcript: List[Dict], clip_start: float,
                                   clip_end: float, output_dir: str,
                                   clip_id: str) -> Dict[str, str]:
        """
        Generate all caption formats for a specific clip

        Args:
            transcript: Full transcript
            clip_start: Start time of clip
            clip_end: End time of clip
            output_dir: Directory to save caption files
            clip_id: ID of the clip

        Returns:
            Dictionary with paths to generated caption files
        """
        # Filter transcript for clip duration
        clip_transcript = [
            seg for seg in transcript
            if seg.get('start', 0) >= clip_start and seg.get('end', 0) <= clip_end
        ]

        # Adjust timestamps to be relative to clip start
        for seg in clip_transcript:
            seg['start'] = seg.get('start', 0) - clip_start
            seg['end'] = seg.get('end', 0) - clip_start

        # Create output directory if needed
        os.makedirs(output_dir, exist_ok=True)

        # Generate caption files
        base_path = os.path.join(output_dir, f"{clip_id}_captions")

        srt_path = f"{base_path}.srt"
        vtt_path = f"{base_path}.vtt"
        json_path = f"{base_path}.json"

        # Generate all formats
        self.generate_srt_captions(clip_transcript, srt_path)
        self.generate_vtt_captions(clip_transcript, vtt_path)

        # Export JSON metadata
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(clip_transcript, f, indent=2)

        return {
            'srt': srt_path,
            'vtt': vtt_path,
            'json': json_path
        }