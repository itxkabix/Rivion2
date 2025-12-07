import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

PROJECT_ROOT = "RIVION"  # 👈 change this if you want a different folder name

list_of_files = [
    # Root
    f"{PROJECT_ROOT}/README.md",
    f"{PROJECT_ROOT}/DEPLOYMENT.md",
    f"{PROJECT_ROOT}/.gitignore",
    f"{PROJECT_ROOT}/docker-compose.yml",

    # ----------------- FRONTEND -----------------
    f"{PROJECT_ROOT}/frontend/package.json",
    f"{PROJECT_ROOT}/frontend/vite.config.js",
    f"{PROJECT_ROOT}/frontend/tailwind.config.js",
    f"{PROJECT_ROOT}/frontend/.env.example",

    # frontend/public
    f"{PROJECT_ROOT}/frontend/public/index.html",
    f"{PROJECT_ROOT}/frontend/public/favicon.ico",

    # frontend/src core
    f"{PROJECT_ROOT}/frontend/src/App.jsx",
    f"{PROJECT_ROOT}/frontend/src/main.jsx",
    f"{PROJECT_ROOT}/frontend/src/index.css",

    # frontend/src/components
    f"{PROJECT_ROOT}/frontend/src/components/FaceCaptureComponent.jsx",
    f"{PROJECT_ROOT}/frontend/src/components/MetadataFormComponent.jsx",
    f"{PROJECT_ROOT}/frontend/src/components/ResultsComponent.jsx",
    f"{PROJECT_ROOT}/frontend/src/components/LoadingSpinner.jsx",
    f"{PROJECT_ROOT}/frontend/src/components/ErrorBoundary.jsx",

    # frontend/src/pages
    f"{PROJECT_ROOT}/frontend/src/pages/HomePage.jsx",
    f"{PROJECT_ROOT}/frontend/src/pages/SearchPage.jsx",
    f"{PROJECT_ROOT}/frontend/src/pages/ResultsPage.jsx",

    # frontend/src/styles
    f"{PROJECT_ROOT}/frontend/src/styles/tailwind.css",
    f"{PROJECT_ROOT}/frontend/src/styles/globals.css",

    # frontend/src/utils
    f"{PROJECT_ROOT}/frontend/src/utils/api.js",
    f"{PROJECT_ROOT}/frontend/src/utils/constants.js",
    f"{PROJECT_ROOT}/frontend/src/utils/helpers.js",

    # ----------------- BACKEND -----------------
    f"{PROJECT_ROOT}/backend/requirements.txt",
    f"{PROJECT_ROOT}/backend/.env.example",
    f"{PROJECT_ROOT}/backend/docker/Dockerfile",
    f"{PROJECT_ROOT}/backend/docker-compose.yml",

    # backend/app core
    f"{PROJECT_ROOT}/backend/app/__init__.py",
    f"{PROJECT_ROOT}/backend/app/main.py",
    f"{PROJECT_ROOT}/backend/app/config.py",

    # backend/app/models
    f"{PROJECT_ROOT}/backend/app/models/__init__.py",
    f"{PROJECT_ROOT}/backend/app/models/schemas.py",     # Pydantic schemas
    f"{PROJECT_ROOT}/backend/app/models/database.py",    # SQLAlchemy models

    # backend/app/routes
    f"{PROJECT_ROOT}/backend/app/routes/__init__.py",
    f"{PROJECT_ROOT}/backend/app/routes/search.py",      # /api/v1/search
    f"{PROJECT_ROOT}/backend/app/routes/health.py",      # /api/health

    # backend/app/services
    f"{PROJECT_ROOT}/backend/app/services/__init__.py",
    f"{PROJECT_ROOT}/backend/app/services/face_detection.py",  # RetinaFace
    f"{PROJECT_ROOT}/backend/app/services/embedding.py",       # ArcFace
    f"{PROJECT_ROOT}/backend/app/services/emotion.py",         # ViT emotion
    f"{PROJECT_ROOT}/backend/app/services/database.py",        # DB operations
    f"{PROJECT_ROOT}/backend/app/services/s3_storage.py",      # AWS S3

    # backend/app/utils
    f"{PROJECT_ROOT}/backend/app/utils/__init__.py",
    f"{PROJECT_ROOT}/backend/app/utils/logger.py",
    f"{PROJECT_ROOT}/backend/app/utils/validators.py",

    # backend/app/middleware
    f"{PROJECT_ROOT}/backend/app/middleware/__init__.py",
    f"{PROJECT_ROOT}/backend/app/middleware/error_handler.py",

    # backend/tests
    f"{PROJECT_ROOT}/backend/tests/__init__.py",
    f"{PROJECT_ROOT}/backend/tests/test_endpoints.py",
    f"{PROJECT_ROOT}/backend/tests/test_services.py",
]


def create_structure(files: list[str]) -> None:
    for filepath in files:
        path = Path(filepath)
        directory, filename = os.path.split(path)

        # Create directory
        if directory:
            os.makedirs(directory, exist_ok=True)
            logging.info(f"Created directory: {directory}")

        # Create file if not exist or empty
        if (not os.path.exists(path)) or (os.path.getsize(path) == 0):
            with open(path, "w", encoding="utf-8") as f:
                # Optional: tiny hints in a few key files
                if filename in {"main.py"}:
                    f.write("# TODO: implement FastAPI app here\n")
                elif filename in {"App.jsx"}:
                    f.write("// TODO: implement main React App component\n")
                elif filename in {"index.html"}:
                    f.write("<!-- TODO: base HTML template -->\n")
                else:
                    f.write("")
            logging.info(f"Created file: {path}")
        else:
            logging.info(f"File exists (skipped): {path}")


if __name__ == "__main__":
    create_structure(list_of_files)
    logging.info("RIVION - FaceEmotionSearch project structure creation complete.")
