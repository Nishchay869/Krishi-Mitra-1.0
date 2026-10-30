"""EigenCAM via PCA on feature activations; class-agnostic, not causal proof."""
import argparse
import json
from pathlib import Path


def main():
    import cv2
    import numpy as np
    import torch
    from PIL import Image, ImageOps
    from ultralytics import YOLO
    p = argparse.ArgumentParser(); p.add_argument('weights'); p.add_argument('image')
    p.add_argument('lesion_mask', help='Binary expert annotation in ORIGINAL image coordinates')
    p.add_argument('output'); p.add_argument('--layer', type=int, default=-2); p.add_argument('--size', type=int, default=1024)
    a = p.parse_args(); out = Path(a.output); out.mkdir(parents=True, exist_ok=False)
    model = YOLO(a.weights).model.cpu().eval()
    with Image.open(a.image) as source:
        image = source.convert('RGB')
    w, h = image.size; scale = a.size/max(w,h); nw,nh = round(w*scale),round(h*scale)
    left, top = (a.size-nw)//2, (a.size-nh)//2
    padded = Image.new('RGB',(a.size,a.size),(114,114,114)); padded.paste(image.resize((nw,nh)),(left,top))
    tensor = torch.from_numpy(np.array(padded).copy()).permute(2,0,1).unsqueeze(0).float()/255.
    activations = []
    def capture(_module, _inputs, output):
        if not isinstance(output, torch.Tensor) or output.ndim != 4:
            raise ValueError('Choose a layer with a BCHW tensor output')
        activations.append(output.detach())
    handle = model.model[a.layer].register_forward_hook(capture)
    try:
        with torch.inference_mode():
            model(tensor)
    finally:
        handle.remove()
    feature = activations[-1][0].permute(1,2,0).numpy()
    height,width,channels = feature.shape
    flat = feature.reshape(-1,channels); flat -= flat.mean(0,keepdims=True)
    _, _, vt = np.linalg.svd(flat, full_matrices=False)
    cam = (flat@vt[0]).reshape(height,width)
    # Eigenvector sign is arbitrary; preserve both interpretations for audit.
    mask = cv2.imread(a.lesion_mask, cv2.IMREAD_GRAYSCALE)
    if mask is None or mask.shape != (h,w) or not np.any(mask):
        raise ValueError('Nonempty lesion mask must match original image dimensions')
    scores = {}
    for name, heat in [('positive',cam),('negative',-cam)]:
        heat = (heat-heat.min())/(np.ptp(heat)+1e-8)
        heat = cv2.resize(heat,(a.size,a.size))[top:top+nh,left:left+nw]
        heat = cv2.resize(heat,(w,h))
        scores[name+'_mass_inside_lesions'] = float(heat[mask>0].sum()/(heat.sum()+1e-8))
        overlay = cv2.addWeighted(cv2.cvtColor(np.array(image),cv2.COLOR_RGB2BGR),.6,
                                 cv2.applyColorMap((heat*255).astype('uint8'),cv2.COLORMAP_JET),.4,0)
        cv2.imwrite(str(out/f'eigencam_{name}.png'),overlay)
    scores['lesion_area_fraction'] = float((mask>0).mean())
    (out/'audit.json').write_text(json.dumps(scores,indent=2))


if __name__ == '__main__':
    main()
