"""Train the leaf disease CNN (spec §3.2).

Requires TensorFlow (pip install -r requirements-ml.txt) and the PlantVillage dataset
arranged as one folder per class, e.g. data/plantvillage/Tomato___Late_blight/*.jpg.

Usage: python -m ml.train_disease --data data/plantvillage [--epochs 15]
Saves ml/models/disease_cnn.keras and ml/models/disease_classes.json.
"""
import argparse
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / 'ml' / 'models'
IMG_SIZE = (64, 64)


def build_model(num_classes):
    from tensorflow import keras
    from tensorflow.keras import layers

    model = keras.Sequential([
        keras.Input(shape=(*IMG_SIZE, 3)),
        layers.Rescaling(1.0 / 255),
        layers.RandomFlip('horizontal'),
        layers.RandomRotation(0.1),
        layers.Conv2D(32, 3, activation='relu', padding='same'),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, activation='relu', padding='same'),
        layers.MaxPooling2D(),
        layers.Conv2D(128, 3, activation='relu', padding='same'),
        layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.4),
        layers.Dense(num_classes, activation='softmax'),
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model


def main():
    import tensorflow as tf

    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default=BASE_DIR / 'data' / 'plantvillage')
    parser.add_argument('--epochs', type=int, default=15)
    args = parser.parse_args()

    common = dict(validation_split=0.2, seed=42, image_size=IMG_SIZE, batch_size=64)
    train_ds = tf.keras.utils.image_dataset_from_directory(args.data, subset='training', **common)
    val_ds = tf.keras.utils.image_dataset_from_directory(args.data, subset='validation', **common)
    class_names = train_ds.class_names

    # Decode JPEGs once and keep 64x64 uint8 tensors in RAM (~650 MB for PlantVillage);
    # the model's Rescaling layer handles the conversion back to [0, 1] floats.
    autotune = tf.data.AUTOTUNE
    to_uint8 = lambda x, y: (tf.cast(x, tf.uint8), y)  # noqa: E731
    train_ds = train_ds.map(to_uint8, num_parallel_calls=autotune).cache().shuffle(200).prefetch(autotune)
    val_ds = val_ds.map(to_uint8, num_parallel_calls=autotune).cache().prefetch(autotune)

    model = build_model(len(class_names))
    model.fit(train_ds, validation_data=val_ds, epochs=args.epochs,
              callbacks=[tf.keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True)])
    loss, acc = model.evaluate(val_ds)
    print(f'Validation accuracy: {acc:.4f}')

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model.save(MODELS_DIR / 'disease_cnn.keras')
    (MODELS_DIR / 'disease_classes.json').write_text(json.dumps(class_names, indent=2))
    print(f'Saved model to {MODELS_DIR}')


if __name__ == '__main__':
    main()
