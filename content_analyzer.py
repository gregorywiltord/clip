"""
Content Analyzer for Viral Video Detection
Analyzes transcribed content for viral characteristics:
- Hook detection (attention-grabbing openings)
- Punchline detection (quotable moments)
- Educational content detection (value-providing segments)
- Emotional content analysis (engaging storytelling)
- Caption readiness analysis
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class ContentSegment:
    """Represents a segment of content with analysis scores"""
    start_time: float
    end_time: float
    text: str
    hook_score: float
    punchline_score: float
    educational_score: float
    emotional_score: float
    caption_readiness: float


class ContentAnalyzer:
    """Analyzes content for viral characteristics"""

    def __init__(self):
        # Hook detection patterns
        self.hook_patterns = {
            'questions': r'^\s*[Ww]h(at|ere|en|y|o|ich)|[Hh]ow\s+(?:much|many|do|does|did|can|could|would|should)',
            'shocking_statements': r'^\s*(?:[Yy]ou\s+(?:won\'t|will\s+not)\s+believe|(?:[Ss]hocking|[Aa]mazing|[Ii]ncredible|[Uu]nbelievable))',
            'numbers': r'^\s*\d+\s*(?:ways|tips|tricks|things|facts|secrets|methods)',
            'teasers': r'^\s*(?:[Ww]ait\s+until\s+you\s+see|[Dd]on\'t\s+miss|[Yy]ou\s+need\s+to\s+see)',
            'direct_address': r'^\s*(?:[Hh]ey\s+everyone|[Ll]isten\s+up|[Pp]ay\s+attention|[Tt]his\s+is\s+(?:important|huge|big))',
            'curiosity_gaps': r'^\s*(?:[Tt]he\s+(?:secret|truth|reason|key|trick)|[Ww]hat\s+(?:no\s+one\s+tells\s+you|they\s+don\'t\s+want\s+you\s+to\s+know))'
        }

        # Punchline detection patterns
        self.punchline_patterns = {
            'punctuation': r'[!?]{2,}$',
            'emphasis': r'(?:[A-Z]{2,}|(?:very|really|absolutely|totally|completely)\s+\w+)',
            'contrast': r'(?:but|however|yet|although|nevertheless)\s+',
            'revelation': r'(?:turns?\s+out|actually|in\s+fact|the\s+truth\s+is|believe\s+it\s+or\s+not)',
            'humor_indicators': r'(?:lol|haha|funny|joke|kidding|just\s+saying)',
            'memorable_phrases': r'(?:game\s+changer|mind\s+blowing|life\s+changing|next\s+level|next\s+step)'
        }

        # Educational content patterns
        self.educational_patterns = {
            'instructional': r'(?:how\s+to|step\s+by\s+step|tutorial|guide|learn|teach|show\s+you)',
            'explanatory': r'(?:here\'s\s+(?:the|why|how)|this\s+is\s+(?:why|how|because)|the\s+reason\s+(?:is|why))',
            'tips': r'(?:tip|trick|hack|advice|suggestion|recommendation)',
            'facts': r'(?:fact|statistic|research|study|data|evidence|proof)',
            'lists': r'(?:first|second|third|finally|lastly|next|then)',
            'value_proposition': r'(?:save\s+(?:time|money)|benefit|advantage|improve|increase|decrease|reduce)'
        }

        # Emotional content patterns
        self.emotional_patterns = {
            'positive_emotions': r'(?:love|happy|amazing|wonderful|beautiful|incredible|fantastic|joy|excited|thrilled)',
            'negative_emotions': r'(?:sad|terrible|awful|horrible|bad|worst|hate|angry|frustrated|disappointed)',
            'surprise': r'(?:surprising|unexpected|shocking|amazing|incredible|unbelievable|wow)',
            'intensity': r'(?:extremely|incredibly|absolutely|totally|completely|utterly|intensely)',
            'personal_stories': r'(?:i\s+(?:felt|experienced|went\s+through|remember)|my\s+(?:story|experience))',
            'dramatic': r'(?:never|ever|always|forever|life\s+or\s+death|critical|crucial|essential)'
        }

        # Caption readability patterns
        self.caption_readiness_patterns = {
            'short_sentences': r'^.{1,80}[.!?]$',
            'simple_words': r'^(?:[a-zA-Z]+\s*){1,15}$',
            'no_complex_punctuation': r'^[^;:(){}\[\]]*$',
            'clear_structure': r'^(?:[A-Z][^.!?]*[.!?]\s*)+$'
        }

    def detect_hooks(self, transcript: List[Dict]) -> List[Dict]:
        """
        Detect attention-grabbing hooks in the transcript

        Args:
            transcript: List of segments with 'start', 'end', and 'text' keys

        Returns:
            List of hook segments with scores
        """
        hooks = []

        for segment in transcript:
            text = segment.get('text', '').strip()
            if not text:
                continue

            hook_score = 0.0
            matched_patterns = []

            # Check each hook pattern
            for pattern_name, pattern in self.hook_patterns.items():
                if re.search(pattern, text, re.IGNORECASE):
                    hook_score += 0.15
                    matched_patterns.append(pattern_name)

            # Bonus for early segments (first 30 seconds)
            if segment.get('start', 0) < 30:
                hook_score += 0.2

            # Bonus for short, punchy hooks
            if len(text.split()) <= 10:
                hook_score += 0.1

            # Normalize score
            hook_score = min(hook_score, 1.0)

            if hook_score > 0.3:  # Only keep significant hooks
                hooks.append({
                    'start': segment.get('start', 0),
                    'end': segment.get('end', 0),
                    'text': text,
                    'hook_score': hook_score,
                    'matched_patterns': matched_patterns
                })

        return sorted(hooks, key=lambda x: x['hook_score'], reverse=True)

    def identify_punchlines(self, transcript: List[Dict]) -> List[Dict]:
        """
        Identify quotable moments and punchlines

        Args:
            transcript: List of segments with 'start', 'end', and 'text' keys

        Returns:
            List of punchline segments with scores
        """
        punchlines = []

        for segment in transcript:
            text = segment.get('text', '').strip()
            if not text:
                continue

            punchline_score = 0.0
            matched_patterns = []

            # Check each punchline pattern
            for pattern_name, pattern in self.punchline_patterns.items():
                if re.search(pattern, text, re.IGNORECASE):
                    punchline_score += 0.2
                    matched_patterns.append(pattern_name)

            # Bonus for memorable phrasing
            if any(word in text.lower() for word in ['remember', 'never forget', 'always', 'key', 'important']):
                punchline_score += 0.15

            # Bonus for emotional impact
            if any(word in text.lower() for word in ['love', 'hate', 'amazing', 'terrible', 'best', 'worst']):
                punchline_score += 0.1

            # Normalize score
            punchline_score = min(punchline_score, 1.0)

            if punchline_score > 0.3:  # Only keep significant punchlines
                punchlines.append({
                    'start': segment.get('start', 0),
                    'end': segment.get('end', 0),
                    'text': text,
                    'punchline_score': punchline_score,
                    'matched_patterns': matched_patterns
                })

        return sorted(punchlines, key=lambda x: x['punchline_score'], reverse=True)

    def detect_educational_content(self, transcript: List[Dict]) -> List[Dict]:
        """
        Identify educational and value-providing content

        Args:
            transcript: List of segments with 'start', 'end', and 'text' keys

        Returns:
            List of educational segments with scores
        """
        educational_segments = []

        for segment in transcript:
            text = segment.get('text', '').strip()
            if not text:
                continue

            educational_score = 0.0
            matched_patterns = []

            # Check each educational pattern
            for pattern_name, pattern in self.educational_patterns.items():
                if re.search(pattern, text, re.IGNORECASE):
                    educational_score += 0.15
                    matched_patterns.append(pattern_name)

            # Bonus for clear explanations
            if any(word in text.lower() for word in ['because', 'since', 'due to', 'as a result', 'therefore']):
                educational_score += 0.1

            # Bonus for practical value
            if any(word in text.lower() for word in ['use', 'apply', 'implement', 'do', 'make', 'create']):
                educational_score += 0.1

            # Normalize score
            educational_score = min(educational_score, 1.0)

            if educational_score > 0.3:  # Only keep significant educational content
                educational_segments.append({
                    'start': segment.get('start', 0),
                    'end': segment.get('end', 0),
                    'text': text,
                    'educational_score': educational_score,
                    'matched_patterns': matched_patterns
                })

        return sorted(educational_segments, key=lambda x: x['educational_score'], reverse=True)

    def analyze_emotional_content(self, transcript: List[Dict]) -> List[Dict]:
        """
        Analyze emotional content and storytelling elements

        Args:
            transcript: List of segments with 'start', 'end', and 'text' keys

        Returns:
            List of emotional segments with scores
        """
        emotional_segments = []

        for segment in transcript:
            text = segment.get('text', '').strip()
            if not text:
                continue

            emotional_score = 0.0
            matched_patterns = []

            # Check each emotional pattern
            for pattern_name, pattern in self.emotional_patterns.items():
                if re.search(pattern, text, re.IGNORECASE):
                    emotional_score += 0.15
                    matched_patterns.append(pattern_name)

            # Bonus for storytelling elements
            if any(word in text.lower() for word in ['story', 'experience', 'happened', 'remember', 'moment']):
                emotional_score += 0.1

            # Bonus for personal connection
            if any(word in text.lower() for word in ['i', 'my', 'me', 'we', 'us', 'our']):
                emotional_score += 0.05

            # Normalize score
            emotional_score = min(emotional_score, 1.0)

            if emotional_score > 0.3:  # Only keep significant emotional content
                emotional_segments.append({
                    'start': segment.get('start', 0),
                    'end': segment.get('end', 0),
                    'text': text,
                    'emotional_score': emotional_score,
                    'matched_patterns': matched_patterns
                })

        return sorted(emotional_segments, key=lambda x: x['emotional_score'], reverse=True)

    def calculate_caption_readiness(self, text: str) -> float:
        """
        Calculate how well text works with captions

        Args:
            text: Text segment to analyze

        Returns:
            Caption readiness score (0.0 to 1.0)
        """
        if not text or not text.strip():
            return 0.0

        caption_score = 0.0

        # Check short sentences
        if re.search(self.caption_readiness_patterns['short_sentences'], text):
            caption_score += 0.3

        # Check simple words
        if re.search(self.caption_readiness_patterns['simple_words'], text):
            caption_score += 0.2

        # Check no complex punctuation
        if re.search(self.caption_readiness_patterns['no_complex_punctuation'], text):
            caption_score += 0.2

        # Check clear structure
        if re.search(self.caption_readiness_patterns['clear_structure'], text):
            caption_score += 0.3

        # Penalty for very long segments
        if len(text) > 150:
            caption_score -= 0.2

        # Penalty for complex words
        complex_words = ['however', 'nevertheless', 'furthermore', 'consequently', 'subsequently']
        if any(word in text.lower() for word in complex_words):
            caption_score -= 0.1

        return max(0.0, min(caption_score, 1.0))

    def combine_viral_scores(self, hooks: List[Dict], punchlines: List[Dict],
                            educational: List[Dict], emotional: List[Dict],
                            transcript: List[Dict]) -> List[ContentSegment]:
        """
        Combine all viral content scores into comprehensive segments

        Args:
            hooks: Hook detection results
            punchlines: Punchline detection results
            educational: Educational content detection results
            emotional: Emotional content detection results
            transcript: Full transcript for caption readiness

        Returns:
            List of ContentSegment objects with combined scores
        """
        # Create a map of time segments to scores
        segment_scores = {}

        # Process hooks
        for hook in hooks:
            key = (hook['start'], hook['end'])
            if key not in segment_scores:
                segment_scores[key] = {
                    'start': hook['start'],
                    'end': hook['end'],
                    'text': hook['text'],
                    'hook_score': 0.0,
                    'punchline_score': 0.0,
                    'educational_score': 0.0,
                    'emotional_score': 0.0
                }
            segment_scores[key]['hook_score'] = hook['hook_score']

        # Process punchlines
        for punchline in punchlines:
            key = (punchline['start'], punchline['end'])
            if key not in segment_scores:
                segment_scores[key] = {
                    'start': punchline['start'],
                    'end': punchline['end'],
                    'text': punchline['text'],
                    'hook_score': 0.0,
                    'punchline_score': 0.0,
                    'educational_score': 0.0,
                    'emotional_score': 0.0
                }
            segment_scores[key]['punchline_score'] = punchline['punchline_score']

        # Process educational content
        for edu in educational:
            key = (edu['start'], edu['end'])
            if key not in segment_scores:
                segment_scores[key] = {
                    'start': edu['start'],
                    'end': edu['end'],
                    'text': edu['text'],
                    'hook_score': 0.0,
                    'punchline_score': 0.0,
                    'educational_score': 0.0,
                    'emotional_score': 0.0
                }
            segment_scores[key]['educational_score'] = edu['educational_score']

        # Process emotional content
        for emo in emotional:
            key = (emo['start'], emo['end'])
            if key not in segment_scores:
                segment_scores[key] = {
                    'start': emo['start'],
                    'end': emo['end'],
                    'text': emo['text'],
                    'hook_score': 0.0,
                    'punchline_score': 0.0,
                    'educational_score': 0.0,
                    'emotional_score': 0.0
                }
            segment_scores[key]['emotional_score'] = emo['emotional_score']

        # Convert to ContentSegment objects and calculate caption readiness
        content_segments = []
        for key, scores in segment_scores.items():
            caption_readiness = self.calculate_caption_readiness(scores['text'])

            segment = ContentSegment(
                start_time=scores['start'],
                end_time=scores['end'],
                text=scores['text'],
                hook_score=scores['hook_score'],
                punchline_score=scores['punchline_score'],
                educational_score=scores['educational_score'],
                emotional_score=scores['emotional_score'],
                caption_readiness=caption_readiness
            )
            content_segments.append(segment)

        return content_segments

    def analyze_full_transcript(self, transcript: List[Dict]) -> Dict:
        """
        Perform complete content analysis on a transcript

        Args:
            transcript: Full transcript with segments

        Returns:
            Complete analysis results with all scores
        """
        # Run all analyses
        hooks = self.detect_hooks(transcript)
        punchlines = self.identify_punchlines(transcript)
        educational = self.detect_educational_content(transcript)
        emotional = self.analyze_emotional_content(transcript)

        # Combine scores
        content_segments = self.combine_viral_scores(
            hooks, punchlines, educational, emotional, transcript
        )

        return {
            'hooks': hooks,
            'punchlines': punchlines,
            'educational_content': educational,
            'emotional_content': emotional,
            'content_segments': content_segments,
            'summary': {
                'total_hooks': len(hooks),
                'total_punchlines': len(punchlines),
                'total_educational': len(educational),
                'total_emotional': len(emotional),
                'total_viral_segments': len(content_segments)
            }
        }