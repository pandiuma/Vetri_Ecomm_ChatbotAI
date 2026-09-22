import os
from dotenv import load_dotenv
from pathlib import Path
import cloudinary
import cloudinary.uploader
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load .env
load_dotenv(os.path.join(BASE_DIR, ".env"))

cloudinary_url = os.getenv("CLOUDINARY_URL")

if not cloudinary_url:
    raise ValueError("CLOUDINARY_URL was not found in .env")

# Parse Cloudinary URL
parsed = urlparse(cloudinary_url)

api_key = parsed.username
api_secret = parsed.password
cloud_name = parsed.hostname

if not api_key or not api_secret or not cloud_name:
    raise ValueError("Invalid CLOUDINARY_URL format")

# Configure Cloudinary explicitly
cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret,
    secure=True,
)

MEDIA_PRODUCTS = os.path.join(BASE_DIR, "media", "products")

images = [
    "samsung_ur5i31i.jpg",
    "handbag2.jpg",
    "handbag.jpg",
    "clutch_UYf88cG.jpg",
    "clutch2.jpg",
    "backpack2.jpg",
    "Keyboard.jpg",
    "backpack.jpg",
    "Footwear.jpg",
]

for filename in images:
    file_path = os.path.join(MEDIA_PRODUCTS, filename)

    if not os.path.exists(file_path):
        print(f"NOT FOUND: {filename}")
        continue

    try:
        result = cloudinary.uploader.upload(
            file_path,
            folder="products",
            use_filename=True,
            unique_filename=False,
            overwrite=False,
        )

        print(f"UPLOADED: {filename}")
        print(f"Cloudinary URL: {result['secure_url']}")
        print("-" * 60)

    except Exception as e:
        print(f"FAILED: {filename}")
        print(f"Error: {e}")
        print("-" * 60)