# users/ml_model.py
import os


import librosa
import logging
import numpy as np
from django.conf import settings  # for MEDIA_ROOT or weight path
# from .views import AttentionCNN  # adjust this import to where you put the class

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F


# Attention modules remain unchanged
class ChannelAttention(nn.Module):
   def __init__(self, in_channels, reduction=16):
       super(ChannelAttention, self).__init__()
       self.avg_pool = nn.AdaptiveAvgPool2d(1)
       self.max_pool = nn.AdaptiveMaxPool2d(1)

       self.fc = nn.Sequential(
           nn.Conv2d(in_channels, in_channels // reduction, 1, bias=False),
           nn.ReLU(),
           nn.Conv2d(in_channels // reduction, in_channels, 1, bias=False)
       )
       self.sigmoid = nn.Sigmoid()

   def forward(self, x):
       avg_out = self.fc(self.avg_pool(x))
       max_out = self.fc(self.max_pool(x))
       out = avg_out + max_out
       return self.sigmoid(out) * x  # Apply attention directly


class SpatialAttention(nn.Module):
   def __init__(self, kernel_size=7):
       super(SpatialAttention, self).__init__()
       assert kernel_size in (3, 7), 'kernel size must be 3 or 7'
       padding = 3 if kernel_size == 7 else 1

       self.conv = nn.Conv2d(2, 1, kernel_size, padding=padding, bias=False)
       self.sigmoid = nn.Sigmoid()

   def forward(self, x):
       avg_out = torch.mean(x, dim=1, keepdim=True)
       max_out, _ = torch.max(x, dim=1, keepdim=True)
       x_cat = torch.cat([avg_out, max_out], dim=1)
       out = self.conv(x_cat)
       return self.sigmoid(out) * x  # Apply attention directly


# Updated model: AttentionCNN now uses num_classes=2 for binary classification.
class AttentionCNN(nn.Module):
   def __init__(self, num_classes=2):
       super(AttentionCNN, self).__init__()

       # First conv block
       self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
       self.bn1 = nn.BatchNorm2d(32)
       self.relu1 = nn.ReLU()
       self.pool1 = nn.MaxPool2d(2)
       self.ca1 = ChannelAttention(32)
       self.sa1 = SpatialAttention()

       # Second conv block
       self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
       self.bn2 = nn.BatchNorm2d(64)
       self.relu2 = nn.ReLU()
       self.pool2 = nn.MaxPool2d(2)
       self.ca2 = ChannelAttention(64)
       self.sa2 = SpatialAttention()

       # Third conv block
       self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
       self.bn3 = nn.BatchNorm2d(128)
       self.relu3 = nn.ReLU()
       self.pool3 = nn.MaxPool2d(2)
       self.ca3 = ChannelAttention(128)
       self.sa3 = SpatialAttention()

       # Global pooling and classifier
       self.avg_pool = nn.AdaptiveAvgPool2d(1)
       self.flatten = nn.Flatten()
       self.fc1 = nn.Linear(128, 64)
       self.relu4 = nn.ReLU()
       self.dropout = nn.Dropout(0.5)
       self.fc2 = nn.Linear(64, num_classes)  # num_classes is now 2

   def forward(self, x):
       # Conv block 1 with attention
       x = self.pool1(self.relu1(self.bn1(self.conv1(x))))
       x = self.ca1(x)
       x = self.sa1(x)

       # Conv block 2 with attention
       x = self.pool2(self.relu2(self.bn2(self.conv2(x))))
       x = self.ca2(x)
       x = self.sa2(x)

       # Conv block 3 with attention
       x = self.pool3(self.relu3(self.bn3(self.conv3(x))))
       x = self.ca3(x)
       x = self.sa3(x)

       # Classifier
       x = self.avg_pool(x)
       x = self.flatten(x)
       x = self.dropout(self.relu4(self.fc1(x)))
       x = self.fc2(x)

       return x


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = AttentionCNN(num_classes=2).to(DEVICE)

# 2) Load & filter the checkpoint
checkpoint = torch.load(os.path.join(settings.BASE_DIR, "model.pth"),
                        map_location=DEVICE)
model_dict = model.state_dict()

# Keep only the keys that both exist in the checkpoint *and* have the same shape
filtered_dict = {
    k: v
    for k, v in checkpoint.items()
    if k in model_dict and v.size() == model_dict[k].size()
}

# Report what we’re loading / skipping
print(
    f"Loading {len(filtered_dict)}/{len(model_dict)} parameters from checkpoint")
skipped = set(model_dict.keys()) - set(filtered_dict.keys())
if skipped:
    print("  Skipped layers:", skipped)

# 3) Update & load
model_dict.update(filtered_dict)
model.load_state_dict(model_dict)

model.eval()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
def predict_cough(wav_path: str) -> dict:
    """
    1) Load a WAV file
    2) Preprocess to log‑mel spectrogram
    3) Run through the CNN
    4) Return { 'healthy': prob, 'covid': prob }
    """
    # load audio (16 kHz mono)
    y, sr = librosa.load(wav_path, sr=16000, mono=True)
    # pad/trim to exactly 3 s
    target = sr * 3
    if len(y) < target:
        y = np.pad(y, (0, target - len(y)))
    else:
        y = y[:target]

    # mel‑spectrogram
    melspec = librosa.feature.melspectrogram(
        y=y, sr=sr, n_fft=1024, hop_length=512, n_mels=128
    )
    log_mel = librosa.power_to_db(melspec)
    # normalize (use same stats as training if you have them)
    log_mel = (log_mel - log_mel.mean()) / (log_mel.std() + 1e-6)

    # to tensor shape (1,1,128, T)
    tensor = (
        torch.from_numpy(log_mel)
        .unsqueeze(0)
        .unsqueeze(0)
        .float()
        .to(DEVICE)
    )

    # inference
    with torch.no_grad():
        logits = model(tensor)
        probs = F.softmax(logits, dim=1).cpu().numpy()[0]

    return {"healthy": float(probs[0]), "covid": float(probs[1])}
