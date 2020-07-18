from params import *
import shutil
import numpy as np
from scapy.all import *


def remove_flow_folder(pkt_id):
    flow_folder = folder_root + "flow" + os.sep + str(pkt_id)
    shutil.rmtree(flow_folder)
    print(flow_folder, "is removed success!")


def get_files_hierarchically(dir_path):
    """
     get the files hierarchically under the folder
    :param dir_path: absolute path
    :return: narray , the item is the files with absolute path
    """
    files = np.array([])
    for home, dir_list, file_list in os.walk(dir_path):
        for filename in file_list:
            files = np.concatenate((files, [os.path.join(home, filename)]))
            # files.append(os.path.join(home, filename))
    # print("get %d files" % (len(files)))
    return files


def regularize_number(item):
    """
    transform the item into hexadecimal like "0xff"
    :param item:
    :return:
    """
    item = "".join(filter(str.isalnum, item))  # remove the non-number and non-alpha
    item = re.sub(r'[g-z]|[G-Z]', "", item)  # remove the illegal alpha except for (a-f,A-F)
    if 2 < len(item):
        item = item[:2]
    elif 0 == len(item):
        item = "00"
    else:
        item = "0" + item
    item = "0x" + item
    return item


def parse_binary(bin_object):
    """
    transfer the str to list with number
    :param bin_object:
    :return: narray (int)
    """
    num_array = np.array([])
    bin_list = str(bin_object).split("\\")
    for item in bin_list:
        if item == 'n' or item == 'b\'':
            pass
        else:
            item = regularize_number(item)
            num_array = np.concatenate((num_array, [int(item, 16)]))
    return num_array


def reshape_with_padding(pkt_narray, shape):
    """
     reshape the array by specified the shape,if the size of the pkt_array is smaller than
     shape, padding the pkt_array with zeros
    :param pkt_narray: narray , one dimensional list
    :param shape: list , one dimensional list
    :return: narray , 2 dimension narray with the specified shape
    """
    size = shape[0] * shape[1]
    if pkt_narray.size < size:
        for i in range(size - len(pkt_narray)):
            pkt_narray = np.append(pkt_narray, 0)
    else:
        pkt_narray = pkt_narray[:size]
    return pkt_narray.reshape(shape)


def process_packet(pkt):
    """
    process the pkt by the binary
    :param pkt: object , pkt object
    :return: narray, 3 dimension narray with shape like 1*n*m
    """
    reshape_size = tuple([1] + mat_size)
    packet_list = parse_binary(pkt)
    packet_narray = reshape_with_padding(packet_list, mat_size)

    return packet_narray.reshape(reshape_size)


def process_pcap(pcap_file):
    """
    process the pcap file into three dimension narray, each packet is an two dimension narray
    :param pcap_file: a pcap file path
    :return: narray, three dimensional narray like shape([n,m,l]),each packet is an matrix.
    """

    packet_list = rdpcap(pcap_file)
    flow_narray = np.array([])
    for i in range(min(pkt_num, len(packet_list))):
        if flow_narray.size == 0:
            flow_narray = process_packet(packet_list[i])
        else:
            flow_narray = np.concatenate((flow_narray, process_packet(packet_list[i])))
    return flow_narray


def flow_to_arr(pcap_list):
    """
     transfer the flow into npy
    :param pcap_list:
    :return: narray, two, the x contains the matrix and the y contains the label
    """
    x = []
    for pcap in pcap_list:
        pkt_array = process_pcap(pcap)
        x.append(pkt_array)
    return np.array(x)  # three dimensional narray like shape([n,m,l]),each packet is an matrix.


def get_flow_from_folder(pkt_id):
    flow_folder = folder_root + "flow" + os.sep + str(pkt_id)
    files = get_files_hierarchically(flow_folder)
    flow_array = flow_to_arr(files)
    return flow_array


def padding(n_array):
    gap = pkt_num - n_array.shape[0]
    padding_arr = np.array(n_array)
    for i in range(gap):
        padding_arr = np.concatenate((padding_arr, np.zeros((1, 1, image_size, image_size))))
    return padding_arr


def transform_main(flow_id):
    f_array = get_flow_from_folder(flow_id)
    f_array = padding(f_array)
    remove_flow_folder(flow_id)
    return f_array


if __name__ == '__main__':
    pkt_id = "192.168.137.1_49718_239.255.255.250_1900_UDP"
    flow_array = get_flow_from_folder(pkt_id)
    print(flow_array.shape)
