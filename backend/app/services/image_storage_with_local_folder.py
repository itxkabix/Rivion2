"""
Image Storage Service - Load images from local drive folder and search
Handles file storage, database operations, and similarity search
"""

import os
import shutil
from datetime import datetime, timedelta
import logging
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

# Storage configuration
BASE_UPLOAD_DIR = "backend/uploads"
SESSIONS_DIR = os.path.join(BASE_UPLOAD_DIR, "sessions")
FACES_DIR = os.path.join(BASE_UPLOAD_DIR, "faces")
ARCHIVE_DIR = os.path.join(BASE_UPLOAD_DIR, "archive")

# ===== NEW: Local drive folder configuration =====
# Point this to your images folder
LOCAL_IMAGES_FOLDER = "C:/Users/Lenovo/OneDrive/Documents/GitHub/Rivion/images"  # Change this path!

# Create directories if they don't exist
os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(FACES_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

logger.info(f"Storage directories initialized: {SESSIONS_DIR}")
logger.info(f"Local images folder: {LOCAL_IMAGES_FOLDER}")


def set_local_images_folder(folder_path: str) -> bool:
    """
    Set the local folder where images are stored
    
    Args:
        folder_path: Path to local images folder
    
    Returns:
        True if folder exists and is valid
    """
    global LOCAL_IMAGES_FOLDER
    
    if os.path.exists(folder_path):
        LOCAL_IMAGES_FOLDER = folder_path
        logger.info(f"✅ Local images folder set to: {LOCAL_IMAGES_FOLDER}")
        return True
    else:
        logger.error(f"❌ Folder does not exist: {folder_path}")
        return False


def save_session_image(session_id: str, image_data: bytes) -> str:
    """
    Save captured session image to disk
    
    Args:
        session_id: Unique session identifier
        image_data: Raw image bytes
    
    Returns:
        Path to saved image
    """
    try:
        # Create session directory
        session_dir = os.path.join(SESSIONS_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Save with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"captured_{timestamp}.jpg"
        image_path = os.path.join(session_dir, image_filename)
        
        # Write image to disk
        with open(image_path, 'wb') as f:
            f.write(image_data)
        
        logger.info(f"Session image saved: {image_path}")
        
        return image_path
    
    except Exception as e:
        logger.error(f"Error saving session image: {e}")
        raise


def save_face_image(session_id: str, user_name: str, emotion: str, image_data: bytes) -> str:
    """
    Save detected face image to faces directory
    
    Args:
        session_id: Session ID
        user_name: User's name
        emotion: Detected emotion
        image_data: Face image bytes
    
    Returns:
        Path to saved face image
    """
    try:
        # Create user/emotion directory structure
        user_emotion_dir = os.path.join(FACES_DIR, user_name, emotion)
        os.makedirs(user_emotion_dir, exist_ok=True)
        
        # Create filename with timestamp and unique ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        face_filename = f"{emotion}_{timestamp}_{unique_id}.jpg"
        face_path = os.path.join(user_emotion_dir, face_filename)
        
        # Write face image
        with open(face_path, 'wb') as f:
            f.write(image_data)
        
        logger.info(f"Face image saved: {face_path}")
        
        return face_path
    
    except Exception as e:
        logger.error(f"Error saving face image: {e}")
        raise


def get_images_from_local_folder(emotion: str = None, user_name: str = None) -> list:
    """
    ===== NEW FUNCTION =====
    Load images from local drive folder
    
    Args:
        emotion: Filter by emotion (optional)
        user_name: Filter by user (optional)
    
    Returns:
        List of images from local folder
    """
    try:
        images = []
        
        if not os.path.exists(LOCAL_IMAGES_FOLDER):
            logger.warning(f"Local images folder not found: {LOCAL_IMAGES_FOLDER}")
            return images
        
        logger.info(f"Searching local folder: {LOCAL_IMAGES_FOLDER}")
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(LOCAL_IMAGES_FOLDER):
            for file in files:
                # Check if it's an image file
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                    image_path = os.path.join(root, file)
                    
                    # Extract info from path or filename
                    # Expected structure: emotion/image.jpg or user/emotion/image.jpg
                    relative_path = os.path.relpath(image_path, LOCAL_IMAGES_FOLDER)
                    path_parts = relative_path.split(os.sep)
                    
                    # Determine emotion and user from folder structure
                    detected_emotion = path_parts[0] if len(path_parts) > 0 else "unknown"
                    detected_user = path_parts[1] if len(path_parts) > 2 else user_name or "default"
                    
                    # Apply filters
                    if emotion and detected_emotion.lower() != emotion.lower():
                        continue
                    if user_name and detected_user.lower() != user_name.lower():
                        continue
                    
                    try:
                        stat_info = os.stat(image_path)
                        image_info = {
                            "filename": file,
                            "path": image_path,
                            "emotion": detected_emotion,
                            "user_name": detected_user,
                            "size": stat_info.st_size,
                            "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                            "source": "local_folder"
                        }
                        images.append(image_info)
                        logger.info(f"Found image: {image_path} ({detected_emotion})")
                    except Exception as e:
                        logger.warning(f"Could not read image info: {e}")
        
        logger.info(f"✅ Found {len(images)} images in local folder")
        return images
    
    except Exception as e:
        logger.error(f"Error reading local images: {e}")
        return []


def get_all_stored_images(user_name: str = None) -> list:
    """
    Get all stored images - from backend AND local folder
    
    Args:
        user_name: Optional filter by user name
    
    Returns:
        List of image metadata
    """
    try:
        images = []
        
        # ===== NEW: Get images from local folder =====
        local_images = get_images_from_local_folder(user_name=user_name)
        images.extend(local_images)
        
        # Get images from backend storage
        if user_name:
            user_dir = os.path.join(FACES_DIR, user_name)
            if os.path.exists(user_dir):
                for emotion_folder in os.listdir(user_dir):
                    emotion_path = os.path.join(user_dir, emotion_folder)
                    if os.path.isdir(emotion_path):
                        for image_file in os.listdir(emotion_path):
                            if image_file.endswith(('.jpg', '.png')):
                                image_path = os.path.join(emotion_path, image_file)
                                images.append({
                                    "filename": image_file,
                                    "path": image_path,
                                    "emotion": emotion_folder,
                                    "user_name": user_name,
                                    "size": os.path.getsize(image_path),
                                    "created": datetime.fromtimestamp(os.path.getctime(image_path)).isoformat(),
                                    "source": "backend_storage"
                                })
        else:
            if os.path.exists(FACES_DIR):
                for user_folder in os.listdir(FACES_DIR):
                    user_path = os.path.join(FACES_DIR, user_folder)
                    if os.path.isdir(user_path):
                        for emotion_folder in os.listdir(user_path):
                            emotion_path = os.path.join(user_path, emotion_folder)
                            if os.path.isdir(emotion_path):
                                for image_file in os.listdir(emotion_path):
                                    if image_file.endswith(('.jpg', '.png')):
                                        image_path = os.path.join(emotion_path, image_file)
                                        images.append({
                                            "filename": image_file,
                                            "path": image_path,
                                            "emotion": emotion_folder,
                                            "user_name": user_folder,
                                            "size": os.path.getsize(image_path),
                                            "created": datetime.fromtimestamp(os.path.getctime(image_path)).isoformat(),
                                            "source": "backend_storage"
                                        })
        
        logger.info(f"Found {len(images)} total images (local + backend)")
        return images
    
    except Exception as e:
        logger.error(f"Error retrieving images: {e}")
        return []


def get_images_by_emotion(emotion: str, user_name: str = None) -> list:
    """
    Get all images matching a specific emotion - from local folder AND backend
    
    Args:
        emotion: Emotion to filter by
        user_name: Optional user filter
    
    Returns:
        List of images with matching emotion
    """
    try:
        all_images = get_all_stored_images(user_name)
        matching_images = [img for img in all_images if img['emotion'].lower() == emotion.lower()]
        
        logger.info(f"Found {len(matching_images)} images with emotion: {emotion}")
        return matching_images
    
    except Exception as e:
        logger.error(f"Error filtering by emotion: {e}")
        return []


def get_similar_images(current_emotion: str, user_name: str = None, limit: int = 5) -> list:
    """
    Get similar images based on emotion matching - from local folder AND backend
    
    Args:
        current_emotion: Current detected emotion
        user_name: Optional user filter
        limit: Maximum results to return
    
    Returns:
        List of similar images
    """
    try:
        # Get images with same emotion (highest priority)
        same_emotion = get_images_by_emotion(current_emotion, user_name)
        
        if len(same_emotion) >= limit:
            return same_emotion[:limit]
        
        # If not enough, add related emotions
        emotion_similarity = {
            "happy": ["surprise"],
            "sad": ["neutral", "fear"],
            "angry": ["fear", "disgust"],
            "fear": ["sad", "angry"],
            "surprise": ["happy"],
            "disgust": ["angry", "sad"],
            "neutral": ["sad"]
        }
        
        related_emotions = emotion_similarity.get(current_emotion, [])
        results = same_emotion.copy()
        
        # Add images from related emotions
        for related_emotion in related_emotions:
            if len(results) >= limit:
                break
            related_images = get_images_by_emotion(related_emotion, user_name)
            results.extend(related_images)
        
        logger.info(f"Found {len(results)} similar images for emotion: {current_emotion}")
        return results[:limit]
    
    except Exception as e:
        logger.error(f"Error finding similar images: {e}")
        return []


def read_image_as_base64(image_path: str) -> str:
    """
    Read image file and convert to base64
    
    Args:
        image_path: Path to image file
    
    Returns:
        Base64 encoded image string
    """
    try:
        import base64
        
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return None
        
        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
        
        logger.info(f"Image converted to base64: {image_path}")
        return base64_image
    
    except Exception as e:
        logger.error(f"Error converting image to base64: {e}")
        return None


def get_image_metadata(image_path: str) -> dict:
    """
    Get metadata about an image file
    
    Args:
        image_path: Path to image
    
    Returns:
        Dictionary with file metadata
    """
    try:
        if not os.path.exists(image_path):
            return None
        
        stat_info = os.stat(image_path)
        
        return {
            "filename": os.path.basename(image_path),
            "path": image_path,
            "size_bytes": stat_info.st_size,
            "size_mb": round(stat_info.st_size / (1024 * 1024), 2),
            "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "exists": True
        }
    
    except Exception as e:
        logger.error(f"Error getting image metadata: {e}")
        return None


def get_storage_stats() -> dict:
    """
    Get storage usage statistics from both local folder and backend
    
    Returns:
        Dictionary with storage stats
    """
    try:
        total_size = 0
        total_images = 0
        users = {}
        emotions = {}
        
        # Stats from backend storage
        for root, dirs, files in os.walk(FACES_DIR):
            for file in files:
                if file.endswith(('.jpg', '.png')):
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    total_images += 1
                    
                    parts = file_path.split(os.sep)
                    if len(parts) >= 2:
                        user = parts[-3] if len(parts) > 2 else "unknown"
                        emotion = parts[-2] if len(parts) > 1 else "unknown"
                        
                        if user not in users:
                            users[user] = 0
                        users[user] += 1
                        
                        if emotion not in emotions:
                            emotions[emotion] = 0
                        emotions[emotion] += 1
        
        # Stats from local folder
        local_images = get_all_stored_images()
        for img in local_images:
            if img['source'] == 'local_folder':
                total_images += 1
                total_size += img.get('size', 0)
                user = img['user_name']
                emotion = img['emotion']
                
                if user not in users:
                    users[user] = 0
                users[user] += 1
                
                if emotion not in emotions:
                    emotions[emotion] = 0
                emotions[emotion] += 1
        
        return {
            "total_images": total_images,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "users": users,
            "emotions": emotions,
            "backend_storage_path": FACES_DIR,
            "local_images_path": LOCAL_IMAGES_FOLDER
        }
    
    except Exception as e:
        logger.error(f"Error getting storage stats: {e}")
        return {}


def cleanup_empty_directories():
    """Clean up empty directories in storage"""
    try:
        removed_dirs = 0
        
        for root, dirs, files in os.walk(FACES_DIR, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        removed_dirs += 1
                        logger.info(f"Removed empty directory: {dir_path}")
                except Exception as e:
                    logger.warning(f"Could not remove directory {dir_path}: {e}")
        
        logger.info(f"Cleaned up {removed_dirs} empty directories")
        return removed_dirs
    
    except Exception as e:
        logger.error(f"Error cleaning up directories: {e}")
        return 0
