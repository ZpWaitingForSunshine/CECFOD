#
import numpy as np

class Settings:
    def __init__(self):
        # 坐标
        self.H = 1000    # 地图长
        self.W = 1000    # 地图宽
        self.N = 4   # 无人机数量
        self.M = 10  # 可疑区域
        self.K = 5   # 云虚拟机
        self.I = 5  # 子任务个数
        self.places = np.array([[0.4, 0.4439],
                           [0.2439, 0.1463],
                           [0.1707, 0.2293],
                           [0.2293, 0.761],
                           [0.5171, 0.9414],
                           [0.8732, 0.6536],
                           [0.6878, 0.5219],
                           [0.8488, 0.3609],
                           [0.6683, 0.2536],
                           [0.6195, 0.2634]])

        self.s = 1 # 飞行速度
        self.Pf = 1 # 飞行功率
        self.E = np.ones(self.N)  # En的电量
        self.D = np.zeros(self.N)  # En的电量
        self.RDMT_Cloud = np.array([[1, 2, 3, 4, 5],
                         [1, 2, 3, 4, 5],
                         [1, 2, 3, 4, 5],
                         [1, 2, 3, 4, 5],
                         [1, 2, 3, 4, 5]])  # 云虚拟机的RDMT表，一行表示一个任务才不同并行度的执行时间
        self.RDMT_Edge = np.array([1, 1, 1, 1, 1])   # 五个任务在无人机上执行需要多少时间
        self.Pi_edge = np.array([1, 1, 1, 1, 1])     # 五个任务在无人机上执行的功耗
        self.w_cost_c2e = np.array([1, 1, 1, 1, 1, 1])  # 云到边的通信消耗，HSI MSI W H S C
        self.w_cost_e2c = np.array([1, 1, 1, 1, 1, 1])  # 边到云的通信消耗，HSI MSI W H S C







