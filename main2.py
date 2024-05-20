# # -*- coding: utf-8 -*-
# """main.py"""
# import numpy as np
# import geatpy as ea # import geatpy
#
# from MyProblem import MyProblem
#
# # from MyProblem import MyProblem # 导入自定义问题接口
# """===========================实例化问题对象========================"""
# problem = MyProblem() # 生成问题对象
# """=============================种群设置==========================="""
# NIND = 40 # 种群规模
# # 创建区域描述器，这里需要创建两个，前2个变量用RI编码，其余用排列编码
# Encodings = ['P', 'BG']
# Field1 = ea.crtfld(Encodings[0], problem.varTypes[:2], problem.ranges[:,:2], problem.borders[:,:2])
# Field2 = ea.crtfld(Encodings[1], problem.varTypes[2:], problem.ranges[:,2:], problem.borders[:,2:])
# Fields = [Field1, Field2]
# population = ea.PsyPopulation(Encodings, Fields, NIND) #
# # 实例化种群对象（此时种群还没被初始化，仅仅是完成种群对象的实例化）
# """===========================算法参数设置=========================="""
# myAlgorithm = ea.soea_psy_EGA_templet(problem, population) #
# # 实例化一个算法模板对象
# myAlgorithm.MAXGEN = 25 # 最大进化代数
# myAlgorithm.logTras = 50 #设置每隔多少代记录日志，若设置成0则表示不记录日志
# myAlgorithm.verbose = True # 设置是否打印输出日志信息
# myAlgorithm.drawing = 1 #
# # 设置绘图方式（0：不绘图；1：绘制结果图；2：绘制目标空间过程动画；
# # 3：绘制决策空间过程动画）
# """===========================调用算法模板进行种群进化============="""
# [BestIndi, population] = myAlgorithm.run() #
# # 执行算法模板，得到最优个体以及最后一代种群
# BestIndi.save() # 把最优个体的信息保存到文件中
# """==================================输出结果====================="""
# print('评价次数：%s' % myAlgorithm.evalsNum)
# print('时间已过 %s 秒' % myAlgorithm.passTime)
# if BestIndi.sizes != 0:
#     print('最优的目标函数值为：%s' % (BestIndi.ObjV[0][0]))
#     print('最优的控制变量值为：')
#     for i in range(BestIndi.Phen.shape[1]):
#         print(BestIndi.Phen[0, i])
# else:
#     print('没找到可行解。')

# -*- coding: utf-8 -*-
"""该案例展示了一个需要混合编码种群来进化的最大化目标的单目标优化问题.

问题的定义详见MyProblem.py。
分析：
该问题可以单纯用实整数编码'RI'来实现，但由于有一个”x3,x4,x5,x6互不相等“的约束，
因此把x3,x4,x5,x6用排列编码'P'，x1和x2采用实整数编码'RI'来求解会更好。
MyProblem是问题类，本质上是不需要管具体使用什么编码的，因此混合编码的设置在执行脚本main.py中进行而不是在此处。
"""
from MyProblem import MyProblem  # 导入自定义问题接口
import numpy as np
import geatpy as ea  # import geatpy

if __name__ == '__main__':
    # 实例化问题对象
    problem = MyProblem()


    # 快速构建算法
    algorithm = ea.soea_psy_EGA_templet(
        problem,
        ea.PsyPopulation(Encodings=['P', 'BG'],
                         NIND=1,
                         EncoIdxs=[list(range(0, problem.settings.N + problem.settings.M - 1)), list(range(problem.settings.N + problem.settings.M - 1, problem.Dim))]),
        MAXGEN=80,  # 最大进化代数
        logTras=1)  # 表示每隔多少代记录一次日志信息，0表示不记录。
    # 求解
    res = ea.optimize(algorithm,
                      verbose=True,
                      drawing=1,
                      outputMsg=True,
                      drawLog=False,
                      saveFlag=True)
    print(res)