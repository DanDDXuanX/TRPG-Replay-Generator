#!/usr/bin/env python
# coding: utf-8
# 标记语言 <-> json{dic}

import numpy as np
import pandas as pd

import os
import json

from .Exceptions import DecodeError,ParserError,WarningPrint,SyntaxsError
from .Regexs import *
from .Formulas import *
from .Medias import Text,StrokeText,RichText,Bubble,Balloon,DynamicBubble,ChatWindow,Animation,GroupedAnimation,Dice,HitPoint,Background,BGM,Audio
from .FreePos import Pos,FreePos,PosGrid
from .FilePaths import Filepath
from .ProjConfig import Config
from .Motion import MotionMethod
from .Utils import concat_xy

# 输入文件，基类
class Script:
    # 类型名对应的Class
    Media_type = {
        'Pos':Pos,'FreePos':FreePos,'PosGrid':PosGrid,
        'Text':Text,'StrokeText':StrokeText,'RichText':RichText,
        'Bubble':Bubble,'Balloon':Balloon,'DynamicBubble':DynamicBubble,'ChatWindow':ChatWindow,
        'Animation':Animation,'GroupedAnimation':GroupedAnimation,'HitPoint':HitPoint,'Dice':Dice,
        'Background':Background,
        'BGM':BGM,'Audio':Audio
        }
    # 类型名对应的参数列表
    type_keyword_position = {
        'Pos'           :['pos'],
        'FreePos'       :['pos'],
        'PosGrid'       :['pos','end','x_step','y_step'],
        'Text'          :['fontfile','fontsize','color','line_limit','label_color'],
        'StrokeText'    :['fontfile','fontsize','color','line_limit','edge_color','edge_width','projection','label_color'],
        'RichText'      :['fontfile','fontsize','color','line_limit','label_color'],
        'Bubble'        :['filepath','scale','Main_Text','Header_Text','pos','mt_pos','ht_pos','ht_target','align','line_distance','label_color'],
        'Balloon'       :['filepath','scale','Main_Text','Header_Text','pos','mt_pos','ht_pos','ht_target','align','line_distance','label_color'],
        'DynamicBubble' :['filepath','scale','Main_Text','Header_Text','pos','mt_pos','mt_end','ht_pos','ht_target','fill_mode','fit_axis','line_distance','label_color'],
        'ChatWindow'    :['filepath','scale','sub_key','sub_Bubble','sub_Anime','sub_align','pos','sub_pos','sub_end','am_left','am_right','sub_distance','label_color'],
        'Background'    :['filepath','scale','pos','label_color'],
        'Animation'     :['filepath','scale','pos','tick','loop','label_color'],
        'Audio'         :['filepath','label_color'],
        'BGM'           :['filepath','volume','loop','label_color']
        }
    type_keyword_default = {
        'Pos'           :[[0,0]],
        'FreePos'       :[[0,0]],
        'PosGrid'       :[[0,0],[100,100],2,2],
        'Text'          :['./media/SourceHanSansCN-Regular.otf',40,[0,0,0,255],20,'Lavender'],
        'StrokeText'    :['./media/SourceHanSansCN-Regular.otf',40,[0,0,0,255],20,[255,255,255,255],1,'C','Lavender'],
        'RichText'      :['./media/SourceHanSansCN-Regular.otf',40,[0,0,0,255],20,'Lavender'],
        'Bubble'        :[None,1.0,{'type':'Text'},None,[0,0],[0,0],[0,0],'Name','left',1.5,'Lavender'],
        'Balloon'       :[None,1.0,{'type':'Text'},[None],[0,0],[0,0],[[0,0]],['Name'],'left',1.5,'Lavender'],
        'DynamicBubble' :[None,1.0,{'type':'Text'},None,[0,0],[0,0],[100,100],[0,0],'Name','stretch','free',1.5,'Lavender'],
        'ChatWindow'    :[None,1.0,['关键字'],[{'type':'Bubble'}],[None],['left'],[0,0],[0,0],[100,100],0,100,0,'Lavender'],
        'Background'    :['black',1.0,[0,0],'Lavender'],
        'Animation'     :['./media/heart_shape.png',1.0,[0,0],1,True,'Lavender'], # TODO:这个默认的filepath应该修改！
        'Audio'         :['./media/SE_dice.wav','Caribbean'], # TODO:这个默认的filepath应该修改！
        'BGM'           :['./toy/media/BGM.ogg',100,True,'Caribbean'] # TODO:这个默认的filepath应该修改！
        }
    # 初始化
    def __init__(self,string_input=None,dict_input=None,file_input=None,json_input=None) -> None:
        # 字符串输入
        if string_input is not None:
            self.struct:dict = self.parser(script=string_input)
        # 字典 输入：不安全的方法
        elif dict_input is not None:
            self.struct:dict = dict_input.copy()
        # 如果输入了脚本文件
        elif file_input is not None:
            self.struct:dict = self.parser(script=self.load_file(filepath=file_input))
        # 如果输入了json文件：不安全的方法
        elif json_input is not None:
            self.struct:dict = self.load_json(filepath=json_input)
        # 如果没有输入
        else:
            self.struct:dict = {}
    # 读取文本文件
    def load_file(self,filepath:str)->str:
        try:
            stdin_text = open(filepath,'r',encoding='utf-8').read()
        except UnicodeDecodeError as E:
            raise DecodeError('DecodeErr',E)
        # 清除 UTF-8 BOM
        if stdin_text[0] == '\ufeff':
            print(WarningPrint('UFT8BOM'))
            stdin_text = stdin_text[1:]
        return stdin_text
    # 将读取的文本文件解析为json
    def load_json(self,filepath:str)->dict:
        return json.loads(self.load_file(filepath=filepath))
    # 保存为文本文件
    def dump_file(self,filepath:str)->None:
        list_of_scripts = self.export()
        with open(filepath,'w',encoding='utf-8') as of:
            of.write(list_of_scripts)
    # 保存为json
    def dump_json(self,filepath:str)->None:
        with open(filepath,'w',encoding='utf-8') as of:
            of.write(json.dumps(self.struct,indent=4))
    # 深复制
    def copy(self):
        return self.__class__(dict_input=self.struct)
    # 待重载的：
    def parser(self,script:str)->dict:
        return {}
    def export(self)->str:
        return ''
    # 删除
    def delete(self, key):
        self.struct.pop(key)
    # 添加
    def add(self, key:str, section:dict):
        self.struct[key] = section.copy()
# 媒体定义文件
class MediaDef(Script):
    def __init__(self, string_input=None, dict_input=None, file_input=None, json_input=None) -> None:
        super().__init__(string_input, dict_input, file_input, json_input)
        # 媒体的相对位置@
        if file_input is not None:
            self.media_path = os.path.dirname(file_input.replace('\\','/'))
        elif json_input is not None:
            self.media_path = os.path.dirname(json_input.replace('\\','/'))
        else:
            self.media_path = Filepath.RplGenpath
        # 执行媒体类的类变量变更
        # Filepath.Mediapath = self.media_path # 因为MediaDef()用的太多了，不能在初始化的时候这样用了！
        # raise Exception()
    # MDF -> struct
    def list_parser(self,list_str:str)->list:
        # 列表，元组，不包含外括号
        list_str = list_str.replace(' ','')
        values = re.findall("(\w+\(\)|\[[-\w,.\ ]+\]|\([-\d,.\ ]+\)|\w+\[[\d\,]+\]|[^,()]+)",list_str)
        this_list = []
        for value in values:
            this_list.append(self.value_parser(value))
        return this_list
    def subscript_parser(self,obj_name:str,sub_indexs:str)->dict:
        # Object[1,2]
        this_subscript = {'type':'subscript','object':'$'+obj_name}
        this_subscript['index'] = self.list_parser(sub_indexs)
        return this_subscript
    def value_parser(self,value:str):
    # 数值、字符串、列表、实例化、subs、对象
        # 1. 是数值
        if re.match('^-?[\d\.]+(e-?\d+)?$',value):
            if '.' in value:
                return float(value)
            else:
                return int(value)
        # 2. 是字符串
        elif re.match('^(\".+\"|\'.+\')$',value):
            return value[1:-1]
        # 3. 是列表或者元组：不能嵌套！
        elif re.match('^\[.+\]|\(.+\)$',value):
            return self.list_parser(value[1:-1])
        # 4. 是另一个实例化: Class()
        elif re.match('^[a-zA-Z_]\w*\(.*\)$',value):
            obj_type,obj_value = re.findall('^([a-zA-Z_]\w*)\((.*)\)$',string=value)[0]
            return self.instance_parser(obj_type,obj_value)
        # 5. 是一个subscript: Obj[1]
        elif re.match('^\w+\[[\d\, ]+\]$',value):
            obj_name,sub_indexs = re.findall('(\w+)\[([\d\, ]+)\]$',string=value)[0]
            return self.subscript_parser(obj_name,sub_indexs)
        # 6. 是特殊的常量
        elif value in ('False','True','None'):
            return {'False':False,'True':True,'None':None}[value]
        # 7. 是一个对象名 Obj
        elif re.match('^\w*$',value) and value[0].isdigit()==False:
            return '$' + value
        else:
            raise SyntaxsError('InvExp',value)
    def instance_parser(self,obj_type:str,obj_args:str)->dict:
        # 实例化
        this_instance = {'type':obj_type}
        # Pos 类型
        if obj_type in ['Pos','FreePos']:
            this_instance['pos'] = self.list_parser(obj_args)
            return this_instance
        # 其他类型
        else:
            args_list = RE_mediadef_args.findall(obj_args)
            allow_position_args = True
            for i,arg in enumerate(args_list):
                keyword,value = arg
                # 关键字
                if keyword == '':
                    if allow_position_args == True:
                        try:
                            keyword = self.type_keyword_position[obj_type][i]
                        except IndexError:
                            # 给媒体指定了过多的参数
                            SyntaxsError('ToMuchArgs',obj_type)
                    else:
                        # 非法使用的顺序参数
                        print(args_list)
                        raise SyntaxsError('BadPosArg')
                else:
                    allow_position_args = False
                # 值
                this_instance[keyword] = self.value_parser(value)
            return this_instance
    def parser(self,script:str) -> dict:
        # 分割小节
        object_define_text = script.split('\n')
        # 结构体
        struct = {}
        # 逐句读取小节
        for i,text in enumerate(object_define_text):
            # 空行
            if text == '':
                struct[str(i)] = {'type':'blank'}
                continue
            # 备注
            elif text[0] == '#':
                struct[str(i)] = {'type':'comment','content':text[1:]}
                continue
            # 有内容的
            try:
                # 尝试解析媒体定义文件
                obj_name,obj_type,obj_args = RE_mediadef.findall(text)[0]
            except:
                # 格式不合格的行直接报错
                try:
                    obj_name,value_obj = RE_subscript_def.findall(text)[0]
                    struct[obj_name] = self.value_parser(value_obj)
                    continue
                except Exception:
                    raise SyntaxsError('MediaDef',text,str(i+1))
            else:
                # 格式合格的行开始解析
                try:
                    # 如果是非法的标识符
                    if (len(re.findall('\w+',obj_name))==0)|(obj_name[0].isdigit()):
                        raise SyntaxsError('InvaName')
                    else:
                        this_section = self.instance_parser(obj_type,obj_args[1:-1])
                except Exception as E:
                    print(E)
                    raise SyntaxsError('MediaDef',text,str(i+1))
                struct[obj_name] = this_section
        return struct
    # struct -> MDF
    def instance_export(self,media_object:dict)->str:
        type_this = media_object['type']
        if type_this == 'subscript':
            # 要去掉对象名前的$
            return media_object['object'][1:] + self.list_export(media_object['index'],is_tuple=False)
        elif type_this in ['Pos','FreePos']:
            return type_this + self.list_export(media_object['pos'],is_tuple=True)
        else:
            argscript_list = []
            for key in media_object.keys():
                if key == 'type':
                    continue
                else:
                    argscript_list.append(key + '=' + self.value_export(media_object[key]))
            return type_this + '(' + ','.join(argscript_list) + ')'
    def list_export(self,list_object:list,is_tuple=True)->str:
        list_unit = []
        for unit in list_object:
            if type(unit) not in [int,float]:
                is_tuple = False
            list_unit.append(self.value_export(unit))
        # 注意：纯数值组成的列表使用tuple
        if is_tuple:
            return '(' + ','.join(list_unit) + ')'
        # 反之必须使用list，源于解析的要求
        else:
            return '[' + ','.join(list_unit) + ']'
    def value_export(self,unit:object)->str:
        # 常量
        if type(unit) in [int,float]:
            return str(unit)
        elif type(unit) is bool:
            return {False:'False',True:'True'}[unit]
        elif unit is None:
            return 'None'
        # 字符串
        elif type(unit) is str:
            # 如果是一个引用对象
            if unit[0] == '$':
                return unit[1:]
            else:
                if "'" in unit:
                    unit.replace("'","\\'")
                return "'" + unit + "'"
        # 列表
        elif type(unit) is list:
            return self.list_export(unit)
        # 对象
        elif type(unit) is dict:
            return self.instance_export(unit)
        # 其他
        else:
            return ''       
    def export(self)->str:
        list_of_scripts = []
        for key in self.struct.keys():
            obj_this:dict = self.struct[key]
            type_this:str = obj_this['type']
            # 空行
            if type_this == 'blank':
                this_script = ''
            # 备注
            elif type_this == 'comment':
                this_script = '#' + obj_this['content']
            # 实例化
            else:
                this_script = key + ' = ' + self.instance_export(obj_this)
            # 添加到列表
            list_of_scripts.append(this_script)
        # 返回
        return '\n'.join(list_of_scripts)
    # 执行：实例化媒体定义文件中的媒体类，并保存在 self.Medias:dict
    def instance_execute(self,instance_dict:dict)->object:
        # 本行的类型
        type_this:str  = instance_dict['type']
        if type_this in ['blank','comment']:
            # 如果是空行或者备注
            return None
        elif type_this == 'subscript':
            # 如果是subscript
            object_this = self.reference_object_execute(instance_dict['object'])
            index_this:list = instance_dict['index']
            # 借用魔法方法
            return object_this.__getitem__(index_this)
        elif type_this in ['Pos','FreePos']:
            # 如果是采取特殊实例化
            ClassThis:type = self.Media_type[type_this]
            pos_this:list = self.list_execute(instance_dict['pos'])
            return ClassThis(*pos_this)
        else:
            # 建立关键字字典
            ClassThis:type = self.Media_type[type_this]
            this_instance_args = {}
            # 遍历元素
            for key in instance_dict.keys():
                if key == 'type':
                    continue
                else:
                    value_this = instance_dict[key]
                    this_instance_args[key] = self.value_execute(value_this)
            # 实例化
            return ClassThis(**this_instance_args)       
    def list_execute(self,list_object:list)->list:
        this_list_unit = []
        for unit in list_object:
            this_list_unit.append(self.value_execute(unit))
        return this_list_unit
    def value_execute(self,unit:object)->object:
        if type(unit) is str:
            if unit[0] == '$':
                return self.reference_object_execute(unit)
            else:
                return unit
        elif type(unit) is dict:
            # 递归调用 instance_execute
            return self.instance_execute(unit)
        elif type(unit) is list:
            # 是列表
            return self.list_execute(unit)
        else:
            # 是值
            return unit
    def reference_object_execute(self,reference_name:str)->object:
        # 根据 $媒体名 返回 媒体对象
        media_name = reference_name[1:]
        try:
            return self.Medias[media_name]
        except Exception:
            # 强制实例化
            if media_name in self.struct.keys():
                try:
                    obj_dict_this = self.struct[media_name]
                    return self.instance_execute(obj_dict_this)
                except Exception as E:
                    print(E)
                    text = self.instance_export(obj_dict_this)
                    raise SyntaxsError('MediaDef',text,'?') # TODO:改改这个SyntaxsError的输出文本吧
            else:
                raise SyntaxsError('UndefName',media_name)
    def execute(self) -> dict:
        # 媒体对象的容器
        self.Medias = {}
        # 每一个媒体类
        for i,obj_name in enumerate(self.struct.keys()):
            # 来自结构体
            obj_dict_this:dict = self.struct[obj_name]
            # 实例化
            try:
                object_this = self.instance_execute(obj_dict_this)
            except Exception as E:
                print(E)
                text = self.instance_export(obj_dict_this)
                raise SyntaxsError('MediaDef',text,str(i+1)) # TODO:改改这个SyntaxsError的输出文本吧
            # 保存:
            if object_this is None:
                pass
            else:
                self.Medias[obj_name] = object_this
        return self.Medias
    # 访问:
    def get_type(self,_type,cw=True) -> list:
        type_name = {
            'anime'     :['Animation'],
            'bubble'    :['Bubble','Balloon','DynamicBubble'],
            'text'      :['Text','StrokeText','RichText'],
            'pos'       :['Pos','FreePos'],
            'freepos'   :['FreePos'],
            'background':['Background'],
            'audio'     :['Audio'],
            'bgm'       :['BGM'],
            'chatwindow':['ChatWindow']
        }
        output = []
        type_this:list = type_name[_type]
        for keys in self.struct:
            section_this = self.struct[keys]
            if section_this['type'] in type_this:
                output.append(keys)
            # 在bubble类里的ChatWindow
            elif cw and _type == 'bubble' and section_this['type'] == 'ChatWindow':
                for sub_key in section_this['sub_key']:
                    output.append(keys + ':' + sub_key)
        output.sort()
        return output
    def get_moveable(self):
        return (
            self.get_type('freepos') + 
            self.get_type('anime') + 
            self.get_type('bubble',cw=False) + 
            self.get_type('chatwindow') + 
            self.get_type('background')
        )
    def update_media_file(self,name:str,old_path:str,new_path:str):
        this_section = self.struct[name]
        # 获取关键字
        if this_section['type'] in ['Text','StrokeText','RichText']:
            keyword = 'fontfile'
        else:
            keyword = 'filepath'
        # 检查old是匹配的，才更新为new
        if this_section[keyword] == old_path:
            this_section[keyword] = new_path
        else:
            print(name, old_path, this_section[keyword])
    # 操作：
    def rename(self,to_rename:str,new_name:str)->dict:
        self.struct[new_name] = self.struct.pop(to_rename)
        return self.struct[new_name]
    def new_element(self,name:str,element_type:str)->str:
        while name in self.struct:
            name += '_new'
        else:
            new_struct = {
                'type' : element_type,
            }
            for key,args in zip(self.type_keyword_position[element_type],self.type_keyword_default[element_type]):
                new_struct[key] = args
            # 应用变更
            self.struct[name] = new_struct
        # 返回关键字
        return name

# 角色配置文件
class CharTable(Script):
    table_col = ['Name','Subtype','Animation','Bubble','Voice','SpeechRate','PitchRate']
    # 初始化
    def __init__(self,table_input=None,dict_input=None,file_input=None,json_input=None) -> None:
        # DataFrame 输入
        if table_input is not None:
            self.struct:dict = self.parser(table=table_input)
        # 字典 输入
        elif dict_input is not None:
            self.struct:dict = dict_input
        # 如果输入了 tsv、xlsx、xls
        elif file_input is not None:
            self.struct:dict = self.parser(table=self.load_table(filepath=file_input))
        # 如果输入了json文件：不安全的方法
        elif json_input is not None:
            self.struct:dict = self.load_json(filepath=json_input)
        # 如果没有输入
        else:
            self.struct:dict = {}
    # 从文件读取表格
    def load_table(self, filepath: str) -> pd.DataFrame:
        # 读取表格，并把表格中的空值处理为 "NA"
        try:
            if filepath.split('.')[-1] in ['xlsx','xls']:
                # 是excel表格
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore') # 禁用读取excel时报出的：UserWarning: Data Validation extension is not supported and will be removed
                    # 支持excel格式的角色配置表，默认读取sheet1
                    charactor_table:pd.DataFrame = pd.read_excel(filepath,dtype = str).fillna('NA')
            else:
                # 是tsv
                charactor_table:pd.DataFrame = pd.read_csv(filepath,sep='\t',dtype = str).fillna('NA')
            # 用 'NA' 填补角色表的缺失值 ['Animation','Bubble','Voice']
            for colname in ['Animation','Bubble','Voice']:
                if colname not in charactor_table.columns:
                    charactor_table[colname] = 'NA'
                else:
                    charactor_table[colname] = charactor_table[colname].fillna('NA')
            # 用 0 填补语速和语调列
            for colname in ['SpeechRate','PitchRate']:
                if colname not in charactor_table.columns:
                    charactor_table[colname] = 0
                else:
                    charactor_table[colname] = charactor_table[colname].replace('NA',0).fillna(0).astype(int)
            # key，必须要unique
            charactor_table.index = charactor_table['Name']+'.'+charactor_table['Subtype']
            if charactor_table.index.is_unique == False:
                duplicate_subtype_name = charactor_table.index[charactor_table.index.duplicated()][0]
                raise SyntaxsError('DupSubtype',duplicate_subtype_name)
        except Exception as E:
            raise SyntaxsError('CharTab',E)
        # 如果角色表缺省关键列
        if ('Animation' not in charactor_table.columns) | ('Bubble' not in charactor_table.columns):
            raise SyntaxsError('MissCol')
        # 返回角色表格
        return charactor_table
    # 将DataFrame 解析为 dict：
    def parser(self, table: pd.DataFrame) -> dict:
        # 正常是to_dict 是以列为key，需要转置为以行为key
        return table.T.to_dict()
    # 将 dict 转为 DataFrame
    def export(self)->pd.DataFrame:
        # dict -> 转为 DataFrame，把潜在的缺失值处理为'NA'
        table_col = self.table_col
        chartab = pd.DataFrame(self.struct).T.fillna('NA')
        if len(chartab) == 0:
            chartab = pd.DataFrame(columns=table_col)
            return chartab
        else:
            customize_col = self.get_customize(chartab)
            return chartab[table_col+customize_col]
    # 保存为文本文件 (tsv)
    def dump_file(self,filepath:str)->None:
        charactor_table = self.export()
        charactor_table.to_csv(filepath,sep='\t',index=False)
    # 执行：角色表哪儿有需要执行的哦，直接返回自己的表就行了
    def execute(self) -> pd.DataFrame:
        return self.export().copy()
    # 变动角色名
    def rename(self,to_rename:str,new_name:str):
        chartable:pd.DataFrame = self.export()
        chartable['Name'] = chartable['Name'].replace(to_rename,new_name)
        chartable.index = chartable['Name']+'.'+chartable['Subtype']
        self.struct = self.parser(chartable)
    def resubtype(self,to_resubtype:str,new_subtype:str)->dict:
        # 新建项目
        self.struct[new_subtype] = self.struct.pop(to_resubtype)
        return self.struct[new_subtype]
    # 删除整个角色
    def delete_chara(self,name:str):
        # 获取需要删除的列表
        list_to_delete = []
        for key in self.struct:
            if key.split('.')[0] == name:
                list_to_delete.append(key)
        # 执行删除
        for key in list_to_delete:
            self.delete(key)
    # 添加角色的默认差分
    def add_chara_default(self,name:str):
        if name + '.default' not in self.struct.keys():
            self.struct[name+'.default'] = {
                'Name'      : name,
                'Subtype'   : 'default',
                'Animation' : 'NA',
                'Bubble'    : 'NA',
                'Voice'     : 'NA',
                'SpeechRate': 0,
                'PitchRate' : 0,
            }
    # 添加一个角色差分
    def new_subtype(self,name:str,subtype:str)->str:
        keyword  = name + '.' + subtype
        while keyword in self.struct:
            keyword += '_new'
            subtype += '_new'
        else:
            # 基本项目
            new_struct = {
                'Name'      : name,
                'Subtype'   : subtype,
                'Animation' : 'NA',
                'Bubble'    : 'NA',
                'Voice'     : 'NA',
                'SpeechRate': 0,
                'PitchRate' : 0,
            }
            # 自定义项目
            for custom in self.get_customize():
                new_struct[custom] = 'init'
            # 赋值
            self.struct[keyword] = new_struct
        # 返回关键字
        return keyword
    # 添加一个自定义
    def add_customize(self,colname):
        # 如果这个列名已经使用过了
        if colname in self.table_col or colname in self.customize_col:
            return
        else:
            for keyword in self.struct:
                self.struct[keyword][colname] = 'init'
    # 修改一个角色的内容
    def configure(self,key:str,section:dict):
        # 修改内容
        self.struct[key].update(section)
    # 读取
    # 获取所有可用角色、差分名
    def get_names(self)->list:
        table = self.execute()
        return table['Name'].unique().tolist()
    def get_subtype(self, name)->list:
        table = self.execute()
        try:
            return table[table['Name'] == name]['Subtype'].unique().tolist()
        except:
            return []
    def get_customize(self,df:pd.DataFrame=None)->list:
        try:
            return self.customize_col
        except AttributeError:
            if df is not None:
                chartab = df
            else:
                chartab = pd.DataFrame(self.struct).T.fillna('NA')
            self.customize_col = [col for col in chartab.columns if col not in self.table_col]
            return self.customize_col
# log文件
class RplGenLog(Script):
    # RGL -> struct
    def charactor_parser(self,cr:str,i=0)->dict: # [CH1,CH2,CH3]
        list_of_CR = RE_characor.findall(cr)
        this_charactor_set = {}
        if len(list_of_CR) > 3:
            # 角色不能超过3个!
            raise ParserError('2muchChara',str(i+1))
        for k,charactor in enumerate(list_of_CR[0:3]):
            this_charactor = {}
            # 名字 (透明度) .差分
            this_charactor['name'],alpha,subtype= charactor
            if subtype == '':
                this_charactor['subtype'] = 'default'
            else:
                this_charactor['subtype'] = subtype[1:] # 去除首字符.
            if alpha == '':
                this_charactor['alpha'] = None
            else:
                this_charactor['alpha'] = int(alpha[1:-1]) # 去掉首尾括号
            this_charactor_set[str(k)] = this_charactor
        return this_charactor_set
    def method_parser(self,method:str)->dict: # <method=0>
        this_section = {}
        if method == '':
            this_section['method'] = 'default'
            this_section['method_dur'] = 'default'
        else:
            this_section['method'],method_dur =RE_modify.findall(method)[0]
            if method_dur == '':
                this_section['method_dur'] = 'default'
            else:
                this_section['method_dur'] = int(method_dur[1:])
        return this_section
    def sound_parser(self,sound:str,i=0)->dict: # {SE;30}
        this_sound_set = {}
        if sound == '':
            return this_sound_set
        else:
            # 星标列表 {*}
            list_of_AS = RE_asterisk.findall(sound)
            # 没检测到星标
            if len(list_of_AS) == 0:  
                pass
            # 检查到一个星标
            elif len(list_of_AS) == 1:
                # obj;  time
                this_asterisk = {}
                # 音效
                if list_of_AS[0][1] == '':
                    this_asterisk['sound'] = None
                else:
                    this_asterisk['sound'] = list_of_AS[0][1][:-1] # 去除最后存在的分号
                # 时间
                if list_of_AS[0][-1] == '':
                    this_asterisk['time'] = None
                else:
                    try:
                        this_asterisk['time'] = float(list_of_AS[0][-1])
                    except Exception:
                        this_asterisk['time'] = None
                        if this_asterisk['sound'] is None:
                            # 指定发言内容
                            this_asterisk['specified_speech'] = list_of_AS[0][-1]
                if this_asterisk['sound'] is None or this_asterisk['time'] is None:
                    # 如果是待合成的
                    this_sound_set['{*}'] = this_asterisk
                else:
                    # 如果是合规的
                    this_sound_set['*'] = this_asterisk
            # 检测到复数个星标
            else:
                raise ParserError('2muchAster',str(i+1))
            # 音效列表 {}
            list_of_SE = RE_sound_simple.findall(sound)
            for k,se in enumerate(list_of_SE): #this_sound = ['{SE_obj;30}','{SE_obj;30}']
                this_soundeff = {}
                if ';' in se:
                    this_soundeff['sound'],delay = se[1:-1].split(';')
                    try:
                        this_soundeff['delay'] = int(delay)
                    except Exception:
                        this_soundeff['delay'] = 0
                else:
                    this_soundeff['sound'] = se[1:-1]
                    this_soundeff['delay'] = 0
                this_sound_set[str(k)] = this_soundeff
            # 给到上一层
            return this_sound_set
    def bubble_parser(self,bubble_exp:str,i=0)->dict: # Bubble("header_","main_text",<w2w=1>)
        # 解析
        try:
            this_bb,this_hd,this_tx,this_method_label,this_tx_method,this_tx_dur = RE_bubble.findall(bubble_exp)[0]
        except IndexError:
            raise ParserError('InvaPBbExp',bubble_exp,str(i+1))
        # 结构
        this_bubble = {}
        # 对象
        this_bubble['bubble'] = this_bb
        # 文字
        this_bubble['header_text'] = this_hd
        this_bubble['main_text'] = this_tx
        # 文字效果
        this_bubble['tx_method'] = self.method_parser(this_method_label)
        # 返回
        return this_bubble
    def parser(self,script:str) -> dict:
        # 分割小节
        stdin_text = script.split('\n')
        # 结构体
        struct = {}
        # 逐句读取小节
        for i,text in enumerate(stdin_text):
            # 本行的结构体
            this_section = {}
            # 空白行
            if text == '':
                this_section['type'] = 'blank'
            # 注释行 格式： # word
            elif text[0] == '#':
                this_section['type'] = 'comment'
                this_section['content'] = text[1:]
            # 对话行 格式： [角色1,角色2(30).happy]<replace=30>:巴拉#巴拉#巴拉<w2w=1>
            elif (text[0] == '[') & (']' in text):
                # 类型
                this_section['type'] = 'dialog'
                # 拆分为：[角色框]、<效果>、:文本、<文本效果>、{音效}
                try:
                    cr,cre,ts,tse,se = RE_dialogue.findall(text)[0]
                except IndexError:
                    raise ParserError('UnableDial')
                # [角色框]
                this_section['charactor_set'] = self.charactor_parser(cr=cr,i=1)
                # <效果>
                this_section['ab_method'] =  self.method_parser(cre)
                # :文本
                this_section['content'] = ts
                # <文本效果>
                this_section['tx_method'] = self.method_parser(tse)
                # {音效}
                this_section['sound_set'] = self.sound_parser(sound=se,i=i)
            # 背景设置行，格式： <background><black=30>:BG_obj
            elif text[0:12] == '<background>':
                # 解析
                try:
                    obj_type,obje,objc = RE_placeobj.findall(text)[0]
                    # 类型
                    this_section['type'] = obj_type
                except IndexError:
                    raise ParserError('UnableParse',str(i+1))
                # <效果>
                this_section['bg_method'] = self.method_parser(obje)
                # 对象
                this_section['object'] = objc
            # 常驻立绘设置行，格式：<animation><black=30>:(Am_obj,Am_obj2)
            elif text[0:11] == '<animation>':
                # 解析
                try:
                    obj_type,obje,objc = RE_placeobj.findall(text)[0]
                    # 类型
                    this_section['type'] = obj_type
                except IndexError:
                    raise ParserError('UnableParse',str(i+1))
                # <效果>
                this_section['am_method'] = self.method_parser(obje)
                # 对象
                if objc == 'NA' or objc == 'None':
                    this_section['object'] = None
                elif (objc[0] == '(') and (objc[-1] == ')'):
                    # 如果是一个集合
                    this_GA_set = {} # GA
                    animation_list = objc[1:-1].split(',')
                    for k,am in enumerate(animation_list):
                        this_GA_set[str(k)] = am
                    this_section['object'] = this_GA_set
                else:
                    this_section['object'] = objc
            # 常驻气泡设置行，格式：<bubble><black=30>:Bubble_obj("Header_text","Main_text",<text_method>)
            elif text[0:8] == '<bubble>':
                # 解析
                try:
                    obj_type,obje,objc = RE_placeobj.findall(text)[0]
                    # 类型
                    this_section['type'] = obj_type
                except IndexError:
                    raise ParserError('UnableParse',str(i+1))
                # <效果>
                this_section['bb_method'] = self.method_parser(obje)
                # 对象
                if objc == 'NA' or objc == 'None':
                    this_section['object'] = None
                elif '(' not in objc and objc[-1] != ')':
                    # 如果是一个纯对象
                    this_section['object'] = objc
                else:
                    # 如果是一个Bubble表达式
                    this_section['object'] = self.bubble_parser(bubble_exp=objc,i=i)
            # 参数设置行，格式：<set:speech_speed>:220
            elif (text[0:5] == '<set:') & ('>:' in text):
                try:
                    set_type,target,args = RE_setting.findall(text)[0]
                except IndexError:
                    raise ParserError('UnableParse',str(i+1))
                # 类型
                this_section['type'] = set_type
                this_section['target'] = target
                # 类型1：整数型
                if target in ['am_dur_default','bb_dur_default','bg_dur_default','tx_dur_default','speech_speed','asterisk_pause','secondary_alpha']:
                    this_section['value_type'] = 'digit' # natural number
                    try:
                        this_section['value'] = int(args)
                    except:
                        print(WarningPrint('Set2Invalid',target,args))
                        this_section['value'] = args
                # 类型2：method
                elif target in ['am_method_default','bb_method_default','bg_method_default','tx_method_default']:
                    this_section['value_type'] = 'method'
                    try:
                        this_section['value'] = self.method_parser(args)
                    except IndexError:
                        raise ParserError('SetInvMet',target,args)
                # 类型3：BGM 禁用
                # elif target == 'BGM':
                #     this_section['value_type'] = 'music'
                #     this_section['value'] = args
                # 类型4：函数
                elif target == 'formula':
                    this_section['value_type'] = 'function'
                    if args in formula_available.keys() or args[0:6] == 'lambda':
                        this_section['value'] = args
                    else:
                        raise ParserError('UnspFormula',args,str(i+1))
                # 类型5：枚举
                elif target == 'inline_method_apply':
                    this_section['value_type'] = 'enumerate'
                    this_section['value'] = args
                # 否则无法解析
                else:
                    raise ParserError('UnsuppSet',target,str(i+1))
            # 位置重设行，格式：<move:FreePos_obj>:NewPos
            elif (text[0:6] == '<move:') & ('>:' in text):
                try:
                    set_type,target,args = RE_setting.findall(text)[0]
                    expression:tuple = RE_pos_exp.findall(args)[0]
                except IndexError:
                    raise ParserError('UnableParse',str(i+1))
                # 目标
                pos_exp = {}
                pos_exp['pos1'] = MediaDef().value_parser(expression[0])
                if expression[1] == '':
                    # 单纯赋值
                    pos_exp['operator'] = None
                    pos_exp['pos2'] = None
                else:
                    # 加减运算
                    pos_exp['operator'] = expression[2]
                    pos_exp['pos2'] = MediaDef().value_parser(expression[3])
                # 类型
                this_section['type'] = set_type
                this_section['target'] = target
                this_section['value'] = pos_exp
            # 表格赋值行，格式：<table:Name.Subtype.Column>
            elif (text[0:7] == '<table:') & ('>:' in text):
                try:
                    set_type,target,args = RE_setting.findall(text)[0]
                except IndexError:
                    raise ParserError('UnableParse',str(i+1))
                this_target = {}
                target_split = target.split('.')
                if len(target_split) == 2:
                    this_target['name'],this_target['column'] = target_split
                    this_target['subtype'] = None
                elif len(target_split) == 3:
                    this_target['name'],this_target['subtype'],this_target['column'] = target_split
                # 如果超过4个指定项目，无法解析，抛出ParserError(不被支持的参数)
                else:
                    raise ParserError('UnsuppSet',target,str(i+1))
                this_section['type'] = set_type
                this_section['target'] = this_target
                this_section['value'] = args
            # BGM 行，格式：<BGM>:
            elif text[0:6] in ['<BGM>:','<bgm>:']:
                this_section['type'] = 'music'
                this_section['value'] = text[6:]
            # 清除行，仅适用于ChatWindow
            elif (text[0:8] == '<clear>:'):
                this_section['type'] = 'clear'
                this_section['object'] = text[8:]
            # 预设动画，损失生命
            elif text[0:11] == '<hitpoint>:':
                this_section['type'] = 'hitpoint'
                name_tx,heart_max,heart_begin,heart_end = RE_hitpoint.findall(text)[0]
                this_section['content'] = name_tx
                try:
                    this_section['hp_max'] = int(heart_max)
                    this_section['hp_begin'] = int(heart_begin)
                    this_section['hp_end'] = int(heart_end)
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrHit',str(i+1))
            # 预设动画，骰子
            elif text[0:7] == '<dice>:':
                this_section['type'] = 'dice'
                dice_args = RE_dice.findall(text[7:])
                if len(dice_args) == 0:
                    raise ParserError('NoDice')
                else:
                    try:
                        this_dice_set = {}
                        for k,dice in enumerate(dice_args):
                            this_dice = {}
                            tx,dicemax,check,face = dice
                            this_dice['content'] = tx
                            this_dice['dicemax'] = int(dicemax)
                            this_dice['face'] = int(face)
                            if check == 'NA':
                                this_dice['check'] = None
                            else:
                                this_dice['check'] = int(check)
                            this_dice_set[str(k)] = this_dice
                        this_section['dice_set'] = this_dice_set
                    except Exception as E:
                        print(E)
                        raise ParserError('ParErrDice',str(i+1))
            # 等待行，停留在上一个小节的结束状态，不影响S图层
            elif text[0:7] == '<wait>:':
                this_section['type'] = 'wait'
                try:
                    this_section['time'] = int(RE_wait.findall(text)[0])
                except Exception as E:
                    raise ParserError('InvWaitArg',E)
            # 异常行，报出异常
            else:
                raise ParserError('UnrecLine',str(i+1))
            struct[str(i)] = this_section
        # 返回值
        return struct
    # struct -> RGL
    def method_export(self,method_obj:dict)->str:
        if method_obj['method'] == 'default':
            return ''
        else:
            if method_obj['method_dur'] == 'default':
                return '<'+ method_obj['method'] +'>'
            else:
                return '<'+ method_obj['method'] + '=' + str(method_obj['method_dur']) +'>'
    def sound_export(self,sound_obj_set:dict)->str:
        sound_script_list = []
        for key in sound_obj_set.keys():
            sound_obj = sound_obj_set[key]
            if key == '*': # {sound;*50}
                sound_script_list.append('{' + sound_obj['sound'] + ';*' + str(sound_obj['time']) + '}')
            elif key == '{*}':
                if 'specified_speech' in sound_obj.keys(): # {*abc}
                    sound_script_list.append('{*' + str(sound_obj['specified_speech']) + '}')
                elif sound_obj['sound'] is not None: # {sound;*}
                    sound_script_list.append('{' + str(sound_obj['sound']) + ';*}')
                else:
                    sound_script_list.append('{*}') # {*}
            else:
                if sound_obj['delay'] != 0: # {sound;5}
                    sound_script_list.append('{' + str(sound_obj['sound']) +';'+ str(sound_obj['delay']) +'}')
                else: # {sound}
                    sound_script_list.append('{' + str(sound_obj['sound']) + '}')
        return ''.join(sound_script_list)
    def anime_export(self,anime_obj:dict)->str:
        if anime_obj is None:
            OB = 'NA'
        elif type(anime_obj) is str:
            OB =  anime_obj
        else:
            OB = '(' + ','.join(anime_obj.values()) + ')'
        return OB
    def bubble_export(self,bubble_obj:dict)->str:
        if bubble_obj is None:
            OB = 'NA'
        elif type(bubble_obj) is str:
            OB = bubble_obj
        else:
            bubble_object = bubble_obj
            TM = self.method_export(bubble_object['tx_method'])
            OB = '{}("{}","{}"{})'.format(
                bubble_object['bubble'],
                bubble_object['header_text'],
                bubble_object['main_text'],TM)
        return OB
    def move_export(self,pos_value:dict)->str:
        # 重现value
        if pos_value['operator'] is None:
            value = MediaDef().value_export(pos_value['pos1'])
        else:
            pos1 = MediaDef().value_export(pos_value['pos1'])
            pos2 = MediaDef().value_export(pos_value['pos2'])
            value = pos1 + pos_value['operator'] + pos2
        return value
    def dice_export(self,dice_obj:dict)->str:
        list_of_dice_express = []
        for key in dice_obj.keys():
            this_dice = dice_obj[key]
            if this_dice['check'] is None:
                CK = 'NA'
            else:
                CK = int(this_dice['check'])
            list_of_dice_express.append(
                '({},{},{},{})'.format(
                    this_dice['content'],
                    this_dice['dicemax'],
                    CK,
                    this_dice['face']))
        return ','.join(list_of_dice_express)
    def export(self) -> str:
        list_of_scripts = []
        for section_key in self.struct.keys():
            this_section:dict = self.struct[section_key]
            type_this:str = this_section['type']
            # 空行
            if type_this == 'blank':
                this_script = ''
            # 备注
            elif type_this == 'comment':
                this_script = '#' + this_section['content']
            # 对话行
            elif type_this == 'dialog':
                # 角色
                charactor_set:dict = this_section['charactor_set']
                charactor_script_list:list = []
                for key in charactor_set.keys():
                    charactor = charactor_set[key]
                    charactor_script = charactor['name']
                    if charactor['alpha'] is not None:
                        charactor_script = charactor_script + '(%d)'%charactor['alpha']
                    if charactor['subtype'] != 'default':
                        charactor_script = charactor_script + '.' + charactor['subtype']
                    charactor_script_list.append(charactor_script)
                CR = '[' + ','.join(charactor_script_list) + ']'
                # 媒体效果
                MM = self.method_export(this_section['ab_method'])
                TM = self.method_export(this_section['tx_method'])
                SE = self.sound_export(this_section['sound_set'])
                this_script = CR + MM + ':' + this_section['content'] + TM + SE
            # 背景
            elif type_this == 'background':
                MM = self.method_export(this_section['bg_method'])
                this_script = '<background>' + MM + ':' + this_section['object']
            # 立绘
            elif type_this == 'animation':
                MM = self.method_export(this_section['am_method'])
                OB = self.anime_export(this_section['object'])
                this_script = '<animation>' + MM + ':' + OB
            # 气泡
            elif type_this == 'bubble':
                MM = self.method_export(this_section['bb_method'])
                OB = self.bubble_export(this_section['object'])
                this_script = '<bubble>' + MM + ':' + OB
            # 设置
            elif type_this == 'set':
                if this_section['value_type'] == 'digit':
                    value = str(this_section['value'])
                elif this_section['value_type'] in ['function','enumerate']:
                    value = this_section['value']
                elif this_section['value_type'] == 'method':
                    value = self.method_export(this_section['value'])
                else:
                    continue
                target = this_section['target']
                this_script = '<set:{}>:{}'.format(target,value)
            # 移动
            elif type_this == 'move':
                target = this_section['target']
                # 重现value
                value = self.move_export(this_section['value'])
                this_script = '<move:{}>:{}'.format(target,value)
            # 表格
            elif type_this == 'table':
                value = this_section['value']
                if this_section['target']['subtype'] is None:
                    target = this_section['target']['name'] +'.'+ this_section['target']['column']
                else:
                    target = this_section['target']['name'] +'.'+ this_section['target']['subtype'] +'.'+ this_section['target']['column']
                this_script = '<table:{}>:{}'.format(target,value)
            # 音乐
            elif type_this == 'music':
                value = this_section['value']
                this_script = '<bgm>:{}'.format(value)
            # 清除
            elif type_this == 'clear':
                this_script = '<clear>:' + this_section['object']
            # 生命值
            elif type_this == 'hitpoint':
                this_script = '<hitpoint>:({},{},{},{})'.format(
                    this_section['content'],
                    this_section['hp_max'],
                    this_section['hp_begin'],
                    this_section['hp_end']
                )
            # 骰子
            elif type_this == 'dice':
                this_script = '<dice>:' + self.dice_export(this_section['dice_set'])
            # 停留
            elif type_this == 'wait':
                this_script = '<wait>:{}'.format(this_section['time'])
            else:
                this_script = ''
            # 添加到列表
            list_of_scripts.append(this_script)
        # 返回
        return '\n'.join(list_of_scripts)
    # 执行解析 -> (timeline:pd.DF,breakpoint:pd.Ser,builtin_media:dict?<方便在其他模块实例化>
    def tx_method_execute(self,text:str,text_obj:Text,tx_method:dict,line_limit:int,this_duration:int,i=0) -> np.ndarray:
        # content: 不包含richlabel
        content, idxmap = text_obj.raw(text)
        idx_uf = np.frompyfunc(lambda x:idxmap[x],1,1)
        # 
        content_length:int = len(content)
        UF_limit_content_length:np.ufunc = np.frompyfunc(lambda x:int(x) if x<=content_length else content_length,1,1)
        # 检查文字是否合理
        self.check_text_execute(content_text=content,this_line_limit=line_limit,i=i)
        # 检查文字效果时间
        if this_duration < tx_method['method_dur']:
            # 小节持续时间过短，不显示任何文字效果
            print(WarningPrint('TxMetDrop',str(i+1)))
            return idx_uf(content_length*np.ones(this_duration))
        # 全部显示
        if tx_method['method'] == 'all':
            if tx_method['method_dur'] >= this_duration:
                main_text_eff = np.zeros(this_duration)
            else:
                main_text_eff = np.hstack([
                    np.zeros(tx_method['method_dur']),
                    content_length*np.ones(this_duration-tx_method['method_dur'])
                    ])
            return idx_uf(main_text_eff.astype(int))
        # 逐字显示
        elif tx_method['method'] == 'w2w':
            # 在asterisk_pause/2 时间开始显示第一个字
            delay = int(self.dynamic['asterisk_pause']/2)
            delay_timeline = np.zeros(delay,dtype=int)
            w2w_timeline = np.arange(0,this_duration-delay,1)//tx_method['method_dur'] + 1
            return idx_uf(UF_limit_content_length(np.hstack([delay_timeline,w2w_timeline])))
        # 逐行显示
        elif tx_method['method'] == 'l2l':
            if ((content[0]=='^')|('#' in content)): #如果是手动换行的列
                lines = content.split('#')
                wc_list = []
                len_this = 0
                for x,l in enumerate(lines): #x是井号的数量
                    len_this = len_this +len(l)+1 #当前行的长度
                    #print(len_this,len(l),x,ts[0:len_this])
                    wc_list.append(np.ones(tx_method['method_dur']*len(l))*len_this)
                try:
                    wc_list.append(np.ones(this_duration - (len(content)-x)*tx_method['method_dur'])*len(content)) #this_duration > est # 1.6.1 update
                    word_count_timeline = np.hstack(wc_list)
                except Exception: 
                    word_count_timeline = np.hstack(wc_list) # this_duration < est
                    word_count_timeline = word_count_timeline[0:this_duration]
                return idx_uf(UF_limit_content_length(word_count_timeline).astype(int))
            else:
                return idx_uf(UF_limit_content_length((np.arange(0,this_duration,1)//(tx_method['method_dur']*line_limit)+1)*line_limit))
        # 逐句显示
        elif tx_method['method'] == 's2s':
            # TODO
            pass
        # 聊天窗滚动
        elif tx_method['method'] == 'run':
            # return [-1 ~ -0<因为不能是0，所以用-1e-10替代>]，仅在ChatWindows中是有效的，其余等价于 <all=0>
            return np.hstack([
                self.dynamic['formula'](-1,-1e-10,tx_method['method_dur']),
                np.ones(this_duration-tx_method['method_dur']) * content_length
                ])
        else:
            raise ParserError('UnrecTxMet', self.method_export(tx_method), str(i+1))
    def cross_timeline_execute(self,timeline:pd.DataFrame,method:MotionMethod,begin:int,center:int,end:int,layer:str)->np.ndarray:
        # 交叉溶解的时间轴生成 
        dur = center - begin
        last = timeline.loc[begin:center-1,layer].values
        last = np.hstack([last,np.repeat(last[-1],dur)])
        this = timeline.loc[center:end-1,layer].values
        this = np.hstack([np.repeat(this[0],dur),this])
        return method.cross_mark(this,last)
    def place_bubble_execute(self,this_placed_bubble:tuple,last_section:int,this_section:int)->None:
        if self.break_point[last_section] == self.break_point[this_section]:
            # 如果持续时间是0，直接略过
            return
        # 处理上一次的
        last_placed_index = range(self.break_point[last_section],self.break_point[this_section])
        this_duration = len(last_placed_index)
        this_bb,bb_method,bb_dur,this_hd,this_tx,text_method,text_dur,bb_center = this_placed_bubble
        # 如果place的this_duration小于切换时间，则清除动态切换效果
        if (this_duration<(2*bb_dur+1)) & (this_bb != 'NA'):
            print(WarningPrint('PBbMetDrop'))
            bb_dur = 0
            bb_method = 'replace'
        # 立绘的对象
        self.main_timeline.loc[last_placed_index,'BbS'] = this_bb
        if this_bb=='NA':
            # this_bb 可能为空的，需要先处理这种情况！
            self.main_timeline.loc[last_placed_index,'BbS_main'] = ''
            self.main_timeline.loc[last_placed_index,'BbS_main_e'] = 0
            self.main_timeline.loc[last_placed_index,'BbS_header'] = ''
            self.main_timeline.loc[last_placed_index,'BbS_a'] = 0
            self.main_timeline.loc[last_placed_index,'BbS_c'] = 'NA'
            self.main_timeline.loc[last_placed_index,'BbS_p'] = 'NA'
        else:
            bb_method_obj = MotionMethod(bb_method,bb_dur,self.dynamic['formula'],this_section)
            self.main_timeline.loc[last_placed_index,'BbS_a'] = bb_method_obj.alpha(this_duration,100)
            self.main_timeline.loc[last_placed_index,'BbS_c'] = bb_center
            self.main_timeline.loc[last_placed_index,'BbS_p'] = bb_method_obj.motion(this_duration)
            self.main_timeline.loc[last_placed_index,'BbS_header'] = this_hd
            self.main_timeline.loc[last_placed_index,'BbS_main'] = this_tx
            # 如果是放置正常的气泡
            if type(self.medias[this_bb]) in [Bubble,Balloon,DynamicBubble]:
                maintext_this = self.medias[this_bb].MainText
                line_limit_this = maintext_this.line_limit
            # 如果是放置一个的聊天窗
            elif type(self.medias[this_bb]) is ChatWindow:
                keyword_this = this_hd.split('|')[-1].split('#')[0]
                maintext_this = self.medias[this_bb].sub_Bubble[keyword_this].MainText
                line_limit_this = maintext_this.line_limit
            # 切换效果
            self.main_timeline.loc[last_placed_index,'BbS_main_e'] = self.tx_method_execute(
                text=this_tx,
                text_obj=maintext_this,
                tx_method={'method':text_method,'method_dur':text_dur},
                line_limit=line_limit_this,
                this_duration=this_duration,
                i=last_section)
    def place_anime_execute(self,this_placed_anime:tuple,last_section:int,this_section:int)->None:
        if self.break_point[last_section] == self.break_point[this_section]:
            # 如果持续时间是0，直接略过
            return
        # 处理上一次的
        last_placed_index = range(self.break_point[last_section],self.break_point[this_section])
        this_duration = len(last_placed_index)
        this_am,am_method,am_dur,am_center = this_placed_anime
        # 如果place的this_duration小于切换时间，则清除动态切换效果
        if (this_duration<(2*am_dur+1)) & (this_am != 'NA'):
            print(WarningPrint('PAmMetDrop'))
            am_dur = 0
            am_method = 'replace'
        # 立绘的对象
        self.main_timeline.loc[last_placed_index,'AmS'] = this_am
        # this_am 可能为空的，需要先处理这种情况！
        if this_am == 'NA':
            self.main_timeline.loc[last_placed_index,'AmS_t'] = 0
            self.main_timeline.loc[last_placed_index,'AmS_a'] = 0
            self.main_timeline.loc[last_placed_index,'AmS_c'] = 'NA'
            self.main_timeline.loc[last_placed_index,'AmS_p'] = 'NA'
        else:
            am_method_obj = MotionMethod(am_method,am_dur,self.dynamic['formula'],this_section)
            self.main_timeline.loc[last_placed_index,'AmS_a'] = am_method_obj.alpha(this_duration,100)
            self.main_timeline.loc[last_placed_index,'AmS_p'] = am_method_obj.motion(this_duration)
            self.main_timeline.loc[last_placed_index,'AmS_t'] = self.medias[this_am].get_tick(this_duration)
            self.main_timeline.loc[last_placed_index,'AmS_c'] = am_center
    def check_text_execute(self,content_text,this_line_limit,i):
        # 未声明手动换行
        if ('#' in content_text)&(content_text[0]!='^'):
            # content_text = '^' + content_text # 补齐申明符号 # 因为和富文本冲突，取消这个功能
            print(WarningPrint('UndeclMB',str(i+1)))
        # 行数过多的警告
        if (len(content_text)>this_line_limit*4) | (len(content_text.split('#'))>4):
            print(WarningPrint('More4line',str(i+1)))
        # 手动换行的字数超限的警告
        if ((content_text[0]=='^')|('#' in content_text))&(np.frompyfunc(len,1,1)(content_text.replace('^','').split('#')).max()>this_line_limit):
            print(WarningPrint('MBExceed',str(i+1)))
    def execute(self,media_define:MediaDef,char_table:CharTable,config:Config)->pd.DataFrame:
        # 媒体和角色 # 浅复制，只复制了对象地址
        self.medias:dict = media_define.Medias.copy()
        self.charactors:pd.DataFrame = char_table.export().copy()
        # section:小节号, BG: 背景，Am：立绘，Bb：气泡，BGM：背景音乐，Voice：语音，SE：音效
        render_arg = [
        'section',
        'BG1','BG1_a','BG1_c','BG1_p','BG2','BG2_a','BG2_c','BG2_p',
        'Am1','Am1_t','Am1_a','Am1_c','Am1_p','Am2','Am2_t','Am2_a','Am2_c','Am2_p','Am3','Am3_t','Am3_a','Am3_c','Am3_p',
        'AmS','AmS_t','AmS_a','AmS_c','AmS_p',
        'Bb','Bb_main','Bb_main_e','Bb_header','Bb_a','Bb_c','Bb_p',
        'BbS','BbS_main','BbS_main_e','BbS_header','BbS_a','BbS_c','BbS_p',
        'BGM','Voice','SE'
        ]
        # 断点文件: index + 1 == section, 因为还要包含尾部，所以总长比section长1
        self.break_point = pd.Series(0,index=range(0,len(self.struct.keys())+1),dtype=int)
        # 视频+音轨 时间轴
        self.main_timeline = pd.DataFrame(dtype=str,columns=render_arg)
        # 更新 self.media
        self.medias['black'] = Background('black')
        self.medias['white'] = Background('white')
        # self.medias.update(bulitin_media.execute())
        # 背景音乐队列
        BGM_queue = []
        # 初始化的背景、放置立绘、放置气泡
        this_background = "black"
        # 放置的立绘
        last_placed_animation_section = 0
        this_placed_animation = ('NA','replace',0,'NA') # am,method,method_dur,center
        # 放置的气泡
        last_placed_bubble_section = 0
        this_placed_bubble = ('NA','replace',0,'','','all',0,'NA') # bb,method,method_dur,HT,MT,tx_method,tx_dur,center
        # 当前对话小节的am_bb_method
        last_dialog_method = {'Am':None,'Bb':None,'A1':0,'A2':0,'A3':0}
        this_dialog_method = {'Am':None,'Bb':None,'A1':0,'A2':0,'A3':0}
        # 动态变量
        self.dynamic = {
            #默认切换效果（立绘）
            'am_method_default' : {'method':'replace','method_dur':0},
            #默认切换效果持续时间（立绘）
            'am_dur_default' : 10,
            #默认切换效果（文本框）
            'bb_method_default' : {'method':'replace','method_dur':0},
            #默认切换效果持续时间（文本框）
            'bb_dur_default' : 10,
            #默认切换效果（背景）
            'bg_method_default' : {'method':'replace','method_dur':0},
            #默认切换效果持续时间（背景）
            'bg_dur_default' : 10,
            #默认文本展示方式
            'tx_method_default' : {'method':'all','method_dur':0},
            #默认单字展示时间参数
            'tx_dur_default' : 5,
            #语速，单位word per minute
            'speech_speed' : 220,
            #默认的曲线函数
            'formula' : linear,
            # 星标音频的句间间隔 a1.4.3，单位是帧，通过处理delay
            'asterisk_pause' : 20,
            # a 1.8.8 次要立绘的默认透明度
            'secondary_alpha' : 60,
            # 对话行内指定的方法的应用对象：animation、bubble、both、none
            'inline_method_apply' : 'both'
        }

        # 开始遍历
        for key in self.struct.keys():
            # 保留前一行的切换效果参数，重置当前行的参数
            last_dialog_method = this_dialog_method
            this_dialog_method = {'Am':None,'Bb':None,'A1':0,'A2':0,'A3':0}
            # 本小节：
            i = int(key)
            this_section = self.struct[key]
            # 空白行
            if this_section['type'] == 'blank':
                self.break_point[i+1]=self.break_point[i]
                continue
            # 注释行
            elif this_section['type'] == 'comment':
                self.break_point[i+1]=self.break_point[i]
                continue
            # 对话行
            elif this_section['type'] == 'dialog':
                try:
                    # 这个小节的持续时长
                    if '*' in this_section['sound_set'].keys():
                        # 如果存在星标音效：持续时长 = 星标间隔 + ceil(秒数时间*帧率)
                        this_duration:int = self.dynamic['asterisk_pause'] + np.ceil(this_section['sound_set']['*']['time'] * config.frame_rate).astype(int)
                    elif '{*}' in this_section['sound_set'].keys():
                        # 如果存在待处理星标：举起伊可
                        raise ParserError('UnpreAster', str(i+1))
                    else:
                        # 如果缺省星标：持续时间 = 字数/语速 + 星标间隔
                        this_duration:int = self.dynamic['asterisk_pause'] + int(len(this_section['content'])/(self.dynamic['speech_speed']/60/config.frame_rate))
                    # 本小节的切换效果：am_method，bb_method
                    if this_section['ab_method']['method'] == 'default' or self.dynamic['inline_method_apply'] == 'none':
                        # 未指定
                        am_method:dict = self.dynamic['am_method_default'].copy()
                        bb_method:dict = self.dynamic['bb_method_default'].copy()
                    else:
                        # 有指定
                        if self.dynamic['inline_method_apply'] in ['animation','both']:
                            am_method:dict = this_section['ab_method'].copy()
                        else:
                            am_method:dict = self.dynamic['am_method_default'].copy()
                        if self.dynamic['inline_method_apply'] in ['bubble','both']:
                            bb_method:dict = this_section['ab_method'].copy()
                        else:
                            bb_method:dict = self.dynamic['bb_method_default'].copy()
                    # 是否缺省时长
                    if am_method['method_dur'] == 'default':
                        am_method['method_dur'] = self.dynamic['am_dur_default']
                    if bb_method['method_dur'] == 'default':
                        bb_method['method_dur'] = self.dynamic['bb_dur_default']
                    # 小节持续时长是否低于切换效果的持续时长？
                    method_dur = max(am_method['method_dur'],bb_method['method_dur'])
                    if this_duration<(2*method_dur+1):
                        this_duration = 2*method_dur+1
                    # 建立本小节的timeline文件
                    this_timeline=pd.DataFrame(index=range(0,this_duration),dtype=str,columns=render_arg)
                    this_timeline['BG2'] = this_background
                    this_timeline['BG2_a'] = 100
                    # 载入切换效果
                    am_method_obj = MotionMethod(am_method['method'],am_method['method_dur'],self.dynamic['formula'],i)
                    bb_method_obj = MotionMethod(bb_method['method'],bb_method['method_dur'],self.dynamic['formula'],i)
                    this_dialog_method['Am'] = am_method_obj
                    this_dialog_method['Bb'] = bb_method_obj
                    # 遍历角色
                    for chara_key in this_section['charactor_set'].keys():
                        this_charactor:dict = this_section['charactor_set'][chara_key]
                        # 获取角色配置
                        name:str = this_charactor['name']
                        subtype:str = this_charactor['subtype']
                        alpha:int = this_charactor['alpha']
                        try:
                            this_charactor_config = self.charactors.loc[name+'.'+subtype]
                        except KeyError as E: # 在角色表里面找不到name，raise在这里！
                            raise ParserError('UndefName',name+'.'+subtype,str(i+1),E)
                        # 立绘：'Am1','Am1_t','Am1_a','Am1_c','Am1_p
                        this_layer:str = 'Am%d' % (int(chara_key) + 1)
                        AN = this_layer.replace('m','')
                        this_am:str = this_charactor_config['Animation']
                        # 立绘的名字
                        this_timeline[this_layer] = this_am
                        if this_am == 'NA':
                            # 如果立绘缺省
                            this_timeline[this_layer+'_t'] = 0
                            this_timeline[this_layer+'_c'] = 'NA'
                            this_timeline[this_layer+'_a'] = 0
                            this_timeline[this_layer+'_p'] = 'NA'
                            this_dialog_method[AN] = 0
                        elif this_am not in self.medias.keys():
                            # 如果媒体名未定义
                            raise ParserError('UndefAnime', this_am, name+'.'+subtype)
                        elif type(self.medias[this_am]) not in [Animation,GroupedAnimation,Dice,HitPoint]:
                            # 如果媒体不是一个立绘类
                            raise ParserError('NotAnime', this_am, name+'.'+subtype)
                        else:
                            # 立绘的对象、帧顺序、中心位置
                            this_am_obj:Animation = self.medias[this_am]
                            this_timeline[this_layer+'_t'] = this_am_obj.get_tick(this_duration)
                            this_timeline[this_layer+'_c'] = str(this_am_obj.pos)
                            # 立绘的透明度
                            if alpha is None:
                                alpha = -1
                            if alpha >= 0 and alpha <= 100:
                                # 如果有指定合法的透明度，则使用指定透明度
                                this_timeline[this_layer+'_a']=am_method_obj.alpha(this_duration,alpha)
                                this_dialog_method[AN] = alpha
                            else:
                                # 如果指定是None（默认），或者其他非法值
                                if chara_key == '0': # 如果是首要角色，透明度为100
                                    this_timeline[this_layer+'_a']=am_method_obj.alpha(this_duration,100)
                                    this_dialog_method[AN] = 100
                                else: # 如果是次要角色，透明度为secondary_alpha，默认值60
                                    this_timeline[this_layer+'_a']=am_method_obj.alpha(this_duration,self.dynamic['secondary_alpha'])
                                    this_dialog_method[AN] = self.dynamic['secondary_alpha']
                            # 立绘的运动
                            this_timeline[this_layer+'_p'] = am_method_obj.motion(this_duration)
                        # 气泡参数: 'Bb','Bb_main','Bb_main_e','Bb_header','Bb_a','Bb_c','Bb_p',
                        if chara_key == '0':
                            # 仅考虑首要角色的气泡
                            this_layer = 'Bb'
                            this_bb_key:str = this_charactor_config['Bubble']
                            # 是否是 ChatWindow:key 的形式？
                            if ':' in this_bb_key:
                                this_bb:str = this_bb_key.split(':')[0]
                            else:
                                this_bb:str = this_bb_key
                            if this_bb == 'NA':
                                # 气泡是否缺省？
                                this_timeline[this_layer] = 'NA'
                                this_timeline[this_layer+'_main'] = ''
                                this_timeline[this_layer+'_main_e'] = 0
                                this_timeline[this_layer+'_header'] = ''
                                this_timeline[this_layer+'_c'] = 'NA'
                                this_timeline[this_layer+'_a'] = 0
                                this_timeline[this_layer+'_p'] = 'NA'
                            elif this_bb not in self.medias.keys():
                                # 如果媒体名未定义
                                raise ParserError('UndefBubble', this_bb, name+'.'+subtype)
                            elif type(self.medias[this_bb]) not in [Bubble,Balloon,DynamicBubble,ChatWindow]:
                                # 如果媒体不是一个气泡类
                                raise ParserError('NotBubble', this_bb, name+'.'+subtype)
                            else:
                                # 气泡的对象
                                this_bb_obj:Bubble = self.medias[this_bb]
                                # 头文本
                                try:
                                    if type(this_bb_obj) is ChatWindow:
                                        # ChatWindow 类：只有一个头文本，头文本不能包含|和#，还需要附上key
                                        if this_bb_key == this_bb:
                                            # 如果聊天窗没有key，在单独使用
                                            raise ParserError('CWUndepend', this_bb)
                                        cw_key = this_bb_key.split(':')[1]
                                        # 获取当前key的子气泡的target，target是角色表的列
                                        try:
                                            targets:str = this_bb_obj.sub_Bubble[cw_key].target
                                        except KeyError:
                                            raise ParserError('InvalidKey', cw_key, this_bb)
                                        # 获取target的文本内容
                                        if ('|' in this_charactor_config[targets]) | ('#' in this_charactor_config[targets]):
                                            # 如果包含了非法字符：| #
                                            raise ParserError('InvSymbpd',name+'.'+subtype)
                                        else:
                                            target_text = cw_key+'#'+this_charactor_config[targets]
                                    elif type(this_bb_obj) is Balloon:
                                        # Balloon 类：有若干个头文本，targets是一个list,用 | 分隔
                                        targets:list = this_bb_obj.target
                                        target_text = '|'.join(this_charactor_config[targets].values)
                                    else: #  type(this_bb_obj) in [Bubble,DynamicBubble]:
                                        # Bubble,DynamicBubble类：只有一个头文本
                                        targets:str = this_bb_obj.target
                                        target_text = this_charactor_config[targets]
                                except KeyError as E:
                                    raise ParserError('TgNotExist', E, this_bb)
                                # 主文本
                                content_text = this_section['content']
                                if type(this_bb_obj) is ChatWindow:
                                    mainText_this = this_bb_obj.sub_Bubble[cw_key].MainText
                                else:
                                    mainText_this = this_bb_obj.MainText
                                if mainText_this is None:
                                    # 气泡如果缺失主文本
                                    raise ParserError('MissMainTx',this_bb)
                                else:
                                    this_line_limit:int = mainText_this.line_limit
                                # 主头文本有非法字符，双引号，反斜杠
                                if ('"' in target_text) | ('\\' in target_text) | ('"' in content_text) | ('\\' in content_text):
                                    raise ParserError('InvSymbqu',str(i+1))
                                # 赋值给当前时间轴的Bb轨道
                                this_timeline['Bb'] = this_bb
                                this_timeline['Bb_a'] = bb_method_obj.alpha(this_duration,100)
                                this_timeline['Bb_p'] = bb_method_obj.motion(this_duration)
                                this_timeline['Bb_c'] = str(this_bb_obj.pos)
                                if type(this_bb_obj) is ChatWindow:
                                    # 如果是聊天窗对象，更新timeline对象，追加历史记录
                                    this_timeline['Bb_header'] = this_bb_obj.UF_add_header_text(target_text)
                                    this_timeline['Bb_main'] = this_bb_obj.UF_add_main_text(content_text)
                                    # 更新bubble对象的历史记录
                                    this_bb_obj.append(content_text,target_text)
                                else:
                                    # 如果是普通气泡，记录下这个小节的历史记录
                                    this_timeline['Bb_main'] = content_text
                                    this_timeline['Bb_header'] = target_text
                                    this_bb_obj.recode(content_text,target_text)
                                # 文字显示效果
                                if this_section['tx_method']['method'] == 'default':
                                    # 未指定
                                    tx_method:dict = self.dynamic['tx_method_default'].copy()
                                else:
                                    # 有指定
                                    tx_method:dict = this_section['tx_method'].copy()
                                # 是否缺省时长
                                if tx_method['method_dur'] == 'default':
                                    tx_method['method_dur'] = self.dynamic['tx_dur_default']
                                # 效果记录
                                this_timeline['Bb_main_e'] = self.tx_method_execute(
                                    text=content_text,
                                    text_obj=mainText_this,
                                    tx_method=tx_method,
                                    line_limit=this_line_limit,
                                    this_duration=this_duration,
                                    i=i)
                    # 音效
                    for sound_key in this_section['sound_set'].keys():
                        this_sound:dict = this_section['sound_set'][sound_key]
                        # 音效时间点
                        if sound_key == '*':
                            # 如果是星标音效
                            delay:int = int(self.dynamic['asterisk_pause']/2)
                        else:
                            # 是一般的音效: 不能超过小节长度
                            delay:int = min(this_sound['delay'],this_duration-1)
                        # 音效对象
                        if this_sound['sound'] in self.medias.keys():
                            # 如果是音效媒体：视为音效
                            this_timeline.loc[delay,'SE'] = this_sound['sound']
                        elif os.path.isfile(this_sound['sound'][1:-1]) == True:
                            # 如果是一个指向文件的路径：视为语音
                            this_timeline.loc[delay,'Voice'] = this_sound['sound']
                        elif this_sound['sound'] in ['NA','']:
                            # 如果音效对象是空值或NA
                            pass
                        else:
                            raise ParserError('SEnotExist', this_sound['sound'], str(i+1))
                    # 背景音乐
                    if BGM_queue != []:
                        #从BGM_queue里取第一个出来
                        this_timeline.loc[0,'BGM'] = BGM_queue.pop(0)
                    # 和主时间轴合并
                    this_timeline['section'] = i
                    self.break_point[i+1]=self.break_point[i]+this_duration
                    this_timeline.index = range(self.break_point[i],self.break_point[i+1])
                    self.main_timeline = pd.concat([self.main_timeline,this_timeline],axis=0)
                    # 交叉溶解检查：立绘的
                    if this_dialog_method['Am'].cross_check(last_dialog_method['Am']):
                        # 如果本小节的Am切换效果和前一小节通过交叉溶解检查
                        this_method_dur = this_dialog_method['Am'].method_dur
                        cross_frame_break = self.break_point[i]
                        cross_frame_begin = self.break_point[i]-this_method_dur
                        cross_frame_end = self.break_point[i]+this_method_dur
                        for k in range(1,4):
                            AK_this = this_dialog_method['A%d'%k]
                            AK_last = last_dialog_method['A%d'%k]
                            if AK_this <=0 or AK_last <=0:
                                continue
                            else:
                                cross_alpha_this = this_dialog_method['Am'].cross_alpha(last_dialog_method['Am'],AK_this,AK_last)
                                cross_motion_this = this_dialog_method['Am'].cross_motion(last_dialog_method['Am'])
                            # 编辑时间轴：Am Am_t Am_c
                            for layer in ['Am%d'%k,'Am%d_t'%k,'Am%d_c'%k]:
                                self.main_timeline.loc[cross_frame_begin:cross_frame_end-1,layer] = self.cross_timeline_execute(
                                    timeline = self.main_timeline,
                                    method = this_dialog_method['Am'],
                                    begin = cross_frame_begin,
                                    center = cross_frame_break,
                                    end = cross_frame_end,
                                    layer = layer
                                )
                            # 编辑时间轴：Am_a，Am_p
                            self.main_timeline.loc[cross_frame_begin:cross_frame_end-1,'Am%d_a'%k] = cross_alpha_this
                            self.main_timeline.loc[cross_frame_begin:cross_frame_end-1,'Am%d_p'%k] = cross_motion_this
                    # 交叉溶解检查：气泡的
                    if this_dialog_method['Bb'].cross_check(last_dialog_method['Bb']) is True:
                        # 气泡
                        this_method_dur = this_dialog_method['Bb'].method_dur
                        cross_frame_break = self.break_point[i]
                        cross_frame_begin = self.break_point[i]-this_method_dur
                        cross_frame_end = self.break_point[i]+this_method_dur
                        # 获取透明度和运动
                        cross_alpha_this = this_dialog_method['Bb'].cross_alpha(last_dialog_method['Bb'])
                        cross_motion_this = this_dialog_method['Bb'].cross_motion(last_dialog_method['Bb'])
                        # 替换到对应时间轴
                        # 'Bb','Bb_main','Bb_header','Bb_a','Bb_c','Bb_p',
                        for layer in ['Bb','Bb_main','Bb_header','Bb_c','Bb_main_e']:
                            self.main_timeline.loc[cross_frame_begin:cross_frame_end-1,layer] = self.cross_timeline_execute(
                                timeline = self.main_timeline,
                                method = this_dialog_method['Bb'],
                                begin = cross_frame_begin,
                                center = cross_frame_break,
                                end = cross_frame_end,
                                layer = layer
                                )
                        # Bb_a
                        self.main_timeline.loc[cross_frame_begin:cross_frame_end-1,'Bb_a'] = cross_alpha_this
                        # Bb_p
                        self.main_timeline.loc[cross_frame_begin:cross_frame_end-1,'Bb_p'] = cross_motion_this
                    continue
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrDial', str(i+1))
            # 背景设置行
            elif this_section['type'] == 'background':
                try:
                    # 对象是否存在
                    this_bg:str = this_section['object']
                    if this_bg not in self.medias.keys():
                        raise ParserError('UndefBackGd',this_bg,str(i+1))
                    elif type(self.medias[this_bg]) is not Background:
                        raise ParserError('NotBackGd',this_bg,str(i+1))
                    else:
                        next_background = this_bg
                    # 背景切换效果
                    if this_section['bg_method']['method'] == 'default':
                        bg_method = self.dynamic['bg_method_default'].copy()
                    else:
                        bg_method = this_section['bg_method'].copy()
                    if bg_method['method_dur'] == 'default':
                        bg_method['method_dur'] = self.dynamic['bg_dur_default']
                    method = bg_method['method']
                    method_dur = bg_method['method_dur']
                    if method=='replace': #replace 改为立刻替换 并持续n秒
                        this_timeline=pd.DataFrame(index=range(0,method_dur),dtype=str,columns=render_arg)
                        this_timeline['BG2']=next_background
                        this_timeline['BG2_a']=100
                        this_timeline['BG2_c']=str(self.medias[next_background].pos)
                    elif method=='delay': # delay 等价于原来的replace，延后n秒，然后替换
                        this_timeline=pd.DataFrame(index=range(0,method_dur),dtype=str,columns=render_arg)
                        this_timeline['BG2']=this_background
                        this_timeline['BG2_a']=100
                        this_timeline['BG2_c']=str(self.medias[this_background].pos)
                    # 'black','white'
                    elif method in ['black','white']:
                        this_timeline=pd.DataFrame(index=range(0,method_dur),dtype=str,columns=render_arg)
                        # 下图层BG2，前半程是旧图层，后半程是新图层，透明度均为100
                        this_timeline.loc[:(method_dur//2),'BG2'] = this_background
                        this_timeline.loc[(method_dur//2):,'BG2'] = next_background
                        this_timeline.loc[:(method_dur//2),'BG2_c']=str(self.medias[this_background].pos)
                        this_timeline.loc[(method_dur//2):,'BG2_c']=str(self.medias[next_background].pos)
                        this_timeline['BG2_a'] = 100
                        # 上图层BG1，是指定的颜色，透明度是100-abs(formula(100,-100,dur))
                        this_timeline['BG1'] = method
                        this_timeline['BG1_c']='(0,0)'
                        this_timeline['BG1_a']=100-np.abs(self.dynamic['formula'](-100,100,method_dur))
                        pass
                    elif method in ['cross','push','cover']: # 交叉溶解，黑场，白场，推，覆盖
                        this_timeline=pd.DataFrame(index=range(0,method_dur),dtype=str,columns=render_arg)
                        this_timeline['BG1']=next_background
                        this_timeline['BG1_c']=str(self.medias[next_background].pos)
                        this_timeline['BG2']=this_background
                        this_timeline['BG2_c']=str(self.medias[this_background].pos)
                        if method == 'cross':
                            this_timeline['BG1_a']=self.dynamic['formula'](0,100,method_dur)
                            this_timeline['BG2_a']=100
                        elif method in ['push','cover']:
                            this_timeline['BG1_a']=100
                            this_timeline['BG2_a']=100
                            if method == 'push': # 新背景从右侧把旧背景推出去
                                this_timeline['BG1_p'] = concat_xy(self.dynamic['formula'](config.Width,0,method_dur),np.zeros(method_dur))
                                this_timeline['BG2_p'] = concat_xy(self.dynamic['formula'](0,-config.Width,method_dur),np.zeros(method_dur))
                            else: #cover 新背景从右侧进来叠在原图上面
                                this_timeline['BG1_p'] = concat_xy(self.dynamic['formula'](config.Width,0,method_dur),np.zeros(method_dur))
                                this_timeline['BG2_p'] = 'NA'
                    else:
                        raise ParserError('SwitchBkGd',method,str(i+1))
                    this_background = next_background #正式切换背景
                    # BGM
                    if BGM_queue != []:
                        this_timeline.loc[0,'BGM'] = BGM_queue.pop(0)
                    # 时间轴延长
                    this_timeline['section'] = i
                    self.break_point[i+1]=self.break_point[i]+len(this_timeline.index)
                    this_timeline.index = range(self.break_point[i],self.break_point[i+1])
                    self.main_timeline = pd.concat([self.main_timeline,this_timeline],axis=0)
                    continue
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrBkGd',str(i+1))
            # 放置立绘行
            elif this_section['type'] == 'animation':
                # 前一次的
                self.place_anime_execute(this_placed_anime=this_placed_animation,this_section=i,last_section=last_placed_animation_section)
                # 处理本次的
                try:
                    # 处理默认值
                    am_method:dict = this_section['am_method'].copy()
                    if am_method['method'] == 'default':
                        am_method:dict = self.dynamic['am_method_default'].copy()
                    if am_method['method_dur'] == 'default':
                        am_method['method_dur'] = self.dynamic['am_dur_default']
                    method = am_method['method']
                    method_dur = am_method['method_dur']
                    # 如果是多个立绘
                    if type(this_section['object']) is dict:
                        anime_objs = []
                        anime_poses = []
                        # 检查是否是立绘对象
                        for idx in this_section['object'].keys():
                            am_name = this_section['object'][idx]
                            if am_name not in self.medias.keys():
                                raise ParserError('UndefPAnime',am_name,str(i+1))
                            elif type(self.medias[am_name]) not in [Animation,Dice,HitPoint,GroupedAnimation]:
                                raise ParserError('NotPAnime',am_name,str(i+1))
                            else:
                                anime_objs.append(self.medias[am_name])
                                anime_poses.append(self.medias[am_name].pos)
                        # 生成组合立绘
                        Auto_media_name = 'BIA_'+str(i+1)
                        self.medias[Auto_media_name] = GroupedAnimation(subanimation_list=anime_objs,subanimation_current_pos=anime_poses)
                        # 标记为下一次
                        this_placed_animation = (Auto_media_name,method,method_dur,'(0,0)') # 因为place的应用是落后于设置的，因此需要保留c参数！
                        last_placed_animation_section = i
                    # 如果是单个立绘
                    elif this_section['object'] in self.medias.keys():
                        am_name = this_section['object']
                        if type(self.medias[am_name]) not in [Animation,Dice,HitPoint,GroupedAnimation]:
                            raise ParserError('NotPAnime',am_name,str(i+1))
                        else: # 如果type 不是 Animation 类，也 UndefPAnime
                            this_placed_animation = (am_name,method,method_dur,str(self.medias[am_name].pos))
                            last_placed_animation_section = i
                    # 如果是取消立绘
                    elif this_section['object'] is None:
                        this_placed_animation = ('NA','replace',0,'(0,0)')
                        last_placed_animation_section = i
                    else:
                        raise ParserError('UndefPAnime',this_section['object'],str(i+1))
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrAnime',str(i+1))
            # 放置气泡行
            elif this_section['type'] == 'bubble':
                # 处理上一次的
                self.place_bubble_execute(this_placed_bubble=this_placed_bubble,last_section=last_placed_bubble_section,this_section=i)
                # 获取本次的
                try:
                    # 处理默认值
                    bb_method:dict = this_section['bb_method'].copy()
                    if bb_method['method'] == 'default':
                        bb_method:dict = self.dynamic['bb_method_default'].copy()
                    if bb_method['method_dur'] == 'default':
                        bb_method['method_dur'] = self.dynamic['bb_dur_default']
                    # 如果是设置为NA
                    bb_target = this_section['object']
                    if bb_target is None:
                        this_placed_bubble = ('NA','replace',0,'','','all',0,'NA')
                        last_placed_bubble_section = i
                        # 提前终止所必须的
                        self.break_point[i+1]=self.break_point[i]
                        continue
                    elif type(bb_target) is str:
                        bb_target_name = bb_target
                    else:
                        bb_target_name = bb_target['bubble']
                    # 检查放置气泡类型
                    if bb_target_name not in self.medias.keys():
                        raise ParserError('UndefPBb',bb_target_name,str(i+1))
                    elif type(self.medias[bb_target_name]) not in [Bubble,Balloon,DynamicBubble,ChatWindow]:
                        raise ParserError("NotPBubble",bb_target_name,str(i+1))
                    else:
                        bb_object:Bubble = self.medias[bb_target_name]
                    # 如果是纯气泡显示这个Bubble前一次的记录
                    if type(bb_target) is str:
                        this_placed_bubble = (
                            bb_target_name,
                            bb_method['method'],
                            bb_method['method_dur'],
                            bb_object.header_text,
                            bb_object.main_text,
                            'all', # method
                            0, # method_dur
                            str(bb_object.pos)
                            )
                        last_placed_bubble_section = i
                    # 正常的放置气泡
                    else:
                        # 检查，tx_method 的合法性
                        tx_method = bb_target['tx_method'].copy()
                        if tx_method['method'] == 'default':
                            tx_method = self.dynamic['tx_method_default'].copy()
                        if tx_method['method_dur'] == 'default':
                            tx_method['method_dur'] = self.dynamic['tx_dur_default']
                        # 如果是非法的
                        if tx_method['method'] not in ['all','w2w','s2s','l2l','run']:
                            raise ParserError('UnrecPBbTxM',tx_method['method'],str(i+1))
                        else:
                            # 如果类型是聊天窗
                            if type(bb_object) is ChatWindow:
                                bb_object.append(bb_target['main_text'],bb_target['header_text'])
                            else:
                                bb_object.recode(bb_target['main_text'],bb_target['header_text'])
                            # append 或者 recode 之后，bb_object.header_text 正是我们需要的值
                            this_placed_bubble = (
                                bb_target['bubble'],
                                bb_method['method'],
                                bb_method['method_dur'],
                                bb_object.header_text,
                                bb_object.main_text,
                                tx_method['method'],
                                tx_method['method_dur'],
                                str(bb_object.pos)
                                )
                            last_placed_bubble_section = i
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrBb',str(i+1))
            # 动态设置行
            elif this_section['type'] == 'set':
                try:
                    # 类型1：整数型
                    if this_section['value_type'] == 'digit':
                        self.dynamic[this_section['target']] = this_section['value']
                    # 类型2：method
                    elif this_section['value_type'] == 'method':
                        self.dynamic[this_section['target']] = this_section['value']
                    # 类型3：BGM
                    # elif this_section['value_type'] == 'music':
                    # 类型4：函数
                    elif this_section['value_type'] == 'function':
                        if this_section['value'] in formula_available.keys():
                            self.dynamic['formula'] = formula_available[this_section['value']]
                        elif this_section['value'][0:6] == 'lambda':
                            try:
                                self.dynamic['formula'] = eval(this_section['value'])
                                print(WarningPrint('UseLambda',str(self.dynamic['formula'](0,1,2)),str(i+1)))                          
                            except Exception:
                                raise ParserError('UnspFormula',this_section['value'],str(i+1))
                        else:
                            raise ParserError('UnspFormula',this_section['value'],str(i+1))
                    # 类型5：枚举
                    elif this_section['value_type'] == 'enumerate':
                        if this_section['value'] in ['animation','bubble','both','none']:
                            self.dynamic[this_section['target']] = this_section['value']
                        else:
                            print(WarningPrint('Set2Invalid',this_section['target'],this_section['value']))
                    # 类型6：角色表
                    # elif this_section['value_type'] == 'chartab':
                    # 类型7：不被支持的参数
                    else:
                        raise ParserError('UnsuppSet',this_section['target'],str(i+1))
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrSet',str(i+1))
            # 移动位置行
            elif this_section['type'] == 'move':
                try:
                    target = this_section['target']
                    value = this_section['value']
                    # 获取value对象
                    try:
                        if value['operator'] is None:
                            value_pos = media_define.value_execute(value['pos1'])
                        else:
                            pos1 = media_define.value_execute(value['pos1'])
                            pos2 = media_define.value_execute(value['pos2'])
                            if value['operator'] == '+':
                                value_pos = pos1 + pos2
                            else:
                                value_pos = pos1 - pos2
                        # 检查是否是一个Pos对象
                        if type(value_pos) in [Pos,FreePos]:
                            pass
                        elif type(value_pos) in [list,tuple]:
                            value_pos = Pos(*value_pos)
                        else:
                            raise ValueError('Invalid value type: {}'.format(type(value_pos)))
                    except Exception as E:
                        raise ParserError('IvSyFrPos',target,E)
                    # 检查target的类型
                    if target not in self.medias.keys():
                        raise ParserError('UndefMvObj',target)
                    elif type(self.medias[target]) is FreePos:
                        # 自由位置对象
                        self.medias[target].set(value_pos)
                    elif type(self.medias[target]) in [Animation,Bubble,Balloon,DynamicBubble,Balloon,ChatWindow]:
                        # 如果是图形类媒体
                        self.medias[target].pos = value_pos
                    else:
                        raise ParserError('CannotMvObj',target)
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrMv')
            # 角色表格行
            elif this_section['type'] == 'table':
                try:
                    name = this_section['target']['name']
                    subtype = this_section['target']['subtype']
                    column = this_section['target']['column']
                    if column not in self.charactors.columns:
                        # 如果目标列不存在于角色表
                        raise ParserError('ModUndefCol',column)
                    elif column in ['Name','Subtype','Animation','Bubble','Voice','SpeechRate','PitchRate']:
                        # 如果尝试修改受保护的列
                        raise ParserError('ModProtcCol',column)
                    elif name not in self.charactors['Name'].values:
                        # 如果角色名不存在
                        raise ParserError('UndefTgName',name,str(i+1))
                    if subtype != None:
                        # 如果指定了差分，改动差分
                        if name + '.' + subtype not in self.charactors.index:
                            # 如果指定了差分名，但是差分名不存在
                            raise ParserError('UndefTgSubt',name+'.'+subtype,str(i+1))
                        else:
                            try:
                                self.charactors.loc[name+'.'+subtype,column] = this_section['value']
                            except Exception as E:
                                raise ParserError('ModCTError','.'.join([name,subtype,column]),E)
                    else:
                        # 如果没指定差分，改动整个角色
                        try:
                            self.charactors.loc[self.charactors['Name']==name,column] = this_section['value']
                        except Exception as E:
                            raise ParserError('ModCTError','.'.join([name,column]),E)
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrTab',str(i+1))
                pass
            # 背景音乐行
            elif this_section['type'] == 'music':
                try:
                    if this_section['value'] in self.medias.keys():
                        if type(self.medias[this_section['value']]) is not BGM:
                            raise ParserError("NotBGM",this_section['value'],str(i+1))
                        else:
                            BGM_queue.append(this_section['value'])
                    elif os.path.isfile(this_section['value'][1:-1]):
                        BGM_queue.append(this_section['value'])
                    elif this_section['value'] == 'stop':
                        BGM_queue.append(this_section['value'])
                    else:
                        raise ParserError('UndefBGM',this_section['value'],str(i+1))
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrBGM',str(i+1))
            # 清除聊天窗
            elif this_section['type'] == 'clear':
                if this_section['object'] not in self.medias.keys():
                    print(WarningPrint('ClearUndef',this_section['object']))
                elif type(self.medias[this_section['object']]) is not ChatWindow:
                    print(WarningPrint('ClearNotCW',this_section['object']))
                else:
                    self.medias[this_section['object']].clear()
            # 生命值动画
            elif this_section['type'] == 'hitpoint':
                frame_rate = config.frame_rate
                try:
                    this_timeline=pd.DataFrame(index=range(0,frame_rate*4),dtype=str,columns=render_arg)
                    # 背景
                    alpha_timeline = np.hstack([self.dynamic['formula'](0,1,frame_rate//2),np.ones(frame_rate*3-frame_rate//2),self.dynamic['formula'](1,0,frame_rate)])
                    this_timeline['BG1'] = 'black' # 黑色背景
                    this_timeline['BG1_a'] = alpha_timeline * 80
                    this_timeline['BG2'] = this_background
                    this_timeline['BG2_a'] = 100
                    # 新建内建动画
                    Auto_media_name = 'BIA_'+str(i+1)
                    for layer in range(0,3):
                        # 在媒体列表中添加内建媒体
                        self.medias[Auto_media_name+'_'+str(layer)] = HitPoint(
                            describe   = this_section['content'],
                            heart_max  = this_section['hp_max'],
                            heart_begin= this_section['hp_begin'],
                            heart_end  = this_section['hp_end'],
                            layer= layer
                            )
                    # 动画参数
                    # 灰色框
                    this_timeline['Am3'] = Auto_media_name+'_0'
                    this_timeline['Am3_a'] = alpha_timeline * 100
                    this_timeline['Am3_t'] = 0
                    this_timeline['Am3_c'] = 'NA'
                    this_timeline['Am3_p'] = 'NA'
                    # 留下的血
                    this_timeline['Am2'] = Auto_media_name+'_1'
                    this_timeline['Am2_a'] = alpha_timeline * 100
                    this_timeline['Am2_t'] = 0
                    this_timeline['Am2_c'] = 'NA'
                    this_timeline['Am2_p'] = 'NA'
                    # 丢掉的血
                    this_timeline['Am1'] = Auto_media_name+'_2'
                    this_timeline['Am1_c'] = 'NA'
                    if this_section['hp_begin'] > this_section['hp_end']:
                        # 掉血模式
                        this_timeline['Am1_a'] = np.hstack([self.dynamic['formula'](0,100,frame_rate//2),
                                                            np.ones(frame_rate*2-frame_rate//2)*100,
                                                            left(100,0,frame_rate//2),
                                                            np.zeros(frame_rate*2-frame_rate//2)]) #0-0.5出现，2-2.5消失
                        this_timeline['Am1_p'] = concat_xy(np.zeros(frame_rate*4),
                                                           np.hstack([np.zeros(frame_rate*2), # 静止2秒
                                                           left(0,-int(config.Height*0.3),frame_rate//2), # 半秒切走
                                                           int(config.Height*0.3)*np.ones(frame_rate*2-frame_rate//2)])) #1.5秒停止
                        this_timeline['Am1_t'] = 0
                    else:
                        # 回血模式
                        this_timeline['Am1_a'] = alpha_timeline * 100 # 跟随全局血量
                        this_timeline['Am1_p'] = 'NA' # 不移动
                        this_timeline['Am1_t'] = np.hstack([np.zeros(frame_rate*1), # 第一秒静止
                                                            np.arange(0,frame_rate,1), # 第二秒播放
                                                            np.ones(frame_rate*2)*(frame_rate-1)]) # 后两秒静止
                    # BGM
                    if BGM_queue != []:
                        this_timeline.loc[0,'BGM'] = BGM_queue.pop(0) #从BGM_queue里取出来一个
                    # 时间轴延长
                    this_timeline['section'] = i
                    self.break_point[i+1]=self.break_point[i]+len(this_timeline.index)
                    this_timeline.index = range(self.break_point[i],self.break_point[i+1])
                    self.main_timeline = pd.concat([self.main_timeline,this_timeline],axis=0)
                    continue
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrHit',str(i+1))
            # 骰点动画
            elif this_section['type'] == 'dice':
                frame_rate = config.frame_rate
                width = config.Width
                height = config.Height
                try:
                    # 建立小节
                    this_timeline=pd.DataFrame(index=range(0,frame_rate*5),dtype=str,columns=render_arg) # 5s
                    # 背景
                    alpha_timeline = np.hstack([self.dynamic['formula'](0,1,frame_rate//2),np.ones(frame_rate*4-frame_rate//2),self.dynamic['formula'](1,0,frame_rate)])
                    this_timeline['BG1'] = 'black' # 黑色背景
                    this_timeline['BG1_a'] = alpha_timeline * 80
                    this_timeline['BG2'] = this_background
                    this_timeline['BG2_a'] = 100
                    # 新建内建动画
                    Auto_media_name = 'BIA_'+str(i+1)
                    for layer in range(0,3):
                        # 在媒体列表中添加内建媒体
                        self.medias[Auto_media_name+'_'+str(layer)] = Dice(
                            dice_set = this_section['dice_set'],
                            layer = layer
                            )
                    # 动画参数
                    # 文字描述
                    this_timeline['Am3'] = Auto_media_name+'_0'
                    this_timeline['Am3_a'] = alpha_timeline * 100
                    this_timeline['Am3_t'] = 0
                    this_timeline['Am3_c'] = 'NA'
                    this_timeline['Am3_p'] = 'NA'
                    # 滚动骰点
                    this_timeline['Am2'] = np.hstack([np.repeat(Auto_media_name+'_1',int(frame_rate*2.5)),np.repeat('NA',frame_rate*5-int(frame_rate*2.5))]) # 2.5s
                    this_timeline['Am2_a'] = np.hstack([self.dynamic['formula'](0,100,frame_rate//2),
                                                        np.ones(int(frame_rate*2.5)-2*(frame_rate//2))*100,
                                                        self.dynamic['formula'](100,0,frame_rate//2),
                                                        np.zeros(frame_rate*5-int(frame_rate*2.5))])
                    this_timeline['Am2_t'] = np.hstack([np.arange(0,int(frame_rate*2.5)),np.zeros(frame_rate*5-int(frame_rate*2.5))])
                    this_timeline['Am2_c'] = 'NA'
                    this_timeline['Am2_p'] = 'NA'
                    # 出目显示
                    this_timeline['Am1'] = np.hstack([np.repeat('NA',frame_rate*5-int(frame_rate*2.5)),np.repeat(Auto_media_name+'_2',int(frame_rate*2.5))])
                    this_timeline['Am1_a'] = np.hstack([np.zeros(frame_rate*5-int(frame_rate*2.5)),
                                                        self.dynamic['formula'](0,100,frame_rate//2),
                                                        np.ones(int(frame_rate*2.5)-frame_rate//2-frame_rate)*100,
                                                        self.dynamic['formula'](100,0,frame_rate)])
                    this_timeline['Am1_t'] = 0
                    this_timeline['Am1_c'] = 'NA'
                    this_timeline['Am1_p'] = 'NA'
                    # SE
                    this_timeline.loc[frame_rate//3,'SE'] = "'./media/SE_dice.wav'"
                    # BGM
                    if BGM_queue != []:
                        this_timeline.loc[0,'BGM'] = BGM_queue.pop(0) #从BGM_queue里取第一个出来 alpha 1.13.5
                    # 时间轴延长
                    this_timeline['section'] = i
                    self.break_point[i+1]=self.break_point[i]+len(this_timeline.index)
                    this_timeline.index = range(self.break_point[i],self.break_point[i+1])
                    self.main_timeline = pd.concat([self.main_timeline,this_timeline],axis=0)
                    continue
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrDice',str(i+1))
            # 暂停画面
            elif this_section['type'] == 'wait':
                try:
                    # 持续指定帧，仅显示当前背景
                    this_timeline=pd.DataFrame(index=range(0,this_section['time']),dtype=str,columns=render_arg)
                    # 停留的帧：当前时间轴的最后一帧，不含S图层
                    try:
                        wait_frame = self.main_timeline.iloc[-1].copy()
                    except IndexError:
                        raise ParserError('WaitBegin')
                    # 检查wait frame里面，有没有透明度为0，如果有则删除图层
                    for layer in config.zorder:
                        if wait_frame[layer+'_a'] == 0:
                            # 以防导出xml项目异常
                            wait_frame[layer] = 'NA'
                    # 不应用：0：section，BGM，Voice，SE
                    this_timeline[render_arg[1:-3]] = wait_frame[render_arg[1:-3]]
                    # BGM
                    if BGM_queue != []:
                        this_timeline.loc[0,'BGM'] = BGM_queue.pop(0)
                    # 时间轴延长
                    this_timeline['section'] = i
                    self.break_point[i+1]=self.break_point[i]+len(this_timeline.index)
                    this_timeline.index = range(self.break_point[i],self.break_point[i+1])
                    self.main_timeline = pd.concat([self.main_timeline,this_timeline],axis=0)
                    continue
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrWait',str(i+1))
            else:
                self.break_point[i+1]=self.break_point[i]
                continue
            self.break_point[i+1]=self.break_point[i]
        # 处理place的末端
        try:
            self.place_anime_execute(this_placed_anime=this_placed_animation,last_section=last_placed_animation_section,this_section=i+1)
            self.place_bubble_execute(this_placed_bubble=this_placed_bubble,last_section=last_placed_bubble_section,this_section=i+1)
        except Exception as E:
            raise ParserError('ParErrCompl')
        # 去掉和前一帧相同的帧，节约了性能
        self.main_timeline = self.main_timeline.fillna('NA') #假设一共10帧
        timeline_diff = self.main_timeline.iloc[:-1].copy() #取第0-9帧
        timeline_diff.index = timeline_diff.index+1 #设置为第1-10帧
        timeline_diff.loc[0]='NA' #再把第0帧设置为NA
        dropframe = (self.main_timeline == timeline_diff.sort_index()).all(axis=1) # 这样，就是原来的第10帧和第9帧在比较了
        # 去掉重复帧
        self.main_timeline = self.main_timeline[dropframe == False].copy()
        self.break_point = self.break_point.astype(int)
        # 返回
        return self.main_timeline
    # 操作
    def reindex(self):
        old_struct_keys = [int(x) for x in self.struct.keys()]
        old_struct_keys.sort()
        new_struct_keys = [str(x) for x in range(0,len(old_struct_keys))]
        new_struct:dict = {}
        for idx,ele in enumerate(old_struct_keys):
            this_new = new_struct_keys[idx]
            new_struct[this_new] = self.struct[str(ele)]
        self.struct = new_struct
    def exchange(self,key1:str,key2:str)->bool:
        try:
            self.struct[key1], self.struct[key2] = self.struct[key2], self.struct[key1]
            return True
        except:
            return False
# 下播了下播了，开3D太卡了，都没法做测试了555