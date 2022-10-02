from PIL import Image, ImageDraw, ImageFont

label_pos_show_text = ImageFont.truetype('./media/SourceHanSerifSC-Heavy.otf', 30)


class Media:
    """
    这个公共类只是为了以后可能的扩展，目前用不到
    """
    def __init__(self):
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
    def __init__(self,fontfile='./media/SourceHanSansCN-Regular.otf',fontsize=40,color=(0,0,0,255),line_limit=20,edge_color=(255,255,255,255),label_color='Lavender'):
        super().__init__(fontfile=fontfile,fontsize=fontsize,color=color,line_limit=line_limit,label_color=label_color)
        self.edge_color=edge_color
    def draw(self,lenth=-1):
        if lenth ==-1:
            lenth = self.line_limit
        test_canvas = Image.new(mode='RGBA',size=(self.size*int(self.line_limit*1.5),self.size*2),color=(0,0,0,0))#高度贪婪2x,宽度贪婪1.5x
        test_draw = ImageDraw.Draw(test_canvas)
        for pos in [(0,0),(0,1),(0,2),(1,0),(1,2),(2,0),(2,1),(2,2)]:
            test_draw.text(pos, ('测试文本'*50)[0:lenth], font = self.text_render,fill = self.edge_color)
        test_draw.text((1,1), ('测试文本'*50)[0:lenth], font = self.text_render,fill = self.color)
        p1,p2,p3,p4 = test_canvas.getbbox()
        return test_canvas.crop((0,0,p3,p4))
class Bubble(Media):
    def __init__(self,filepath=None,Main_Text=Text(),Header_Text=None,pos=(0,0),mt_pos=(0,0),ht_pos=(0,0),align='left',line_distance=1.5,label_color='Lavender'):
        if filepath is None or filepath == 'None': # 支持气泡图缺省
            self.media  = Image.new(mode='RGBA',size=(1920,1080),color=(0,0,0,0))
        else:
            self.media = Image.open(filepath)
        self.pos = pos
        self.MainText = Main_Text
        self.mt_pos = mt_pos
        self.Header = Header_Text
        self.ht_pos = ht_pos
        self.line_distance = line_distance
        if align in ('left','center'):
            self.align = align
        else:
            raise ValueError('align非法参数：',align)
    def preview(self,image_canvas):
        def pos_add(pos1,pos2):
            return pos1[0]+pos2[0],pos1[1]+pos2[1]
        draw = ImageDraw.Draw(image_canvas)
        p_x,p_y = self.pos
        h_x,h_y = pos_add(self.ht_pos,self.pos)
        m_x,m_y = pos_add(self.mt_pos,self.pos)
        if self.media.mode == 'RGBA':
            image_canvas.paste(self.media,self.pos,mask=self.media.split()[-1])
        else:
            image_canvas.paste(self.media,self.pos)
        draw.line([p_x-100,p_y,p_x+100,p_y],fill='green',width=2)
        draw.line([p_x,p_y-100,p_x,p_y+100],fill='green',width=2)
        draw.text((p_x,p_y),'({0},{1})'.format(p_x,p_y),font=label_pos_show_text,fill='green')
        if self.Header != None:
            draw_text = self.Header.draw()
            image_canvas.paste(draw_text,pos_add(self.ht_pos,self.pos),draw_text.split()[-1])
            draw.line([h_x-100,h_y,h_x+100,h_y],fill='blue',width=2)
            draw.line([h_x,h_y-50,h_x,h_y+50],fill='blue',width=2)
            draw.text((h_x,h_y-35),'({0},{1})'.format(h_x-p_x,h_y-p_y),font=label_pos_show_text,fill='blue')
        if self.MainText != None:
            tx_w = self.MainText.size*self.MainText.line_limit
            tx_h = self.line_distance*self.MainText.size
            mx,my = self.mt_pos
            for i,l in enumerate(range(self.MainText.line_limit,0,-self.MainText.line_limit//4)):
                draw_text = self.MainText.draw(l)
                image_canvas.paste(draw_text,pos_add(self.pos,(int(mx+(tx_w-draw_text.size[0])//2*(self.align=='center')),int(my+i*tx_h))),draw_text.split()[-1])
            draw.line([m_x-100,m_y,m_x+100,m_y],fill='blue',width=2)
            draw.line([m_x,m_y-50,m_x,m_y+50],fill='blue',width=2)
            draw.text((m_x,m_y-35),'({0},{1})'.format(m_x-p_x,m_y-p_y),font=label_pos_show_text,fill='blue')
class Background(Media):
    cmap = {'black':(0,0,0,255),'white':(255,255,255,255),'greenscreen':(0,177,64,255)}
    def __init__(self,filepath,pos = (0,0),label_color='Lavender'):
        if filepath in Background.cmap.keys(): #添加了，对纯色定义的背景的支持
            self.media = Image.new(mode='RGBA',size=(1920,1080),color=Background.cmap[filepath]) # GUI里面没有全局的screen_size，用1080p的参数替代
        else:
            self.media = Image.open(filepath)
        self.pos = pos
    def preview(self,image_canvas):
        if self.media.mode == 'RGBA':
            image_canvas.paste(self.media,self.pos,mask=self.media.split()[-1])
        else:
            image_canvas.paste(self.media,self.pos)
        draw = ImageDraw.Draw(image_canvas)
        p_x,p_y = self.pos
        draw.line([p_x-100,p_y,p_x+100,p_y],fill='green',width=2)
        draw.line([p_x,p_y-100,p_x,p_y+100],fill='green',width=2)
        draw.text((p_x,p_y),'({0},{1})'.format(p_x,p_y),font=label_pos_show_text,fill='green')
class Animation(Media):
    def __init__(self,filepath,pos = (0,0),tick=1,loop=True,label_color='Lavender'):
        if '*' in filepath:
            raise ValueError('动画对象不支持预览！')
        else:
            self.media = Image.open(filepath)
        self.pos = pos
        self.loop = loop
        self.this = 0
        self.tick = tick
    def preview(self,image_canvas):
        if self.media.mode == 'RGBA':
            image_canvas.paste(self.media,self.pos,mask=self.media.split()[-1])
        else:
            image_canvas.paste(self.media,self.pos)
        draw = ImageDraw.Draw(image_canvas)
        p_x,p_y = self.pos
        draw.line([p_x-100,p_y,p_x+100,p_y],fill='green',width=2)
        draw.line([p_x,p_y-100,p_x,p_y+100],fill='green',width=2)
        draw.text((p_x,p_y),'({0},{1})'.format(p_x,p_y),font=label_pos_show_text,fill='green')
