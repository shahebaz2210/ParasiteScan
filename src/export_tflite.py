import os
import tensorflow as tf

def export_to_tflite():
    MODEL_PATH = os.path.join('models', 'parasitescan_best.h5')
    TFLITE_MODEL_PATH = os.path.join('models', 'parasitescan_model.tflite')
    
    if not os.path.exists(MODEL_PATH):
        print(f"Original model not found at {MODEL_PATH}")
        return
        
    print(f"Loading {MODEL_PATH}...")
    model = tf.keras.models.load_model(MODEL_PATH)
    
    print("Converting to TensorFlow Lite format...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    
    # Enable optimization (quantization) for mobile
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    tflite_model = converter.convert()
    
    print(f"Saving TFLite model to {TFLITE_MODEL_PATH}...")
    with open(TFLITE_MODEL_PATH, 'wb') as f:
        f.write(tflite_model)
        
    print(f"Success! Model size: {len(tflite_model) / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    export_to_tflite()
