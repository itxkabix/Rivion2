# RIVION Face Recognition Installation Guide

## Overview
RIVION now uses **face recognition** to find exact matches of captured faces in your images folder, then displays the emotions from those matched images.

## Installation Steps

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Face Recognition Libraries

#### Option A: Using face_recognition (Recommended for accuracy)

**Windows:**
```bash
# Install CMake first (required for dlib)
pip install cmake

# Install dlib (this may take a while)
pip install dlib

# Install face_recognition
pip install face-recognition
```

**Linux/Mac:**
```bash
# Install system dependencies first
# Ubuntu/Debian:
sudo apt-get install cmake libopenblas-dev liblapack-dev libx11-dev

# Then install Python packages
pip install dlib
pip install face-recognition
```

#### Option B: Using DeepFace only (Easier installation)

If `face_recognition` installation fails, you can use DeepFace for both face recognition and emotion detection:

```bash
pip install deepface
pip install tensorflow
```

Then update `backend/app/services/face_recognition_service.py` to use DeepFace's face recognition.

### 3. Verify Installation

```bash
cd backend
python -c "import face_recognition; print('✅ face_recognition installed')"
python -c "from deepface import DeepFace; print('✅ DeepFace installed')"
```

## How It Works

1. **Face Capture**: User captures their face via webcam
2. **Face Encoding**: System extracts face encoding (128-dimensional vector)
3. **Face Matching**: System compares captured face with all faces in `frontend/Images/` folder
4. **Emotion Detection**: For each matched face, system detects emotion using DeepFace
5. **Display Results**: Shows matched images with their emotions and similarity scores

## Configuration

### Face Matching Threshold

Edit `backend/app/routes/search.py`:
- `tolerance=0.6` - Lower = more strict matching (default 0.6)
- Adjust based on your needs (0.4-0.7 range recommended)

### Images Folder

The system automatically scans `frontend/Images/` folder. Make sure your images are organized by emotion:
- `frontend/Images/happy/`
- `frontend/Images/sad/`
- `frontend/Images/angry/`
- etc.

## Troubleshooting

### Issue: "No module named 'dlib'"
**Solution**: Install dlib manually (see Option A above) or use DeepFace only (Option B)

### Issue: "No faces found"
**Solution**: 
- Ensure images contain clear, front-facing faces
- Check that face_recognition can detect faces: `python -c "import face_recognition; print(face_recognition.__version__)"`

### Issue: "CMake not found"
**Solution**: Install CMake: `pip install cmake` or download from https://cmake.org/

### Issue: Slow face matching
**Solution**: 
- Face encodings are cached in `backend/face_encodings_cache.pkl`
- First run indexes all images (slower)
- Subsequent runs use cache (much faster)

## Testing

```bash
cd backend
python -c "
from app.services.face_recognition_service import index_images_folder
from pathlib import Path
images_folder = Path('..') / 'frontend' / 'Images'
indexed = index_images_folder(str(images_folder))
print(f'Indexed {len(indexed)} images')
"
```

