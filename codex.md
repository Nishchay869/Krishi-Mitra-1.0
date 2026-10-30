Act as a Principal Computer Vision Engineer and Agritech ML Specialist. 

I have a leaf disease detection model that achieved 99%+ accuracy on 5,000 lab/studio images (e.g., PlantVillage), but it completely fails on real-world field photos due to domain shift (the "Clever Hans" effect: shortcut learning on uniform backgrounds, studio lighting, and image downsampling).

Build an end-to-end, production-grade PyTorch and Ultralytics pipeline to solve this domain gap and achieve enterprise-level reliability (>95% precision with zero false-confidence on bad inputs).

Please generate clean, modular, production-ready code covering the following 5 modules:

---

### MODULE 1: DATA PIPELINE & BACKGROUND DECOUPLING
1. Synthetic Background Swapper:
   - Use `rembg` or `SAM 2` (Segment Anything 2) to segment the leaf foreground from existing lab datasets.
   - Composite the extracted leaf masks onto a bank of 2,000+ random outdoor field backgrounds (soil, farmers' hands, cloudy sky, harsh sunlight, weeds, stems).
2. In-Situ Dataset Integration:
   - Write instructions and loader scripts to integrate open-field datasets (PlantDoc, FieldPlant, Kaggle Cassava/FGVC).
3. Negative Class ("Not-A-Leaf / Healthy Background"):
   - Add a dedicated background class consisting of non-leaf objects (fingers, shoes, soil, tractor parts, healthy grass).

---

### MODULE 2: FIELD-ROBUST AUGMENTATION PIPELINE (Albumentations)
Configure an aggressive outdoor transformation pipeline that simulates real-world mobile capture:
- Lighting: `RandomSunFlare`, `RandomShadow`, `ColorJitter` (brightness, contrast, saturation).
- Camera noise: `MotionBlur`, `GaussianBlur`, `ISO / GaussNoise`.
- Physical occlusions: `CoarseDropout` (cutout to simulate fingers and overlapping foliage).
- Geometry: `ShiftScaleRotate` with letterboxed padding (preserving the native aspect ratio without distortion).

---

### MODULE 3: MODEL ARCHITECTURE (YOLOv11 Lesion Detection & Classification)
Instead of whole-image ResNet/EfficientNet classification, implement:
1. A YOLOv11-based object detection and instance segmentation pipeline (`yolo11x-seg` or `yolo11m`) trained to detect individual disease lesions rather than classify the entire frame.
2. Loss functions optimized for small lesion detection with decoupled heads to prevent background interference.

---

### MODULE 4: PRODUCTION GUARDRAILS & SELECTIVE PREDICTION
Write the inference service with safety thresholds:
1. Pre-Inference Quality Gate (OpenCV):
   - Reject blurry images using Laplacian variance thresholding (`cv2.Laplacian(img, cv2.CV_64F).var() < 100`).
   - Reject severe under/over-exposure via luminance histogram analysis.
2. Out-of-Distribution (OOD) & Confidence Filtering:
   - If maximum class probability < 0.80 or lesion area < minimum pixel threshold, trigger an explicit fallback: "Uncertain diagnosis. Please capture the leaf closer, in indirect daylight, and steady the camera."
   - Never output a high-confidence false diagnosis.

---

### MODULE 5: AUDITING & INTERPRETABILITY
1. Grad-CAM / EigenCAM implementation on test images to verify activations focus strictly on biological lesions and not on background soil or fingers.
2. Evaluation script calculating: mAP@0.5, mAP@0.5:0.95, Precision-Recall curves, and False Positive Rate on pure background photos.

Provide runnable Python scripts with requirements, clear directory layout, and deployment instructions