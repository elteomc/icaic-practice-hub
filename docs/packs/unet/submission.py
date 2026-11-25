import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

### QUESTION 2.1 START: Fix the Architecture (10 pts)

class BrokenUNet(nn.Module):
    def __init__(self, in_channels=3, out_classes=2):
        super(BrokenUNet, self).__init__()
        
        # --- ENCODER (Intern removed padding to 'save compute') ---
        # Note: kernel=3, padding=0 causes spatial dimension reduction by 2 pixels per layer.
        self.enc1_1 = nn.Conv2d(in_channels, 64, kernel_size=3, padding=0) 
        self.enc1_2 = nn.Conv2d(64, 64, kernel_size=3, padding=0)
        self.pool1 = nn.MaxPool2d(2) # Downsample by 2
        
        self.enc2_1 = nn.Conv2d(64, 128, kernel_size=3, padding=0)
        self.enc2_2 = nn.Conv2d(128, 128, kernel_size=3, padding=0)
        self.pool2 = nn.MaxPool2d(2) # Downsample by 2
        
        # --- BOTTLENECK ---
        self.bot1 = nn.Conv2d(128, 256, kernel_size=3, padding=0)
        self.bot2 = nn.Conv2d(256, 256, kernel_size=3, padding=0)
        
        # --- DECODER ---
        self.upconv1 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        
        # Decoder Convolutions
        # Expects 256 input channels (128 from upconv + 128 from skip)
        self.dec1_1 = nn.Conv2d(256, 128, kernel_size=3, padding=0)
        self.dec1_2 = nn.Conv2d(128, 64, kernel_size=3, padding=0)
        
        self.final = nn.Conv2d(64, out_classes, kernel_size=1)

    def center_crop(self, layer, target_shape):
        """
        Crop the layer to match target dimensions (center-aligned).
        
        Why needed: With padding=0, encoder feature maps are LARGER than 
        decoder feature maps after upsampling. We need to crop the encoder 
        features from the center to match decoder size for concatenation.
        
        Args:
            layer: Tensor of shape (B, C, H_large, W_large) - the skip connection from encoder
            target_shape: torch.Size (B, C, H_small, W_small) - the upsampled decoder tensor
        
        Returns:
            Cropped tensor of shape (B, C, H_small, W_small)
        
        Example:
            layer shape: (1, 128, 122, 122)  <- from encoder
            target_shape: (1, 128, 114, 114) <- from decoder after upsampling
            Need to crop: from [122x122] to [114x114]
            Center crop: start at (122-114)//2 = 4, end at 4+114 = 118
            Return: layer[:, :, 4:118, 4:118]
        """
        # TODO Step 1: Extract dimensions from layer

        # TODO Step 2: Extract target dimensions from target_shape

        # TODO Step 3: Calculate center crop offsets

        # TODO Step 4: Return center-cropped tensor
        raise NotImplementedError('Implement the center crop')
    

    def forward(self, x):
        # 1. Encoder 1
        x1 = F.relu(self.enc1_1(x))
        x1 = F.relu(self.enc1_2(x1))
        x1_p = self.pool1(x1)
        
        # 2. Encoder 2
        x2 = F.relu(self.enc2_1(x1_p))
        x2 = F.relu(self.enc2_2(x2))
        x2_p = self.pool2(x2)
        
        # 3. Bottleneck
        bot = F.relu(self.bot1(x2_p))
        bot = F.relu(self.bot2(bot))
        
        # 4. Decoder 1
        d1 = self.upconv1(bot)
        
        # --- CRASH POINT: Shape Mismatch ---
        # x2 is larger (from Encoder). d1 is smaller (from Bottleneck).
        # You must use self.center_crop() here to make x2 match d1.
        
        # TODO: UNCOMMENT the line below after implementing center_crop()
        x2_cropped = x2  # This placeholder will cause a crash - you must fix it!
        
        # Concatenate along channel axis (dim=1)
        cat1 = torch.cat((x2_cropped, d1), dim=1)
        
        dec1 = F.relu(self.dec1_1(cat1))
        dec1 = F.relu(self.dec1_2(dec1))
        
        return self.final(dec1)

### QUESTION 2.1 END

def calculate_miou(pred_mask, true_mask, num_classes=2):
    """Average class IoUs, skipping classes with zero union."""
    raise NotImplementedError("Implement mean IoU")
