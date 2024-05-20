import numpy as np

from SubTask import SubTask


class CloudTask():  # 继承Problem父类
    def __init__(self):
        self.startTime = 0
        self.finshedTime = 0
        self.subtask: SubTask = None
        self.communication_flag_c = np.array([0, 0, 0, 0, 0, 0])  # 边到云的通信消耗，HSI MSI W H S C
        self.id = -1
        self.n = -1
        self.r = -1
        self.pre = []

