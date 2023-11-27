#!/usr/bin/env python
# coding: utf-8
# 拓展功能

# 1. 自动处理双人同屏时，展示多个角色的逻辑

from .ScriptParser import MediaDef, CharTable, RplGenLog

def make_rgl_char(name,subtype):
    return {
        "name": name,
        "subtype": subtype,
        "alpha": None
    }
def auto_duet(rgl:RplGenLog,mdf:MediaDef,ctb:CharTable,left_label:str='Teal',right_label:str='Magenta'):
    # 记录的前一个角色
    recode_left_name = None
    recode_right_name = None
    # 从头开始遍历一个rgl
    for idx in rgl.struct:
        this_section = rgl.struct[idx]
        # 如果不是对话行，那没事了
        if this_section['type'] != 'dialog':
            continue
        # 反之：检查有几个角色
        charactors = this_section['charactor_set']
        if len(charactors) != 1:
            continue
        # 再，检查角色的立绘
        primary = charactors["0"]
        char_keyword = primary['name'] + '.' + primary['subtype']
        char_anime_name = ctb.struct[char_keyword]['Animation']
        if char_anime_name == 'NA':
            continue
        char_colorlabel = mdf.struct[char_anime_name]['label_color']
        # 看是左还是右
        if char_colorlabel == left_label:
            if recode_right_name:
                charactors["1"] = make_rgl_char(*recode_right_name)
            recode_left_name = [primary['name'],primary['subtype']]
        elif char_colorlabel == right_label:
            if recode_left_name:
                charactors["1"] = make_rgl_char(*recode_left_name)
            recode_right_name = [primary['name'],primary['subtype']]
        else:
            continue
    return rgl