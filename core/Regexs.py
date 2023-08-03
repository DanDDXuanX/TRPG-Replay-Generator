#!/usr/bin/env python
# coding: utf-8
# 正则表达式定义

import re

# replay_generator
# 将对话行拆分为：[角色框]、<效果>、:文本、<文本效果>、{音效}
RE_dialogue = re.compile('^\[([\ \w\.\;\(\)\,]+)\](<[\w\=\d]+>)?:(.+?)(<[\w\=\d]+>)?({.+})?$')
# 将放置媒体行，拆分为：<标志>、<效果>、对象
RE_placeobj = re.compile('^<(background|animation|bubble)>(<[\w\=]+>)?:(.+)$')
RE_bubble = re.compile('(\w+)\("([^\\"]*)","([^\\"]*)",?(<(\w+)=?(\d+)?>)?\)')
RE_setting = re.compile('^<(set|move|table):([\w\ \.]+)>:(.+)$')
# 将多个角色拆分为单个角色
RE_characor = re.compile('([\w\ ]+)(\(\d*\))?(\.\w+)?')
# 将一个<效果> 拆分为 效果、=持续时间
RE_modify = re.compile('<(\w+)(=\d+)?>')
# 将多个音效拆分为单个音效
RE_sound = re.compile('({.+?})')
# 新增：单独提取普通音频框
RE_sound_simple = re.compile('({[^*]+?})')
# 解析位置运算的表达式
RE_pos_exp = re.compile("^(\w+|\w+\[[\d\,\ ]+\]|\([\d\,\ ]+\))( *(\+|\-) *(\w+|\w+\[[\d\,\ ]+\]|\([\d\,\ ]+\)))?$")
# 单独提取星标音频框
RE_asterisk = re.compile('(\{([^\{\}]*?[;])?\*([\w\ \.\,，。：？！“”]*)?\})')
RE_hitpoint = re.compile('<hitpoint>:\((.+?),(\d+),(\d+),(\d+)\)') # a 1.6.5 血条预设动画
RE_dice = re.compile('\((.+?),(\d+),([\d]+|NA),(\d+)\)') # a 1.7.5 骰子预设动画，老虎机
RE_wait = re.compile('^<wait>:(.+)$')
# 媒体定义的解析
RE_mediadef = re.compile('^(\w+) *= *(Pos|FreePos|PosGrid|Text|StrokeText|RichText|HPLabel|Bubble|Balloon|DynamicBubble|ChatWindow|Animation|GroupedAnimation|BuiltInAnimation|Background|BGM|Audio)(\(.*\))')
RE_mediadef_args = re.compile("(fontfile|fontsize|color|line_limit|marker|fg_path|bg_path|width|repeat|filepath|scale|Main_Text|Header_Text|pos|end|x_step|y_step|mt_pos|mt_rotate|mt_end|ht_pos|ht_rotate|ht_target|fill_mode|fit_axis|align|vertical_align|head_align|line_distance|line_num_est|tick|loop|volume|edge_color|edge_width|projection|sub_key|sub_Bubble|sub_Anime|sub_align|sub_pos|sub_end|am_left|am_right|sub_distance|label_color)?\ {0,4}=?\ {0,4}(Text\(\)|Pos\(\)|\[[\w,'()]+\]|\w+\[[\d\,]+\]|[^,()]+|\([-\d,\ ]+\))")
RE_subscript_def = re.compile('^(\w+) *= *(\w+\[.*\])')
# 富文本的富标记
RE_rich = re.compile("(\[/?[\w\^\#]{1,2}(?:\:[\w\#]+)?\])")