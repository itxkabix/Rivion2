import torch
import numpy as np
from torchvision import transforms
from PIL import Image
import logging

logger = logging.getLogger(__name__)

# Emotion labels
EMOTION_LABELS = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

def analyze_emotion(image_path: str) -> tuple:
    """
    Analyze emotion in image
    
    Returns:
        (dominant_emotion, emotion_distribution_dict, confidence)
    """
    try:
        # Load image
        image = Image.open(image_path).convert('RGB')
        
        # Placeholder: In real implementation, load ViT model
        # For now, return mock results
        
        # Mock emotion distribution
        emotion_dist = {
            'happy': 0.45,
            'sad': 0.15,
            'angry': 0.10,
            'neutral': 0.20,
            'fear': 0.05,
            'surprise': 0.03,
            'disgust': 0.02,
        }
        
        dominant_emotion = max(emotion_dist, key=emotion_dist.get)
        confidence = emotion_dist[dominant_emotion]
        
        logger.info(f"Emotion analyzed: {dominant_emotion} ({confidence*100:.1f}%)")
        
        return dominant_emotion, emotion_dist, confidence
        
    except Exception as e:
        logger.error(f"Emotion analysis error: {e}")
        return 'neutral', {}, 0.0

def aggregate_emotions(emotion_results: list) -> tuple:
    """
    Aggregate emotions from multiple images
    
    Returns:
        (dominant_emotion, emotion_confidence, emotion_distribution)
    """
    if not emotion_results:
        return 'neutral', 0.0, {}
    
    # Count emotions
    emotion_counts = {}
    for result in emotion_results:
        emotion = result['emotion']
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    # Find dominant
    dominant_emotion = max(emotion_counts, key=emotion_counts.get)
    total_images = len(emotion_results)
    emotion_confidence = emotion_counts[dominant_emotion] / total_images
    
    # Build distribution
    emotion_distribution = {
        emotion: count / total_images
        for emotion, count in emotion_counts.items()
    }
    
    logger.info(f"Aggregated emotion: {dominant_emotion} ({emotion_confidence*100:.1f}%)")
    
    return dominant_emotion, emotion_confidence, emotion_distribution
