#!/usr/bin/env python
# coding: utf-8

# log读取器

import re
import pandas as pd
import numpy as np

class StoryImporter:
    parse_struct = {
        "QQExport" : {
            "new": {
                "cmd"   : "new",
                "regex" : r"^(\d{4}-\d{2}-\d{2} \d{1,2}:\d{1,2}:\d{1,2})\s+(.*?)(\([^)]+\)|\<[^>]+\>)$",
                "ID"    : r"$3",
                "name"  : r"$2",
                "speech": ""
            },
            "add": {
                "cmd"   : "add",
                "regex" : r"^(.*)$",
                "ID"    : None,
                "name"  : None,
                "speech": r"$1"
            }
        },
        "QQCopy" : {
            "new":{
                "regex" : r"^(【.{0,10}】)?(.+?)\s+(\d{4}/\d{1,2}/\d{1,2}\s+)?(\d{1,2}:\d{1,2}:\d{1,2})$",
                "ID"    : r"$2",
                "name"  : r"$2",
                "speech": ""
            },
            "add": {
                "regex" : r"^(.*)$",
                "ID"    : None,
                "name"  : None,
                "speech": r"$1"
            }
        },
        "RGLoid":{
            "new":{
                "regex" : r"^\[([^\[\]]+?)(,.+?)?\](<.+>)?:(.+?)(<.+>)?({.+})?$",
                "ID"    : r"$1",
                "name"  : r"$1",
                "speech": r"$2"
            }
        },
        # "Maoye":{},
        "FVTT":{
            "new":{
                "regex" : r"^\[(\d+\/\d+\/\d+, \d+:\d+:\d+ [AP]M)\] (.+)$",
                "ID"    : r"$2",
                "name"  : r"$2",
                "speech": None
            },
            "add": {
                "regex" : r"^(.*)$",
                "ID"    : None,
                "name"  : None,
                "speech": r"$1"
            }
        },
        "SinaNya":{
            "new":{
                "regex" : r"^(<\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d>\s*)?\[?([^\]]+)\]?:\s*?([^\n]+)$",
                "ID"    : r"$2",
                "name"  : r"$2",
                "speech": r"$3"
            },
        },
        "Rendered":{
            "new":{
                "regex" : r"^((\d{4}\/\d{2}\/\d{2}\s)?\d{2}:\d{2}:\d{2})?<(.+?)(\([^)]+\))?>:(.*)$",
                "ID"    : r"$3",
                "name"  : r"$3",
                "speech": r"$5"
            },
            "add": {
                "regex" : r"^(.*)$",
                "ID"    : None,
                "name"  : None,
                "speech": r"$1"
            }
        },
    }
    struct_col = ['ID','name','speech']
    def __init__(self) -> None:
        self.log_mode = None
        self.section = {
            "ID"    :"",
            "name"  :"",
            "speech":""
        }
        self.results = pd.DataFrame(columns = self.struct_col)
        self.line_index = 0
    def load(self,text:str):
        lines = text.split('\n')
        for line in lines:
            if self.log_mode is None:
                self.identify(line=line)
            # 解析，或者pass
            self.parse(line=line)
    def identify(self,line:str):
        for mode in self.parse_struct:
            regex = self.parse_struct[mode]['new']['regex']
            if re.match(regex,line):
                self.log_mode = mode
                print(self.log_mode)
                return mode
        return None
    def parse(self,line:str):
        if self.log_mode is None:
            return None
        else:
            for cmd in self.parse_struct[self.log_mode]:
                this_cmd = self.parse_struct[self.log_mode][cmd]
                regex = this_cmd['regex']
                M = re.match(regex,line)
                if M:
                    # 执行
                    self.execute(match=M, cmd=cmd, cmd_args=this_cmd)
                    # 跳过循环
                    break
    def execute(self,match:re.Match,cmd:str,cmd_args:dict):
        if cmd == 'add':
            for col in self.struct_col:
                if cmd_args[col]:
                    group_index = int(cmd_args[col][1:])
                    self.section[col] += match.group(group_index) + '\n' # 如果是以多行模式结束，则结尾是换行符！
        elif cmd == 'new':
            self.recode()
            for col in self.struct_col:
                if cmd_args[col]:
                    group_index = int(cmd_args[col][1:])
                    self.section[col] = match.group(group_index)
        else:
            pass
    def recode(self):
        # 始终有一个为空行的0
        # 记录这一行的结果
        self.results.loc[self.line_index] = self.section
        # 清空section
        self.section = {
            "ID"    :"",
            "name"  :"",
            "speech":""
        }
        # 序号+1
        self.line_index += 1
        # 调试
        if self.line_index % 1000 == 0:
            print(self.line_index)
    def get_charactor_ID(self):
        ID_valid = re.compile('[\w\ ]+')
        if len(self.results) == 0:
            return []
        else:
            this_result = self.results[1:]
            raw_ID = this_result['ID'].value_counts()
            all_ID = raw_ID.index.map(ID_valid.findall)
    def get_charactor_name(self):
        if len(self.results) == 0:
            return []
        else:
            this_result = self.results[1:]
            raw_name = this_result['name'].value_counts()
            # TODO
