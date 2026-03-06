import os
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from preprocessing import get_data_generators
from model_builder import build_model

def train():
    TRAIN_DIR = os.path.join('data', 'processed', 'train')
    VAL_DIR = os.path.join('data', 'processed', 'val')
    MODEL_DIR = 'models'
    MODEL_PATH = os.path.join(MODEL_DIR, 'parasitescan_best.h5')

    os.makedirs(MODEL_DIR, exist_ok=True)

    # Note: Kaggle dataset paths might need fixing depending on how it's downloaded.
    if not os.path.exists(TRAIN_DIR) or not os.listdir(os.path.join(TRAIN_DIR, 'parasitized')):
        print(f"Warning: Data not found in {TRAIN_DIR}. Please run data_loader.py first.")
        # We can't actually train if data is missing, we'll exit gracefully.
        # return

    # Hyperparameters
    EPOCHS = 35
    BATCH_SIZE = 32
    TARGET_SIZE = (128, 128)

    # 1. Get Data Generators
    try:
        train_gen, val_gen = get_data_generators(TRAIN_DIR, VAL_DIR, TARGET_SIZE, BATCH_SIZE)
    except Exception as e:
        print(f"Failed to load data generators: {e}. Ensure data is present.")
        return

    # 2. Build Model
    model = build_model(input_shape=(TARGET_SIZE[0], TARGET_SIZE[1], 3))

    # 3. Callbacks
    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True,
        verbose=1
    )

    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.2,
        patience=3,
        min_lr=1e-6,
        verbose=1
    )

    model_checkpoint = ModelCheckpoint(
        filepath=MODEL_PATH,
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    )

    callbacks = [early_stopping, reduce_lr, model_checkpoint]

    print(f"Starting training for {EPOCHS} epochs...")
    history = model.fit(
        train_gen,
        epochs=EPOCHS,
        validation_data=val_gen,
        callbacks=callbacks
    )

    print(f"Training completed. Best model saved to {MODEL_PATH}")
    return history

if __name__ == "__main__":
    train()
