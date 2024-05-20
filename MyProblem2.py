# -*- coding: utf-8 -*-
"""MyProblem.py"""
import copy

import numpy as np
import geatpy as ea
import json

from CloudTask import CloudTask
from EdgeTask import EdgeTask
from SubTask import SubTask
from Task import Task
from TaskGroup import TaskGroup
from tools import split_array_by_greater_than_N, calu_distance, calu_fly_power_cost, find_max_finshedtime_pre, \
    find_max_finshedtime_cloud_pre, build_relationship
from Settings import Settings


class MyProblem(ea.Problem):  # 继承Problem父类
    def __init__(self):
        name = 'MyProblem'  # 初始化name（函数名称，可以随意设置）
        M = 1  # 初始化M（目标维数）

        self.settings = Settings()
        settings = self.settings

        # 初始化maxormins（目标最小最大化标记列表，1：最小化；-1：最大化）
        maxormins = [-1]

        # 初始化Dim（决策变量维数） 无人机 + 虚拟机个数 -1 + （无人机 + 虚拟机个数） * 子任务数量 * 任务数量
        Dim = settings.N + settings.M - 1 + (settings.K + settings.N) * settings.I * settings.M
        # 初始化决策变量的类型，元素为0表示变量是连续的；1为离散的
        varTypes = np.ones(Dim)
        lb = list(np.zeros(settings.N + settings.M - 1)) + list(np.zeros((settings.K + settings.N) * settings.I * settings.M))   # 决策变量下界
        ub = list((settings.N + settings.M - 2) * np.ones(settings.N + settings.M - 1)) + list(np.ones((settings.K + settings.N) * settings.I * settings.M))  # 决策变量上界
        lbin = [1] * Dim  # 决策变量下边界
        ubin = [1] * Dim  # 决策变量上边界

        # 调用父类构造方法完成实例化
        ea.Problem.__init__(self, name, M, maxormins, Dim, varTypes, lb,
                            ub, lbin, ubin)

    def aimFunc(self, pop):  # 目标函数
        X = pop.Phen  # 得到决策变量矩阵
        settings = self.settings

        places = settings.places  # 一个二维数组，
        W = settings.W
        H = settings.H
        s = settings.s

        relationships = []
        gantts = []

        # 获取前面N个  排列的
        front = settings.N + settings.M - 1
        # 区域分组
        groups = split_array_by_greater_than_N(np.reshape(X[:, 0: front], [-1]), front - settings.N)  # 把任务分给了无人机

        # task_matrix = convert_to_2d_array(X[:, front:], settings.I * settings.M)
        # 任务的表格
        task_schedule_matrix = np.reshape(X[:, front:], [settings.M, settings.I, settings.K + settings.N])
        # task_matrix = np.hsplit(X[:, front:], )
        # 区域任务分组
        task_groups = []  # 保存了所有task，每一行是一个无人机的任务合集

        for n in range(len(groups)):  # i表示group的无人机的id
            # 以下是一个无人机的飞行区域的操作
            task_group = TaskGroup()
            task_group.power_fly_cost = calu_fly_power_cost(places, groups[n], W, H, s, settings.Pf)  # 计算飞行的能量消耗
             # 无人机的序列  有先后顺序
            rn = len(groups[n])  # rn 无人机n的飞行区域

            for r in range(rn):  # 现在是一个无人机飞行的操作
                # 这里要给每个task
                task = Task()  # 初始化任务
                task.n = n   # 无人机编号
                task.id = groups[n][r]  # id 是任务的id，可以通过id找position的位置和任务
                if r > 0:
                    task.preNode = task_group.taskList[r - 1]
                task.position = places[int(task.id)] # 找到自己的地址

                # 获取所有任务的初始时间，上一个的时间加上距离和时间
                if r == 0:
                    task.photoTime = calu_distance(0, 0, W * task.position[0], H * task.position[1]) / s # 距离除以飞行速度,
                else:
                    # 获取上一个的飞行时间  和上一个的距离 算时间
                    task.photoTime = task.preNode.photoTime \
                                     + calu_distance(W * task.preNode.position[0], H * task.preNode.position[1],
                                                     W * task.position[0], H * task.position[1]) / s  # 距离除以飞行速度,
                # todo 然后获取 把初始化subtask，subtask 有提交的时间（不是最后的队列时间），有任务的发生位置，有消耗时间，
                task_n_schedule_matrix = task_schedule_matrix[int(task.id)]  # 获取任务排列矩阵 5 * 9 的矩阵，每一行代表这个任务在哪里运行,无人机在前，虚拟机在后

                for i in range(settings.I):  # I
                    subTask = SubTask()
                    subTask.n = n
                    subTask.i = i
                    subTask.r = r
                    subTask.rn = rn
                    # 确认一下这个task的子任务的前序
                    if i == 2:
                        subTask.preNodes = [0, 1, 2]
                    if i == 3:
                        subTask.preNodes = [3]
                    if i == 4:
                        subTask.preNodes = [4]
                    num_parallelism = np.sum(task_n_schedule_matrix[i, settings.N:])

                    #
                    if task_n_schedule_matrix[i][task.n] == 1 or num_parallelism == 0: # 表明在本地制作的
                        task.quene.append(1)
                        subTask.pos = 1  # 在边
                        subTask.execution_position = [n]
                        if i == 0:
                            # 如果第一个任务在边端，那只需要做W的更新即可
                            subTask.submitTime = task.photoTime     # 第一个时间是任务开始时间
                            subTask.execution_time_e = settings.RDMT_Edge[i]  # 执行时间
                            subTask.finished_time = subTask.submitTime + subTask.execution_time_e
                            task.data_e['W'] = 1  # W的认识
                            subTask.power_cost = settings.Pi_edge[i] #
                            task_group.power_compute_cost += subTask.power_cost

                        if i == 1:
                            subTask.execution_time_e = settings.RDMT_Edge[i]  # 执行时间
                            # 如果W也在边端 结束时间
                            if task.quene[0] == 1:
                                subTask.submitTime = task.subTasks[0].finished_time  # 第一个时间是任务开始时间
                                subTask.finished_time = subTask.submitTime + subTask.execution_time_e   # W更新的结束时间加上H的执行时间
                            else:
                                subTask.submitTime = task.photoTime
                                subTask.finished_time = subTask.submitTime + subTask.execution_time_e
                            task.data_e['H'] = 1
                            subTask.power_cost = settings.Pi_edge[i]  #
                            task_group.power_compute_cost += subTask.power_cost

                        if i == 2:
                            # 如果S在本地，需要下载HSI
                            if task.data_e['HSI'] == 0: # 没有缓存, 加上时间
                                subTask.communication = settings.w_cost_c2e[0]  # 加上交互的时间
                                task.data_e['HSI'] = 1  # 变为缓存
                                subTask.communication_flag_e[0] = 1  # 说明需要
                                # subTask.submitTime = task.photoTime + subTask.communication  # 第一个时间是任务开始时间
                            subTask.execution_time_e = settings.RDMT_Edge[i]   # 执行时间

                            if task.quene[1] == 1:
                                subTask.submitTime = task.subTasks[1].finished_time
                            elif task.quene[0] == 1 and task.quene[1] == 0:  # 第一个任务不在
                                subTask.submitTime = task.subTasks[0].finished_time
                                # subTask.finished_time = subTask.submitTime + subTask.communication + subTask.execution_time_e  # W更新完 给S更新
                            elif task.quene[0] == 0 and task.quene[1] == 0:
                                subTask.submitTime = task.photoTime

                            subTask.finished_time = subTask.submitTime + subTask.communication + subTask.execution_time_e  # H 更新完的时间加上交互时间
                            task.data_e['S'] = 1
                            subTask.power_cost = settings.Pi_edge[i]  #
                            task_group.power_compute_cost += subTask.power_cost

                        if i == 3:  # 更新C  需要 等所有的
                            subTask.execution_time_e = settings.RDMT_Edge[i]  # 执行时间
                            if task.data_e['W'] == 0: # 没有缓存, W在云上
                                subTask.communication += settings.w_cost_c2e[0]  # 加上交互的时间
                                task.data_e['W'] = 1  # 变为缓存
                                subTask.communication_flag_e[2] = 1  # 说明需要
                            if task.data_e['H'] == 0: # 没有缓存, H在云上
                                subTask.communication += settings.w_cost_c2e[1]  # 加上交互的时间
                                task.data_e['H'] = 1  # 变为缓存
                                subTask.communication_flag_e[3] = 1  # 说明需要
                            if task.data_e['S'] == 0:  # 没有缓存, S在云上
                                subTask.communication += settings.w_cost_c2e[2]  # 加上交互的时间
                                task.data_e['S'] = 1  # 变为缓存
                                subTask.communication_flag_e[4] = 1  # 说明需要
                            # 找到边上那个最晚的任务时间 max(WHS)
                            subTask.submitTime = max(task.subTasks[0].finished_time,
                                                        task.subTasks[1].finished_time,
                                                        task.subTasks[2].finished_time)
                            subTask.finished_time = subTask.submitTime + subTask.communication + subTask.execution_time_e #  + 通讯时间和执行时间 就是结束时间
                            task.data_e['C'] = 1
                            subTask.power_cost = settings.Pi_edge[i]  #
                            task_group.power_compute_cost += subTask.power_cost

                        if i == 4:  # 融合目标检测 需要WHSC
                            subTask.execution_time_e = settings.RDMT_Edge[i]  # 执行时间
                            if task.data_e['W'] == 0:  # 没有缓存, W在云上
                                subTask.communication += settings.w_cost_c2e[2]  # 加上交互的时间
                                task.data_e['W'] = 1  # 变为缓存
                                subTask.communication_flag_e[2] = 1  # 说明需要
                            if task.data_e['H'] == 0:  # 没有缓存, H在云上
                                subTask.communication += settings.w_cost_c2e[3]  # 加上交互的时间
                                task.data_e['H'] = 1  # 变为缓存
                                subTask.communication_flag_e[3] = 1  # 说明需要
                            if task.data_e['S'] == 0:  # 没有缓存, S在云上
                                subTask.communication += settings.w_cost_c2e[4]  # 加上交互的时间
                                task.data_e['S'] = 1  # 变为缓存
                                subTask.communication_flag_e[4] = 1  # 说明需要
                            if task.data_e['C'] == 0:  # 没有缓存, C在云上
                                subTask.communication += settings.w_cost_c2e[5]  # 加上交互的时间
                                task.data_e['C'] = 1  # 变为缓存
                                subTask.communication_flag_e[5] = 1  # 说明需要
                            subTask.submitTime = task.subTasks[i - 1].finished_time
                            subTask.finished_time = subTask.submitTime + subTask.communication + subTask.execution_time_e
                            subTask.power_cost = settings.Pi_edge[i]  #
                            task_group.power_compute_cost += subTask.power_cost

                    else:  # 在云上
                        task.quene.append(0)
                        subTask.pos = 0
                        subTask.parallelism = num_parallelism
                        subTask.execution_position = list(task_n_schedule_matrix[i, settings.N:])
                        if i == 0:  # 如果MSI在云端，需要上传
                            subTask.submitTime = task.photoTime
                            if task.data_c['MSI'] == 0:  # 没有缓存, 加上时间
                                subTask.communication = settings.w_cost_e2c[1]  # 加上交互的时间
                                task.data_c['MSI'] = 1  # 变为缓存
                                subTask.communication_flag_c[1] = 1 # 说明需要
                            # 获取这个任务的并行度
                            subTask.execution_time_c = settings.RDMT_Cloud[i, int(num_parallelism - 1)]
                            subTask.finished_time = subTask.submitTime + subTask.communication + subTask.execution_time_c
                            task.data_c['W'] = 1  # 变为缓存


                        if i == 1:  # 如果MSI在云端，需要上传
                            if task.quene[0] == 0: # 第一个也是在云端
                                subTask.submitTime = task.subTasks[0].finished_time
                            else: # 如果不在云端
                                subTask.communication = settings.w_cost_e2c[1] # 加上交互的时间
                                subTask.submitTime = task.photoTime
                                task.data_c['MSI'] = 1  # 变为缓存
                                subTask.communication_flag_c[1] = 1  # 说明需要
                            subTask.execution_time_c = settings.RDMT_Cloud[i, int(num_parallelism - 1)]
                            subTask.finished_time = subTask.submitTime + subTask.communication + subTask.execution_time_c
                            task.data_c['H'] = 1  # 变为缓存
                        if i == 2:  # 更新C  需要
                            subTask.submitTime = task.photoTime
                            subTask.execution_time_c = settings.RDMT_Cloud[i, int(num_parallelism - 1)]
                            subTask.finished_time = subTask.submitTime + subTask.communication + subTask.execution_time_c
                            task.data_c['S'] = 1  # 变为缓存
                        if i == 3:  # 是S的更新
                            if task.data_c['W'] == 0:  # 没有缓存, W在云上
                                subTask.communication += settings.w_cost_e2c[2]  # 加上交互的时间
                                task.data_c['W'] = 1  # 变为缓存
                                subTask.communication_flag_c[2] = 1  # 说明需要
                            if task.data_c['H'] == 0:  # 没有缓存, H在云上
                                subTask.communication += settings.w_cost_e2c[3]  # 加上交互的时间
                                task.data_c['H'] = 1  # 变为缓存
                                subTask.communication_flag_c[3] = 1  # 说明需要
                            if task.data_c['S'] == 0:  # 没有缓存, S在云上
                                subTask.communication += settings.w_cost_e2c[4]  # 加上交互的时间
                                task.data_c['S'] = 1  # 变为缓存
                                subTask.communication_flag_c[4] = 1  # 说明需要
                            subTask.submitTime = max(task.subTasks[0].finished_time,
                                                     task.subTasks[1].finished_time,
                                                     task.subTasks[2].finished_time)
                            subTask.finished_time = subTask.submitTime + subTask.communication + subTask.execution_time_e  # + 通讯时间和执行时间 就是结束时间
                            task.data_c['C'] = 1

                        if i == 4:  # 融合目标检测 需要WHSC
                            if task.data_c['W'] == 0:  # 没有缓存, W在云上
                                subTask.communication += settings.w_cost_e2c[2]  # 加上交互的时间
                                task.data_c['W'] = 1  # 变为缓存
                                subTask.communication_flag_c[2] = 1  # 说明需要
                            if task.data_c['H'] == 0:  # 没有缓存, H在云上
                                subTask.communication += settings.w_cost_e2c[3]  # 加上交互的时间
                                task.data_c['H'] = 1  # 变为缓存
                                subTask.communication_flag_c[3] = 1  # 说明需要
                            if task.data_c['S'] == 0:  # 没有缓存, S在云上
                                subTask.communication += settings.w_cost_e2c[4]  # 加上交互的时间
                                task.data_c['S'] = 1  # 变为缓存
                                subTask.communication_flag_c[4] = 1  # 说明需要
                            if task.data_c['C'] == 0:  # 没有缓存, C在云上
                                subTask.communication += settings.w_cost_e2c[5]  # 加上交互的时间
                                task.data_c['C'] = 1  # 变为缓存
                                subTask.communication_flag_c[5] = 1  # 说明需要
                            subTask.submitTime = task.subTasks[i - 1].finished_time
                            subTask.finished_time = subTask.submitTime + subTask.communication + subTask.execution_time_c

                    task.subTasks.append(subTask)


                # 最后根据云任务列表和边缘端的时间，所有按照时间模型
                # task_groups[i].append(task)
                task_group.taskList.append(task)
            task_groups.append(task_group)
        print("初始化结束")

        # 以上是任务预处理

        # todo 把云和边的任务排列一下
        tasks_all = []
        for i in range(len(task_groups)):
            for j in range(len(task_groups[i].taskList)):
                for k in range(settings.I):
                    subTask_temp: SubTask = task_groups[i].taskList[j].subTasks[k]
                    # if subTask_temp.bb == 0 and subTask_temp.submitTime >= submittime:
                    tasks_all.append(subTask_temp)

                            # subTask_temp.bb = 1
        # 按时间排序吧
        tasks_all.sort(key=lambda x: x.submitTime)

        # todo 把任务都分配到机子上
        edgeTasks = [[] for _ in range(settings.N)]

        cloudTasks = [[] for _ in range(settings.K)]
        id = 0
        for im in range(settings.M * settings.I):
            subTask_temp: SubTask = tasks_all.pop()
            n = subTask_temp.n  # 无人机
            if subTask_temp.pos == 1: # 在边端
                edge_task = EdgeTask()
                edge_task.subtask = subTask_temp

                if edgeTasks[n] == []: # 如果是空的那就放进去
                    edge_task.startTime = subTask_temp.submitTime
                    edge_task.finshedTime = edge_task.startTime + subTask_temp.execution_time_e + subTask_temp.communication
                    edge_task.communication_flag_e = subTask_temp.communication_flag_e

                else:
                    pre: EdgeTask = edgeTasks[n][-1] # 获取前面一个
                    # 找前序节点的finishtime
                    if subTask_temp.submitTime > pre.finshedTime:
                        if subTask_temp.i == 0 or subTask_temp.i == 1 or subTask_temp.i == 2: # 如果是WHS更新，就没必要获取前序节点了
                            edge_task.startTime = subTask_temp.submitTime
                        elif subTask_temp.i == 3:
                            edge_task.startTime = max(find_max_finshedtime_pre(cloudTasks, edgeTasks, n, [0, 1, 2]), subTask_temp.submitTime)
                        elif subTask_temp.i == 4:
                            edge_task.startTime = max(find_max_finshedtime_pre(cloudTasks, edgeTasks, n, [3]),
                                                      subTask_temp.submitTime)
                    else:
                        if subTask_temp.i == 0 or subTask_temp.i == 1 or subTask_temp.i == 2:  # 如果是WHS更新，就没必要获取前序节点了
                            edge_task.startTime = pre.finshedTime
                        elif subTask_temp.i == 3:
                            edge_task.startTime = max(find_max_finshedtime_pre(cloudTasks, edgeTasks, n, [0, 1, 2]),
                                                      pre.finshedTime)
                        elif subTask_temp.i == 4:
                            edge_task.startTime = max(find_max_finshedtime_pre(cloudTasks, edgeTasks, n, [3]),
                                                      pre.finshedTime)
                    edge_task.finshedTime = edge_task.startTime + subTask_temp.execution_time_e + subTask_temp.communication

                id = 10000000 + subTask_temp.n * (subTask_temp.rn * settings.I) + subTask_temp.rn * settings.I + subTask_temp.i
                edge_task.id = id
                edge_task.n = subTask_temp.n
                edge_task.r = subTask_temp.r
                edgeTasks[n].append(edge_task) # 加入边端

            else:
            # 在云端
                cloudTask = CloudTask()
                cloudTask.subtask = subTask_temp
                # 先找到这个任务的前面的时间 再对比提交时间

                # 找到前面空的
                if subTask_temp.i == 0 or subTask_temp.i == 1 or subTask_temp.i == 2: # 如果是WHS更新，就没必要获取前序节点了
                    cloudTask.startTime = max(find_max_finshedtime_cloud_pre(cloudTasks, edgeTasks, n, None, subTask_temp.execution_position),
                                              subTask_temp.submitTime) # 找到前序节点和vm上的最后时间
                if subTask_temp.i == 3:
                    cloudTask.startTime = max(
                        find_max_finshedtime_cloud_pre(cloudTasks, edgeTasks, n, [0, 1, 2], subTask_temp.execution_position),
                        subTask_temp.submitTime)  # 找到前序节点和vm上的最后时间

                if subTask_temp.i == 4:
                    cloudTask.startTime = max(
                        find_max_finshedtime_cloud_pre(cloudTasks, edgeTasks, n, [3],
                                                       subTask_temp.execution_position),
                        subTask_temp.submitTime)  # 找到前序节点和vm上的最后时间
                cloudTask.finshedTime = cloudTask.startTime + subTask_temp.execution_time_e + subTask_temp.communication

                for vmi in range(settings.I):
                    if subTask_temp.execution_position[vmi] == 1:
                        cloudTask_temp = copy.copy(cloudTask)
                        cloudTask_temp.n = subTask_temp.n
                        cloudTask_temp.r = subTask_temp.r
                        cloudTask_temp.id = subTask_temp.n * (subTask_temp.rn * settings.I * settings.K) + \
                                            subTask_temp.r * settings.I * settings.K + subTask_temp.i * settings.K + vmi

                        cloudTasks[vmi].append(cloudTask_temp)


        build_relationship(cloudTasks, edgeTasks)
        print()




        x1 = X[:, [0]]
        x2 = X[:, [1]]
        x3 = X[:, [2]]
        x4 = X[:, [3]]
        x5 = X[:, [4]]
        x6 = X[:, [5]]
        pop.ObjV = np.sin(2 * x1) - np.cos(x2) + 2 * x3 ** 2 - 3 * x4 + (
                    x5 - 3) ** 2 + 7 * x6  # 计算目标函数值，赋值给pop种群对象的ObjV属性
