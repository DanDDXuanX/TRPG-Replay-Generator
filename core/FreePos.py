#!/usr/bin/env python
# coding: utf-8

# Pos 和 FreePos的类定义，原来的所有pos，全修改为Pos类对象。
# 注意：Pos类指画布全局的Pos，因此不可以给htpos和mtpos使用！
# htpos和mtpos仍然只能使用tuple！
# Pos在GUI中标记为绿字！

import numpy as np
import pygame
from pygame.draw import line,circle
from .Formulas import formula_available

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
        self.pos = self
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
    def use(self,duration=0):
        if duration <= 0:
            return str(self)
        else:
            return np.repeat(str(self),int(duration))
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
        elif type(others) == BezierCurve: # 如果将一个自由位置设置为贝塞尔曲线，那么只会在起点生效
            self.set(others.pos)
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
class BezierCurve:
    pygame.font.init()
    def __init__(self, pos, control_left:list, control_right:list, anchor:list, frame_point:list, speed_formula:list):
        self.pos = pos
        self.control_left = control_left
        self.control_right = control_right
        self.anchor = anchor
        self.frame_point = frame_point
        self.speed_formula = speed_formula
        # 标记字体
        self.markertext = pygame.font.Font('./assets/SourceHanSansCN-Regular.otf',30)
        # 执行初始化
        self.make_curve()
    def make_curve(self):
        self.curve_set = {}
        if type(self.pos) in [Pos, FreePos]:
            self.pos = self.pos
        elif type(self.pos) == BezierCurve:
            raise Exception('Recursive calling!')
        else:
            self.pos = Pos(*self.pos)
        # 创建曲线组合时间点组
        for i in range(len(self.anchor)):
            if i == 0:
                start_point = self.pos.get()
            else:
                start_point = self.anchor[i-1]
            try:
                # 两个控制点的位置是相对位置
                raw_pos = [start_point, self.control_left[i], self.control_right[i], self.anchor[i]]
                relative_pos = raw_pos.copy()
                for idx, dot in enumerate(raw_pos):
                    if type(dot) in [Pos, FreePos]:
                        relative_pos[idx] = dot.get()
                    elif type(dot) == BezierCurve:
                        raise Exception('Recursive calling!')
                relative_pos = np.array(relative_pos)
                # 计算为绝对位置
                absolute_pos = relative_pos.copy()
                absolute_pos[1,:] = relative_pos[0,:] + relative_pos[1,:]
                absolute_pos[2,:] = relative_pos[3,:] + relative_pos[2,:]
                self.curve_set[i] = {
                    'control_points' : absolute_pos,
                    'frame_timestamp': self.frame_point[i],
                    'time_formula' : formula_available[self.speed_formula[i]],
                }
            except IndexError:
                absolute_pos = np.array([start_point, start_point, self.anchor[i], self.anchor[i]])
                self.curve_set[i] = {
                    'control_points' : absolute_pos,
                    'frame_timestamp': self.frame_point[-1],
                    'time_formula' : formula_available[self.speed_formula[-1]],
                }
        # 创建曲线
        self.all_dots = np.array(self.pos)
        for key in self.curve_set:
            # 曲线段的持续时间
            if key == 0:
                length = self.curve_set[key]['frame_timestamp']
            else:
                length = self.curve_set[key]['frame_timestamp'] - self.curve_set[key-1]['frame_timestamp']
            # 曲线段的速度曲线
            control_points:np.ndarray = self.curve_set[key]['control_points']
            formula:function = self.curve_set[key]['time_formula']
            frametime = formula(0,1,length+1)[1:]
            UF_evaluate = np.frompyfunc(lambda t: self.evaluate(control_point=control_points,t=t),1,1)
            self.curve_set[key]['dots'] = UF_evaluate(frametime)
            self.all_dots = np.hstack([self.all_dots, self.curve_set[key]['dots']])
        # 最后
        self.max_idx = len(self.all_dots)-1
    def evaluate(self, control_point:np.ndarray, t:float)->Pos:
        if t < 0:
            t = 0
        elif t > 1:
            t = 1
        else:
            t = np.float64(t)
        bernstein_coefficients = np.array([
            (1 - t)**3,
            3 * t * (1 - t)**2,
            3 * t**2 * (1 - t),
            t**3
        ])
        # Evaluate the Bezier curve at the given parameter.
        point = Pos(*np.dot(bernstein_coefficients, control_point))
        return point
    def get(self):
        return self.pos.get()
    def __getitem__(self,idx:int)->Pos:
        if idx > self.max_idx:
            return self.all_dots[self.max_idx]
        elif idx < 0:
            return self.all_dots[0]
        else:
            return self.all_dots[int(idx)]
    # 使用
    def use(self,duration=0):
        use_UF = np.frompyfunc(lambda x:x.use(),1,1)
        if duration <= 0:
            return self.pos.use()
        else:
            total_length = len(self.all_dots)
            if duration <= total_length:
                return use_UF(self.all_dots[0:duration])
            else:
                return use_UF(np.hstack([self.all_dots,np.repeat(self.all_dots[-1],duration-total_length)]))
    # 当预览时
    def preview(self, surface):
        def plot_anchor(pos:Pos,keyframe=0):
            if type(pos) in [Pos,FreePos]:
                px,py = pos.get()
            else:
                px,py = pos
            line(surface, color='#00aa00',start_pos=(px-50,py),end_pos=(px+50,py),width=3)
            line(surface, color='#00aa00',start_pos=(px,py-50),end_pos=(px,py+50),width=3)
            surface.blit(self.markertext.render(str(keyframe),True,'#00aa00'), (px+10,py-50))
        # 锚点（额外的十字叉）
        plot_anchor(self.pos, 0)
        for idx in self.curve_set:
            this_kf = self.curve_set[idx]['frame_timestamp']
            dot = self.curve_set[idx]['control_points'][3,:]
            plot_anchor(dot, this_kf)
        # 曲线点（小圆点）
        for idx, dot in enumerate(self.all_dots):
            if idx != 0:
                line(surface, color='#00aa00',start_pos=self.all_dots[idx-1].get(),end_pos=dot.get(),width=2)
            circle(surface,color='#00aa00',center=dot.get(),radius=4)
    def convert(self):
        pass
    # 在IPW中的点
    def get_pos(self):
        pos_dict = {
            'anchor':{
                'a0':{
                    'pos' : self.pos.get(),
                },
            },
            'control': {}
        }
        for idx in self.curve_set:
            pos_dict['anchor'][f'a{idx+1}'] = {'pos': self.curve_set[idx]['control_points'][3,:]}
            pos_dict['control'][f'cl{idx+1}'] = {
                'anchor'  : self.curve_set[idx]['control_points'][0,:],
                'control' : self.curve_set[idx]['control_points'][1,:],
            }
            pos_dict['control'][f'cr{idx+1}'] = {
                'anchor'  : self.curve_set[idx]['control_points'][3,:],
                'control' : self.curve_set[idx]['control_points'][2,:],
            }
        return pos_dict
    def configure(self, key: str, value, index: int = 0):
        try:
            self.__setattr__(key,value)
        except AttributeError:
            pass
        # 执行初始化
        self.make_curve()