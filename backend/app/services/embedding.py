import numpy as np
import cv2

def extract_embedding(face_image: np.ndarray) -> np.ndarray:
    """
    Extract a simple embedding from a face image using histogram.
    
    In production, this would use ArcFace/InsightFace.
    For now, return a normalized histogram (cheap embedding).
    """
    try:
        # Resize to 128x128
        face_resized = cv2.resize(face_image, (128, 128))
        
        # Convert to grayscale
        gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
        
        # Compute histogram (poor man's embedding)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        
        # Pad to 512 dims (to match expected embedding size)
        embedding = np.zeros(512)
        embedding[:256] = hist
        
        return embedding
        
    except Exception as e:
        print(f"Error extracting embedding: {e}")
        raise
