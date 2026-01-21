import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Config:
    SECRET_KEY = "dev-secret"  # replace with env var / secure key in production
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    LOG_FILE = os.path.join(BASE_DIR, "logs", "uploads.log")

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    ALLOWED_EXTENSIONS = {".txt", ".csv", ".docx"}
