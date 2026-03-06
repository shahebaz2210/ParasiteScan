from tensorflow.keras.preprocessing.image import ImageDataGenerator

def get_data_generators(train_dir, val_dir, target_size=(128, 128), batch_size=32):
    """
    Creates and returns train and validation data generators with data augmentation.
    """
    print("Setting up data generators...")
    
    # Train data generator with augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        zoom_range=0.2,
        horizontal_flip=True
    )

    # Validation data generator without augmentation (only rescaling)
    val_datagen = ImageDataGenerator(
        rescale=1./255
    )

    print("Loading training data:")
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=target_size,
        batch_size=batch_size,
        class_mode='binary',
        shuffle=True
    )

    print("Loading validation data:")
    val_generator = val_datagen.flow_from_directory(
        val_dir,
        target_size=target_size,
        batch_size=batch_size,
        class_mode='binary',
        shuffle=False
    )

    return train_generator, val_generator
