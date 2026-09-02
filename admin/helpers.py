"""Admin utility helpers."""
import os
import uuid
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
MAX_IMAGE_SIZE = (2400, 2400)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file_storage):
    """Save an uploaded image, resize if needed. Returns (filename, url, size_bytes)."""
    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_folder = os.path.join(current_app.static_folder, 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)

    img = Image.open(file_storage.stream)
    img.thumbnail(MAX_IMAGE_SIZE, Image.LANCZOS)
    img.save(filepath, optimize=True, quality=88)

    size_bytes = os.path.getsize(filepath)
    url = f"/static/uploads/{filename}"
    return filename, url, size_bytes


def delete_image(filename):
    """Delete an uploaded image from disk."""
    filepath = os.path.join(current_app.static_folder, 'uploads', filename)
    if os.path.exists(filepath):
        os.remove(filepath)
