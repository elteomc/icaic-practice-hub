import torch
from torch import nn


class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.output = nn.Linear(2, 1)

    def forward(self, x):
        return self.output(x)
