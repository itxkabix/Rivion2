"""
Backend API endpoint for face emotion detection with image storage and retrieval
Handles face capture, emotion analysis, similarity search, and database operations
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import base64
import io
import uuid
from datetime import datetime
import logging
import os

# Import services
from app.services.emotion import analyze_emotion
# NEW: Import storage service
from app.services.image_storage import (
    save_session_image, 
    save_face_image, 
    get_similar_images,
    read_image_as_base64,
    get_storage_stats,
    get_all_stored_images
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1", tags=["face-emotion"])

# ==================== FACE CAPTURE & ANALYSIS ====================

@router.post("/analyze-face")
async def analyze_face(
    image: UploadFile = File(...),
    user_name: str = Form(...),
    privacy_agreed: bool = Form(...)
):
    """
    Analyze face from uploaded image and store in backend
    
    Args:
        image: Uploaded image file (JPG/PNG)
        user_name: User's name
        privacy_agreed: Privacy policy agreement
    
    Returns:
        JSON with emotion analysis + similar images found in database
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Read image file
        image_data = await image.read()
        
        logger.info(f"Processing image for session: {session_id} | User: {user_name}")
        
        # ===== STEP 1: Save session image to backend =====
        session_image_path = save_session_image(session_id, image_data)
        logger.info(f"✅ Session image saved: {session_image_path}")
        
        # ===== STEP 2: Save temporary file for emotion analysis =====
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        temp_image_path = os.path.join(temp_dir, f"{session_id}.jpg")
        
        with open(temp_image_path, 'wb') as f:
            f.write(image_data)
        
        # ===== STEP 3: Analyze emotion =====
        dominant_emotion, emotion_dist, confidence = analyze_emotion(temp_image_path)
        
        if dominant_emotion == 'neutral' and confidence == 0.0:
            logger.warning(f"❌ Emotion analysis failed for session {session_id}")
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Could not analyze image. Please ensure it contains a clear face.",
                    "session_id": session_id
                }
            )
        
        logger.info(f"✅ Emotion detected: {dominant_emotion} ({confidence*100:.1f}%)")
        
        # ===== STEP 4: Save face image to backend storage =====
        face_image_path = save_face_image(
            session_id=session_id,
            user_name=user_name,
            emotion=dominant_emotion,
            image_data=image_data
        )
        logger.info(f"✅ Face image stored: {face_image_path}")
        
        # ===== STEP 5: Search for similar images in database =====
        similar_images = get_similar_images(
            current_emotion=dominant_emotion,
            user_name=user_name,
            limit=5
        )
        
        # Convert similar images to include base64 for display
        similar_images_with_data = []
        for img in similar_images:
            try:
                img_base64 = read_image_as_base64(img['path'])
                similar_images_with_data.append({
                    "filename": img['filename'],
                    "emotion": img['emotion'],
                    "user_name": img['user_name'],
                    "created": img['created'],
                    "image_base64": img_base64 if img_base64 else None,
                    "thumbnail_url": f"/api/v1/image/{img['filename']}"
                })
            except Exception as e:
                logger.warning(f"Could not convert similar image: {e}")
        
        logger.info(f"✅ Found {len(similar_images_with_data)} similar images")
        
        # ===== STEP 6: Generate emotion statement =====
        emotion_statement = generate_emotion_statement(dominant_emotion, confidence)
        
        # ===== STEP 7: Prepare response =====
        response_data = {
            "success": True,
            "session_id": session_id,
            "user_name": user_name,
            "dominant_emotion": dominant_emotion,
            "emotion_confidence": float(confidence),
            "all_emotions": emotion_dist,
            "statement": emotion_statement,
            "captured_at": datetime.utcnow().isoformat(),
            "image_stored": True,
            "stored_image_path": face_image_path,
            "similar_images_found": len(similar_images_with_data),
            "similar_images": similar_images_with_data
        }
        
        logger.info(f"✅ Analysis complete for session {session_id}")
        
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
        logger.error(f"❌ Error analyzing face: {str(e)}", exc_info=True)
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
    Search for similar faces in database
    
    Args:
        image: Uploaded image file
        user_name: User's name for logging
    
    Returns:
        Emotion analysis + similar faces from database
    """
    try:
        session_id = str(uuid.uuid4())
        image_data = await image.read()
        
        logger.info(f"Search request - Session: {session_id} | User: {user_name}")
        
        # Save temporary image for analysis
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        temp_image_path = os.path.join(temp_dir, f"{session_id}.jpg")
        
        with open(temp_image_path, 'wb') as f:
            f.write(image_data)
        
        # Analyze emotion
        dominant_emotion, emotion_dist, confidence = analyze_emotion(temp_image_path)
        
        if dominant_emotion == 'neutral' and confidence == 0.0:
            logger.warning(f"Analysis failed for session {session_id}")
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Could not analyze image",
                    "similar_faces": []
                }
            )
        
        logger.info(f"✅ Emotion found: {dominant_emotion}")
        
        # ===== SEARCH DATABASE FOR SIMILAR IMAGES =====
        similar_images = get_similar_images(
            current_emotion=dominant_emotion,
            user_name=user_name,
            limit=10
        )
        
        # Prepare image data for frontend
        similar_images_with_data = []
        for img in similar_images:
            try:
                img_base64 = read_image_as_base64(img['path'])
                similar_images_with_data.append({
                    "filename": img['filename'],
                    "emotion": img['emotion'],
                    "user_name": img['user_name'],
                    "created": img['created'],
                    "image_base64": img_base64 if img_base64 else None
                })
            except Exception as e:
                logger.warning(f"Could not process image: {e}")
        
        emotion_statement = generate_emotion_statement(dominant_emotion, confidence)
        
        response_data = {
            "success": True,
            "session_id": session_id,
            "user_name": user_name,
            "dominant_emotion": dominant_emotion,
            "emotion_confidence": float(confidence),
            "all_emotions": emotion_dist,
            "statement": emotion_statement,
            "similar_images_found": len(similar_images_with_data),
            "similar_images": similar_images_with_data,
            "searched_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ Search complete - Found {len(similar_images_with_data)} matches")
        
        # Clean up
        try:
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
        except:
            pass
        
        return JSONResponse(status_code=200, content=response_data)
        
    except Exception as e:
        logger.error(f"❌ Error searching faces: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error searching: {str(e)}",
                "similar_faces": []
            }
        )


@router.get("/all-images")
async def get_all_images(user_name: str = None):
    """
    Get all stored images from backend database
    
    Args:
        user_name: Optional filter by user
    
    Returns:
        List of all stored images
    """
    try:
        images = get_all_stored_images(user_name)
        
        # Convert to include base64
        images_with_data = []
        for img in images:
            try:
                img_base64 = read_image_as_base64(img['path'])
                images_with_data.append({
                    **img,
                    "image_base64": img_base64 if img_base64 else None
                })
            except:
                pass
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "total_images": len(images_with_data),
                "images": images_with_data
            }
        )
    except Exception as e:
        logger.error(f"Error getting all images: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e), "images": []}
        )


@router.get("/storage-stats")
async def get_storage_stats_endpoint():
    """Get storage usage statistics"""
    try:
        stats = get_storage_stats()
        return JSONResponse(status_code=200, content=stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


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


# ==================== HELPER FUNCTIONS ====================

def generate_emotion_statement(emotion: str, confidence: float) -> str:
    """
    Generate human-readable emotion statement
    
    Args:
        emotion: Emotion label
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
        "neutral": "😐 Your expression is neutral."
    }
    
    confidence_pct = int(confidence * 100)
    base_statement = emotion_descriptions.get(emotion, "Your emotional state is unclear.")
    
    return f"{base_statement} (Confidence: {confidence_pct}%)"
