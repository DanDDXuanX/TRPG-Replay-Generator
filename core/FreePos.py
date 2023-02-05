#!/usr/bin/env python
# coding: utf-8

# Pos 和 FreePos的类定义，原来的所有pos，全修改为Pos类对象。
# 注意：Pos类指画布全局的Pos，因此不可以给htpos和mtpos使用！
# htpos和mtpos仍然只能使用tuple！
# Pos在GUI中标记为绿字！

import numpy as np

class Pos:
    # 初始化
    # 这种初始化模式更优雅，但是并不和GUI的逻辑兼容，重新考虑一下？
    def __init__(self,*argpos):
        if len(argpos) == 0:
            self.x = 0
            self.y = 0
        elif len(argpos) == 1:
            self.x = int(argpos[0])
            self.y = int(argpos[0])
        else:
            self.x = int(argpos[0])
            self.y = int(argpos[1])
    # 重载取负号
    def __neg__(self):
        return Pos(-self.x,-self.y)
    # 重载加法
    def __add__(self,others):
        if type(others) is Pos:
            x = self.x + others.x
            y = self.y + others.y
            return Pos(x,y)
        elif type(others) in [list,tuple,np.ndarray]:
            try:
                x = self.x + int(others[0])
                y = self.y + int(others[1])
                return Pos(x,y)
            except IndexError: # 列表数组长度不足
                raise Exception('The length of tuple to add is insufficient.')
            except ValueError: # 列表数组不能解释为整数
                raise Exception('Invalid value type to add.')
        else: # 用来加的不是一个合理的类型
            raise Exception('Unsuppoeted type to add!')
    # 重载减法
    def __sub__(self,others):
        return -(-self + others)
    # 重载相等判断
    def __eq__(self,others):
        if type(others) is Pos:
            return (self.x == others.x) and (self.y == others.y)
        elif type(others) in [list,tuple,np.ndarray]:
            try:
                return (self.x == int(others[0])) and (self.y == int(others[1]))
            except IndexError: # 列表数组长度不足
                return False
            except ValueError: # 列表数组不能解释为整数
                return False
        else: # 用来判断的不是一个合理的类型
            return False
    def __str__(self):
        return "({x},{y})".format(x=self.x,y=self.y)
    def get(self):
        return (self.x,self.y)
    def convert(self):
        pass
class FreePos(Pos):
    # 重设位置
    def set(self,others):
        if type(others) in [Pos,FreePos]:
            self.x = others.x
            self.y = others.y
        elif type(others) in [list,tuple,np.ndarray]:
            try:
                self.x = int(others[0])
                self.y = int(others[1])
            except IndexError: # 列表数组长度不足
                raise Exception('The length of tuple to set is insufficient.')
            except ValueError: # 列表数组不能解释为整数
                raise Exception('Invalid value type to set.')
        else: # 设置的不是一个合理的类型
            raise Exception('Unsuppoeted type to set!')
class PosGrid:
    def __init__(self,pos,end,x_step,y_step):
        x1,y1 = pos
        x2,y2 = end
        if (x1>=x2) | (y1>=y2):
            raise Exception('Invalid separate param end for posgrid!')
        X,Y = np.mgrid[x1:x2:(x2-x1)/x_step,y1:y2:(y2-y1)/y_step].astype(int)
        self._grid = np.frompyfunc(lambda x,y:Pos(x,y),2,1)(X,Y)
    def __getitem__(self,key)->Pos:
        return self._grid[key[0],key[1]]
    def size(self):
        return self._grid.shape
    def convert(self):
        pass