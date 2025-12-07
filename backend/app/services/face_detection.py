import cv2
import numpy as np

# Load OpenCV's default frontal face cascade
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

def detect_faces(image_bytes: bytes):
    """Return list of cropped face images (as numpy arrays)."""
    # Convert bytes → np array → BGR image
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
    )
    
    crops = []
    for (x, y, w, h) in faces:
        face = img[y:y + h, x:x + w]
        crops.append(face)
    return crops
