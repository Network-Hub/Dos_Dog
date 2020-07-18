from flow_dump import *
import random

if __name__ == '__main__':
    print("---start sniff the packet---")
    save_path = folder_root + os.sep + "results" + os.sep + "label_" + str(random.randint(1, 1000)) + ".csv"
    sniff_main(save_path)  # 开始嗅探数据包
