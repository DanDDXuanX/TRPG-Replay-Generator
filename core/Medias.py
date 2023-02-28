#!/usr/bin/env python
# coding: utf-8

# RplGenCore 涉及的所有媒体类定义

import numpy as np
import pygame
import pydub

from .FilePaths import Filepath
from .FreePos import Pos,FreePos
from .Exceptions import MediaError, WarningPrint
from .Formulas import sigmoid

# 主程序 replay_generator
# 媒体对象，所有媒体类的基类
class MediaObj:
    # 工程分辨率
    screen_size = (1920,1080)
    # 工程帧率
    frame_rate = 30
    # 色图
    cmap = {
        'black':(0,0,0,255),'white':(255,255,255,255),
        'greenscreen':(0,177,64,255),
        'notetext':(118,185,0,255),'empty':(0,0,0,0)
        }
    # 初始化
    def __init__(self,filepath:str,label_color:str) -> None:
        # 文件路径是非法关键字
        if (filepath is None) or (filepath == 'None') or (filepath in self.cmap.keys()):
            self.filepath = None
        # 否则是一个Filepath 对象
        else:
            self.filepath = Filepath(filepath=filepath)
        # 标签颜色
        self.label_color = label_color
    # 缩放图像媒体
    def zoom(self,media:pygame.Surface,scale:float) -> pygame.Surface:
        if scale == 1:
            return media
        elif scale <= 0:
            raise MediaError('InvScale',scale)
        else:
            sizex,sizey = media.get_size()
            target_size = int(sizex * scale),int(sizey * scale)
            return pygame.transform.smoothscale(media,target_size)
    # 转换媒体，仅图像媒体类需要
    def convert(self):
        pass
# 文字对象
class Text(MediaObj):
    pygame.font.init()
    def __init__(self,fontfile:str='./media/SourceHanSansCN-Regular.otf',fontsize:int=40,color:tuple=(0,0,0,255),line_limit:int=20,label_color:str='Lavender'):
        super().__init__(filepath=fontfile,label_color=label_color)
        self.text_render = pygame.font.Font(self.filepath.exact(),fontsize)
        self.color=color
        self.size=fontsize
        self.line_limit = line_limit
    def render(self,tx):
        face = self.text_render.render(tx,True,self.color[0:3])
        if self.color[3] < 255:
            face.set_alpha(self.color[3])
        return face
    # 返回包含了若干行字的列表
    def draw(self,text:str)->list:
        # 气泡的effect含义
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
            ceil_div = lambda x,y: -(-x//y)
            for i in range(0,ceil_div(len(text),self.line_limit)):#较为简单粗暴的自动换行
                out_text.append(self.render(text[i*self.line_limit:(i+1)*self.line_limit]))
        else:
            out_text = [self.render(text)]
        return out_text
# 描边文本
class StrokeText(Text):
    pygame.font.init()
    def __init__(self,fontfile='./media/SourceHanSansCN-Regular.otf',fontsize=40,color=(0,0,0,255),line_limit=20,edge_color=(255,255,255,255),edge_width=1,projection='C',label_color='Lavender'):
        super().__init__(fontfile=fontfile,fontsize=fontsize,color=color,line_limit=line_limit,label_color=label_color) # 继承
        # 描边颜色
        self.edge_color = edge_color
        # 投影方向
        self.dirction_dict = {
            'C' :np.array([ 0, 0]),
            'E' :np.array([ 1, 0]),
            'W' :np.array([-1, 0]),
            'N' :np.array([ 0,-1]),
            'S' :np.array([ 0, 1]),
            'NE':np.array([ 1,-1]),
            'NW':np.array([-1,-1]),
            'SE':np.array([ 1, 1]),
            'SW':np.array([-1, 1]),
        }
        if projection in self.dirction_dict.keys():
            self.dirction = projection
        else:
            self.dirction = 'C'
        # 描边宽度
        try:
            self.edge_width = int(edge_width)
        except ValueError:
            raise MediaError("InvEgWd",edge_width)
        if self.edge_width < 0:
            raise MediaError("InvEgWd",edge_width)
        elif self.edge_width > 3:
            print(WarningPrint('WideEdge'))
        # bug：受限于pygame的性能，无法正确的表现透明度不同的描边和字体，但在导出PR项目时是正常的
        if (self.color[3] < 255) | (self.edge_color[3] < 255):
            print(WarningPrint('AlphaText'))
    def render(self,tx):
        edge = self.text_render.render(tx,True,self.edge_color[0:3])
        face = self.text_render.render(tx,True,self.color[0:3])
        ew = self.edge_width
        # 描边图层
        canvas = pygame.Surface((edge.get_size()[0]+2*ew,edge.get_size()[1]+2*ew),pygame.SRCALPHA)
        # 如果有描边
        if ew > 0:
            # 角
            for pos in [[0,0],[0,2*ew],[2*ew,0],[2*ew,2*ew]]:
                canvas.blit(edge,pos)
            # 边
            for i in range(1,ew*2):
                for pos in [[0,i],[i,0],[2*ew,i],[i,2*ew]]:
                    canvas.blit(edge,pos)
        # 如果没有描边，则直接不放描边
        else:
            pass
        # face图层：在投影模式下，也至少回保留一个像素
        canvas.blit(face,(ew,ew)-self.dirction_dict[self.dirction]*(ew-1))
        # bug：受限于pygame的性能，无法正确的表现透明度不同的描边和字体，但在导出PR项目时是正常的
        if (self.color[3] < 255) | (self.edge_color[3] < 255):
            # 按照透明度的最小值显示
            min_alpha = min(self.color[3],self.edge_color[3])
            canvas.set_alpha(min_alpha)
        return canvas
# 气泡
class Bubble(MediaObj):                                   
    # 初始化
    def __init__(self,filepath=None,scale=1,Main_Text=Text(),Header_Text=None,pos=(0,0),mt_pos=(0,0),ht_pos=(0,0),ht_target='Name',align='left',line_distance=1.5,label_color='Lavender'):
        # 媒体和路径
        super().__init__(filepath=filepath,label_color=label_color)
        if self.filepath is None:
            # 媒体设为空图
            self.media = pygame.Surface(self.screen_size,pygame.SRCALPHA)
            self.media.fill(self.cmap['empty'])
        else:
            self.media = self.zoom(pygame.image.load(self.filepath.exact()),scale=scale)
            self.scale = scale
        # 位置
        if type(pos) in [Pos,FreePos]:
            self.pos = pos
        else:
            self.pos = Pos(*pos)
        # 主文本和头文本
        self.MainText = Main_Text
        self.mt_pos = mt_pos # 只可以是tuple
        self.Header = Header_Text
        self.ht_pos = ht_pos # 只可以是tuple or list tuple
        self.target = ht_target
        # 主文本行距
        if line_distance >= 1:
            self.line_distance = line_distance
        elif line_distance > 0:
            self.line_distance = line_distance # alpha 1.9.2 debug 当linedistance低于1时，忘记初始化line_distance这个参数了
            print(WarningPrint('LineDist'))
        else:
            raise MediaError('ILineDist',line_distance)
        # 主文本对齐
        if align in ('left','center'):
            self.align = align
        else:
            raise MediaError('BadAlign',align)
    def tx_effect(self,main_text:str,effect:float)->str:
        # 效果
        if effect >= 0:
            return main_text[:int(effect)]
        else:
            return main_text
    # 返回一个添加好文字的Bubble Surface
    def draw(self, text:str,header:str='',effect:int=-1)->tuple:
        # 底图
        temp = self.media.copy()
        # 头文本有定义，且输入文本不为空
        if (self.Header!=None) & (header!=''):
            temp.blit(self.Header.draw(header)[0],self.ht_pos)
        # 主文本，应用效果
        x,y = self.mt_pos
        main_text = self.tx_effect(text,effect)
        for i,s in enumerate(self.MainText.draw(main_text)):
            if self.align == 'left':
                temp.blit(s,(x,y+i*self.MainText.size*self.line_distance))
            else: # 就只可能是center了
                word_w,word_h = s.get_size()
                temp.blit(s,(x+(self.MainText.size*self.MainText.line_limit - word_w)//2,y+i*self.MainText.size*self.line_distance))
        return temp,temp.get_size()
    # 将气泡对象丢上主Surface
    def display(self, surface:pygame.surface, text:str, header:str='',effect:int=999,alpha:int=100,center:str='NA',adjust:str='NA'):
        # 中心位置
        if center == 'NA':
            render_center = self.pos
        else:
            render_center = Pos(*eval(center))
        # 校正位置
        if adjust in ['(0,0)','NA']:
            render_pos = render_center
        else:
            render_pos = render_center + eval(adjust)
        # 文本效果：整数：截取字符串的前一部分
        # Bubble Surface
        temp,temp_size = self.draw(text,header,effect)
        # 将Bubble blit 到 surface
        if alpha !=100:
            temp.set_alpha(alpha/100*255)
        surface.blit(temp,render_pos.get())
    # 转换媒体对象
    def convert(self):
        self.media = self.media.convert_alpha()
# 气球
class Balloon(Bubble):
    def __init__(self,filepath=None,scale=1,Main_Text=Text(),Header_Text=[None],pos=(0,0),mt_pos=(0,0),ht_pos=[(0,0)],ht_target=['Name'],align='left',line_distance=1.5,label_color='Lavender'):
        super().__init__(filepath=filepath,scale=scale,Main_Text=Main_Text,Header_Text=Header_Text,pos=pos,mt_pos=mt_pos,ht_pos=ht_pos,ht_target=ht_target,align=align,line_distance=line_distance,label_color=label_color)
        if len(self.Header)!=len(self.ht_pos) or len(self.Header)!=len(self.target):
            raise MediaError('BnHead')
        else:
            self.header_num = len(self.Header)
    # 重载draw
    def draw(self, text:str,header:str='',effect:int=-1)->tuple:
        temp = self.media.copy()
        # 复合header用|作为分隔符
        header_texts = header.split('|')
        for i,header_text_this in enumerate(header_texts):
            # Header 不为None ，且输入文本不为空
            if (self.Header[i]!=None) & (header_text_this!=''):
                temp.blit(self.Header[i].draw(header_text_this)[0],self.ht_pos[i])
            # 如果达到了header数量上限，多余的header_text弃用
            if i == self.header_num -1:
                break
        # 头文本
        main_text = self.tx_effect(text,effect)
        x,y = self.mt_pos
        for i,s in enumerate(self.MainText.draw(main_text)):
            if self.align == 'left':
                temp.blit(s,(x,y+i*self.MainText.size*self.line_distance))
            else: # 就只可能是center了
                word_w,word_h = s.get_size()
                temp.blit(s,(x+(self.MainText.size*self.MainText.line_limit - word_w)//2,y+i*self.MainText.size*self.line_distance))
        return temp,temp.get_size()
# 自适应气泡
class DynamicBubble(Bubble):
    def __init__(self,filepath=None,scale=1,Main_Text=Text(),Header_Text=None,pos=(0,0),mt_pos=(0,0),mt_end=(0,0),ht_pos=(0,0),ht_target='Name',fill_mode='stretch',fit_axis='free',line_distance=1.5,label_color='Lavender'):
        # align 只能为left
        super().__init__(filepath=filepath,scale=scale,Main_Text=Main_Text,Header_Text=Header_Text,pos=pos,mt_pos=mt_pos,ht_pos=ht_pos,ht_target=ht_target,line_distance=line_distance,label_color=label_color)
        if (mt_pos[0] >= mt_end[0]) | (mt_pos[1] >= mt_end[1]) | (mt_end[0] > self.media.get_size()[0]) | (mt_end[1] > self.media.get_size()[1]):
            raise MediaError('InvSep','mt_end')
        elif (mt_pos[0] < 0) | (mt_pos[1] < 0):
            raise MediaError('InvSep','mt_pos')
        else:
            self.mt_end = mt_end
        # fill_mode 只能是 stretch 或者 collage
        if fill_mode in ['stretch','collage']:
            self.fill_mode = fill_mode
        else:
            raise MediaError('InvFill',fill_mode)
        # fit_axis 只能是 free vertical horizontal
        if fit_axis in ['free','vertical','horizontal']:
            self.horizontal,self.vertical = {'free':(1,1),'vertical':(0,1),'horizontal':(1,0)}[fit_axis]
        else:
            raise MediaError('InvFit',fit_axis)
        # x,y轴上的四条分割线
        self.x_tick = [0,self.mt_pos[0],self.mt_end[0],self.media.get_size()[0]]
        self.y_tick = [0,self.mt_pos[1],self.mt_end[1],self.media.get_size()[1]]
        self.bubble_clip = []
        # 0 3 6
        # 1 4 7
        # 2 5 8
        for i in range(0,3):
            for j in range(0,3):
                self.bubble_clip.append(self.media.subsurface((self.x_tick[i],self.y_tick[j],
                                                               self.x_tick[i+1]-self.x_tick[i],
                                                               self.y_tick[j+1]-self.y_tick[j]
                                                               )))
        # 以np array 的形式存储气泡碎片
        # 注意，这9个碎片有的尺寸有可能为0！这种情况是能够兼容的。

        self.bubble_clip = np.array(self.bubble_clip)
        self.bubble_clip_size = np.frompyfunc(lambda x:x.get_size(),1,1)(self.bubble_clip)
    # 重载draw
    def draw(self, text:str,header:str='',effect:int=-1)->tuple:
        # 首先，需要把主文本渲染出来
        main_text = self.tx_effect(text,effect)
        # 不能完全空白，不然main_text_list为空，无法后续执行
        if main_text == '':
            main_text = ' '
        main_text_list = self.MainText.draw(main_text)
        # 第一次循环：获取最大的x和最大的y
        xlim=0
        for i,text_surf in enumerate(main_text_list):
            x_this,y_this = text_surf.get_size()
            y_this = i*self.MainText.size*self.line_distance + y_this
            if x_this > xlim:
                xlim = int(x_this)
            ylim = int(y_this)
        # 检查适应方向
        if self.vertical == 0:
            ylim = self.bubble_clip_size[4][1]
        if self.horizontal == 0:
            xlim = self.bubble_clip_size[4][0]
        # 建立变形后的气泡
        temp_size_x = xlim + self.x_tick[1] + self.x_tick[3] - self.x_tick[2]
        temp_size_y = ylim + self.y_tick[1] + self.y_tick[3] - self.y_tick[2]
        temp = pygame.Surface((temp_size_x,temp_size_y),pygame.SRCALPHA)
        temp.fill((0,0,0,0))
        # 气泡碎片的渲染位置
        bubble_clip_pos = {
            0:(0,0),
            1:(0,self.y_tick[1]),
            2:(0,self.y_tick[1]+ylim),
            3:(self.x_tick[1],0),
            4:(self.x_tick[1],self.y_tick[1]),
            5:(self.x_tick[1],self.y_tick[1]+ylim),
            6:(self.x_tick[1]+xlim,0),
            7:(self.x_tick[1]+xlim,self.y_tick[1]),
            8:(self.x_tick[1]+xlim,self.y_tick[1]+ylim)
        }
        # 气泡碎片的目标大小
        bubble_clip_scale = {
            0:False,
            1:(self.x_tick[1],ylim),
            2:False,
            3:(xlim,self.y_tick[1]),
            4:(xlim,ylim),
            5:(xlim,self.y_tick[3]-self.y_tick[2]),
            6:False,
            7:(self.x_tick[3]-self.x_tick[2],ylim),
            8:False
        }
        for i in range(0,9):
            if 0 in self.bubble_clip_size[i]:
                continue
            else:
                if bubble_clip_scale[i] == False:
                    temp.blit(self.bubble_clip[i],bubble_clip_pos[i])
                else:
                    if self.fill_mode == 'stretch':
                        temp.blit(pygame.transform.scale(self.bubble_clip[i],bubble_clip_scale[i]),bubble_clip_pos[i])
                    elif self.fill_mode == 'collage':
                        # 新建拼贴图层，尺寸为气泡碎片的目标大小
                        collage = pygame.Surface(bubble_clip_scale[i],pygame.SRCALPHA)
                        collage.fill((0,0,0,0))
                        col_x,col_y = (0,0)
                        while col_y < bubble_clip_scale[i][1]:
                            col_x = 0
                            while col_x < bubble_clip_scale[i][0]:
                                collage.blit(self.bubble_clip[i],(col_x,col_y))
                                col_x = col_x + self.bubble_clip_size[i][0]
                            col_y = col_y + self.bubble_clip_size[i][1]
                        temp.blit(collage,bubble_clip_pos[i])
        # 第二次循环：把主文本blit到临时容器
        for i,text_surf in enumerate(main_text_list):
            temp.blit(text_surf,(self.x_tick[1],self.y_tick[1]+i*self.MainText.size*self.line_distance))
        # 头文本
        if (self.Header!=None) & (header!=''):    # Header 有定义，且输入文本不为空
            if self.ht_pos[0] > self.x_tick[2]:
                ht_renderpos_x = self.ht_pos[0] - self.x_tick[2] + self.x_tick[1] + xlim
            else:
                ht_renderpos_x = self.ht_pos[0]
            if self.ht_pos[1] > self.y_tick[2]:
                ht_renderpos_y = self.ht_pos[1] - self.y_tick[2] + self.y_tick[1] + ylim
            else:
                ht_renderpos_y = self.ht_pos[1]
            temp.blit(self.Header.draw(header)[0],(ht_renderpos_x,ht_renderpos_y))
        return temp,(temp_size_x,temp_size_y)
    def convert(self): # 和Animation类相同的convert
        super().convert()
        self.bubble_clip = np.frompyfunc(lambda x:x.convert_alpha(),1,1)(self.bubble_clip)
# 聊天窗
class ChatWindow(Bubble):
    def __init__(self,filepath=None,scale=1,sub_key=['Key1'],sub_Bubble=[Bubble()],sub_Anime=[],sub_align=['left'],pos=(0,0),sub_pos=(0,0),sub_end=(0,0),am_left=0,am_right=0,sub_distance=50,label_color='Lavender'):
        # 媒体和路径
        MediaObj.__init__(self,filepath=filepath,label_color=label_color)
        if self.filepath is None: # 支持气泡图缺省
            # 媒体设为空图
            self.media = pygame.Surface(self.screen_size,pygame.SRCALPHA)
            self.media.fill(self.cmap['empty'])
        else:
            self.media = self.zoom(pygame.image.load(self.filepath.exact()),scale=scale)
            self.scale = scale
        # 位置
        if type(pos) in [Pos,FreePos]:
            self.pos = pos
        else:
            self.pos = Pos(*pos)
        # 检查子气泡和key是否是能匹配
        if len(sub_Bubble) != len(sub_key):
            raise MediaError('CWKeyLen')
        # 子气泡和对齐
        self.sub_Bubble = {}
        self.sub_Anime = {}
        self.sub_align = {}
        for i,key in enumerate(sub_key):
            # 检查气泡是否是 Ballon
            if type(sub_Bubble[i]) is Balloon:
                raise MediaError('Bn2CW',key)
            self.sub_Bubble[key] = sub_Bubble[i]
            # 载入对齐，默认是左对齐
            try:
                if sub_align[i] in ['left','right']:
                    self.sub_align[key] = sub_align[i]
                else:
                    raise MediaError('BadAlign',sub_align[i])
            except IndexError:
                self.sub_align[key] = 'left'
            # 载入子立绘，默认是None
            try:
                if sub_Anime[i].length == 1:
                    self.sub_Anime[key] = sub_Anime[i]
                else:
                    raise MediaError('DA2CW')
            except (IndexError,AttributeError):
                # IndexError: sub_Anime[i] list index out of range\
                # AttributeError: 'NoneType' object (sub_Anime[i]) has no attribute 'length'
                self.sub_Anime[key] = None

        # 子气泡尺寸
        if (sub_pos[0] >= sub_end[0]) | (sub_pos[1] >= sub_end[1]):
            raise MediaError('InvSep','sub_end')
        else:
            self.sub_size = (sub_end[0]-sub_pos[0],sub_end[1]-sub_pos[1])
            self.sub_pos = sub_pos
        # 立绘对齐位置
        if am_left >= am_right:
            raise MediaError('InvSep','am_right')
        else:
            self.am_left = am_left
            self.am_right = am_right
        # 子气泡间隔
        self.sub_distance = sub_distance
        # 留存文本容器：
        self.main_text = ''
        self.header_text = ''
        # 测试子气泡尺寸，基于第一个子气泡对象，渲染一个最小子气泡图层
        test_subsurface_size = self.sub_Bubble[sub_key[0]].draw(' ')[1]
        # 按照最小子气泡图层的高度 + sub_distance 作为一个单位长度
        self.max_recode = np.ceil(self.sub_size[1]/(test_subsurface_size[1] + self.sub_distance))
    # 给聊天窗添加记录
    def append(self, text, header):
        if self.main_text == '':
            self.main_text = text
            self.header_text = header
        else:
            # 如果当前的记录数达到最大记录数
            if len(self.header_text.split('|')) >= self.max_recode:
                # 将记录的句子的一个段删除 S = S[S.find('|')+1:]
                self.main_text = self.main_text[self.main_text.find('|')+1:]
                self.header_text = self.header_text[self.header_text.find('|')+1:]
            self.main_text = self.main_text + '|' + text
            self.header_text = self.header_text + '|' + header
    # 清空聊天窗
    def clear(self):
        self.main_text = ''
        self.header_text = ''
    # 执行向量相加
    def UF_add_main_text(self,text):
        return np.frompyfunc(lambda x : x if self.main_text == '' else self.main_text+'|'+x,1,1)(text)
    def UF_add_header_text(self,header):
        return np.frompyfunc(lambda x : x if self.header_text == '' else self.header_text+'|'+x,1,1)(header)
    # 渲染气泡
    def draw(self, text:str,header:str='',effect:int=-1)->tuple:
        # 母气泡的复制品
        temp = self.media.copy()
        # 容纳子气泡的容器
        sub_surface = pygame.Surface(self.sub_size,pygame.SRCALPHA)
        sub_surface.fill((0,0,0,0))
        # 容纳立绘的容器，宽度=amright-amleft，高度等于子气泡
        sub_groupam = pygame.Surface((self.am_right-self.am_left,self.sub_size[1]),pygame.SRCALPHA)
        sub_groupam.fill((0,0,0,0))
        # 拆分主文本和头文本
        main_text_list = text.split('|')
        header_text_list = header.split('|')
        # 应用效果于最后一个片段的文本
        main_text_list[-1] = self.tx_effect(main_text_list[-1],effect)
        # 注意，由于w2w或者l2l的设定，main_text_list 很可能和 header_text_list 并不能完全匹配！
        # 主1|主2|主3|
        # 头1|头2|头3|头4|头5
        # 头：|key#header_text|
        # 第一次循环：对应主文本和头文本的关系
        header_main_pair = []
        for i,main_text in enumerate(main_text_list):
            header_main_pair.append((header_text_list[i],main_text))
        # 将头主文本对列表倒序
        header_main_pair = header_main_pair[::-1]
        # 第二次循环：渲染子气泡
        y_bottom = self.sub_size[1] # 当前句子的可用y底部
        for idx,header_main in enumerate(header_main_pair):
            # 解析(键#头文本,主文本)
            bubble_header_this,main_this = header_main
            key_this,header_this = bubble_header_this.split('#')
            # 绘制子气泡
            subbubble_surface_this,subbubble_surface_size = self.sub_Bubble[key_this].draw(main_this,header_this)
            # 如果是run：把当前的y_bottom 向下移动 effect * (这个小节的高度 + 小节见间距)，并且不渲染第一小节
            if idx == 0 and effect < 0:
                y_bottom = y_bottom - (subbubble_surface_size[1] + self.sub_distance) * (effect + 1)
                continue
            if self.sub_align[key_this] == 'left':
                # x = 0，y = 底部-子气泡的高度
                sub_surface.blit(subbubble_surface_this,(0,y_bottom-subbubble_surface_size[1]))
                if self.sub_Anime[key_this] is not None:
                    sub_groupam.blit(self.sub_Anime[key_this].media[0],(0,y_bottom-subbubble_surface_size[1]))
            else:
                # x = 右侧 - 子气泡的宽度，y同上
                sub_surface.blit(subbubble_surface_this,(self.sub_size[0]-subbubble_surface_size[0],y_bottom-subbubble_surface_size[1]))
                if self.sub_Anime[key_this] is not None:
                    sub_groupam.blit(self.sub_Anime[key_this].media[0],(self.am_right-self.am_left-self.sub_Anime[key_this].media[0].get_size()[0],y_bottom-subbubble_surface_size[1]))
            # 更新可用底部 = 前一次底部 - 子气泡高度 - 子气泡间距
            y_bottom = y_bottom - subbubble_surface_size[1] - self.sub_distance
            # 如果可用底部已经达到顶部之外
            if y_bottom < 0:
                break
        # 将子气泡容器渲染到母气泡容器
        temp.blit(sub_surface,self.sub_pos)
        temp.blit(sub_groupam,(self.am_left,self.sub_pos[1]))
        return temp,temp.get_size()
# 背景
class Background(MediaObj):
    def __init__(self,filepath,scale=1,pos = (0,0),label_color='Lavender'):
        # 文件和路径
        super().__init__(filepath=filepath,label_color=label_color)
        if filepath in self.cmap.keys():
            self.media = pygame.Surface(self.screen_size)
            self.media.fill(self.cmap[filepath])
        else:
            self.media = self.zoom(pygame.image.load(self.filepath.exact()),scale=scale)
            self.scale = scale
        # 位置
        if type(pos) in [Pos,FreePos]:
            self.pos = pos
        else:
            self.pos = Pos(*pos)
    def display(self,surface,alpha=100,center='NA',adjust='NA'):
        if center == 'NA':
            render_center = self.pos
        else:
            render_center = Pos(*eval(center))
        if adjust in ['(0,0)','NA']:
            render_pos = render_center
        else:
            render_pos = render_center + eval(adjust)
        if alpha !=100:
            temp = self.media.copy()
            temp.set_alpha(alpha/100*255)
            surface.blit(temp,render_pos.get())
        else:
            surface.blit(self.media,render_pos.get())
    def convert(self):
        self.media = self.media.convert_alpha()
# 立绘
class Animation(MediaObj):
    def __init__(self,filepath,scale=1,pos = (0,0),tick=1,loop=True,label_color='Lavender'):
        # 文件和路径
        super().__init__(filepath=filepath,label_color=label_color)
        self.length = len(self.filepath.list())
        # self.media -> np.ndarray(Surface)
        self.media:np.ndarray = np.frompyfunc(lambda x:self.zoom(pygame.image.load(x),scale=scale),1,1)(self.filepath.list())
        self.scale = scale
        if type(pos) in [Pos,FreePos]:
            self.pos = pos
        else:
            self.pos = Pos(*pos)
        # 动画循环参数
        self.loop = loop
        self.this = 0
        self.tick = tick
    def display(self,surface,alpha=100,center='NA',adjust='NA',frame=0):
        self.this = frame
        if center == 'NA':
            render_center = self.pos
        else:
            render_center = Pos(*eval(center))
        if adjust in ['(0,0)','NA']:
            render_pos = render_center
        else:
            render_pos = render_center + eval(adjust)
        if alpha !=100:
            temp = self.media[int(self.this)].copy()
            temp.set_alpha(alpha/100*255)
            surface.blit(temp,render_pos.get())
        else:
            surface.blit(self.media[int(self.this)],render_pos.get())
    def get_tick(self,duration): # 1.8.0
        if self.length > 1: # 如果length > 1 说明是多帧的动画！
            tick_lineline = (np.arange(0,duration if self.loop else self.length,1/self.tick)[0:duration]%(self.length))
            tick_lineline = np.hstack([tick_lineline,(self.length-1)*np.ones(duration-len(tick_lineline))]).astype(int)
        else:
            tick_lineline = np.zeros(duration).astype(int)
        return tick_lineline
    def convert(self):
        self.media = np.frompyfunc(lambda x:x.convert_alpha(),1,1)(self.media)
# 组合立绘
class GroupedAnimation(Animation):
    def __init__(self,subanimation_list,subanimation_current_pos=None,label_color='Mango'):
        # 新建画板，尺寸为全屏
        canvas_surface = pygame.Surface(self.screen_size,pygame.SRCALPHA)
        canvas_surface.fill(self.cmap['empty'])
        # 如果外部未指定位置参数，则使用子Animation类的自身的pos
        if subanimation_current_pos is None:
            subanimation_current_pos = [None]*len(subanimation_list)
        # 如果指定的位置参数和子Animation的数量不一致，报出报错
        elif len(subanimation_current_pos) != len(subanimation_list):
            raise MediaError('GAPrame')
        # 开始在画板上绘制立绘
        else:
            # 越后面的位于越上层的图层
            # [zhang,drink_left] [(0,0),(0,0)] # list of Animation/str | list of tuple/str
            for am_name,am_pos in zip(subanimation_list,subanimation_current_pos):
                try:
                    if type(am_name) in [Animation,BuiltInAnimation,GroupedAnimation]:
                        subanimation = am_name
                    else: # type(am_name) is str
                        subanimation = eval(am_name)
                except NameError as E:
                    raise MediaError('Undef2GA',am_name)
                if subanimation.length > 1:
                    raise MediaError('DA2GA',am_name)
                else:
                    if am_pos is None:
                        subanimation.display(canvas_surface)
                    else:
                        # 为什么需要指定center呢？是因为，如果使用了FreePos，pos在parser的进度中，可能会变动。
                        # 正常来说，每个立绘的实时pos被记录在了timeline上，在render的时候，不采用本身的pos
                        # 在主程序中，GroupedAnimation的定义发生在parser中，因此位置准确
                        # 但是，在导出时，只能通过BIA的形式传递给导出模块。
                        # 如果BIA的参数中没有包括每个子Animation的准确位置，就会一律使用初始化位置
                        # （因为导出模块没有parser，FreePos类都停留在初始化位置）
                        subanimation.display(canvas_surface,center=str(am_pos)) # am_pos = "(0,0)"
        # 初始化
        self.length = 1
        self.media = np.array([canvas_surface])
        self.pos = Pos(0,0)
        self.loop = 0
        self.this = 0
        self.tick = 1
        self.label_color = label_color
# 内建动画
class BuiltInAnimation(Animation):
    def __init__(self,anime_type='hitpoint',anime_args=('0',0,0,0),screensize = (1920,1080),layer=0,label_color='Mango'):
        BIA_text = Text('./media/SourceHanSerifSC-Heavy.otf',fontsize=int(0.0521*screensize[0]),color=(255,255,255,255),line_limit=10)
        frame_rate = self.frame_rate
        self.label_color = label_color
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
                raise MediaError('InvHPArg',','.join([str(name_tx),str(heart_max),str(heart_begin),str(heart_end)]))
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
                self.pos = Pos((screensize[0]-max(nx,total_heart))/2,(4/5*screensize[1]-hy-ny)/2)
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
                self.pos = Pos((screensize[0]-total_heart)/2,3/5*screensize[1]+ny/2-hy/2)
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
                self.pos = Pos(heart_end//2*(hx + distance)+(heart_end%2)*int(hx/2)+(screensize[0]-total_heart)/2,3/5*screensize[1]+ny/2-hy/2)
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
                    raise MediaError('InvDCSytx',str(die),E)
                if (dice_face>dice_max)|(dice_check<-1)|(dice_check>dice_max)|(dice_face<0)|(dice_max<=0):
                    raise MediaError('InvDCArg', ','.join([str(name_tx),str(dice_max),str(dice_check),str(dice_face)]))
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
                        canvas.blit(check_surf,(int(0.7292*screensize[0]),y_anchor+i*y_unit+(y_unit-cy)//2)) # 0.7292*screensize[0] = 1400
                self.media = np.array([canvas])
                self.pos = Pos(0,0)
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
                self.pos = Pos(int(0.5833*screensize[0]),y_anchor)
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
                self.pos = Pos(int(0.5833*screensize[0]),y_anchor) # 0.5833*screensize[0] = 1120
                self.tick = 1
                self.loop = 1
            else:
                pass
            self.this = 0
            self.length=len(self.media)
# 音效
class Audio(MediaObj):
    pygame.mixer.init()
    def __init__(self,filepath,label_color='Caribbean'):
        # 文件路径
        super().__init__(filepath=filepath,label_color=label_color)
        try:
            self.media = pygame.mixer.Sound(self.filepath.exact())
        except Exception as E:
            raise MediaError('BadAudio',filepath)
    def display(self,channel,volume=100):
        channel.set_volume(volume/100)
        channel.play(self.media)
    def get_length(self):
        return self.media.get_length()
# 背景音乐
class BGM(MediaObj):
    def __init__(self,filepath,volume=100,loop=True,label_color='Caribbean'):
        # 文件路径
        super().__init__(filepath=filepath,label_color=label_color)
        self.media = self.filepath.exact()
        self.volume = volume/100
        if loop == True:
            self.loop = -1 #大概是不可能能放完的
        else:
            self.loop = 0
        if self.filepath.type() not in ['ogg']:#建议的格式
            print(WarningPrint('BadBGMFmt',filepath.split('.')[-1]))
    def display(self):
        if pygame.mixer.music.get_busy() == True: #如果已经在播了
            pygame.mixer.music.stop() #停止
            pygame.mixer.music.unload() #换碟
        else:
            pass
        pygame.mixer.music.load(self.media) #进碟
        pygame.mixer.music.play(loops=self.loop) #开始播放
        pygame.mixer.music.set_volume(self.volume) #设置音量

# 导出视频模块 export video
# 音效
class Audio_Video(MediaObj):
    def __init__(self,filepath,label_color='Caribbean'):
        super().__init__(filepath=filepath,label_color=label_color)
        self.media = pydub.AudioSegment.from_file(self.filepath.exact())
# 背景音乐
class BGM_Video(MediaObj):
    def __init__(self,filepath,volume=100,loop=True,label_color='Caribbean'):
        super().__init__(filepath=filepath,label_color=label_color)
        self.media = pydub.AudioSegment.from_file(self.filepath.exact()) + np.log10(volume/100) * 20 # 调整音量
        self.loop = loop