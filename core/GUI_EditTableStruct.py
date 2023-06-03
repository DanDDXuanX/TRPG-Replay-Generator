#!/usr/bin/env python
# coding: utf-8

# 以 格式化的字典的形式存储的，编辑区的每个小节的结构

TableStruct:dict = {
    # 角色表
    'CharTable' :{
        'charactor':{
            "NameSep":{
                "Text": "角色",
                "Command":None,
                "Content":{
                    "Name": {
                        "ktext": "名字：",
                        "dtext": "",
                        "ditem": "label",
                        "valuekey": "Name",
                        "vitem": "label",
                        "vtype": "str",
                        "default": ""
                    },
                    "Subtype": {
                        "ktext": "差分：",
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "Subtype",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "default"
                    },
                }
            },
            "MediaSep":{
                "Text": "媒体",
                "Command":None,
                "Content":{
                    "Animation": {
                        "ktext": "立绘：",
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "Animation",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "NA"
                    },
                    "Bubble": {
                        "ktext": "气泡：",
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "Bubble",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "NA"
                    },
                }
            },
            "VoiceSep":{
                "Text": "语音",
                "Command":None,
                "Content":{
                    "Voice": {
                        "ktext": "音源：",
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "Voice",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "NA"
                    },
                    "SpeechRate": {
                        "ktext": "语速：",
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "SpeechRate",
                        "vitem": "entry",
                        "vtype": "int",
                        "default": 0
                    },
                    "PitchRate": {
                        "ktext": "语调：",
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "PitchRate",
                        "vitem": "entry",
                        "vtype": "int",
                        "default": 0
                    }
                }
            },
            "CustomSep":{
                "Text": "自定义",
                "Command":None,
                "Content":{}
            }
        },
    },
    # 媒体定义
    'MediaDef':{
        "Pos":{
            "InfoSep":{
                "Text": "基本信息",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "类型：",
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "Pos"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "新建位置"
                    },
                }
            },
            "ArgsSep":{
                "Text": "参数",
                "Command":None,
                "Content":{
                    "pos":{
                        "ktext": "位置：",
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "(0,0)"
                    }
                }
            }
        },
        "FreePos":{
            "InfoSep":{
                "Text": "基本信息",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "类型：",
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "FreePos"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "新建自由位置"
                    },
                },
            },
            "ArgsSep":{
                "Text": "参数",
                "Command":None,
                "Content":{
                    "pos": {
                        "ktext": "位置：",
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                },
            },
        },
        "PosGrid":{
            "InfoSep":{
                "Text": "基本信息",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "类型：",
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "FreePos"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "新建自由位置"
                    },
                }
            },
            "ArgsSep":{
                "Text": "参数",
                "Command":None,
                "Content":{
                    "pos": {
                        "ktext": "起点：",
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "end": {
                        "ktext": "终点：",
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "end",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(1,1)"
                    },
                    "x_step": {
                        "ktext": "水平点数：",
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "x_step",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 0
                    },
                    "y_step": {
                        "ktext": "垂直点数：",
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "y_step",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 0
                    }
                }
            }
        },
        "Text":{
            "InfoSep":{
                "Text": "基本信息",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "类型：",
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "Text"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "新建文字"
                    },
                    "label_color": {
                        "ktext": "标签色：",
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "Lavender"
                    },
                }
            },
            "FontSep":{
                "Text": "字体",
                "Command":None,
                "Content":{
                    "fontfile": {
                        "ktext": "字体路径：",
                        "dtext": "浏览",
                        "ditem": "button",
                        "valuekey": "fontfile",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "./media/SourceHanSansCN-Regular.otf"
                    },
                    "line_limit": {
                        "ktext": "单行字数：",
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "line_limit",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 20
                    }
                }
            },
            "StyleSep":{
                "Text": "样式",
                "Command":None,
                "Content":{
                    "fontsize": {
                        "ktext": "大小：",
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "fontsize",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 40
                    },
                    "color": {
                        "ktext": "颜色：",
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "color",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0,0,255)"
                    },
                }
            }
        },
        "StrokeText":{
            "InfoSep":{
                "Text": "基本信息",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "类型：",
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "StrokeText"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "新建描边字"
                    },
                    "label_color": {
                        "ktext": "标签色：",
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "Lavender"
                    },
                }
            },
            "FontSep":{
                "Text": "字体",
                "Command":None,
                "Content":{
                    "fontfile": {
                        "ktext": "字体路径：",
                        "dtext": "浏览",
                        "ditem": "button",
                        "valuekey": "fontfile",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "./media/SourceHanSansCN-Regular.otf"
                    },
                    "line_limit": {
                        "ktext": "单行字数：",
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "line_limit",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 20
                    },
                }
            },
            "StyleSep":{
                "Text": "字体样式",
                "Command":None,
                "Content":{
                    "fontsize": {
                        "ktext": "大小：",
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "fontsize",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 40
                    },
                    "color": {
                        "ktext": "颜色：",
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "color",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0,0,255)"
                    },
                }
            },
            "StrokeSep":{
                "Text": "描边样式",
                "Command":None,
                "Content":{
                    "edge_color": {
                        "ktext": "颜色：",
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "edge_color",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(255,255,255,255)"
                    },
                    "edge_width": {
                        "ktext": "宽度：",
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "edge_width",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": "1"
                    },
                    "projection": {
                        "ktext": "投影方向：",
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "projection",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "C"
                    }
                }
            },
        },
        "RichText":{
            "InfoSep":{
                "Text": "基本信息",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "类型：",
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "RichText"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "新建富文本"
                    },
                    "label_color": {
                        "ktext": "标签色：",
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "Lavender"
                    },
                }
            },
            "FontSep":{
                "Text": "字体",
                "Command":None,
                "Content":{
                    "fontfile": {
                        "ktext": "字体路径：",
                        "dtext": "浏览",
                        "ditem": "button",
                        "valuekey": "fontfile",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "./media/SourceHanSansCN-Regular.otf"
                    },
                    "line_limit": {
                        "ktext": "单行字数：",
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "line_limit",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 20
                    }
                }
            },
            "StyleSep":{
                "Text": "样式",
                "Command":None,
                "Content":{
                    "fontsize": {
                        "ktext": "大小：",
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "fontsize",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 40
                    },
                    "color": {
                        "ktext": "颜色：",
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "color",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0,0,255)"
                    },
                }
            }
        },
        "Bubble":{
            "InfoSep":{
                "Text": "基本信息",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "类型：",
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "Bubble"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "新建气泡"
                    },
                    "label_color": {
                        "ktext": "标签色：",
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "Lavender"
                    },
                }
            },
            "ImageSep":{
                "Text": "图像",
                "Command":None,
                "Content":{
                    "filepath": {
                        "ktext": "图片路径：",
                        "dtext": "浏览",
                        "ditem": "button",
                        "valuekey": "filepath",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "None"
                    },
                    "pos": {
                        "ktext": "位置：",
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "scale": {
                        "ktext": "缩放：",
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "scale",
                        "vitem": "spine",
                        "vtype": "float",
                        "default": 1.0
                    },
                }
            },
            "MainSep":{
                "Text": "主文本",
                "Command":None,
                "Content":{
                    "Main_Text": {
                        "ktext": "字体：",
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "Main_Text",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "Text()"
                    },
                    "mt_pos": {
                        "ktext": "位置：",
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "mt_pos",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "align": {
                        "ktext": "对齐：",
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "align",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "left"
                    },
                    "line_distance": {
                        "ktext": "行距：",
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "line_distance",
                        "vitem": "spine",
                        "vtype": "float",
                        "default": 1.5
                    },
                }
            },
            "HeadSep":{
                "Text": "头文本",
                "Command":None,
                "Content":{
                    "Header_Text": {
                        "ktext": "字体：",
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "Header_Text",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "None"
                    },
                    "ht_pos": {
                        "ktext": "位置：",
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "ht_pos",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "ht_target": {
                        "ktext": "目标：",
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "ht_target",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "Name"
                    }
                }
            },
        },
    },
    # 剧本
    'RplGenLog':{},
    # 项目设置
    'Config':{},
    # 软件设置
    'Preference':{},
}