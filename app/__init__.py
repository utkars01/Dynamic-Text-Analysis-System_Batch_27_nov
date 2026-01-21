import os
from flask import Flask
from .config import Config
import logging
from logging.handlers import RotatingFileHandler

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)

    # ensure upload and log directories exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(os.path.dirname(app.config["LOG_FILE"]), exist_ok=True)

    # Setup logging for upload events (separate logger)
    upload_logger = logging.getLogger("uploads")
    upload_logger.setLevel(logging.INFO)
    if not upload_logger.handlers:
        handler = RotatingFileHandler(app.config["LOG_FILE"], maxBytes=5*1024*1024, backupCount=2)
        formatter = logging.Formatter("%(asctime)s\t%(levelname)s\t%(message)s")
        handler.setFormatter(formatter)
        upload_logger.addHandler(handler)

    # Attach logger to app for easy access in routes
    app.upload_logger = upload_logger

    # Import and register routes
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
