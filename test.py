import numpy as np
x1 = 0
x2= 0
b = np.hstack([(x1 - 0.5)**2 - 0.25,
                            (x2 - 1)**2 - 1])  # 计算违反约束程度值，赋值给种群对象的CV属性