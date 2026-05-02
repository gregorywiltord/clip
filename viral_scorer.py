"""
Viral Scorer for Video Content
Combines multiple factors to calculate viral potential scores:
- Speech clarity
- Hook quality
- Punchline impact
- Educational value
- Emotional engagement
- Audio quality
- Visual engagement
- Caption readiness
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class ViralSegment:
    """Represents a video segment with viral potential scores"""
    start_time: float
    end_time: float
    duration: float
    text: str
    speech_clarity: float
    hook_quality: float
    punchline_impact: float
    educational_value: float
    emotional_engagement: float
    audio_quality: float
    visual_engagement: float
    caption_readiness: float
    overall_viral_score: float
    reasoning: List[str]


class ViralScorer:
    """Calculates viral potential scores for video segments"""

    def __init__(self):
        # Weight configuration for viral scoring
        self.weights = {
            'speech_clarity': 0.25,
            'hook_quality': 0.20,
            'punchline_impact': 0.15,
            'educational_value': 0.15,
            'emotional_engagement': 0.10,
            'audio_quality': 0.10,
            'visual_engagement': 0.05,
            'caption_readiness': 0.10
        }

        # Optimal clip length ranges (in seconds)
        self.optimal_lengths = {
            'primary': (30, 45),    # Sweet spot for engagement
            'secondary': (15, 30),  # Punchy content
            'tertiary': (45, 60)    # Storytelling content
        }

    def calculate_viral_score(self, segment_data: Dict) -> ViralSegment:
        """
        Calculate comprehensive viral score for a segment

        Args:
            segment_data: Dictionary containing all segment metrics

        Returns:
            ViralSegment object with calculated scores
        """
        # Extract individual scores
        speech_clarity = segment_data.get('speech_clarity', 0.0)
        hook_quality = segment_data.get('hook_quality', 0.0)
        punchline_impact = segment_data.get('punchline_impact', 0.0)
        educational_value = segment_data.get('educational_value', 0.0)
        emotional_engagement = segment_data.get('emotional_engagement', 0.0)
        audio_quality = segment_data.get('audio_quality', 0.0)
        visual_engagement = segment_data.get('visual_engagement', 0.0)
        caption_readiness = segment_data.get('caption_readiness', 0.0)

        # Calculate weighted viral score
        overall_viral_score = (
            speech_clarity * self.weights['speech_clarity'] +
            hook_quality * self.weights['hook_quality'] +
            punchline_impact * self.weights['punchline_impact'] +
            educational_value * self.weights['educational_value'] +
            emotional_engagement * self.weights['emotional_engagement'] +
            audio_quality * self.weights['audio_quality'] +
            visual_engagement * self.weights['visual_engagement'] +
            caption_readiness * self.weights['caption_readiness']
        )

        # Generate reasoning for the score
        reasoning = self._generate_reasoning(segment_data)

        return ViralSegment(
            start_time=segment_data.get('start_time', 0.0),
            end_time=segment_data.get('end_time', 0.0),
            duration=segment_data.get('duration', 0.0),
            text=segment_data.get('text', ''),
            speech_clarity=speech_clarity,
            hook_quality=hook_quality,
            punchline_impact=punchline_impact,
            educational_value=educational_value,
            emotional_engagement=emotional_engagement,
            audio_quality=audio_quality,
            visual_engagement=visual_engagement,
            caption_readiness=caption_readiness,
            overall_viral_score=overall_viral_score,
            reasoning=reasoning
        )

    def _generate_reasoning(self, segment_data: Dict) -> List[str]:
        """Generate human-readable reasoning for the viral score"""
        reasoning = []

        # Speech clarity reasoning
        speech_clarity = segment_data.get('speech_clarity', 0.0)
        if speech_clarity > 0.8:
            reasoning.append("Excellent speech clarity - easy to understand and caption")
        elif speech_clarity > 0.6:
            reasoning.append("Good speech clarity - suitable for captions")
        elif speech_clarity > 0.4:
            reasoning.append("Moderate speech clarity - may need caption editing")
        else:
            reasoning.append("Poor speech clarity - not ideal for viral content")

        # Hook quality reasoning
        hook_quality = segment_data.get('hook_quality', 0.0)
        if hook_quality > 0.7:
            reasoning.append("Strong hook - grabs attention immediately")
        elif hook_quality > 0.5:
            reasoning.append("Good hook - engages viewers early")
        elif hook_quality > 0.3:
            reasoning.append("Moderate hook - some engagement potential")

        # Punchline impact reasoning
        punchline_impact = segment_data.get('punchline_impact', 0.0)
        if punchline_impact > 0.7:
            reasoning.append("Highly quotable - great for sharing")
        elif punchline_impact > 0.5:
            reasoning.append("Memorable content - shareable moments")
        elif punchline_impact > 0.3:
            reasoning.append("Some quotable potential")

        # Educational value reasoning
        educational_value = segment_data.get('educational_value', 0.0)
        if educational_value > 0.7:
            reasoning.append("High educational value - provides clear learning")
        elif educational_value > 0.5:
            reasoning.append("Good educational content - useful information")
        elif educational_value > 0.3:
            reasoning.append("Some educational value")

        # Emotional engagement reasoning
        emotional_engagement = segment_data.get('emotional_engagement', 0.0)
        if emotional_engagement > 0.7:
            reasoning.append("High emotional impact - compelling storytelling")
        elif emotional_engagement > 0.5:
            reasoning.append("Good emotional engagement - connects with viewers")
        elif emotional_engagement > 0.3:
            reasoning.append("Some emotional content")

        # Audio quality reasoning
        audio_quality = segment_data.get('audio_quality', 0.0)
        if audio_quality > 0.7:
            reasoning.append("Excellent audio quality - professional sound")
        elif audio_quality > 0.5:
            reasoning.append("Good audio quality - clear and pleasant")
        elif audio_quality > 0.3:
            reasoning.append("Acceptable audio quality")

        # Visual engagement reasoning
        visual_engagement = segment_data.get('visual_engagement', 0.0)
        if visual_engagement > 0.7:
            reasoning.append("High visual engagement - dynamic and interesting")
        elif visual_engagement > 0.5:
            reasoning.append("Good visual content - engaging visuals")
        elif visual_engagement > 0.3:
            reasoning.append("Moderate visual engagement")

        # Caption readiness reasoning
        caption_readiness = segment_data.get('caption_readiness', 0.0)
        if caption_readiness > 0.8:
            reasoning.append("Perfect for captions - clear and concise")
        elif caption_readiness > 0.6:
            reasoning.append("Good for captions - minimal editing needed")
        elif caption_readiness > 0.4:
            reasoning.append("Caption-friendly with some adjustments")

        # Length optimization reasoning
        duration = segment_data.get('duration', 0.0)
        if self.optimal_lengths['primary'][0] <= duration <= self.optimal_lengths['primary'][1]:
            reasoning.append("Optimal length for maximum engagement (30-45s)")
        elif self.optimal_lengths['secondary'][0] <= duration <= self.optimal_lengths['secondary'][1]:
            reasoning.append("Good punchy length (15-30s)")
        elif self.optimal_lengths['tertiary'][0] <= duration <= self.optimal_lengths['tertiary'][1]:
            reasoning.append("Good storytelling length (45-60s)")
        else:
            reasoning.append(f"Length {duration:.1f}s - consider adjusting for optimal engagement")

        return reasoning

    def rank_viral_segments(self, segments: List[ViralSegment]) -> List[ViralSegment]:
        """
        Rank segments by viral potential

        Args:
            segments: List of ViralSegment objects

        Returns:
            Sorted list of segments by viral score (highest first)
        """
        return sorted(segments, key=lambda x: x.overall_viral_score, reverse=True)

    def optimize_clip_length(self, segment: ViralSegment, target_length: Optional[float] = None) -> Dict:
        """
        Optimize clip length for viral potential

        Args:
            segment: ViralSegment to optimize
            target_length: Optional target length in seconds

        Returns:
            Dictionary with optimized start/end times
        """
        current_duration = segment.duration

        if target_length:
            # Use specified target length
            optimal_duration = target_length
        else:
            # Find best optimal range
            if self.optimal_lengths['primary'][0] <= current_duration <= self.optimal_lengths['primary'][1]:
                # Already in optimal range
                return {
                    'start_time': segment.start_time,
                    'end_time': segment.end_time,
                    'duration': current_duration,
                    'optimization': 'already_optimal'
                }
            elif current_duration < self.optimal_lengths['primary'][0]:
                # Too short, extend to primary minimum
                optimal_duration = self.optimal_lengths['primary'][0]
            else:
                # Too long, trim to primary maximum
                optimal_duration = self.optimal_lengths['primary'][1]

        # Calculate new times (center the adjustment)
        duration_diff = optimal_duration - current_duration
        half_diff = duration_diff / 2

        new_start = max(0, segment.start_time - half_diff)
        new_end = new_start + optimal_duration

        return {
            'start_time': new_start,
            'end_time': new_end,
            'duration': optimal_duration,
            'optimization': 'adjusted'
        }

    def generate_viral_report(self, viral_segments: List[ViralSegment], top_n: int = 5) -> Dict:
        """
        Generate comprehensive viral analysis report

        Args:
            viral_segments: List of analyzed segments
            top_n: Number of top segments to include in report

        Returns:
            Complete viral analysis report
        """
        # Rank segments
        ranked_segments = self.rank_viral_segments(viral_segments)

        # Get top segments
        top_segments = ranked_segments[:top_n]

        # Calculate statistics
        scores = [seg.overall_viral_score for seg in viral_segments]
        avg_score = np.mean(scores) if scores else 0.0
        max_score = np.max(scores) if scores else 0.0
        min_score = np.min(scores) if scores else 0.0

        # Analyze score distribution
        high_potential = len([s for s in scores if s > 0.7])
        medium_potential = len([s for s in scores if 0.5 <= s <= 0.7])
        low_potential = len([s for s in scores if s < 0.5])

        # Generate recommendations
        recommendations = self._generate_recommendations(top_segments)

        return {
            'summary': {
                'total_segments': len(viral_segments),
                'average_viral_score': float(avg_score),
                'max_viral_score': float(max_score),
                'min_viral_score': float(min_score),
                'high_potential_segments': high_potential,
                'medium_potential_segments': medium_potential,
                'low_potential_segments': low_potential
            },
            'top_segments': [
                {
                    'rank': i + 1,
                    'start_time': seg.start_time,
                    'end_time': seg.end_time,
                    'duration': seg.duration,
                    'overall_viral_score': seg.overall_viral_score,
                    'text': seg.text,
                    'reasoning': seg.reasoning,
                    'component_scores': {
                        'speech_clarity': seg.speech_clarity,
                        'hook_quality': seg.hook_quality,
                        'punchline_impact': seg.punchline_impact,
                        'educational_value': seg.educational_value,
                        'emotional_engagement': seg.emotional_engagement,
                        'audio_quality': seg.audio_quality,
                        'visual_engagement': seg.visual_engagement,
                        'caption_readiness': seg.caption_readiness
                    }
                }
                for i, seg in enumerate(top_segments)
            ],
            'recommendations': recommendations,
            'score_distribution': {
                'high_potential': high_potential,
                'medium_potential': medium_potential,
                'low_potential': low_potential
            }
        }

    def _generate_recommendations(self, top_segments: List[ViralSegment]) -> List[str]:
        """Generate actionable recommendations based on top segments"""
        recommendations = []

        if not top_segments:
            recommendations.append("No high-potential segments detected. Consider content with clearer speech or more engaging hooks.")
            return recommendations

        # Analyze top segment characteristics
        top_segment = top_segments[0]

        # Length recommendations
        if top_segment.duration < 30:
            recommendations.append("Consider extending top segments to 30-45 seconds for optimal engagement")
        elif top_segment.duration > 60:
            recommendations.append("Consider trimming longer segments to 45-60 seconds for better retention")

        # Content type recommendations
        if top_segment.hook_quality > 0.7:
            recommendations.append("Strong hooks detected - focus on opening 5-10 seconds for maximum impact")
        if top_segment.punchline_impact > 0.7:
            recommendations.append("Highly quotable content found - these segments have high sharing potential")
        if top_segment.educational_value > 0.7:
            recommendations.append("Educational content detected - these segments provide clear value to viewers")
        if top_segment.emotional_engagement > 0.7:
            recommendations.append("Emotional content found - these segments create strong viewer connection")

        # Caption recommendations
        if top_segment.caption_readiness > 0.8:
            recommendations.append("Excellent caption readiness - minimal editing required for subtitles")
        elif top_segment.caption_readiness > 0.6:
            recommendations.append("Good caption readiness - some editing may improve subtitle quality")

        # Overall strategy
        if len(top_segments) >= 3:
            recommendations.append(f"Multiple high-potential segments detected - recommend creating {min(5, len(top_segments))} clips for testing")
        else:
            recommendations.append("Limited high-potential segments - consider improving content structure or speech clarity")

        return recommendations

    def batch_score_segments(self, segments_data: List[Dict]) -> List[ViralSegment]:
        """
        Calculate viral scores for multiple segments

        Args:
            segments_data: List of segment data dictionaries

        Returns:
            List of ViralSegment objects with calculated scores
        """
        viral_segments = []

        for segment_data in segments_data:
            try:
                viral_segment = self.calculate_viral_score(segment_data)
                viral_segments.append(viral_segment)
            except Exception as e:
                print(f"Error scoring segment: {e}")
                continue

        return viral_segments