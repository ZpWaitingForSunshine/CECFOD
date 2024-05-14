class TaskGroup():  # 任务
    def __init__(self):
        self.taskList = []  # 存储task
        self.firstNode = None
        self.lastNode = None
        self.power_fly_cost = 0
        self.power_compute_cost = 0
