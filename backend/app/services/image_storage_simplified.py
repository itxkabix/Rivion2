"""
Image Storage Service - SIMPLIFIED VERSION
Automatically detects emotion from filenames
Works with ANY folder structure
"""

import os
import base64
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)

# Storage configuration
BASE_UPLOAD_DIR = "backend/uploads"
SESSIONS_DIR = os.path.join(BASE_UPLOAD_DIR, "sessions")
FACES_DIR = os.path.join(BASE_UPLOAD_DIR, "faces")
ARCHIVE_DIR = os.path.join(BASE_UPLOAD_DIR, "archive")

# ===== YOUR LOCAL IMAGES FOLDER =====
# Change this to your actual folder path (use forward slashes!)
LOCAL_IMAGES_FOLDER = "C:/Users/Lenovo/OneDrive/Documents/GitHub/Rivion/frontend/Images"

# Create directories
os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(FACES_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

logger.info(f"✅ Storage initialized: {SESSIONS_DIR}")
logger.info(f"✅ Local images folder: {LOCAL_IMAGES_FOLDER}")


def set_local_images_folder(folder_path: str) -> bool:
    """Set the local folder where images are stored"""
    global LOCAL_IMAGES_FOLDER
    
    # Convert backslashes to forward slashes
    folder_path = folder_path.replace("\\", "/")
    
    if os.path.exists(folder_path):
        LOCAL_IMAGES_FOLDER = folder_path
        logger.info(f"✅ Images folder set to: {LOCAL_IMAGES_FOLDER}")
        return True
    else:
        logger.error(f"❌ Folder not found: {folder_path}")
        return False


def detect_emotion_from_filename(filename: str) -> str:
    """
    Detect emotion from filename or use 'default'
    Checks if filename contains emotion keywords
    """
    emotions = ["happy", "sad", "angry", "fear", "surprise", "disgust", "neutral"]
    filename_lower = filename.lower()
    
    for emotion in emotions:
        if emotion in filename_lower:
            return emotion
    
    return "neutral"  # Default emotion


def detect_emotion_from_folder(filepath: str) -> str:
    """
    Try to detect emotion from folder structure
    Example: /happy/image.jpg -> "happy"
    """
    path_parts = filepath.split(os.sep)
    
    emotions = ["happy", "sad", "angry", "fear", "surprise", "disgust", "neutral"]
    
    for part in path_parts:
        if part.lower() in emotions:
            return part.lower()
    
    return None


def get_images_from_local_folder(emotion: str = None, user_name: str = None) -> list:
    """
    Load ALL images from local folder
    Automatically detects emotion from folder or filename
    Works with ANY folder structure!
    """
    try:
        images = []
        
        if not os.path.exists(LOCAL_IMAGES_FOLDER):
            logger.warning(f"❌ Folder not found: {LOCAL_IMAGES_FOLDER}")
            return images
        
        logger.info(f"🔍 Scanning folder: {LOCAL_IMAGES_FOLDER}")
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(LOCAL_IMAGES_FOLDER):
            for file in files:
                # Check if it's an image
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')):
                    image_path = os.path.join(root, file)
                    
                    # Try to detect emotion from folder structure first
                    detected_emotion = detect_emotion_from_folder(image_path)
                    
                    # If not found in folder, try filename
                    if not detected_emotion:
                        detected_emotion = detect_emotion_from_filename(file)
                    
                    # Apply emotion filter if specified
                    if emotion and detected_emotion.lower() != emotion.lower():
                        continue
                    
                    # Apply user filter if specified
                    if user_name:
                        if user_name.lower() not in image_path.lower():
                            continue
                    
                    try:
                        stat_info = os.stat(image_path)
                        image_info = {
                            "filename": file,
                            "path": image_path,
                            "emotion": detected_emotion,
                            "user_name": user_name or "default",
                            "size": stat_info.st_size,
                            "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                            "source": "local_folder"
                        }
                        images.append(image_info)
                        logger.info(f"   ✅ {detected_emotion}: {file}")
                    except Exception as e:
                        logger.warning(f"   ⚠️  Could not read: {file} - {e}")
        
        logger.info(f"✅ Found {len(images)} images total")
        return images
    
    except Exception as e:
        logger.error(f"❌ Error scanning folder: {e}")
        return []


def get_all_stored_images(user_name: str = None) -> list:
    """Get all images from local folder + backend"""
    try:
        images = []
        
        # Get from local folder
        local_images = get_images_from_local_folder(user_name=user_name)
        images.extend(local_images)
        logger.info(f"📊 Total images: {len(images)}")
        
        return images
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return []


def get_images_by_emotion(emotion: str, user_name: str = None) -> list:
    """Get all images matching an emotion"""
    try:
        images = get_images_from_local_folder(emotion=emotion, user_name=user_name)
        logger.info(f"   Found {len(images)} {emotion} images")
        return images
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return []


def get_similar_images(current_emotion: str, user_name: str = None, limit: int = 10) -> list:
    """
    Get similar images based on emotion
    First returns exact matches, then similar emotions
    """
    try:
        # Get exact emotion matches
        same_emotion = get_images_by_emotion(current_emotion, user_name)
        logger.info(f"   Exact matches ({current_emotion}): {len(same_emotion)}")
        
        if len(same_emotion) >= limit:
            return same_emotion[:limit]
        
        # If not enough, add related emotions
        emotion_similarity = {
            "happy": ["surprise", "neutral"],
            "sad": ["neutral", "fear"],
            "angry": ["fear", "disgust"],
            "fear": ["sad", "angry"],
            "surprise": ["happy", "neutral"],
            "disgust": ["angry", "sad"],
            "neutral": ["happy", "sad"]
        }
        
        related_emotions = emotion_similarity.get(current_emotion, [])
        results = same_emotion.copy()
        
        # Add from related emotions
        for related in related_emotions:
            if len(results) >= limit:
                break
            related_images = get_images_by_emotion(related, user_name)
            results.extend(related_images)
            logger.info(f"   Added {len(related_images)} {related} images")
        
        logger.info(f"   Total results: {len(results)}")
        return results[:limit]
    
    except Exception as e:
        logger.error(f"❌ Error finding similar: {e}")
        return []


def read_image_as_base64(image_path: str) -> str:
    """Convert image to base64 for frontend display"""
    try:
        if not os.path.exists(image_path):
            logger.error(f"❌ Image not found: {image_path}")
            return None
        
        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
        
        return base64_image
    
    except Exception as e:
        logger.error(f"❌ Error converting to base64: {e}")
        return None


def save_session_image(session_id: str, image_data: bytes) -> str:
    """Save captured image to backend"""
    try:
        session_dir = os.path.join(SESSIONS_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"captured_{timestamp}.jpg"
        image_path = os.path.join(session_dir, image_filename)
        
        with open(image_path, 'wb') as f:
            f.write(image_data)
        
        logger.info(f"✅ Saved: {image_path}")
        return image_path
    
    except Exception as e:
        logger.error(f"❌ Error saving: {e}")
        raise


def save_face_image(session_id: str, user_name: str, emotion: str, image_data: bytes) -> str:
    """Save face to backend storage"""
    try:
        user_emotion_dir = os.path.join(FACES_DIR, user_name, emotion)
        os.makedirs(user_emotion_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        face_filename = f"{emotion}_{timestamp}_{unique_id}.jpg"
        face_path = os.path.join(user_emotion_dir, face_filename)
        
        with open(face_path, 'wb') as f:
            f.write(image_data)
        
        logger.info(f"✅ Face saved: {face_path}")
        return face_path
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise


def get_storage_stats() -> dict:
    """Get storage statistics"""
    try:
        total_images = 0
        total_size = 0
        emotions = {}
        
        images = get_all_stored_images()
        
        for img in images:
            total_images += 1
            total_size += img.get('size', 0)
            
            emotion = img['emotion']
            if emotion not in emotions:
                emotions[emotion] = 0
            emotions[emotion] += 1
        
        return {
            "total_images": total_images,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "emotions": emotions,
            "local_images_path": LOCAL_IMAGES_FOLDER
        }
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {}


def cleanup_empty_directories():
    """Clean up empty folders"""
    try:
        removed = 0
        for root, dirs, files in os.walk(FACES_DIR, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        removed += 1
                except:
                    pass
        return removed
    except:
        return 0
