"""YOLO11 decoupled detection heads + CIoU, DFL, classification and mask losses."""
import argparse
from pathlib import Path


def main():
    from ultralytics import YOLO
    p = argparse.ArgumentParser()
    p.add_argument('data'); p.add_argument('--task', choices=['detect', 'segment'], default='segment')
    p.add_argument('--weights', default='yolo11x-seg.pt'); p.add_argument('--epochs', type=int, default=150)
    p.add_argument('--device', default='cpu'); p.add_argument('--batch', type=int, default=4)
    p.add_argument('--size', type=int, default=1024); p.add_argument('--project', default='field_vision/runs')
    a = p.parse_args()
    model = YOLO(a.weights)
    if model.task != a.task:
        raise ValueError('Use yolo11x-seg.pt for segmentation or yolo11m.pt for detection')
    model.train(data=str(Path(a.data).resolve()), epochs=a.epochs, imgsz=a.size,
                device=a.device, batch=a.batch, project=a.project, name='lesions',
                seed=42, deterministic=True, patience=30, workers=2,
                # Large native-resolution input reduces tiny-lesion destruction.
                box=9.0, cls=.5, dfl=2.0, mask_ratio=1, overlap_mask=False,
                # Outdoor transforms were materialized with synchronized labels.
                mosaic=0., mixup=0., hsv_h=0., hsv_s=0., hsv_v=0.,
                degrees=0., translate=0., scale=0., fliplr=0., flipud=0.)


if __name__ == '__main__':
    main()
