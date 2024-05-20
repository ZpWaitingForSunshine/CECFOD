class Relationship:
    # def __init__(self, id, source, target, type):
    def __init__(self):
        self.id = -1
        self.source = -1
        self.target = -1
        self.type = -1
        # {id: 1, source: 1, target: 2, type: "1"},
        # {id: 2, source: 2, target: 3, type: "0"}

    # 定义一个方法，用来在序列化时返回一个字典
    def to_dict(self):
        return {key: value for key, value in self.__dict__.items()}