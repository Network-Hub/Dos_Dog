import torch.nn as nn
from params import *
import torch


class Flatten(nn.Module):
    def __init__(self):
        super(Flatten, self).__init__()

    def forward(self, x):
        return x.view(x.size(0), -1)


class simpleExtractor(nn.Module):
    """
    https://blog.csdn.net/zchang81/article/details/75370662
    """

    def __init__(self):
        super(simpleExtractor, self).__init__()
        self.cnn_encoder = nn.Sequential(
            nn.Conv2d(1, n_c * 2, kernel_size=3, stride=1, padding=1),  # 输入：[batch_size*pkt,1,32,32]，输出：[batch_size,32,
            # 32,32]
            nn.ReLU(nn.BatchNorm2d(n_c * 2)),
            nn.MaxPool2d(2),  # 输入：[batch_size*pkt_num,1,32,32]，输出：[batch_size*pkt_num,32,16,16]
            nn.Dropout(0.25),
            nn.Conv2d(n_c * 2, 4 * n_c, kernel_size=3, stride=1, padding=1),
            # 输入：[batch_size,32,16,16]，输出：[batch_size,32,16,16]
            nn.ReLU(nn.BatchNorm2d(4 * n_c)),
            # 输入：[batch_size*pkt,64,16,16]，输出：[batch_size*pkt,nc,14,14],
            nn.Conv2d(4 * n_c, n_c, kernel_size=3, stride=1),
            nn.ReLU(nn.BatchNorm2d(n_c)),
            nn.MaxPool2d(2),  # 输入：[batch_size*pkt,nc,14,14]，输出：[batch_size*pkt,nc,7,7]
            nn.Dropout(0.25),
            Flatten(),  # 输入：[batch_size*pkt,nc,7,7]，输出：[batch_size,pkt*nc*7*7]
            nn.Linear(n_c * 7 * 7, 32)  # 输入：[batch_size,pkt*nc*7*7]，输出：[batch_size,32*pkt]
        )
        self.gru_encoder = nn.GRU(32, 16, 1, bidirectional=True, batch_first=True)
        # self.flatten = Flatten()

    def forward(self, x):
        x = self.cnn_encoder(x)  # 输出：[96, 32]
        # print("x in extractor!", x.shape)
        x = x.view(batch_size, package_num, 32)  # 输入：[batch_size*batch_size,32]，输出：[batch_size,pkt,32]
        x, h = self.gru_encoder(x)  # 输入：[batch_size,pkt,32], 输出：[batch_size,pkt,32]
        x = torch.flatten(x, start_dim=1)  # 输入：[batch_size,pkt,32], 输出：[batch_size,pkt*32]
        return x


class simpleClassifier(nn.Module):
    """
    https://blog.csdn.net/zchang81/article/details/75370662
    """

    def __init__(self):
        super(simpleClassifier, self).__init__()
        self.classifier = nn.Sequential(
            nn.Linear(package_num * 32, 1),  # 输入：[batch_size,pkt*32], 输出：[batch_size,1]
            nn.Sigmoid()
        )

    def forward(self, x):
        x = self.classifier(x)
        return x
