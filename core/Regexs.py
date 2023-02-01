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
RE_setting = re.compile('^<set:([\w\ \.]+)>:(.+)$')
# 将多个角色拆分为单个角色
RE_characor = re.compile('([\w\ ]+)(\(\d*\))?(\.\w+)?')
# 将一个<效果> 拆分为 效果、=持续时间
RE_modify = re.compile('<(\w+)(=\d+)?>')
# 将多个音效拆分为单个音效
RE_sound = re.compile('({.+?})')
# 新增：单独提取普通音频框
RE_sound_simple = re.compile('({[^*]+?})')
# 单独提取星标音频框
RE_asterisk = re.compile('(\{([^\{\}]*?[;])?\*([\w\ \.\,，。：？！“”]*)?\})')
RE_hitpoint = re.compile('<hitpoint>:\((.+?),(\d+),(\d+),(\d+)\)') # a 1.6.5 血条预设动画
RE_dice = re.compile('\((.+?),(\d+),([\d]+|NA),(\d+)\)') # a 1.7.5 骰子预设动画，老虎机
RE_wait = re.compile('^<wait>:(.+)$')
RE_mediadef = re.compile('^(\w+) *= *(Pos|FreePos|PosGrid|Text|StrokeText|Bubble|Balloon|DynamicBubble|ChatWindow|Animation|GroupedAnimation|BuiltInAnimation|Background|BGM|Audio)(\(.*\))')