import torch
import torch.nn as nn
from torch.nn.utils import weight_norm
from typing import Dict, Any
from backend.deep_learning.models.base.enterprise_base_model import EnterpriseBaseModel

class Chomp1d(nn.Module):
    def __init__(self, chomp_size):
        super().__init__()
        self.chomp_size = chomp_size

    def forward(self, x):
        return x[:, :, :-self.chomp_size].contiguous()

class TemporalBlock(nn.Module):
    def __init__(self, n_inputs, n_outputs, kernel_size, stride, dilation, padding, dropout=0.2):
        super().__init__()
        self.conv1 = weight_norm(nn.Conv1d(n_inputs, n_outputs, kernel_size,
                                           stride=stride, padding=padding, dilation=dilation))
        self.chomp1 = Chomp1d(padding)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(dropout)

        self.conv2 = weight_norm(nn.Conv1d(n_outputs, n_outputs, kernel_size,
                                           stride=stride, padding=padding, dilation=dilation))
        self.chomp2 = Chomp1d(padding)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(dropout)

        self.net = nn.Sequential(self.conv1, self.chomp1, self.relu1, self.dropout1,
                                 self.conv2, self.chomp2, self.relu2, self.dropout2)
        self.downsample = nn.Conv1d(n_inputs, n_outputs, 1) if n_inputs != n_outputs else None
        self.relu = nn.ReLU()

    def forward(self, x):
        out = self.net(x)
        res = x if self.downsample is None else self.downsample(x)
        return self.relu(out + res)

class TemporalConvNet(EnterpriseBaseModel):
    """
    Temporal Convolutional Network using Dilated Causal Convolutions.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = "TCN"
        
        self.input_dim = config.get("num_features", 10)
        self.num_channels = config.get("num_channels", [32, 64, 128])
        self.kernel_size = config.get("kernel_size", 3)
        self.dropout = config.get("dropout", 0.2)
        
        layers = []
        num_levels = len(self.num_channels)
        for i in range(num_levels):
            dilation_size = 2 ** i
            in_channels = self.input_dim if i == 0 else self.num_channels[i-1]
            out_channels = self.num_channels[i]
            layers.append(TemporalBlock(
                in_channels, out_channels, self.kernel_size, stride=1, 
                dilation=dilation_size, padding=(self.kernel_size-1) * dilation_size, 
                dropout=self.dropout
            ))
            
        self.tcn = nn.Sequential(*layers)
        
        # We take the output of the last timestep
        self.head = nn.Linear(self.num_channels[-1], 1)

    def forward(self, x: tuple) -> torch.Tensor:
        seq, _ = x # mask is ignored in basic TCN (zero padding handled by causal conv implicitly)
        
        # TCN expects (Batch, Channels, SeqLen)
        seq = seq.transpose(1, 2)
        
        out = self.tcn(seq)
        
        # Take the last time step
        out = out[:, :, -1]
        
        return self.head(out)
