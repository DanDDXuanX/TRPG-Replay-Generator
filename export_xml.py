#!/usr/bin/env python
# coding: utf-8
edtion = 'alpha 1.8.9'

# 外部参数输入

import argparse
import sys
import os

ap = argparse.ArgumentParser(description="Export Premiere Pro XML from timeline file.")
ap.add_argument("-l", "--TimeLine", help='Timeline (and break_point with same name), which was generated by replay_generator.py.',type=str)
ap.add_argument("-d", "--MediaObjDefine", help='Definition of the media elements, using real python code.',type=str)
ap.add_argument("-t", "--CharacterTable", help='This program do not need CharacterTable.',type=str)
ap.add_argument("-o", "--OutputPath", help='Choose the destination directory to save the project timeline and break_point file.',type=str,default=None)
# 增加一个，读取时间轴和断点文件的选项！
ap.add_argument("-F", "--FramePerSecond", help='Set the FPS of display, default is 30 fps, larger than this may cause lag.',type=int,default=30)
ap.add_argument("-W", "--Width", help='Set the resolution of display, default is 1920, larger than this may cause lag.',type=int,default=1920)
ap.add_argument("-H", "--Height", help='Set the resolution of display, default is 1080, larger than this may cause lag.',type=int,default=1080)
ap.add_argument("-Z", "--Zorder", help='Set the display order of layers, not recommended to change the values unless necessary!',type=str,
                default='BG3,BG2,BG1,Am3,Am2,Am1,Bb')
args = ap.parse_args()

media_obj = args.MediaObjDefine #媒体对象定义文件的路径
char_tab = args.CharacterTable #角色和媒体对象的对应关系文件的路径
stdin_log = args.TimeLine #log路径
output_path = args.OutputPath #保存的时间轴，断点文件的目录

screen_size = (args.Width,args.Height) #显示的分辨率
frame_rate = args.FramePerSecond #帧率 单位fps
zorder = args.Zorder.split(',') #渲染图层顺序

try:
    for path in [stdin_log,media_obj]:
        if path == None:
            raise OSError("[31m[ArgumentError]:[0m Missing principal input argument!")
        if os.path.isfile(path) == False:
            raise OSError("[31m[ArgumentError]:[0m Cannot find file "+path)

    if output_path == None:
        pass 
    elif os.path.isdir(output_path) == False:
        try:
            os.makedirs(output_path)
        except Exception:
            raise OSError("[31m[SystemError]:[0m Cannot make directory "+output_path)
    output_path = output_path.replace('\\','/')

    # FPS
    if frame_rate <= 0:
        raise ValueError("[31m[ArgumentError]:[0m "+str(frame_rate))
    elif frame_rate>30:
        print("[33m[warning]:[0m",'FPS is set to '+str(frame_rate)+', which may cause lag in the display!')

    if (screen_size[0]<=0) | (screen_size[1]<=0):
        raise ValueError("[31m[ArgumentError]:[0m "+str(screen_size))
    if screen_size[0]*screen_size[1] > 3e6:
        print("[33m[warning]:[0m",'Resolution is set to more than 3M, which may cause lag in the display!')
except Exception as E:
    print(E)
    sys.exit(1)

# 包导入

import pandas as pd
import numpy as np
from PIL import Image,ImageFont,ImageDraw
import re
import time #开发模式，显示渲染帧率
from pygame import mixer
import glob # 匹配路径

# 文字对象

outtext_index = 0
outanime_index = 0 
clip_index = 0
file_index = 0

class Text:
    def __init__(self,fontfile='./media/SourceHanSansCN-Regular.otf',fontsize=40,color=(0,0,0,255),line_limit=20):
        self.color=color
        self.size=fontsize
        self.line_limit = line_limit
        self.fontpath = fontfile
    def render(self,tx):
        font_this = ImageFont.truetype(self.fontpath, self.size)
        text_this = Image.new(mode='RGBA',size=(self.size*int(len(tx)*1.5),self.size*2),color=(0,0,0,0)) # 画布贪婪为2x高度，1.5*宽度
        draw_this = ImageDraw.Draw(text_this)
        draw_this.text((0,0),tx,font = font_this,align ="left",fill = self.color)
        return text_this
    def draw(self,text):
        out_text = []
        if ('#' in text) | (text[0]=='^'): #如果有手动指定的换行符
            if text[0]=='^': # 如果使用^指定的手动换行，则先去掉这个字符。
                text = text[1:]
            text_line = text.split('#')
            for tx in text_line:
                out_text.append(self.render(tx))
        elif len(text) > self.line_limit: #如果既没有主动指定，字符长度也超限
            for i in range(0,len(text)//self.line_limit+1):
                out_text.append(self.render(text[i*self.line_limit:(i+1)*self.line_limit]))
        else:
            out_text = [self.render(text)]
        return out_text
    def convert(self):
        pass

class StrokeText(Text):
    def __init__(self,fontfile='./media/SourceHanSansCN-Regular.otf',fontsize=40,color=(0,0,0,255),line_limit=20,edge_color=(255,255,255,255)):
        super().__init__(fontfile=fontfile,fontsize=fontsize,color=color,line_limit=line_limit) # 继承
        self.edge_color=edge_color
    def render(self,tx):
        font_this = ImageFont.truetype(self.fontpath, self.size)
        text_this = Image.new(mode='RGBA',size=(self.size*int(len(tx)*1.5),self.size*2),color=(0,0,0,0)) # 画布贪婪为2x高度，1.5*宽度
        draw_this = ImageDraw.Draw(text_this)
        for pos in [(0,0),(0,1),(0,2),(1,0),(1,2),(2,0),(2,1),(2,2)]:
            draw_this.text(pos,tx,font = font_this,align ="left",fill = self.edge_color)
        draw_this.text((1,1),tx,font = font_this,align ="left",fill = self.color)
        return text_this

    # 对话框、气泡、文本框
class Bubble:
    def __init__(self,filepath,Main_Text=Text(),Header_Text=None,pos=(0,0),mt_pos=(0,0),ht_pos=(0,0),align='left',line_distance=1.5):
        global file_index
        self.path = reformat_path(filepath)
        self.MainText = Main_Text
        self.mt_pos = mt_pos
        self.Header = Header_Text
        self.ht_pos = ht_pos
        self.pos = pos
        self.line_distance = line_distance
        self.size = Image.open(filepath).size
        self.filename = self.path.split('/')[-1]
        self.fileindex = 'BBfile_' + '%d'% file_index
        self.PRpos = PR_center_arg(np.array(self.size),np.array(self.pos))
        self.align = align
        file_index = file_index+1
    def display(self,begin,end,text,header=''): # 这段代码是完全没有可读性的屎，但是确实可运行，非必要不要改
        global outtext_index,clip_tplt,clip_index
        # 生成文本图片
        ofile = output_path+'/auto_TX_%d'%outtext_index+'.png'
        canvas = Image.new(mode='RGBA',size=self.size,color=(0,0,0,0))
        if (self.Header!=None) & (header!=''):    # Header 有定义，且输入文本不为空
            ht_text = self.Header.draw(header)[0]
            try:
                p1,p2,p3,p4 = ht_text.getbbox() # 如果是空图的话，getbbox返回None，会发生TypeError
                canvas.paste(ht_text.crop((p1,p2,p3,p4)),(self.ht_pos[0]+p1,self.ht_pos[1]+p2)) # 兼容微软雅黑这种，bbox到处飘的字体
            except TypeError:
                pass
        x,y = self.mt_pos
        for i,mt_text in enumerate(self.MainText.draw(text)):
            try:
                p1,p2,p3,p4 = mt_text.getbbox() # 先按照bboxcrop，然后按照原位置放置
            except TypeError: # 如果遇到了空图导致的TypeError，直接跳过这一循环，走到下一行
                continue
            if self.align == 'left':
                canvas.paste(mt_text.crop((p1,p2,p3,p4)),(x+p1,int(y+i*self.MainText.size*self.line_distance+p2)))
            else: # alpha 1.7.0 兼容居中
                word_w = p3 - p1
                canvas.paste(mt_text.crop((p1,p2,p3,p4)),
                             (x + p1 + (self.MainText.size*self.MainText.line_limit - word_w)//2,
                              int(y+i*self.MainText.size*self.line_distance+p2)
                             )
                            )
        canvas.save(ofile)
        
        # 生成序列
        width,height = self.size
        pr_horiz,pr_vert = self.PRpos
        clip_bubble = clip_tplt.format(**{'clipid':'BB_clip_%d'%clip_index,
                              'clipname':'BB_clip_%d'%clip_index,
                              'timebase':'%d'%frame_rate,
                              'ntsc':Is_NTSC,
                              'start':'%d'%begin,
                              'end':'%d'%end,
                              'in':'%d'%90000,
                              'out':'%d'%(90000+end-begin),
                              'fileid':self.fileindex,
                              'filename':self.filename,
                              'filepath':self.path,
                              'filewidth':'%d'%width,
                              'fileheight':'%d'%height,
                              'horiz':'%.5f'%pr_horiz,
                              'vert':'%.5f'%pr_vert})
        clip_text = clip_tplt.format(**{'clipid':'TX_clip_%d'%clip_index,
                              'clipname':'TX_clip_%d'%clip_index,
                              'timebase':'%d'%frame_rate,
                              'ntsc':Is_NTSC,
                              'start':'%d'%begin,
                              'end':'%d'%end,
                              'in':'%d'%90000,
                              'out':'%d'%(90000+end-begin),
                              'fileid':'auto_TX_%d'%outtext_index,
                              'filename':'auto_TX_%d.png'%outtext_index,
                              'filepath':reformat_path(ofile),
                              'filewidth':'%d'%width,
                              'fileheight':'%d'%height,
                              'horiz':'%.5f'%pr_horiz,
                              'vert':'%.5f'%pr_vert})

        outtext_index = outtext_index + 1
        clip_index = clip_index+1
        return (clip_bubble,clip_text)

    def convert(self):
        pass

# 背景图片
class Background:
    def __init__(self,filepath,pos = (0,0)):
        global file_index 
        if filepath in cmap.keys(): #对纯色定义的背景的支持
            ofile = output_path+'/auto_BG_'+filepath+'.png'
            Image.new(mode='RGBA',size=screen_size,color=cmap[filepath]).save(ofile)
            self.path = reformat_path(ofile)
            self.size = screen_size
        else:
            self.path = reformat_path(filepath)
            self.size = Image.open(filepath).size
        self.pos = pos
        self.PRpos = PR_center_arg(np.array(self.size),np.array(self.pos))
        self.filename = self.path.split('/')[-1]
        self.fileindex = 'BGfile_%d'% file_index
        file_index = file_index+1
    def display(self,begin,end):
        global clip_tplt,clip_index
        width,height = self.size
        pr_horiz,pr_vert = self.PRpos
        clip_this = clip_tplt.format(**{'clipid':'BG_clip_%d'%clip_index,
                              'clipname':'BG_clip_%d'%clip_index,
                              'timebase':'%d'%frame_rate,
                              'ntsc':Is_NTSC,
                              'start':'%d'%begin,
                              'end':'%d'%end,
                              'in':'%d'%90000,
                              'out':'%d'%(90000+end-begin),
                              'fileid':self.fileindex,
                              'filename':self.filename,
                              'filepath':self.path,
                              'filewidth':'%d'%width,
                              'fileheight':'%d'%height,
                              'horiz':'%.5f'%pr_horiz,
                              'vert':'%.5f'%pr_vert})
        clip_index = clip_index+1
        return clip_this
    def convert(self):
        pass

# 立绘图片
class Animation:
    def __init__(self,filepath,pos = (0,0),tick=1,loop=True):
        global file_index 
        self.path = reformat_path(glob.glob(filepath)[0]) # 兼容动画Animation，只使用第一帧！
        self.pos = pos
        self.size = Image.open(glob.glob(filepath)[0].replace('\\','/')).size # 兼容动画
        self.filename = self.path.split('/')[-1]
        self.fileindex = 'AMfile_%d'% file_index
        self.PRpos = PR_center_arg(np.array(self.size),np.array(self.pos))
        file_index = file_index+1
    def display(self,begin,end):
        global clip_tplt,clip_index
        width,height = self.size
        pr_horiz,pr_vert = self.PRpos
        clip_this = clip_tplt.format(**{'clipid':'AM_clip_%d'%clip_index,
                              'clipname':'AM_clip_%d'%clip_index,
                              'timebase':'%d'%frame_rate,
                              'ntsc':Is_NTSC,
                              'start':'%d'%begin,
                              'end':'%d'%end,
                              'in':'%d'%90000,
                              'out':'%d'%(90000+end-begin),
                              'fileid':self.fileindex,
                              'filename':self.filename,
                              'filepath':self.path,
                              'filewidth':'%d'%width,
                              'fileheight':'%d'%height,
                              'horiz':'%.5f'%pr_horiz,
                              'vert':'%.5f'%pr_vert})
        clip_index = clip_index+1
        return clip_this
    def convert(self):
        pass

# a1.6.5 内建动画，这是一个Animation类的子类，重构了构造函数
class BuiltInAnimation(Animation):
    def __init__(self,anime_type='hitpoint',anime_args=('0',0,0,0),screensize = (1920,1080),layer=0):
        global file_index,outanime_index
        if anime_type == 'hitpoint':
            # 载入图片
            heart = Image.open('./media/heart.png')
            heart_shape = Image.open('./media/heart_shape.png')
            hx,hy = heart.size
            # 重设图片尺寸，根据screensize[0]
            if screensize[0]!=1920:
                multip = screensize[0]/1920
                heart = heart.resize((int(hx*multip),int(hy*multip)))
                heart_shape = heart_shape.resize((int(hx*multip),int(hy*multip)))
                hx,hy = heart.size
            # 动画参数
            name_tx,heart_max,heart_begin,heart_end = anime_args
            if (heart_end==heart_begin)|(heart_max<max(heart_begin,heart_end)):
                raise MediaError('[BIAnimeError]:','Invalid argument',name_tx,heart_max,heart_begin,heart_end,'for BIAnime hitpoint!')
            elif heart_end > heart_begin: # 如果是生命恢复
                temp = heart_end
                heart_end = heart_begin
                heart_begin = temp # 则互换顺序 确保 begin一定是小于end的

            distance = int(0.026*screensize[0]) # default = 50

            total_heart = int(heart_max/2 * hx + max(0,np.ceil(heart_max/2-1)) * distance) #画布总长
            left_heart = int(heart_end/2 * hx + max(0,np.ceil(heart_end/2-1)) * distance) #画布总长
            lost_heart = int((heart_begin-heart_end)/2 * hx + np.floor((heart_begin-heart_end)/2) * distance)
            # 姓名文本
            BIA_text = ImageFont.truetype('./media/SourceHanSerifSC-Heavy.otf', int(0.0521*screensize[0])) # 1080p:size=100
            test_canvas = Image.new(mode='RGBA',size=screensize,color=(0,0,0,0))
            test_draw = ImageDraw.Draw(test_canvas)
            test_draw.text((0,0), name_tx, font = BIA_text, align ="left",fill = (255,255,255,255))
            try:
                p1,p2,p3,p4 = test_canvas.getbbox()
            except TypeError:
                p1,p2,p3,p4 = (0,0,1,int(0.0521*screensize[0])) # nx=1 ny =fontsize
            nx = p3 - p1
            ny = p4 - p2
            nametx_surf = test_canvas.crop((p1,p2,p3,p4))
            # 开始制图
            if layer==0: # 底层 阴影图
                self.pos = ((screensize[0]-max(nx,total_heart))/2,(4/5*screensize[1]-hy-ny)/2)
                canvas = Image.new(size=(max(nx,total_heart),hy+ny+screensize[1]//5),mode='RGBA',color=(0,0,0,0))
                self.size = canvas.size
                if nx > total_heart:
                    canvas.paste(nametx_surf,(0,0))
                    posx = (nx-total_heart)//2
                else:
                    canvas.paste(nametx_surf,((total_heart-nx)//2,0))
                    posx = 0
                posy = ny+screensize[1]//5
                for i in range(1,heart_max+1): # 偶数，低于最终血量
                    if i%2 == 0:
                        canvas.paste(heart_shape,(posx,posy))
                        posx = posx + hx + distance
                    else:
                        pass
                if heart_max%2 == 1: # max是奇数
                    left_heart_shape = heart_shape.crop((0,0,int(hx/2),hy))
                    canvas.paste(left_heart_shape,(total_heart-int(hx/2),posy))
            elif layer==1: # 剩余的血量
                self.pos = ((screensize[0]-total_heart)/2,3/5*screensize[1]+ny/2-hy/2)
                # 1.6.5 防止报错 剩余血量即使是空图，也要至少宽30pix
                canvas = Image.new(size=(max(30,left_heart),hy),mode='RGBA',color=(0,0,0,0)) 
                self.size = canvas.size
                posx,posy = 0,0
                for i in range(1,heart_end+1): # 偶数，低于最终血量
                    if i%2 == 0:
                        canvas.paste(heart,(posx,posy))
                        posx = posx + hx + distance
                    else:
                        pass
                if heart_end%2 == 1: # end是奇数
                    left_heart = heart.crop((0,0,int(hx/2),hy))
                    canvas.paste(left_heart,(heart_end//2*(hx + distance),0))
            elif layer==2: # 损失/恢复的血量
                self.pos = (heart_end//2*(hx + distance)+(heart_end%2)*int(hx/2)+(screensize[0]-total_heart)/2,3/5*screensize[1]+ny/2-hy/2)
                canvas = Image.new(size=(lost_heart,hy),mode='RGBA',color=(0,0,0,0))
                self.size = canvas.size
                posx,posy = 0,0
                for i in range(1,heart_begin-heart_end+1): 
                    if (i == 1)&(heart_end%2 == 1): # 如果end是奇数，先来半个右边
                        right_heart = heart.crop((int(hx/2),0,hx,hy))
                        canvas.paste(right_heart,(posx,posy))
                        posx = posx + int(hx/2) + distance
                    elif ((i - heart_end%2)%2 == 0): # 如果和end的差值是
                        canvas.paste(heart,(posx,posy))
                        posx = posx + hx + distance
                    elif (i == heart_begin-heart_end)&(heart_begin%2 == 1): # 如果最右边边也是半个心
                        left_heart = heart.crop((0,0,int(hx/2),hy))
                        canvas.paste(left_heart,(posx,posy))
                    else:
                        pass
            else:
                pass
            ofile = output_path+'/auto_BIA_%d'%outanime_index+'.png'
            canvas.save(ofile)

            #剩下的需要定义的
            self.path = reformat_path(ofile) # 兼容动画Animation，只使用第一帧！
            self.filename = 'auto_BIA_%d'%outanime_index+'.png'
            self.fileindex = 'AMfile_%d'% file_index
            #print(np.array(self.size),np.array(self.pos))
            self.PRpos = PR_center_arg(np.array(self.size),np.array(self.pos))
            outanime_index = outanime_index+1
            file_index = file_index+1
        if anime_type == 'dice':
            for die in anime_args:
                try:
                    # 转换为int类型，NA转换为-1
                    name_tx,dice_max,dice_check,dice_face = die
                    dice_max,dice_face,dice_check = map(lambda x:-1 if x=='NA' else int(x),(dice_max,dice_face,dice_check))
                except ValueError as E: #too many values to unpack,not enough values to unpack
                    raise MediaError('[BIAnimeError]:','Invalid syntax:',str(die),E)
                if (dice_face>dice_max)|(dice_check<-1)|(dice_check>dice_max)|(dice_face<=0)|(dice_max<=0):
                    raise MediaError('[BIAnimeError]:','Invalid argument',name_tx,dice_max,dice_check,dice_face,'for BIAnime dice!')
            N_dice = len(anime_args)
            if N_dice > 4:
                N_dice=4
                anime_args = anime_args[0:4]# 最多4个
            y_anchor = {4:int(0.1667*screensize[1]),3:int(0.25*screensize[1]),2:int(0.3333*screensize[1]),1:int(0.4167*screensize[1])}[N_dice]
            y_unit = int(0.1667*screensize[1])
            BIA_text = ImageFont.truetype('./media/SourceHanSerifSC-Heavy.otf', int(0.0521*screensize[0]))
            if layer==0: # 底层 名字 /检定
                canvas = Image.new(mode='RGBA',size=screensize,color=(0,0,0,0))
                for i,die in enumerate(anime_args): 
                    name_tx,dice_max,dice_check,dice_face = die
                    dice_max,dice_face,dice_check = map(lambda x:-1 if x=='NA' else int(x),(dice_max,dice_face,dice_check))
                    # 渲染
                    test_canvas = Image.new(mode='RGBA',size=screensize,color=(0,0,0,0))
                    test_draw = ImageDraw.Draw(test_canvas)
                    test_draw.text((0,0), name_tx, font = BIA_text, align ="left",fill = (255,255,255,255))
                    try:
                        p1,p2,p3,p4 = test_canvas.getbbox() # 重新包装为函数？
                    except TypeError:
                        p1,p2,p3,p4 = (0,0,1,int(0.0521*screensize[0])) # nx=1 ny =fontsize
                    nx = p3 - p1
                    ny = p4 - p2
                    name_surf = test_canvas.crop((p1,p2,p3,p4))
                    canvas.paste(name_surf,(int(0.3125*screensize[0])-nx//2,y_anchor+i*y_unit+(y_unit-ny)//2)) # 0.3125*screensize[0] = 600
                    if dice_check != -1:
                        test_canvas = Image.new(mode='RGBA',size=screensize,color=(0,0,0,0))
                        test_draw = ImageDraw.Draw(test_canvas)
                        test_draw.text((0,0), '/%d'%dice_check, font = BIA_text, align ="left",fill = (255,255,255,255))
                        try:
                            p1,p2,p3,p4 = test_canvas.getbbox()
                        except TypeError:
                            p1,p2,p3,p4 = (0,0,1,int(0.0521*screensize[0])) # nx=1 ny =fontsize
                        cx = p3 - p1
                        cy = p4 - p2
                        check_surf = test_canvas.crop((p1,p2,p3,p4))
                        canvas.paste(check_surf,(int(0.7292*screensize[0]),y_anchor+i*y_unit+(y_unit-ny)//2)) # 0.7292*screensize[0] = 1400
                self.size = screen_size
                self.pos = (0,0)
            elif layer==1: #无法显示动态，留空白
                canvas = Image.new(mode='RGBA',size=(int(0.1458*screensize[0]),y_unit*N_dice),color=(0,0,0,0))
                self.size = (int(0.1458*screensize[0]),y_unit*N_dice)
                self.pos = (int(0.5833*screensize[0]),y_anchor)
            elif layer==2:
                dice_cmap={3:(124,191,85,255),1:(94,188,235,255),0:(245,192,90,255),2:(233,86,85,255),-1:(255,255,255,255)}
                canvas = Image.new(mode='RGBA',size=(int(0.1458*screensize[0]),y_unit*N_dice),color=(0,0,0,0))
                self.size = (int(0.1458*screensize[0]),y_unit*N_dice)
                self.pos = (int(0.5833*screensize[0]),y_anchor)
                for i,die in enumerate(anime_args): 
                    name_tx,dice_max,dice_check,dice_face = die
                    dice_max,dice_face,dice_check = map(lambda x:-1 if x=='NA' else int(x),(dice_max,dice_face,dice_check))
                    significant = 0.05 # 大成功失败阈值
                    if dice_check == -1:
                        color_flag = -1
                    else:
                        color_flag = ((dice_face/dice_max<=significant)|(dice_face/dice_max>(1-significant)))*2 + (dice_face<=dice_check)
                    BIA_color_Text = ImageFont.truetype('./media/SourceHanSerifSC-Heavy.otf', int(0.0651*screensize[0]))
                    test_canvas = Image.new(mode='RGBA',size=(int(0.1458*screensize[0]),y_unit),color=(0,0,0,0))
                    test_draw = ImageDraw.Draw(test_canvas)
                    test_draw.text((0,0),str(dice_face),font=BIA_color_Text,align="left",fill=dice_cmap[color_flag])
                    try:
                        p1,p2,p3,p4 = test_canvas.getbbox()
                    except TypeError:
                        p1,p2,p3,p4 = (0,0,1,int(0.0651*screensize[0])) # nx=1 ny =fontsize
                    fx = p3 - p1
                    fy = p4 - p2
                    face_surf = test_canvas.crop((p1,p2,p3,p4))
                    canvas.paste(face_surf,(int(0.1458*screensize[0]-fx-0.0278*screensize[1]),i*y_unit+(y_unit-fy)//2))
            else:
                pass
            ofile = output_path+'/auto_BIA_%d'%outanime_index+'.png'
            canvas.save(ofile)
            self.path = reformat_path(ofile) # 兼容动画Animation，只使用第一帧！
            self.filename = 'auto_BIA_%d'%outanime_index+'.png'
            self.fileindex = 'AMfile_%d'% file_index
            self.PRpos = PR_center_arg(np.array(self.size),np.array(self.pos))
            outanime_index = outanime_index+1
            file_index = file_index+1
            
# 音效
class Audio:
    def __init__(self,filepath):
        global file_index 
        self.path = reformat_path(filepath)
        self.length = get_audio_length(filepath)*frame_rate
        self.filename = self.path.split('/')[-1]
        self.fileindex = 'AUfile_%d'% file_index
        file_index = file_index+1
        
    def display(self,begin):
        global audio_clip_tplt,clip_index
        clip_this = audio_clip_tplt.format(**{'clipid':'AU_clip_%d'%clip_index,
                                              'type':Audio_type,
                                              'clipname':'AU_clip_%d'%clip_index,
                                              'audiolen':'%d'%self.length,
                                              'timebase':'%d'%frame_rate,
                                              'ntsc':Is_NTSC,
                                              'start':'%d'%begin,
                                              'end':'%d'%(begin+self.length),
                                              'in':'0',
                                              'out':'%d'%self.length,
                                              'fileid':self.fileindex,
                                              'filename':self.filename,
                                              'filepath':self.path})
        clip_index = clip_index+1
        return clip_this
    
    def convert(self):
        pass

# 背景音乐
class BGM:
    def __init__(self,filepath,volume=100,loop=True):
        print('[33m[warning]:[0m BGM '+filepath+' is automatically ignored, you should add BGM manually in Premiere Pro later.')
    def convert(self):
        pass

# 异常定义

class ParserError(Exception):
    def __init__(self,*description):
        self.description = ' '.join(map(str,description))
    def __str__(self):
        return self.description

class MediaError(ParserError):
    pass

# 函数定义

# 获取音频长度
def get_audio_length(filepath):
    mixer.init()
    try:
        this_audio = mixer.Sound(filepath)
    except Exception as E:
        print('[33m[warning]:[0m Unable to get audio length of '+str(filepath)+', due to:',E)
        return np.nan
    return this_audio.get_length()

# 重格式化路径
def reformat_path(path):#only use for windows path format
    cwd = os.getcwd().replace('\\','/')
    if path[0] == '/': #unix正斜杠，报错
        raise ValueError('invalid path type')
    if '\\' in path: #是不是反斜杠？
        path = path.replace('\\','/') 
    if ('&' in path)|('<' in path)|('>' in path):
        path = path.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;') # aplha1.7.2 xml 转移的bug
    if ('"' in path)|("'" in path):
        path = path.replace('"','&quot;').replace("'",'&apos;')
    if path[0] == '.':#是不是./123/型
        path = cwd + path[1:]
    if path[0:2] not in ['C:','D:','E:','F:','G:','H:']: #是不是123/型
        path = cwd + '/' + path
    disk_label = path[0]
    path = path.replace('//','/')
    return 'file://localhost/' + disk_label + '%3a' + path[path.find('/'):]

# 处理bg 和 am 的parser
def parse_timeline(layer):
    global timeline,break_point
    track = timeline[[layer]]
    clips = []
    item,begin,end = 'NA',0,0
    for key,values in track.iterrows():
        #如果item变化了，或者进入了指定的断点
        if (values[layer] != item) | (key in break_point.values): 
            if (item == 'NA') | (item!=item): # 如果itme是空 
                pass # 则不输出什么
            else:
                end = key #否则把当前key作为一个clip的断点
                clips.append((item,begin,end)) #并记录下这个断点
            item = values[layer] #无论如何，重设item和begin
            begin = key
        else: #如果不满足断点要求，那么就什么都不做
            pass
    # 循环结束之后，最后检定一次是否需要输出一个clips
    #end = key # alpha 1.7.5 debug: 循环结束时的key有可能并不是时间轴的终点
    end = int(break_point.max()) # 因为有可能到终点为止，所有帧都是一样的，而导致被去重略去
    if (item == 'NA') | (item!=item):
        pass
    else:
        clips.append((item,begin,end))
    return clips #返回一个clip的列表

# 处理Bb 的parser
def parse_timeline_bubble(layer):
    global timeline,break_point
    track = timeline[[layer,layer+'_main',layer+'_header']]
    clips = []
    item,begin,end = 'NA',0,0
    for key,values in track.iterrows():
        #如果item变化了，或者进入了指定的断点(这是保证断句的关键！)
        if (values[layer] != item) | (key in break_point.values): 
            if (item == 'NA') | (item!=item): # 如果itme是空 
                pass # 则不输出什么
            else:
                end = key #否则把当前key作为一个clip的断点
                clips.append((item,main_text,header_text,begin,end)) #并记录下这个断点
            item = values[layer] #无论如何，重设item和begin
            main_text = values[layer + '_main']
            header_text = values[layer + '_header']
            begin = key
        else: #如果不满足断点要求，那么就什么都不做
            pass
        # 然后更新文本内容
        main_text = values[layer + '_main']
        header_text = values[layer + '_header']
    # 循环结束之后，最后检定一次是否需要输出一个clips
    #end = key
    end = int(break_point.max()) # alpha 1.7.5 debug: 而breakpoint的最大值一定是时间轴的终点
    if (item == 'NA') | (item!=item):
        pass
    else:
        clips.append((item,main_text,header_text,begin,end))
    return clips #返回一个clip的列表

# pygame形式的pos转换为PR形式的pos

def PR_center_arg(obj_size,pygame_pos):
    screensize = np.array(screen_size)
    return (pygame_pos+obj_size/2-screensize/2)/obj_size

# 全局变量

cmap = {'black':(0,0,0,255),'white':(255,255,255,255),'greenscreen':(0,177,64,255)}
Is_NTSC = str(frame_rate % 30 == 0)
Audio_type = 'Stereo'
stdin_name = stdin_log.replace('\\','/').split('/')[-1]
occupied_variable_name = open('./media/occupied_variable_name.list','r',encoding='utf8').read().split('\n')

# 载入xml 模板文件

project_tplt = open('./xml_templates/tplt_sequence.xml','r',encoding='utf8').read()
track_tplt = open('./xml_templates/tplt_track.xml','r',encoding='utf8').read()
audio_track_tplt = open('./xml_templates/tplt_audiotrack.xml','r',encoding='utf8').read()
clip_tplt = open('./xml_templates/tplt_clip.xml','r',encoding='utf8').read()
audio_clip_tplt = open('./xml_templates/tplt_audio_clip.xml','r',encoding='utf8').read()

# 载入timeline 和 breakpoint

timeline = pd.read_pickle(stdin_log)
break_point = pd.read_pickle(stdin_log.replace('timeline','breakpoint'))
bulitin_media = pd.read_pickle(stdin_log.replace('timeline','bulitinmedia'))

def main():
    global media_list
    print('[export XML]: Welcome to use exportXML for TRPG-replay-generator '+edtion)
    print('[export XML]: The output xml file and refered png files will be saved at "'+output_path+'"')

    # 载入od文件
    try:
        object_define_text = open(media_obj,'r',encoding='utf-8').read()#.split('\n')
    except UnicodeDecodeError as E:
        print('[31m[DecodeError]:[0m',E)
        sys.exit(1)
    if object_define_text[0] == '\ufeff': # 139 debug
        print('[33m[warning]:[0m','UTF8 BOM recognized in MediaDef, it will be drop from the begin of file!')
        object_define_text = object_define_text[1:]
    object_define_text = object_define_text.split('\n')

    media_list=[]
    for i,text in enumerate(object_define_text):
        if text == '':
            continue
        elif text[0] == '#':
            continue
        else:
            try:
                exec(text) #对象实例化
                obj_name = text.split('=')[0]
                obj_name = obj_name.replace(' ','')
                if obj_name in occupied_variable_name:
                    raise SyntaxError('Obj name occupied')
                elif (len(re.findall('\w+',obj_name))==0)|(obj_name[0].isdigit()):
                    raise SyntaxError('Invalid Obj name')
                media_list.append(obj_name) #记录新增对象名称
            except Exception as E:
                print('[31m[SyntaxError]:[0m "'+text+'" appeared in media define file line ' + str(i+1)+' is invalid syntax:',E)
                sys.exit(1)
    black = Background('black')
    white = Background('white')
    media_list.append('black')
    media_list.append('white')
    # alpha 1.6.5 载入导出的内建媒体
    for key,values in bulitin_media.iteritems():
        exec(values)
        media_list.append(key)

    # 开始生成

    print('[export XML]: Begin to export.')
    video_tracks = []
    audio_tracks = []
    for layer in zorder + ['SE','Voice']:
        if layer == 'Bb':
            track_items = parse_timeline_bubble(layer)
            bubble_clip_list = []
            text_clip_list = []
            for item in track_items:
                bubble_this,text_this = eval('{0}.display(begin ={1},end={2},text="{3}",header="{4}")'
                                             .format(item[0],item[3],item[4],item[1],item[2]))
                bubble_clip_list.append(bubble_this)
                text_clip_list.append(text_this)
            video_tracks.append(track_tplt.format(**{'targeted':'False','clips':'\n'.join(bubble_clip_list)}))
            video_tracks.append(track_tplt.format(**{'targeted':'True','clips':'\n'.join(text_clip_list)}))
            
        elif layer in ['SE','Voice']:
            track_items = parse_timeline(layer)
            clip_list = []
            for item in track_items:
                if item[0] in media_list:
                    clip_list.append(eval('{0}.display(begin={1})'.format(item[0],item[1])))
                elif os.path.isfile(item[0][1:-1]) == True: # 注意这个位置的item[0]首尾应该有个引号
                    temp = Audio(item[0][1:-1])
                    clip_list.append(temp.display(begin=item[1]))
                else:
                    print("[33m[warning]:[0m",'Audio file',item[0],'is not exist.')
            audio_tracks.append(audio_track_tplt.format(**{'type':Audio_type,'clips':'\n'.join(clip_list)}))
            
        else:
            track_items = parse_timeline(layer)
            clip_list = []
            for item in track_items:
                clip_list.append(eval('{0}.display(begin={1},end={2})'.format(item[0],item[1],item[2])))
            video_tracks.append(track_tplt.format(**{'targeted':'False','clips':'\n'.join(clip_list)}))

    main_output = project_tplt.format(**{'timebase':'%d'%frame_rate,
                           'ntsc':Is_NTSC,
                           'sequence_name':stdin_name,
                           'screen_width':'%d'%screen_size[0],
                           'screen_height':'%d'%screen_size[1],
                           'tracks_vedio':'\n'.join(video_tracks),
                           'tracks_audio':'\n'.join(audio_tracks)})

    ofile = open(output_path+'/'+stdin_name+'.xml','w',encoding='utf-8')
    ofile.write(main_output)
    ofile.close()
    print('[export XML]: Done!')
if __name__ == '__main__':
    main()