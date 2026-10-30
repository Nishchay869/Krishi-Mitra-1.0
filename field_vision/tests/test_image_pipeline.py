import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

READY = all(importlib.util.find_spec(name) for name in ('cv2','numpy','albumentations','PIL','yaml'))


@unittest.skipUnless(READY, 'Install the image pipeline dependencies in an isolated environment')
class ImagePipeline(unittest.TestCase):
    def test_quality_rejects_blur_dark_and_white(self):
        import numpy as np
        import cv2
        from field_vision.inference import quality_gate, Policy
        policy=Policy()
        self.assertEqual(quality_gate(np.zeros((300,500,3),dtype='uint8'),policy),'underexposed')
        self.assertEqual(quality_gate(np.full((300,500,3),255,dtype='uint8'),policy),'overexposed')
        self.assertEqual(quality_gate(np.full((300,500,3),128,dtype='uint8'),policy),'blurred')
        texture=np.random.default_rng(42).integers(40,200,(300,500,3),dtype='uint8')
        self.assertIsNone(quality_gate(texture,policy))
        self.assertEqual(quality_gate(cv2.GaussianBlur(texture,(31,31),10),policy),'blurred')

    def test_augmentation_keeps_validation_and_negative_labels(self):
        import numpy as np
        from PIL import Image
        from field_vision.data import prepare, validate_label
        from field_vision.augment import augment
        from field_vision.common import sha256
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); rows=[]
            for i,(split,kind) in enumerate([('train','leaf'),('train','background'),('val','leaf')]):
                image=root/f'{i}.png'; label=root/f'{i}.txt'
                Image.fromarray(np.random.default_rng(i).integers(30,220,(180,300,3),dtype='uint8')).save(image)
                label.write_text('0 .3 .3 .7 .3 .7 .7 .3 .7' if kind=='leaf' else '')
                rows.append({'image':str(image),'label':str(label),'split':split,'kind':kind,
                             'source':'test','group':str(i),'annotation_scope':'lesion_reviewed'})
            manifest=root/'manifest.jsonl'; manifest.write_text('\n'.join(json.dumps(r) for r in rows))
            prepare(manifest,root/'prepared',['lesion'],'segment')
            augment(root/'prepared',root/'augmented','segment',2,256,42)
            original=next((root/'prepared/images/val').glob('*'))
            self.assertEqual(sha256(original),sha256(root/'augmented/images/val'/original.name))
            self.assertEqual(len(list((root/'augmented/images/train').glob('*'))),6)
            for label in (root/'augmented/labels/train').glob('*'):
                validate_label(label.read_text(),'segment',1)
                if label.name.startswith('0000001'):
                    self.assertEqual(label.read_text(),'')
            rows[2]['group']=rows[0]['group']
            manifest.write_text('\n'.join(json.dumps(r) for r in rows))
            with self.assertRaisesRegex(ValueError,'leakage'):
                prepare(manifest,root/'leaky',['lesion'],'segment')
