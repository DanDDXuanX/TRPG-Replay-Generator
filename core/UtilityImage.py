#!/usr/bin/env python
# coding: utf-8

from PIL import Image
from .FilePaths import Filepath
import zipfile
import pygame

# 通用图像读取器

class UtilityImage:
    def __init__(self,file_path:str) -> None:
        self.filepath = Filepath(file_path)
    def check_format(self,filepath:Filepath)->str:
        self.format = filepath.type()
    # 支持的格式：正常、apng、gif、zip
    def apng_gif_to_images(self, filepath)->list:
        apng_image = Image.open(filepath)
        frames = []
        try:
            while True:
                frames.append(apng_image.copy())
                apng_image.seek(len(frames))  # Move to the next frame
        except EOFError:
            pass
        return frames
    def zip_to_image(self, filepath)->list:
        frames = []
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            # 从压缩文件中获取文件列表
            file_list = zip_ref.namelist()
            file_list.sort()
            # 遍历列表中的文件
            for file_name in file_list:
                image_this = Image.open(file_name)
                frames.append(image_this)
    # PIL -> pygame
    def image_to_surface(self, image:Image.Image)->pygame.Surface:
        image_data = image.tobytes()
        surface = pygame.image.fromstring(string=image_data, size=image.size, format=image.mode)
        return surface