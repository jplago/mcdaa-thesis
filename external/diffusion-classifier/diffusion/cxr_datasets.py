import pandas as pd
import torch
from torch.utils.data import Dataset
from PIL import Image
import torchvision.transforms as transforms
import os

class CXRDataset(Dataset):
    def __init__(self, csv_file, dataset_base_path, transform=None):
        self.data = pd.read_csv(csv_file)
        self.transform = transform
        self.base_path = dataset_base_path
        
        # Create a mapping from file index to label
        self.file_to_class = {
            str(idx): self.data.iloc[idx]['label']
            for idx in range(len(self.data))
        }
        self.class_to_idx = {0:0, 1:1}
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        img_path = os.path.join(self.base_path, self.data.iloc[idx]['record_path'])
        label = int(self.data.iloc[idx]['label'])
        
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        
        return image, label

