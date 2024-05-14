
class Task():  # 继承Problem父类
    def __init__(self):
        self.id = 0         # 任务提交的顺序
        self.n = -1         # 在那个飞机上的
        self.preNode = None # 前面一个task
        self.nextNode = None #
        self.subTasks = []
        self.photoTime = 0  # 拍照时间，也就是到这个地方的时间，从0开始算
        self.position = [0, 0]  # 地址
        self.quene = []
        self.data_c = {'HSI': 1,
                       'MSI': 0,
                       'W': 0,
                       'H': 0,
                       'S': 0,
                       'C': 0}  # 是否在云端
        self.data_e = {'HSI': 0,
                       'MSI': 1,
                       'W': 0,
                       'H': 0,
                       'S': 0,
                       'C': 0}  # 是否在边端缓存了

        # self.subid = 0      # 0表示W  1表示H 2 表示S 3表示C
        # self.startTime = 0  # 开始时间
        # self.submitTime = 0 # 任务提交时间
        # self.endTime = 0    # 结束时间
        # self.position = 0   # position 表示在无人机还是云端， 范围是0到K+N 0-N表示在无人机上，N到K+N表示
        # self.pre = []       # 前序节点




