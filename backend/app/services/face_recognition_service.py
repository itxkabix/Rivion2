"""
Face Recognition Service
Uses face_recognition library for accurate face matching
Extracts face embeddings and compares them to find exact matches
Falls back to DeepFace if face_recognition is not available
"""

import numpy as np
import cv2
from PIL import Image
import logging
from pathlib import Path
import pickle
import os

logger = logging.getLogger(__name__)

# Try to import face_recognition
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
    logger.info("✅ face_recognition library available")
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logger.warning("⚠️ face_recognition not available, will use DeepFace fallback")
    try:
        from deepface import DeepFace
        DEEPFACE_AVAILABLE = True
        logger.info("✅ DeepFace available as fallback")
    except ImportError:
        DEEPFACE_AVAILABLE = False
        logger.error("❌ Neither face_recognition nor DeepFace available!")

# Cache for face encodings from images folder
FACE_ENCODINGS_CACHE = {}
CACHE_FILE = "backend/face_encodings_cache.pkl"


def load_face_encodings_cache():
    """Load cached face encodings from disk"""
    global FACE_ENCODINGS_CACHE
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'rb') as f:
                FACE_ENCODINGS_CACHE = pickle.load(f)
            logger.info(f"Loaded {len(FACE_ENCODINGS_CACHE)} face encodings from cache")
        else:
            FACE_ENCODINGS_CACHE = {}
    except Exception as e:
        logger.warning(f"Could not load face encodings cache: {e}")
        FACE_ENCODINGS_CACHE = {}


def save_face_encodings_cache():
    """Save face encodings cache to disk"""
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(FACE_ENCODINGS_CACHE, f)
        logger.info(f"Saved {len(FACE_ENCODINGS_CACHE)} face encodings to cache")
    except Exception as e:
        logger.warning(f"Could not save face encodings cache: {e}")


def extract_face_encoding(image_path: str) -> list:
    """
    Extract face encoding from an image
    
    Args:
        image_path: Path to image file
        
    Returns:
        List of face encodings (one per face in image)
    """
    try:
        if FACE_RECOGNITION_AVAILABLE:
            # Use face_recognition library
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                logger.debug(f"No faces found in {image_path}")
                return []
            
            face_encodings = face_recognition.face_encodings(image, face_locations)
            logger.debug(f"Found {len(face_encodings)} face(s) in {image_path}")
            return face_encodings
            
        elif DEEPFACE_AVAILABLE:
            # Fallback to DeepFace
            from deepface import DeepFace
            try:
                # DeepFace returns embedding directly
                embedding = DeepFace.represent(
                    img_path=image_path,
                    model_name='VGG-Face',  # or 'Facenet', 'OpenFace', etc.
                    enforce_detection=False
                )
                # DeepFace returns list of dicts, extract embedding
                if isinstance(embedding, list) and len(embedding) > 0:
                    return [np.array(embedding[0]['embedding'])]
                elif isinstance(embedding, dict):
                    return [np.array(embedding['embedding'])]
                return []
            except Exception as e:
                logger.debug(f"DeepFace could not find face in {image_path}: {e}")
                return []
        else:
            logger.error("No face recognition library available!")
            return []
        
    except Exception as e:
        logger.error(f"Error extracting face encoding from {image_path}: {e}")
        return []


def extract_face_encoding_from_bytes(image_bytes: bytes) -> list:
    """
    Extract face encoding from image bytes
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        List of face encodings
    """
    try:
        import io
        import tempfile
        
        if FACE_RECOGNITION_AVAILABLE:
            # Use face_recognition
            from PIL import Image
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image_array = np.array(image)
            
            face_locations = face_recognition.face_locations(image_array)
            if not face_locations:
                logger.debug("No faces found in uploaded image")
                return []
            
            face_encodings = face_recognition.face_encodings(image_array, face_locations)
            logger.debug(f"Found {len(face_encodings)} face(s) in uploaded image")
            return face_encodings
            
        elif DEEPFACE_AVAILABLE:
            # Fallback to DeepFace
            from deepface import DeepFace
            # Save to temp file (DeepFace needs file path)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_file.write(image_bytes)
                tmp_path = tmp_file.name
            
            try:
                embedding = DeepFace.represent(
                    img_path=tmp_path,
                    model_name='VGG-Face',
                    enforce_detection=False
                )
                if isinstance(embedding, list) and len(embedding) > 0:
                    return [np.array(embedding[0]['embedding'])]
                elif isinstance(embedding, dict):
                    return [np.array(embedding['embedding'])]
                return []
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        else:
            logger.error("No face recognition library available!")
            return []
        
    except Exception as e:
        logger.error(f"Error extracting face encoding from bytes: {e}")
        return []


def compare_faces(encoding1: np.ndarray, encoding2: np.ndarray, tolerance: float = 0.6) -> bool:
    """
    Compare two face encodings to see if they match
    
    Args:
        encoding1: First face encoding
        encoding2: Second face encoding
        tolerance: Distance threshold (lower = more strict, default 0.6)
        
    Returns:
        True if faces match, False otherwise
    """
    try:
        if FACE_RECOGNITION_AVAILABLE:
            distance = face_recognition.face_distance([encoding1], encoding2)[0]
            return distance <= tolerance
        else:
            # Use cosine similarity for DeepFace embeddings
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity([encoding1], [encoding2])[0][0]
            distance = 1.0 - similarity
            return distance <= tolerance
    except Exception as e:
        logger.error(f"Error comparing faces: {e}")
        return False


def get_face_distance(encoding1: np.ndarray, encoding2: np.ndarray) -> float:
    """
    Get the distance between two face encodings (lower = more similar)
    
    Args:
        encoding1: First face encoding
        encoding2: Second face encoding
        
    Returns:
        Distance value (0.0 = identical, higher = more different)
    """
    try:
        if FACE_RECOGNITION_AVAILABLE:
            distance = face_recognition.face_distance([encoding1], encoding2)[0]
            return float(distance)
        else:
            # Use cosine similarity for DeepFace embeddings
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity([encoding1], [encoding2])[0][0]
            distance = 1.0 - similarity
            return float(distance)
    except Exception as e:
        logger.error(f"Error calculating face distance: {e}")
        return 1.0


def index_images_folder(images_folder: str, force_reindex: bool = False) -> dict:
    """
    Index all faces in the images folder
    
    Args:
        images_folder: Path to images folder
        force_reindex: If True, reindex even if cache exists
        
    Returns:
        Dictionary mapping image_path -> list of face encodings
    """
    global FACE_ENCODINGS_CACHE
    
    # Load cache if not already loaded
    if not FACE_ENCODINGS_CACHE:
        load_face_encodings_cache()
    
    images_folder = Path(images_folder).resolve()
    
    if not images_folder.exists():
        logger.warning(f"Images folder not found: {images_folder}")
        return {}
    
    # Check if we need to reindex
    if not force_reindex and FACE_ENCODINGS_CACHE:
        logger.info(f"Using cached face encodings ({len(FACE_ENCODINGS_CACHE)} images)")
        return FACE_ENCODINGS_CACHE
    
    logger.info(f"Indexing faces in: {images_folder}")
    
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')
    indexed = {}
    total_faces = 0
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(str(images_folder)):
        for file in files:
            if file.lower().endswith(valid_extensions):
                image_path = Path(root) / file
                image_path_str = str(image_path)
                
                # Skip if already indexed and file hasn't changed
                if image_path_str in FACE_ENCODINGS_CACHE and not force_reindex:
                    indexed[image_path_str] = FACE_ENCODINGS_CACHE[image_path_str]
                    continue
                
                # Extract face encodings
                encodings = extract_face_encoding(image_path_str)
                
                if encodings:
                    indexed[image_path_str] = encodings
                    total_faces += len(encodings)
                    logger.debug(f"Indexed {len(encodings)} face(s) from {file}")
                else:
                    logger.debug(f"No faces found in {file}")
    
    # Update cache
    FACE_ENCODINGS_CACHE = indexed
    save_face_encodings_cache()
    
    logger.info(f"✅ Indexed {len(indexed)} images with {total_faces} total faces")
    return indexed


def find_matching_faces(
    query_encoding: np.ndarray,
    images_folder: str,
    tolerance: float = 0.6,
    max_results: int = 10
) -> list:
    """
    Find matching faces in the images folder
    
    Args:
        query_encoding: Face encoding from captured image
        images_folder: Path to images folder
        tolerance: Distance threshold for matching
        max_results: Maximum number of results to return
        
    Returns:
        List of matching images with similarity scores
    """
    try:
        # Index images folder
        indexed_faces = index_images_folder(images_folder)
        
        if not indexed_faces:
            logger.warning("No faces indexed in images folder")
            return []
        
        matches = []
        
        # Compare query encoding with all indexed faces
        for image_path, encodings in indexed_faces.items():
            for encoding in encodings:
                distance = get_face_distance(query_encoding, encoding)
                
                if distance <= tolerance:
                    similarity = 1.0 - distance  # Convert distance to similarity (0-1)
                    matches.append({
                        'image_path': image_path,
                        'similarity': similarity,
                        'distance': distance
                    })
        
        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Remove duplicates (same image path, keep best match)
        seen_paths = set()
        unique_matches = []
        for match in matches:
            if match['image_path'] not in seen_paths:
                seen_paths.add(match['image_path'])
                unique_matches.append(match)
                if len(unique_matches) >= max_results:
                    break
        
        logger.info(f"Found {len(unique_matches)} matching faces")
        return unique_matches
        
    except Exception as e:
        logger.error(f"Error finding matching faces: {e}", exc_info=True)
        return []


# Initialize cache on import
load_face_encodings_cache()

