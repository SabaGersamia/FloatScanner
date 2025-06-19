import json
from pathlib import Path
from django.conf import settings

class ImageManager:
    _instance = None
    _image_data = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._load_image_data()
        return cls._instance

    @classmethod
    def _load_image_data(cls):
        try:
            json_path = Path(settings.BASE_DIR) / 'scanner' / 'data' / 'listings_images.json'
            with open(json_path, 'r', encoding='utf-8') as f:
                cls._image_data = json.load(f)
        except Exception as e:
            print(f"Error loading image data: {e}")
            cls._image_data = {}

    @classmethod
    def get_image_url(cls, listing_id):
        return cls._image_data.get(str(listing_id), {}).get('listing_image', '')