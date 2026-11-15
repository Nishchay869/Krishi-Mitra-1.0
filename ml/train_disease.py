"""Train the leaf disease classifier with transfer learning (spec §3.2).

Requires TensorFlow (pip install -r requirements-ml.txt) and images arranged as one
folder per class named Crop___Disease, e.g. data/disease_merged/Tomato___Late_blight/*.jpg.
Build that folder from several downloaded datasets with scripts/merge_disease_datasets.py.

Training runs in two phases on an ImageNet-pretrained backbone:
  1. backbone frozen, only the new classifier head learns (fast, stable);
  2. the top of the backbone is unfrozen and fine-tuned at a low learning rate.

Usage:
  python -m ml.train_disease --data data/disease_merged
  python -m ml.train_disease --data data/disease_merged --arch mobilenetv3 --epochs 8 --fine-tune-epochs 8
  python -m ml.train_disease --data data/disease_merged --test-dir data/field_test

Saves ml/models/disease_cnn.keras, disease_classes.json and disease_metrics.json.
An existing model is kept as disease_cnn.prev.keras / disease_classes.prev.json.

The model takes raw RGB pixels in [0, 255] at its own input size; the backbone does its
own normalisation. Inference code reads the size from model.input_shape.
"""
import argparse
import json
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / 'ml' / 'models'
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}

ARCHS = {
    # name: (keras.applications constructor name, layers to unfreeze when fine-tuning)
    'efficientnetb0': ('EfficientNetB0', 60),
    'efficientnetb3': ('EfficientNetB3', 80),
    'mobilenetv3': ('MobileNetV3Large', 50),
}


def build_model(num_classes, img_size, arch):
    from tensorflow import keras
    from tensorflow.keras import layers

    ctor_name, _ = ARCHS[arch]
    ctor = getattr(keras.applications, ctor_name)
    # EfficientNet and MobileNetV3 include their own input rescaling, so they take [0, 255].
    base = ctor(include_top=False, weights='imagenet', input_shape=(img_size, img_size, 3))
    base.trainable = False

    augment = keras.Sequential([
        layers.RandomFlip('horizontal_and_vertical'),
        layers.RandomRotation(0.15),
        layers.RandomZoom(0.15),
        layers.RandomTranslation(0.1, 0.1),
        layers.RandomContrast(0.2),
        layers.RandomBrightness(0.2, value_range=(0, 255)),
    ], name='augment')

    inputs = keras.Input(shape=(img_size, img_size, 3))
    x = augment(inputs)  # active only during training
    x = base(x, training=False)  # keep BatchNorm statistics frozen, also while fine-tuning
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation='softmax', dtype='float32')(x)
    return keras.Model(inputs, outputs, name=f'disease_{arch}'), base


def class_weights(train_dir_counts):
    """Inverse-frequency weights so small classes are not ignored."""
    total = sum(train_dir_counts)
    n = len(train_dir_counts)
    return {i: total / (n * c) for i, c in enumerate(train_dir_counts) if c}


def count_images(data_dir, class_names):
    return [sum(1 for p in (Path(data_dir) / c).iterdir() if p.suffix.lower() in IMAGE_EXTS)
            for c in class_names]


def evaluate_folder(model, test_dir, class_names, img_size):
    """Accuracy on a separate folder (ideally real field photos). Unknown classes are skipped."""
    import numpy as np
    from PIL import Image

    index = {c: i for i, c in enumerate(class_names)}
    crop_of = np.array([c.split('___')[0] for c in class_names])
    per_class, correct, crop_correct, total, skipped = {}, 0, 0, 0, []
    for folder in sorted(p for p in Path(test_dir).iterdir() if p.is_dir()):
        if folder.name not in index:
            skipped.append(folder.name)
            continue
        files = [p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTS]
        same_crop = crop_of == folder.name.split('___')[0]
        hits = crop_hits = 0
        for start in range(0, len(files), 32):
            batch = np.stack([
                np.asarray(Image.open(f).convert('RGB').resize((img_size, img_size)), dtype='float32')
                for f in files[start:start + 32]
            ])
            # photo + mirror image, averaged, exactly like disease/predictor.py
            probs = (model.predict(batch, verbose=0) + model.predict(batch[:, :, ::-1, :], verbose=0)) / 2
            hits += int((probs.argmax(axis=1) == index[folder.name]).sum())
            # "farmer told us the crop": only compare diseases of that crop, like the app does
            crop_hits += int((np.where(same_crop, probs, 0).argmax(axis=1) == index[folder.name]).sum())
        per_class[folder.name] = {'n': len(files), 'accuracy': hits / len(files) if files else None,
                                  'accuracy_crop_known': crop_hits / len(files) if files else None}
        correct += hits
        crop_correct += crop_hits
        total += len(files)
    if skipped:
        print(f'Test folders not in training classes (skipped): {", ".join(skipped)}')
    weakest = sorted((v['accuracy_crop_known'], k, v['n']) for k, v in per_class.items() if v['n'])[:8]
    print('Weakest classes on field photos (crop known):')
    for acc, name, n in weakest:
        print(f'  {acc:6.1%}  {name}  ({n} photos)')
    return {'n': total, 'accuracy': correct / total if total else None,
            'accuracy_crop_known': crop_correct / total if total else None, 'per_class': per_class}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--data', default=BASE_DIR / 'data' / 'disease_merged')
    parser.add_argument('--arch', choices=sorted(ARCHS), default='efficientnetb0')
    parser.add_argument('--img-size', type=int, default=224)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--epochs', type=int, default=10, help='phase 1: frozen backbone')
    parser.add_argument('--fine-tune-epochs', type=int, default=10, help='phase 2: 0 to skip')
    parser.add_argument('--val-split', type=float, default=0.2)
    parser.add_argument('--test-dir', help='optional separate Crop___Disease folder tree, e.g. field photos')
    parser.add_argument('--out', default=MODELS_DIR, help='output directory')
    args = parser.parse_args()

    import tensorflow as tf
    from tensorflow import keras

    size = (args.img_size, args.img_size)
    common = dict(validation_split=args.val_split, seed=42, image_size=size,
                  batch_size=args.batch_size, label_mode='int')
    train_ds = keras.utils.image_dataset_from_directory(args.data, subset='training', shuffle=True, **common)
    val_ds = keras.utils.image_dataset_from_directory(args.data, subset='validation', shuffle=False, **common)
    class_names = train_ds.class_names
    print(f'{len(class_names)} classes')

    autotune = tf.data.AUTOTUNE
    # No .cache(): 224px images for a large merged dataset would not fit in RAM.
    train_ds = train_ds.prefetch(autotune)
    val_ds = val_ds.prefetch(autotune)

    model, base = build_model(len(class_names), args.img_size, args.arch)
    weights = class_weights(count_images(args.data, class_names))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    checkpoint = out / 'disease_cnn.training.keras'
    callbacks = [
        keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=3, restore_best_weights=True),
        keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.3, patience=2),
        keras.callbacks.ModelCheckpoint(checkpoint, monitor='val_accuracy', save_best_only=True),
    ]
    metrics = ['accuracy', keras.metrics.SparseTopKCategoricalAccuracy(k=3, name='top3')]

    print('Phase 1: training classifier head (backbone frozen)')
    model.compile(optimizer=keras.optimizers.Adam(1e-3), loss='sparse_categorical_crossentropy', metrics=metrics)
    model.fit(train_ds, validation_data=val_ds, epochs=args.epochs, class_weight=weights, callbacks=callbacks)

    if args.fine_tune_epochs > 0:
        _, unfreeze = ARCHS[args.arch]
        print(f'Phase 2: fine-tuning top {unfreeze} backbone layers')
        base.trainable = True
        for layer in base.layers[:-unfreeze]:
            layer.trainable = False
        for layer in base.layers:
            if isinstance(layer, keras.layers.BatchNormalization):
                layer.trainable = False
        model.compile(optimizer=keras.optimizers.Adam(1e-5), loss='sparse_categorical_crossentropy', metrics=metrics)
        model.fit(train_ds, validation_data=val_ds, epochs=args.fine_tune_epochs,
                  class_weight=weights, callbacks=callbacks)

    # The checkpoint holds the best val_accuracy across both phases (fine-tuning can make it worse).
    if checkpoint.exists():
        model = keras.models.load_model(checkpoint)
    loss, acc, top3 = model.evaluate(val_ds)
    print(f'Validation accuracy: {acc:.4f}  top-3: {top3:.4f}')
    report = {'arch': args.arch, 'img_size': args.img_size, 'num_classes': len(class_names),
              'val_accuracy': acc, 'val_top3': top3, 'val_loss': loss}
    if args.test_dir:
        report['test'] = evaluate_folder(model, args.test_dir, class_names, args.img_size)
        t = report['test']
        if t['n']:
            print(f"Field test accuracy: {t['accuracy']:.1%} (all classes), "
                  f"{t['accuracy_crop_known']:.1%} (crop known, like the app) on {t['n']} images")

    model_path, classes_path = out / 'disease_cnn.keras', out / 'disease_classes.json'
    backed_up = model_path.exists()
    if backed_up:
        shutil.copy2(model_path, out / 'disease_cnn.prev.keras')
    if classes_path.exists():
        shutil.copy2(classes_path, out / 'disease_classes.prev.json')
    model.save(model_path)
    classes_path.write_text(json.dumps(class_names, indent=2))
    (out / 'disease_metrics.json').write_text(json.dumps(report, indent=2))
    checkpoint.unlink(missing_ok=True)
    print(f'Saved model to {out}' + (' (previous model kept as disease_cnn.prev.keras)' if backed_up else ''))


if __name__ == '__main__':
    main()
