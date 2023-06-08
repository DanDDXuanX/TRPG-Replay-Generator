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
                        "tooltip":"角色的名字\n注：只能使用：中文、英文、数字、空格、下划线",
                        "dtext": "",
                        "ditem": "label",
                        "valuekey": "Name",
                        "vitem": "label",
                        "vtype": "str",
                        "default": ""
                    },
                    "Subtype": {
                        "ktext": "差分：",
                        "tooltip":"差分代表角色的不同状态，一个角色可以有多个差分。",
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
                        "tooltip":"本角色的立绘形象，请选择一个Animation类媒体。",
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "Animation",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "NA"
                    },
                    "Bubble": {
                        "ktext": "气泡：",
                        "tooltip":"本角色的发言气泡，请选择一个Bubble类媒体。",
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
                        "tooltip":"本角色语音合成的音源。",
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "Voice",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "NA"
                    },
                    "SpeechRate": {
                        "ktext": "语速：",
                        "tooltip":"语音的说话语速，取值范围是-500~500，-500代表0.5倍速度，500代表2倍速度。",
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "SpeechRate",
                        "vitem": "entry",
                        "vtype": "int",
                        "default": 0
                    },
                    "PitchRate": {
                        "ktext": "语调：",
                        "tooltip":"语音的说话音高，取值范围是-500~500，-500代表低八度，500代表高八度。",
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
                "Command":{
                    "type" : "add_kvd",
                },
                "Content":{
                    "{template}" : {
                        "ktext": "{template}：",
                        "tooltip":None,
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "{template}",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "Init"
                    }
                }
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
                        "tooltip":None,
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "Pos"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "tooltip":None,
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
                        "tooltip":None,
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
                        "tooltip":None,
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "FreePos"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "tooltip":None,
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
                        "tooltip":None,
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
                        "tooltip":None,
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "FreePos"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "tooltip":None,
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
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "end": {
                        "ktext": "终点：",
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "end",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(1,1)"
                    },
                    "x_step": {
                        "ktext": "水平点数：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "x_step",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 0
                    },
                    "y_step": {
                        "ktext": "垂直点数：",
                        "tooltip":None,
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
                        "tooltip":None,
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "Text"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "tooltip":None,
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "新建文字"
                    },
                    "label_color": {
                        "ktext": "标签色：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "FontSep":{
                "Text": "字体",
                "Command":None,
                "Content":{
                    "fontfile": {
                        "ktext": "字体路径：",
                        "tooltip":None,
                        "dtext": "浏览",
                        "ditem": "button",
                        "valuekey": "fontfile",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "./media/SourceHanSansCN-Regular.otf"
                    },
                    "line_limit": {
                        "ktext": "单行字数：",
                        "tooltip":None,
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
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "fontsize",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 40
                    },
                    "color": {
                        "ktext": "颜色：",
                        "tooltip":None,
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
                        "tooltip":None,
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "StrokeText"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "tooltip":None,
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "新建描边字"
                    },
                    "label_color": {
                        "ktext": "标签色：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "FontSep":{
                "Text": "字体",
                "Command":None,
                "Content":{
                    "fontfile": {
                        "ktext": "字体路径：",
                        "tooltip":None,
                        "dtext": "浏览",
                        "ditem": "button",
                        "valuekey": "fontfile",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "./media/SourceHanSansCN-Regular.otf"
                    },
                    "line_limit": {
                        "ktext": "单行字数：",
                        "tooltip":None,
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
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "fontsize",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 40
                    },
                    "color": {
                        "ktext": "颜色：",
                        "tooltip":None,
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
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "edge_color",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(255,255,255,255)"
                    },
                    "edge_width": {
                        "ktext": "宽度：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "edge_width",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": "1"
                    },
                    "projection": {
                        "ktext": "投影方向：",
                        "tooltip":None,
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
                        "tooltip":None,
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "RichText"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "tooltip":None,
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "新建富文本"
                    },
                    "label_color": {
                        "ktext": "标签色：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "FontSep":{
                "Text": "字体",
                "Command":None,
                "Content":{
                    "fontfile": {
                        "ktext": "字体路径：",
                        "tooltip":None,
                        "dtext": "浏览",
                        "ditem": "button",
                        "valuekey": "fontfile",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "./media/SourceHanSansCN-Regular.otf"
                    },
                    "line_limit": {
                        "ktext": "单行字数：",
                        "tooltip":None,
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
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "fontsize",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 40
                    },
                    "color": {
                        "ktext": "颜色：",
                        "tooltip":None,
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
                        "tooltip":None,
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "Bubble"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "tooltip":None,
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "新建气泡"
                    },
                    "label_color": {
                        "ktext": "标签色：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "ImageSep":{
                "Text": "图像",
                "Command":None,
                "Content":{
                    "filepath": {
                        "ktext": "图片路径：",
                        "tooltip":None,
                        "dtext": "浏览",
                        "ditem": "button",
                        "valuekey": "filepath",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "None"
                    },
                    "pos": {
                        "ktext": "位置：",
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "scale": {
                        "ktext": "缩放：",
                        "tooltip":None,
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
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "Main_Text",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "Text()"
                    },
                    "mt_pos": {
                        "ktext": "位置：",
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "mt_pos",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "align": {
                        "ktext": "对齐：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "align",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'left'"
                    },
                    "line_distance": {
                        "ktext": "行距：",
                        "tooltip":None,
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
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "Header_Text",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "None"
                    },
                    "ht_pos": {
                        "ktext": "位置：",
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "ht_pos",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "ht_target": {
                        "ktext": "目标：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "ht_target",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Name'"
                    }
                }
            },
        },
        "Balloon":{
            "InfoSep":{
                "Text": "基本信息",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "类型：",
                        "tooltip":None,
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "Balloon"
                    },
                        "Name": {
                        "ktext": "媒体名：",
                        "tooltip":None,
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "新建气球"
                    },
                    "label_color": {
                        "ktext": "标签色：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "ImageSep":{
                "Text": "图像",
                "Command":None,
                "Content":{
                    "filepath": {
                        "ktext": "图片路径：",
                        "tooltip":None,
                        "dtext": "浏览",
                        "ditem": "button",
                        "valuekey": "filepath",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "None"
                    },
                    "pos": {
                        "ktext": "位置：",
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "scale": {
                        "ktext": "缩放：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "scale",
                        "vitem": "spine",
                        "vtype": "float",
                        "default": 1
                    },
                }
            },
            "MainSep":{
                "Text": "主文本",
                "Command":None,
                "Content":{
                    "Main_Text": {
                        "ktext": "字体：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "Main_Text",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "Text()"
                    },
                    "mt_pos": {
                        "ktext": "位置：",
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "mt_pos",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "align": {
                        "ktext": "对齐：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "align",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'left'"
                    },
                    "line_distance": {
                        "ktext": "行距：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "line_distance",
                        "vitem": "spine",
                        "vtype": "float",
                        "default": 1.5
                    },
                }
            },
            "HeadSep-%d":{
                "Text": "头文本-%d",
                "Command":{
                    "type":'add_sep',
                    "key":"Header_Text_%d"
                },
                "Content":{
                    "Header_Text_%d": {
                        "ktext": "字体：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "Header_Text",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "None"
                    },
                    "ht_pos_%d": {
                        "ktext": "位置：",
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "ht_pos",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "ht_target_%d": {
                        "ktext": "目标：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "ht_target",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Name'"
                    }
                }
            },
        },
        "DynamicBubble":{
            "InfoSep":{
                "Text": "基本信息",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "类型：",
                        "tooltip":None,
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "Balloon"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "tooltip":None,
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "新建自适应气泡"
                    },
                    "label_color": {
                        "ktext": "标签色：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "ImageSep":{
                "Text": "图像",
                "Command":None,
                "Content":{
                    "filepath": {
                        "ktext": "图片路径：",
                        "tooltip":None,
                        "dtext": "浏览",
                        "ditem": "button",
                        "valuekey": "filepath",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "None"
                    },
                    "pos": {
                        "ktext": "位置：",
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "scale": {
                        "ktext": "缩放：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "scale",
                        "vitem": "spine",
                        "vtype": "float",
                        "default": 1.0
                    },
                }
            },
            "DynamicSep":{
                "Text": "自适应参数",
                "Command":None,
                "Content":{
                    "fill_mode": {
                        "ktext": "填充模式：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "fill_mode",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'stretch'"
                    },
                    "fit_axis": {
                        "ktext": "适应方向：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "fit_axis",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'free'"
                    },
                }
            },
            "MainSep":{
                "Text": "主文本",
                "Command":None,
                "Content":{
                    "Main_Text": {
                        "ktext": "字体：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "Main_Text",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "Text()"
                    },
                    "mt_pos": {
                        "ktext": "起点：",
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "mt_pos",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "mt_end": {
                        "ktext": "终点：",
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "mt_end",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "line_distance": {
                        "ktext": "行距：",
                        "tooltip":None,
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
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "Header_Text",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "None"
                    },
                    "ht_pos": {
                        "ktext": "位置：",
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "ht_pos",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "ht_target": {
                        "ktext": "目标：",
                        "tooltip":None,
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
        "ChatWindow":{
            "InfoSep":{
                "Text": "基本信息",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "类型：",
                        "tooltip":None,
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "ChatWindow"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "tooltip":None,
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "新建聊天窗"
                    },
                    "label_color": {
                        "ktext": "标签色：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "ImageSep":{
                "Text": "图像",
                "Command":None,
                "Content":{
                    "filepath": {
                        "ktext": "图片路径：",
                        "tooltip":None,
                        "dtext": "浏览",
                        "ditem": "button",
                        "valuekey": "filepath",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "None"
                    },
                    "pos": {
                        "ktext": "位置：",
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "scale": {
                        "ktext": "缩放：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "scale",
                        "vitem": "spine",
                        "vtype": "float",
                        "default": 1
                    },
                }
            },
            "AreaSep":{
                "Text": "滚动区域",
                "Command":None,
                "Content":{
                    "sub_pos": {
                        "ktext": "起点：",
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "sub_pos",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "Text()"
                    },
                    "sub_end": {
                        "ktext": "终点：",
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "sub_end",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "sub_distance": {
                        "ktext": "间距：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "sub_distance",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 50
                    },
                }
            },
            "HeadSep":{
                "Text": "头像位置",
                "Command":None,
                "Content":{
                    "am_left": {
                        "ktext": "左边界：",
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "am_left",
                        "vitem": "entry",
                        "vtype": "int",
                        "default": 0
                    },
                    "am_right": {
                        "ktext": "右边界：",
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "am_right",
                        "vitem": "entry",
                        "vtype": "int",
                        "default": 0
                    },
                }
            },
            "SubSep-%d":{
                "Text": "子气泡-%d",
                "Command":{
                    "type":'add_sep',
                    "key":"sub_key-%d"
                },
                "Content":{
                    "sub_key-%d": {
                        "ktext": "关键字：",
                        "tooltip":None,
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "sub_key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "Key1"
                    },
                    "sub_Bubble-%d": {
                        "ktext": "气泡：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "sub_Bubble",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "Bubble()"
                    },
                    "sub_Anime-%d": {
                        "ktext": "头像：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "sub_Anime",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "None"
                    },
                    "sub_align-%d": {
                        "ktext": "对齐：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "sub_align",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'left'"
                    }
                }
            }
        },
        "Animation":{
            "InfoSep":{
                "Text": "基本信息",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "类型：",
                        "tooltip":None,
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "Animation"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "tooltip":None,
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "新建立绘"
                    },
                    "label_color": {
                        "ktext": "标签色：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "ImageSep":{
                "Text": "图像",
                "Command":None,
                "Content":{
                    "filepath": {
                        "ktext": "图片路径：",
                        "tooltip":None,
                        "dtext": "浏览",
                        "ditem": "button",
                        "valuekey": "filepath",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": ""
                    },
                    "pos": {
                        "ktext": "位置：",
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "scale": {
                        "ktext": "缩放：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "scale",
                        "vitem": "spine",
                        "vtype": "float",
                        "default": 1.0
                    },
                }
            },
            "AnimeSep":{
                "Text": "动画",
                "Command":None,
                "Content":{
                    "tick": {
                        "ktext": "拍率：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "tick",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 1
                    },
                    "loop": {
                        "ktext": "循环播放：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "loop",
                        "vitem": "combox",
                        "vtype": "bool",
                        "default": True
                    }
                }
            }
        },
        "Background":{
            "InfoSep":{
                "Text": "基本信息",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "类型：",
                        "tooltip":None,
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "Background"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "tooltip":None,
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "新建背景"
                    },
                    "label_color": {
                        "ktext": "标签色：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "ImageSep":{
                "Text": "图像",
                "Command":None,
                "Content":{
                    "filepath": {
                        "ktext": "图片路径：",
                        "tooltip":None,
                        "dtext": "浏览",
                        "ditem": "button",
                        "valuekey": "filepath",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "'black'"
                    },
                    "pos": {
                        "ktext": "位置：",
                        "tooltip":None,
                        "dtext": "选择",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "scale": {
                        "ktext": "缩放：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "scale",
                        "vitem": "spine",
                        "vtype": "float",
                        "default": 1.0
                    },
                }
            },
        },
        "Audio":{
            "InfoSep":{
                "Text": "基本信息",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "类型：",
                        "tooltip":None,
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "Audio"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "tooltip":None,
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "新建音效"
                    },
                    "label_color": {
                        "ktext": "标签色：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "Caribbean"
                    },
                }
            },
            "AudioSep":{
                "Text":"音频",
                "Command":None,
                "Content":{
                    "filepath": {
                        "ktext": "音频路径：",
                        "tooltip":None,
                        "dtext": "浏览",
                        "ditem": "button",
                        "valuekey": "filepath",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": ""
                    }
                }
            }
        },
        "BGM":{
            "InfoSep":{
                "Text": "基本信息",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "类型：",
                        "tooltip":None,
                        "dtext": "帮助",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "BGM"
                    },
                    "Name": {
                        "ktext": "媒体名：",
                        "tooltip":None,
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "新建背景音乐"
                    },
                    "label_color": {
                        "ktext": "标签色：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "Caribbean"
                    },
                }
            },
            "AudioSep":{
                "Text": "音频",
                "Command":None,
                "Content":{
                    "filepath": {
                        "ktext": "音频路径：",
                        "tooltip":None,
                        "dtext": "浏览",
                        "ditem": "button",
                        "valuekey": "filepath",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": ""
                    },
                    "volume": {
                        "ktext": "音量：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "volume",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 100
                    },
                    "loop": {
                        "ktext": "循环播放：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "loop",
                        "vitem": "combox",
                        "vtype": "bool",
                        "default": True
                    }
                }
            }
        },
    },
    # 剧本
    'RplGenLog':{
        "blank":{
            "BlankSep":{
                "Text":"空白行",
                "Command":None,
                "Content":{}
            }
        },
        "comment":{
            "CommentSep":{
                "Text":"注释",
                "Command":None,
                "Content":{
                    "content":{
                        "ktext": "文本：",
                        "tooltip":None,
                        "dtext": "",
                        "ditem": "label",
                        "valuekey": "content",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": ""
                    }
                }
            }
            },
        "dialog":{},
        "background":{
            "BgSep":{
                "Text":"背景",
                "Command":None,
                "Content":{
                    "object":{
                        "ktext": "对象：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "object",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "black"
                    }
                },
            },
            "BgMetSep":{
                "Text":"切换效果",
                "Command":{
                    "type":"subscript",
                    "key":"."
                    },
                "Content":{}
            }
        },
        "animation":{
            "AmSep":{
                "Text":"立绘",
                "Command":None,
                "Content":{}
            },
            "AmMetSep":{
                "Text":"切换效果",
                "Command":None,
                "Content":{}
            }
        },
        "bubble":{
            "BbSep":{
                "Text":"气泡",
                "Command":None,
                "Content":{
                    
                }
            },
            "BbMetSep":{
                "Text":"切换效果",
                "Command":None,
                "Content":{}
            },
            "TxMetSep":{
                "Text":"文字效果",
                "Command":None,
                "Content":{}
            }
        },
        "set":{},
        "move":{},
        "table":{
            "TableSep":{
                "Text":"修改目标",
                "Command":{
                    "type":"subscript",
                    "key":"."
                },
                "Content":{
                    "name":{
                        "ktext": "角色：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "target.name",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": ""
                    },
                    "subtype":{
                        "ktext": "差分：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "target.subtype",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": None
                    },
                    "column":{
                        "ktext": "角色表列：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "target.column",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": ""
                    },
                }
            },
            "ValueSep":{
                "Text":"值",
                "Command":None,
                "Content":{
                    'value':{
                        "ktext": "修改为：",
                        "tooltip":None,
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "value",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": ""
                    }
                }
            }
        },
        "music":{
            "BGMSep":{
                "Text":"背景音乐",
                "Command":None,
                "Content":{
                    "value":{
                        "ktext": "音频：",
                        "tooltip":None,
                        "dtext": "浏览",
                        "ditem": "button",
                        "valuekey": "value",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": ""
                    }
                }
            }
        },
        "clear":{
            "CwSep":{
                "Text":"清除目标",
                "Command":None,
                "Content":{
                    "object":{
                        "ktext": "聊天窗：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "object",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": ""
                    }
                }
            }
        },
        "hitpoint":{
            "HpSep":{
                "Text":"生命值动画",
                "Command":None,
                "Content":{
                    "content":{
                        "ktext": "描述：",
                        "tooltip":None,
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "content",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": ""
                    },
                    "hp_max":{
                        "ktext": "HP上限：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "hp_max",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 0
                    },
                    "hp_begin":{
                        "ktext": "初始HP：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "hp_begin",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 0
                    },
                    "hp_end":{
                        "ktext": "结束HP：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "hp_end",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 0
                    },
                }
            }
        },
        "dice":{},
        "wait":{
            "TimeSep":{
                "Text":"停顿",
                "Command":None,
                "Content":{
                    "time":{
                        "ktext": "时长：",
                        "tooltip":None,
                        "dtext": "（帧）",
                        "ditem": "label",
                        "valuekey": "time",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 30
                    }
                }
            }
        },
    },
    # 项目设置
    'Config':{},
    # 软件设置
    'Preference':{},
}

label_colors = {
    "紫罗兰紫"  :"'Violet'",
    "鸢尾花色蓝":"'Iris'",
    "加勒比海蓝":"'Caribbean'",
    "薰衣草粉"  :"'Lavender'",
    "天蓝色"   :"'Cerulean'",
    "森林绿"   :"'Forest'",
    "玫瑰红"   :"'Rose'",
    "芒果橙"   :"'Mango'",
    "紫色"    :"'Purple'",
    "蓝色"    :"'Blue'",
    "深青色"    :"'Teal'",
    "洋红色"   :"'Magenta'",
    "棕黄色"   :"'Tan'",
    "绿色"    :"'Green'",
    "棕色"    :"'Brown'",
    "黄色"    :"'Yellow'"
}

projection = {
    "中心"  :"'C'",
    "上"    :"'N'",
    "下"    :"'S'",
    "左"    :"'W'",
    "右"    :"'E'",
    "左上"  :"'NW'",
    "左下"  :"'SW'",
    "右上"  :"'NE'",
    "右下"  :"'SE'",
}

alignments = {
    "左对齐" : "'left'",
    "居中对齐": "'center'"
}

charactor_columns={
    "Name（角色名）":"'Name'",
    "Subtype（差分名）":"'Subtype'",
    "Animation（立绘）":"'Animation'",
    "Bubble（气泡）":"'Bubble'",
    "Voice（音源）":"'Voice'",
    "SpeechRate（语速）":"'SpeechRate'",
    "PitchRate（语调）":"'PitchRate'",
}

fill_mode = {
    "拉伸" : "'stretch'",
    "拼贴" : "'collage'",
}
fit_axis = {
    "自由" : "'free'",
    "垂直" : "'vertical'",
    "水平" : "'horizontal'"
}

True_False = {
    "是": True,
    "否": False
}