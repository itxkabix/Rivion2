"""
DIAGNOSTIC + FIX: Image Search Issues
Run this to find and fix the problem
"""

import os
import sys
from pathlib import Path

print("=" * 80)
print("🔍 FACE EMOTION ANALYZER - IMAGE SEARCH DIAGNOSTICS")
print("=" * 80)

# ============================================================================
# SECTION 1: Check if image_storage.py exists and has correct functions
# ============================================================================
print("\n1️⃣  Checking image_storage.py...")

try:
    from app.services.image_storage import (
        get_images_from_local_folder,
        set_local_images_folder,
        get_all_stored_images,
        get_similar_images
    )
    print("✅ All functions imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   FIX: Make sure you replaced image_storage.py with image_storage_with_local_folder.py")

# ============================================================================
# SECTION 2: Check if local folder path is set
# ============================================================================
print("\n2️⃣  Checking LOCAL_IMAGES_FOLDER...")

try:
    from app.services import image_storage
    folder_path = image_storage.LOCAL_IMAGES_FOLDER
    print(f"   Path: {folder_path}")
    
    if os.path.exists(folder_path):
        print("✅ Folder exists!")
        
        # List contents
        print(f"\n   Contents:")
        for root, dirs, files in os.walk(folder_path):
            level = root.replace(folder_path, '').count(os.sep)
            indent = ' ' * 2 * level
            rel_path = os.path.relpath(root, folder_path)
            print(f"{indent}📁 {rel_path}/")
            
            sub_indent = ' ' * 2 * (level + 1)
            for file in files[:5]:  # Show first 5 files
                print(f"{sub_indent}📄 {file}")
            if len(files) > 5:
                print(f"{sub_indent}... and {len(files) - 5} more files")
    else:
        print(f"❌ Folder does not exist: {folder_path}")
        print("\n   FIX OPTIONS:")
        print("   Option A: Edit image_storage.py line 14")
        print("   LOCAL_IMAGES_FOLDER = 'C:/path/to/your/images'")
        print("\n   Option B: Use API to set folder")
        print("   curl -X POST http://localhost:8000/api/v1/set-images-folder -F folder_path=C:/path/to/images")
        
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================================
# SECTION 3: Check emotion structure
# ============================================================================
print("\n3️⃣  Checking image organization...")

try:
    from app.services.image_storage import get_images_from_local_folder
    
    images = get_images_from_local_folder()
    if images:
        print(f"✅ Found {len(images)} images!")
        
        emotions = {}
        for img in images:
            emotion = img.get('emotion', 'unknown')
            if emotion not in emotions:
                emotions[emotion] = 0
            emotions[emotion] += 1
        
        print(f"\n   Images by emotion:")
        for emotion, count in emotions.items():
            print(f"   - {emotion}: {count} images")
    else:
        print("❌ No images found")
        print("\n   ISSUES TO CHECK:")
        print("   1. Are images organized in emotion subfolders?")
        print("      Expected: emotion/image.jpg")
        print("      Or: user/emotion/image.jpg")
        print("\n   2. Are image extensions correct?")
        print("      Supported: .jpg, .jpeg, .png, .bmp, .gif")
        print("\n   3. Is the folder path correct?")
        print("      Windows: C:/Users/Lenovo/path/to/images")
        print("      NOT: C:\\Users\\Lenovo\\path\\to\\images")
        
except Exception as e:
    print(f"❌ Error checking images: {e}")

# ============================================================================
# SECTION 4: Check search functionality
# ============================================================================
print("\n4️⃣  Testing search functionality...")

try:
    from app.services.image_storage import get_similar_images
    
    # Try to get happy images
    similar = get_similar_images("happy", limit=5)
    print(f"✅ Search working - found {len(similar)} happy images")
    
except Exception as e:
    print(f"❌ Search error: {e}")

# ============================================================================
# SECTION 5: Check backend search.py
# ============================================================================
print("\n5️⃣  Checking search.py routes...")

try:
    from app.routes.search import router
    print("✅ search.py routes loaded")
    
    # List endpoints
    print("\n   Available endpoints:")
    print("   - POST /api/v1/analyze-face")
    print("   - POST /api/v1/search")
    print("   - GET /api/v1/local-images")
    print("   - POST /api/v1/set-images-folder")
    print("   - GET /api/v1/all-images")
    print("   - GET /api/v1/storage-stats")
    
except Exception as e:
    print(f"❌ Error loading search.py: {e}")

# ============================================================================
# SECTION 6: Recommendations
# ============================================================================
print("\n" + "=" * 80)
print("📋 FIXES & RECOMMENDATIONS")
print("=" * 80)

print("""
IF IMAGES NOT FOUND:

1. Edit: backend/app/services/image_storage.py (Line 14)
   Change:
   LOCAL_IMAGES_FOLDER = "C:/Users/Lenovo/OneDrive/Documents/GitHub/Rivion/images"
   
   To your actual path (use forward slashes):
   LOCAL_IMAGES_FOLDER = "C:/Users/Lenovo/Pictures"
   
2. Organize images by emotion:
   Your_Folder/
   ├── happy/
   │   ├── image1.jpg
   │   └── image2.jpg
   ├── sad/
   │   └── image3.jpg
   └── angry/
       └── image4.jpg

3. Restart backend:
   cd backend
   python -m app.main

4. Test API:
   curl http://localhost:8000/api/v1/local-images

5. If still not working, check:
   - Image file extensions (.jpg, .png, etc.)
   - Folder path has no special characters
   - Path uses forward slashes (/)
   - Emotion folder names are lowercase
""")

print("\n" + "=" * 80)
