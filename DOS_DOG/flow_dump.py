# encoding: utf-8
import queue
from flow_detector import *

# 定义一个字典用来记录每个流已经嗅探到的数据包个数
flow_recorder = {}
# 定义一个队列用来缓存数据包
q = queue.Queue()


def put_pkt_to_queue(pkts):
    for pkt in pkts:
        q.put(pkt)


def get_pkt_id(pkt):
    if pkt.haslayer('IP'):
        src_ip = pkt["IP"].src
        dst_ip = pkt["IP"].dst
        if pkt.haslayer('TCP'):
            src_port = pkt['TCP'].sport
            dst_port = pkt['TCP'].dport
            protocol = 'TCP'
        elif pkt.haslayer('UDP'):
            src_port = pkt['UDP'].sport
            dst_port = pkt['UDP'].dport
            protocol = 'UDP'
        elif pkt.haslayer(' ICMP'):
            src_port = "NULL"
            dst_port = "NULL"
            protocol = 'ICMP'
        else:
            src_port = "NULL"
            dst_port = "NULL"
            protocol = 'OTHERS'
    else:
        return ""

    pkt_id = str(src_ip) + "_" + str(src_port) + "_" + str(dst_ip) + "_" + str(dst_port) + "_" + str(protocol)

    return pkt_id


def make_dir(new_dir_path):
    """
    create the new directory if it not exist
    :param new_dir_path: absolutely path , the new directory
    :return: absolutely path
    """
    if os.path.exists(new_dir_path):
        pass
    else:
        os.makedirs(new_dir_path)

    return new_dir_path


# 冒泡事件触发函数
def put_pkt_to_folder(pkt, pkt_id):
    save_folder = make_dir(folder_root + os.sep + "flow" + os.sep + str(pkt_id))
    wrpcap(save_folder + os.sep + str(random.randint(0, 1000)) + ".pcap", pkt)
    # print(pkt_id, " dumped to ", save_folder, " success!")
    # 更新字典中的值
    if pkt_id in flow_recorder:
        flow_recorder[pkt_id] = flow_recorder[pkt_id] + 1
    else:
        flow_recorder[pkt_id] = 1
    if is_full(pkt_id):
        # flow_recorder.pop(pkt_id)
        print(flow_recorder[pkt_id])
        flow_recorder[pkt_id] = 0  # 重新计数
        return 1
    else:
        return 0


def start_detect(pkt_id):
    flow_array = transform_main(pkt_id)
    label = detector_main(flow_array)
    print(pkt_id, "is:", label)
    return label


def dump_pkt_from_queue():
    if q.empty():
        # print("queue is empty!")
        return "NULL", -1
    else:
        pkt = q.get()
        pkt_id = get_pkt_id(pkt)
        if pkt_id == "":
            return "NULL", -1
        else:
            flag = put_pkt_to_folder(pkt, pkt_id)
            return pkt_id, flag


# 要开一个新的线程来专门嗅探数据包
def sniff_pkt():
    while True:
        pkts = sniff(filter=sniff_filter, iface=sniff_iface, count=sniff_count)  # 抓包 # prn=lambda x: x.show()
        put_pkt_to_queue(pkts)


def sniff_main(save_path):
    # 创建一个线程用来监听数据包
    thread1 = threading.Thread(target=sniff_pkt, name="thread1")
    # 开启监听
    thread1.start()
    # 尝试从队列中获取数据包
    i = 0
    while True:
        pkt_id, flag = dump_pkt_from_queue()
        if flag == 1:
            label = start_detect(pkt_id)
            save_label(save_path, label, i)
            i += 1


def is_full(pkt_id):
    if flow_recorder[pkt_id] >= pkt_num:
        return True
    else:
        return False


if __name__ == '__main__':
    sniff_main()
