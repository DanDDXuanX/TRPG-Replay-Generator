#!/usr/bin/env python
# coding: utf-8
# 立绘和气泡的动态切换效果

import numpy as np
from .Utils import concat_xy
from .Exceptions import ParserError

class MotionMethod:
    # 关键字字典
    ## 尺度关键字
    scale_dic = {
        'major' :0.3,
        'minor' :0.12,
        'entire':1.0
        }
    ## 方向关键字：up = 0 剩下的逆时针
    direction_dic = {
        'up'   :0,
        'down' :180,
        'left' :90,
        'right':270
        }
    # 屏幕分辨率的配置：
    screen_size = (1920,1080)
    # 解析关键字组，初始化对象
    def __init__(self,method_name:str,method_dur:int,formula,i=0) -> None:
        # 动画函数
        self.formula = formula
        # 小节序号
        self.section = i
        # 小节持续时间
        self.method_dur = method_dur
        # 关键字组
        method_keys = method_name.split('_')
        # 切换效果参数：默认值
        self.method_args = {
            'alpha'    :'replace', # 透明度
            'motion'   :'static',  # 动态
            'direction':0,         # 方向:'up'
            'scale'    :'major',       # 尺度:
            'cut'      :(1,1)      # 切入切出:'both'
            }
        # 解析关键字
        for key in method_keys:
            if key in ['black','cross','replace','delay']:
                self.method_args['alpha'] = key
            elif key in ['pass','leap','static','circular']:
                self.method_args['motion'] = key
            elif key.startswith('shake'):
                self.method_args['motion'] = key
            elif key in ['up','down','left','right']:
                self.method_args['direction'] = self.direction_dic[key]
            elif key in ['major','minor','entire']:
                self.method_args['scale'] = key
            elif key in ['in','out','both']:
                self.method_args['cut'] = {'in':(1,0),'out':(0,1),'both':(1,1)}[key]
            elif 'DG' == key[0:2]:
                try:
                    self.method_args['direction'] = float(key[2:])
                except Exception:
                    raise ParserError('SwitchDial',method_name,str(self.section+1))
            else:
                try:
                    self.method_args['scale'] = int(key)
                except Exception:
                    raise ParserError('SwitchDial',method_name,str(self.section+1))
    # 透明度
    def alpha(self,this_duration,media_alpha=100):
        # 切入切出
        cutin,cutout = self.method_args['cut']
        # 不同的透明度模式
        if self.method_args['alpha'] == 'replace': #--
            alpha_timeline = np.hstack(np.ones(this_duration)) # replace的延后功能撤销！
        elif self.method_args['alpha'] == 'delay': #_-
            alpha_timeline = np.hstack([np.zeros(self.method_dur),np.ones(this_duration-self.method_dur)]) # 延后功能
        elif self.method_args['alpha'] == 'cross' : # 如果切换效果无法match，black 和 cross 的效果是一样的
            alpha_timeline = np.hstack([self.dynamic(1,self.method_dur,1,1,cutin),np.ones(this_duration-2*self.method_dur),self.dynamic(1,self.method_dur,1,0,cutout)])
        else: # method_args['alpha'] == 'black' or 'cross':#>1<
            alpha_timeline = np.hstack([self.dynamic(1,self.method_dur,1,1,cutin),np.ones(this_duration-2*self.method_dur),self.dynamic(1,self.method_dur,1,0,cutout)])
        return alpha_timeline * media_alpha
    # 运动
    def motion(self,this_duration,method_dur=None):
        # 切入切出
        cutin,cutout = self.method_args['cut']
        # 指定dur？
        if method_dur is None:
            method_dur = self.method_dur
        else:
            method_dur = int(method_dur)
        # 如果运动模式是静止：
        if self.method_args['motion'] == 'static':
            return np.repeat('NA',this_duration)
        # 设定弧度
        theta = np.deg2rad(self.method_args['direction'])
        # 尺度上下绑定屏幕高度，左右绑定屏幕宽度*scale_dic[method_args['scale']]
        if self.method_args['scale'] in ['major','minor','entire']: 
            scale_value = ((np.cos(theta)*self.screen_size[1])**2+(np.sin(theta)*self.screen_size[0])**2)**(1/2)*self.scale_dic[self.method_args['scale']]
        else:
            scale_value = self.method_args['scale']
        # 运动方式
        if self.method_args['motion'] == 'pass': # >0>
            D1 = np.hstack([self.dynamic(scale_value*np.sin(theta),method_dur,0,1,cutin),
                            np.zeros(this_duration-2*method_dur),
                            self.dynamic(-scale_value*np.sin(theta),method_dur,0,0,cutout)])
            D2 = np.hstack([self.dynamic(scale_value*np.cos(theta),method_dur,0,1,cutin),
                            np.zeros(this_duration-2*method_dur),
                            self.dynamic(-scale_value*np.cos(theta),method_dur,0,0,cutout)])
        elif self.method_args['motion'] == 'leap': # >0<
            D1 = np.hstack([self.dynamic(scale_value*np.sin(theta),method_dur,0,1,cutin),
                            np.zeros(this_duration-2*method_dur),
                            self.dynamic(scale_value*np.sin(theta),method_dur,0,0,cutout)])
            D2 = np.hstack([self.dynamic(scale_value*np.cos(theta),method_dur,0,1,cutin),
                            np.zeros(this_duration-2*method_dur),
                            self.dynamic(scale_value*np.cos(theta),method_dur,0,0,cutout)])
        # 实验性质的功能，想必不可能真的有人用这么鬼畜的效果吧：这个不支持交叉溶解！
        elif self.method_args['motion'] == 'circular': 
            theta_timeline = (
                np
                .repeat(self.formula(0-theta,2*np.pi-theta,method_dur),np.ceil(this_duration/method_dur).astype(int))
                .reshape(method_dur,np.ceil(this_duration/method_dur).astype(int))
                .transpose().ravel())[0:this_duration]
            D1 = np.sin(theta_timeline)*scale_value
            D2 = -np.cos(theta_timeline)*scale_value
        # 震动
        elif self.method_args['motion'].startswith('shake'):
            circle_digit = self.method_args['motion'][5:]
            D1 = np.hstack([self.shake_eff(scale_value*np.sin(theta),method_dur,circle_digit,cutin),
                            np.zeros(this_duration-2*method_dur),
                            self.shake_eff(scale_value*np.sin(theta),method_dur,circle_digit,cutout)])
            D2 = np.hstack([self.shake_eff(scale_value*np.cos(theta),method_dur,circle_digit,cutin),
                            np.zeros(this_duration-2*method_dur),
                            self.shake_eff(scale_value*np.cos(theta),method_dur,circle_digit,cutout)])
        else:
            return np.repeat('NA',this_duration)
        pos_timeline = concat_xy(D1,D2)
        return pos_timeline
    # 震动的函数
    def shake_eff(self,scale:int,duration:int,circle:str,enable:bool):
        if circle == '':
            f = 1
        else:
            try:
                f = int(circle)/10
            except ValueError:
                f = 1
        if enable:
            X = np.linspace(0,10,duration)
            return scale * np.exp(-0.5*X) * np.sin(f * 2*np.pi*X)
        else:
            return np.zeros(duration)
    # 动态(尺度,持续事件,平衡位置,切入切出,启用)
    def dynamic(self,scale:int,duration:int,balance:int,cut:int,enable:bool)->np.ndarray:
        if enable == True:
            # cutin=1,cutout=0
            if cut == balance:
                return self.formula(0,scale,duration)
            else:
                return self.formula(scale,0,duration)
        # enable == False:
        else:
            return np.ones(duration)*scale*balance
    # 生成本小节切入和前小节切出的交叉时间轴
    def cross_mark(self,self_in:np.ndarray,last_out:np.ndarray)->np.ndarray:
        # 前半 last->self;后半self<-last
        UF_out_mark = np.frompyfunc(lambda x,y:str(x)+' -> '+str(y),2,1)
        UF_in_mark = np.frompyfunc(lambda x,y:str(x)+' <- '+str(y),2,1)
        return np.hstack([
            UF_out_mark(last_out[:self.method_dur],self_in[:self.method_dur]),
            UF_in_mark(self_in[self.method_dur:],last_out[self.method_dur:])
            ])
    def cross_alpha(self,last,self_alpha=100,last_alpha=100)->np.ndarray:
        # 本小节的切入
        self_in_timeline = self.dynamic(1,self.method_dur*2,1,1,1)*self_alpha
        # 前小节的切出
        last_out_timeline = last.dynamic(1,last.method_dur*2,1,0,1)*last_alpha
        # 生成交叉小节
        cross_timeline = self.cross_mark(self_in_timeline,last_out_timeline)
        # 返回交叉小节
        return cross_timeline
    def cross_motion(self,last)->np.ndarray:
        # 本小节的切入
        self_in_timeline = self.motion(self.method_dur*4,self.method_dur*2)[:self.method_dur*2]
        # 前小节的切出
        last_out_timeline = last.motion(last.method_dur*4,last.method_dur*2)[self.method_dur*2:]
        # 生成交叉小节
        cross_timeline = self.cross_mark(self_in_timeline,last_out_timeline)
        # 返回交叉小节
        return cross_timeline
    # 检查两个切换效果是否能匹配
    def cross_check(self,last)->bool:
        # last指前一个小节的method
        if last is None:
            # 如果前一个小节不存在，那么不能交叉
            return 0
        elif self.method_args['alpha'] != 'cross' or last.method_args['alpha'] != 'cross':
            # 如果前一个小节和本小节的切换效果不都是cross，那么不能交叉
            return False
        elif self.method_dur != last.method_dur:
            # 如果前一个小节和本小节的切换时间不匹配，那么不能交叉
            return False
        elif self.method_args['cut'][0] != 1 or last.method_args['cut'][1] != 1:
            # 如果本小节的切入或前小节的切出不都有效，那么不能交叉
            return False
        elif self.method_args['motion'] == 'circular' or last.method_args['motion'] == 'circular':
            # 如果运动方式是实验性功能，那么不能交叉
            return False
        else:
            # 如果不满足上述条件，则可以交叉
            return True
