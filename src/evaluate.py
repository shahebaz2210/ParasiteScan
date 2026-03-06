import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
import matplotlib.pyplot as plt
import cv2

# Ensure matplotlib runs headlessly if in server mode
import matplotlib
matplotlib.use('Agg')

def evaluate_model():
    MODEL_PATH = os.path.join('models', 'parasitescan_best.h5')
    VAL_DIR = os.path.join('data', 'processed', 'val')
    TARGET_SIZE = (128, 128)
    BATCH_SIZE = 32

    if not os.path.exists(MODEL_PATH):
        print(f"Model not found at {MODEL_PATH}")
        return

    print("Loading model...")
    model = load_model(MODEL_PATH)
    
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    try:
        val_generator = val_datagen.flow_from_directory(
            VAL_DIR,
            target_size=TARGET_SIZE,
            batch_size=BATCH_SIZE,
            class_mode='binary',
            shuffle=False
        )
    except Exception as e:
        print(f"Failed to load validation data: {e}. Skipping evaluation.")
        return

    print("Evaluating model...")
    results = model.evaluate(val_generator)
    print(f"Loss: {results[0]:.4f}, Accuracy: {results[1]:.4f}")

    # Predictions
    print("Generating predictions...")
    y_pred_prob = model.predict(val_generator)
    y_pred = (y_pred_prob > 0.5).astype(int)
    y_true = val_generator.classes

    # Classification Report
    print("Classification Report:")
    print(classification_report(y_true, y_pred, target_names=val_generator.class_indices.keys()))

    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    print("Confusion Matrix:")
    print(cm)
    
    # Optional: Save plots
    os.makedirs('notebooks', exist_ok=True)
    
    # ROC Curve Plot
    fpr, tpr, _ = roc_curve(y_true, y_pred_prob)
    roc_auc = auc(fpr, tpr)
    
    plt.figure()
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic')
    plt.legend(loc="lower right")
    plt.savefig('notebooks/roc_curve.png')
    print("ROC curve saved to notebooks/roc_curve.png")

def make_gradcam_heatmap(img_array, model, last_conv_layer_name, pred_index=None):
    """
    Grad-CAM implementation.
    """
    grad_model = tf.keras.models.Model(
        [model.inputs], [model.get_layer(last_conv_layer_name).output, model.output]
    )

    with tf.GradientTape() as tape:
        last_conv_layer_output, preds = grad_model(img_array)
        if pred_index is None:
            pred_index = tf.argmax(preds[0])
        class_channel = preds[:, pred_index]

    grads = tape.gradient(class_channel, last_conv_layer_output)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    last_conv_layer_output = last_conv_layer_output[0]
    heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
    return heatmap.numpy()

def save_and_display_gradcam(img_path, heatmap, cam_path="notebooks/grad_cam.jpg", alpha=0.4):
    """
    Overlays Grad-CAM heatmap on original image.
    """
    img = cv2.imread(img_path)
    if img is None:
        return
        
    heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
    heatmap = np.uint8(255 * heatmap)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    superimposed_img = heatmap * alpha + img
    cv2.imwrite(cam_path, superimposed_img)

if __name__ == "__main__":
    evaluate_model()
