#!/usr/bin/env python
# coding: utf-8

# Pos 和 FreePos的类定义，原来的所有pos，全修改为Pos类对象。
# 注意：Pos类指画布全局的Pos，因此不可以给htpos和mtpos使用！
# htpos和mtpos仍然只能使用tuple！
# Pos在GUI中标记为绿字！

import numpy as np
import pygame
from pygame.draw import line

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
    def preview(self, surface:pygame.Surface):
        px = self.x
        py = self.y
        # line
        line(surface, color='#00aa00',start_pos=(px-100,py),end_pos=(px+100,py),width=3)
        line(surface, color='#00aa00',start_pos=(px,py-100),end_pos=(px,py+100),width=3)
    def convert(self):
        pass
    def get_pos(self):
        pos_dict = {
            'orange': {
                'o0':{
                    'pos' : (self.x, self.y),
                }
            },
        }
        return pos_dict
    def configure(self, key: str, value, index: int = 0):
        if key == 'pos':
            self.x = int(value[0])
            self.y = int(value[1])
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
        else:
            self.pos = pos
            self.end = end
        self._size = [x_step,y_step]
        self.make_grid()
    def __getitem__(self,key)->Pos:
        return self._grid[key[0],key[1]]
    def make_grid(self):
        x_step, y_step = self._size
        x1,y1 = self.pos
        x2,y2 = self.end
        X,Y = np.mgrid[x1:x2:(x2-x1)/x_step,y1:y2:(y2-y1)/y_step].astype(int)
        self._grid = np.frompyfunc(lambda x,y:Pos(x,y),2,1)(X,Y)
    def size(self):
        return self._grid.shape
    def preview(self, surface):
        W,H = surface.get_size()
        # 起点
        line(surface, color='#aa00aa',start_pos=(self.pos[0],0),end_pos=(self.pos[0],H),width=3)
        line(surface, color='#aa00aa',start_pos=(0,self.pos[1]),end_pos=(W,self.pos[1]),width=3)
        # 终点
        line(surface, color='#aa00aa',start_pos=(self.end[0],0),end_pos=(self.end[0],H),width=3)
        line(surface, color='#aa00aa',start_pos=(0,self.end[1]),end_pos=(W,self.end[1]),width=3)
        # 网点
        for i in range(self._size[0]):
            for j in range(self._size[1]):
                pos_this = self._grid[i][j]
                px = pos_this.x
                py = pos_this.y
                line(surface, color='#00aa00',start_pos=(px-20,py),end_pos=(px+20,py),width=3)
                line(surface, color='#00aa00',start_pos=(px,py-20),end_pos=(px,py+20),width=3)
    def convert(self):
        pass
    def get_pos(self):
        pos_dict = {
            'orange': {
                'o0':{
                    'pos' : self.pos,
                },
                'o1':{
                    'end' : self.end,
                }
            },
        }
        return pos_dict
    def configure(self, key: str, value, index: int = 0):
        if key == 'pos':
            self.pos = value
        elif key == 'end':
            self.end = value
        elif key == 'x_step':
            self._size[0] = value
        elif key == 'y_step':
            self._size[1] = value
        self.make_grid()