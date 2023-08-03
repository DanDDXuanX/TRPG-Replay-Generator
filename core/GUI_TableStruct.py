#!/usr/bin/env python
# coding: utf-8

# 以 格式化的字典的形式存储的表结构

EditTableStruct = {
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
                        "default": "init"
                    }
                }
            }
        },
        'charactor.args':{
            "Name"      :"Name",
            "Subtype"   :"Subtype",
            "Animation" :"Animation",
            "Bubble"    :"Bubble",
            "Voice"     :"Voice",
            "SpeechRate":"SpeechRate",
            "PitchRate" :"PitchRate"
        }
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
        "Pos.args":{
            "type"  :'type',
            "pos"   :'pos',
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
        "FreePos.args":{
            "type"  :'type',
            "pos"   :'pos',
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
        "PosGrid.args":{
            "type"  : "type",
            "pos"   : "pos",
            "end"   : "end",
            "x_step": "x_step",
            "y_step": "y_step"
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
                        "default": "'./media/SourceHanSansCN-Regular.otf'"
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
        "Text.args":{
            "type"          : "type",
            "fontfile"      : "fontfile",
            "fontsize"      : "fontsize",
            "color"         : "color",
            "line_limit"    : "line_limit",
            "label_color"   : "label_color"
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
                        "default": "'./media/SourceHanSansCN-Regular.otf'"
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
        "StrokeText.args":{
            "type"          : "type",
            "fontfile"      : "fontfile",
            "fontsize"      : "fontsize",
            "color"         : "color",
            "line_limit"    : "line_limit",
            "edge_color"    : "edge_color",
            "edge_width"    : "edge_width",
            "projection"    : "projection",
            "label_color"   : "label_color"
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
                        "default": "'./media/SourceHanSansCN-Regular.otf'"
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
        "RichText.args":{
            "type"          : "type",
            "fontfile"      : "fontfile",
            "fontsize"      : "fontsize",
            "color"         : "color",
            "line_limit"    : "line_limit",
            "label_color"   : "label_color"
        },
        "HPLabel":{
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
                        "default": "HPLabel"
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
                        "default": "'./media/SourceHanSansCN-Regular.otf'"
                    },
                    "marker": {
                        "ktext": "文字标签：",
                        "tooltip":None,
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "marker",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "'A/B'"
                    },
                    "align": {
                        "ktext": "血条位置：",
                        "tooltip":None,
                        "dtext": "浏览",
                        "ditem": "button",
                        "valuekey": "align",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'left'"
                    },
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
            },
            "ImageSep":{
                "Text": "图形",
                "Command":None,
                "Content":{
                    "fg_path": {
                        "ktext": "前景路径：",
                        "tooltip":None,
                        "dtext": "浏览",
                        "ditem": "button",
                        "valuekey": "fg_path",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "'./media/heart.png'"
                    },
                    "bg_path": {
                        "ktext": "背景路径：",
                        "tooltip":None,
                        "dtext": "浏览",
                        "ditem": "button",
                        "valuekey": "bg_path",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "'./media/heart_shape.png'"
                    },
                }
            },
            "BarSep":{
                "Text": "血条",
                "Command":None,
                "Content":{
                    "width": {
                        "ktext": "宽度：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "width",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 0
                    },
                    "repeat": {
                        "ktext": "单位：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "repeat",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 2
                    },
                }
            }
        },
        "HPLabel.args":{
            "type"          : "type",
            "fontfile"      : "fontfile",
            "fontsize"      : "fontsize",
            "color"         : "color",
            "marker"        : "marker",
            "fg_path"       : "fg_path",
            "bg_path"       : "bg_path",
            "align"         : "align",
            "width"         : "width",
            "repeat"        : "repeat",
            "label_color"   : "label_color"
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
                    "mt_rotate": {
                        "ktext": "旋转：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "mt_rotate",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 0
                    },
                    "align": {
                        "ktext": "水平对齐：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "align",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'left'"
                    },
                    "vertical_align": {
                        "ktext": "垂直对齐：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "vertical_align",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'top'"
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
                    "line_num_est": {
                        "ktext": "行数：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "line_num_est",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 4
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
                    "ht_rotate": {
                        "ktext": "旋转：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "ht_rotate",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": "0"
                    },
                    "head_align": {
                        "ktext": "对齐：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "head_align",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'left'"
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
        "Bubble.args":{
            "type"          : "type",
            "filepath"      : "filepath",
            "scale"         : "scale",
            "pos"           : "pos",
            "Main_Text"     : "Main_Text",
            "mt_pos"        : "mt_pos",
            "mt_rotate"     : "mt_rotate",
            "align"         : "align",
            "vertical_align": "vertical_align",
            "head_align"    : "head_align",
            "line_distance" : "line_distance",
            "line_num_est"  : "line_num_est",
            "Header_Text"   : "Header_Text",
            "ht_pos"        : "ht_pos",
            "ht_rotate"     : "ht_rotate",
            "ht_target"     : "ht_target",
            "label_color"   : "label_color",
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
                    "mt_rotate": {
                        "ktext": "旋转：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "mt_rotate",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 0
                    },
                    "align": {
                        "ktext": "水平对齐：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "align",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'left'"
                    },
                    "vertical_align": {
                        "ktext": "垂直对齐：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "vertical_align",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'top'"
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
                    "line_num_est": {
                        "ktext": "行数：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "line_num_est",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 4
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
                        "default": "Text()"
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
                    "ht_rotate_%d": {
                        "ktext": "旋转：",
                        "tooltip":None,
                        "dtext": "（数值）",
                        "ditem": "label",
                        "valuekey": "ht_rotate",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": "0"
                    },
                    "head_align_%d": {
                        "ktext": "对齐：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "head_align",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'left'"
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
        "Balloon.args":{
            "type"          : "type",
            "filepath"      : "filepath",
            "scale"         : "scale",
            "pos"           : "pos",
            "Main_Text"     : "Main_Text",
            "mt_pos"        : "mt_pos",
            "mt_rotate"     : "mt_rotate",
            "align"         : "align",
            "vertical_align": "vertical_align",
            "head_align"    : "head_align_%d",
            "line_distance" : "line_distance",
            "line_num_est"  : "line_num_est",
            "Header_Text"   : "Header_Text_%d",
            "ht_pos"        : "ht_pos_%d",
            "ht_rotate"     : "ht_rotate_%d",
            "ht_target"     : "ht_target_%d",
            "label_color"   : "label_color",
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
        "DynamicBubble.args":{
            "type"          : "type",
            "filepath"      : "filepath",
            "scale"         : "scale",
            "pos"           : "pos",
            "Main_Text"     : "Main_Text",
            "mt_pos"        : "mt_pos",
            "mt_end"        : "mt_end",
            "line_distance" : "line_distance",
            "Header_Text"   : "Header_Text",
            "ht_pos"        : "ht_pos",
            "ht_target"     : "ht_target",
            "fill_mode"     : "fill_mode",
            "fit_axis"      : "fit_axis",
            "label_color"   : "label_color",
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
                        "valuekey": "$key",
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
                    "key":"sub_key_%d"
                },
                "Content":{
                    "sub_key_%d": {
                        "ktext": "关键字：",
                        "tooltip":None,
                        "dtext": "（输入）",
                        "ditem": "label",
                        "valuekey": "sub_key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "'Key%d'"
                    },
                    "sub_Bubble_%d": {
                        "ktext": "气泡：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "sub_Bubble",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "Bubble()"
                    },
                    "sub_Anime_%d": {
                        "ktext": "头像：",
                        "tooltip":None,
                        "dtext": "（选择）",
                        "ditem": "label",
                        "valuekey": "sub_Anime",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "None"
                    },
                    "sub_align_%d": {
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
        "ChatWindow.args":{
            "type"          : "type",
            "filepath"      : "filepath",
            "scale"         : "scale",
            "pos"           : "pos",
            "sub_pos"       : "sub_pos",
            "sub_end"       : "sub_end",
            "am_left"       : "am_left",
            "am_right"      : "am_right",
            "sub_distance"  : "sub_distance",
            "sub_key"       : "sub_key_%d",
            "sub_Bubble"    : "sub_Bubble_%d",
            "sub_Anime"     : "sub_Anime_%d",
            "sub_align"     : "sub_align_%d",
            "label_color"   : "label_color",
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
        "Animation.args":{
            "type"          : "type",
            "filepath"      : "filepath",
            "scale"         : "scale",
            "pos"           : "pos",
            "tick"          : "tick",
            "loop"          : "loop",
            "label_color"   : "label_color"
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
        "Background.args":{
            "type"          : "type",
            "filepath"      : "filepath",
            "scale"         : "scale",
            "pos"           : "pos",
            "label_color"   : "label_color"
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
                        "default": "'Caribbean'"
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
        "Audio.args":{
            "type"          : "type",
            "filepath"      : "filepath",
            "label_color"   : "label_color"
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
                        "default": "'Caribbean'"
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
        "BGM.args":{
            "type"          : "type",
            "filepath"      : "filepath",
            "volume"        : "volume",
            "loop"          : "loop",
            "label_color"   : "label_color"
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
}

PreferenceTableStruct = {
    "KeySep":{
        "Text": "语音合成Key",
        "Command":None,
        "Content":{
            "Aliyun.accesskey": {
                "ktext": "阿里云-AccessKey",
                "tooltip":"在AccessKey管理中获取，是一段长度为24的乱码。",
                "dtext": "（输入）",
                "ditem": "label",
                "valuekey": "Aliyun.accesskey",
                "vitem": "entry",
                "vtype": "str",
                "default": "请输入你的AccessKey！"
            },
            "Aliyun.accesskey_secret": {
                "ktext": "阿里云-AccessKeySecret",
                "tooltip":"在AccessKey管理中获取，是一段长度为30的乱码。",
                "dtext": "（输入）",
                "ditem": "label",
                "valuekey": "Aliyun.accesskey_secret",
                "vitem": "entry",
                "vtype": "str",
                "default": "请输入你的AccessKeySecret！"
            },
            "Aliyun.appkey": {
                "ktext": "阿里云-AppKey",
                "tooltip":"在智能语音服务的项目管理页面中，新建项目后获取，是一段长度为16的乱码。",
                "dtext": "（输入）",
                "ditem": "label",
                "valuekey": "Aliyun.appkey",
                "vitem": "entry",
                "vtype": "str",
                "default": "请输入你的AppKey！"
            },
            "Azure.azurekey": {
                "ktext": "微软Azure-密钥",
                "tooltip":"在语音服务中，点击管理密钥后获取，是一段长度为32的乱码。",
                "dtext": "（输入）",
                "ditem": "label",
                "valuekey": "Azure.azurekey",
                "vitem": "entry",
                "vtype": "str",
                "default": "请输入你的密钥！"
            },
            "Azure.service_region": {
                "ktext": "微软Azure-位置/区域",
                "tooltip":"开通语音服务时选择的服务区域。",
                "dtext": "（输入）",
                "ditem": "label",
                "valuekey": "Azure.service_region",
                "vitem": "entry",
                "vtype": "str",
                "default": "eastasia"
            },
        }
    },
    "AppearanceSep":{
        "Text": "界面外观",
        "Command":None,
        "Content":{
            "System.lang":{
                "ktext": "语言：",
                "tooltip":"在控制台终端显示的语言。",
                "dtext": "（选择）",
                "ditem": "label",
                "valuekey": "System.lang",
                "vitem": "combox",
                "vtype": "str",
                "default": 'en'
            },
            "System.theme":{
                "ktext": "主题：",
                "tooltip": "主界面的配色方案，有深色和浅色两个选择。",
                "dtext": "（选择）",
                "ditem": "label",
                "valuekey": "System.theme",
                "vitem": "combox",
                "vtype": "str",
                "default": 'rplgenlight'
            },
        }
    },       
    "MediaSep":{
        "Text": "内建动画",
        "Command":None,
        "Content":{
            "BIA.font":{
                "ktext": "内建动画字体：",
                "tooltip":"骰子和血条动画中的文字部分的字体。",
                "dtext": "浏览",
                "ditem": "button",
                "valuekey": "BIA.font",
                "vitem": "entry",
                "vtype": "str",
                "default": './media/SourceHanSerifSC-Heavy.otf'
            },
            "BIA.font_size":{
                "ktext": "内建动画字号：",
                "tooltip":"骰子和血条动画中文字的大小的乘数，实际字号等于这个数值乘以项目的宽分辨率。",
                "dtext": "（数值）",
                "ditem": "label",
                "valuekey": "BIA.font_size",
                "vitem": "entry",
                "vtype": "float",
                "default": 0.0521
            },
            "BIA.dice_mode":{
                "ktext": "骰子模式：",
                "tooltip":"在骰子动画中，类COC规则是出目小于检定值为成功，而类DND规则是相反的。",
                "dtext": "（选择）",
                "ditem": "label",
                "valuekey": "BIA.dice_mode",
                "vitem": "combox",
                "vtype": "str",
                "default": 'COC'
            },
            "BIA.dice_threshold":{
                "ktext": "骰子阈值：",
                "tooltip":"在骰子动画中，最极端的出目值被规定为大成功/大失败，指定大成功的阈值（比例）。",
                "dtext": "（输入）",
                "ditem": "label",
                "valuekey": "BIA.dice_threshold",
                "vitem": "entry",
                "vtype": "float",
                "default": 0.05
            },
            "BIA.heart_pic":{
                "ktext": "HP动画前景：",
                "tooltip":"在血条动画中，代表剩余生命值的符号的图片。",
                "dtext": "浏览",
                "ditem": "button",
                "valuekey": "BIA.heart_pic",
                "vitem": "entry",
                "vtype": "str",
                "default": './media/heart.png'
            },
            "BIA.heart_shape":{
                "ktext": "HP动画背景：",
                "tooltip":"在血条动画中，代表生命值总量的符号的图片。",
                "dtext": "浏览",
                "ditem": "button",
                "valuekey": "BIA.heart_shape",
                "vitem": "entry",
                "vtype": "str",
                "default": './media/heart_shape.png'
            },
            "BIA.heart_distance":{
                "ktext": "HP动画心心距离：",
                "tooltip":"在血条动画中，邻近的两个心心的间距的乘数，实际间距等于这个数值乘以项目的宽分辨率。",
                "dtext": "（数值）",
                "ditem": "label",
                "valuekey": "BIA.heart_distance",
                "vitem": "entry",
                "vtype": "float",
                "default": 0.026
            },
        }
    },
    "EditSep":{
        "Text": "编辑设置",
        "Command":None,
        "Content":{
            "Edit.auto_periods":{
                "ktext": "自动句号：",
                "tooltip":"当拆分对话行时，是否自动纠正句尾的标点符号？",
                "dtext": "（选择）",
                "ditem": "label",
                "valuekey": "Edit.auto_periods",
                "vitem": "combox",
                "vtype": "bool",
                "default": False
            },
            "Edit.import_mode":{
                "ktext": "导入模式：",
                "tooltip":"向项目导入脚本时，如果脚本中包含了项目中已有的名称，采用何种模式来处理？",
                "dtext": "（选择）",
                "ditem": "label",
                "valuekey": "Edit.import_mode",
                "vitem": "combox",
                "vtype": "str",
                "default": 'add'
            },
            'Edit.auto_convert':{
                "ktext": "音频转格式：",
                "tooltip":"选择音频文件时，如果是不支持的格式，是否自动生成一个推荐的格式的副本？",
                "dtext": "（选择）",
                "ditem": "label",
                "valuekey": "Edit.auto_convert",
                "vitem": "combox",
                "vtype": "str",
                "default": 'ask'
            },
            'Edit.asterisk_import':{
                "ktext": "自动星标语音：",
                "tooltip":"在剧本页，使用tab菜单浏览文件导入音频时，是否自动将音频处理为星标语音？",
                "dtext": "（选择）",
                "ditem": "label",
                "valuekey": "Edit.asterisk_import",
                "vitem": "combox",
                "vtype": "bool",
                "default": True
            },
            'Edit.rename_boardcast':{
                "ktext": "更名广播：",
                "tooltip":"当修改一个角色或媒体对象的名称时，是否将变更同步到所有引用这个对象的位置？",
                "dtext": "（选择）",
                "ditem": "label",
                "valuekey": "Edit.rename_boardcast",
                "vitem": "combox",
                "vtype": "str",
                "default": 'ask'
            }
        }
    },
    "PreviewSep":{
        "Text": "预览设置",
        "Command":None,
        "Content":{
            "Preview.progress_bar_style":{
                "ktext": "进度条风格：",
                "tooltip":"选择进度条是彩色风格、黑白风格，还是不显示进度条。",
                "dtext": "（选择）",
                "ditem": "label",
                "valuekey": "Preview.progress_bar_style",
                "vitem": "combox",
                "vtype": "str",
                "default": 'color'
            },
            "Preview.framerate_counter":{
                "ktext": "帧率显示器开启：",
                "tooltip":"选择是否常驻开启帧率显示器。",
                "dtext": "（选择）",
                "ditem": "label",
                "valuekey": "Preview.framerate_counter",
                "vitem": "combox",
                "vtype": "bool",
                "default": True
            },
        }
    },
    "ExportSep":{
        "Text": "导出设置",
        "Command":None,
        "Content":{
            "Export.force_split_clip":{
                "ktext": "强制拆分剪辑：",
                "tooltip":"导出PR项目时，如果选择是，在所有小节断点，都会强制拆分所有剪辑，即使这个断点前后是同一个媒体。",
                "dtext": "（选择）",
                "ditem": "label",
                "valuekey": "Export.force_split_clip",
                "vitem": "combox",
                "vtype": "bool",
                "default": False
            },
            "Export.crf":{
                "ktext": "视频质量：",
                "tooltip":"导出为mp4视频时的质量，即ffmpeg的crf值；取值范围为0-51，越小对应越高的视频质量，通常合理范围为18-28。",
                "dtext": "（选择）",
                "ditem": "label",
                "valuekey": "Export.crf",
                "vitem": "spine",
                "vtype": "int",
                "default": 24
            },
            "Export.hwaccels":{
                "ktext": "硬件加速：",
                "tooltip":"导出为mp4视频时，是否使用GPU硬件加速导出？注意，仅适用于支持CUDA的NVIDIA GPU，如果硬件不支持会发生错误！",
                "dtext": "（选择）",
                "ditem": "label",
                "valuekey": "Export.hwaccels",
                "vitem": "combox",
                "vtype": "bool",
                "default": False
            },
        }
    },
}

ExecuteTableStruct = {
    "InputSep":{
        "Text": "输入文件",
        "Command":None,
        "Content":{
            "mediadef": {
                "ktext": "媒体定义：",
                "tooltip":"媒体库的定义文件，是一个txt文本文件",
                "dtext": "浏览",
                "ditem": "button",
                "valuekey": None,
                "vitem": "entry",
                "vtype": "str",
                "default": ""
            },
            "chartab": {
                "ktext": "角色配置：",
                "tooltip":"角色配置表，是一个tsv表格或者xlsx表格",
                "dtext": "浏览",
                "ditem": "button",
                "valuekey": None,
                "vitem": "entry",
                "vtype": "str",
                "default": ""
            },
            "logfile": {
                "ktext": "剧本文件：",
                "tooltip":"也称log文件，是一个rgl文本文件",
                "dtext": "浏览",
                "ditem": "button",
                "valuekey": None,
                "vitem": "entry",
                "vtype": "str",
                "default": ""
            },
        }
    },
    "ArgsSep":{
        "Text": "设置",
        "Command":None,
        "Content":{
            "width":{
                "ktext": "分辨率-宽：",
                "tooltip":None,
                "dtext": "（偶数）",
                "ditem": "label",
                "valuekey": None,
                "vitem": "entry",
                "vtype": "int",
                "default": 1920
            },
            "height":{
                "ktext": "分辨率-高：",
                "tooltip":None,
                "dtext": "（偶数）",
                "ditem": "label",
                "valuekey": None,
                "vitem": "entry",
                "vtype": "int",
                "default": 1080
            },
            "framerate":{
                "ktext": "帧率：",
                "tooltip":None,
                "dtext": "（数值）",
                "ditem": "label",
                "valuekey": None,
                "vitem": "entry",
                "vtype": "int",
                "default": 30
            },
            "zorder":{
                "ktext": "图层顺序：",
                "tooltip":None,
                "dtext": "（输入）",
                "ditem": "label",
                "valuekey": "pos",
                "vitem": "entry",
                "vtype": "str",
                "default": "BG2,BG1,Am3,Am2,Am1,AmS,Bb,BbS"
            },
        }
    }
}

ProjectTableStruct = {
    "EmptyProject":{
        "BasicSep":{
            "Text": "基本",
            "Command":None,
            "Content":{
                "proj_name":{
                    "ktext": "项目名称：",
                    "tooltip":"项目的名称，需要同时是一个合法的文件名！",
                    "dtext": "",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "str",
                    "default": "新建空白项目"
                },
                "proj_cover":{
                    "ktext": "项目封面：",
                    "tooltip":"可以选择一张图片作为项目封面。",
                    "dtext": "浏览",
                    "ditem": "button",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "str",
                    "default": "无"
                },
                "save_pos":{
                    "ktext": "保存位置：",
                    "tooltip":"保存项目文件的文件夹。",
                    "dtext": "浏览",
                    "ditem": "button",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "str",
                    "default": ""
                },
            }
        },
        "VideoSep":{
            "Text": "视频",
            "Command":None,
            "Content":{
                "preset_video":{
                    "ktext": "预设：",
                    "tooltip":None,
                    "dtext": "",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "combox",
                    "vtype": "str",
                    "default": "横屏-高清 (1920x1080, 30fps)"
                },
                "video_width":{
                    "ktext": "分辨率宽：",
                    "tooltip":"视频画布的宽度，单位是像素。",
                    "dtext": "（偶数）",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "int",
                    "default": 1920
                },
                "video_height":{
                    "ktext": "分辨率高：",
                    "tooltip":"视频画布的高度，单位是像素。",
                    "dtext": "（偶数）",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "int",
                    "default": 1080
                },
                "frame_rate":{
                    "ktext": "帧率：",
                    "tooltip":"视频每秒的帧数。",
                    "dtext": "（整数）",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "int",
                    "default": 30
                },
            }
        },
        "LayerSep":{
            "Text": "图层",
            "Command":None,
            "Content":{
                "preset_layer":{
                    "ktext": "预设：",
                    "tooltip":None,
                    "dtext": "",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "combox",
                    "vtype": "str",
                    "default": "背景->立绘->气泡"
                },
                "layer_zorder":{
                    "ktext": "图层顺序：",
                    "tooltip":"警告：这是一个敏感的参数，指定错误的值可能导致程序崩溃，请谨慎修改！",
                    "dtext": "",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "str",
                    "default": "BG2,BG1,Am3,Am2,Am1,AmS,Bb,BbS"
                },
            }
        }
    },
    "IntelProject":{
        "BasicSep":{
            "Text": "基本",
            "Command":None,
            "Content":{
                "proj_name":{
                    "ktext": "项目名称：",
                    "tooltip":"项目的名称，需要同时是一个合法的文件名！",
                    "dtext": "",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "str",
                    "default": "新建智能项目"
                },
                "proj_cover":{
                    "ktext": "项目封面：",
                    "tooltip":"可以选择一张图片作为项目封面。",
                    "dtext": "浏览",
                    "ditem": "button",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "str",
                    "default": "无"
                },
                "save_pos":{
                    "ktext": "保存位置：",
                    "tooltip":"保存项目文件的文件夹。",
                    "dtext": "浏览",
                    "ditem": "button",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "str",
                    "default": ""
                }
            }
        },
        "TpltSep":{
            "Text": "选择模板",
            "Command":None,
            "Content":{
                "template":{
                    "ktext": "模板：",
                    "tooltip":"智能项目的预设模板。", # ，访问创意工坊获取更多预设样式模板
                    "dtext": "（选择）",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "combox",
                    "vtype": "str",
                    "default": ""
                },
            }
        },
        "LogSep":{
            "Text": "导入剧本",
            "Command":None,
            "Content":{
                "textfile":{
                    "ktext": "文件：",
                    "tooltip":"导入智能项目的剧本或者跑团日志文件。\n注意：请导入原始的文本文件，而不是染色后的Word文档！",
                    "dtext": "浏览",
                    "ditem": "button",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "str",
                    "default": ""
                },
                "section_break":{
                    "ktext": "自动分段：",
                    "tooltip":"过长的文本会被自动分段为多个剧本。\n注意：选择0则为不分段，但单个剧本过长会导致严重卡顿！",
                    "dtext": "（选择）",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "combox",
                    "vtype": "int",
                    "default": 300
                },
            }
        }
    }
}

# 给Combobox使用的key，value映射关系
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
left_right = {
    '左侧' : "'left'",
    '右侧' : "'right'"
}
alignments = {
    "左对齐" : "'left'",
    "居中对齐": "'center'",
    "右对齐" : "'right'",
}
vertical_alignments = {
    "顶部对齐" : "'top'",
    "居中对齐": "'center'",
    "底部对齐" : "'bottom'",
}
chatalign = {
    "靠左" : "'left'",
    "靠右" : "'right'"
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
askyesno = {
    "每次询问"  : 'ask',
    "始终是"    : 'yes',
    "始终否"    : 'no'
}
language = {
    '中文' : 'zh',
    'English' : 'en'
}
theme = {
    '浅色' : 'rplgenlight',
    '深色' : 'rplgendark'
}
progressbar = {
    '彩色' : 'color',
    '黑白' : 'black',
    '隐藏' : 'hide',
}
import_mode = {
    '新增' : 'add',
    '覆盖' : 'replace'
}
dice_mode = {
    '类COC' : 'COC',
    '类DND' : 'DND'
}
# 新建媒体按钮的结构
NewElement = {
    "charactor":{
        "charactor":{
            "text":"角色差分",
            "tooltip":"【角色差分】是一个角色的不同状态，每个差分可以独立地设置不同的立绘、气泡和语音。",
            "icon":'./media/icon/new/charactor.png'
        }
    },
    "Pos":{
        "Pos":{
            "text":"固定点",
            "tooltip":"【固定点】是画布上的一个不可以移动的点，可以用作图片媒体的位置参数。",
            "icon":'./media/icon/new/Pos.png'
        },
        "FreePos":{
            "text":"自由点",
            "tooltip":"【自由点】是一个可以通过<move>命令移动的点；所有使用自由点作为位置的媒体，当自由点移动后都会同步移动。",
            "icon":'./media/icon/new/FreePos.png'
        },
        "PosGrid":{
            "text":"点网格",
            "tooltip":"【点网格】是一组棋盘网格状的点；点网格的每一个成员都是一个固定点。",
            "icon":'./media/icon/new/PosGrid.png'
        }
    },
    "Text":{
        "Text":{
            "text":"字体",
            "tooltip":"【字体】是最基本的文本字体，通过指定一个字体文件来建立一个字体媒体。",
            "icon":'./media/icon/new/Text.png'
        },
        "StrokeText":{
            "text":"描边字体",
            "tooltip":"和基本字体相比，【描边字体】多了一个可以指定颜色和宽度的描边。",
            "icon":'./media/icon/new/StrokeText.png'
        },
        "RichText":{
            "text":"富文本",
            "tooltip":"使用【富文本】的气泡，可以灵活调整文本的斜体、粗体、字号和颜色。",
            "icon":'./media/icon/new/RichText.png'
        },
        "HPLabel":{
            "text":"血条标签",
            "tooltip":"使用【血条标签】，可以把特定的文本显示为血条样式。",
            "icon":'./media/icon/new/HPLabel.png'
        },
    },
    "Bubble":{
        "Bubble":{
            "text":"气泡",
            "tooltip":"【气泡】是最基本的发言文本框，包含一张底图、一个主文本和一个头文本。",
            "icon":'./media/icon/new/Bubble.png'
        },
        "Balloon":{
            "text":"气球",
            "tooltip":"和气泡相比，【气球】允许设置多个头文本，用于显示不同的角色自定义文本。",
            "icon":'./media/icon/new/Balloon.png'
        },
        "DynamicBubble":{
            "text":"动态气泡",
            "tooltip":"和气泡相比，【动态气泡】的底图尺寸将跟随主文本的长度而变化，常用于聊天窗。",
            "icon":'./media/icon/new/DynamicBubble.png'
        },
        "ChatWindow":{
            "text":"聊天窗",
            "tooltip":"【聊天窗】是即时社交软件风格的文本框，可以滚动显示多条发言内容。",
            "icon":'./media/icon/new/ChatWindow.png'
        },
    },
    "Animation":{
        "Animation":{
            "text":"立绘",
            "tooltip":"【立绘】是最通用的图像媒体，可以展示角色形象或者道具的图片，也可以播放动画。",
            "icon":'./media/icon/new/Animation.png'
        }
    },
    "Background":{
        "Background":{
            "text":"背景",
            "tooltip":"【背景】是整个画面的背景层。注意，背景必须能完整地覆盖整个画幅，否则会出现异常的显示效果！",
            "icon":'./media/icon/new/Background.png'
        }
    },
    "Audio":{
        "Audio":{
            "text":"音效",
            "tooltip":"【音效】是常用的音频媒体，在对话行中可以播放音效，每次音效仅播放一次！",
            "icon":'./media/icon/new/Audio.png'
        },
        "BGM":{
            "text":"背景音乐",
            "tooltip":"【背景音乐】是可以循环播放的音频媒体，使用<bgm>命令控制播放和停止，不会影响音效。",
            "icon":'./media/icon/new/BGM.png'
        }
    }
}

# 动态切换效果的结构
ABMethod = {
    "透明度":{
        "直接替换"      : "replace",
        "淡入淡出"      : "black",
        "交叉溶解"      : "cross",
        "延后替换"      : "delay",
    },
    "运动":{
        "静止"          :'static',
        "通过"          :'pass',
        "跳起"          :'leap',
        "环形"          :'circular'
    },
    "方向":{
        "上"            :'up',
        "下"            :'down',
        "左"            :'left',
        "右"            :'right',
        "指定角度（45度）":'DG45',
    },
    "尺度":{
        "长距离"            : "major",
        "短距离"            : "minor",
        "全屏尺度"          : "entire",
        "指定长度（100像素）": '100'
    },
    '进出':{
        "双端"  : 'both',
        "仅切入": 'in',
        "仅切出": 'out'
    }
}