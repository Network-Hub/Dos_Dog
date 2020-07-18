import os

folder_root = os.getcwd() + os.sep

sniff_count = 6
sniff_iface = "Intel(R) Dual Band Wireless-AC 8265"
sniff_filter = "not icmp"

pkt_num = 6
mat_size = [32, 32]

batch_size = 1  # 训练期间的batch大小
image_size = 32  # 训练图像的空间大小。所有图像将使用变压器调整为此大小。

package_num = 6

nc = 1  # 训练图像中的通道数。对于彩色图像，这是3
nz = 100  # 潜在向量 z 的大小(例如： 生成器输入的大小)
ngf = 32  # 生成器中特征图的大小
ndf = 32  # 判别器中特征图的大小
ngpu = 1
n_c = 16

