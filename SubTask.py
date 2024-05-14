
class SubTask():  # 继承Problem父类
    def __init__(self):
        self.i = -1 # 第几个task 1 2 3 4 5
        self.r = -1 # 无人机上的序号
        self.n = -1 # 无人机的序号

        self.preNodes = None  # 前序节点，None没有
        self.submitTime = -1 #提交的时间， 和任务产生的时间有关系
        self.pos = -1   # 任务在无人机运行（无人机id）还是在虚拟机运行，虚拟机id
        self.communication = 0
        self.execution_time_c = 0  # 在云端的计算时间
        self.execution_time_e = 0  # 在边缘端的计算时间
        self.finished_time = 0 # 记录理论上任务提交到结束的时间，不管在云端还是边端
        self.parallelism = 0
        self.power_cost = 0

