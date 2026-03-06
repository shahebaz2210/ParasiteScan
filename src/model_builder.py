import tensorflow as tf
from tensorflow.keras import layers, models, metrics

def build_model(input_shape=(128, 128, 3)):
    """
    Builds and compiles the Custom CNN architecture.
    """
    print("Building custom CNN architecture...")
    model = models.Sequential([
        layers.InputLayer(input_shape=input_shape),
        
        # Block 1
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        
        # Block 2
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        
        # Block 3
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        
        # Batch Normalization and Dropout
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        
        # Fully Connected Layers
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        
        # Output Layer
        layers.Dense(1, activation='sigmoid')
    ])

    print("Compiling model...")
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.0001)
    
    model.compile(
        optimizer=optimizer,
        loss='binary_crossentropy',
        metrics=['accuracy', metrics.AUC(name='auc')]
    )
    
    return model

if __name__ == "__main__":
    model = build_model()
    model.summary()
