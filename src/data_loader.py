import os
import shutil
import random

def split_data(source_dir, train_dir, val_dir, split_ratio=0.8):
    """
    Splits the NIH Malaria dataset into training and validation sets.
    Assumes source_dir contains 'Parasitized' and 'Uninfected' folders.
    """
    classes = ['Parasitized', 'Uninfected']
    
    for cls in classes:
        cls_source = os.path.join(source_dir, cls)
        
        if not os.path.exists(cls_source):
            print(f"Warning: Source directory not found: {cls_source}")
            continue

        images = [f for f in os.listdir(cls_source) if f.endswith('.png')]
        random.shuffle(images)
        
        split_idx = int(len(images) * split_ratio)
        train_images = images[:split_idx]
        val_images = images[split_idx:]
        
        # Target directories matching the format
        cls_target = 'parasitized' if cls == 'Parasitized' else 'uninfected'
        
        train_target_dir = os.path.join(train_dir, cls_target)
        val_target_dir = os.path.join(val_dir, cls_target)
        
        os.makedirs(train_target_dir, exist_ok=True)
        os.makedirs(val_target_dir, exist_ok=True)
        
        print(f"Copying {len(train_images)} training images for {cls}...")
        for img in train_images:
            shutil.copy(os.path.join(cls_source, img), os.path.join(train_target_dir, img))
            
        print(f"Copying {len(val_images)} validation images for {cls}...")
        for img in val_images:
            shutil.copy(os.path.join(cls_source, img), os.path.join(val_target_dir, img))

if __name__ == "__main__":
    # Adjust paths if Kaggle downloads it differently
    RAW_DATA_DIR = os.path.join('data', 'raw', 'cell_images', 'cell_images')
    if not os.path.exists(RAW_DATA_DIR):
        RAW_DATA_DIR = os.path.join('data', 'raw', 'cell_images')

    TRAIN_DIR = os.path.join('data', 'processed', 'train')
    VAL_DIR = os.path.join('data', 'processed', 'val')
    
    split_data(RAW_DATA_DIR, TRAIN_DIR, VAL_DIR)
    print("Data splitting complete!")
