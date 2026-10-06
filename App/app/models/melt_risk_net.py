import torch.nn as nn


class MeltRiskNet(nn.Module):
    """Same architecture as the training scripts (p3_combined_A.py / p3_combined_B.py)."""

    def __init__(self, input_size, hidden1, hidden2):
        super().__init__()
        self.layer1 = nn.Linear(input_size, hidden1)
        self.relu1 = nn.ReLU()
        self.layer2 = nn.Linear(hidden1, hidden2)
        self.relu2 = nn.ReLU()
        self.layer3 = nn.Linear(hidden2, 1)

    def forward(self, x):
        x = self.layer1(x)
        x = self.relu1(x)
        x = self.layer2(x)
        x = self.relu2(x)
        x = self.layer3(x)
        return x
