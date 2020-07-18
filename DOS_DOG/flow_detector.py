from deep_model import *
import pandas as pd
from torch.autograd import Variable
from flow_transform import *

device = torch.device("cuda:0" if (torch.cuda.is_available() and ngpu > 0) else "cpu")  # choose CPU when available


def make_variable(tensor):
    tensor = Variable(tensor)
    tensor = tensor.float().to(device)
    return tensor


def get_from_trained_Classifier(save_root, prototype="simpleNet"):
    if prototype == "simpleNet":
        model = simpleClassifier()
    else:
        warnings.warn("not support yet!")
    model_path = save_root + "model" + os.sep + "netC.pkl"
    model.load_state_dict(torch.load(model_path))  # 从训练好的模型中加载参数直接初始化，这种优化策略比较直接
    model.eval()
    if torch.cuda.is_available() and ngpu > 0:
        model.cuda()
    return model


def get_from_trained_Extractor(save_root, prototype="simpleNet"):
    if prototype == "simpleNet":
        model = simpleExtractor()
    else:
        warnings.warn("not support yet!")
    model_path = save_root + "model" + os.sep + "netE.pkl"
    model.load_state_dict(torch.load(model_path))  # 从训练好的模型中加载参数直接初始化
    model.eval()
    if torch.cuda.is_available() and ngpu > 0:
        model.cuda()
    return model


def save_label(save_path, label, i):
    if os.path.exists(save_path):
        df = pd.read_csv(save_path, index_col=0)
    else:
        df = pd.DataFrame(columns=['predict'])
    df.loc[i] = label
    df.to_csv(save_path)
    print("label saved in", save_path)
    return save_path


def detect_flow(netE, netC, data):
    """
    test performance of the model which connect the extractor and the classifier
    :param data:
    :param netE: object, the extractor trained in target dataset
    :param netC: object, the classifier trained in source dataset
    :return:None
    """
    predict_array = np.array([])
    netE.eval()
    netC.eval()
    # vector =   # tensor, size default as ([64, 128, 4, 4])
    output = netC(netE(make_variable(torch.from_numpy(data))))  # 神经网络的输出是浮点型的(0,1)
    predict_array = np.append(predict_array, output.detach().cpu().clone().numpy())  # from GPU to CPU

    return predict_array


def binary(x):
    if x > 0.5:
        return 1
    else:
        return 0


def detector_main(flow_data):
    netC = get_from_trained_Classifier(folder_root)
    netE = get_from_trained_Extractor(folder_root)
    flow_label = binary(detect_flow(netE, netC, flow_data)[0])
    return flow_label


if __name__ == '__main__':
    pkt_id = "192.168.137.1_49718_239.255.255.250_1900_UDP"
    flow_array = get_flow_from_folder(pkt_id)
    label = detector_main(flow_array)
    print("the flow label is:", label)
