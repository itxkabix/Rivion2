"""
Backend API endpoint for face emotion detection
Handles face capture, emotion analysis, and similarity search
Compatible with existing emotion.py and services
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import base64
import io
import uuid
from datetime import datetime
import logging
from PIL import Image
import numpy as np
import os
from pathlib import Path

# Import your existing services (matching your actual code)
from app.services.emotion_detection import analyze_emotion
from app.services.face_recognition_service import (
    extract_face_encoding_from_bytes,
    find_matching_faces,
    index_images_folder
)
from app.services.image_storage import (
    get_images_from_local_folder,
    get_similar_images,
    read_image_as_base64,
    get_storage_stats,
    LOCAL_IMAGES_FOLDER
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1", tags=["face-emotion"])

# Set local images folder path
LOCAL_IMAGES_FOLDER_PATH = "frontend/Images"

# ==================== FACE CAPTURE & ANALYSIS ====================

@router.post("/analyze-face")
async def analyze_face(
    image: UploadFile = File(...),
    user_name: str = Form(...),
    privacy_agreed: bool = Form(...)
):
    """
    Analyze face from uploaded image
    
    Args:
        image: Uploaded image file (JPG/PNG)
        user_name: User's name
        privacy_agreed: Privacy policy agreement
    
    Returns:
        JSON with emotion analysis results
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Read image file
        image_data = await image.read()
        
        # Save temporary image file
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_image_path = os.path.join(temp_dir, f"{session_id}.jpg")
        
        # Write image to temp file
        with open(temp_image_path, 'wb') as f:
            f.write(image_data)
        
        # Convert to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        logger.info(f"Processing image for session: {session_id}")
        
        # ===== STEP 1: Extract face encoding from captured image =====
        face_encodings = extract_face_encoding_from_bytes(image_data)
        
        if not face_encodings:
            logger.warning(f"No face detected in captured image for session {session_id}")
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "No face detected in the image. Please ensure your face is clearly visible.",
                    "session_id": session_id
                }
            )
        
        # Use the first (largest) face if multiple faces detected
        query_encoding = face_encodings[0]
        logger.info(f"✅ Face encoding extracted from captured image")
        
        # ===== STEP 2: Find matching faces in images folder =====
        # Get project root to find images folder
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent
        images_folder = project_root / LOCAL_IMAGES_FOLDER.replace('\\', '/')
        
        logger.info(f"Searching for matching faces in: {images_folder}")
        matching_faces = find_matching_faces(
            query_encoding=query_encoding,
            images_folder=str(images_folder),
            tolerance=0.6,  # Adjustable threshold
            max_results=10
        )
        
        if not matching_faces:
            logger.warning(f"No matching faces found for session {session_id}")
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "session_id": session_id,
                    "user_name": user_name,
                    "message": "No matching faces found in the images folder. Try capturing a clearer image or add more images to the folder.",
                    "matched_images": [],
                    "dominant_emotion": "neutral",
                    "emotion_confidence": 0.0,
                    "all_emotions": {},
                    "statement": "No matching faces found."
                }
            )
        
        logger.info(f"✅ Found {len(matching_faces)} matching face(s)")
        
        # ===== STEP 3: Extract emotions from matched images =====
        matched_images_with_emotions = []
        emotion_results = []
        
        for match in matching_faces:
            image_path = match['image_path']
            similarity = match['similarity']
            
            # Analyze emotion from the matched image (not the captured image)
            emotion, emotion_dist, emotion_conf = analyze_emotion(image_path)
            
            # Get image metadata
            from pathlib import Path as PathLib
            image_path_obj = PathLib(image_path)
            filename = image_path_obj.name
            
            # Detect emotion from folder name if emotion detection failed
            if emotion == 'neutral' and emotion_conf < 0.5:
                path_parts = str(image_path).lower().split('/')
                for part in path_parts:
                    if part in ['happy', 'sad', 'angry', 'fear', 'surprise', 'disgust', 'neutral']:
                        emotion = part
                        emotion_conf = 0.8
                        break
            
            # Convert to base64
            base64_data = read_image_as_base64(image_path)
            
            if base64_data:
                matched_images_with_emotions.append({
                    "filename": filename,
                    "emotion": emotion,
                    "confidence": float(emotion_conf),
                    "similarity": float(similarity),
                    "source": "local_folder",
                    "image_base64": base64_data,
                    "path": image_path
                })
                
                emotion_results.append({
                    'emotion': emotion,
                    'confidence': emotion_conf
                })
        
        # ===== STEP 4: Aggregate emotions from matched images =====
        if emotion_results:
            # Count emotions
            emotion_counts = {}
            total_confidence = 0.0
            for result in emotion_results:
                emotion = result['emotion']
                conf = result['confidence']
                if emotion not in emotion_counts:
                    emotion_counts[emotion] = {'count': 0, 'total_conf': 0.0}
                emotion_counts[emotion]['count'] += 1
                emotion_counts[emotion]['total_conf'] += conf
                total_confidence += conf
            
            # Find dominant emotion
            dominant_emotion = max(emotion_counts, key=lambda x: emotion_counts[x]['count'])
            dominant_count = emotion_counts[dominant_emotion]['count']
            dominant_confidence = emotion_counts[dominant_emotion]['total_conf'] / dominant_count if dominant_count > 0 else 0.0
            
            # Build distribution
            total_matches = len(emotion_results)
            all_emotions = {
                emotion: counts['count'] / total_matches
                for emotion, counts in emotion_counts.items()
            }
        else:
            dominant_emotion = 'neutral'
            dominant_confidence = 0.0
            all_emotions = {}
        
        logger.info(f"✅ Aggregated emotion: {dominant_emotion} ({dominant_confidence*100:.1f}%)")
        
        # Generate emotion statement
        emotion_statement = generate_emotion_statement(dominant_emotion, dominant_confidence)
        
        # Prepare response
        response_data = {
            "success": True,
            "session_id": session_id,
            "user_name": user_name,
            "dominant_emotion": dominant_emotion,
            "emotion_confidence": float(dominant_confidence),
            "all_emotions": all_emotions,
            "statement": emotion_statement,
            "captured_at": datetime.utcnow().isoformat(),
            "image_base64": base64_image,
            "matched_count": len(matched_images_with_emotions),
            "similar_images": matched_images_with_emotions  # Matched faces with their emotions
        }
        
        logger.info(f"Analysis complete for session {session_id}")
        
        # Clean up temp file
        try:
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
        except Exception as e:
            logger.warning(f"Could not delete temp file: {e}")
        
        return JSONResponse(
            status_code=200,
            content=response_data
        )
        
    except Exception as e:
        logger.error(f"Error analyzing face: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error processing image: {str(e)}"
            }
        )


@router.post("/search")
async def search_faces(
    image: UploadFile = File(...),
    user_name: str = Form(...)
):
    """
    Search for similar faces and analyze emotion
    
    Args:
        image: Uploaded image file
        user_name: User's name for logging
    
    Returns:
        Emotion analysis and similar faces
    """
    try:
        image_data = await image.read()
        
        # Save temporary image file
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        
        session_id = str(uuid.uuid4())
        temp_image_path = os.path.join(temp_dir, f"{session_id}.jpg")
        
        with open(temp_image_path, 'wb') as f:
            f.write(image_data)
        
        logger.info(f"Searching similar faces for user: {user_name}")
        
        # Analyze emotion
        dominant_emotion, emotion_dist, confidence = analyze_emotion(temp_image_path)
        
        if dominant_emotion == 'neutral' and confidence == 0.0:
            logger.warning(f"Analysis failed for user {user_name}")
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Could not analyze image",
                    "similar_faces": []
                }
            )
        
        logger.info(f"Found emotion: {dominant_emotion}")
        
        emotion_statement = generate_emotion_statement(dominant_emotion, confidence)
        
        # For now, return empty similar faces (implement with vector DB later)
        similar_faces = []
        
        response_data = {
            "success": True,
            "user_name": user_name,
            "session_id": session_id,
            "dominant_emotion": dominant_emotion,
            "emotion_confidence": float(confidence),
            "all_emotions": emotion_dist,
            "statement": emotion_statement,
            "similar_faces": similar_faces,
            "searched_at": datetime.utcnow().isoformat()
        }
        
        # Clean up temp file
        try:
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
        except Exception as e:
            logger.warning(f"Could not delete temp file: {e}")
        
        return JSONResponse(
            status_code=200,
            content=response_data
        )
        
    except Exception as e:
        logger.error(f"Error searching faces: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error searching: {str(e)}",
                "similar_faces": []
            }
        )


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details by session ID"""
    try:
        logger.info(f"Fetching session: {session_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "session_id": session_id,
                "status": "Session retrieved successfully"
            }
        )
    except Exception as e:
        logger.error(f"Error fetching session: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Error fetching session"}
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "face-emotion-analyzer",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@router.get("/local-images")
async def get_local_images(emotion: str = None):
    """
    Get images from local folder (frontend/Images/)
    
    Args:
        emotion: Optional emotion filter (happy, sad, angry, etc.)
    
    Returns:
        List of images with base64 encoded data
    """
    try:
        logger.info(f"Fetching local images (emotion filter: {emotion})")
        
        # Get images from local folder
        images = get_images_from_local_folder(emotion=emotion)
        
        # Convert to base64 and prepare response
        result_images = []
        for img in images[:10]:  # Max 10 results
            base64_data = read_image_as_base64(img['path'])
            if base64_data:
                result_images.append({
                    "filename": img['filename'],
                    "emotion": img['emotion'],
                    "confidence": img.get('confidence', 0.8),
                    "source": img['source'],
                    "image_base64": base64_data,
                    "size": img.get('size', 0),
                    "created": img.get('created', '')
                })
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "count": len(result_images),
                "images": result_images,
                "folder_path": LOCAL_IMAGES_FOLDER_PATH
            }
        )
    
    except Exception as e:
        logger.error(f"Error fetching local images: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error fetching images: {str(e)}",
                "images": []
            }
        )


@router.get("/storage-stats")
async def get_storage_statistics():
    """
    Get storage statistics from both local folder and backend storage
    
    Returns:
        Storage statistics including total images, size, users, emotions
    """
    try:
        logger.info("Fetching storage statistics")
        
        stats = get_storage_stats()
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "stats": stats
            }
        )
    
    except Exception as e:
        logger.error(f"Error fetching storage stats: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error fetching stats: {str(e)}",
                "stats": {}
            }
        )


# ==================== HELPER FUNCTIONS ====================

def generate_emotion_statement(emotion: str, confidence: float) -> str:
    """
    Generate human-readable emotion statement
    
    Args:
        emotion: Emotion label ('happy', 'sad', 'angry', 'fear', 'neutral', 'disgust', 'surprise')
        confidence: Confidence score (0-1)
    
    Returns:
        Human-readable statement with emoji
    """
    emotion_descriptions = {
        "happy": "😊 You look happy and cheerful!",
        "sad": "😔 You seem to be feeling sad.",
        "angry": "😠 You appear to be feeling angry.",
        "fear": "😟 You seem fearful or anxious.",
        "surprise": "😮 You look surprised!",
        "disgust": "😕 You seem disgusted.",
        "neutral": "😐 Your expression is neutral.",
        "disgust": "😕 You seem disgusted."
    }
    
    confidence_pct = int(confidence * 100)
    base_statement = emotion_descriptions.get(emotion, "Your emotional state is unclear.")
    
    return f"{base_statement} (Confidence: {confidence_pct}%)"
