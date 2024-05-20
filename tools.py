import json
import math
# coding=utf-8
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from CloudTask import CloudTask
from Gantt import Gantt
from Relationship import Relationship
from SubTask import SubTask
import numpy as np

def split_array_by_greater_than_N(arr, N):
    sub_arrays = []  # 用于存储分割后的子数组
    temp_array = []  # 用于临时存储当前子数组的元素

    for num in arr:
        if num > N:
            # 当遇到大于9的数字时，将临时数组添加到结果中，并重置临时数组
            sub_arrays.append(temp_array)
            temp_array = []
        else:
            # 否则，将数字添加到临时数组中
            temp_array.append(num)

    # 将最后一个临时数组添加到结果中（如果它不为空）
    if temp_array:
        sub_arrays.append(temp_array)

    return sub_arrays

def calu_distance(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance
# def convert_to_2d_array(arr, elements_per_row):
#

def calu_fly_power_cost(places, m, W, H, s, P):
    if len(m) == 0:
        return 0
    else:
        distance = 0
        for i in range(len(m) - 1):
            distance += calu_distance(W * places[int(m[i])][0], H * places[int(m[i])][1], W * places[int(m[i + 1])][0], H * places[int(m[i + 1])][1])
        distance += calu_distance(0, 0, W * places[int(m[0])][0], H * places[int(m[0])][1])
        distance += calu_distance(W * places[int(m[-1])][0], H * places[int(m[-1])][1], 0, 0)
        return distance / s * P, distance  # 路程除以速度乘以功耗


def find_max_distance(groups):
    maxDistance = 0
    for task_group in groups:
        if maxDistance < task_group.distance:
            maxDistance = task_group.distance
    return maxDistance

# 找出前序节点的最晚的id
def find_max_finshedtime_pre(cloudTasks, edgeTasks, n, ls):
    finshedTime = 0
    for CT in cloudTasks:
        for cloudTask in CT:
            if cloudTask.subtask.i in ls and cloudTask.finshedTime > finshedTime:
                finshedTime = cloudTask.finshedTime

    # for ET in edgeTasks[n]:
    #     for edgeTask in ET:
    #         if edgeTask.subtask.i in ls and edgeTask.finshedTime < finshedTime:
    #             finshedTime = edgeTask.finshedTime
    for edgeTask in edgeTasks[n]:
        if edgeTask.subtask.i in ls and edgeTask.finshedTime > finshedTime:
            finshedTime = edgeTask.finshedTime

    return finshedTime

def find_max_finshedtime_cloud_pre(cloudTasks, edgeTasks, n, ls, vms):
    #
    print()
    finshedTime = 0
    # 先云端的finished time
    # 如果无前序节点，那云端最后一个
    indices = [index for index, value in enumerate(vms) if value == 1]
    for i in range(len(indices)):
        if len(cloudTasks[indices[i]]) > 0:
            last = cloudTasks[indices[i]][-1]
            if last.finshedTime > finshedTime:
                finshedTime = last.finshedTime

    # 如果有前序节点，那找云端和边端最后一个
    if ls and len(ls) > 0:
        for CT in cloudTasks:
            for cloudTask in CT:
                if cloudTask.subtask.i in ls and cloudTask.finshedTime > finshedTime:
                    finshedTime = cloudTask.finshedTime

        for edgeTask in edgeTasks[n]:
            if edgeTask.subtask.i in ls and edgeTask.finshedTime > finshedTime:
                finshedTime = edgeTask.finshedTime

    return finshedTime



def find_pre_subtask(cloudTasks, edgeTasks, n, ls, r):
    pre = []
    for CT in cloudTasks:
        for cloudTask in CT:
            if cloudTask.subtask.i in ls and cloudTask.subtask.n == n and cloudTask.subtask.r == r:
                pre.append(cloudTask.id)

    for edgeTask in edgeTasks[n]:
        if edgeTask.subtask.i in ls and edgeTask.subtask.n == n and edgeTask.subtask.r == r:
            pre.append(edgeTask.id)

    return pre
def build_relationship(cloudTasks, edgeTasks):
    # 从所有的节点找
    for CT in cloudTasks:
        for cloudTask in CT:
            if cloudTask.subtask.i == 3:
                cloudTask.pre = find_pre_subtask(cloudTasks, edgeTasks, cloudTask.n, [0, 1, 2], cloudTask.r)

            if cloudTask.subtask.i == 4:
                cloudTask.pre = find_pre_subtask(cloudTasks, edgeTasks, cloudTask.n, [3], cloudTask.r)

    for ET in edgeTasks:
        for edgeTask in ET:
            if edgeTask.subtask.i == 3:
                edgeTask.pre = find_pre_subtask(cloudTasks, edgeTasks, edgeTask.n, [0, 1, 2], edgeTask.r)

            if edgeTask.subtask.i == 4:
                edgeTask.pre = find_pre_subtask(cloudTasks, edgeTasks, edgeTask.n, [3], edgeTask.r)

def findlastfinshtime_c(cloudTasks):
    finishedTime = 0
    for CT in cloudTasks:
        if len(CT) > 0:
            t = CT[-1].finshedTime
            if t > finishedTime:
                finishedTime = t
    return finishedTime

def findlastfinshtime_e(edgeTasks):
    finishedTime = []
    for CT in edgeTasks:
        if len(CT) > 0:
            finishedTime.append(CT[-1].finshedTime)
        else:
            finishedTime.append(0)

    return finishedTime

def calu_power_cost(taskgroups):
    cost = []
    for taskgroup in taskgroups:
        cost.append(taskgroup.power_compute_cost + taskgroup.power_fly_cost)
    return cost

# 创建json
def create_json(cloudTasks, edgeTasks, N):
    links = []
    data = []
    for i, CT in enumerate(cloudTasks):
        for cloudTask in CT:
            gantt = Gantt()
            gantt.id = cloudTask.id
            gantt.start_date = cloudTask.startTime
            gantt.duration = cloudTask.finshedTime - cloudTask.startTime
            gantt.pos = i + N
            gantt.text = str(cloudTask.subtask.n) + "-" + str(cloudTask.subtask.r) + "-" + str(cloudTask.subtask.i)
            data.append(gantt.to_dict())

            # 创建links
            for p in range(len(cloudTask.pre)):
                relationship = Relationship()
                relationship.target = gantt.id
                relationship.source = cloudTask.pre[p]
                links.append(relationship.to_dict())

    for i, ET in enumerate(edgeTasks):
        for edgeTask in ET:
            gantt = Gantt()
            gantt.id = edgeTask.id
            gantt.start_date = edgeTask.startTime
            gantt.duration = edgeTask.finshedTime - edgeTask.startTime
            gantt.pos = i
            gantt.text = str(edgeTask.subtask.n) + "-" + str(edgeTask.subtask.r) + "-" + str(edgeTask.subtask.i)
            data.append(gantt.to_dict())

        for p in range(len(edgeTask.pre)):
            relationship = Relationship()
            relationship.target = gantt.id
            relationship.source = edgeTask.pre[p]
            links.append(relationship.to_dict())

    res = {"data": data, "links": links}

    class MyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return super(MyEncoder, self).default(obj)
    json_string = json.dumps(res, cls=MyEncoder)

    print(json_string)

def create_list(cloudTasks, edgeTasks, N, K):
    links = []
    left = [[] for _ in range(N + K)]
    add = [[] for _ in range(N + K)]
    text = [[] for _ in range(N + K)]
    data = []
    for i, CT in enumerate(cloudTasks):
        for cloudTask in CT:
            # gantt = Gantt()
            # gantt.id = cloudTask.id
            # gantt.start_date = cloudTask.startTime
            # gantt.duration = cloudTask.finshedTime - cloudTask.startTime
            # gantt.pos = i + N
            # gantt.text = str(cloudTask.subtask.n) + "-" + str(cloudTask.subtask.r) + "-" + str(cloudTask.subtask.i)
            # data.append(gantt.to_dict())
            left[i + N].append(cloudTask.startTime)
            add[i + N].append( cloudTask.finshedTime - cloudTask.startTime)
            text[i + N].append(str(cloudTask.subtask.n) + "-" + str(cloudTask.subtask.r) + "-" + str(cloudTask.subtask.i))

            # 创建links
            # for p in range(len(cloudTask.pre)):
            #     relationship = Relationship()
            #     relationship.target = gantt.id
            #     relationship.source = cloudTask.pre[p]
            #     links.append(relationship.to_dict())

    for i, ET in enumerate(edgeTasks):
        for edgeTask in ET:
            # gantt = Gantt()
            # gantt.id = edgeTask.id
            # gantt.start_date = edgeTask.startTime
            # gantt.duration = edgeTask.finshedTime - edgeTask.startTime
            # gantt.pos = i
            # gantt.text = str(edgeTask.subtask.n) + "-" + str(edgeTask.subtask.r) + "-" + str(edgeTask.subtask.i)
            # data.append(gantt.to_dict())
            left[i].append(edgeTask.startTime)
            add[i].append(edgeTask.finshedTime - edgeTask.startTime)
            text[i].append(str(edgeTask.subtask.n) + "-" + str(edgeTask.subtask.r) + "-" + str(edgeTask.subtask.i))
        # for p in range(len(edgeTask.pre)):
        #     relationship = Relationship()
        #     relationship.target = gantt.id
        #     relationship.source = edgeTask.pre[p]
        #     links.append(relationship.to_dict())

    drwaGantt(add, left, text)
    print()

def drwaGantt(add, left, text):
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # add = [[14, 6, 23], [18, 7, 35], [10, 30, 21], [18, 5, 30], [10, 25, 20], [12, 35, 20], [10, 32, 17], [10, 20, 16]]
    # left = [[0, 14, 20], [14, 32, 43], [32, 42, 78], [42, 72, 99], [60, 77, 129], [70, 102, 149], [82, 137, 169],
    #         [92, 169, 189]]
    m = range(len(add))
    color = ['b', 'g', 'r', 'y', 'c', 'm', 'k']

    # 画布设置，大小与分辨率
    plt.figure(figsize=(40, 8), dpi=80)
    # barh-柱状图换向，循坏迭代-层叠效果
    for i in m:
        if len(add[i]) > 0:
            n = range(len(add[i]))
            for j in n:
                plt.barh(m[i] + 1, add[i][j], left=left[i][j], color=color[j % len(color)])
                plt.text(left[i][j] + add[i][j] / 2, m[i] + 1, text[i][j], va='center', ha='center')
                # plt.text("hel")
    plt.title("流水加工甘特图")
    labels = [''] * len(add[0])
    # for f in n:
    #     labels[f] = "工序%d" % (f + 1)
    # 图例绘制
    # patches = [mpatches.Patch(color=color[i], label="{:s}".format(labels[i])) for i in range(len(add[0]))]
    # plt.legend(handles=patches, loc=4)
    # XY轴标签
    plt.xlabel("加工时间/s")
    plt.ylabel("工件加工优先级")
    # 网格线，此图使用不好看，注释掉
    # plt.grid(linestyle="--",alpha=0.5)
    plt.show()


# def sort_by_submittime(tasks_all):
#     submittime = 0
#     tasks_all_sorted = []
#     subtask_flag:SubTask = tasks_all[0]
#     while len(tasks_all) > 0:
#         for subtask in tasks_all:
#             if subtask_flag.submitTime >

