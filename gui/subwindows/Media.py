from PIL import Image, ImageDraw, ImageFont

label_pos_show_text = ImageFont.truetype('./media/SourceHanSerifSC-Heavy.otf', 30)


class Media:
    """
    这个公共类只是为了以后可能的扩展，目前用不到
    """
    def __init__(self):
        pass

# FreePos 相关
class Pos(Media):
    # 初始化
    # 这种初始化模式更优雅，但是并不和GUI的逻辑兼容，重新考虑一下？
    def __init__(self,*argpos):
        if len(argpos) == 0:
            self.x = 0
            self.y = 0
        elif len(argpos) == 1:
            self.x = int(argpos[0])
            self.y = int(argpos[0])
        else:
            self.x = int(argpos[0])
            self.y = int(argpos[1])
    # 重载取负号
    def __neg__(self):
        return Pos(-self.x,-self.y)
    # 重载加法
    def __add__(self,others):
        if type(others) is Pos:
            x = self.x + others.x
            y = self.y + others.y
            return Pos(x,y)
        elif type(others) in [list,tuple]:
            try:
                x = self.x + int(others[0])
                y = self.y + int(others[1])
                return Pos(x,y)
            except IndexError: # 列表数组长度不足
                raise Exception()
            except ValueError: # 列表数组不能解释为整数
                raise Exception()
        else: # 用来加的不是一个合理的类型
            raise Exception()
    # 重载减法
    def __sub__(self,others):
        return -(-self + others)
    # 重载相等判断
    def __eq__(self,others):
        if type(others) is Pos:
            return (self.x == others.x) and (self.y == others.y)
        elif type(others) in [list,tuple]:
            try:
                return (self.x == int(others[0])) and (self.y == int(others[1]))
            except IndexError: # 列表数组长度不足
                return False
            except ValueError: # 列表数组不能解释为整数
                return False
        else: # 用来判断的不是一个合理的类型
            return False
    def __str__(self):
        return "({x},{y})".format(x=self.x,y=self.y)
    def get(self):
        return (self.x,self.y)
    def preview(self,image_canvas):
        p_x = self.x
        p_y = self.y
        draw = ImageDraw.Draw(image_canvas)
        draw.line([p_x-100,p_y,p_x+100,p_y],fill='green',width=2)
        draw.line([p_x,p_y-100,p_x,p_y+100],fill='green',width=2)
        draw.text((p_x,p_y),'({0},{1})'.format(p_x,p_y),font=label_pos_show_text,fill='green')
    def convert(self):
        pass
class FreePos(Pos):
    # 重设位置
    def set(self,others):
        if type(others) in [Pos,FreePos]:
            self.x = others.x
            self.y = others.y
        elif type(others) in [list,tuple]:
            try:
                self.x = int(others[0])
                self.y = int(others[1])
            except IndexError: # 列表数组长度不足
                raise Exception('The length of tuple to set is insufficient.')
            except ValueError: # 列表数组不能解释为整数
                raise Exception('Invalid value type.')
        else: # 设置的不是一个合理的类型
            raise Exception('Unsuppoeted type to set!')
class PosGrid:
    def __init__(self,pos,end,x_step,y_step):
        x1,y1 = pos
        x2,y2 = end
        if (x1>=x2) | (y1>=y2):
            raise Exception('Invalid separate param end for posgrid!')
        else:
            self.pos = pos
            self.end = end
        X = []
        Y = []
        i = 0
        for i in range(0,x_step):
            X.append(int(x1+i*(x2-x1)/x_step))
        for i in range(0,y_step):
            Y.append(int(y1+i*(y2-y1)/y_step))
        self._grid=[]
        for x in X:
            col = []
            for y in Y:
                col.append(Pos(x,y))
            self._grid.append(col)
        self._size = (x_step,y_step)
    def __getitem__(self,key):
        return self._grid[key[0]][key[1]]
    def size(self):
        return self._size
    def preview(self,image_canvas):
        draw = ImageDraw.Draw(image_canvas)
        size = image_canvas.size
        # 起点，
        draw.line([0,self.pos[1],size[0],self.pos[1]],fill='purple',width=2)
        draw.line([self.pos[0],0,self.pos[0],size[1]],fill='purple',width=2)
        draw.text(self.pos,'({0},{1})'.format(*self.pos),font=label_pos_show_text,fill='purple')
        # 终点
        draw.line([0,self.end[1],size[0],self.end[1]],fill='purple',width=2)
        draw.line([self.end[0],0,self.end[0],size[1]],fill='purple',width=2)
        text_to_show = '({0},{1})'.format(*self.end)
        draw.text((self.end[0]-len(text_to_show)*16,self.end[1]-40),text_to_show,font=label_pos_show_text,fill='purple')
        # 网点
        for i in range(self._size[0]): # x轴 
            for j in range(self._size[1]): # y轴
                pos_this = self._grid[i][j]
                p_x = pos_this.x
                p_y = pos_this.y
                draw.line([p_x-20,p_y,p_x+20,p_y],fill='green',width=2)
                draw.line([p_x,p_y-20,p_x,p_y+20],fill='green',width=2)
    def convert(self):
        pass
class Text(Media):
    def __init__(self,fontfile='./media/SourceHanSansCN-Regular.otf',fontsize=40,color=(0,0,0,255),line_limit=20,label_color='Lavender'):
        self.text_render = ImageFont.truetype(fontfile, fontsize)
        self.color=color
        self.size=fontsize
        self.line_limit = line_limit
    def draw(self,lenth=-1):
        if lenth ==-1:
            lenth = self.line_limit
        test_canvas = Image.new(mode='RGBA',size=(self.size*int(self.line_limit*1.5),self.size*2),color=(0,0,0,0))#高度贪婪2x,宽度贪婪1.5x
        test_draw = ImageDraw.Draw(test_canvas)
        test_draw.text((0,0), ('测试文本'*50)[0:lenth], font = self.text_render,fill = self.color)
        p1,p2,p3,p4 = test_canvas.getbbox()
        return test_canvas.crop((0,0,p3,p4))
    def preview(self,image_canvas,prevpos='None'):
        can_W,can_H = image_canvas.size
        draw_text = self.draw()
        txt_w,txt_h = draw_text.size
        if prevpos=='None':
            image_canvas.paste(draw_text,((can_W-txt_w)//2,(can_H-txt_h)//2),mask=draw_text.split()[-1])
        else:
            image_canvas.paste(draw_text,prevpos,mask=draw_text.split()[-1])
class StrokeText(Text):
    def __init__(self,fontfile='./media/SourceHanSansCN-Regular.otf',fontsize=40,color=(0,0,0,255),line_limit=20,edge_color=(255,255,255,255),edge_width=1,label_color='Lavender'):
        super().__init__(fontfile=fontfile,fontsize=fontsize,color=color,line_limit=line_limit,label_color=label_color)
        self.edge_color=edge_color
        try:
            self.edge_width = int(edge_width)
        except ValueError:
            raise Exception("非法的描边宽度！")
        if self.edge_width < 0:
            raise Exception("非法的描边宽度！")
    def draw(self,lenth=-1):
        if lenth ==-1:
            lenth = self.line_limit
        ew = self.edge_width
        test_canvas = Image.new(mode='RGBA',size=(self.size*int(self.line_limit*1.5)+2*ew,self.size*2+2*ew),color=(0,0,0,0))#高度贪婪2x,宽度贪婪1.5x
        test_draw = ImageDraw.Draw(test_canvas)
        # 角
        for pos in [[0,0],[0,2*ew],[2*ew,0],[2*ew,2*ew]]:
            test_draw.text(pos, ('测试文本'*50)[0:lenth], font = self.text_render,fill = self.edge_color)
        # 边
        for i in range(1,ew*2):
            for pos in [[0,i],[i,0],[2*ew,i],[i,2*ew]]:
                test_draw.text(pos, ('测试文本'*50)[0:lenth], font = self.text_render,fill = self.edge_color)
        # 中心
        test_draw.text((ew,ew), ('测试文本'*50)[0:lenth], font = self.text_render,fill = self.color)
        p1,p2,p3,p4 = test_canvas.getbbox()
        return test_canvas.crop((0,0,p3,p4))
class Bubble(Media):
    def __init__(self,filepath=None,Main_Text=Text(),Header_Text=None,pos=(0,0),mt_pos=(0,0),ht_pos=(0,0),ht_target='Name',align='left',line_distance=1.5,label_color='Lavender'):
        if filepath is None or filepath == 'None': # 支持气泡图缺省
            self.media  = Image.new(mode='RGBA',size=(1920,1080),color=(0,0,0,0))
        else:
            self.media = Image.open(filepath).convert('RGBA')
        if type(pos) in [Pos,FreePos]:
            self.pos = pos
        else:
            self.pos = Pos(*pos)
        self.MainText = Main_Text
        self.mt_pos = mt_pos
        self.Header = Header_Text
        self.ht_pos = ht_pos
        self.target = ht_target
        self.line_distance = line_distance
        if align in ('left','center'):
            self.align = align
        else:
            raise ValueError('align非法参数：',align)
    def draw(self,lines=4,show_marker=True):
        bubble_canvas = self.media.copy()
        draw = ImageDraw.Draw(bubble_canvas)
        if self.Header != None:
            draw_text = self.Header.draw()
            bubble_canvas.paste(draw_text,self.ht_pos,mask=draw_text)
            # 位置标记
            if show_marker:
                h_x,h_y = self.ht_pos
                draw.line([h_x-100,h_y,h_x+100,h_y],fill='blue',width=2)
                draw.line([h_x,h_y-50,h_x,h_y+50],fill='blue',width=2)
                draw.text((h_x,h_y-40),'({0},{1})'.format(*self.ht_pos),font=label_pos_show_text,fill='blue')
        if self.MainText != None:
            tx_w = self.MainText.size*self.MainText.line_limit
            tx_h = self.line_distance*self.MainText.size
            m_x,m_y = self.mt_pos
            for i,l in enumerate(range(self.MainText.line_limit,0,-self.MainText.line_limit//lines)):
                draw_text = self.MainText.draw(l)
                bubble_canvas.paste(draw_text,(int(m_x+(tx_w-draw_text.size[0])//2*(self.align=='center')),int(m_y+i*tx_h)),mask=draw_text)
            # 位置标记
            if show_marker:
                draw.line([m_x-100,m_y,m_x+100,m_y],fill='blue',width=2)
                draw.line([m_x,m_y-50,m_x,m_y+50],fill='blue',width=2)
                draw.text((m_x,m_y-40),'({0},{1})'.format(*self.mt_pos),font=label_pos_show_text,fill='blue')
        return bubble_canvas
    def preview(self,image_canvas):
        bubble_canvas = self.draw(4)
        image_canvas.paste(bubble_canvas,self.pos.get(),mask=bubble_canvas)
        self.pos.preview(image_canvas)

class Balloon(Bubble):
    def __init__(self,filepath=None,Main_Text=Text(),Header_Text=[None],pos=(0,0),mt_pos=(0,0),ht_pos=[(0,0)],ht_target=['Name'],align='left',line_distance=1.5,label_color='Lavender'):
        super().__init__(filepath=filepath,Main_Text=Main_Text,Header_Text=Header_Text,pos=pos,mt_pos=mt_pos,ht_pos=ht_pos,ht_target=ht_target,align=align,line_distance=line_distance,label_color=label_color)
        if len(self.Header)!=len(self.ht_pos) or len(self.Header)!=len(self.target):
            raise Exception('\x1B[31m[BubbleError]:\x1B[0m ' + 'length of header params does not match!')
        else:
            self.header_num = len(self.Header)
    def draw(self,lines=4,show_marker=True):
        bubble_canvas = self.media.copy()
        draw = ImageDraw.Draw(bubble_canvas)
        for i,HT in enumerate(self.Header):
            if HT != None:
                draw_text = HT.draw()
                bubble_canvas.paste(draw_text,self.ht_pos[i],draw_text)
                if show_marker:
                    h_x,h_y = self.ht_pos[i]
                    draw.line([h_x-100,h_y,h_x+100,h_y],fill='blue',width=2)
                    draw.line([h_x,h_y-50,h_x,h_y+50],fill='blue',width=2)
                    draw.text((h_x,h_y-40),'({0},{1})'.format(*self.ht_pos[i]),font=label_pos_show_text,fill='blue')
        if self.MainText != None:
            tx_w = self.MainText.size*self.MainText.line_limit
            tx_h = self.line_distance*self.MainText.size
            m_x,m_y = self.mt_pos
            for i,l in enumerate(range(self.MainText.line_limit,0,-self.MainText.line_limit//lines)):
                draw_text = self.MainText.draw(l)
                bubble_canvas.paste(draw_text,(int(m_x+(tx_w-draw_text.size[0])//2*(self.align=='center')),int(m_y+i*tx_h)),mask=draw_text)
            # 位置标记
            if show_marker:
                draw.line([m_x-100,m_y,m_x+100,m_y],fill='blue',width=2)
                draw.line([m_x,m_y-50,m_x,m_y+50],fill='blue',width=2)
                draw.text((m_x,m_y-40),'({0},{1})'.format(*self.mt_pos),font=label_pos_show_text,fill='blue')
        return bubble_canvas

class DynamicBubble(Bubble):
    def __init__(self,filepath=None,Main_Text=Text(),Header_Text=None,pos=(0,0),mt_pos=(0,0),mt_end=(0,0),ht_pos=(0,0),ht_target='Name',fill_mode='stretch',line_distance=1.5,label_color='Lavender'):
        super().__init__(filepath=filepath,Main_Text=Main_Text,Header_Text=Header_Text,pos=pos,mt_pos=mt_pos,ht_pos=ht_pos,ht_target=ht_target,line_distance=line_distance,label_color=label_color)
        if (mt_pos[0] >= mt_end[0]) | (mt_pos[1] >= mt_end[1]) | (mt_end[0] > self.media.size[0]) | (mt_end[1] > self.media.size[1]):
            raise Exception('Invalid bubble separate params mt_end!')
        elif (mt_pos[0] < 0) | (mt_pos[1] < 0):
            raise Exception('Invalid bubble separate params mt_pos!')
        else:
            self.mt_end = mt_end
        # fill_mode 只能是 stretch 或者 collage
        if fill_mode in ['stretch','collage']:
            self.fill_mode = fill_mode
        else:
            raise Exception('Invalid fill mode params ' + fill_mode)
        # x,y轴上的四条分割线
        self.size = self.media.size
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
    def draw(self,lines=4,show_marker=True):
        # 主文本
        text_canvas = Image.new(mode='RGBA',size=(1920,1080),color=(0,0,0,0))
        if self.MainText == None:
            raise Exception('Main_Text of Bubble is None!')
        else:
            tx_h = self.line_distance*self.MainText.size
            for i,l in enumerate(range(self.MainText.line_limit,0,-self.MainText.line_limit//lines)):
                draw_text = self.MainText.draw(l)
                text_canvas.paste(draw_text,(0,int(i*tx_h)),mask=draw_text)
            try:
                p1,p2,xlim,ylim = text_canvas.getbbox()
            except ValueError:
                xlim = int(self.MainText.size/2)
                ylim = self.MainText.size
        temp_size_x = xlim + self.x_tick[1] + self.x_tick[3] - self.x_tick[2]
        temp_size_y = ylim + self.y_tick[1] + self.y_tick[3] - self.y_tick[2]
        bubble_canvas = Image.new(mode='RGBA',size=(temp_size_x,temp_size_y),color=(0,0,0,0))
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
        # 主文本
        bubble_canvas.paste(text_canvas,self.mt_pos,mask=text_canvas)
        draw = ImageDraw.Draw(bubble_canvas)
        # 头文本
        if self.Header!=None:    # Header 有定义，且输入文本不为空
            if self.ht_pos[0] > self.x_tick[2]:
                ht_renderpos_x = self.ht_pos[0] - self.x_tick[2] + self.x_tick[1] + xlim
            else:
                ht_renderpos_x = self.ht_pos[0]
            if self.ht_pos[1] > self.y_tick[2]:
                ht_renderpos_y = self.ht_pos[1] - self.y_tick[2] + self.y_tick[1] + ylim
            else:
                ht_renderpos_y = self.ht_pos[1]
            draw_text = self.Header.draw()
            bubble_canvas.paste(draw_text,(ht_renderpos_x,ht_renderpos_y),mask=draw_text)
            if show_marker:
                # 头文本标记
                h_x,h_y = self.ht_pos
                draw.line([h_x-100,h_y,h_x+100,h_y],fill='blue',width=2)
                draw.line([h_x,h_y-50,h_x,h_y+50],fill='blue',width=2)
                draw.text((h_x,h_y-40),'({0},{1})'.format(*self.ht_pos),font=label_pos_show_text,fill='blue')
            # 头文本标记
        if show_marker:
            # 可变气泡分割显示：
            size = bubble_canvas.size
            # 起点，
            draw.line([0,self.mt_pos[1],size[0],self.mt_pos[1]],fill='purple',width=2)
            draw.line([self.mt_pos[0],0,self.mt_pos[0],size[1]],fill='purple',width=2)
            draw.text(self.mt_pos,'({0},{1})'.format(*self.mt_pos),font=label_pos_show_text,fill='purple')
            # 终点
            end_x,end_y = bubble_clip_pos[8]
            draw.line([0,end_y,size[0],end_y],fill='purple',width=2)
            draw.line([end_x,0,end_x,size[1]],fill='purple',width=2)
            text_to_show = '({0},{1})'.format(*self.mt_end)
            draw.text((end_x-len(text_to_show)*16,end_y-40),text_to_show,font=label_pos_show_text,fill='purple')
            # 主文本标记
            m_x,m_y = self.mt_pos
            draw.line([m_x-100,m_y,m_x+100,m_y],fill='blue',width=2)
            draw.line([m_x,m_y-50,m_x,m_y+50],fill='blue',width=2)
            draw.text((m_x,m_y-40),'({0},{1})'.format(*self.mt_pos),font=label_pos_show_text,fill='blue')
        return bubble_canvas
    def preview(self,image_canvas):
        import random
        # 自适应气泡预览时，行数随机
        bubble_canvas = self.draw(random.randint(1,7))
        image_canvas.paste(bubble_canvas,self.pos.get(),mask=bubble_canvas)
        self.pos.preview(image_canvas)
    
class ChatWindow(Bubble):
    def __init__(self,filepath=None,sub_key=['Key1'],sub_Bubble=[Bubble()],sub_Anime=[],sub_align=['left'],pos=(0,0),sub_pos=(0,0),sub_end=(0,0),am_left=0,am_right=0,sub_distance=50,label_color='Lavender'):
        if len(sub_Bubble) != len(sub_key):
            raise Exception('length of sub-key and sub-bubble does not match!')
        # 空白底图
        if filepath is None or filepath == 'None':
            self.media = Image.new('RGBA',(1920,1080),(0,0,0,0))
            self.size = (1920,1080)
        else:
            self.media = Image.open(filepath).convert('RGBA')
            self.size = self.media.size
        # 位置
        if type(pos) in [Pos,FreePos]:
            self.pos = pos
        else:
            self.pos = Pos(*pos)
        # 子气泡和对齐
        self.sub_Bubble = {}
        self.sub_Anime = {}
        self.sub_align = {}
        for i,key in enumerate(sub_key):
            # 检查气泡是否是 Ballon
            if type(sub_Bubble[i]) is Balloon:
                raise Exception('Ballon object "'+key+'" is not supported to be set as a sub-bubble of ChatWindow!')
            self.sub_Bubble[key] = sub_Bubble[i]
            # 载入对齐，默认是左对齐
            try:
                if sub_align[i] in ['left','right']:
                    self.sub_align[key] = sub_align[i]
                else:
                    raise Exception('Unsupported align: '+sub_align[i])
            except IndexError:
                self.sub_align[key] = 'left'
            # 载入子立绘，默认是None
            try:
                self.sub_Anime[key] = sub_Anime[i]
            except IndexError:
                self.sub_Anime[key] = None
        # 子气泡尺寸
        if (sub_pos[0] >= sub_end[0]) | (sub_pos[1] >= sub_end[1]):
            raise Exception('Invalid bubble separate params sub_end!')
        else:
            self.sub_size = (sub_end[0]-sub_pos[0],sub_end[1]-sub_pos[1])
            self.sub_pos = sub_pos
        # 立绘对齐位置
        if am_left >= am_right:
            raise Exception('Invalid bubble separate params am_right!')
        else:
            self.am_left = am_left
            self.am_right = am_right
        # 子气泡间隔
        self.sub_distance = sub_distance
    def draw(self,show_marker=True):
        # 主容器
        bubble_canvas = self.media.copy()
        draw = ImageDraw.Draw(bubble_canvas)
        # 子气泡容器
        sub_canvas = Image.new(mode='RGBA',size=self.sub_size,color=(0,0,0,0))
        # 子立绘容器
        am_canvas = Image.new(mode='RGBA',size=(self.am_right-self.am_left,self.sub_size[1]),color=(0,0,0,0))
        # 渲染子气泡
        y_bottom = self.sub_size[1] # 当前句子的可用y底部
        for key_this in self.sub_Bubble.keys():
            subbubble_canvas = self.sub_Bubble[key_this].draw(lines=1,show_marker=False)
            subbubble_size = subbubble_canvas.size
            if self.sub_align[key_this] == 'left':
                sub_canvas.paste(subbubble_canvas,(0,y_bottom-subbubble_size[1]))
                if self.sub_Anime[key_this] is not None:
                    am_canvas.paste(self.sub_Anime[key_this].media,(0,y_bottom-subbubble_size[1]))
            else:
                sub_canvas.paste(subbubble_canvas,(self.sub_size[0]-subbubble_size[0],y_bottom-subbubble_size[1]))
                if self.sub_Anime[key_this] is not None:
                    am_canvas.paste(self.sub_Anime[key_this].media,(self.am_right-self.am_left-self.sub_Anime[key_this].size[0],y_bottom-subbubble_size[1]))
            y_bottom = y_bottom - subbubble_size[1] - self.sub_distance
            if y_bottom < 0:
                break
        bubble_canvas.paste(sub_canvas,self.sub_pos,mask=sub_canvas)
        bubble_canvas.paste(am_canvas,(self.am_left,self.sub_pos[1]),mask=am_canvas)
        # 显示标记
        if show_marker:
            # 可变气泡分割显示：
            size = self.size
            # 起点，
            draw.line([0,self.sub_pos[1],size[0],self.sub_pos[1]],fill='purple',width=2)
            draw.line([self.sub_pos[0],0,self.sub_pos[0],size[1]],fill='purple',width=2)
            draw.text(self.sub_pos,'({0},{1})'.format(*self.sub_pos),font=label_pos_show_text,fill='purple')
            # 终点
            end_x = self.sub_pos[0] + self.sub_size[0]
            end_y = self.sub_pos[1] + self.sub_size[1]
            draw.line([0,end_y,size[0],end_y],fill='purple',width=2)
            draw.line([end_x,0,end_x,size[1]],fill='purple',width=2)
            text_to_show = '({0},{1})'.format(end_x,end_y)
            draw.text((end_x-len(text_to_show)*16,end_y-40),text_to_show,font=label_pos_show_text,fill='purple')
            # 立绘边界
            draw.line([self.am_left,0,self.am_left,size[1]],fill='red',width=2)
            draw.line([self.am_right,0,self.am_right,size[1]],fill='red',width=2)
            # 左侧标记
            draw.text((self.am_left,self.sub_pos[1]-40),'({0},{1})'.format(self.am_left,self.sub_pos[1]),font=label_pos_show_text,fill='red')
            # 右侧标记
            text_to_show = '({0},{1})'.format(self.am_right,end_y)
            draw.text((self.am_right-len(text_to_show)*16,end_y),text_to_show,font=label_pos_show_text,fill='red')
        return bubble_canvas

class Background(Media):
    cmap = {'black':(0,0,0,255),'white':(255,255,255,255),'greenscreen':(0,177,64,255)}
    def __init__(self,filepath,pos = (0,0),label_color='Lavender'):
        if filepath in Background.cmap.keys(): #添加了，对纯色定义的背景的支持
            self.media = Image.new(mode='RGBA',size=(1920,1080),color=Background.cmap[filepath]) # GUI里面没有全局的screen_size，用1080p的参数替代
        else:
            self.media = Image.open(filepath).convert('RGBA')
        if type(pos) in [Pos,FreePos]:
            self.pos = pos
        else:
            self.pos = Pos(*pos)
    def preview(self,image_canvas):
        if self.media.mode == 'RGBA':
            image_canvas.paste(self.media,self.pos.get(),mask=self.media.split()[-1])
        else:
            image_canvas.paste(self.media,self.pos.get())
        draw = ImageDraw.Draw(image_canvas)
        p_x,p_y = self.pos.get()
        draw.line([p_x-100,p_y,p_x+100,p_y],fill='green',width=2)
        draw.line([p_x,p_y-100,p_x,p_y+100],fill='green',width=2)
        draw.text((p_x,p_y),'({0},{1})'.format(p_x,p_y),font=label_pos_show_text,fill='green')
class Animation(Media):
    def __init__(self,filepath,pos = (0,0),tick=1,loop=True,label_color='Lavender'):
        if '*' in filepath:
            raise ValueError('动画对象不支持预览！')
        else:
            self.media = Image.open(filepath).convert('RGBA')
        if type(pos) in [Pos,FreePos]:
            self.pos = pos
        else:
            self.pos = Pos(*pos)
        self.size = self.media.size
        self.loop = loop
        self.this = 0
        self.tick = tick
    def preview(self,image_canvas):
        if self.media.mode == 'RGBA':
            image_canvas.paste(self.media,self.pos.get(),mask=self.media.split()[-1])
        else:
            image_canvas.paste(self.media,self.pos.get())
        draw = ImageDraw.Draw(image_canvas)
        p_x,p_y = self.pos.get()
        draw.line([p_x-100,p_y,p_x+100,p_y],fill='green',width=2)
        draw.line([p_x,p_y-100,p_x,p_y+100],fill='green',width=2)
        draw.text((p_x,p_y),'({0},{1})'.format(p_x,p_y),font=label_pos_show_text,fill='green')

# class GroupedAnimation(Animation)
# GroupedAnimation 更多的情况还是作为BIA在使用，还是不要开放给媒体定义文件用了。
