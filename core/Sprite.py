#!/usr/bin/env python
# coding: utf-8

# 精灵立绘

from .Medias import Animation, Audio

import pygame
import numpy as np

class Sprite(Animation):
    def __init__(
        self, 
        filepath: str, 
        eyepath:str = None,
        mouthpath:str = None,
        scale: float = 1, 
        pos: tuple = ..., 
        tick: int = 1, 
        blink_mean: float=4.0,
        blink_std: float=1.0,
        label_color: str = 'Lavender'
    ) -> None:
        # 脸层
        super().__init__(filepath, scale, pos, tick, loop=True, label_color=label_color)
        self.eye = Animation(eyepath, scale, pos, tick=1, loop=True, label_color=label_color)
        self.mouth = Animation(mouthpath, scale, pos, tick=1, loop=True, label_color=label_color)
        # 眨眼参数
        self.blink_mean = blink_mean
        self.blink_std = blink_std
    def display(self, surface: pygame.Surface, alpha: float = 100, center: str = 'NA', adjust: str = 'NA', frame: int = 0, bright: float = 100) -> None:
        # 从
        t_m = frame % self.mouth.length
        t_e = (frame//self.mouth.length)%self.eye.length
        t_f = frame//(self.mouth.length*self.eye.length)
        # face层
        super().display(surface, alpha, center, adjust, t_f, bright)
        # eye层
        self.eye.display(surface, alpha, center, adjust, t_e, bright)
        # mouth层
        self.mouth.display(surface, alpha, center, adjust, t_m, bright)
    def export(self, begin: int, end: int, center: str = 'NA') -> str:
        return super().export(begin, end, center)
    def get_tick(self, duration: int, audio:Audio, delay:int, framerate:int) -> np.ndarray:
        # Sprite tick 计算方法
        # tick = t_f * L(e) * L(m) + t_e * L(m) + t_m
        # 口型参数
        ## 获取音频的响度序列
        mouse_samplerate = framerate//self.tick
        audio_dB = audio.dBFS(mouse_samplerate)
        if self.tick!=1:
            audio_dB = audio_dB.repeat(self.tick)
        ## 创建分位数梯度
        mouth_step = []
        for step in np.linspace(0.1,0.95,self.mouth.length):
            mouth_step.append(np.quantile(audio_dB,step))
        def gradient(x):
            for i,step in enumerate(mouth_step):
                if x<step:
                    return i
            else:
                return i
        ## 计算分位数梯度
        if delay + len(audio_dB) > duration:
            mouse_ticks = (
                np.hstack([
                    np.zeros(delay),
                    np.frompyfunc(gradient,1,1)(audio_dB)
                ])[0:duration]
            )
        else:
            mouse_ticks = np.zeros(duration)
            mouse_ticks[delay:delay+len(audio_dB)] = np.frompyfunc(gradient,1,1)(audio_dB)
        mouse_ticks = mouse_ticks.astype(int)
        # 眨眼参数
        eye_ticks = np.zeros(duration)
        eye_loop = np.hstack([
            np.arange(1,self.eye.length,1),
            np.arange(self.eye.length-2,0,-1)
        ])
        loop_length = len(eye_loop)
        this = 0
        while this < duration:
            gap = int(np.random.normal(self.blink_mean*framerate,scale=self.blink_std*framerate))
            if gap < loop_length:
                gap = loop_length
            if gap+this >= duration:
                break
            eye_ticks[this+gap-loop_length:this+gap] += eye_loop
            this += gap
        eye_ticks = eye_ticks.astype(int)
        # 外轮廓动画参数
        face_ticks = super().get_tick(duration=duration)
        # flag
        flag_ticks = face_ticks*self.eye.length*self.mouth.length + eye_ticks*self.mouth.length + mouse_ticks
        return flag_ticks
    def convert(self):
        super().convert()
        self.eye.convert()
        self.mouth.convert()
    def get_pos(self) -> dict:
        return super().get_pos()
    def configure(self, key: str, value, index: int = 0):
        # TODO: Sprite类的特殊config方法
        super().configure(key, value, index)
        if key == 'eyepath':
            self.eye.configure(key='filepath',value=value)
        elif key == 'mouthpath':
            self.mouth.configure(key='filepath',value=value)
        elif key == 'scale':
            # 如果是scale，self的尺寸在super已经更新，eye和mouth的尺寸需要额外更新
            self.eye.configure(key='scale',value=value)
            self.mouth.configure(key='scale',value=value)
