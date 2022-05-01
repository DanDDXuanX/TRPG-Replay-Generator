#!/usr/bin/env python
# coding: utf-8
edtion = 'alpha 1.10.0'

# 外部参数输入

import argparse
import sys
import os

# 参数处理
ap = argparse.ArgumentParser(description="Generating your TRPG replay video from logfile.")
ap.add_argument("-l", "--LogFile", help='The standerd input of this programme, which is mainly composed of TRPG log.',type=str)
ap.add_argument("-d", "--MediaObjDefine", help='Definition of the media elements, using real python code.',type=str)
ap.add_argument("-t", "--CharacterTable", help='The correspondence between character and media elements, using tab separated text file or Excel table.',type=str)
ap.add_argument("-o", "--OutputPath", help='Choose the destination directory to save the project timeline and breakpoint file.',type=str,default=None)
# 选项
ap.add_argument("-F", "--FramePerSecond", help='Set the FPS of display, default is 30 fps, larger than this may cause lag.',type=int,default=30)
ap.add_argument("-W", "--Width", help='Set the resolution of display, default is 1920, larger than this may cause lag.',type=int,default=1920)
ap.add_argument("-H", "--Height", help='Set the resolution of display, default is 1080, larger than this may cause lag.',type=int,default=1080)
ap.add_argument("-Z", "--Zorder", help='Set the display order of layers, not recommended to change the values unless necessary!',type=str,
                default='BG3,BG2,BG1,Am3,Am2,Am1,Bb')
# 用于语音合成的key
ap.add_argument("-K", "--AccessKey", help='Your AccessKey, to use with --SynthsisAnyway',type=str,default="Your_AccessKey")
ap.add_argument("-S", "--AccessKeySecret", help='Your AccessKeySecret, to use with --SynthsisAnyway',type=str,default="Your_AccessKey_Secret")
ap.add_argument("-A", "--Appkey", help='Your Appkey, to use with --SynthsisAnyway',type=str,default="Your_Appkey")
# 用于导出视频的质量值
ap.add_argument("-Q", "--Quality", help='Choose the quality (ffmpeg crf) of output video, to use with --ExportVideo.',type=int,default=24)
# Flags
ap.add_argument('--ExportXML',help='Export a xml file to load in Premiere Pro, some .png file will be created at same time.',action='store_true')
ap.add_argument('--ExportVideo',help='Export MP4 video file, this will disables interface display',action='store_true')
ap.add_argument('--SynthesisAnyway',help='Execute speech_synthezier first, and process all unprocessed asterisk time label.',action='store_true')
ap.add_argument('--FixScreenZoom',help='Windows system only, use this flag to fix incorrect windows zoom.',action='store_true')

args = ap.parse_args()

# 退出程序
def system_terminated(exit_type='Error'):
    exit_print = {'Error':'A major error occurred. Execution terminated!',
                  'User':'Display terminated, due to user commands.',
                  'Video':'Video exported. Execution terminated!',
                  'End':'Display finished!'}
    print('[replay generator]: '+exit_print[exit_type])
    if exit_type == 'Error':
        sys.exit(1) # 错误退出的代码
    else:
        sys.exit(0) # 正常退出的代码

media_obj = args.MediaObjDefine #媒体对象定义文件的路径
char_tab = args.CharacterTable #角色和媒体对象的对应关系文件的路径
stdin_log = args.LogFile #log路径
output_path = args.OutputPath #保存的时间轴，断点文件的目录

screen_size = (args.Width,args.Height) #显示的分辨率
frame_rate = args.FramePerSecond #帧率 单位fps
zorder = args.Zorder.split(',') #渲染图层顺序

AKID = args.AccessKey
AKKEY = args.AccessKeySecret
APPKEY = args.Appkey

crf = args.Quality # 导出视频的质量值

exportXML = args.ExportXML #导出为XML
exportVideo = args.ExportVideo #导出为视频
synthfirst = args.SynthesisAnyway #是否先行执行语音合成
fixscreen = args.FixScreenZoom # 是否修复窗体缩放

try:
    for path in [stdin_log,media_obj,char_tab]:
        if path == None:
            raise OSError("[31m[ArgumentError]:[0m Missing principal input argument!")
        if os.path.isfile(path) == False:
            raise OSError("[31m[ArgumentError]:[0m Cannot find file "+path)

    if output_path == None:
        if (synthfirst == True) | (exportXML == True) | (exportVideo == True):
            raise OSError("[31m[ArgumentError]:[0m Some flags requires output path, but no output path is specified!")
    elif os.path.isdir(output_path) == False:
        raise OSError("[31m[ArgumentError]:[0m Cannot find directory "+output_path)
    else:
        output_path = output_path.replace('\\','/')

    # FPS
    if frame_rate <= 0:
        raise ValueError("[31m[ArgumentError]:[0m Invalid frame rate:"+str(frame_rate))
    elif frame_rate>30:
        print("[33m[warning]:[0m",'FPS is set to '+str(frame_rate)+', which may cause lag in the display!')

    if (screen_size[0]<=0) | (screen_size[1]<=0):
        raise ValueError("[31m[ArgumentError]:[0m Invalid resolution:"+str(screen_size))
    if screen_size[0]*screen_size[1] > 3e6:
        print("[33m[warning]:[0m",'Resolution is set to more than 3M, which may cause lag in the display!')
except Exception as E:
    print(E)
    system_terminated('Error')

# 包导入

import pandas as pd
import numpy as np
import pygame
import pygame.freetype
import re
import time #开发模式，显示渲染帧率
import glob # 匹配路径


# 类定义 alpha 1.9.6

# 文字对象
class Text:
    pygame.font.init()
    def __init__(self,fontfile='./media/SourceHanSansCN-Regular.otf',fontsize=40,color=(0,0,0,255),line_limit=20):
        self.text_render = pygame.font.Font(fontfile,fontsize)
        self.color=color
        self.size=fontsize
        self.line_limit = line_limit
    def render(self,tx):
        face = self.text_render.render(tx,True,self.color[0:3])
        if self.color[3] < 255:
            face.set_alpha(self.color[3])
        return face
    def draw(self,text):
        out_text = []
        if text == '':
            return []
        if ('#' in text) | (text[0]=='^'): #如果有手动指定的换行符 # bug:如果手动换行，但是第一个#在30字以外，异常的显示
            if text[0]=='^': # 如果使用^指定的手动换行，则先去掉这个字符。
                text = text[1:]
            text_line = text.split('#')
            for tx in text_line:
                out_text.append(self.render(tx))
        elif len(text) > self.line_limit: #如果既没有主动指定，字符长度也超限
            for i in range(0,len(text)//self.line_limit+1):#较为简单粗暴的自动换行
                out_text.append(self.render(text[i*self.line_limit:(i+1)*self.line_limit]))
        else:
            out_text = [self.render(text)]
        return out_text
    def convert(self):
        pass

# 描边文本，是Text的子类。注意，使用这个媒体类可能会影响帧率！
class StrokeText(Text):
    pygame.font.init()
    def __init__(self,fontfile='./media/SourceHanSansCN-Regular.otf',fontsize=40,color=(0,0,0,255),line_limit=20,edge_color=(255,255,255,255)):
        super().__init__(fontfile=fontfile,fontsize=fontsize,color=color,line_limit=line_limit) # 继承
        self.edge_color=edge_color
    def render(self,tx):
        edge = self.text_render.render(tx,True,self.edge_color[0:3])
        face = self.text_render.render(tx,True,self.color[0:3])
        if self.edge_color[3] < 255:
            edge.set_alpha(self.edge_color[3])
        if self.color[3] < 255:
            face.set_alpha(self.color[3])
        canvas = pygame.Surface((edge.get_size()[0]+2,edge.get_size()[1]+2),pygame.SRCALPHA)
        for pos in [(0,0),(0,1),(0,2),(1,0),(1,2),(2,0),(2,1),(2,2)]:
            canvas.blit(edge,pos)
        canvas.blit(face,(1,1))
        return canvas

# 对话框、气泡、文本框
class Bubble:
    def __init__(self,filepath,Main_Text=Text(),Header_Text=None,pos=(0,0),mt_pos=(0,0),ht_pos=(0,0),align='left',line_distance=1.5):
        self.media = pygame.image.load(filepath)
        self.pos = pos
        self.MainText = Main_Text
        self.mt_pos = mt_pos
        self.Header = Header_Text
        self.ht_pos = ht_pos
        if line_distance >= 1:
            self.line_distance = line_distance
        elif line_distance > 0:
            self.line_distance = line_distance # alpha 1.9.2 debug 当linedistance低于1时，忘记初始化line_distance这个参数了
            print("[33m[warning]:[0m",'Line distance is set to less than 1!')
        else:
            raise MediaError('[31m[BubbleError]:[0m', 'Invalid line distance:',line_distance)
        if align in ('left','center'):
            self.align = align
        else:
            raise MediaError('[31m[BubbleError]:[0m', 'Unsupported align:',align)
    def display(self,surface,text,header='',alpha=100,adjust='NA'):
        if adjust in ['0,0','NA']:
            render_pos = self.pos
        else:
            adx,ady = split_xy(adjust)
            render_pos = (self.pos[0]+adx,self.pos[1]+ady)
        temp = self.media.copy()
        if (self.Header!=None) & (header!=''):    # Header 有定义，且输入文本不为空
            temp.blit(self.Header.draw(header)[0],self.ht_pos)
        x,y = self.mt_pos
        for i,s in enumerate(self.MainText.draw(text)):
            if self.align == 'left':
                temp.blit(s,(x,y+i*self.MainText.size*self.line_distance))
            else: # 就只可能是center了
                word_w,word_h = s.get_size()
                temp.blit(s,(x+(self.MainText.size*self.MainText.line_limit - word_w)//2,y+i*self.MainText.size*self.line_distance))
        if alpha !=100:
            temp.set_alpha(alpha/100*255)            
        surface.blit(temp,render_pos)
    def convert(self):
        self.media = self.media.convert_alpha()

# 背景图片
class Background:
    def __init__(self,filepath,pos = (0,0)):
        if filepath in cmap.keys(): #添加了，对纯色定义的背景的支持
            self.media = pygame.surface.Surface(screen_size)
            self.media.fill(cmap[filepath])
        else:
            self.media = pygame.image.load(filepath)
        self.pos = pos
    def display(self,surface,alpha=100,adjust='NA'):
        if adjust in ['0,0','NA']:
            render_pos = self.pos
        else:
            adx,ady = split_xy(adjust)
            render_pos = (self.pos[0]+adx,self.pos[1]+ady)
        if alpha !=100:
            temp = self.media.copy()
            temp.set_alpha(alpha/100*255)
            surface.blit(temp,render_pos)
        else:
            surface.blit(self.media,render_pos)
    def convert(self):
        self.media = self.media.convert_alpha()

# 这个是真的动画了，用法和旧版的amination是一样的！
class Animation:
    def __init__(self,filepath,pos = (0,0),tick=1,loop=True):
        file_list = np.frompyfunc(lambda x:x.replace('\\','/'),1,1)(glob.glob(filepath))
        self.length = len(file_list)
        if self.length == 0:
            raise MediaError('[31m[AnimationError]:[0m','Cannot find file match',filepath)
        self.media = np.frompyfunc(pygame.image.load,1,1)(file_list)
        self.pos = pos
        self.loop = loop
        self.this = 0
        self.tick = tick
    def display(self,surface,alpha=100,adjust='NA',frame=0):
        self.this = frame
        if adjust in ['0,0','NA']:
            render_pos = self.pos
        else:
            adx,ady = split_xy(adjust)
            render_pos = (self.pos[0]+adx,self.pos[1]+ady)
        if alpha !=100:
            temp = self.media[int(self.this)].copy()
            temp.set_alpha(alpha/100*255)
            surface.blit(temp,render_pos)
        else:
            surface.blit(self.media[int(self.this)],render_pos)
    def get_tick(self,duration): # 1.8.0
        if self.length > 1: # 如果length > 1 说明是多帧的动画！
            tick_lineline = (np.arange(0,duration if self.loop else self.length,1/self.tick)[0:duration]%(self.length))
            tick_lineline = np.hstack([tick_lineline,(self.length-1)*np.ones(duration-len(tick_lineline))]).astype(int)
        else:
            tick_lineline = np.zeros(duration).astype(int)
        return tick_lineline
    def convert(self):
        self.media = np.frompyfunc(lambda x:x.convert_alpha(),1,1)(self.media)

# a1.7.5 内建动画，Animation类的子类
class BuiltInAnimation(Animation):
    def __init__(self,anime_type='hitpoint',anime_args=('0',0,0,0),screensize = (1920,1080),layer=0):
        BIA_text = Text('./media/SourceHanSerifSC-Heavy.otf',fontsize=int(0.0521*screensize[0]),color=(255,255,255,255),line_limit=10)
        if anime_type == 'hitpoint': # anime_args=('0',0,0,0)
            # 载入图片
            heart = pygame.image.load('./media/heart.png')
            heart_shape = pygame.image.load('./media/heart_shape.png')
            hx,hy = heart.get_size()
            # 重设图片尺寸，根据screensize[0]
            if screensize[0]!=1920:
                multip = screensize[0]/1920
                heart = pygame.transform.scale(heart,(int(hx*multip),int(hy*multip)))
                heart_shape = pygame.transform.scale(heart_shape,(int(hx*multip),int(hy*multip)))
                hx,hy = heart.get_size()
            # 动画参数
            name_tx,heart_max,heart_begin,heart_end = anime_args

            if (heart_end==heart_begin)|(heart_max<max(heart_begin,heart_end)):
                raise MediaError('[31m[BIAnimeError]:[0m','Invalid argument',name_tx,heart_max,heart_begin,heart_end,'for BIAnime hitpoint!')
            elif heart_end > heart_begin: # 如果是生命恢复
                temp = heart_end
                heart_end = heart_begin
                heart_begin = temp # 则互换顺序 确保 begin一定是小于end的
                heal_heart = True
            else:
                heal_heart = False

            distance = int(0.026*screensize[0]) # default = 50

            total_heart = int(heart_max/2 * hx + max(0,np.ceil(heart_max/2-1)) * distance) #画布总长
            left_heart = int(heart_end/2 * hx + max(0,np.ceil(heart_end/2-1)) * distance) #画布总长
            lost_heart = int((heart_begin-heart_end)/2 * hx + np.floor((heart_begin-heart_end)/2) * distance)

            nametx_surf = BIA_text.draw(name_tx)[0] # 名牌
            nx,ny = nametx_surf.get_size() # 名牌尺寸
            # 开始制图
            if layer==0: # 底层 阴影图
                self.pos = ((screensize[0]-max(nx,total_heart))/2,(4/5*screensize[1]-hy-ny)/2)
                canvas = pygame.Surface((max(nx,total_heart),hy+ny+screensize[1]//5),pygame.SRCALPHA)
                canvas.fill((0,0,0,0))
                if nx > total_heart:
                    canvas.blit(nametx_surf,(0,0))
                    posx = (nx-total_heart)//2
                else:
                    canvas.blit(nametx_surf,((total_heart-nx)//2,0))
                    posx = 0
                posy = ny+screensize[1]//5
                self.tick = 1
                self.loop = 1
                for i in range(1,heart_max+1): # 偶数，低于最终血量
                    if i%2 == 0:
                        canvas.blit(heart_shape,(posx,posy))
                        posx = posx + hx + distance
                    else:
                        pass
                if heart_max%2 == 1: # max是奇数
                    left_heart_shape = heart_shape.subsurface((0,0,int(hx/2),hy))
                    canvas.blit(left_heart_shape,(total_heart-int(hx/2),posy))
            elif layer==1: # 剩余的血量
                self.pos = ((screensize[0]-total_heart)/2,3/5*screensize[1]+ny/2-hy/2)
                canvas = pygame.Surface((left_heart,hy),pygame.SRCALPHA)
                canvas.fill((0,0,0,0))
                posx,posy = 0,0
                self.tick = 1
                self.loop = 1
                for i in range(1,heart_end+1): # 偶数，低于最终血量
                    if i%2 == 0:
                        canvas.blit(heart,(posx,posy))
                        posx = posx + hx + distance
                    else:
                        pass
                if heart_end%2 == 1: # end是奇数
                    left_heart = heart.subsurface((0,0,int(hx/2),hy))
                    canvas.blit(left_heart,(heart_end//2*(hx + distance),0))
            elif layer==2: # 损失/恢复的血量
                self.pos = (heart_end//2*(hx + distance)+(heart_end%2)*int(hx/2)+(screensize[0]-total_heart)/2,3/5*screensize[1]+ny/2-hy/2)
                canvas = pygame.Surface((lost_heart,hy),pygame.SRCALPHA)
                canvas.fill((0,0,0,0))
                posx,posy = 0,0
                self.tick = 1
                self.loop = 1
                for i in range(1,heart_begin-heart_end+1): 
                    if (i == 1)&(heart_end%2 == 1): # 如果end是奇数，先来半个右边
                        right_heart = heart.subsurface((int(hx/2),0,int(hx/2),hy))
                        canvas.blit(right_heart,(posx,posy))
                        posx = posx + int(hx/2) + distance
                    elif ((i - heart_end%2)%2 == 0): # 如果和end的差值是
                        canvas.blit(heart,(posx,posy))
                        posx = posx + hx + distance
                    elif (i == heart_begin-heart_end)&(heart_begin%2 == 1): # 如果最右边边也是半个心
                        left_heart = heart.subsurface((0,0,int(hx/2),hy))
                        canvas.blit(left_heart,(posx,posy))
                    else:
                        pass
            else:
                pass
            if (heal_heart == True)&(layer == 2): # 恢复动画
                crop_timeline = sigmoid(0,lost_heart,frame_rate).astype(int) # 裁剪时间线
                self.media = np.frompyfunc(lambda x:canvas.subsurface(0,0,x,hy),1,1)(crop_timeline) # 裁剪动画
            else:
                self.media=np.array([canvas]) # 正常的输出，单帧
            #剩下的需要定义的
            self.this = 0
            self.length=len(self.media)
        if anime_type == 'dice': # anime_args=('name',max,check,face) #骰子
            def get_possible_digit(dice_max):
                dice_max = 10**(int(np.log10(dice_max))+1)-1
                possible = {}
                for i in range(0,100):
                    if dice_max//(10**i)>=10:
                        possible[i] = list(range(0,10))
                    elif dice_max//(10**i)>=1:
                        possible[i] = list(range(0,1+dice_max//(10**i)))
                    else:
                        break
                dice_value = np.repeat('',10)
                for i in possible.keys():
                    digit = np.array(possible[i])
                    np.random.shuffle(digit) # 乱序
                    if len(digit)<10:
                        digit = np.hstack([digit,np.repeat('',10-len(digit))])
                    dice_value = np.frompyfunc(lambda x,y:x+y,2,1)(digit.astype(str),dice_value)
                return max(possible.keys())+1,dice_value
            # 动画参数
            # 检查参数合法性
            for die in anime_args:
                try:
                    # 转换为int类型，NA转换为-1
                    name_tx,dice_max,dice_check,dice_face = die
                    dice_max,dice_face,dice_check = map(lambda x:-1 if x=='NA' else int(x),(dice_max,dice_face,dice_check))
                except ValueError as E: #too many values to unpack,not enough values to unpack
                    raise MediaError('[31m[BIAnimeError]:[0m','Invalid syntax:',str(die),E)
                if (dice_face>dice_max)|(dice_check<-1)|(dice_check>dice_max)|(dice_face<=0)|(dice_max<=0):
                    raise MediaError('[31m[BIAnimeError]:[0m','Invalid argument',name_tx,dice_max,dice_check,dice_face,'for BIAnime dice!')
            # 最多4个
            N_dice = len(anime_args)
            if N_dice > 4:
                N_dice=4
                anime_args = anime_args[0:4]# 最多4个
            #y_anchor = {4:180,3:270,2:360,1:450}[N_dice] # sep=180 x[600,1400]
            y_anchor = {4:int(0.1667*screensize[1]),3:int(0.25*screensize[1]),2:int(0.3333*screensize[1]),1:int(0.4167*screensize[1])}[N_dice]
            y_unit = int(0.1667*screensize[1])
            if layer==0: # 底层 名字 /检定
                canvas = pygame.Surface(screensize,pygame.SRCALPHA)
                for i,die in enumerate(anime_args): 
                    name_tx,dice_max,dice_check,dice_face = die
                    dice_max,dice_face,dice_check = map(lambda x:-1 if x=='NA' else int(x),(dice_max,dice_face,dice_check))
                    # 渲染
                    name_surf = BIA_text.render(name_tx)
                    nx,ny = name_surf.get_size()
                    canvas.blit(name_surf,(int(0.3125*screensize[0])-nx//2,y_anchor+i*y_unit+(y_unit-ny)//2)) # 0.3125*screensize[0] = 600
                    if dice_check != -1:
                        check_surf = BIA_text.render('/%d'%dice_check)
                        cx,cy = check_surf.get_size()
                        canvas.blit(check_surf,(int(0.7292*screensize[0]),y_anchor+i*y_unit+(y_unit-ny)//2)) # 0.7292*screensize[0] = 1400
                self.media = np.array([canvas])
                self.pos = (0,0)
                self.tick = 1
                self.loop = 1
            elif layer==1:
                #画布
                canvas = []
                for i in range(0,int(2.5*frame_rate)):
                    canvas_frame = pygame.Surface((int(0.1458*screensize[0]),y_unit*N_dice),pygame.SRCALPHA) # 0.1458*screensize[0] = 280
                    canvas.append(canvas_frame)
                # 骰子
                for l,die in enumerate(anime_args): 
                    name_tx,dice_max,dice_check,dice_face = die
                    dice_max,dice_face,dice_check = map(lambda x:-1 if x=='NA' else int(x),(dice_max,dice_face,dice_check))
                    cols,possible_digit = get_possible_digit(dice_max)
                    dx,dy = BIA_text.render('0'*cols).get_size()
                    # running cols
                    run_surf = pygame.Surface((dx,dy*len(possible_digit)),pygame.SRCALPHA)
                    for i,digit in enumerate(possible_digit):
                        for j,char in enumerate(digit): # alpha 1.8.4 兼容非等宽数字，比如思源宋体
                            char_this = BIA_text.render(char)
                            run_surf.blit(char_this,(j*(dx//cols),dy*i))
                    run_cols = np.frompyfunc(lambda x:run_surf.subsurface(x*(dx//cols),0,dx//cols,dy*10),1,1)(np.arange(0,cols))
                    # range
                    slot_surf = []
                    for i in range(0,int(2.5*frame_rate)):
                        slot_frame = pygame.Surface((dx,dy),pygame.SRCALPHA)
                        slot_surf.append(slot_frame)
                    for i in range(0,cols):
                        if cols == 1:
                            speed_multiplier = 1
                        else:
                            speed_multiplier = np.linspace(2,1,cols)[i]
                        speed = speed_multiplier*dy*11/2.5/frame_rate
                        for t in range(0,int(2.5*frame_rate/speed_multiplier)):
                            slot_surf[t].blit(run_cols[i],(i*dx//cols,int(dy-t*speed)))
                    for t in range(0,int(2.5*frame_rate/speed_multiplier)):
                        #canvas[t].blit(slot_surf[t],(int(0.1458*screensize[0]-dx-0.0278*screensize[1]),(l+1)*y_unit-dy-int(0.0278*screensize[1]))) #0.0278*screensize[1] = 30
                        canvas[t].blit(slot_surf[t],(int(0.1458*screensize[0]-dx-0.0278*screensize[1]),l*y_unit+(y_unit-dy)//2))
                self.media = np.array(canvas)
                self.pos = (int(0.5833*screensize[0]),y_anchor)
                self.tick = 1
                self.loop = 1
            elif layer==2:
                dice_cmap={3:(124,191,85,255),1:(94,188,235,255),0:(245,192,90,255),2:(233,86,85,255),-1:(255,255,255,255)}
                canvas = pygame.Surface((int(0.1458*screensize[0]),y_unit*N_dice),pygame.SRCALPHA)
                for i,die in enumerate(anime_args): 
                    name_tx,dice_max,dice_check,dice_face = die
                    dice_max,dice_face,dice_check = map(lambda x:-1 if x=='NA' else int(x),(dice_max,dice_face,dice_check))
                    # 渲染 0.0651
                    significant = 0.05 # 大成功失败阈值
                    if dice_check == -1:
                        color_flag = -1
                    else:
                        color_flag = ((dice_face/dice_max<=significant)|(dice_face/dice_max>(1-significant)))*2 + (dice_face<=dice_check)
                    BIA_color_Text = Text('./media/SourceHanSerifSC-Heavy.otf',fontsize=int(0.0651*screensize[0]),color=dice_cmap[color_flag],line_limit=10) # 1.25
                    face_surf = BIA_color_Text.render(str(dice_face))
                    fx,fy = face_surf.get_size()
                    #canvas.blit(face_surf,(int(0.1458*screensize[0]-fx-0.0278*screensize[1]),(i+1)*y_unit-fy-int(0.0278*screensize[1])))
                    canvas.blit(face_surf,(int(0.1458*screensize[0]-fx-0.0278*screensize[1]),i*y_unit+(y_unit-fy)//2))
                self.media = np.array([canvas])
                self.pos = (int(0.5833*screensize[0]),y_anchor) # 0.5833*screensize[0] = 1120
                self.tick = 1
                self.loop = 1
            else:
                pass
            self.this = 0
            self.length=len(self.media)

# 音效
class Audio:
    pygame.mixer.init()
    def __init__(self,filepath):
        self.media = pygame.mixer.Sound(filepath)
    def display(self,channel,volume=100):
        channel.set_volume(volume/100)
        channel.play(self.media)
    def convert(self):
        pass

# 背景音乐
class BGM:
    def __init__(self,filepath,volume=100,loop=True):
        self.media = filepath
        self.volume = volume/100
        if loop == True:
            self.loop = -1 #大概是不可能能放完的
        else:
            self.loop = 0
        if filepath.split('.')[-1] not in ['ogg']: #建议的格式
            print("[33m[warning]:[0m",'A not recommend music format "'+filepath.split('.')[-1]+'" is specified, which may cause unstableness during displaying!')
    def display(self):
        if pygame.mixer.music.get_busy() == True: #如果已经在播了
            pygame.mixer.music.stop() #停止
            pygame.mixer.music.unload() #换碟
        else:
            pass
        pygame.mixer.music.load(self.media) #进碟
        pygame.mixer.music.play(loops=self.loop) #开始播放
        pygame.mixer.music.set_volume(self.volume) #设置音量
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

# 正则表达式定义

RE_dialogue = re.compile('^\[([\ \w\.\;\(\)\,]+)\](<[\w\=\d]+>)?:(.+?)(<[\w\=\d]+>)?({.+})?$')
RE_background = re.compile('^<background>(<[\w\=]+>)?:(.+)$')
RE_setting = re.compile('^<set:([\w\_]+)>:(.+)$')
RE_characor = re.compile('([\w\ ]+)(\(\d*\))?(\.\w+)?')
RE_modify = re.compile('<(\w+)(=\d+)?>')
RE_sound = re.compile('({.+?})')
RE_asterisk = re.compile('(\{([^\{\}]*?[,;])?\*([\w\.\,，。：？！“”]*)?\})') # v 1.8.7 给星标后文本额外增加几个可用的中文符号
RE_hitpoint = re.compile('<hitpoint>:\((.+?),(\d+),(\d+),(\d+)\)') # a 1.6.5 血条预设动画
RE_dice = re.compile('\((.+?),(\d+),([\d]+|NA),(\d+)\)') # a 1.7.5 骰子预设动画，老虎机
#RE_asterisk = re.compile('(\{([^\{\}]*?[,;])?\*([\w\.\,，]*)?\})') # v 1.7.3 修改匹配模式以匹配任何可能的字符（除了花括号）
#RE_asterisk = re.compile('\{\w+[;,]\*(\d+\.?\d*)\}') # 这种格式对于{path;*time的}的格式无效！
#RE_asterisk = re.compile('(\{([\w\.\\\/\'\":]*?[,;])?\*([\w\.\,，]*)?\})') # a 1.4.3 修改了星标的正则（和ss一致）,这种对于有复杂字符的路径无效！

# 绝对的全局变量

python3 = sys.executable.replace('\\','/') # 获取python解释器的路径

cmap = {'black':(0,0,0,255),'white':(255,255,255,255),'greenscreen':(0,177,64,255),'notetext':(118,185,0,255)}
#render_arg = ['BG1','BG1_a','BG2','BG2_a','BG3','BG3_a','Am1','Am1_a','Am2','Am2_a','Am3','Am3_a','Bb','Bb_main','Bb_header','Bb_a']
#render_arg = ['BG1','BG1_a','BG2','BG2_a','BG3','BG3_a','Am1','Am1_a','Am2','Am2_a','Am3','Am3_a','Bb','Bb_main','Bb_header','Bb_a','BGM','Voice','SE']
render_arg = ['section','BG1','BG1_a','BG1_p','BG2','BG2_a','BG2_p','BG3','BG3_a','BG3_p',
              'Am1','Am1_t','Am1_a','Am1_p','Am2','Am2_t','Am2_a','Am2_p','Am3','Am3_t','Am3_a','Am3_p',
              'Bb','Bb_main','Bb_header','Bb_a','Bb_p','BGM','Voice','SE']
# 1.6.3 Am的更新，再新增一列，动画的帧！
# 被占用的变量名 # 1.7.7
occupied_variable_name = open('./media/occupied_variable_name.list','r',encoding='utf8').read().split('\n')

# 数学函数定义 formula

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

# 可以<set:keyword>动态调整的全局变量

am_method_default = '<replace=0>' #默认切换效果（立绘）
am_dur_default = 10 #默认切换效果持续时间（立绘）

bb_method_default = '<replace=0>' #默认切换效果（文本框）
bb_dur_default = 10 #默认切换效果持续时间（文本框）

bg_method_default = '<replace=0>' #默认切换效果（背景）
bg_dur_default = 10 #默认切换效果持续时间（背景）

tx_method_default = '<all=0>' #默认文本展示方式
tx_dur_default = 5 #默认单字展示时间参数

speech_speed = 220 #语速，单位word per minute
formula = linear #默认的曲线函数
asterisk_pause = 20 # 星标音频的句间间隔 a1.4.3，单位是帧，通过处理delay

secondary_alpha = 60 # a 1.8.8 次要立绘的默认透明度

# 其他函数定义

# 解析对话行 []
def get_dialogue_arg(text):
    cr,cre,ts,tse,se = RE_dialogue.findall(text)[0]
    this_duration = int(len(ts)/(speech_speed/60/frame_rate))
    this_charactor = RE_characor.findall(cr)
    # 切换参数
    if cre=='': # 没有指定 都走默认值
        am_method,am_dur = RE_modify.findall(am_method_default)[0]
        bb_method,bb_dur = RE_modify.findall(bb_method_default)[0]
    else: # 有指定，变得相同
        am_method,am_dur = RE_modify.findall(cre)[0] 
        bb_method,bb_dur = am_method,am_dur
    if am_dur == '':# 没有指定 都走默认值
        am_dur = am_dur_default
    else:# 有指定，变得相同
        am_dur = int(am_dur.replace('=',''))
    if bb_dur == '':
        bb_dur = bb_dur_default
    else:
        bb_dur = int(bb_dur.replace('=',''))
    # 文本显示参数
    if tse=='':
        tse = tx_method_default
    text_method,text_dur = RE_modify.findall(tse)[0] #<black=\d+> 
    if text_dur == '':
        text_dur = tx_dur_default
    else:
        text_dur = int(text_dur.replace('=',''))
    # 语音和音效参数
    if se == '':
        this_sound = []
    else:
        this_sound = RE_sound.findall(se)

    return (this_charactor,this_duration,am_method,am_dur,bb_method,bb_dur,ts,text_method,text_dur,this_sound)

# 解析背景行 <background>
def get_background_arg(text):
    bge,bgc = RE_background.findall(text)[0]
    if bge=='':
        bge = bg_method_default
    method,method_dur = RE_modify.findall(bge)[0]
    if method_dur == '':
        method_dur = bg_dur_default
    else:
        method_dur = int(method_dur.replace('=',''))
    return (bgc,method,method_dur)

# 解释设置行 <set:>
def get_seting_arg(text):
    target,args = RE_setting.findall(text)[0]
    return (target,args)

# 截断字符串
def cut_str(str_,len_):
    return str_[0:int(len_)]
UF_cut_str = np.frompyfunc(cut_str,2,1)

# 设定合理透明度范围
def alpha_range(x):
    if x>100:
        return 100
    if x<0:
        return 0
    else:
        return x

# UF : 将2个向量组合成"x,y"的形式
concat_xy = np.frompyfunc(lambda x,y:'%d'%x+','+'%d'%y,2,1)

# 把拼接起来的修正位置分隔开
def split_xy(concated):
    x,y = concated.split(',')
    return int(x),int(y)

def am_methods(method_name,method_dur,this_duration,i):
    def dynamic(scale,duration,balance,cut,enable): # 动态(尺度,持续,平衡,进出,启用)
        if enable == True: # cutin=1,cutout=0
            if cut == balance:
                return formula(0,scale,duration)
            else:
                return formula(scale,0,duration)
        else: # enable == False:
            return np.ones(duration)*scale*balance
    if method_dur == 0:
        return np.ones(this_duration),'NA'
    Height = screen_size[1]
    Width = screen_size[0]
    method_keys = method_name.split('_')
    method_args = {'alpha':'replace','motion':'static','direction':'up','scale':'major','cut':'both'} #default
    scale_dic = {'major':0.3,'minor':0.12,'entire':1.0}
    direction_dic = {'up':0,'down':180,'left':90,'right':270} # up = 0 剩下的逆时针
    # parse method name
    for key in method_keys:
        if key in ['black','replace','delay']:
            method_args['alpha'] = key
        elif key in ['pass','leap','static','circular']:
            method_args['motion'] = key
        elif key in ['up','down','left','right']:
            method_args['direction'] = key
        elif key in ['major','minor','entire']:
            method_args['scale'] = key
        elif key in ['in','out','both']:
            method_args['cut'] = key
        elif 'DG' == key[0:2]:
            try:
                method_args['direction'] = float(key[2:])
            except Exception:
                raise ParserError('[31m[ParserError]:[0m Unrecognized switch method: "'+method_name+'" appeared in dialogue line ' + str(i+1)+'.')
        else:
            try:
                method_args['scale'] = int(key)
            except Exception:
                raise ParserError('[31m[ParserError]:[0m Unrecognized switch method: "'+method_name+'" appeared in dialogue line ' + str(i+1)+'.')
    # 切入，切出，或者双端
    cutin,cutout ={'in':(1,0),'out':(0,1),'both':(1,1)}[method_args['cut']]
    # alpha
    if method_args['alpha'] == 'replace': #--
        alpha_timeline = np.hstack(np.ones(this_duration)) # replace的延后功能撤销！
    elif method_args['alpha'] == 'delay': #_-
        alpha_timeline = np.hstack([np.zeros(method_dur),np.ones(this_duration-method_dur)]) # 延后功能
    else: # method_args['alpha'] == 'black':#>1<
        alpha_timeline = np.hstack([dynamic(1,method_dur,1,1,cutin),np.ones(this_duration-2*method_dur),dynamic(1,method_dur,1,0,cutout)])
    # static 的提前终止
    if method_args['motion'] == 'static':
        pos_timeline = 'NA'
        return alpha_timeline,pos_timeline
    
    # direction
    try:
        theta = np.deg2rad(direction_dic[method_args['direction']])
    except Exception: # 设定为角度
        theta = np.deg2rad(method_args['direction'])
    # scale
    if method_args['scale'] in ['major','minor','entire']: #上下绑定屏幕高度，左右绑定屏幕宽度*scale_dic[method_args['scale']]
        method_args['scale'] = ((np.cos(theta)*Height)**2+(np.sin(theta)*Width)**2)**(1/2)*scale_dic[method_args['scale']]
    else: # 指定了scale
        pass
    # motion
    if method_args['motion'] == 'pass': # >0>
        D1 = np.hstack([dynamic(method_args['scale']*np.sin(theta),method_dur,0,1,cutin),
                        np.zeros(this_duration-2*method_dur),
                        dynamic(-method_args['scale']*np.sin(theta),method_dur,0,0,cutout)])
        D2 = np.hstack([dynamic(method_args['scale']*np.cos(theta),method_dur,0,1,cutin),
                        np.zeros(this_duration-2*method_dur),
                        dynamic(-method_args['scale']*np.cos(theta),method_dur,0,0,cutout)])
    elif method_args['motion'] == 'leap': # >0<
        D1 = np.hstack([dynamic(method_args['scale']*np.sin(theta),method_dur,0,1,cutin),
                        np.zeros(this_duration-2*method_dur),
                        dynamic(method_args['scale']*np.sin(theta),method_dur,0,0,cutout)])
        D2 = np.hstack([dynamic(method_args['scale']*np.cos(theta),method_dur,0,1,cutin),
                        np.zeros(this_duration-2*method_dur),
                        dynamic(method_args['scale']*np.cos(theta),method_dur,0,0,cutout)])
    # 实验性质的功能，想必不可能真的有人用这么鬼畜的效果吧
    elif method_args['motion'] == 'circular': 
        theta_timeline = (
            np
            .repeat(formula(0-theta,2*np.pi-theta,method_dur),np.ceil(this_duration/method_dur).astype(int))
            .reshape(method_dur,np.ceil(this_duration/method_dur).astype(int))
            .transpose().ravel())[0:this_duration]
        D1 = np.sin(theta_timeline)*method_args['scale']
        D2 = -np.cos(theta_timeline)*method_args['scale']
    else:
        pos_timeline = 'NA'
        return alpha_timeline,pos_timeline
    pos_timeline = concat_xy(D1,D2)
    return alpha_timeline,pos_timeline

# 解析函数
def parser(stdin_text):
    # 断点
    global formula
    break_point = pd.Series(index=range(0,len(stdin_text)),dtype=int)
    break_point[0]=0
    # 视频+音轨 时间轴
    render_timeline = []
    BGM_queue = []
    this_background = "black"
    # 内建的媒体，主要指BIA
    bulitin_media = {}

    for i,text in enumerate(stdin_text):
        # 空白行
        if text == '':
            break_point[i+1]=break_point[i]
            continue
        # 注释行 格式： # word
        elif text[0] == '#':
            break_point[i+1]=break_point[i]
            continue
        # 对话行 格式： [角色1,角色2(30).happy]<replace=30>:巴拉#巴拉#巴拉<w2w=1>
        elif text[0] == '[':
            try:
                # 从ts长度预设的 this_duration
                this_charactor,this_duration,am_method,am_dur,bb_method,bb_dur,ts,text_method,text_dur,this_sound = get_dialogue_arg(text)
                # a 1.3 从音频中加载持续时长 {SE1;*78} 注意，这里只需要载入星标时间，检查异常不在这里做：
                asterisk_timeset = RE_asterisk.findall('\t'.join(this_sound)) #在音频标志中读取
                if len(asterisk_timeset) == 0:  #没检测到星标
                    pass
                elif len(asterisk_timeset) == 1: #检查到一个星标
                    try:
                        asterisk_time = float(asterisk_timeset[0][-1]) #取第二个，转化为浮点数
                        this_duration = asterisk_pause + np.ceil((asterisk_time)*frame_rate).astype(int) # a1.4.3 添加了句间停顿
                    except Exception:
                        print('[33m[warning]:[0m','Failed to load asterisk time in dialogue line ' + str(i+1)+'.')
                else: #检测到复数个星标
                    raise ParserError('[31m[ParserError]:[0m Too much asterisk time labels are set in dialogue line ' + str(i+1)+'.')

                # 确保时长不短于切换特效时长
                if this_duration<(2*max(am_dur,bb_dur)+1):
                    this_duration = 2*max(am_dur,bb_dur)+1

                # 建立本小节的timeline文件
                this_timeline=pd.DataFrame(index=range(0,this_duration),dtype=str,columns=render_arg)
                this_timeline['BG1'] = this_background
                this_timeline['BG1_a'] = 100
                # 载入切换效果
                alpha_timeline_A,pos_timeline_A = am_methods(am_method,am_dur,this_duration,i)
                alpha_timeline_B,pos_timeline_B = am_methods(bb_method,bb_dur,this_duration,i)
                #各个角色：
                if len(this_charactor) > 3:
                    raise ParserError('[31m[ParserError]:[0m Too much charactor is specified in dialogue line ' + str(i+1)+'.')
                for k,charactor in enumerate(this_charactor[0:3]):
                    name,alpha,subtype= charactor
                    # 处理空缺参数
                    if subtype == '':
                        subtype = '.default'
                    if alpha == '':
                        alpha = -1
                    else:
                        alpha = int(alpha[1:-1])
                    # 立绘的参数
                    try:
                        this_am = charactor_table.loc[name+subtype]['Animation']
                        this_timeline['Am'+str(k+1)] = this_am
                    except Exception as E: # 在角色表里面找不到name，raise在这里！
                        raise ParserError('[31m[ParserError]:[0m Undefined Name '+ name+subtype +' in dialogue line ' + str(i+1)+'. due to:',E)
                    # 动画的参数
                    if (this_am!=this_am) | (this_am=='NA'):# this_am 可能为空的，需要先处理这种情况！
                        this_timeline['Am'+str(k+1)+'_t'] = 0
                    else:
                        try:
                            this_timeline['Am'+str(k+1)+'_t'] = eval('{am}.get_tick({dur})'.format(am=this_am,dur=this_duration))
                        except NameError as E: # 指定的am没有定义！
                            raise ParserError('[31m[ParserError]:[0m',E,', which is specified to',name+subtype,'as Animation!')
                    # 检查气泡文本的可用性 alpha 1.8.4
                    if ('"' in name) | ('\\' in name) | ('"' in ts) | ('\\' in ts):
                        raise ParserError('[31m[ParserError]:[0m','Invalid symbol (double quote or backslash) appeared in speech text in dialogue line ' + str(i+1)+'.')
                    # 气泡的参数
                    if k == 0:
                        this_bb = charactor_table.loc[name+subtype]['Bubble']
                        if (this_bb!=this_bb) | (this_bb=='NA'): # 主要角色一定要有bubble！，次要的可用没有
                            raise ParserError('[31m[ParserError]:[0m','No bubble is specified to major charactor',name+subtype,'of dialogue line '+str(i+1)+'.')
                        this_timeline['Bb'] = charactor_table.loc[name+subtype]['Bubble'] # 异常处理，未定义的名字
                        this_timeline['Bb_main'] = ts
                        this_timeline['Bb_header'] = name
                        this_timeline['Bb_a'] = alpha_timeline_B*100
                        this_timeline['Bb_p'] = pos_timeline_B
                    #透明度参数
                    if (alpha >= 0)&(alpha <= 100): # alpha 1.8.8 如果有指定合法的透明度，则使用指定透明度
                        this_timeline['Am'+str(k+1)+'_a']=alpha_timeline_A*alpha
                    else: # 如果没有指定透明度
                        if k == 0: # 如果是首要角色，透明度为100
                            this_timeline['Am'+str(k+1)+'_a']=alpha_timeline_A*100
                        else: # 如果是次要角色，透明度为secondary_alpha，默认值60
                            this_timeline['Am'+str(k+1)+'_a']=alpha_timeline_A*secondary_alpha 
                    # 位置时间轴信息
                    this_timeline['Am'+str(k+1)+'_p'] = pos_timeline_A
    
                # 针对文本内容的警告
                try:
                    this_line_limit = eval(this_timeline['Bb'][0]+'.MainText.line_limit') #获取行长，用来展示各类警告信息
                    if (len(ts)>this_line_limit*4) | (len(ts.split('#'))>4): #行数过多的警告
                        print('[33m[warning]:[0m','More than 4 lines will be displayed in dialogue line ' + str(i+1)+'.')
                    if ((ts[0]=='^')|('#' in ts))&(np.frompyfunc(len,1,1)(ts.replace('^','').split('#')).max()>this_line_limit): # 手动换行的字数超限的警告
                        print('[33m[warning]:[0m','Manual break line length exceed the Bubble line_limit in dialogue line ' + str(i+1)+'.') #alpha1.6.3
                except AttributeError: # 'NoneType' object has no attribute 'line_limit'
                    raise ParserError('[31m[ParserError]:[0m','Main_Text of "{0}" is None!'.format(this_timeline['Bb'][0]))
                except NameError as E: # 指定的bb没有定义！
                    raise ParserError('[31m[ParserError]:[0m',E,', which is specified to',name+subtype,'as Bubble!')
                # 文字显示的参数
                if text_method == 'all':
                    if text_dur == 0:
                        pass
                    else:
                        this_timeline.loc[0:text_dur,'Bb_main'] = '' #将前n帧的文本设置为空白
                elif text_method == 'w2w':
                    word_count_timeline = np.arange(0,this_duration,1)//text_dur+1
                    this_timeline['Bb_main'] = UF_cut_str(this_timeline['Bb_main'],word_count_timeline)
                elif text_method == 'l2l': 
                    if ((ts[0]=='^')|('#' in ts)): #如果是手动换行的列
                        word_count_timeline = get_l2l(ts,text_dur,this_duration) # 不保证稳定呢！
                    else:
                        line_limit = eval(this_timeline['Bb'][1]+'.MainText.line_limit') #获取主文本对象的line_limit参数
                        word_count_timeline = (np.arange(0,this_duration,1)//(text_dur*line_limit)+1)*line_limit
                    this_timeline['Bb_main'] = UF_cut_str(this_timeline['Bb_main'],word_count_timeline)
                else:
                    raise ParserError('[31m[ParserError]:[0m Unrecognized text display method: "'+text_method+'" appeared in dialogue line ' + str(i+1)+'.')
                #音频信息
                if BGM_queue != []:
                    this_timeline.loc[0,'BGM'] = BGM_queue.pop() #从BGM_queue里取出来一个
                for sound in this_sound: #this_sound = ['{SE_obj;30}','{SE_obj;30}']
                    try:
                        se_obj,delay = sound[1:-1].split(';')#sound = '{SE_obj;30}'
                    except Exception: # #sound = '{SE_obj}'
                        delay = '0'
                        se_obj = sound[1:-1] # 去掉花括号
                    if delay == '':
                        delay = 0
                    elif '*' in delay: # 如果是星标时间 delay 是asterisk_pause的一半
                        delay = int(asterisk_pause/2)
                    elif int(delay) >= this_duration: # delay 不能比一个单元还长
                        delay = this_duration-1
                    else:
                        delay = int(delay)
                    if '*' in se_obj:
                        raise ParserError('[31m[ParserError]:[0m Unprocessed asterisk time label appeared in dialogue line ' + str(i+1) + '. Add --SynthesisAnyway may help.')
                    if se_obj in media_list: # 如果delay在媒体里已经定义，则视为SE
                        this_timeline.loc[delay,'SE'] = se_obj
                    elif os.path.isfile(se_obj[1:-1]) == True: #或者指向一个确定的文件，则视为语音
                        this_timeline.loc[delay,'Voice'] = se_obj
                    elif se_obj in ['NA','']: # 如果se_obj是空值或NA，则什么都不做 alpha1.8.5
                        pass
                    else:
                        raise ParserError('[31m[ParserError]:[0m The sound effect "'+se_obj+'" specified in dialogue line ' + str(i+1)+' is not exist!')
                this_timeline['section'] = i
                render_timeline.append(this_timeline)
                break_point[i+1]=break_point[i]+this_duration
                continue
            except Exception as E:
                print(E)
                raise ParserError('[31m[ParserError]:[0m Parse exception occurred in dialogue line ' + str(i+1)+'.')
                continue
        # 背景设置行，格式： <background><black=30>:BG_obj
        elif '<background>' in text:
            try:
                bgc,method,method_dur = get_background_arg(text)
                if bgc in media_list: # 检查是否是已定义的对象
                    next_background=bgc
                else:
                    raise ParserError('[31m[ParserError]:[0m The background "'+bgc+'" specified in background line ' + str(i+1)+' is not defined!')
                if method=='replace': #replace 改为立刻替换 并持续n秒
                    this_timeline=pd.DataFrame(index=range(0,method_dur),dtype=str,columns=render_arg)
                    this_timeline['BG1']=next_background
                    this_timeline['BG1_a']=100
                elif method=='delay': # delay 等价于原来的replace，延后n秒，然后替换
                    this_timeline=pd.DataFrame(index=range(0,method_dur),dtype=str,columns=render_arg)
                    this_timeline['BG1']=this_background
                    this_timeline['BG1_a']=100
                elif method in ['cross','black','white','push','cover']: # 交叉溶解，黑场，白场，推，覆盖
                    this_timeline=pd.DataFrame(index=range(0,method_dur),dtype=str,columns=render_arg)
                    this_timeline['BG1']=next_background
                    this_timeline['BG2']=this_background
                    if method in ['black','white']:
                        this_timeline['BG3']=method
                        this_timeline['BG1_a']=formula(-100,100,method_dur)
                        this_timeline['BG1_a']=this_timeline['BG1_a'].map(alpha_range)
                        this_timeline['BG2_a']=formula(100,-100,method_dur)
                        this_timeline['BG2_a']=this_timeline['BG2_a'].map(alpha_range)
                        this_timeline['BG3_a']=100
                    elif method == 'cross':
                        this_timeline['BG1_a']=formula(0,100,method_dur)
                        this_timeline['BG2_a']=100
                    elif method in ['push','cover']:
                        this_timeline['BG1_a']=100
                        this_timeline['BG2_a']=100
                        if method == 'push': # 新背景从右侧把旧背景推出去
                            this_timeline['BG1_p'] = concat_xy(formula(screen_size[0],0,method_dur),np.zeros(method_dur))
                            this_timeline['BG2_p'] = concat_xy(formula(0,-screen_size[0],method_dur),np.zeros(method_dur))
                        else: #cover 新背景从右侧进来叠在原图上面
                            this_timeline['BG1_p'] = concat_xy(formula(screen_size[0],0,method_dur),np.zeros(method_dur))
                            this_timeline['BG2_p'] = 'NA'
                else:
                    raise ParserError('[31m[ParserError]:[0m Unrecognized switch method: "'+method+'" appeared in background line ' + str(i+1)+'.')
                this_background = next_background #正式切换背景
                this_timeline['section'] = i
                render_timeline.append(this_timeline)
                break_point[i+1]=break_point[i]+len(this_timeline.index)
                continue
            except Exception as E:
                print(E)
                raise ParserError('[31m[ParserError]:[0m Parse exception occurred in background line ' + str(i+1)+'.')
                continue
        # 参数设置行，格式：<set:speech_speed>:220
        elif ('<set:' in text) & ('>:' in text):
            try:
                target,args = get_seting_arg(text)
                if target in ['am_dur_default','bb_dur_default','bg_dur_default','tx_dur_default','speech_speed','asterisk_pause','secondary_alpha']:
                    try: 
                        args = int(args) #如果args是整数值型
                        if args < 0:
                            raise ParserError('invalid args')
                    except Exception:
                        print('[33m[warning]:[0m','Setting',target,'to invalid value',args,',the argument will not changed.')
                        args = eval(target) # 保持原数值不变
                    exec("global {0} ; {0} = {1}".format(target,str(args)))
                elif target in ['am_method_default','bb_method_default','bg_method_default','tx_method_default']:
                    exec("global {0} ; {0} = {1}".format(target,'\"'+args+'\"')) # 当作文本型，无论是啥都接受
                elif target == 'BGM':
                    if args in media_list:
                        BGM_queue.append(args)
                    elif os.path.isfile(args[1:-1]):
                        BGM_queue.append(args)
                    elif args == 'stop':
                        BGM_queue.append(args)
                    else:
                        raise ParserError('[31m[ParserError]:[0m The BGM "'+args+'" specified in setting line ' + str(i+1)+' is not exist!')
                elif target == 'formula':
                    if args in formula_available.keys():
                        formula = formula_available[args]
                    elif args[0:6] == 'lambda':
                        try:
                            formula = eval(args)
                            print('[33m[warning]:[0m','Using lambda formula range ',formula(0,1,2),
                                  ' in line',str(i+1),', which may cause unstableness during displaying!')                            
                        except Exception:
                            raise ParserError('[31m[ParserError]:[0m Unsupported formula "'+args+'" is specified in setting line ' + str(i+1)+'.')
                    else:
                        raise ParserError('[31m[ParserError]:[0m Unsupported formula "'+args+'" is specified in setting line ' + str(i+1)+'.')
                else:
                    raise ParserError('[31m[ParserError]:[0m Unsupported setting "'+target+'" is specified in setting line ' + str(i+1)+'.')
                    continue
            except Exception as E:
                print(E)
                raise ParserError('[31m[ParserError]:[0m Parse exception occurred in setting line ' + str(i+1)+'.')
                continue
        # 预设动画，损失生命
        elif text[0:11]=='<hitpoint>:':
            try:
                # 载入参数
                name_tx,heart_max,heart_begin,heart_end = RE_hitpoint.findall(text)[0]
                heart_max = int(heart_max)
                heart_begin = int(heart_begin)
                heart_end = int(heart_end)
                # 建立小节
                this_timeline=pd.DataFrame(index=range(0,frame_rate*4),dtype=str,columns=render_arg)
                # 背景
                #alpha_timeline,pos_timeline = am_methods('black',method_dur=frame_rate//2,this_duration=frame_rate*4,i=i)
                alpha_timeline = np.hstack([formula(0,1,frame_rate//2),np.ones(frame_rate*3-frame_rate//2),formula(1,0,frame_rate)])
                this_timeline['BG1'] = 'black' # 黑色背景
                this_timeline['BG1_a'] = alpha_timeline * 80
                this_timeline['BG2'] = this_background
                this_timeline['BG2_a'] = 100
                # 新建内建动画
                Auto_media_name = 'BIA_'+str(i+1)
                code_to_run = 'global {media_name}_{layer} ;{media_name}_{layer} = BuiltInAnimation(anime_type="hitpoint",anime_args=("{name}",{hmax},{hbegin},{hend}),screensize = {screensize},layer={layer})'
                code_to_run_0 = code_to_run.format(media_name=Auto_media_name,name=name_tx,hmax='%d'%heart_max,hbegin='%d'%heart_begin,hend='%d'%heart_end,screensize=str(screen_size),layer='0')
                code_to_run_1 = code_to_run.format(media_name=Auto_media_name,name=name_tx,hmax='%d'%heart_max,hbegin='%d'%heart_begin,hend='%d'%heart_end,screensize=str(screen_size),layer='1')
                code_to_run_2 = code_to_run.format(media_name=Auto_media_name,name=name_tx,hmax='%d'%heart_max,hbegin='%d'%heart_begin,hend='%d'%heart_end,screensize=str(screen_size),layer='2')
                exec(code_to_run_0) # 灰色框
                exec(code_to_run_1) # 留下的血
                exec(code_to_run_2) # 丢掉的血
                media_list.append(Auto_media_name+'_0')
                media_list.append(Auto_media_name+'_1')
                media_list.append(Auto_media_name+'_2')
                bulitin_media[Auto_media_name+'_0'] = code_to_run_0
                bulitin_media[Auto_media_name+'_1'] = code_to_run_1
                bulitin_media[Auto_media_name+'_2'] = code_to_run_2
                # 动画参数
                this_timeline['Am3'] = Auto_media_name+'_0'
                this_timeline['Am3_a'] = alpha_timeline * 100
                this_timeline['Am3_t'] = 0
                this_timeline['Am3_p'] = 'NA'
                this_timeline['Am2'] = Auto_media_name+'_1'
                this_timeline['Am2_a'] = alpha_timeline * 100
                this_timeline['Am2_t'] = 0
                this_timeline['Am2_p'] = 'NA'
                this_timeline['Am1'] = Auto_media_name+'_2'
    
                if heart_begin > heart_end: # 掉血模式
                    this_timeline['Am1_a'] = np.hstack([formula(0,100,frame_rate//2),
                                                        np.ones(frame_rate*2-frame_rate//2)*100,
                                                        left(100,0,frame_rate//2),
                                                        np.zeros(frame_rate*2-frame_rate//2)]) #0-0.5出现，2-2.5消失
                    this_timeline['Am1_p'] = concat_xy(np.zeros(frame_rate*4),
                                                       np.hstack([np.zeros(frame_rate*2), # 静止2秒
                                                                  left(0,-int(screen_size[1]*0.3),frame_rate//2), # 半秒切走
                                                                  int(screen_size[1]*0.3)*np.ones(frame_rate*2-frame_rate//2)])) #1.5秒停止
                    this_timeline['Am1_t'] = 0
                else: # 回血模式
                    this_timeline['Am1_a'] = alpha_timeline * 100 # 跟随全局血量
                    this_timeline['Am1_p'] = 'NA' # 不移动
                    this_timeline['Am1_t'] = np.hstack([np.zeros(frame_rate*1), # 第一秒静止
                                                        np.arange(0,frame_rate,1), # 第二秒播放
                                                        np.ones(frame_rate*2)*(frame_rate-1)]) # 后两秒静止
                # 收尾
                if BGM_queue != []:
                    this_timeline.loc[0,'BGM'] = BGM_queue.pop() #从BGM_queue里取出来一个 alpha 1.8.5
                this_timeline['section'] = i
                render_timeline.append(this_timeline)
                break_point[i+1]=break_point[i]+len(this_timeline.index)
                continue
            except Exception as E:
                print(E)
                raise ParserError('[31m[ParserError]:[0m Parse exception occurred in hitpoint line ' + str(i+1)+'.')
                continue
        # 预设动画，骰子
        elif text[0:7]=='<dice>:':
            try:
                # 获取参数
                dice_args = RE_dice.findall(text[7:])
                if len(dice_args) == 0:
                    raise ParserError('[31m[ParserError]:[0m','Invalid syntax, no dice args is specified!')
                # 建立小节
                this_timeline=pd.DataFrame(index=range(0,frame_rate*5),dtype=str,columns=render_arg) # 5s
                # 背景
                alpha_timeline = np.hstack([formula(0,1,frame_rate//2),np.ones(frame_rate*4-frame_rate//2),formula(1,0,frame_rate)])
                this_timeline['BG1'] = 'black' # 黑色背景
                this_timeline['BG1_a'] = alpha_timeline * 80
                this_timeline['BG2'] = this_background
                this_timeline['BG2_a'] = 100
                # 新建内建动画
                Auto_media_name = 'BIA_'+str(i+1)
                code_to_run = 'global {media_name}_{layer} ;{media_name}_{layer} = BuiltInAnimation(anime_type="dice",anime_args={dice_args},screensize = {screensize},layer={layer})'
                code_to_run_0 = code_to_run.format(media_name=Auto_media_name,dice_args=str(dice_args),screensize=str(screen_size),layer='0')
                code_to_run_1 = code_to_run.format(media_name=Auto_media_name,dice_args=str(dice_args),screensize=str(screen_size),layer='1')
                code_to_run_2 = code_to_run.format(media_name=Auto_media_name,dice_args=str(dice_args),screensize=str(screen_size),layer='2')
                exec(code_to_run_0) # 描述和检定值
                exec(code_to_run_1) # 老虎机
                exec(code_to_run_2) # 输出结果
                media_list.append(Auto_media_name+'_0')
                media_list.append(Auto_media_name+'_1')
                media_list.append(Auto_media_name+'_2')
                bulitin_media[Auto_media_name+'_0'] = code_to_run_0
                bulitin_media[Auto_media_name+'_1'] = code_to_run_1
                bulitin_media[Auto_media_name+'_2'] = code_to_run_2
                # 动画参数0
                this_timeline['Am3'] = Auto_media_name+'_0'
                this_timeline['Am3_a'] = alpha_timeline * 100
                this_timeline['Am3_t'] = 0
                this_timeline['Am3_p'] = 'NA'
                # 1
                this_timeline['Am2'] = np.hstack([np.repeat(Auto_media_name+'_1',int(frame_rate*2.5)),np.repeat('NA',frame_rate*5-int(frame_rate*2.5))]) # 2.5s
                this_timeline['Am2_a'] = np.hstack([formula(0,100,frame_rate//2),
                                                    np.ones(int(frame_rate*2.5)-2*(frame_rate//2))*100,
                                                    formula(100,0,frame_rate//2),
                                                    np.zeros(frame_rate*5-int(frame_rate*2.5))])
                this_timeline['Am2_t'] = np.hstack([np.arange(0,int(frame_rate*2.5)),np.zeros(frame_rate*5-int(frame_rate*2.5))])
                this_timeline['Am2_p'] = 'NA'
                # 2
                this_timeline['Am1'] = np.hstack([np.repeat('NA',frame_rate*5-int(frame_rate*2.5)),np.repeat(Auto_media_name+'_2',int(frame_rate*2.5))])
                this_timeline['Am1_a'] = np.hstack([np.zeros(frame_rate*5-int(frame_rate*2.5)),
                                                    formula(0,100,frame_rate//2),
                                                    np.ones(int(frame_rate*2.5)-frame_rate//2-frame_rate)*100,
                                                    formula(100,0,frame_rate)])
                this_timeline['Am1_t'] = 0
                this_timeline['Am1_p'] = 'NA'
                # SE
                this_timeline.loc[frame_rate//3,'SE'] = "'./media/SE_dice.wav'"
                # 收尾
                if BGM_queue != []:
                    this_timeline.loc[0,'BGM'] = BGM_queue.pop() #从BGM_queue里取出来一个 alpha 1.8.5
                this_timeline['section'] = i
                render_timeline.append(this_timeline)
                break_point[i+1]=break_point[i]+len(this_timeline.index)
                continue
            except Exception as E:
                print(E)
                raise ParserError('[31m[ParserError]:[0m Parse exception occurred in dice line ' + str(i+1)+'.')
                continue
        # 异常行，报出异常
        else:
            raise ParserError('[31m[ParserError]:[0m Unrecognized line: '+ str(i+1)+'.')
        break_point[i+1]=break_point[i]
        
    render_timeline = pd.concat(render_timeline,axis=0)
    render_timeline.index = np.arange(0,len(render_timeline),1)
    render_timeline = render_timeline.fillna('NA') #假设一共10帧
    timeline_diff = render_timeline.iloc[:-1].copy() #取第0-9帧
    timeline_diff.index = timeline_diff.index+1 #设置为第1-10帧
    timeline_diff.loc[0]='NA' #再把第0帧设置为NA
    dropframe = (render_timeline == timeline_diff.sort_index()).all(axis=1) # 这样，就是原来的第10帧和第9帧在比较了
    bulitin_media = pd.Series(bulitin_media,dtype=str)
    break_point = break_point.astype(int) # breakpoint 数据类型改为整数
    # 这样就去掉了，和前一帧相同的帧，节约了性能
    return render_timeline[dropframe == False].copy(),break_point,bulitin_media

# 渲染函数
def render(this_frame):
    global zorder,media_list
    for layer in zorder:
        # 不渲染的条件：图层为"Na"，或者np.nan
        if (this_frame[layer]=='NA')|(this_frame[layer]!=this_frame[layer]):
            continue
        elif this_frame[layer+'_a']<=0: #或者图层的透明度小于等于0(由于fillna("NA"),出现的异常)
            continue
        elif this_frame[layer] not in media_list:
            raise RuntimeError('[31m[RenderError]:[0m Undefined media object : "'+this_frame[layer]+'".')
            continue
        elif layer[0:2] == 'BG':
            try:
                exec('{0}.display(surface=screen,alpha={1},adjust={2})'.format(this_frame[layer],this_frame[layer+'_a'],'\"'+this_frame[layer+'_p']+'\"'))
            except Exception:
                raise RuntimeError('[31m[RenderError]:[0m Failed to render "'+this_frame[layer]+'" as Background.')
        elif layer[0:2] == 'Am': # 兼容H_LG1(1)这种动画形式 alpha1.6.3
            try:
                exec('{0}.display(surface=screen,alpha={1},adjust={2},frame={3})'.format(
                                                                                         this_frame[layer],
                                                                                         this_frame[layer+'_a'],
                                                                                         '\"'+this_frame[layer+'_p']+'\"',
                                                                                         this_frame[layer+'_t']))
            except Exception:
                raise RuntimeError('[31m[RenderError]:[0m Failed to render "'+this_frame[layer]+'" as Animation.')
        elif layer == 'Bb':
            try:
                exec('{0}.display(surface=screen,text={2},header={3},alpha={1},adjust={4})'.format(this_frame[layer],
                                                                                                   this_frame[layer+'_a'],
                                                                                                   '\"'+this_frame[layer+'_main']+'\"',
                                                                                                   '\"'+this_frame[layer+'_header']+'\"',
                                                                                                   '\"'+this_frame[layer+'_p']+'\"'))
            except Exception:
                raise RuntimeError('[31m[RenderError]:[0m Failed to render "'+this_frame[layer]+'" as Bubble.')
    for key in ['BGM','Voice','SE']:
        if (this_frame[key]=='NA')|(this_frame[key]!=this_frame[key]): #如果是空的
            continue
        elif this_frame[key] == 'stop': # a 1.6.0更新
            pygame.mixer.music.stop() #停止
            pygame.mixer.music.unload() #换碟
        elif (this_frame[key] not in media_list): #不是预先定义的媒体，则一定是合法的路径
            if key == 'BGM':
                temp_BGM = BGM(filepath=this_frame[key][1:-1])
                temp_BGM.display()
            else:
                temp_Audio = Audio(filepath=this_frame[key][1:-1])
                temp_Audio.display(channel=eval(channel_list[key]))#这里的参数需要是对象
        else: # 预先定义的媒体
            try:
                if key == 'BGM':
                    exec('{0}.display()'.format(this_frame[key])) #否则就直接播放对象
                else:
                    exec('{0}.display(channel={1})'.format(this_frame[key],channel_list[key])) #否则就直接播放对象
            except Exception:
                raise RuntimeError('[31m[RenderError]:[0m Failed to play audio "'+this_frame[layer]+'"')
    return 1
# 手动换行的l2l
def get_l2l(ts,text_dur,this_duration): #如果是手动换行的列
    lines = ts.split('#')
    wc_list = []
    len_this = 0
    for x,l in enumerate(lines): #x是井号的数量
        len_this = len_this +len(l)+1 #当前行的长度
        #print(len_this,len(l),x,ts[0:len_this])
        wc_list.append(np.ones(text_dur*len(l))*len_this)
    try:
        wc_list.append(np.ones(this_duration - (len(ts)-x)*text_dur)*len(ts)) #this_duration > est # 1.6.1 update
        word_count_timeline = np.hstack(wc_list)
    except Exception: 
        word_count_timeline = np.hstack(wc_list) # this_duration < est
        word_count_timeline = word_count_timeline[0:this_duration]
    return word_count_timeline.astype(int)

# 倒计时器
def timer(clock):
    global W,H
    white.display(screen)
    screen.blit(note_text.render('%d'%clock,fgcolor=(150,150,150,255),size=0.0926*H)[0],(0.484*W,0.463*H)) # for 1080p
    pygame.display.update()
    pygame.time.delay(1000)

def stop_SE():
    for Ch in channel_list.values():
        exec(Ch+'.stop()')

def pause_SE(stats):
    if stats == 0:
        pygame.mixer.music.pause()
        for Ch in channel_list.values():
            exec(Ch+'.pause()')
    else:
        pygame.mixer.music.unpause()
        for Ch in channel_list.values():
            exec(Ch+'.unpause()')

# Main():

print('[replay generator]: Welcome to use TRPG-replay-generator '+edtion)

# 检查是否需要先做语音合成

if synthfirst == True:
    command = python3 +' ./speech_synthesizer.py --LogFile {lg} --MediaObjDefine {md} --CharacterTable {ct} --OutputPath {of} --AccessKey {AK} --AccessKeySecret {AS} --Appkey {AP}'
    command = command.format(lg = stdin_log.replace('\\','/'),md = media_obj.replace('\\','/'), of = output_path, ct = char_tab.replace('\\','/'), AK = AKID,AS = AKKEY,AP = APPKEY)
    print('[replay generator]: Flag --SynthesisAnyway detected, running command:\n'+'[32m'+command+'[0m')
    try:
        exit_status = os.system(command)
        # 如果是正常退出，将当前的标准输入调整为处理后的log文件
        if (exit_status == 0)&(os.path.isfile(output_path+'/AsteriskMarkedLogFile.txt') == True):
            stdin_log = output_path+'/AsteriskMarkedLogFile.txt'
        else:
            raise OSError('Exception above')
    except Exception as E:
        print('[33m[warning]:[0m Failed to synthesis speech, due to:',E)

# 载入od文件
print('[replay generator]: Loading media definition file.')

try:
    object_define_text = open(media_obj,'r',encoding='utf-8').read()#.split('\n') # 修改后的逻辑
except UnicodeDecodeError as E:
    print('[31m[DecodeError]:[0m',E)
    system_terminated('Error')
if object_define_text[0] == '\ufeff': # UTF-8 BOM
    print('[33m[warning]:[0m','UTF8 BOM recognized in MediaDef, it will be drop from the begin of file!')
    object_define_text = object_define_text[1:] # 去掉首位
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
            print(E)
            print('[31m[SyntaxError]:[0m "'+text+'" appeared in media define file line ' + str(i+1)+' is invalid syntax:')
            system_terminated('Error')
black = Background('black')
white = Background('white')
media_list.append('black')
media_list.append('white')

# 载入ct文件
print('[replay generator]: Loading charactor table.')

try:
    if char_tab.split('.')[-1] in ['xlsx','xls']:
        charactor_table = pd.read_excel(char_tab,dtype = str) # 支持excel格式的角色配置表
    else:
        charactor_table = pd.read_csv(char_tab,sep='\t',dtype = str)
    charactor_table.index = charactor_table['Name']+'.'+charactor_table['Subtype']
    if ('Animation' not in charactor_table.columns) | ('Bubble' not in charactor_table.columns): # 139debug
        raise SyntaxError('missing necessary columns.')
except Exception as E:
    print('[31m[SyntaxError]:[0m Unable to load charactor table:',E)
    system_terminated('Error')

# 载入log文件 parser()
print('[replay generator]: Parsing Log file.')

try:
    stdin_text = open(stdin_log,'r',encoding='utf8').read()#.split('\n')
except UnicodeDecodeError as E:
    print('[31m[DecodeError]:[0m',E)
    system_terminated('Error')
if stdin_text[0] == '\ufeff': # 139 debug # 除非是完全空白的文件
    print('[33m[warning]:[0m','UTF8 BOM recognized in Logfile, it will be drop from the begin of file!')
    stdin_text = stdin_text[1:]
stdin_text = stdin_text.split('\n')
try:
    render_timeline,break_point,bulitin_media = parser(stdin_text)
except ParserError as E:
    print(E)
    system_terminated('Error')

# 判断是否指定输出路径，准备各种输出选项
if output_path != None:
    print('[replay generator]: The timeline and breakpoint file will be save at '+output_path)
    timenow = '%d'%time.time()
    render_timeline.to_pickle(output_path+'/'+timenow+'.timeline')
    break_point.to_pickle(output_path+'/'+timenow+'.breakpoint')
    bulitin_media.to_pickle(output_path+'/'+timenow+'.bulitinmedia')
    if exportXML == True:
        command = python3 + ' ./export_xml.py --TimeLine {tm} --MediaObjDefine {md} --OutputPath {of} --FramePerSecond {fps} --Width {wd} --Height {he} --Zorder {zd}'
        command = command.format(tm = output_path+'/'+timenow+'.timeline',
                                 md = media_obj.replace('\\','/'), of = output_path.replace('\\','/'), 
                                 fps = frame_rate, wd = screen_size[0], he = screen_size[1], zd = ','.join(zorder))
        print('[replay generator]: Flag --ExportXML detected, running command:\n'+'[32m'+command+'[0m')
        try:
            exit_status = os.system(command)
            if exit_status != 0:
                raise OSError('Major error occurred in export_xml!')
        except Exception as E:
            print('[33m[warning]:[0m Failed to export XML, due to:',E)
    if exportVideo == True:
        command = python3 + ' ./export_video.py --TimeLine {tm} --MediaObjDefine {md} --OutputPath {of} --FramePerSecond {fps} --Width {wd} --Height {he} --Zorder {zd} --Quality {ql}'
        command = command.format(tm = output_path+'/'+timenow+'.timeline',
                                 md = media_obj.replace('\\','/'), of = output_path.replace('\\','/'), 
                                 fps = frame_rate, wd = screen_size[0], he = screen_size[1], zd = ','.join(zorder),ql = crf)
        print('[replay generator]: Flag --ExportVideo detected, running command:\n'+'[32m'+command+'[0m')
        try:
            exit_status = os.system(command)
            if exit_status != 0:
                raise OSError('Major error occurred in export_video!')
        except Exception as E:
            print('[33m[warning]:[0m Failed to export Video, due to:',E)
        system_terminated('Video') # 如果导出为视频，则提前终止程序

# 初始化界面

if fixscreen == True:
    try:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware() #修复错误的缩放，尤其是在移动设备。
    except Exception:
        print('[33m[warning]:[0m OS exception, --FixScreenZoom is only avaliable on windows system!')

pygame.init()
pygame.display.set_caption('TRPG Replay Generator '+edtion)
fps_clock=pygame.time.Clock()
screen = pygame.display.set_mode(screen_size)
pygame.display.set_icon(pygame.image.load('./media/icon.ico'))
note_text = pygame.freetype.Font('./media/SourceHanSansCN-Regular.otf')

# 建立音频轨道
VOICE = pygame.mixer.Channel(1)
SOUEFF = pygame.mixer.Channel(2)
channel_list = {'Voice':'VOICE','SE':'SOUEFF'}

# 转换媒体对象
for media in media_list: 
    try:
        exec(media+'.convert()')
    except Exception as E:
        print('[31m[MediaError]:[0m Exception during converting',media,':',E)
        system_terminated('Error')

# 预备画面
W,H = screen_size
white.display(screen)
screen.blit(pygame.transform.scale(pygame.image.load('./media/icon.png'),(H//5,H//5)),(0.01*H,0.79*H))
screen.blit(note_text.render('Welcome to TRPG Replay Generator!',fgcolor=(150,150,150,255),size=0.0315*W)[0],(0.230*W,0.460*H)) # for 1080p
screen.blit(note_text.render(edtion,fgcolor=(150,150,150,255),size=0.0278*H)[0],(0.900*W,0.963*H))
screen.blit(note_text.render('Press space to begin.',fgcolor=(150,150,150,255),size=0.0278*H)[0],(0.417*W,0.926*H))
pygame.display.update()
begin = False
while begin == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            system_terminated('User')
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.time.delay(1000)
                pygame.quit()
                system_terminated('User')
            elif event.key == pygame.K_SPACE:
                begin = True
                break
for s in np.arange(5,0,-1):
    timer(s)

# 主循环
n=0
forward = 1 #forward==0代表暂停
show_detail_info = 0 # show_detail_info == 1代表显示详细信息
detail_info = {0:"Project: Resolution: {0}x{1} ; FrameRate: {2} fps;".format(W,H,frame_rate),
               1:"Render Speed: {0} fps",
               2:"Frame: {0}/"+str(break_point.max())+" ; Section: {1}/"+str(len(break_point)),
               3:"Command: {0}"}
resize_screen = 0 # 是否要强制缩小整个演示窗体
while n < break_point.max():
    ct = time.time()
    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                system_terminated('User')
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_SE()
                    pygame.time.delay(1000)
                    pygame.quit()
                    system_terminated('User')
                elif event.key == pygame.K_a:
                    n=break_point[(break_point-n)<0].max()
                    n=break_point[(break_point-n)<0].max()
                    if n != n: # 确保不会被a搞崩
                        n = 0
                    stop_SE()
                    continue
                elif event.key == pygame.K_d:
                    n=break_point[(break_point-n)>0].min()
                    stop_SE()
                    continue
                elif event.key == pygame.K_F11: # 调整缩放一半
                    from pygame._sdl2.video import Window
                    window = Window.from_display_module()
                    resize_screen = 1 - resize_screen
                    if resize_screen == 1:
                        screen_resized = pygame.display.set_mode((W//2,H//2))
                        screen = pygame.Surface(screen_size,pygame.SRCALPHA)
                        window.position = (100,100)
                    else:
                        screen = pygame.display.set_mode(screen_size)
                        window.position = (0,0)
                    pygame.display.update()
                elif event.key == pygame.K_F5: # 详细信息
                    show_detail_info = 1 - show_detail_info # 1->0 0->1
                elif event.key == pygame.K_SPACE: #暂停
                    forward = 1 - forward # 1->0 0->1
                    pause_SE(forward) # 0:pause,1:unpause
                else:
                    pass
        if n in render_timeline.index:
            this_frame = render_timeline.loc[n]
            render(this_frame)
            if forward == 1: # 如果正在播放
                # 显示详情模式
                if show_detail_info == 1:
                    screen.blit(note_text.render(detail_info[0],fgcolor=cmap['notetext'],size=0.0185*H)[0],(10,10))
                    screen.blit(note_text.render(detail_info[1].format(int(1/(time.time()-ct+1e-4))),fgcolor=cmap['notetext'],size=0.0185*H)[0],(10,10+0.0333*H))
                    screen.blit(note_text.render(detail_info[2].format(n,this_frame['section']+1),fgcolor=cmap['notetext'],size=0.0185*H)[0],(10,10+0.0666*H))
                    screen.blit(note_text.render(detail_info[3].format(stdin_text[this_frame['section']]),fgcolor=cmap['notetext'],size=0.0185*H)[0],(10,10+0.1*H))
                # 仅显示帧率
                else:
                    screen.blit(note_text.render('%d'%(1//(time.time()-ct+1e-4)),fgcolor=cmap['notetext'],size=0.0278*H)[0],(10,10)) ##render rate +1e-4 to avoid float divmod()
            else: # 如果正在暂停
                screen.blit(note_text.render('Press space to continue.',fgcolor=cmap['notetext'],size=0.0278*H)[0],(0.410*W,0.926*H)) # pause
            if resize_screen == 1: # 如果缩放到一半大小
                screen_resized.blit(pygame.transform.scale(screen,(W//2,H//2)),(0,0))
        else:
            pass # 节约算力
        pygame.display.update()
        n = n + forward #下一帧
        fps_clock.tick(frame_rate)
    except RuntimeError as E:
        print(E)
        print('[31m[RenderError]:[0m','Render exception at frame:',n)
        pygame.quit()
        system_terminated('Error')
pygame.quit()
system_terminated('End')
