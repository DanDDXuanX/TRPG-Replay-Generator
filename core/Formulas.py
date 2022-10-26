#!/usr/bin/env python
# coding: utf-8
# 数学函数定义 formula

import numpy as np

def normalized(X):
    if len(X)>=2:
        return (X-X.min())/(X.max()-X.min())
    else:
        return X/X # 兼容 持续时间被设置为0，1等极限情况

def linear(begin,end,dur):
    return np.linspace(begin,end,int(dur))

def quadratic(begin,end,dur):
    return (np.linspace(0,1,int(dur))**2)*(end-begin)+begin

def quadraticR(begin,end,dur):
    return (1-np.linspace(1,0,int(dur))**2)*(end-begin)+begin

def sigmoid(begin,end,dur,K=5):
    return normalized(1/(1+np.exp(np.linspace(K,-K,int(dur)))))*(end-begin)+begin

def right(begin,end,dur,K=4):
    return normalized(1/(1+np.exp((quadratic(K,-K,int(dur))))))*(end-begin)+begin

def left(begin,end,dur,K=4):
    return normalized(1/(1+np.exp((quadraticR(K,-K,int(dur))))))*(end-begin)+begin

def sincurve(begin,end,dur):# alpha 1.8.4
    return normalized(np.sin(np.linspace(-np.pi/2,np.pi/2,dur)))*(end-begin)+begin

formula_available={'linear':linear,'quadratic':quadratic,'quadraticR':quadraticR,
                   'sigmoid':sigmoid,'right':right,'left':left,'sincurve':sincurve}