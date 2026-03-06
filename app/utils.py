import json
import os
from datetime import date
from PIL import Image
import numpy as np

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Absolute path for the data tracker JSON file.
STATS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stats.json')

def get_today_scans():
    """Reads the current number of scans done today from stats.json."""
    today_str = date.today().isoformat()
    
    if not os.path.exists(STATS_FILE):
        return 0
        
    try:
        with open(STATS_FILE, 'r') as f:
            data = json.load(f)
            
        # Check if the date recorded is actually today
        if data.get("date") == today_str:
            return data.get("scans", 0)
        else:
            # It's a new day, reset to 0
            return 0
    except (json.JSONDecodeError, IOError):
        return 0

def increment_scan_count():
    """Increments the daily scan count safely and writes to stats.json."""
    today_str = date.today().isoformat()
    current_count = get_today_scans()
    
    new_data = {
        "date": today_str,
        "scans": current_count + 1
    }
    
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(new_data, f)
    except IOError:
        print(f"Failed to write to {STATS_FILE}")

def validate_file(filename):
    """
    Checks if the uploaded file has an allowed extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def prepare_image(file_storage, target_size=(128, 128)):
    """
    Reads a FileStorage object from Flask, resizes, normalizes,
    and returns a NumPy array ready for prediction.
    """
    # Open image
    img = Image.open(file_storage.stream)
    
    # Convert to RGB (in case of RGBA/Grayscale)
    if img.mode != 'RGB':
        img = img.convert('RGB')
        
    # Resize
    img = img.resize(target_size)
    
    # Convert to Array
    img_array = np.array(img)
    
    # Normalize (1./255)
    img_array = img_array.astype('float32') / 255.0
    
    # Expand dims for batch dimension (1, 128, 128, 3)
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array
