import math


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
        return distance / s * P  # 路程除以速度乘以功耗

        # def initSubtask():
