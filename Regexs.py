import re

# 正则表达式定义

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

#RE_asterisk = re.compile('(\{([^\{\}]*?[,;])?\*([\w\.\,，。：？！“”]*)?\})') # v 1.8.7 给星标后文本额外增加几个可用的中文符号
#RE_asterisk = re.compile('(\{([^\{\}]*?[,;])?\*([\w\.\,，]*)?\})') # v 1.7.3 修改匹配模式以匹配任何可能的字符（除了花括号）
#RE_asterisk = re.compile('\{\w+[;,]\*(\d+\.?\d*)\}') # 这种格式对于{path;*time的}的格式无效！
#RE_asterisk = re.compile('(\{([\w\.\\\/\'\":]*?[,;])?\*([\w\.\,，]*)?\})') # a 1.4.3 修改了星标的正则（和ss一致）,这种对于有复杂字符的路径无效！
