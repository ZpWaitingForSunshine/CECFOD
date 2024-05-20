import json

class Gantt:
    def __int__(self):

    # def __init__(self, id, text, start_date, duration, parent, progress, open):
        self.id = -1
        self.text = ""
        self.start_date = 0
        self.duration = 0
        self.parent = 0
        self.progress = 0
        self.open = 0

        # {id: 17, text: "Task #2.1", start_date: "03-04-2023", duration: 2, parent: "13", progress: 1, open: true},

    # 定义一个方法，用来在序列化时返回一个字典
    def to_dict(self):
        return {key: value for key, value in self.__dict__.items()}

# # 一个包含Person类实例的列表
# people = [
#     Person("Alice", 30),
#     Person("Bob", 25),
# ]
#
# # 定义一个函数来序列化Person类的实例
# def serialize_person(obj):
#     if isinstance(obj, Person):
#         return obj.to_dict()
#     raise TypeError("Type not serializable")
#
# # 使用json.dumps()将列表转换成JSON字符串，并指定序列化函数
# json_str = json.dumps(people, default=serialize_person)
#
# print(json_str)