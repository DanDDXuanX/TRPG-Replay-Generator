#!/usr/bin/env python
# coding: utf-8

# 导出为PR项目说使用的媒体类，和pygameMedia相同的接口

import numpy as np
from pygame import mixer
from PIL import Image,ImageFont,ImageDraw

from .Medias import MediaObj
from .FilePaths import Filepath
from .Exceptions import MediaError,WarningPrint
from .FreePos import Pos,FreePos,PosGrid

# PR序列的基类，继承自MediaObj
class PrMediaClip(MediaObj):
    # 剪辑的xml模板
    clip_tplt = open('./xml_templates/tplt_clip.xml','r',encoding='utf8').read()
    audio_clip_tplt = open('./xml_templates/tplt_audio_clip.xml','r',encoding='utf8').read()
    # 初始化序号
    outtext_index = 0
    outanime_index = 0 
    clip_index = 0
    file_index = 0
    # 项目配置参数的初始化
    output_path = './'
    Is_NTSC = True
    Audio_type = 'Stereo'
    # 公共函数：处理PR的图片坐标
    def PR_center_arg(self,obj_size,pygame_pos) -> np.ndarray:
        screensize = np.array(self.screen_size)
        return (pygame_pos+obj_size/2-screensize/2)/obj_size*self.scale
    def zoom(self,media:Image.Image,scale:float)->Image.Image:
        if scale == 1:
            return media
        elif scale <= 0:
            raise MediaError('InvScale',scale)
        else:
            sizex,sizey = media.size
            target_size = int(sizex * scale),int(sizey * scale)
            return media.resize(target_size)
# 字体
class Text(PrMediaClip):
    def __init__(self,fontfile='./media/SourceHanSansCN-Regular.otf',fontsize=40,color=(0,0,0,255),line_limit=20,label_color='Lavender'):
        super().__init__(filepath=fontfile,label_color=label_color)
        self.color=color
        self.size=fontsize
        self.line_limit = line_limit
    def render(self,tx):
        font_this = ImageFont.truetype(self.filepath.exact(), self.size)
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
            ceil_div = lambda x,y: -(-x//y)
            for i in range(0,ceil_div(len(text),self.line_limit)):
                out_text.append(self.render(text[i*self.line_limit:(i+1)*self.line_limit]))
        else:
            out_text = [self.render(text)]
        return out_text
# 描边字体
class StrokeText(Text):
    def __init__(self,fontfile='./media/SourceHanSansCN-Regular.otf',fontsize=40,color=(0,0,0,255),line_limit=20,edge_color=(255,255,255,255),edge_width=1,projection='C',label_color='Lavender'):
        super().__init__(fontfile=fontfile,fontsize=fontsize,color=color,line_limit=line_limit,label_color=label_color) # 继承
        # 描边颜色
        self.edge_color=edge_color
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
    def render(self,tx):
        ew = self.edge_width
        font_this = ImageFont.truetype(self.filepath.exact(), self.size)
        text_this = Image.new(mode='RGBA',size=(self.size*int(len(tx)*1.5)+2*ew,self.size*2+2*ew),color=(0,0,0,0)) # 画布贪婪为2x高度，1.5*宽度
        draw_this = ImageDraw.Draw(text_this)
        if ew > 0:
            # 角
            for pos in [[0,0],[0,2*ew],[2*ew,0],[2*ew,2*ew]]:
                draw_this.text(pos,tx,font = font_this,align ="left",fill = self.edge_color)
            # 边
            for i in range(1,ew*2):
                for pos in [[0,i],[i,0],[2*ew,i],[i,2*ew]]:
                    draw_this.text(pos,tx,font = font_this,align ="left",fill = self.edge_color)
        else:
            pass
        # 中心
        draw_this.text((ew,ew)-self.dirction_dict[self.dirction]*(ew-1),tx,font = font_this,align ="left",fill = self.color)
        return text_this
# 气泡
class Bubble(PrMediaClip):
    def __init__(self,filepath=None,scale=1,Main_Text=Text(),Header_Text=None,pos=(0,0),mt_pos=(0,0),ht_pos=(0,0),ht_target='Name',align='left',line_distance=1.5,label_color='Lavender'):
        super().__init__(filepath=filepath,label_color=label_color)
        # 支持气泡图缺省
        if self.filepath is None:
            self.path = None
            self.media = None
            self.scale = 1
            self.filename = None
            self.size = self.screen_size
            self.origin_size = self.size
        else:
            self.path = self.filepath.xml_reformated()
            origin_media = Image.open(self.filepath.exact()).convert('RGBA')
            self.origin_size = origin_media.size
            self.media = self.zoom(origin_media,scale=scale)
            self.scale = scale
            self.size = self.media.size
            self.filename = self.filepath.name()
        # pos
        if type(pos) in [Pos,FreePos]:
            self.pos = pos
        else:
            self.pos = Pos(*pos)
        # Text
        self.MainText = Main_Text
        self.mt_pos = mt_pos
        self.Header = Header_Text
        self.ht_pos = ht_pos
        self.target = ht_target
        self.line_distance = line_distance
        self.align = align
        # clip
        self.fileindex = 'BBfile_' + '%d'% PrMediaClip.file_index
        PrMediaClip.file_index = PrMediaClip.file_index+1
    # return a canvas
    def draw(self, text, header=''):
        # 生成文本图片
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
                             (x + (self.MainText.size*self.MainText.line_limit - word_w)//2,
                              int(y+i*self.MainText.size*self.line_distance+p2)
                             )
                            )
        # canvas.save(ofile)
        return canvas
    def display(self,begin,end,text,header='',center='NA'): # 这段代码是完全没有可读性的屎，但是确实可运行，非必要不要改
        if center == 'NA':
            self.PRpos = self.PR_center_arg(np.array(self.size),np.array(self.pos.get()))
        else:
            self.PRpos = self.PR_center_arg(np.array(self.size),np.array(Pos(*eval(center)).get()))
        
        ofile = self.output_path+'/auto_TX_%d'%PrMediaClip.outtext_index+'.png'
        canvas_draw = self.draw(text,header)
        canvas_draw.save(ofile)
        
        # 生成序列
        width,height = self.origin_size
        pr_horiz,pr_vert = self.PRpos
        if self.path is None:
            clip_bubble = None
            # print('Render empty Bubble!')
        else:
            clip_bubble = self.clip_tplt.format(**{'clipid':'BB_clip_%d'%PrMediaClip.clip_index,
                                              'clipname':self.filename,
                                              'timebase':'%d'%self.frame_rate,
                                              'ntsc':self.Is_NTSC,
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
                                              'vert':'%.5f'%pr_vert,
                                              'scale':'%.2f'%(self.scale*100),
                                              'colorlabel':self.label_color})
        clip_text = self.clip_tplt.format(**{'clipid':'TX_clip_%d'%PrMediaClip.clip_index,
                                        'clipname':'auto_TX_%d.png'%PrMediaClip.outtext_index,
                                        'timebase':'%d'%self.frame_rate,
                                        'ntsc':self.Is_NTSC,
                                        'start':'%d'%begin,
                                        'end':'%d'%end,
                                        'in':'%d'%90000,
                                        'out':'%d'%(90000+end-begin),
                                        'fileid':'auto_TX_%d'%PrMediaClip.outtext_index,
                                        'filename':'auto_TX_%d.png'%PrMediaClip.outtext_index,
                                        'filepath':Filepath(ofile).xml_reformated(),
                                        'filewidth':'%d'%width,
                                        'fileheight':'%d'%height,
                                        'horiz':'%.5f'%pr_horiz,
                                        'vert':'%.5f'%pr_vert,
                                        'scale':100,
                                        'colorlabel':self.MainText.label_color})
        PrMediaClip.outtext_index = PrMediaClip.outtext_index + 1
        PrMediaClip.clip_index = PrMediaClip.clip_index + 1
        return (clip_bubble,clip_text)
# 气球
class Balloon(Bubble):
    def __init__(self,filepath=None,scale=1,Main_Text=Text(),Header_Text=[None],pos=(0,0),mt_pos=(0,0),ht_pos=[(0,0)],ht_target=['Name'],align='left',line_distance=1.5,label_color='Lavender'):
        super().__init__(filepath=filepath,scale=scale,Main_Text=Main_Text,Header_Text=Header_Text,pos=pos,mt_pos=mt_pos,ht_pos=ht_pos,ht_target=ht_target,align=align,line_distance=line_distance,label_color=label_color)
        if len(self.Header)!=len(self.ht_pos) or len(self.Header)!=len(self.target):
            raise MediaError('BnHead')
        else:
            self.header_num = len(self.Header)
    def draw(self, text, header=''):
        # 生成文本图片 # 同Bubble类
        canvas = Image.new(mode='RGBA',size=self.size,color=(0,0,0,0))
        # 生成头文本
        header_texts = header.split('|')
        for i,header_text_this in enumerate(header_texts):
            # Header 不为None ，且输入文本不为空
            if (self.Header[i]!=None) & (header_text_this!=''):
                ht_text = self.Header[i].draw(header_text_this)[0]
                try:
                    p1,p2,p3,p4 = ht_text.getbbox()
                    canvas.paste(ht_text.crop((p1,p2,p3,p4)),(self.ht_pos[i][0]+p1,self.ht_pos[i][1]+p2)) # 兼容微软雅黑这种，bbox到处飘的字体
                except TypeError:
                    pass
            if i == self.header_num -1:
                break
        # 生成主文本 # 同Bubble类
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
                             (x + (self.MainText.size*self.MainText.line_limit - word_w)//2,
                              int(y+i*self.MainText.size*self.line_distance+p2)
                             )
                            )
        return canvas
# 自适应气泡
class DynamicBubble(Bubble):
    def __init__(self,filepath=None,scale=1,Main_Text=Text(),Header_Text=None,pos=(0,0),mt_pos=(0,0),mt_end=(0,0),ht_pos=(0,0),ht_target='Name',fill_mode='stretch',fit_axis='free',line_distance=1.5,label_color='Lavender'):
        super().__init__(filepath=filepath,scale=scale,Main_Text=Main_Text,Header_Text=Header_Text,pos=pos,mt_pos=mt_pos,ht_pos=ht_pos,ht_target=ht_target,line_distance=line_distance,label_color=label_color)
        if (mt_pos[0] >= mt_end[0]) | (mt_pos[1] >= mt_end[1]) | (mt_end[0] > self.size[0]) | (mt_end[1] > self.size[1]):
            raise MediaError('InvSep','mt_end')
        elif (mt_pos[0] < 0) | (mt_pos[1] < 0):
            raise MediaError('InvSep','mt_pos')
        else:
            self.mt_end = mt_end
        # fill_mode 只能是 stretch 或者 collage
        if fill_mode in ['stretch','collage']:
            self.fill_mode = fill_mode
        else:
            raise MediaError('InvFill', fill_mode)
        # fit_axis 只能是 free vertical horizontal
        if fit_axis in ['free','vertical','horizontal']:
            self.horizontal,self.vertical = {'free':(1,1),'vertical':(0,1),'horizontal':(1,0)}[fit_axis]
        else:
            raise MediaError('InvFit',fit_axis)
        # x,y轴上的四条分割线
        self.x_tick = [0,self.mt_pos[0],self.mt_end[0],self.size[0]]
        self.y_tick = [0,self.mt_pos[1],self.mt_end[1],self.size[1]]
        self.bubble_clip = []
        # 0 3 6
        # 1 4 7
        # 2 5 8
        for i in range(0,3):
            for j in range(0,3):
                try:
                    # crop(left, upper, right, lower)
                    self.bubble_clip.append(self.media.crop((self.x_tick[i],self.y_tick[j],
                                                             self.x_tick[i+1],self.y_tick[j+1]
                                                            )))
                except Exception:
                    # 无效的clip
                    self.bubble_clip.append(None)
        self.bubble_clip_size = list(map(lambda x:(0,0) if x is None else x.size, self.bubble_clip))

    def draw(self, text, header = ''):
        # 首先，需要把主文本渲染出来
        main_text_list = self.MainText.draw(text)
        # 第一次循环：获取最大的x和最大的y
        # 导出PR项目的特殊性：如果是一个空白文本，那么getbbox将不能得到理论尺寸。
        # 因此xlim和ylim的初始值被设为半个字的大小。
        xlim = int(self.MainText.size/2)
        ylim = self.MainText.size
        for i,mt_text in enumerate(main_text_list):
            try:
                p1,p2,p3,p4 = mt_text.getbbox() # 先按照bboxcrop，然后按照原位置放置
            except TypeError: # 如果遇到了空图导致的TypeError，直接跳过这一循环，走到下一行
                continue
            # 因为考虑到有的字体的bbox不对劲，因此不减去p1,p2，以p3，p4为准
            x_this = p3
            y_this = p4
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
        bubble_canvas = Image.new(mode='RGBA',size=(temp_size_x,temp_size_y),color=(0,0,0,0))
        text_canvas = Image.new(mode='RGBA',size=(temp_size_x,temp_size_y),color=(0,0,0,0))
        # 生成文本图片
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
            ht_text = self.Header.draw(header)[0]
            try:
                p1,p2,p3,p4 = ht_text.getbbox() # 如果是空图的话，getbbox返回None，会发生TypeError
                text_canvas.paste(ht_text.crop((p1,p2,p3,p4)),(ht_renderpos_x+p1,ht_renderpos_y+p2)) # 兼容微软雅黑这种，bbox到处飘的字体
            except TypeError:
                pass
        # 主文本
        for i,mt_text in enumerate(main_text_list):
            try:
                p1,p2,p3,p4 = mt_text.getbbox() # 先按照bboxcrop，然后按照原位置放置
            except TypeError: # 如果遇到了空图导致的TypeError，直接跳过这一循环，走到下一行
                continue
            text_canvas.paste(mt_text.crop((p1,p2,p3,p4)),(self.x_tick[1]+p1,int(self.y_tick[1]+i*self.MainText.size*self.line_distance+p2)))

        # return ofile
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
                    bubble_canvas.paste(self.bubble_clip[i],bubble_clip_pos[i])
                else:
                    if self.fill_mode == 'stretch':
                        bubble_canvas.paste(self.bubble_clip[i].resize(bubble_clip_scale[i]),bubble_clip_pos[i])
                    elif self.fill_mode == 'collage':
                        # 新建拼贴图层，尺寸为气泡碎片的目标大小
                        collage_canvas = Image.new(mode='RGBA',size=bubble_clip_scale[i],color=(0,0,0,0))
                        col_x,col_y = (0,0)
                        while col_y < bubble_clip_scale[i][1]:
                            col_x = 0
                            while col_x < bubble_clip_scale[i][0]:
                                collage_canvas.paste(self.bubble_clip[i],(col_x,col_y))
                                col_x = col_x + self.bubble_clip_size[i][0]
                            col_y = col_y + self.bubble_clip_size[i][1]
                        bubble_canvas.paste(collage_canvas,bubble_clip_pos[i])
        # 如果气泡图是空的，则返回空
        if bubble_canvas.getbbox() is None:
            return None,text_canvas
        # 无论文本图是不是空的，均正常保存为文件。
        else:
            return bubble_canvas,text_canvas
    def display(self,begin,end,text,header='',center='NA'): # 这段代码是完全没有可读性的屎，但是确实可运行，非必要不要改
        # 先生成文件
        bubble_ofile = self.output_path+'/auto_BB_%d'%PrMediaClip.outtext_index+'.png'
        text_ofile = self.output_path+'/auto_TX_%d'%PrMediaClip.outtext_index+'.png'

        bubble_canvas,text_canvas = self.draw(text,header)
        temp_size = text_canvas.size

        # 保存文件
        text_canvas.save(text_ofile)

        # 获取动态气泡的参数
        width,height = temp_size
        # 获取PR位置参数
        if center == 'NA':
            self.PRpos = self.PR_center_arg(np.array(temp_size),np.array(self.pos.get()))
        else:
            self.PRpos = self.PR_center_arg(np.array(temp_size),np.array(Pos(*eval(center)).get()))
        pr_horiz,pr_vert = self.PRpos
        # 生成序列
        if bubble_canvas is None:
            clip_bubble = None
            # print('Render empty Bubble!')
        else:
            # 先保存气泡图片
            bubble_canvas.save(bubble_ofile)
            clip_bubble = self.clip_tplt.format(**{'clipid':'BB_clip_%d'%PrMediaClip.clip_index,
                                              'clipname':'auto_BB_%d.png'%PrMediaClip.outtext_index,
                                              'timebase':'%d'%self.frame_rate,
                                              'ntsc':self.Is_NTSC,
                                              'start':'%d'%begin,
                                              'end':'%d'%end,
                                              'in':'%d'%90000,
                                              'out':'%d'%(90000+end-begin),
                                              'fileid':'auto_BB_%d'%PrMediaClip.outtext_index,
                                              'filename':'auto_BB_%d.png'%PrMediaClip.outtext_index,
                                              'filepath':Filepath(bubble_ofile).xml_reformated(),
                                              'filewidth':'%d'%width,
                                              'fileheight':'%d'%height,
                                              'horiz':'%.5f'%pr_horiz,
                                              'vert':'%.5f'%pr_vert,
                                              'scale':100,
                                              'colorlabel':self.label_color})
        # tx的clip
        clip_text = self.clip_tplt.format(**{'clipid':'TX_clip_%d'%PrMediaClip.clip_index,
                                        'clipname':'auto_TX_%d.png'%PrMediaClip.outtext_index,
                                        'timebase':'%d'%self.frame_rate,
                                        'ntsc':self.Is_NTSC,
                                        'start':'%d'%begin,
                                        'end':'%d'%end,
                                        'in':'%d'%90000,
                                        'out':'%d'%(90000+end-begin),
                                        'fileid':'auto_TX_%d'%PrMediaClip.outtext_index,
                                        'filename':'auto_TX_%d.png'%PrMediaClip.outtext_index,
                                        'filepath':Filepath(text_ofile).xml_reformated(),
                                        'filewidth':'%d'%width,
                                        'fileheight':'%d'%height,
                                        'horiz':'%.5f'%pr_horiz,
                                        'vert':'%.5f'%pr_vert,
                                        'scale':100,
                                        'colorlabel':self.MainText.label_color})
        PrMediaClip.outtext_index = PrMediaClip.outtext_index + 1
        PrMediaClip.clip_index = PrMediaClip.clip_index+1
        return (clip_bubble,clip_text)
# 聊天窗
class ChatWindow(Bubble):
    def __init__(self,filepath=None,scale=1,sub_key=['Key1'],sub_Bubble=[Bubble()],sub_Anime=[],sub_align=['left'],pos=(0,0),sub_pos=(0,0),sub_end=(0,0),am_left=0,am_right=0,sub_distance=50,label_color='Lavender'):
        # 媒体和路径
        PrMediaClip.__init__(self,filepath=filepath,label_color=label_color)
        # 空白底图
        if self.filepath is None:
            self.path = None
            self.media = None
            self.scale = 1
            self.filename = None
            self.size = self.screen_size
            self.origin_size = self.size
        else:
            self.path = self.filepath.xml_reformated()
            origin_media = Image.open(self.filepath.exact()).convert('RGBA')
            self.origin_size = origin_media.size
            self.media = self.zoom(origin_media,scale=scale)
            self.scale = scale
            self.filename = self.filepath.name()
            self.size = self.media.size
        # 位置
        if type(pos) in [Pos,FreePos]:
            self.pos = pos
        else:
            self.pos = Pos(*pos)
        # 子气泡参数合法性
        if len(sub_Bubble) != len(sub_key):
            raise MediaError('CWKeyLen')
        # 子气泡和对齐
        self.sub_Bubble = {}
        self.sub_Anime = {}
        self.sub_align = {}
        for i,key in enumerate(sub_key):
            # 检查气泡是否是 Ballon
            if type(sub_Bubble[i]) is Balloon:
                raise MediaError('Bn2CW', key)
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
                self.sub_Anime[key] = sub_Anime[i]
            except IndexError:
                self.sub_Anime[key] = None
        # 子气泡尺寸
        if (sub_pos[0] >= sub_end[0]) | (sub_pos[1] >= sub_end[1]):
            raise MediaError('InvSep','sub_end')
        else:
            self.sub_size = (sub_end[0]-sub_pos[0],sub_end[1]-sub_pos[1])
            self.sub_pos = sub_pos
        # 立绘对齐位置
        if am_left >= am_right:
            raise MediaError('InvSep', 'am_right')
        else:
            self.am_left = am_left
            self.am_right = am_right
        # 子气泡间隔
        self.sub_distance = sub_distance
        # 留存文本容器-这边应该用不到：
        self.main_text = ''
        self.header_text = ''
        # 其他气泡类clip的必要参数
        self.fileindex = 'BBfile_' + '%d'% PrMediaClip.file_index
        self.label_color = label_color
        # 这个MainText只是用来给labelcolor做参考用的。
        self.MainText = self.sub_Bubble[sub_key[0]].MainText
        PrMediaClip.file_index = PrMediaClip.file_index + 1

    # 渲染气泡中的文本，对于CW来说，包括子气泡的窗体和PC头像都在这里生成。
    def draw(self, text, header=''):
        # 生成文本图片
        # 主容器，容纳整个文本图
        canvas = Image.new(mode='RGBA',size=self.size,color=(0,0,0,0))
        # 子气泡容器，容纳若干个子气泡及其文本
        sub_canvas = Image.new(mode='RGBA',size=self.sub_size,color=(0,0,0,0))
        # 立绘容器，容纳若干个立绘
        am_canvas = Image.new(mode='RGBA',size=(self.am_right-self.am_left,self.sub_size[1]),color=(0,0,0,0))
        # 拆分主文本和头文本
        main_text_list = text.split('|')
        header_text_list = header.split('|')
        header_main_pair = []
        for i,main_text in enumerate(main_text_list):
            header_main_pair.append((header_text_list[i],main_text))
        # 将头主文本对列表倒序
        header_main_pair = header_main_pair[::-1]
        # 第二次循环：渲染子气泡
        y_bottom = self.sub_size[1] # 当前句子的可用y底部
        for header_main in header_main_pair:
            # 解析(键#头文本,主文本)
            bubble_header_this,main_this = header_main
            key_this,header_this = bubble_header_this.split('#')
            # 绘制子气泡
            if type(self.sub_Bubble[key_this]) is DynamicBubble:
                bubble_canvas,text_canvas = self.sub_Bubble[key_this].draw(main_this,header_this)
            else:
                text_canvas = self.sub_Bubble[key_this].draw(main_this,header_this)
                bubble_canvas = self.sub_Bubble[key_this].media
            if bubble_canvas is not None:
                bubble_canvas.paste(text_canvas,(0,0),mask=text_canvas)
                subbubble_canvas = bubble_canvas
            else:
                subbubble_canvas = text_canvas
            subbubble_size = subbubble_canvas.size
            if self.sub_align[key_this] == 'left':
                sub_canvas.paste(subbubble_canvas,(0,y_bottom-subbubble_size[1]))
                if self.sub_Anime[key_this] is not None:
                    am_canvas.paste(self.sub_Anime[key_this].media,(0,y_bottom-subbubble_size[1]))
            else:
                sub_canvas.paste(subbubble_canvas,(self.sub_size[0]-subbubble_size[0],y_bottom-subbubble_size[1]))
                if self.sub_Anime[key_this] is not None:
                    am_canvas.paste(self.sub_Anime[key_this].media,(self.am_right-self.am_left-self.sub_Anime[key_this].size[0],y_bottom-subbubble_size[1]))
            # 更新可用底部 = 前一次底部 - 子气泡高度 - 子气泡间距
            y_bottom = y_bottom - subbubble_size[1] - self.sub_distance
            # 如果可用底部已经达到顶部之外
            if y_bottom < 0:
                break            
        # 将子气泡容器渲染到母气泡容器
        canvas.paste(sub_canvas,self.sub_pos)
        canvas.paste(am_canvas,(self.am_left,self.sub_pos[1]),mask=am_canvas)
        return canvas
# 背景
class Background(PrMediaClip):
    def __init__(self,filepath,scale=1,pos = (0,0),label_color='Lavender'):
        super().__init__(filepath=filepath,label_color=label_color)
        # 对纯色定义的背景的支持
        if filepath in self.cmap.keys():
            # 新建图像，并保存
            ofile = self.output_path+'/auto_BG_'+filepath+'.png'
            self.media = Image.new(mode='RGBA',size=self.screen_size,color=self.cmap[filepath])
            self.media.save(ofile)
            self.scale = 1
            self.filepath = Filepath(ofile)
            # 路径和尺寸
            self.path = self.filepath.xml_reformated()
            self.size = self.screen_size
            self.origin_size = self.size
        else:
            self.path = self.filepath.xml_reformated()
            origin_media = Image.open(self.filepath.exact()).convert('RGBA')
            self.origin_size = origin_media.size
            self.media = self.zoom(origin_media,scale=scale)
            self.size = self.media.size
            self.scale = scale
        if type(pos) in [Pos,FreePos]:
            self.pos = pos
        else:
            self.pos = Pos(*pos)
        # self.PRpos = PR_center_arg(np.array(self.size),np.array(self.pos.get()))
        self.filename = self.filepath.name()
        self.fileindex = 'BGfile_%d'% PrMediaClip.file_index
        PrMediaClip.file_index = PrMediaClip.file_index+1
    def display(self,begin,end,center='NA'):
        if center == 'NA':
            self.PRpos = self.PR_center_arg(np.array(self.size),np.array(self.pos.get()))
        else:
            self.PRpos = self.PR_center_arg(np.array(self.size),np.array(Pos(*eval(center)).get()))
        width,height = self.origin_size
        pr_horiz,pr_vert = self.PRpos
        clip_this = self.clip_tplt.format(**{'clipid':'BG_clip_%d'%PrMediaClip.clip_index,
                              'clipname':self.filename,
                              'timebase':'%d'%self.frame_rate,
                              'ntsc':self.Is_NTSC,
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
                              'vert':'%.5f'%pr_vert,
                              'scale':'%.2f'%(self.scale*100),
                              'colorlabel':self.label_color})
        PrMediaClip.clip_index = PrMediaClip.clip_index+1
        return clip_this
    def convert(self):
        pass
# 立绘图片
class Animation(PrMediaClip):
    def __init__(self,filepath,scale=1,pos = (0,0),tick=1,loop=True,label_color='Lavender'):
        # 文件路径
        super().__init__(filepath=filepath,label_color=label_color)
        self.path = self.filepath.xml_reformated() # 兼容动画Animation，只使用第一帧！
        origin_media = Image.open(self.filepath.exact()).convert('RGBA')
        self.origin_size = origin_media.size
        self.media = self.zoom(origin_media,scale=scale)
        self.scale = scale
        self.size = self.media.size
        self.filename = self.filepath.name()
        # 位置
        if type(pos) in [Pos,FreePos]:
            self.pos = pos
        else:
            self.pos = Pos(*pos)
        self.fileindex = 'AMfile_%d'% PrMediaClip.file_index
        # 序号
        PrMediaClip.file_index = PrMediaClip.file_index+1
    def display(self,begin,end,center='NA'):
        if center == 'NA':
            self.PRpos = self.PR_center_arg(np.array(self.size),np.array(self.pos.get()))
        else:
            self.PRpos = self.PR_center_arg(np.array(self.size),np.array(Pos(*eval(center)).get()))
        width,height = self.origin_size
        pr_horiz,pr_vert = self.PRpos
        clip_this = self.clip_tplt.format(**{'clipid':'AM_clip_%d'%PrMediaClip.clip_index,
                              'clipname':self.filename,
                              'timebase':'%d'%self.frame_rate,
                              'ntsc':self.Is_NTSC,
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
                              'vert':'%.5f'%pr_vert,
                              'scale':'%.2f'%(self.scale*100),
                              'colorlabel':self.label_color})
        PrMediaClip.clip_index = PrMediaClip.clip_index+1
        return clip_this
# 组合立绘
class GroupedAnimation(Animation):
    def __init__(self,subanimation_list,subanimation_current_pos=None,label_color='Mango'):
        ofile = self.output_path+'/auto_GA_%d'%PrMediaClip.outanime_index+'.png'
        canvas = Image.new(size=self.screen_size,mode='RGBA',color=(0,0,0,0))
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
                # 判断AM
                try:
                    if type(am_name) in [Animation,BuiltInAnimation,GroupedAnimation]:
                        subanimation = am_name
                    else: # type(am_name) is str
                        subanimation = eval(am_name)
                except NameError as E:
                    raise MediaError('Undef2GA', am_name )
                if am_pos is None:
                    # 打开 subanimation 的图片对象，将其按照self.pos, paste到canvas
                    canvas.paste(subanimation.media,subanimation.pos.get(),mask=subanimation.media)
                else:
                    # 打开 subanimation 的图片对象，将其按照am_pos, paste到canvas
                    canvas.paste(subanimation.media,am_pos,mask=subanimation.media)
        # 保存文件
        canvas.save(ofile)
        # 媒体参数
        self.filepath = Filepath(ofile)
        self.pos = Pos(0,0)
        self.path = self.filepath.xml_reformated()
        self.size = self.screen_size
        self.origin_size = self.size
        self.scale = 1
        self.filename = 'auto_GA_%d'%PrMediaClip.outanime_index+'.png'
        self.fileindex = 'AMfile_%d'% PrMediaClip.file_index
        self.label_color = label_color
        # 序号
        PrMediaClip.file_index = PrMediaClip.file_index+1
        PrMediaClip.outanime_index = PrMediaClip.outanime_index+1
# 内建动画
class BuiltInAnimation(Animation):
    def __init__(self,anime_type='hitpoint',anime_args=('0',0,0,0),screensize = (1920,1080),layer=0,label_color='Mango'):
        self.label_color = label_color
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
                self.pos = Pos((screensize[0]-max(nx,total_heart))/2,(4/5*screensize[1]-hy-ny)/2)
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
                self.pos = Pos((screensize[0]-total_heart)/2,3/5*screensize[1]+ny/2-hy/2)
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
                self.pos = Pos(heart_end//2*(hx + distance)+(heart_end%2)*int(hx/2)+(screensize[0]-total_heart)/2,3/5*screensize[1]+ny/2-hy/2)
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
            ofile = self.output_path+'/auto_BIA_%d'%PrMediaClip.outanime_index+'.png'
            canvas.save(ofile)
            #剩下的需要定义的
            self.filepath = Filepath(ofile)
            self.media = canvas
            self.path = self.filepath.xml_reformated() # 兼容动画Animation，只使用第一帧！
            self.scale = 1
            self.origin_size = self.size
            self.filename = self.filepath.name()
            self.fileindex = 'AMfile_%d'% PrMediaClip.file_index
            # 序号
            PrMediaClip.outanime_index = PrMediaClip.outanime_index+1
            PrMediaClip.file_index = PrMediaClip.file_index+1
        if anime_type == 'dice':
            for die in anime_args:
                try:
                    # 转换为int类型，NA转换为-1
                    name_tx,dice_max,dice_check,dice_face = die
                    dice_max,dice_face,dice_check = map(lambda x:-1 if x=='NA' else int(x),(dice_max,dice_face,dice_check))
                except ValueError as E: #too many values to unpack,not enough values to unpack
                    raise MediaError('[BIAnimeError]:','Invalid syntax:',str(die),E)
                if (dice_face>dice_max)|(dice_check<-1)|(dice_check>dice_max)|(dice_face<0)|(dice_max<=0):
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
                        #cx = p3 - p1
                        cy = p4 - p2
                        check_surf = test_canvas.crop((p1,p2,p3,p4))
                        canvas.paste(check_surf,(int(0.7292*screensize[0]),y_anchor+i*y_unit+(y_unit-cy)//2)) # 0.7292*screensize[0] = 1400
                self.size = self.screen_size
                self.pos = Pos(0,0)
            elif layer==1: #无法显示动态，留空白
                canvas = Image.new(mode='RGBA',size=(int(0.1458*screensize[0]),y_unit*N_dice),color=(0,0,0,0))
                self.size = (int(0.1458*screensize[0]),y_unit*N_dice)
                self.pos = Pos(int(0.5833*screensize[0]),y_anchor)
            elif layer==2:
                dice_cmap={3:(124,191,85,255),1:(94,188,235,255),0:(245,192,90,255),2:(233,86,85,255),-1:(255,255,255,255)}
                canvas = Image.new(mode='RGBA',size=(int(0.1458*screensize[0]),y_unit*N_dice),color=(0,0,0,0))
                self.size = (int(0.1458*screensize[0]),y_unit*N_dice)
                self.pos = Pos(int(0.5833*screensize[0]),y_anchor)
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
            ofile = self.output_path+'/auto_BIA_%d'%PrMediaClip.outanime_index+'.png'
            canvas.save(ofile)
            # 其他的
            self.filepath = Filepath(ofile)
            self.media = canvas
            self.path = self.filepath.xml_reformated() # 兼容动画Animation，只使用第一帧！
            self.scale = 1
            self.origin_size = self.size
            self.filename = self.filepath.name()
            self.fileindex = 'AMfile_%d'% PrMediaClip.file_index
            # self.PRpos = PR_center_arg(np.array(self.size),np.array(self.pos.get()))
            PrMediaClip.outanime_index = PrMediaClip.outanime_index+1
            PrMediaClip.file_index = PrMediaClip.file_index+1
# 音效
class Audio(PrMediaClip):
    def __init__(self,filepath,label_color='Caribbean'):
        super().__init__(filepath=filepath,label_color=label_color)
        self.path = self.filepath.xml_reformated()
        self.filename = self.filepath.name()
        self.fileindex = 'AUfile_%d'% PrMediaClip.file_index
        try:
            self.length = self.get_length(self.filepath.exact())*self.frame_rate
        except Exception as E:
            print(WarningPrint('BadAuLen',self.filepath.exact(),E))
            self.length = 0
        PrMediaClip.file_index = PrMediaClip.file_index+1
        
    def display(self,begin):
        clip_this = self.audio_clip_tplt.format(**{'clipid':'AU_clip_%d'%PrMediaClip.clip_index,
                                              'type':self.Audio_type,
                                              'clipname':self.filename,
                                              'audiolen':'%d'%self.length,
                                              'timebase':'%d'%self.frame_rate,
                                              'ntsc':self.Is_NTSC,
                                              'start':'%d'%begin,
                                              'end':'%d'%(begin+self.length),
                                              'in':'0',
                                              'out':'%d'%self.length,
                                              'fileid':self.fileindex,
                                              'filename':self.filename,
                                              'filepath':self.path,
                                              'colorlabel':self.label_color})
        PrMediaClip.clip_index = PrMediaClip.clip_index+1
        return clip_this
    def get_length(self,filepath):
        mixer.init()
        this_audio = mixer.Sound(filepath)
        return this_audio.get_length()
# 背景音乐
class BGM:
    def __init__(self,filepath,volume=100,loop=True,label_color='Forest'):
        print(WarningPrint('BGMIgnore',filepath))
    def convert(self):
        pass
