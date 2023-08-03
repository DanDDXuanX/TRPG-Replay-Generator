#!/usr/bin/env python
# coding: utf-8

# 广播

from .ScriptParser import MediaDef, CharTable, RplGenLog

class BoardcastHandler:
    def __init__(self,mediadef:MediaDef,chartab:CharTable,logfile:dict):
        # 载入项目
        self.mediadef:MediaDef = mediadef
        self.chartab:CharTable = chartab
        self.logfile:dict = logfile
    def rename_media(self,mtype:str,old_name:str,new_name:str)->dict:
        counter = {
            'mediadef'  :0,
            'chartab'   :0,
            'logfile'   :0
        }
        # 位置类
        if mtype in ['Pos','FreePos','PosGrid']:
            # 媒体
            counter['mediadef'] += self._handle_pos(old_name=old_name, new_name=new_name)
            counter['logfile'] += self._handle_rplgenlog(old_name=old_name, new_name=new_name, etype='move_pos')
        elif mtype in ['Text','StrokeText','RichText','HPLabel']:
            counter['mediadef'] += self._handle_text(old_name=old_name, new_name=new_name)
        elif mtype in ['Bubble','Balloon','DynamicBubble']:
            counter['mediadef'] += self._handle_bubble(old_name=old_name, new_name=new_name)
            counter['chartab'] += self._boardcast_chartab(old_name=old_name, new_name=new_name, effect_arg='Bubble')
            counter['logfile'] += self._handle_rplgenlog(old_name=old_name, new_name=new_name, etype='bubble')
            counter['logfile'] += self._handle_rplgenlog(old_name=old_name, new_name=new_name, etype='move_media')
        elif mtype == 'ChatWindow':
            counter['chartab'] += self._boardcast_chartab(old_name=old_name, new_name=new_name, effect_arg='Bubble',cw=True)
            counter['logfile'] += self._handle_rplgenlog(old_name=old_name, new_name=new_name, etype='bubble')
            counter['logfile'] += self._handle_rplgenlog(old_name=old_name, new_name=new_name, etype='clear')
            counter['logfile'] += self._handle_rplgenlog(old_name=old_name, new_name=new_name, etype='move_media')
        elif mtype == 'Animation':
            counter['mediadef'] += self._handle_animation(old_name=old_name, new_name=new_name)
            counter['chartab'] += self._boardcast_chartab(old_name=old_name, new_name=new_name, effect_arg='Animation')
            counter['logfile'] += self._handle_rplgenlog(old_name=old_name, new_name=new_name, etype='animation')
            counter['logfile'] += self._handle_rplgenlog(old_name=old_name, new_name=new_name, etype='move_media')
        elif mtype == 'Background':
            counter['logfile'] += self._handle_rplgenlog(old_name=old_name, new_name=new_name, etype='background')
            counter['logfile'] += self._handle_rplgenlog(old_name=old_name, new_name=new_name, etype='move_media')
        elif mtype == 'Audio':
            counter['logfile'] += self._handle_rplgenlog(old_name=old_name, new_name=new_name, etype='se')
        elif mtype == 'BGM':
            counter['logfile'] += self._handle_rplgenlog(old_name=old_name, new_name=new_name, etype='music')
        else:
            pass
        # 返回值
        return counter
    def rename_charactor(self,old_name,new_name)->dict:
        counter = {
            'mediadef'  :0,
            'chartab'   :0,
            'logfile'   :0
        }
        # 只影响log
        counter['logfile'] += self._handle_rplgenlog(old_name=old_name, new_name=new_name, etype='name')
        # 返回值
        return counter
    def rename_subtype(self,old_name,new_name)->dict:
        counter = {
            'mediadef'  :0,
            'chartab'   :0,
            'logfile'   :0
        }
        # 只影响log
        counter['logfile'] += self._handle_rplgenlog(old_name=old_name, new_name=new_name, etype='subtype')
        # 返回值
        return counter
    def rename_custom(self,old_name,new_name)->dict:
        counter = {
            'mediadef'  :0,
            'chartab'   :0,
            'logfile'   :0
        }
        # 只影响log
        counter['logfile'] += self._handle_target(old_name=old_name, new_name=new_name)
        # 返回值
        return counter
    def _boardcast_mediadef(self, old_name:str, new_name:str, effect_type:list, effect_arg:str):
        old_name_reference = f'${old_name}'
        new_name_reference = f'${new_name}'
        counter = 0
        for keyword in self.mediadef.struct:
            this_section:dict = self.mediadef.struct[keyword]
            if this_section['type'] not in effect_type:
                continue
            else:
                # 情况0：section缺省参数
                if effect_arg not in this_section:
                    continue
                # 情况1：直接是引用参数
                elif this_section[effect_arg] == old_name_reference:
                    # 变更参数
                    this_section[effect_arg] = new_name_reference
                    counter += 1
                # 情况2：是subscript
                elif type(this_section[effect_arg]) is dict:
                    subscript = this_section[effect_arg]
                    if subscript['object'] == old_name_reference:
                        subscript['object'] = new_name_reference
                        counter += 1
                    else:
                        continue
                # 情况3：是list的一部分
                elif type(this_section[effect_arg]) is list:
                    for idx, item in enumerate(this_section[effect_arg]):
                        if item == old_name_reference:
                            this_section[effect_arg][idx] = new_name_reference
                            counter += 1
                # 情况-1：是例外
                else:
                    pass
        # 返回值：执行的次数
        return counter
    def _boardcast_rplgenlog(self, old_name:str, new_name:str, effect_type:str, effect_arg:list)->int:
        old_name_reference = old_name
        new_name_reference = new_name
        counter = 0
        for filename in self.logfile:
            this_rplgenlog:RplGenLog = self.logfile[filename]
            for idx in this_rplgenlog.struct:
                this_section = this_rplgenlog.struct[idx]
                if this_section['type'] != effect_type:
                    continue
                else:
                    for arg in effect_arg:
                        path = arg.split('.')
                        counter += self._boardcast_rgl_section_recursive(
                            section=this_section,
                            old_name_reference=old_name_reference,
                            new_name_reference=new_name_reference,
                            effect_path=path
                        )
        # 返回值
        return counter
    def _boardcast_dialog_subtype(self, old_name:str, new_name:str)->int:
        char_name = old_name.split('.')[0]
        old_name_reference = old_name.split('.')[1]
        new_name_reference = new_name.split('.')[1]
        counter = 0
        for filename in self.logfile:
            this_rplgenlog:RplGenLog = self.logfile[filename]
            for idx in this_rplgenlog.struct:
                this_section = this_rplgenlog.struct[idx]
                # 逐行
                if this_section['type'] != 'dialog':
                    continue
                else:
                    # 逐个角色
                    for cdx in this_section['charactor_set']:
                        this_char = this_section['charactor_set'][cdx]
                        if this_char['name'] != char_name:
                            continue
                        else:
                            if this_char['subtype'] == old_name_reference:
                                this_char['subtype'] = new_name_reference
                                counter += 1
        # 返回值
        return counter
    def _boardcast_rgl_section_recursive(self,section:dict,old_name_reference:str,new_name_reference:str,effect_path:list)->int:
        keyword = effect_path[0]
        # 如果已是终端
        if len(effect_path) == 1:
            # 检查是不是
            if type(section) is not dict:
                return 0
            elif keyword == '*':
                counter = 0
                for idx in section:
                    if section[idx] == old_name_reference:
                        section[idx] = new_name_reference
                        counter += 1
                return counter
            elif section[keyword] == old_name_reference:
                section[keyword] = new_name_reference
                return 1
            elif keyword == 'object' and 'index' in section:
                # 特例：move：posgrid[]
                if section[keyword] == f'${old_name_reference}':
                    section[keyword] = f'${new_name_reference}'
                    return 1
            else:
                return 0
        # 如果不是终端
        else:
            if type(section) is not dict:
                return 0
            elif keyword == '*':
                counter = 0
                for idx in section:
                    counter += self._boardcast_rgl_section_recursive(
                        section=section[idx],
                        old_name_reference=old_name_reference,
                        new_name_reference=new_name_reference,
                        effect_path=effect_path[1:]
                    )
                return counter
            elif keyword not in section:
                return 0
            else:
                return self._boardcast_rgl_section_recursive(
                    section=section[keyword],
                    old_name_reference=old_name_reference,
                    new_name_reference=new_name_reference,
                    effect_path=effect_path[1:]
                )
    def _boardcast_chartab(self, old_name:str, new_name:str, effect_arg:str, cw:bool=False):
        old_name_reference = old_name
        new_name_reference = new_name
        counter = 0
        for keyword in self.chartab.struct:
            this_section:dict = self.chartab.struct[keyword]
            # 情况0：section缺省参数
            if effect_arg not in this_section:
                continue
            # 情况1：直接是引用参数
            elif this_section[effect_arg] == old_name_reference:
                # 变更参数
                this_section[effect_arg] = new_name_reference
                counter += 1
            # 情况2：是聊天窗
            elif cw and this_section[effect_arg].split(':')[0] == old_name_reference:
                # 变更参数
                try:
                    sub_key = this_section[effect_arg].split(':')[1]
                except:
                    continue
                this_section[effect_arg] = f"{new_name_reference}:{sub_key}"
                counter += 1
            else:
                pass
        # 返回值：执行的次数
        return counter
    def _handle_pos(self,old_name,new_name)->int:
        effect_type = ['Animation','Bubble','Balloon','DynamicBubble','ChatWindow','Background']
        effect_arg = 'pos'
        return self._boardcast_mediadef(
            old_name    = old_name,
            new_name    = new_name,
            effect_type = effect_type,
            effect_arg  = effect_arg
        )
    def _handle_text(self,old_name,new_name)->int:
        effect_type = ['Bubble','Balloon','DynamicBubble']
        effect_arg  = ['Main_Text','Header_Text']
        counter = 0
        for arg in effect_arg:
            counter += self._boardcast_mediadef(
                old_name    = old_name,
                new_name    = new_name,
                effect_type = effect_type,
                effect_arg  = arg
            )
        return counter
    def _handle_bubble(self,old_name,new_name)->int:
        effect_type = ['ChatWindow']
        effect_arg = 'sub_Bubble'
        return self._boardcast_mediadef(
            old_name    = old_name,
            new_name    = new_name,
            effect_type = effect_type,
            effect_arg  = effect_arg
        )
    def _handle_animation(self,old_name,new_name)->int:
        effect_type = ['ChatWindow']
        effect_arg = 'sub_Anime'
        return self._boardcast_mediadef(
            old_name    = old_name,
            new_name    = new_name,
            effect_type = effect_type,
            effect_arg  = effect_arg
        )
    def _handle_target(self,old_name,new_name)->int:
        effect_type = ['Bubble','Balloon','DynamicBubble']
        effect_arg = 'ht_target'
        return self._boardcast_mediadef(
            old_name    = old_name,
            new_name    = new_name,
            effect_type = effect_type,
            effect_arg  = effect_arg
        )
    def _handle_rplgenlog(self,old_name,new_name,etype)->int:
        # 确定目标
        if etype == 'move_pos':
            effect_type = 'move'
            effect_args = ['target','value.pos1','value.pos2','value.pos1.object','value.pos2.object']
        elif etype == 'move_media':
            effect_type = 'move'
            effect_args = ['target']
        elif etype == 'animation':
            effect_type = etype
            effect_args = ['object','object.*']
        elif etype == 'bubble':
            effect_type = etype
            effect_args = ['object','object.bubble']
        elif etype in ['background','clear']:
            effect_type = etype
            effect_args = ['object']
        elif etype == 'music':
            effect_type = etype
            effect_args = ['value']
        elif etype == 'se':
            effect_type = 'dialog'
            effect_args = ['sound_set.*.sound']
        elif etype == 'name':
            effect_type = 'dialog'
            effect_args = ['charactor_set.*.name']
        elif etype == 'subtype':
            return self._boardcast_dialog_subtype(
                old_name    =old_name,
                new_name    =new_name,
            )
        else:
            return 0
        # 开始广播
        return self._boardcast_rplgenlog(
            old_name    =old_name,
            new_name    =new_name,
            effect_type =effect_type,
            effect_arg  =effect_args,
        )
