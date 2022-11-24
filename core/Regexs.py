#!/usr/bin/env python
# coding: utf-8
# 正则表达式定义

import re

# replay_generator
RE_dialogue = re.compile('^\[([\ \w\.\;\(\)\,]+)\](<[\w\=\d]+>)?:(.+?)(<[\w\=\d]+>)?({.+})?$')
RE_placeobj = re.compile('^<(background|animation|bubble)>(<[\w\=]+>)?:(.+)$')
RE_bubble = re.compile('(\w+)\("([^\\"]*)","([^\\"]*)",?(<(\w+)=?(\d+)?>)?\)')
RE_setting = re.compile('^<set:([\w\ \.]+)>:(.+)$')
RE_characor = re.compile('([\w\ ]+)(\(\d*\))?(\.\w+)?')
RE_modify = re.compile('<(\w+)(=\d+)?>')
RE_sound = re.compile('({.+?})')
RE_asterisk = re.compile('(\{([^\{\}]*?[;])?\*([\w\ \.\,，。：？！“”]*)?\})') # v 1.11.4 音频框分隔符只能用; *后指定可以有空格
RE_hitpoint = re.compile('<hitpoint>:\((.+?),(\d+),(\d+),(\d+)\)') # a 1.6.5 血条预设动画
RE_dice = re.compile('\((.+?),(\d+),([\d]+|NA),(\d+)\)') # a 1.7.5 骰子预设动画，老虎机
RE_mediadef = re.compile('^(\w+) *= *(Pos|FreePos|PosGrid|Text|StrokeText|Bubble|Balloon|DynamicBubble|ChatWindow|Animation|GroupedAnimation|BuiltInAnimation|Background|BGM|Audio)(\(.*\))')