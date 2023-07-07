#!/usr/bin/env python
# coding: utf-8

# 媒体类定义

import numpy as np
import pygame
import pygame.freetype
import pydub
import re

from .FilePaths import Filepath
from .FreePos import Pos,FreePos
from .Exceptions import MediaError, WarningPrint
from .Formulas import sigmoid
from .Utils import hex_2_rgba
from .Regexs import RE_rich

# 主程序 replay_generator

# 媒体对象，所有媒体类的基类
class MediaObj:
    # 工程分辨率
    screen_size = (1920,1080)
    # 工程帧率
    frame_rate = 30
    # 输出路径
    output_path = '.'
    # 色图
    cmap = {
        'black':(0,0,0,255),'white':(255,255,255,255),
        'greenscreen':(0,177,64,255),
        'notetext':(118,185,0,255),'empty':(0,0,0,0)
        }
    # 导出PR项目相关的类变量
    # clip_XML 模板
    clip_tplt = open('./xml_templates/tplt_clip.xml','r',encoding='utf-8').read()
    audio_clip_tplt = open('./xml_templates/tplt_audio_clip.xml','r',encoding='utf-8').read()
    # PR 工程的项目参数
    Is_NTSC:bool = True
    Audio_type:str = 'Stereo'
    # 导出的序号
    outtext_index:int  = 0 # 文本图片序号，每输出一个文件 +1
    outanime_index:int = 0 # 立绘图片序号，每输出一个文件 +1
    clip_index:int     = 0     # 剪辑序号，每生成一个剪辑 +1
    file_index:int     = 0     # 文件序号，每载入一个文件 +1
    # 是否导出PR项目素材
    export_xml:bool = False # PR序列是否初始化
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
    # 导入图片
    def load_image(self,scale:float):
        # 读取图片文件
        origin_media = pygame.image.load(self.filepath.exact())
        self.origin_size:tuple = origin_media.get_size()
        self.media:pygame.Surface = self.zoom(origin_media,scale=scale)
        self.size:tuple = self.media.get_size()
        self.scale:float  = scale
    # 初始化为PR序列
    def PR_init(self,file_index:str='None') -> None:
        if self.export_xml ==  False:
            pass
        elif file_index == 'None':
            self.xmlpath:str = None
            self.filename:str = None
            self.fileindex = None
        else:
            self.xmlpath:str = self.filepath.xml_reformated()
            self.filename:str = self.filepath.name()
            self.fileindex = file_index % MediaObj.file_index
            MediaObj.file_index = MediaObj.file_index + 1
    # 处理PR的图片坐标
    def PR_center_arg(self,obj_size,pygame_pos) -> np.ndarray:
        screensize = np.array(self.screen_size)
        return (pygame_pos+obj_size/2-screensize/2)/obj_size*self.scale
    # 预览
    def preview(self, surface:pygame.Surface):
        self.display(surface)
    # 转换媒体，仅图像媒体类需要
    def convert(self):
        pass
    # 获取所有点
    def get_pos(self) -> dict:
        return {}
    # 在对象实例化后修改参数
    def configure(self,key:str,value,index:int=0):
        if key == 'filepath':
            # 文件路径是非法关键字
            if (value is None) or (value == 'None') or (value in self.cmap.keys()):
                self.filepath = None
            # 否则是一个Filepath 对象
            else:
                self.filepath = Filepath(filepath=value)
        elif key == 'pos':
            if type(value) in [Pos,FreePos]:
                self.pos = value
            else:
                self.pos = Pos(*value)
        elif key == 'scale':
            self.scale = value
            if self.filepath:
                self.load_image(scale=self.scale)
        else:
            try:
                self.__setattr__(key,value)
            except AttributeError:
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
    # 获取原始文本
    def raw(self,tx:str)->tuple:
        return tx, [x for x in range(0,len(tx)+1)]
    # 渲染一行
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
    # 预览
    def preview(self, surface:pygame.Surface):
        # 测试文本
        test_text = ("测1试Te2st文3本Te4xt" * (self.line_limit//16+1))[0:self.line_limit]
        text_surf:pygame.Surface = self.draw(test_text)[0]
        # 尺寸
        w,h = text_surf.get_size()
        W,H = surface.get_size()
        # 显示在正中间
        surface.blit(text_surf,((W-w)/2,(H-h)/2))
    # 修改
    def configure(self, key: str, value, index: int = 0):
        if key == 'fontfile':
            super().configure(key='filepath',value=value)
            self.text_render = pygame.font.Font(self.filepath.exact(), self.size)
        elif key == 'fontsize':
            self.size = value
            self.text_render = pygame.font.Font(self.filepath.exact(), self.size)
        else:
            # 继承
            super().configure(key, value, index)
# 描边文本
class StrokeText(Text):
    pygame.font.init()
    def __init__(self,fontfile='./media/SourceHanSansCN-Regular.otf',fontsize=40,color=(0,0,0,255),line_limit=20,edge_color=(255,255,255,255),edge_width=1,projection='C',label_color='Lavender'):
        super().__init__(fontfile=fontfile,fontsize=fontsize,color=color,line_limit=line_limit,label_color=label_color) # 继承
        # 描边颜色
        self.edge_color = edge_color
        # 投影方向
        self.projection_dict = {
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
        if projection in self.projection_dict.keys():
            self.projection = projection
        else:
            self.projection = 'C'
        # 描边宽度
        try:
            self.edge_width = int(edge_width)
        except ValueError:
            raise MediaError("InvEgWd",edge_width)
        if self.edge_width < 0:
            raise MediaError("InvEgWd",edge_width)
        elif self.edge_width > 3:
            print(WarningPrint('WideEdge'))
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
        canvas.blit(face,(ew,ew)-self.projection_dict[self.projection]*(ew-1))
        # bug：受限于pygame的性能，无法正确的表现透明度不同的描边和字体，但在导出PR项目时是正常的
        if (self.color[3] < 255) | (self.edge_color[3] < 255):
            # 按照透明度的最小值显示
            min_alpha = min(self.color[3],self.edge_color[3])
            canvas.set_alpha(min_alpha)
        return canvas

# 富文本
class RichText(Text):
    def __init__(self,fontfile='./media/SourceHanSansCN-Regular.otf',fontsize=40,color=(0,0,0,255),line_limit=20,label_color='Lavender'):
        super().__init__(fontfile=fontfile,fontsize=fontsize,color=color,line_limit=line_limit,label_color=label_color) # 继承
    def raw(self, tx:str):
        # 原始文本：
        pattern = RE_rich
        cells = pattern.split(tx)
        raw_text = ""
        idx_map = [0]
        this = 0
        for cell in cells:
            # this是目前这一句开头的位置
            length = len(cell)
            if cell == '[^]':
                raw_text += '^'
                idx_map.append(this+length)
            elif re.match('\[[\#prn]\]',cell):
                raw_text += '#'
                idx_map.append(this+length)
            elif pattern.match(cell):
                pass
            else:
                raw_text += cell
                idx_map += [x for x in range(this+1,this+length+1)]
            this += length
        return raw_text, idx_map
    def render(self,tx:str,riches:dict)->pygame.Surface:
        # 字号
        if riches['fs'] != None and riches['fs'] != self.size:
            fontsize = int(riches['fs'])
            text_render_obj = pygame.font.Font(self.filepath.exact(),fontsize)
        else:
            fontsize = self.size
            text_render_obj = self.text_render
        # 粗体、斜体、下划线
        text_render_obj.set_bold(riches['b'])
        text_render_obj.set_italic(riches['i'])
        text_render_obj.set_underline(riches['u'])
        # 前景
        if riches['fg'] != None:
            fgcolor = hex_2_rgba(riches['fg'])
        else:
            fgcolor = self.color
        # 渲染
        face = text_render_obj.render(tx,True,fgcolor[0:3])
        # 删除线
        if riches['x'] == True:
            w,h = face.get_size()
            pygame.draw.line(face,color=fgcolor[0:3],start_pos=(0,h/2),end_pos=(w,h/2),width=int(fontsize/15))
        # 前景的透明度
        if fgcolor[3] < 255:
            face.set_alpha(fgcolor[3])
        # 背景
        if riches['bg'] != None:
            bgcolor = hex_2_rgba(riches['bg'])
            back = pygame.surface.Surface(face.get_size(),pygame.SRCALPHA)
            back.fill(bgcolor)
            back.blit(face,(0,0))
        else:
            back = face
        return back
    def renderline(self,list_of_cell:list)->pygame.Surface:
        total_width = sum([surf.get_width() for surf in list_of_cell])
        max_height = max([surf.get_height() for surf in list_of_cell])
        result_surf = pygame.Surface((total_width, max_height), pygame.SRCALPHA)
        # 使用 blit() 函数将每个表面绘制到新表面上
        x = 0
        for surf in list_of_cell:
            result_surf.blit(surf, (x, (max_height - surf.get_height())//2))
            x += surf.get_width()
        return result_surf

    def draw(self,text:str)->list:
        # 每次draw的时候，重置一次
        self.riches = {
            'b' : False,
            'u' : False,
            'i' : False,
            'x' : False,
            'fs': None,
            'fg': None,
            'bg': None
        }
        self.manual = False
        # 
        pattern = RE_rich
        cells = pattern.split(text)
        line_cells = []
        len_of_line = 0
        out_text = []
        for cell in cells:
            if pattern.match(cell):
                # a rich label
                if self.parse_richlabel(cell):
                    # 是否是换行命令，或是遍历已达结尾
                    self.manual = True
                    out_text.append(self.renderline(line_cells))
                    line_cells.clear()
                    len_of_line = 0
            else:
                if (len(cell) + len_of_line < self.line_limit) or (self.manual == True):
                    # 如果当前行字数未超过限制，或者是手动换行模式，则延长行
                    line_cells.append(self.render(cell,self.riches))
                    len_of_line += len(cell)
                else:
                    # 否则就截断，自动换行
                    tail_count = self.line_limit - len_of_line
                    line_cells.append(self.render(cell[:tail_count],self.riches))
                    # 换行并输出
                    out_text.append(self.renderline(line_cells))
                    line_cells.clear()
                    # 后半段
                    line_cells.append(self.render(cell[tail_count:],self.riches))
                    len_of_line = len(cell[tail_count:])
        # 收尾工作
        out_text.append(self.renderline(line_cells))
        return out_text

    def parse_richlabel(self,richlabel:str)->bool:
        content = richlabel[1:-1]
        # 减法标签
        if content[0] == '/':
            command = content[1:]
            if command in ['b','u','i','x']:
                self.riches[command] = False
            elif command in ['fs','fg','bg']:
                self.riches[command] = None
            elif command in ['a']:
                self.riches = {
                    'b' : False,
                    'u' : False,
                    'i' : False,
                    'x' : False,
                    'fs': None,
                    'fg': None,
                    'bg': None
                }
            else:
                WarningPrint('InvRichlab', richlabel)
        # 加法标签
        else:
            # 拆分参数
            if ':' in content:
                command,arg = content.split(':')
            else:
                command,arg = content,None
            if command in ['b','u','i','x']:
                self.riches[command] = True
            elif command in ['fs','fg','bg']:
                self.riches[command] = arg
            elif command in ['r','n','p','#']:
                return True
            elif command in ['^']:
                self.manual = True
            else:
                WarningPrint('InvRichlab', richlabel)
        return False

# 气泡
class Bubble(MediaObj):                                   
    # 初始化
    def __init__(
            self,
            filepath:str     = None,
            scale:float      = 1.0,
            Main_Text:Text   = Text(),
            Header_Text:Text = None,
            pos:tuple        = (0,0),
            mt_pos:tuple     = (0,0),
            ht_pos:tuple     = (0,0),
            ht_target:str    = 'Name',
            align:str        = 'left',
            line_distance:float = 1.5,
            label_color:str  = 'Lavender'
            ):
        # 媒体和路径
        super().__init__(filepath=filepath,label_color=label_color)
        # 气泡底图
        if self.filepath is None:
            # 媒体设为空图
            self.media = pygame.Surface(self.screen_size,pygame.SRCALPHA)
            self.media.fill(self.cmap['empty'])
            # 尺寸和缩放
            self.scale:float = 1.0
            self.size:tuple = self.screen_size
            self.origin_size:tuple = self.size
            # PR项目
            self.PR_init('None')
        else:
            # 读取图片文件
            self.load_image(scale=scale)
            # 其他参数
            self.PR_init(file_index='BBfile_%d')
        # 底图位置
        if type(pos) in [Pos,FreePos]:
            self.pos = pos
        else:
            self.pos = Pos(*pos)
        # 主文本和头文本
        self.MainText:Text = Main_Text
        self.mt_pos:tuple  = mt_pos # 只可以是tuple
        self.Header:Text   = Header_Text
        self.ht_pos:tuple  = ht_pos # 只可以是tuple or list tuple
        self.target:str    = ht_target
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
    # 主文本效果，裁切
    def tx_effect(self,main_text:str,effect:float=np.nan)->str:
        # 效果
        if effect >= 0:
            return main_text[:int(effect)]
        else:
            return main_text
    # 主文本和头文本的记录
    def recode(self,main_text:str,header_text:str)->None:
        self.main_text = main_text
        self.header_text = header_text
    # (气泡:surface, 文本:surface, size:tuple)
    def draw(self, text:str, header:str='',effect:float=np.nan)->tuple:
        # 文本画板:和底图相同的大小
        temp = pygame.Surface(self.size,pygame.SRCALPHA)
        temp.fill(self.cmap['empty'])
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
        return (self.media.copy(), temp, self.size)
    # 将气泡对象丢上主Surface
    def display(self, surface:pygame.surface, text:str, header:str='',effect:float=np.nan,alpha:int=100,center:str='NA',adjust:str='NA'):
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
        bubble_draw,text_draw,bubble_size = self.draw(text,header,effect)
        bubble_draw.blit(text_draw,(0,0))
        # 将Bubble blit 到 surface
        if alpha !=100:
            bubble_draw.set_alpha(alpha/100*255)
        surface.blit(bubble_draw,render_pos.get())
    # 导出PR序列：tuple(str|None, str)
    def export(self, begin:int, end:int, text:str, header:str='', center='NA') -> tuple:
        # PR 中的位置
        if center == 'NA':
            self.PRpos = self.PR_center_arg(np.array(self.size),np.array(self.pos.get()))
        else:
            self.PRpos = self.PR_center_arg(np.array(self.size),np.array(Pos(*eval(center)).get()))
        # 渲染画面
        bubble_draw,text_draw,bubble_size = self.draw(text,header,effect=np.nan)
        # 气泡序列
        width,height = self.origin_size
        pr_horiz,pr_vert = self.PRpos
        if self.xmlpath is None:
            clip_bubble = None
        else:
            clip_bubble = self.clip_tplt.format(**{
                'clipid'    : 'BB_clip_%d'%MediaObj.clip_index,
                'clipname'  : self.filename,
                'timebase'  : '%d'%self.frame_rate,
                'ntsc'      : self.Is_NTSC,
                'start'     : '%d'%begin,
                'end'       : '%d'%end,
                'in'        : '%d'%90000,
                'out'       : '%d'%(90000+end-begin),
                'fileid'    : self.fileindex,
                'filename'  : self.filename,
                'filepath'  : self.xmlpath,
                'filewidth' : '%d'%width,
                'fileheight': '%d'%height,
                'horiz'     : '%.5f'%pr_horiz,
                'vert'      : '%.5f'%pr_vert,
                'scale'     : '%.2f'%(self.scale*100),
                'colorlabel': self.label_color
                })
        # 文本序列:导出文件
        text_ofile:str = self.output_path+'/auto_TX_%d'%MediaObj.outtext_index+'.png'
        pygame.image.save(text_draw,text_ofile)
        clip_text = self.clip_tplt.format(**{
            'clipid'    : 'TX_clip_%d'%MediaObj.clip_index,
            'clipname'  : 'auto_TX_%d.png'%MediaObj.outtext_index,
            'timebase'  : '%d'%self.frame_rate,
            'ntsc'      : self.Is_NTSC,
            'start'     : '%d'%begin,
            'end'       : '%d'%end,
            'in'        : '%d'%90000,
            'out'       : '%d'%(90000+end-begin),
            'fileid'    : 'auto_TX_%d'%MediaObj.outtext_index,
            'filename'  : 'auto_TX_%d.png'%MediaObj.outtext_index,
            'filepath'  : Filepath(text_ofile).xml_reformated(),
            'filewidth' : '%d'%width,
            'fileheight': '%d'%height,
            'horiz'     : '%.5f'%pr_horiz,
            'vert'      : '%.5f'%pr_vert,
            'scale'     : 100,
            'colorlabel': self.MainText.label_color})
        # 更新序号
        MediaObj.outtext_index = MediaObj.outtext_index + 1
        MediaObj.clip_index = MediaObj.clip_index + 1
        # 返回
        return (clip_bubble, clip_text)
    # GUI预览
    def test_maintext(self, lines=4):
        # 主文本
        if self.MainText is not None:
            line1 = ((self.MainText.line_limit//lines+1)*"测试文本")
            if type(self.MainText) is RichText:
                richlabels = ['[u]','[i]','[b]','[fg:#ff5555][bg:#cccccc]']
                test_text = '[^]'
                for k in range(0,lines):
                    test_text += richlabels[k]+line1[0:self.MainText.line_limit*(lines-k)//lines]+'[#]'
            else:
                test_text = ''
                for k in range(0,lines):
                    test_text += line1[0:self.MainText.line_limit*(lines-k)//lines]+'#'
                test_text = test_text[:-1]
        else:
            test_text = ''
        return test_text
    def test_header(self):
        if self.Header is not None:
            test_head = ((self.Header.line_limit//4+1)*"测试文本")[0:self.Header.line_limit]
        else:
            test_head = ''
        return test_head
    def preview(self, surface: pygame.Surface, key=None):
        # 主文本
        test_text = self.test_maintext()
        # 头文本
        test_head = self.test_header()
        self.display(surface, text=test_text, header=test_head)
    # 转换媒体对象
    def convert(self):
        self.media = self.media.convert_alpha()
    # 获取所有点
    def get_pos(self) -> dict:
        pos_dict = {
            'green': {
                'g0':{
                    'pos' : self.pos.get(),
                    'scale' : (self.pos + self.media.get_size()).get()
                }
            },
            'blue':{
            }
        }
        if self.MainText:
            pos_dict['blue']['b0'] = {}
            pos_dict['blue']['b0']['mt_pos'] = self.mt_pos
            pos_dict['blue']['b0']['mt_end'] = (
                    self.mt_pos[0] + self.MainText.line_limit*self.MainText.size,
                    self.mt_pos[1] + self.line_distance*self.MainText.size*4
                )
        if type(self.Header) in [Text, StrokeText, RichText]:
            pos_dict['blue']['b1'] = {}
            pos_dict['blue']['b1']['ht_pos'] = self.ht_pos
            pos_dict['blue']['b1']['ht_end'] = (
                    self.ht_pos[0] + self.Header.line_limit*self.Header.size,
                    self.ht_pos[1] + self.Header.size * 1.5
                )
        return pos_dict
    # 修改
    def configure(self, key: str, value, index: int = 0):
        # 底图
        if key == 'filepath':
            super().configure(key, value, index)
            # 底图的初始化
            # 气泡底图
            if self.filepath is None:
                # 媒体设为空图
                self.media = pygame.Surface(self.screen_size,pygame.SRCALPHA)
                self.media.fill(self.cmap['empty'])
                # 尺寸和缩放
                self.scale:float = 1.0
                self.size:tuple = self.screen_size
                self.origin_size:tuple = self.size
            else:
                # 读取图片文件
                self.load_image(scale=self.scale)
        elif key == 'Main_Text':
            self.MainText = value
        elif key == 'Header_Text':
            self.Header = value
        elif key == 'ht_target':
            self.target = value
        else:
            super().configure(key, value, index)

# 气球
class Balloon(Bubble):
    def __init__(
            self,
            filepath:str     = None,
            scale:float      = 1.0,
            Main_Text:Text   = Text(),
            Header_Text:list = [None],
            pos:tuple        = (0,0),
            mt_pos:tuple     = (0,0),
            ht_pos:list      = [(0,0)],
            ht_target:list   = ['Name'],
            align:str        = 'left',
            line_distance:float = 1.5,
            label_color:str  = 'Lavender'
            ):
        # 继承Bubble
        super().__init__(filepath=filepath,scale=scale,Main_Text=Main_Text,Header_Text=Header_Text,pos=pos,mt_pos=mt_pos,ht_pos=ht_pos,ht_target=ht_target,align=align,line_distance=line_distance,label_color=label_color)
        # 检查头文本列表长度是否匹配
        if len(self.Header)!=len(self.ht_pos) or len(self.Header)!=len(self.target):
            raise MediaError('BnHead')
        else:
            self.header_num = len(self.Header)
    # 重载draw: -> (气泡:surface, 文本:surface, size:tuple)
    def draw(self, text:str, header:str='', effect:float=np.nan)->tuple: 
        # 文本画板:和底图相同的大小
        temp =  pygame.Surface(self.size,pygame.SRCALPHA)
        temp.fill(self.cmap['empty'])
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
        return (self.media.copy(), temp, self.size)
    # 重载preview
    def test_header(self):
        test_head = []
        for header_this in self.Header:
            if header_this is not None:
                test_head.append(((header_this.line_limit//4+1)*"测试文本")[0:header_this.line_limit])
            else:
                test_head.append('')
        test_head = '|'.join(test_head)
        return test_head
    def get_pos(self) -> dict:
        pos_dict = super().get_pos()
        for i, HT in enumerate(self.Header):
            if type(HT) in [Text, StrokeText, RichText]:
                pos_dict['blue'][f'b{str(i+1)}'] = {}
                pos_dict['blue'][f'b{str(i+1)}']['ht_pos'] = self.ht_pos[i]
                pos_dict['blue'][f'b{str(i+1)}']['ht_end'] = (
                        self.ht_pos[i][0] + HT.line_limit * HT.size,
                        self.ht_pos[i][1] + HT.size * 1.5
                    )
        return pos_dict
    def configure(self, key: str, value, index: int = 0):
        # if key == 'Header_Text':
        #     if index >= len(self.Header):
        #         self.Header.append(value)
        #     else:
        #         self.Header[index] = value
        # elif key == 'ht_target':
        #     if index >= len(self.target):
        #         self.target.append(value)
        #     else:
        #         self.target[index] = value
        # elif key == 'ht_pos':
        #     if index >= len(self.ht_pos):
        #         self.target.append(tuple(value))
        #     else:
        #         self.ht_pos[index] = value
        # 暂时禁用index，代价是性能
        if key == 'Header_Text':
            self.Header = value
        elif key == 'ht_target':
            self.target = value
        elif key == 'ht_pos':
            self.ht_pos = value
        else:
            super().configure(key, value, index)
    def clear_configure(self,key:str):
        if key == 'Header_Text':
            self.Header.clear()
        elif key == 'ht_target':
            self.target.clear()
        elif key == 'ht_pos':
            self.ht_pos.clear()
# 自适应气泡
class DynamicBubble(Bubble):
    def __init__(
            self,
            filepath:str     = None,
            scale:float      = 1.0,
            Main_Text:Text   = Text(),
            Header_Text:Text = None,
            pos:tuple        = (0,0),
            mt_pos:tuple     = (0,0),
            mt_end:tuple     = (0,0),
            ht_pos:tuple     = (0,0),
            ht_target:str    = 'Name',
            fill_mode:str    = 'stretch',
            fit_axis:str     = 'free',
            line_distance:float = 1.5,
            label_color:str  = 'Lavender'
            ):
        # 继承：Bubble
        super().__init__(filepath=filepath,scale=scale,Main_Text=Main_Text,Header_Text=Header_Text,pos=pos,mt_pos=mt_pos,ht_pos=ht_pos,ht_target=ht_target,line_distance=line_distance,label_color=label_color)
        # 检查气泡分割位置的合法性
        if (mt_pos[0] >= mt_end[0]) | (mt_pos[1] >= mt_end[1]) | (mt_end[0] > self.media.get_size()[0]) | (mt_end[1] > self.media.get_size()[1]):
            raise MediaError('InvSep','mt_end')
        elif (mt_pos[0] < 0) | (mt_pos[1] < 0):
            raise MediaError('InvSep','mt_pos')
        else:
            self.mt_end:tuple = mt_end
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
        # 初始化切片
        self.clip_init()
    # 初始化切片
    def clip_init(self):
        # x,y轴上的四条分割线
        self.x_tick:list = [0,self.mt_pos[0],self.mt_end[0],self.size[0]]
        self.y_tick:list = [0,self.mt_pos[1],self.mt_end[1],self.size[1]]
        # 以np.array的形式存储气泡的9个切片
        self.bubble_clip = []
        # 0 3 6
        # 1 4 7
        # 2 5 8
        for i in range(0,3):
            for j in range(0,3):
                self.bubble_clip.append(self.media.subsurface((
                    self.x_tick[i],
                    self.y_tick[j],
                    self.x_tick[i+1]-self.x_tick[i],
                    self.y_tick[j+1]-self.y_tick[j]
                    )))
        self.bubble_clip:np.ndarray = np.array(self.bubble_clip)
        # 注意，这9个碎片有的尺寸有可能为0！这种情况是能够兼容的。
        self.bubble_clip_size:np.ndarray = np.frompyfunc(lambda x:x.get_size(),1,1)(self.bubble_clip)
    # 重载draw
    def draw(self, text:str, header:str='', effect:float=np.nan) -> tuple:
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
        # 
        bubble_temp = pygame.Surface((temp_size_x,temp_size_y),pygame.SRCALPHA)
        bubble_temp.fill((0,0,0,0))
        text_temp = bubble_temp.copy()
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
                    bubble_temp.blit(self.bubble_clip[i],bubble_clip_pos[i])
                else:
                    if self.fill_mode == 'stretch':
                        bubble_temp.blit(pygame.transform.scale(self.bubble_clip[i],bubble_clip_scale[i]),bubble_clip_pos[i])
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
                        bubble_temp.blit(collage,bubble_clip_pos[i])
        # 第二次循环：把主文本blit到临时容器
        for i,text_surf in enumerate(main_text_list):
            text_temp.blit(text_surf,(self.x_tick[1],self.y_tick[1]+i*self.MainText.size*self.line_distance))
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
            text_temp.blit(self.Header.draw(header)[0],(ht_renderpos_x,ht_renderpos_y))
        return (bubble_temp, text_temp, (temp_size_x,temp_size_y))
    # 导出PR序列：
    def export(self, begin: int, end: int, text: str, header: str = '', center='NA') -> tuple:
        # 渲染画面
        bubble_draw,text_draw,bubble_size = self.draw(text,header,effect=np.nan)
        # 获取动态气泡的参数
        width,height = bubble_size
        # PR 中的位置
        if center == 'NA':
            self.PRpos = self.PR_center_arg(np.array(bubble_size),np.array(self.pos.get()))
        else:
            self.PRpos = self.PR_center_arg(np.array(bubble_size),np.array(Pos(*eval(center)).get()))
        pr_horiz,pr_vert = self.PRpos
        # 气泡序列
        if self.xmlpath is None:
            clip_bubble = None
        else:
            # 自适应气泡不采用 self.fileindex
            bubble_ofile:str = self.output_path+'/auto_BB_%d'%MediaObj.outtext_index+'.png'
            pygame.image.save(bubble_draw,bubble_ofile)
            clip_bubble = self.clip_tplt.format(**{
                'clipid'    : 'BB_clip_%d'%MediaObj.clip_index,
                'clipname'  : 'auto_BB_%d.png'%MediaObj.outtext_index,
                'timebase'  : '%d'%self.frame_rate,
                'ntsc'      : self.Is_NTSC,
                'start'     : '%d'%begin,
                'end'       : '%d'%end,
                'in'        : '%d'%90000,
                'out'       : '%d'%(90000+end-begin),
                'fileid'    : 'auto_BB_%d'%MediaObj.outtext_index,
                'filename'  : 'auto_BB_%d.png'%MediaObj.outtext_index,
                'filepath'  : Filepath(bubble_ofile).xml_reformated(),
                'filewidth' : '%d'%width,
                'fileheight': '%d'%height,
                'horiz'     : '%.5f'%pr_horiz,
                'vert'      : '%.5f'%pr_vert,
                'scale'     : 100,
                'colorlabel': self.label_color
                })
        # 文本序列:导出文件
        text_ofile:str = self.output_path+'/auto_TX_%d'%MediaObj.outtext_index+'.png'
        pygame.image.save(text_draw,text_ofile)
        clip_text = self.clip_tplt.format(**{
            'clipid'    : 'TX_clip_%d'%MediaObj.clip_index,
            'clipname'  : 'auto_TX_%d.png'%MediaObj.outtext_index,
            'timebase'  : '%d'%self.frame_rate,
            'ntsc'      : self.Is_NTSC,
            'start'     : '%d'%begin,
            'end'       : '%d'%end,
            'in'        : '%d'%90000,
            'out'       : '%d'%(90000+end-begin),
            'fileid'    : 'auto_TX_%d'%MediaObj.outtext_index,
            'filename'  : 'auto_TX_%d.png'%MediaObj.outtext_index,
            'filepath'  : Filepath(text_ofile).xml_reformated(),
            'filewidth' : '%d'%width,
            'fileheight': '%d'%height,
            'horiz'     : '%.5f'%pr_horiz,
            'vert'      : '%.5f'%pr_vert,
            'scale'     : 100,
            'colorlabel': self.MainText.label_color})
        # 更新序号
        MediaObj.outtext_index = MediaObj.outtext_index + 1
        MediaObj.clip_index = MediaObj.clip_index + 1
        # 返回
        return (clip_bubble, clip_text)
    def convert(self): # 和Animation类相同的convert
        super().convert()
        self.bubble_clip = np.frompyfunc(lambda x:x.convert_alpha(),1,1)(self.bubble_clip)
    # 预览
    def preview(self, surface: pygame.Surface, key='#edit'):
        if key is None:
            # 主文本
            test_text = self.test_maintext(lines=np.random.randint(1,5))
            # 头文本
            test_head = self.test_header()
            self.display(surface, text=test_text, header=test_head)
        else:
            surface.blit(self.media,self.pos.get())
    def get_pos(self) -> dict:
        pos_dict = {
            'green': {
                'g0':{
                    'pos' : self.pos.get(),
                    'scale' : (self.pos + self.media.get_size()).get()
                }
            },
            'magenta':{
                'm0':{
                    'mt_pos' : self.mt_pos,
                    'mt_end' : self.mt_end,
                }
            },
        }
        blue_dot = {}
        # 如果有头文本
        if type(self.Header) in [Text, StrokeText, RichText]:
            blue_dot['b1'] = {}
            blue_dot['b1']['ht_pos'] = self.ht_pos
            blue_dot['b1']['ht_end'] = (
                    self.ht_pos[0] + self.Header.line_limit*self.Header.size,
                    self.ht_pos[1] + self.Header.size * 1.5
                )
            pos_dict['blue'] = blue_dot
        return pos_dict
    # 调整
    def configure(self, key: str, value, index: int = 0):
        if key == 'fit_axis':
            self.horizontal,self.vertical = {'free':(1,1),'vertical':(0,1),'horizontal':(1,0)}[value]
        else:
            super().configure(key, value, index)
            # 如果涉及到分割线，那么重新初始化分割线
            if key in ['filepath','scale','mt_pos','mt_end']:
                self.clip_init()
# 聊天窗
class ChatWindow(Bubble):
    def __init__(
            self,
            filepath:str     = None,
            scale:float      = 1.0,
            sub_key:list     = ['Key1'],
            sub_Bubble:list  = [Bubble()],
            sub_Anime:list   = [None],
            sub_align:list   = ['left'],
            pos:tuple        = (0,0),
            sub_pos:tuple    = (0,0),
            sub_end:tuple    = (0,0),
            am_left:int      = 0,
            am_right:int     = 0,
            sub_distance:int = 50,
            label_color:str  = 'Lavender'
            ):
        # 媒体和路径
        MediaObj.__init__(self,filepath=filepath,label_color=label_color)
        # 气泡底图
        if self.filepath is None: # 支持气泡图缺省
            # 媒体设为空图
            self.media = pygame.Surface(self.screen_size,pygame.SRCALPHA)
            self.media.fill(self.cmap['empty'])
            # 其他参数
            self.scale:float = 1.0
            self.size:tuple = self.screen_size
            self.origin_size:tuple = self.size
            self.PR_init('None')
        else:
            # 读取图片文件
            self.load_image(scale=scale)
            self.PR_init('BBfile_%d')
        # 位置
        if type(pos) in [Pos,FreePos]:
            self.pos = pos
        else:
            self.pos = Pos(*pos)
        # 检查子气泡和key是否是能匹配
        if len(sub_Bubble) != len(sub_key):
            raise MediaError('CWKeyLen')
        # 子气泡和对齐
        self.sub_key = sub_key
        self.sub_Bubble = {}
        self.sub_Anime = {}
        self.sub_align = {}
        for i,key in enumerate(self.sub_key):
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
        test_subsurface_size = self.sub_Bubble[sub_key[0]].draw(' ')[2]
        # 按照最小子气泡图层的高度 + sub_distance 作为一个单位长度
        self.max_recode = np.ceil(self.sub_size[1]/(test_subsurface_size[1] + self.sub_distance))
        # 留下一个MainText 以供 labelcolor 参考
        self.MainText = self.sub_Bubble[sub_key[0]].MainText
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
    def draw(self, text:str,header:str='',effect:float=np.nan)->tuple:
        # 文本画板:和底图相同的大小
        temp = pygame.Surface(self.size,pygame.SRCALPHA)
        temp.fill(self.cmap['empty'])
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
            subbubble_surface_this,subtext_surface,subbubble_surface_size = self.sub_Bubble[key_this].draw(main_this,header_this)
            subbubble_surface_this.blit(subtext_surface,(0,0))
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
        return (self.media.copy(), temp, self.size)
    # 预览
    def preview(self, surface: pygame.Surface, key=None):
        # 主文本
        test_maintext = []
        test_header = []
        if key in self.sub_Bubble.keys():
            bubble_this:Bubble = self.sub_Bubble[key]
            test_maintext.append(bubble_this.test_maintext(lines=2))
            test_header.append(key+'#'+bubble_this.test_header()) # 需要注意的是，Balloon不可以作为ChatWindow的成员！
        else:
            for key in self.sub_Bubble.keys():
                bubble_this:Bubble = self.sub_Bubble[key]
                test_maintext.append(bubble_this.test_maintext(lines=2))
                test_header.append(key+'#'+bubble_this.test_header()) # 需要注意的是，Balloon不可以作为ChatWindow的成员！
        # 组合
        test_maintext = '|'.join(test_maintext)
        test_header = '|'.join(test_header)
        # 显示
        self.display(surface=surface, text=test_maintext, header=test_header)
    def get_pos(self) -> dict:
        pos_dict = {
            'green': {
                'g0':{
                    'pos' : self.pos.get(),
                    'scale' : (self.pos + self.media.get_size()).get()
                }
            },
            'purple':{
                'p0':{
                    'sub_pos' : self.sub_pos,
                    'sub_end' : (self.sub_pos[0]+self.sub_size[0], self.sub_pos[1]+self.sub_size[1]),
                }
            },
            'red' :{
                'r0':{
                    'am_left' : (self.am_left,0),
                },
                'r1':{
                    'am_right': (self.am_right,0),
                }
            }
        }
        return pos_dict
    # 修改
    def configure(self, key: str, value, index: int = 0):
        if key == 'sub_pos':
            self.sub_size = (self.sub_pos[0] + self.sub_size[0] - value[0], self.sub_pos[1] + self.sub_size[1] - value[1])
            self.sub_pos = value
        elif key == 'sub_end':
            self.sub_size = (value[0]-self.sub_pos[0],value[1]-self.sub_pos[1])
        # 关键词参数们:
        # elif key == 'sub_key':
        #     try:
        #         self.sub_key[index] = value
        #     except IndexError:
        #         self.sub_key.append(value)
        # elif key == 'sub_Bubble':
        #     keyword = self.sub_key[index]
        #     self.sub_Bubble[keyword] = value
        # elif key == 'sub_Anime':
        #     keyword = self.sub_key[index]
        #     self.sub_Anime[keyword] = value
        # elif key == 'sub_align':
        #     keyword = self.sub_key[index]
        #     self.sub_align[keyword] = value
        elif key == 'sub_key':
            # 变更关键
            for idx,keyword in enumerate(key):
                # 长度超出原来的关键字
                if idx >= len(self.sub_key):
                    self.sub_key.append(keyword)
                # 关键字发生变动
                elif keyword != self.sub_key[idx]:
                    self.sub_Bubble[keyword] = self.sub_Bubble.pop(self.sub_key[idx])
                    self.sub_Anime[keyword] = self.sub_Anime.pop(self.sub_key[idx])
                    self.sub_align[keyword] = self.sub_align.pop(self.sub_key[idx])
                    self.sub_key[idx] = keyword
                # 无事发生
                else:
                    pass
        elif key in ['sub_Bubble','sub_Anime','sub_align']:
            self.clear_configure(key=key)
            for idx,ele in enumerate(value):
                if idx >= len(self.sub_key):
                    break
                else:
                    keyword = self.sub_key[idx]
                    self.__getattribute__(key)[keyword] = ele
        else:
            super().configure(key, value, index)
    def clear_configure(self,key:str):
        if key in ['sub_key','sub_Bubble','sub_Anime','sub_align']:
            self.__getattribute__(key).clear()
# 背景
class Background(MediaObj):
    def __init__(
            self,
            filepath:str     ,
            scale:float      = 1.0,
            pos:tuple        = (0,0),
            label_color:str  = 'Lavender'
            ):
        # 文件和路径
        super().__init__(filepath=filepath,label_color=label_color)
        if filepath in self.cmap.keys():
            # 填充纯色
            self.media = pygame.Surface(self.screen_size,pygame.SRCALPHA)
            self.media.fill(self.cmap[filepath])
            # 其他参数
            self.scale:float = 1.0
            self.size:tuple  = self.screen_size
            self.origin_size:tuple = self.size
        else:
            # 读取图片文件
            self.load_image(scale=scale)
        # 路径
        self.PR_init(filepath,'BGfile_%d')
        # 位置
        if type(pos) in [Pos,FreePos]:
            self.pos = pos
        else:
            self.pos = Pos(*pos)
    def PR_init(self,imgfile:str,file_index: str = 'None') -> None:
        # 如果不导出PR项目，那么什么都不做
        if self.export_xml == False:
            pass
        # 如果没有输入文件，而是输入的颜色标签，则将纯色背景保存为文件
        elif self.filepath is None:
            ofile = self.output_path+'/auto_BG_'+imgfile+'.png'
            pygame.image.save(self.media,ofile)
            self.filepath = Filepath(ofile)
        else:
            pass
        return super().PR_init(file_index)
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
    def export(self, begin:int, end:int, center='NA') -> str:
        # PR 中的位置
        if center == 'NA':
            self.PRpos = self.PR_center_arg(np.array(self.size),np.array(self.pos.get()))
        else:
            self.PRpos = self.PR_center_arg(np.array(self.size),np.array(Pos(*eval(center)).get()))
        # 气泡序列
        width,height = self.origin_size
        pr_horiz,pr_vert = self.PRpos
        clip_this = self.clip_tplt.format(**{
            'clipid'    : 'BG_clip_%d'%MediaObj.clip_index,
            'clipname'  : self.filename,
            'timebase'  : '%d'%self.frame_rate,
            'ntsc'      : self.Is_NTSC,
            'start'     : '%d'%begin,
            'end'       : '%d'%end,
            'in'        : '%d'%90000,
            'out'       : '%d'%(90000+end-begin),
            'fileid'    : self.fileindex,
            'filename'  : self.filename,
            'filepath'  : self.xmlpath,
            'filewidth' : '%d'%width,
            'fileheight': '%d'%height,
            'horiz'     : '%.5f'%pr_horiz,
            'vert'      : '%.5f'%pr_vert,
            'scale'     : '%.2f'%(self.scale*100),
            'colorlabel': self.label_color
            })
        # 更新序号
        MediaObj.clip_index = MediaObj.clip_index+1
        # 返回
        return clip_this
    def convert(self):
        self.media = self.media.convert_alpha()
    def get_pos(self) -> dict:
        pos_dict = {
            'green': {
                'g0':{
                    'pos' : self.pos.get(),
                    'scale' : (self.pos + self.media.get_size()).get()
                }
            },
        }
        return pos_dict
    def configure(self, key: str, value, index: int = 0):
        super().configure(key, value, index)
        if key == 'filepath':
            if value in self.cmap.keys():
                # 填充纯色
                self.media = pygame.Surface(self.screen_size,pygame.SRCALPHA)
                self.media.fill(self.cmap[value])
                # 其他参数
                self.scale:float = 1.0
                self.size:tuple  = self.screen_size
                self.origin_size:tuple = self.size
            else:
                # 读取图片文件
                self.load_image(scale=self.scale)
# 立绘
class Animation(MediaObj):
    def __init__(
            self,
            filepath:str,
            scale:float      = 1.0,
            pos:tuple        = (0,0),
            tick:int         = 1,
            loop:bool        = True,
            label_color:str  = 'Lavender'
            ) -> None:
        # 文件和路径
        super().__init__(filepath=filepath,label_color=label_color)
        # 立绘图像
        self.load_image(scale=scale)
        # 初始化PR
        self.PR_init(file_index='AMfile_%d')
        # 位置
        if type(pos) in [Pos,FreePos]:
            self.pos = pos
        else:
            self.pos = Pos(*pos)
        # 动画循环参数
        self.loop:bool = loop
        self.tick:int = tick
        self.this:int = 0
    def load_image(self, scale: float):
        # 立绘图像
        self.length:int = len(self.filepath.list())
        self.media:np.ndarray = np.frompyfunc(lambda x:self.zoom(pygame.image.load(x),scale=scale),1,1)(self.filepath.list())
        # 尺寸是第一张图的尺寸
        self.size:tuple = self.media[0].get_size()
        self.origin_size:tuple = pygame.image.load(self.filepath.list()[0]).get_size()
        self.scale:float  = scale
    def display(self,surface:pygame.Surface,alpha:float=100,center:str='NA',adjust:str='NA',frame:int=0)->None:
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
    def export(self,begin:int,end:int,center:str='NA')->str:
        # PR 中的位置
        if center == 'NA':
            self.PRpos = self.PR_center_arg(np.array(self.size),np.array(self.pos.get()))
        else:
            self.PRpos = self.PR_center_arg(np.array(self.size),np.array(Pos(*eval(center)).get()))
        # 立绘序列
        width,height = self.origin_size
        pr_horiz,pr_vert = self.PRpos
        clip_this = self.clip_tplt.format(**{
            'clipid'    : 'AM_clip_%d'%MediaObj.clip_index,
            'clipname'  : self.filename,
            'timebase'  : '%d'%self.frame_rate,
            'ntsc'      : self.Is_NTSC,
            'start'     : '%d'%begin,
            'end'       : '%d'%end,
            'in'        : '%d'%90000,
            'out'       : '%d'%(90000+end-begin),
            'fileid'    : self.fileindex,
            'filename'  : self.filename,
            'filepath'  : self.xmlpath,
            'filewidth' : '%d'%width,
            'fileheight': '%d'%height,
            'horiz'     : '%.5f'%pr_horiz,
            'vert'      : '%.5f'%pr_vert,
            'scale'     : '%.2f'%(self.scale*100),
            'colorlabel': self.label_color
            })
        MediaObj.clip_index = MediaObj.clip_index+1
        return clip_this
    def get_tick(self,duration:int)->np.ndarray: # 1.8.0
        if self.length > 1:
            # 如果length > 1 说明是多帧的动画！
            tick_lineline = np.arange(0,duration if self.loop else self.length,1/self.tick)[0:duration]%(self.length)
            tick_lineline = np.hstack([tick_lineline,(self.length-1)*np.ones(duration-len(tick_lineline))]).astype(int)
        else:
            # 如果是静态立绘，返回0
            tick_lineline = np.zeros(duration).astype(int)
        return tick_lineline
    def convert(self):
        self.media = np.frompyfunc(lambda x:x.convert_alpha(),1,1)(self.media)
    def get_pos(self) -> dict:
        pos_dict = {
            'green': {
                'g0':{
                    'pos' : self.pos.get(),
                    'scale' : (self.pos + self.media[0].get_size()).get()
                }
            },
        }
        return pos_dict
    def configure(self, key: str, value, index: int = 0):
        super().configure(key, value, index)
        if key == 'filepath':
            self.load_image(scale=self.scale)
# 内建动画的基类：不可以直接使用
class BuiltInAnimation(Animation):
    # BIA初始化：需要在media确定之后！
    def __init__(
        self,
        media:np.ndarray,
        pos:Pos          = Pos(0,0),
        BIA_type:str     = 'BIA',
        label_color:str  = 'Mango') -> None:
        # 类型
        self.BIA_type:str = BIA_type
        # 颜色标签
        self.label_color:str = label_color
        # 初始化立绘图像
        self.media:np.ndarray = media
        self.length:int = len(self.media)
        # 位置
        self.pos = pos
        # 尺寸
        self.size:tuple        = self.media[0].get_size()
        self.origin_size:tuple = self.size
        self.scale:float       = 1.0
        # 动画参数
        self.tick       = 1
        self.loop       = False
        self.this:int   = 0
        # PR序列
        self.PR_init(file_index='AMfile_%d')
    # 所有的内建动画，在导出PR项目初始化的时候，将图像存储为一个文件
    def PR_init(self, file_index: str = 'None') -> None:
        # 如果不导出PR项目，那么什么都不做
        if self.export_xml == False:
            pass
        else:
            # 保存为文件
            filename = '/auto_{}_%d.png'.format(self.BIA_type) % MediaObj.outanime_index
            ofile = self.output_path + filename
            pygame.image.save(self.media[0],ofile)
            self.filepath = Filepath(ofile)
            MediaObj.outanime_index = MediaObj.outanime_index+1
        # 继承
        return super().PR_init(file_index)
    # 内建动画，没有configure
    def configure(self, key: str, value, index: int = 0):
        pass
# 组合立绘
class GroupedAnimation(BuiltInAnimation):
    def __init__(
            self,
            subanimation_list:list,
            subanimation_current_pos=None,
            label_color='Mango'
            ):
        # 新建空白画板，尺寸为全屏
        canvas_surface:pygame.Surface = pygame.Surface(self.screen_size,pygame.SRCALPHA)
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
                # 对象类型检查
                if type(am_name) in [Animation,BuiltInAnimation,GroupedAnimation]:
                    subanimation:Animation = am_name
                else:
                    raise MediaError('Undef2GA',am_name)
                # 检查立绘可用性
                if subanimation.length > 1:
                    # 动态立绘是不可用的！
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
        super().__init__(
            media       = np.array([canvas_surface]),
            pos         = Pos(0,0),
            BIA_type    = 'GA',
            label_color = label_color
            )

# 血条
class HitPoint(BuiltInAnimation):
    def __init__(
        self,
        describe:str    = '',
        heart_max:int   = 0,
        heart_begin:int = 0,
        heart_end:int   = 0,
        layer:int       = 0,
        label_color:str = 'Mango'
        ):
        # 类型
        self.BIA_type = 'HP'
        # 颜色标签
        self.label_color:str = label_color
        # 主要字体
        self.BIA_text = Text('./media/SourceHanSerifSC-Heavy.otf',fontsize=int(0.0521*MediaObj.screen_size[0]),color=(255,255,255,255),line_limit=10)
        # 项目参数
        screensize = self.screen_size
        frame_rate = self.frame_rate
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
        # 动画参数:检查合法性
        if (heart_end==heart_begin)|(heart_max<max(heart_begin,heart_end)):
            raise MediaError('InvHPArg',','.join([str(describe),str(heart_max),str(heart_begin),str(heart_end)]))
        elif heart_end > heart_begin: # 如果是生命恢复
            temp = heart_end
            heart_end = heart_begin
            heart_begin = temp # 则互换顺序 确保 begin一定是小于end的
            heal_heart = True
        else:
            heal_heart = False
        # 心与心之间的距离
        distance = int(0.026*screensize[0]) # 50
        # 画布的尺寸
        total_heart = int(heart_max/2 * hx + max(0,np.ceil(heart_max/2-1)) * distance) #画布总长
        left_heart = int(heart_end/2 * hx + max(0,np.ceil(heart_end/2-1)) * distance) #画布总长
        lost_heart = int((heart_begin-heart_end)/2 * hx + np.floor((heart_begin-heart_end)/2) * distance)
        # 名牌的尺寸
        nametx_surf = self.BIA_text.draw(describe)[0] # 名牌
        nx,ny = nametx_surf.get_size() # 名牌尺寸
        # 开始制图
        # 底层 阴影图
        if layer==0:
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
            for i in range(1,heart_max+1): # 偶数，低于最终血量
                if i%2 == 0:
                    canvas.blit(heart_shape,(posx,posy))
                    posx = posx + hx + distance
                else:
                    pass
            if heart_max%2 == 1: # max是奇数
                left_heart_shape = heart_shape.subsurface((0,0,int(hx/2),hy))
                canvas.blit(left_heart_shape,(total_heart-int(hx/2),posy))
            # 媒体
            self.media:np.ndarray = np.array([canvas])
        # 剩余的血量
        elif layer==1: 
            self.pos = Pos((screensize[0]-total_heart)/2,3/5*screensize[1]+ny/2-hy/2)
            canvas = pygame.Surface((left_heart,hy),pygame.SRCALPHA)
            canvas.fill((0,0,0,0))
            posx,posy = 0,0
            for i in range(1,heart_end+1): # 偶数，低于最终血量
                if i%2 == 0:
                    canvas.blit(heart,(posx,posy))
                    posx = posx + hx + distance
                else:
                    pass
            # 如果剩余的血量是奇数
            if heart_end%2 == 1:
                half_heart = heart.subsurface((0,0,int(hx/2),hy))
                canvas.blit(half_heart,(heart_end//2*(hx + distance),0))
            # 媒体
            self.media:np.ndarray = np.array([canvas])
        # 损失/恢复的血量
        elif layer==2:
            self.pos = Pos(heart_end//2*(hx + distance)+(heart_end%2)*int(hx/2)+(screensize[0]-total_heart)/2,3/5*screensize[1]+ny/2-hy/2)
            canvas = pygame.Surface((lost_heart,hy),pygame.SRCALPHA)
            canvas.fill((0,0,0,0))
            posx,posy = 0,0
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
            if heart_end%2 == 1: # end是奇数
                left_heart = heart.subsurface((0,0,int(hx/2),hy))
                canvas.blit(left_heart,(heart_end//2*(hx + distance),0))
            # 恢复的动画
            if heal_heart == True:
                crop_timeline = sigmoid(0,lost_heart,frame_rate).astype(int) # 裁剪时间线
                self.media:np.ndarray = np.frompyfunc(lambda x:canvas.subsurface(0,0,x,hy),1,1)(crop_timeline)
            else:
                self.media:np.ndarray = np.array([canvas])
        else:
            pass
        # 初始化
        super().__init__(
            media       = self.media,
            pos         = self.pos,
            BIA_type    = 'HP',
            label_color = label_color
            )

# 骰子
class Dice(BuiltInAnimation):
    dice_cmap = {
        3:(124,191,85,255),  # 大成功
        1:(94,188,235,255),  # 成功
        0:(245,192,90,255),  # 失败
        2:(233,86,85,255),   # 大失败
        -1:(255,255,255,255) # 中性的
        }
    significant = 0.05 # 大成功大失败阈值
    def __init__(
        self,
        dice_set:dict  = {},
        layer:int       = 0,
        label_color:str = 'Mango'
        ):
        # 主要字体
        self.BIA_text = Text('./media/SourceHanSerifSC-Heavy.otf',fontsize=int(0.0521*MediaObj.screen_size[0]),color=(255,255,255,255),line_limit=10)
        # 屏幕参数
        screensize:tuple = self.screen_size
        frame_rate:int = self.frame_rate
        # 检查参数合法性：
        for idx in dice_set.keys():
            dice = dice_set[idx]
            # 类型是否合法
            try:
                describe = dice['content']
                dice_face = dice['face']
                dice_max = dice['dicemax']
                dice_check = dice['check']
                dice_max,dice_face,dice_check = map(lambda x:-1 if x==None else int(x),(dice_max,dice_face,dice_check))
            except ValueError as E:
                raise MediaError('InvDCSytx',','.join([str(describe),str(dice_max),str(dice_check),str(dice_face)]),E)
            # 值是否合法
            if (dice_face>dice_max)|(dice_check<-1)|(dice_check>dice_max)|(dice_face<0)|(dice_max<=0):
                raise MediaError('InvDCArg', ','.join([str(describe),str(dice_max),str(dice_check),str(dice_face)]))
        # 最多4个
        N_dice:int = len(dice_set.keys())
        if N_dice > 4:
            N_dice=4
        #y_anchor = {4:180,3:270,2:360,1:450}[N_dice] # sep=180 x[600,1400]
        y_anchor:int = {
            4:int(0.1667*screensize[1]),
            3:int(0.25*screensize[1]),
            2:int(0.3333*screensize[1]),
            1:int(0.4167*screensize[1])
            }[N_dice]
        y_unit:int = int(0.1667*screensize[1])
        # 底层： 名字 检定
        if layer == 0:
            canvas = pygame.Surface(screensize,pygame.SRCALPHA)
            for idx in dice_set.keys(): 
                i = int(idx)
                dice = dice_set[idx]
                # 渲染
                name_surf = self.BIA_text.render(dice['content'])
                nx,ny = name_surf.get_size()
                canvas.blit(name_surf,(int(0.3125*screensize[0])-nx//2,y_anchor+i*y_unit+(y_unit-ny)//2)) # 0.3125*screensize[0] = 600
                if dice['check'] is not None:
                    check_surf = self.BIA_text.render('/%d'%dice['check'])
                    cx,cy = check_surf.get_size()
                    canvas.blit(check_surf,(int(0.7292*screensize[0]),y_anchor+i*y_unit+(y_unit-cy)//2)) # 0.7292*screensize[0] = 1400
            # 媒体和位置
            self.media = np.array([canvas])
            self.pos = Pos(0,0)
        # 滚动的老虎机
        elif layer == 1:
            #画布
            canvas = []
            for i in range(0,int(2.5*frame_rate)):
                canvas_frame = pygame.Surface((int(0.1458*screensize[0]),y_unit*N_dice),pygame.SRCALPHA) # 0.1458*screensize[0] = 280
                canvas.append(canvas_frame)
            # 骰子
            for idx in dice_set.keys():
                D = int(idx)
                dice = dice_set[idx]
                cols,possible_digit = self.get_possible_digit(dice['dicemax'])
                dx,dy = self.BIA_text.render('0'*cols).get_size()
                # running cols
                run_surf = pygame.Surface((dx,dy*len(possible_digit)),pygame.SRCALPHA)
                for i,digit in enumerate(possible_digit):
                    for j,char in enumerate(digit): # alpha 1.8.4 兼容非等宽数字，比如思源宋体
                        char_this = self.BIA_text.render(char)
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
                    canvas[t].blit(slot_surf[t],(int(0.1458*screensize[0]-dx-0.0278*screensize[1]),D*y_unit+(y_unit-dy)//2))
            # 媒体和位置
            self.media = np.array(canvas)
            self.pos = Pos(int(0.5833*screensize[0]),y_anchor)
        # 出目
        elif layer == 2:
            canvas = pygame.Surface((int(0.1458*screensize[0]),y_unit*N_dice),pygame.SRCALPHA)
            for idx in dice_set.keys():
                i = int(idx)
                dice = dice_set[idx]
                # 渲染 0.0651
                if dice['check'] is None:
                    color_flag = -1
                else:
                    face_rate = dice['face']/dice['dicemax']
                    color_flag = ((face_rate <=self.significant)|(face_rate>(1-self.significant)))*2 + (dice['face']<=dice['check'])
                # 有颜色的字体
                BIA_color_Text = Text('./media/SourceHanSerifSC-Heavy.otf',fontsize=int(0.0651*screensize[0]),color=self.dice_cmap[color_flag],line_limit=10)
                face_surf = BIA_color_Text.render(str(dice['face']))
                fx,fy = face_surf.get_size()
                #canvas.blit(face_surf,(int(0.1458*screensize[0]-fx-0.0278*screensize[1]),(i+1)*y_unit-fy-int(0.0278*screensize[1])))
                canvas.blit(face_surf,(int(0.1458*screensize[0]-fx-0.0278*screensize[1]),i*y_unit+(y_unit-fy)//2))
            # 媒体和位置
            self.media = np.array([canvas])
            self.pos = Pos(int(0.5833*screensize[0]),y_anchor) # 0.5833*screensize[0] = 1120
        else:
            pass
        # 初始化
        super().__init__(
            media       = self.media,
            pos         = self.pos,
            BIA_type    = 'DC',
            label_color = label_color
            )
    # 获取所有的骰子可能出现的值，用来生成随机的老虎机样式
    def get_possible_digit(self,dice_max:int) -> tuple:
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

# 音效
class Audio(MediaObj):
    pygame.mixer.init()
    def __init__(self,filepath,label_color='Caribbean'):
        # 文件路径
        super().__init__(filepath=filepath,label_color=label_color)
        # 载入音频
        try:
            self.media = pygame.mixer.Sound(self.filepath.exact())
        except Exception as E:
            raise MediaError('BadAudio',filepath)
        # 音频时长：单位是帧！
        try:
            self.length:int = int(self.media.get_length()*self.frame_rate)
        except Exception as E:
            print(WarningPrint('BadAuLen',self.filepath.exact(),E))
            self.length:int = 0
        self.audioseg = None
        # PR 项目
        self.PR_init(file_index='AUfile_%d')
    def display(self,channel,volume=100):
        channel.set_volume(volume/100)
        channel.play(self.media)
    def export(self,begin:int)->str:
        clip_this = self.audio_clip_tplt.format(**{
            'clipid'    : 'AU_clip_%d'%MediaObj.clip_index,
            'type'      : self.Audio_type,
            'clipname'  : self.filename,
            'audiolen'  : '%d'%self.length,
            'timebase'  : '%d'%self.frame_rate,
            'ntsc'      : self.Is_NTSC,
            'start'     : '%d'%begin,
            'end'       : '%d'%(begin+self.length),
            'in'        : '0',
            'out'       : '%d'%self.length,
            'fileid'    : self.fileindex,
            'filename'  : self.filename,
            'filepath'  : self.xmlpath,
            'colorlabel': self.label_color
            })
        MediaObj.clip_index = MediaObj.clip_index+1
        return clip_this
    # 添加了BGM的片段
    def recode(self)->pydub.AudioSegment:
        if self.audioseg is None:
            self.audioseg = pydub.AudioSegment.from_file(self.filepath.exact())
        return self.audioseg
    # 预览播放
    def waveplot(self):
        # 波形图
        samples:np.ndarray = pygame.sndarray.sample(self.media).T[0]
        pass
    def preview(self, surface: pygame.Surface):
        self.media.play()
    # 修改
    def configure(self, key: str, value, index: int = 0):
        super().configure(key, value, index)
        if key == 'filepath':
            self.media = pygame.mixer.Sound(self.filepath.exact())
            self.length:int = int(self.media.get_length()*self.frame_rate)
# 背景音乐
class BGM(MediaObj):
    def __init__(self,filepath,volume=100,loop=True,label_color='Caribbean'):
        # 文件路径
        super().__init__(filepath=filepath,label_color=label_color)
        self.media = self.filepath.exact()
        self.volume = volume/100
        self.loop:bool = loop
        if self.filepath.type() not in ['ogg']:#建议的格式
            print(WarningPrint('BadBGMFmt',filepath.split('.')[-1]))
        self.audioseg = None
    def display(self):
        if pygame.mixer.music.get_busy() == True: #如果已经在播了
            pygame.mixer.music.stop() #停止
            pygame.mixer.music.unload() #换碟
        else:
            pass
        pygame.mixer.music.load(self.media) #进碟
        pygame.mixer.music.play(loops={False:0,True:-1}[self.loop]) #开始播放
        pygame.mixer.music.set_volume(self.volume) #设置音量
    # 导出视频时的音频操作
    def recode(self,begin:int,end:int)->pydub.AudioSegment:
        # 如果还没初始化
        if self.audioseg is None:
            # 载入文件，调整音量
            self.audioseg = pydub.AudioSegment.from_file(self.filepath.exact()) + np.log10(self.volume)*20
        # 无声的片段
        clip_empty = pydub.AudioSegment.silent(
            duration=int((end-begin)/self.frame_rate*1000),
            frame_rate=48000
            )
        # 添加了BGM的片段
        clip_this = clip_empty.overlay(
            seg = self.audioseg,
            loop= self.loop,
        )
        return clip_this
    # 预览
    def preview(self, surface: pygame.Surface):
        pass
    # 修改
    def configure(self, key: str, value, index: int = 0):
        if key == 'filepath':
            super().configure(key, value, index)
            self.media = self.filepath.exact()
            self.length:int = int(self.media.get_length()*self.frame_rate)
        elif key == 'volume':
            self.volume = value/100
        else:
            super().configure(key, value, index)