import torch
from torch import nn


class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 4, 3)
        self.pool1 = nn.MaxPool2d(2)
        self.conv2 = nn.Conv2d(4, 4, 3)
        self.pool2 = nn.MaxPool2d(2)
        self.activation = nn.ReLU()
        self.output = nn.Linear(4 * 6 * 6, 1)
        self.probability = nn.Sigmoid()

    def forward(self, x):
        x = self.pool1(self.activation(self.conv1(x)))
        x = self.pool2(self.activation(self.conv2(x)))
        return self.probability(self.output(x.flatten(1)))
