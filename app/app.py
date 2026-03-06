import sys
import os

# Add the project root to sys.path so model_loader can be imported correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from app.model_loader import get_model, get_model_metrics
from app.utils import prepare_image, validate_file, get_today_scans, increment_scan_count
import time
import random

app = Flask(__name__)
CORS(app)

# Ensure the app can run without the model for initial UI testing
try:
    # Try to load the model on startup
    _ = get_model()
    MODEL_LOADED = True
except Exception as e:
    print(f"Warning: Model could not be loaded on startup: {e}")
    MODEL_LOADED = False

@app.route('/', methods=['GET'])
def index():
    metrics = get_model_metrics()
    metrics["scans_today"] = get_today_scans()
    return render_template('index.html', metrics=metrics)

@app.route('/predict', methods=['POST'])
def predict():
    start_time = time.time()
    
    # Increment our local daily tracker
    increment_scan_count()
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if not validate_file(file.filename):
        return jsonify({"error": "Invalid file type. Only PNG, JPG, JPEG are allowed."}), 400

    try:
        # 1. Preprocess Image
        img_array = prepare_image(file)
        
        if not MODEL_LOADED:
            # Mock response for testing UI without a trained model
            time.sleep(2)  # Simulate processing time
            is_parasitized = random.choice([True, False])
            if is_parasitized:
                probability = random.uniform(0.90, 0.999)
            else:
                probability = random.uniform(0.001, 0.10)
        else:
            # 2. Predict
            model = get_model()
            prediction = model.predict(img_array)
            probability = float(prediction[0][0])
            
        # 3. Apply Threshold Logic
        # ImageDataGenerator class indices: {'parasitized': 0, 'uninfected': 1}
        # A probability > 0.5 means class 1 (Uninfected)
        label = "Uninfected" if probability > 0.5 else "Parasitized"
        confidence = probability if label == "Uninfected" else 1.0 - probability
        
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        return jsonify({
            "label": label,
            "probability": probability,
            "confidence": confidence,
            "processing_time_ms": processing_time,
            "scans_today": get_today_scans()
        })
        
    except Exception as e:
        return jsonify({"error": f"Error processing image: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "up",
        "model_loaded": MODEL_LOADED
    })

@app.route('/metrics', methods=['GET'])
def metrics():
    return jsonify(get_model_metrics())

if __name__ == '__main__':
    # Disable debug=True in production
    app.run(host='0.0.0.0', port=5000, debug=False)
