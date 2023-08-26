#!/usr/bin/env python
# coding: utf-8

from PIL import Image
from .FilePaths import Filepath
import pygame

# 通用图像读取器

class UtilityImage:
    def __init__(self,file_path:Filepath) -> None:
        if type(file_path) is not Filepath:
            self.filepath = Filepath(file_path)
        else:
            self.filepath = file_path
    def check_format(self,filepath:Filepath)->str:
        self.format = filepath.type()
        return self.format
    def load_file(self)->list:
        suffix = self.check_format(self.filepath)
        if suffix in ['gif','apng']:
            frames = self.apng_gif_to_images(filepath=self.filepath)
        else:
            frames = [Image.open(self.filepath.exact())]
        # 转为surface
        return [self.image_to_surface(f) for f in frames]
    # 支持的格式：正常、apng、gif、zip
    def apng_gif_to_images(self, filepath:Filepath)->list:
        filepath_ = filepath.exact()
        apng_image = Image.open(filepath_)
        frames = []
        try:
            while True:
                if apng_image.mode != 'RGBA':
                    frames.append(apng_image.convert('RGBA'))
                else:
                    frames.append(apng_image.copy())
                apng_image.seek(len(frames))  # Move to the next frame
        except EOFError:
            pass
        return frames
    # PIL -> pygame
    def image_to_surface(self, image:Image.Image)->pygame.Surface:
        image_data = image.tobytes()
        surface = pygame.image.fromstring(image_data, image.size, image.mode)
        return surface
