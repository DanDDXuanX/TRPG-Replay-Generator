import numpy as np

class Pos:
    # 初始化
    def __init__(self,pos=(0,0)):
        if len(pos) == 0:
            self.x = 0
            self.y = 0
        elif len(pos) == 1:
            self.x = int(pos[0])
            self.y = int(pos[0])
        else:
            self.x = int(pos[0])
            self.y = int(pos[1])
    # 重载取负号
    def __neg__(self):
        return Pos((-self.x,-self.y))
    # 重载加法
    def __add__(self,others):
        if type(others) is Pos:
            x = self.x + others.x
            y = self.y + others.y
            return Pos((x,y))
        elif type(others) in [list,tuple]:
            try:
                x = self.x + int(others[0])
                y = self.y + int(others[1])
                return Pos((x,y))
            except IndexError: # 列表数组长度不足
                raise Exception()
            except ValueError: # 列表数组不能解释为整数
                raise Exception()
        else: # 用来加的不是一个合理的类型
            raise Exception()
    # 重载减法
    def __sub__(self,others):
        return -(-self + others)
    # 重载相等判断
    def __eq__(self,others):
        if type(others) is Pos:
            return (self.x == others.x) and (self.y == others.y)
        elif type(others) in [list,tuple]:
            try:
                return (self.x == int(others[0])) and (self.y == int(others[1]))
            except IndexError: # 列表数组长度不足
                return False
            except ValueError: # 列表数组不能解释为整数
                return False
        else: # 用来判断的不是一个合理的类型
            return False
    # 设置
    def set(self,others):
        if type(others) is Pos:
            self.x = others.x
            self.y = others.y
        elif type(others) in [list,tuple]:
            try:
                self.x = int(others[0])
                self.y = int(others[1])
            except IndexError: # 列表数组长度不足
                raise Exception()
            except ValueError: # 列表数组不能解释为整数
                raise Exception()
        else: # 设置的不是一个合理的类型
            raise Exception()
    def recode(self):
        return str(self.x) + ',' + str(self.y)

class PosGrid:
    def __init__(self,x1,x2,x_step,y1,y2,y_step):
        X,Y = np.mgrid[x1:x2:x_step,y1:y2:y_step].astype(int)
        self._grid = np.frompyfunc(lambda x,y:Pos([x,y]),2,1)(X,Y)
    def __getitem__(self,key):
        return self._grid[key[0],key[1]]