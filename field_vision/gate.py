"""Explicit leaf/background classifier and empirical embedding OOD distance."""
import argparse
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader


class LeafGate(nn.Module):
    def __init__(self, pretrained=False):
        super().__init__()
        self.backbone = models.resnet18(weights=models.ResNet18_Weights.DEFAULT if pretrained else None)
        self.backbone.fc = nn.Identity()
        self.head = nn.Linear(512, 2)

    def forward(self, x):
        features = self.backbone(x)
        return self.head(features), features


def transform():
    # Square padding instead of distorting leaf aspect ratio.
    from PIL import ImageOps
    return transforms.Compose([
        transforms.Lambda(lambda image: ImageOps.pad(image.convert('RGB'), (224, 224), color=(114,114,114))),
        transforms.ToTensor(), transforms.Normalize([.485,.456,.406], [.229,.224,.225])])


def embedding_distance(features, mean, variance):
    return ((features-mean)**2 / variance).mean(axis=-1)


def main():
    p = argparse.ArgumentParser(); p.add_argument('data'); p.add_argument('output')
    p.add_argument('--epochs', type=int, default=15); p.add_argument('--device', default='cpu')
    p.add_argument('--pretrained', action='store_true')
    a = p.parse_args(); torch.manual_seed(42); np.random.seed(42)
    train = datasets.ImageFolder(str(Path(a.data)/'train'), transform=transform())
    val = datasets.ImageFolder(str(Path(a.data)/'val'), transform=transform())
    if train.class_to_idx != {'background': 0, 'leaf': 1} or val.class_to_idx != train.class_to_idx:
        raise ValueError('Both splits must contain background and leaf classes')
    model = LeafGate(a.pretrained).to(a.device)
    counts = np.bincount(train.targets, minlength=2)
    loss_fn = nn.CrossEntropyLoss(weight=torch.tensor(1/counts, dtype=torch.float32, device=a.device))
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    for epoch in range(a.epochs):
        model.train()
        for images, targets in DataLoader(train, batch_size=32, shuffle=True):
            optimizer.zero_grad(); logits, _ = model(images.to(a.device))
            loss = loss_fn(logits, targets.to(a.device)); loss.backward(); optimizer.step()
        print(f'epoch={epoch+1} train_loss={loss.item():.4f}')
    model.eval()
    def features(dataset):
        chunks = []
        with torch.inference_mode():
            for images, targets in DataLoader(dataset, batch_size=32):
                _, feature = model(images.to(a.device))
                chunks.append(feature[targets.to(a.device)==1].cpu().numpy())
        return np.concatenate(chunks)
    known_train, known_val = features(train), features(val)
    if len(known_train) < 30 or len(known_val) < 30:
        raise ValueError('Need at least 30 distinct leaf samples in each split for OOD fitting')
    mean, variance = known_train.mean(0), known_train.var(0)+1e-3
    distances = embedding_distance(known_val, mean, variance)
    out = Path(a.output); out.mkdir(parents=True, exist_ok=False)
    torch.save(model.cpu().state_dict(), out/'leaf_gate.pt')
    np.savez(out/'ood.npz', mean=mean, variance=variance,
             threshold=np.quantile(distances, .99))
    print('OOD cutoff is empirical, NOT proof of detection of all unseen inputs. Evaluate negatives separately.')


if __name__ == '__main__':
    main()
