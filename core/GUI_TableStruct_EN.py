#!/usr/bin/env python
# coding: utf-8

# TableStruct: EN

EditTableStruct = {
    # CharTable
    'CharTable' :{
        'charactor':{
            "NameSep":{
                "Text": "Character",
                "Command":None,
                "Content":{
                    "Name": {
                        "ktext": "Name:",
                        "tooltip":"Name of the character\nNote: Only use: Chinese, English, numbers, spaces, underscores.",
                        "dtext": "",
                        "ditem": "label",
                        "valuekey": "Name",
                        "vitem": "label",
                        "vtype": "str",
                        "default": ""
                    },
                    "Subtype": {
                        "ktext": "Subtype:",
                        "tooltip":"Subtype represents different states of a character. A character can have multiple subtypes.",
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "Subtype",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "default"
                    },
                }
            },
            "MediaSep":{
                "Text": "Medias",
                "Command":None,
                "Content":{
                    "Animation": {
                        "ktext": "Animation:",
                        "tooltip":"Select an Animation media object for the visual portrait of this character.",
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "Animation",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "NA"
                    },
                    "Bubble": {
                        "ktext": "Bubble:",
                        "tooltip":"Select a Bubble-class media for the speech bubble of this character.",
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "Bubble",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "NA"
                    },
                }
            },
            "VoiceSep":{
                "Text": "Speaker",
                "Command":None,
                "Content":{
                    "Voice": {
                        "ktext": "Voice:",
                        "tooltip":"Speaker of this character.",
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "Voice",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "NA"
                    },
                    "SpeechRate": {
                        "ktext": "SpeechRate:",
                        "tooltip":"The speech rate for voice, range from -500 to 500. -500 and 500 represents 0.5 and 2 time the normal speed, respectively",
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "SpeechRate",
                        "vitem": "entry",
                        "vtype": "int",
                        "default": 0
                    },
                    "PitchRate": {
                        "ktext": "PitchRate:",
                        "tooltip":"The pitch for voice, range from -500 to 500. -500 and 500 represents a low octave and a high octave, respectively",
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "PitchRate",
                        "vitem": "entry",
                        "vtype": "int",
                        "default": 0
                    }
                }
            },
            "CustomSep":{
                "Text": "Customized",
                "Command":{
                    "type" : "add_kvd",
                },
                "Content":{
                    "{template}" : {
                        "ktext": "{template}：",
                        "tooltip":None,
                        "dtext": "(input)",
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
    # MediaDef
    'MediaDef':{
        "Pos":{
            "InfoSep":{
                "Text": "Basic Information",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "Type:",
                        "tooltip":None,
                        "dtext": "help",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "Pos"
                    },
                    "Name": {
                        "ktext": "Name:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "Pos_new"
                    },
                }
            },
            "ArgsSep":{
                "Text": "Argument",
                "Command":None,
                "Content":{
                    "pos":{
                        "ktext": "pos:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "entry",
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
                "Text": "Basic Information",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "Type:",
                        "tooltip":None,
                        "dtext": "help",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "FreePos"
                    },
                    "Name": {
                        "ktext": "Name:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "FreePos_new"
                    },
                },
            },
            "ArgsSep":{
                "Text": "Argument",
                "Command":None,
                "Content":{
                    "pos": {
                        "ktext": "pos:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "entry",
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
                "Text": "Basic Information",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "Type:",
                        "tooltip":None,
                        "dtext": "help",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "PosGrid"
                    },
                    "Name": {
                        "ktext": "Name:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "PosGrid_new"
                    },
                }
            },
            "ArgsSep":{
                "Text": "Argument",
                "Command":None,
                "Content":{
                    "pos": {
                        "ktext": "start:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "end": {
                        "ktext": "end:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "end",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(1,1)"
                    },
                    "x_step": {
                        "ktext": "x_steps:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "x_step",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 0
                    },
                    "y_step": {
                        "ktext": "y_steps:",
                        "tooltip":None,
                        "dtext": "(digit)",
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
        "BezierCurve":{
            "InfoSep":{
                "Text": "Basic Information",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "Type:",
                        "tooltip":None,
                        "dtext": "help",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "BezierCurve"
                    },
                    "Name": {
                        "ktext": "Name:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "BezierCurve_new"
                    },
                }
            },
            "StartSep":{
                "Text": "Start Point",
                "Command":None,
                "Content":{
                    "pos": {
                        "ktext": "start:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                }
            },
            "AnchorSep-%d":{
                "Text": "Anchor-%d",
                "Command":{
                    "type":'add_sep',
                    "key":"anchor_%d"
                },
                "Content":{
                    "control_left_%d": {
                        "ktext": "L-control:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "control_left",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "control_right_%d": {
                        "ktext": "R-control:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "control_right",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "anchor_%d": {
                        "ktext": "anchor:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "anchor",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "frame_point_%d": {
                        "ktext": "keyframe:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "frame_point",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": "30"
                    },
                    "speed_formula_%d": {
                        "ktext": "formula:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "speed_formula",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'linear'"
                    },
                }
            },
        },
        "BezierCurve.args":{
            "type"          : "type",
            "pos"           : "pos",
            "control_left"  : "control_left_%d",
            "control_right" : "control_right_%d",
            "anchor"        : "anchor_%d",
            "frame_point"   : "frame_point_%d",
            "speed_formula" : "speed_formula_%d"
        },
        "Text":{
            "InfoSep":{
                "Text": "Basic Information",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "Type:",
                        "tooltip":None,
                        "dtext": "help",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "Text"
                    },
                    "Name": {
                        "ktext": "Name:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "Text_new"
                    },
                    "label_color": {
                        "ktext": "label_color:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "FontSep":{
                "Text": "Font",
                "Command":None,
                "Content":{
                    "fontfile": {
                        "ktext": "fontpath:",
                        "tooltip":None,
                        "dtext": "browse",
                        "ditem": "button",
                        "valuekey": "fontfile",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "'./assets/SourceHanSansCN-Regular.otf'"
                    },
                    "line_limit": {
                        "ktext": "line_limit:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "line_limit",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 20
                    }
                }
            },
            "StyleSep":{
                "Text": "Style",
                "Command":None,
                "Content":{
                    "fontsize": {
                        "ktext": "size:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "fontsize",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 40
                    },
                    "color": {
                        "ktext": "color:",
                        "tooltip":None,
                        "dtext": "select",
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
                "Text": "Basic Information",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "Type:",
                        "tooltip":None,
                        "dtext": "help",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "StrokeText"
                    },
                    "Name": {
                        "ktext": "Name:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "StrokeText_new"
                    },
                    "label_color": {
                        "ktext": "label_color:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "FontSep":{
                "Text": "Font",
                "Command":None,
                "Content":{
                    "fontfile": {
                        "ktext": "fontpath:",
                        "tooltip":None,
                        "dtext": "browse",
                        "ditem": "button",
                        "valuekey": "fontfile",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "'./assets/SourceHanSansCN-Regular.otf'"
                    },
                    "line_limit": {
                        "ktext": "line_limit:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "line_limit",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 20
                    },
                }
            },
            "StyleSep":{
                "Text": "Font Style",
                "Command":None,
                "Content":{
                    "fontsize": {
                        "ktext": "size:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "fontsize",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 40
                    },
                    "color": {
                        "ktext": "color:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "color",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0,0,255)"
                    },
                }
            },
            "StrokeSep":{
                "Text": "Stroke Style",
                "Command":None,
                "Content":{
                    "edge_color": {
                        "ktext": "color:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "edge_color",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(255,255,255,255)"
                    },
                    "edge_width": {
                        "ktext": "width:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "edge_width",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 1
                    },
                    "projection": {
                        "ktext": "projection:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "projection",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'C'"
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
                "Text": "Basic Information",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "Type:",
                        "tooltip":None,
                        "dtext": "help",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "RichText"
                    },
                    "Name": {
                        "ktext": "Name:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "RichText_new"
                    },
                    "label_color": {
                        "ktext": "label_color:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "FontSep":{
                "Text": "Font",
                "Command":None,
                "Content":{
                    "fontfile": {
                        "ktext": "fontpath:",
                        "tooltip":None,
                        "dtext": "browse",
                        "ditem": "button",
                        "valuekey": "fontfile",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "'./assets/SourceHanSansCN-Regular.otf'"
                    },
                    "line_limit": {
                        "ktext": "line_limit:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "line_limit",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 20
                    }
                }
            },
            "StyleSep":{
                "Text": "Style",
                "Command":None,
                "Content":{
                    "fontsize": {
                        "ktext": "size:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "fontsize",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 40
                    },
                    "color": {
                        "ktext": "color:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "color",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0,0,255)"
                    },
                    "scale": {
                        "ktext": "icon_scale：",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "scale",
                        "vitem": "spine",
                        "vtype": "float",
                        "default": 1.0
                    },
                }
            },
            "IconifySep-%d":{
                "Text": "Iconify-%d",
                "Command":{
                    "type":'add_sep',
                    "key":"sub_key_%d"
                },
                "Content":{
                    "sub_key_%d":{
                        "ktext": "keyword:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "sub_key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "'Key%d'"
                    },
                    "sub_icon_%d":{
                        "ktext": "icon_path:",
                        "tooltip":None,
                        "dtext": "browse",
                        "ditem": "button",
                        "valuekey": "sub_icon",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "'./assets/icon.png'"
                    }
                }
            }
        },
        "RichText.args":{
            "type"          : "type",
            "fontfile"      : "fontfile",
            "fontsize"      : "fontsize",
            "color"         : "color",
            "line_limit"    : "line_limit",
            "scale"         : "scale",
            "sub_key"       : "sub_key_%d",
            "sub_icon"      : "sub_icon_%d",
            "label_color"   : "label_color",
        },
        "HPLabel":{
            "InfoSep":{
                "Text": "Basic Information",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "Type:",
                        "tooltip":None,
                        "dtext": "help",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "HPLabel"
                    },
                    "Name": {
                        "ktext": "Name:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "HPLabel_new"
                    },
                    "label_color": {
                        "ktext": "label_color:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "FontSep":{
                "Text": "Font",
                "Command":None,
                "Content":{
                    "fontfile": {
                        "ktext": "fontpath:",
                        "tooltip":None,
                        "dtext": "browse",
                        "ditem": "button",
                        "valuekey": "fontfile",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "'./assets/SourceHanSansCN-Regular.otf'"
                    },
                    "marker": {
                        "ktext": "marker:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "marker",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "'A/B'"
                    },
                    "align": {
                        "ktext": "align:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "align",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'left'"
                    },
                }
            },
            "StyleSep":{
                "Text": "Font Style",
                "Command":None,
                "Content":{
                    "fontsize": {
                        "ktext": "size:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "fontsize",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 40
                    },
                    "color": {
                        "ktext": "color:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "color",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0,0,255)"
                    },
                }
            },
            "ImageSep":{
                "Text": "Hitpoint Image",
                "Command":None,
                "Content":{
                    "fg_path": {
                        "ktext": "fg_path:",
                        "tooltip":None,
                        "dtext": "browse",
                        "ditem": "button",
                        "valuekey": "fg_path",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "'./assets/heart.png'"
                    },
                    "bg_path": {
                        "ktext": "bg_path:",
                        "tooltip":None,
                        "dtext": "browse",
                        "ditem": "button",
                        "valuekey": "bg_path",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "'./assets/heart_shape.png'"
                    },
                }
            },
            "BarSep":{
                "Text": "Hitpoint Style",
                "Command":None,
                "Content":{
                    "width": {
                        "ktext": "width:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "width",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 0
                    },
                    "repeat": {
                        "ktext": "unit:",
                        "tooltip":None,
                        "dtext": "(digit)",
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
                "Text": "Basic Information",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "Type:",
                        "tooltip":None,
                        "dtext": "help",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "Bubble"
                    },
                    "Name": {
                        "ktext": "Name:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "Bubble_new"
                    },
                    "label_color": {
                        "ktext": "label_color:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "ImageSep":{
                "Text": "Image",
                "Command":None,
                "Content":{
                    "filepath": {
                        "ktext": "filepath:",
                        "tooltip":None,
                        "dtext": "browse",
                        "ditem": "button",
                        "valuekey": "filepath",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "None"
                    },
                    "pos": {
                        "ktext": "pos:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "scale": {
                        "ktext": "scale:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "scale",
                        "vitem": "spine",
                        "vtype": "float",
                        "default": 1.0
                    },
                }
            },
            "MainSep":{
                "Text": "Main Text",
                "Command":None,
                "Content":{
                    "Main_Text": {
                        "ktext": "text:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "Main_Text",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "Text()"
                    },
                    "mt_pos": {
                        "ktext": "pos:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "mt_pos",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "mt_rotate": {
                        "ktext": "rotate:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "mt_rotate",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 0
                    },
                    "align": {
                        "ktext": "horz_align:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "align",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'left'"
                    },
                    "vertical_align": {
                        "ktext": "vert_align:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "vertical_align",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'top'"
                    },
                    "line_distance": {
                        "ktext": "line_distance:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "line_distance",
                        "vitem": "spine",
                        "vtype": "float",
                        "default": 1.5
                    },
                    "line_num_est": {
                        "ktext": "line_num:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "line_num_est",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 4
                    },
                }
            },
            "HeadSep":{
                "Text": "Header Text",
                "Command":None,
                "Content":{
                    "Header_Text": {
                        "ktext": "text:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "Header_Text",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "None"
                    },
                    "ht_pos": {
                        "ktext": "pos:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "ht_pos",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "ht_rotate": {
                        "ktext": "rotate:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "ht_rotate",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": "0"
                    },
                    "head_align": {
                        "ktext": "align:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "head_align",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'left'"
                    },
                    "ht_target": {
                        "ktext": "target:",
                        "tooltip":None,
                        "dtext": "(select)",
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
                "Text": "Basic Information",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "Type:",
                        "tooltip":None,
                        "dtext": "help",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "Balloon"
                    },
                        "Name": {
                        "ktext": "Name:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "Balloon_new"
                    },
                    "label_color": {
                        "ktext": "label_color:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "ImageSep":{
                "Text": "Image",
                "Command":None,
                "Content":{
                    "filepath": {
                        "ktext": "filepath:",
                        "tooltip":None,
                        "dtext": "browse",
                        "ditem": "button",
                        "valuekey": "filepath",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "None"
                    },
                    "pos": {
                        "ktext": "pos:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "scale": {
                        "ktext": "scale:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "scale",
                        "vitem": "spine",
                        "vtype": "float",
                        "default": 1
                    },
                }
            },
            "MainSep":{
                "Text": "Main Text",
                "Command":None,
                "Content":{
                    "Main_Text": {
                        "ktext": "text:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "Main_Text",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "Text()"
                    },
                    "mt_pos": {
                        "ktext": "pos:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "mt_pos",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "mt_rotate": {
                        "ktext": "rotate:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "mt_rotate",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 0
                    },
                    "align": {
                        "ktext": "horz_align:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "align",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'left'"
                    },
                    "vertical_align": {
                        "ktext": "vert_align:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "vertical_align",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'top'"
                    },
                    "line_distance": {
                        "ktext": "line_distance:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "line_distance",
                        "vitem": "spine",
                        "vtype": "float",
                        "default": 1.5
                    },
                    "line_num_est": {
                        "ktext": "line_num:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "line_num_est",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 4
                    },
                }
            },
            "HeadSep-%d":{
                "Text": "HeaderText-%d",
                "Command":{
                    "type":'add_sep',
                    "key":"Header_Text_%d"
                },
                "Content":{
                    "Header_Text_%d": {
                        "ktext": "text:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "Header_Text",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "Text()"
                    },
                    "ht_pos_%d": {
                        "ktext": "pos:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "ht_pos",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "ht_rotate_%d": {
                        "ktext": "rotate:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "ht_rotate",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": "0"
                    },
                    "head_align_%d": {
                        "ktext": "align:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "head_align",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'left'"
                    },
                    "ht_target_%d": {
                        "ktext": "target:",
                        "tooltip":None,
                        "dtext": "(select)",
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
                "Text": "Basic Information",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "Type:",
                        "tooltip":None,
                        "dtext": "help",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "DynamicBubble"
                    },
                    "Name": {
                        "ktext": "Name:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "DynamicBubble_new"
                    },
                    "label_color": {
                        "ktext": "label_color:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "ImageSep":{
                "Text": "Image",
                "Command":None,
                "Content":{
                    "filepath": {
                        "ktext": "filepath:",
                        "tooltip":None,
                        "dtext": "browse",
                        "ditem": "button",
                        "valuekey": "filepath",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "None"
                    },
                    "pos": {
                        "ktext": "pos:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "scale": {
                        "ktext": "scale:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "scale",
                        "vitem": "spine",
                        "vtype": "float",
                        "default": 1.0
                    },
                }
            },
            "DynamicSep":{
                "Text": "Adaption",
                "Command":None,
                "Content":{
                    "fill_mode": {
                        "ktext": "fill_mode:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "fill_mode",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'stretch'"
                    },
                    "fit_axis": {
                        "ktext": "fit_axis:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "fit_axis",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'free'"
                    },
                }
            },
            "MainSep":{
                "Text": "Main Text",
                "Command":None,
                "Content":{
                    "Main_Text": {
                        "ktext": "text:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "Main_Text",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "Text()"
                    },
                    "mt_pos": {
                        "ktext": "start:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "mt_pos",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "mt_end": {
                        "ktext": "end:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "mt_end",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "line_distance": {
                        "ktext": "line_distance:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "line_distance",
                        "vitem": "spine",
                        "vtype": "float",
                        "default": 1.5
                    },
                }
            },
            "HeadSep":{
                "Text": "Header Text",
                "Command":None,
                "Content":{
                    "Header_Text": {
                        "ktext": "text:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "Header_Text",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "None"
                    },
                    "ht_pos": {
                        "ktext": "pos:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "ht_pos",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "ht_target": {
                        "ktext": "target:",
                        "tooltip":None,
                        "dtext": "(select)",
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
                "Text": "Basic Information",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "Type:",
                        "tooltip":None,
                        "dtext": "help",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "ChatWindow"
                    },
                    "Name": {
                        "ktext": "Name:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "ChatWindow_new"
                    },
                    "label_color": {
                        "ktext": "label_color:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "ImageSep":{
                "Text": "Image",
                "Command":None,
                "Content":{
                    "filepath": {
                        "ktext": "filepath:",
                        "tooltip":None,
                        "dtext": "browse",
                        "ditem": "button",
                        "valuekey": "filepath",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "None"
                    },
                    "pos": {
                        "ktext": "pos:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "scale": {
                        "ktext": "scale:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "scale",
                        "vitem": "spine",
                        "vtype": "float",
                        "default": 1
                    },
                }
            },
            "AreaSep":{
                "Text": "Scroll Area",
                "Command":None,
                "Content":{
                    "sub_pos": {
                        "ktext": "start:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "sub_pos",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "Text()"
                    },
                    "sub_end": {
                        "ktext": "end:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "sub_end",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "sub_distance": {
                        "ktext": "distance:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "sub_distance",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 50
                    },
                }
            },
            "HeadSep":{
                "Text": "Avatar Position",
                "Command":None,
                "Content":{
                    "am_left": {
                        "ktext": "left_border:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "am_left",
                        "vitem": "entry",
                        "vtype": "int",
                        "default": 0
                    },
                    "am_right": {
                        "ktext": "right_border:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "am_right",
                        "vitem": "entry",
                        "vtype": "int",
                        "default": 0
                    },
                }
            },
            "SubSep-%d":{
                "Text": "SubBubble-%d",
                "Command":{
                    "type":'add_sep',
                    "key":"sub_key_%d"
                },
                "Content":{
                    "sub_key_%d": {
                        "ktext": "keyword:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "sub_key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "'Key%d'"
                    },
                    "sub_Bubble_%d": {
                        "ktext": "bubble:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "sub_Bubble",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "Bubble()"
                    },
                    "sub_Anime_%d": {
                        "ktext": "avatar:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "sub_Anime",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "None"
                    },
                    "sub_align_%d": {
                        "ktext": "align:",
                        "tooltip":None,
                        "dtext": "(select)",
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
                "Text": "Basic Information",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "Type:",
                        "tooltip":None,
                        "dtext": "help",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "Animation"
                    },
                    "Name": {
                        "ktext": "Name:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "Animation_new"
                    },
                    "label_color": {
                        "ktext": "label_color:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "ImageSep":{
                "Text": "Image",
                "Command":None,
                "Content":{
                    "filepath": {
                        "ktext": "filepath:",
                        "tooltip":None,
                        "dtext": "browse",
                        "ditem": "button",
                        "valuekey": "filepath",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": ""
                    },
                    "pos": {
                        "ktext": "pos:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "scale": {
                        "ktext": "scale:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "scale",
                        "vitem": "spine",
                        "vtype": "float",
                        "default": 1.0
                    },
                }
            },
            "AnimeSep":{
                "Text": "Anime",
                "Command":None,
                "Content":{
                    "tick": {
                        "ktext": "tick_rate:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "tick",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 1
                    },
                    "loop": {
                        "ktext": "loop:",
                        "tooltip":None,
                        "dtext": "(select)",
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
        "Sprite":{
            "InfoSep":{
                "Text": "Basic Information",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "Type:",
                        "tooltip":None,
                        "dtext": "help",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "Sprite"
                    },
                    "Name": {
                        "ktext": "Name:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "Sprite_new"
                    },
                    "label_color": {
                        "ktext": "label_color:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "ImageSep":{
                "Text": "Image",
                "Command":None,
                "Content":{
                    "filepath": {
                        "ktext": "face_anime:",
                        "tooltip":None,
                        "dtext": "browse",
                        "ditem": "button",
                        "valuekey": "filepath",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": ""
                    },
                    "pos": {
                        "ktext": "pos:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "scale": {
                        "ktext": "scale:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "scale",
                        "vitem": "spine",
                        "vtype": "float",
                        "default": 1.0
                    },
                    "tick": {
                        "ktext": "tick_rate:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "tick",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 1
                    }
                }
            },
            "AnimeSep":{
                "Text": "Anime",
                "Command":None,
                "Content":{
                    "mouthpath": {
                        "ktext": "mouth_anime:",
                        "tooltip":None,
                        "dtext": "browse",
                        "ditem": "button",
                        "valuekey": "mouthpath",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "None"
                    },
                    "eyepath": {
                        "ktext": "blink_anime:",
                        "tooltip":None,
                        "dtext": "browse",
                        "ditem": "button",
                        "valuekey": "eyepath",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "None"
                    },
                    "blink_mean": {
                        "ktext": "blink_mean:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "blink_mean",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 4
                    },
                    "blink_std": {
                        "ktext": "blink_std:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "blink_std",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 1
                    },
                }
            },
        },
        "Sprite.args":{
            "type"          : "type",
            "filepath"      : "filepath",
            "eyepath"       : "eyepath",
            "mouthpath"     : "mouthpath",
            "scale"         : "scale",
            "pos"           : "pos",
            "tick"          : "tick",
            "blink_mean"    : "blink_mean",
            "blink_std"     : "blink_std",
            "label_color"   : "label_color"
        },
        "Background":{
            "InfoSep":{
                "Text": "Basic Information",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "Type:",
                        "tooltip":None,
                        "dtext": "help",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "Background"
                    },
                    "Name": {
                        "ktext": "Name:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "Background_new"
                    },
                    "label_color": {
                        "ktext": "label_color:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Lavender'"
                    },
                }
            },
            "ImageSep":{
                "Text": "Image",
                "Command":None,
                "Content":{
                    "filepath": {
                        "ktext": "filepath:",
                        "tooltip":None,
                        "dtext": "browse",
                        "ditem": "button",
                        "valuekey": "filepath",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "'black'"
                    },
                    "pos": {
                        "ktext": "pos:",
                        "tooltip":None,
                        "dtext": "select",
                        "ditem": "button",
                        "valuekey": "pos",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "(0,0)"
                    },
                    "scale": {
                        "ktext": "scale:",
                        "tooltip":None,
                        "dtext": "(digit)",
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
                "Text": "Basic Information",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "Type:",
                        "tooltip":None,
                        "dtext": "help",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "Audio"
                    },
                    "Name": {
                        "ktext": "Name:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "Audio_new"
                    },
                    "label_color": {
                        "ktext": "label_color:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Caribbean'"
                    },
                }
            },
            "AudioSep":{
                "Text":"Audio",
                "Command":None,
                "Content":{
                    "filepath": {
                        "ktext": "filepath:",
                        "tooltip":None,
                        "dtext": "browse",
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
                "Text": "Basic Information",
                "Command":None,
                "Content":{
                    "type": {
                        "ktext": "Type:",
                        "tooltip":None,
                        "dtext": "help",
                        "ditem": "button",
                        "valuekey": "type",
                        "vitem": "label",
                        "vtype": "str",
                        "default": "BGM"
                    },
                    "Name": {
                        "ktext": "Name:",
                        "tooltip":None,
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "$key",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": "BGM_new"
                    },
                    "label_color": {
                        "ktext": "label_color:",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "label_color",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": "'Caribbean'"
                    },
                }
            },
            "AudioSep":{
                "Text": "Audio",
                "Command":None,
                "Content":{
                    "filepath": {
                        "ktext": "filepath:",
                        "tooltip":None,
                        "dtext": "browse",
                        "ditem": "button",
                        "valuekey": "filepath",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": ""
                    },
                    "volume": {
                        "ktext": "volume:",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "volume",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 100
                    },
                    "loop": {
                        "ktext": "loop:",
                        "tooltip":None,
                        "dtext": "(select)",
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
    # RplGenLog: Abandoned
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
                        "dtext": "(select)",
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
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "target.name",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": ""
                    },
                    "subtype":{
                        "ktext": "差分：",
                        "tooltip":None,
                        "dtext": "(select)",
                        "ditem": "label",
                        "valuekey": "target.subtype",
                        "vitem": "combox",
                        "vtype": "str",
                        "default": None
                    },
                    "column":{
                        "ktext": "角色表列：",
                        "tooltip":None,
                        "dtext": "(select)",
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
                        "dtext": "(input)",
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
                        "dtext": "browse",
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
                        "dtext": "(select)",
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
                        "dtext": "(input)",
                        "ditem": "label",
                        "valuekey": "content",
                        "vitem": "entry",
                        "vtype": "str",
                        "default": ""
                    },
                    "hp_max":{
                        "ktext": "HP上限：",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "hp_max",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 0
                    },
                    "hp_begin":{
                        "ktext": "初始HP：",
                        "tooltip":None,
                        "dtext": "(digit)",
                        "ditem": "label",
                        "valuekey": "hp_begin",
                        "vitem": "spine",
                        "vtype": "int",
                        "default": 0
                    },
                    "hp_end":{
                        "ktext": "结束HP：",
                        "tooltip":None,
                        "dtext": "(digit)",
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
    "AppearanceSep":{
        "Text": "Appearance",
        "Command":None,
        "Content":{
            "System.lang":{
                "ktext": "language",
                "tooltip":"Language of UI. Need restarted for take effect.",
                "dtext": "(select)",
                "ditem": "label",
                "valuekey": "System.lang",
                "vitem": "combox",
                "vtype": "str",
                "default": 'en'
            },
            "System.theme":{
                "ktext": "Theme",
                "tooltip": "Color theme of UI, two options: dark, light. Need restarted for take effect.",
                "dtext": "(select)",
                "ditem": "label",
                "valuekey": "System.theme",
                "vitem": "combox",
                "vtype": "str",
                "default": 'rplgenlight'
            },
            "System.editer_fontsize":{
                "ktext": "Editor Fontsize",
                "tooltip": "Font size in RGL Editor, need to restart rgl page for take effect.",
                "dtext": "(digit)",
                "ditem": "label",
                "valuekey": "System.editer_fontsize",
                "vitem": "spine",
                "vtype": "int",
                "default": 12
            },
            "System.editer_colorschemes":{
                "ktext": "Editor Colorschemes",
                "tooltip": "Color scheme for the RGL Editor, need to restart rgl page for take effect.",
                "dtext": "(select)",
                "ditem": "label",
                "valuekey": "System.editer_colorschemes",
                "vitem": "combox",
                "vtype": "str",
                "default": "monokai"
            },
            "System.terminal_fontsize":{
                "ktext": "Terminal Fontsize",
                "tooltip": "Font size in terminal view. Need restarted for take effect.",
                "dtext": "(digit)",
                "ditem": "label",
                "valuekey": "System.terminal_fontsize",
                "vitem": "spine",
                "vtype": "int",
                "default": 14
            },
            "System.performance_mode":{
                "ktext": "Performance Mode",
                "tooltip": "Omit the thumbnails of medias to avoid lagging when there is large number of medias.",
                "dtext": "(select)",
                "ditem": "label",
                "valuekey": "System.performance_mode",
                "vitem": "combox",
                "vtype": "bool",
                "default": False
            },
            "System.workshop_path":{
                "ktext": "Steam Workshop Path",
                "tooltip": "Path to steam workshop path, typically a folder named 2550090.",
                "dtext": "browse",
                "ditem": "button",
                "valuekey": "System.workshop_path",
                "vitem": "entry",
                "vtype": "str",
                "default": "../../workshop/content/2550090/"
            },
        }
    },       
    "MediaSep":{
        "Text": "Bulitin-Anime",
        "Command":None,
        "Content":{
            "BIA.font":{
                "ktext": "BIA Font",
                "tooltip":"Font used in Dice and Hitpoint Anine.",
                "dtext": "browse",
                "ditem": "button",
                "valuekey": "BIA.font",
                "vitem": "entry",
                "vtype": "str",
                "default": './assets/SourceHanSerifSC-Heavy.otf'
            },
            "BIA.font_size":{
                "ktext": "BIA Fontsize",
                "tooltip":"The multiplier for font size in BIA, The actual size is equal to this_value X screenwidth.",
                "dtext": "(digit)",
                "ditem": "label",
                "valuekey": "BIA.font_size",
                "vitem": "entry",
                "vtype": "float",
                "default": 0.0521
            },
            "BIA.dice_mode":{
                "ktext": "Dice Mode",
                "tooltip":"In Dice anime, COC success: roll<=target; DND success: roll>=target; ruleless: no judgment.",
                "dtext": "(select)",
                "ditem": "label",
                "valuekey": "BIA.dice_mode",
                "vitem": "combox",
                "vtype": "str",
                "default": 'COC'
            },
            "BIA.dice_threshold":{
                "ktext": "Dice Threshold",
                "tooltip":"In Dice anime，extreme outcomes is designated as critical. Specified a ratio for critical.",
                "dtext": "(input)",
                "ditem": "label",
                "valuekey": "BIA.dice_threshold",
                "vitem": "entry",
                "vtype": "float",
                "default": 0.05
            },
            "BIA.heart_pic":{
                "ktext": "Hitpoint Foreground",
                "tooltip":"In HP anime, this image represents remaining HP.",
                "dtext": "browse",
                "ditem": "button",
                "valuekey": "BIA.heart_pic",
                "vitem": "entry",
                "vtype": "str",
                "default": './assets/heart.png'
            },
            "BIA.heart_shape":{
                "ktext": "Hitpoint Background",
                "tooltip":"In HP anime, this image represents the max of HP.",
                "dtext": "browse",
                "ditem": "button",
                "valuekey": "BIA.heart_shape",
                "vitem": "entry",
                "vtype": "str",
                "default": './assets/heart_shape.png'
            },
            "BIA.heart_distance":{
                "ktext": "Heart Distance",
                "tooltip":"In HP anime, the multiplier for the distance between hearts.",
                "dtext": "(digit)",
                "ditem": "label",
                "valuekey": "BIA.heart_distance",
                "vitem": "entry",
                "vtype": "float",
                "default": 0.026
            },
        }
    },
    "EditSep":{
        "Text": "Editing",
        "Command":None,
        "Content":{
            "Edit.auto_periods":{
                "ktext": "Auto Punctuation",
                "tooltip":"When splitting dialogue lines, automatically correct punctuation at the end of sentences?",
                "dtext": "(select)",
                "ditem": "label",
                "valuekey": "Edit.auto_periods",
                "vitem": "combox",
                "vtype": "bool",
                "default": False
            },
            "Edit.import_mode":{
                "ktext": "Import Mode",
                "tooltip":"How to handle duplicate name when importing scripts?",
                "dtext": "(select)",
                "ditem": "label",
                "valuekey": "Edit.import_mode",
                "vitem": "combox",
                "vtype": "str",
                "default": 'add'
            },
            'Edit.auto_convert':{
                "ktext": "Convert Audio",
                "tooltip":"Whether convert unsupported audio format to appropriate format when importing?",
                "dtext": "(select)",
                "ditem": "label",
                "valuekey": "Edit.auto_convert",
                "vitem": "combox",
                "vtype": "str",
                "default": 'ask'
            },
            'Edit.asterisk_import':{
                "ktext": "Asterisk Import",
                "tooltip":"In RGL page, if import a audio by tab menu, should the audio be processed as asterisk?",
                "dtext": "(select)",
                "ditem": "label",
                "valuekey": "Edit.asterisk_import",
                "vitem": "combox",
                "vtype": "bool",
                "default": True
            },
            'Edit.rename_boardcast':{
                "ktext": "Rename Boardcast",
                "tooltip":"When renameing a object, should the the changes be synchronized to all references?",
                "dtext": "(select)",
                "ditem": "label",
                "valuekey": "Edit.rename_boardcast",
                "vitem": "combox",
                "vtype": "str",
                "default": 'ask'
            },
            'Edit.masked_symbol':{
                "ktext": "Ignored Symbol",
                "tooltip":"Ignore the symbols when synthesizing speech to avoid abnormal punctuation.",
                "dtext": "(input)",
                "ditem": "label",
                "valuekey": "Edit.masked_symbol",
                "vitem": "entry",
                "vtype": "str",
                "default": ""
            }
        }
    },
    "PreviewSep":{
        "Text": "Preview",
        "Command":None,
        "Content":{
            "Preview.progress_bar_style":{
                "ktext": "Progress Bar Style",
                "tooltip":"Choose color style of progress bar in preview player.",
                "dtext": "(select)",
                "ditem": "label",
                "valuekey": "Preview.progress_bar_style",
                "vitem": "combox",
                "vtype": "str",
                "default": 'color'
            },
            "Preview.framerate_counter":{
                "ktext": "Framerate Counter",
                "tooltip":"Whether display fps counter at top left in preview player.",
                "dtext": "(select)",
                "ditem": "label",
                "valuekey": "Preview.framerate_counter",
                "vitem": "combox",
                "vtype": "bool",
                "default": True
            },
        }
    },
    "ExportSep":{
        "Text": "Export",
        "Command":None,
        "Content":{
            "Export.force_split_clip":{
                "ktext": "Force Split Clips",
                "tooltip":"When exporting as PR project, should the clips be split at every breakpoint?",
                "dtext": "(select)",
                "ditem": "label",
                "valuekey": "Export.force_split_clip",
                "vitem": "combox",
                "vtype": "bool",
                "default": False
            },
            "Export.export_srt":{
                "ktext": "Export SRT Subtitle",
                "tooltip":"When exporting as PR project, should all speech content be exported as SRT subtitles?",
                "dtext": "(select)",
                "ditem": "label",
                "valuekey": "Export.export_srt",
                "vitem": "combox",
                "vtype": "bool",
                "default": False
            },
            "Export.crf":{
                "ktext": "Vidio Quality CRF",
                "tooltip":"The quality of the exported MP4 video, can range from 0 to 51, smaller value means to higher quality",
                "dtext": "(select)",
                "ditem": "label",
                "valuekey": "Export.crf",
                "vitem": "spine",
                "vtype": "int",
                "default": 24
            },
            "Export.hwaccels":{
                "ktext": "Hardware Accelerate",
                "tooltip":"Use GPU to accelerate exporting? Note: NVIDIA GPU with CUDA support only.",
                "dtext": "(select)",
                "ditem": "label",
                "valuekey": "Export.hwaccels",
                "vitem": "combox",
                "vtype": "bool",
                "default": False
            },
            "Export.alpha_export":{
                "ktext": "Alpha Export",
                "tooltip":"Additionally export the alpha channel to a mask video?",
                "dtext": "(select)",
                "ditem": "label",
                "valuekey": "Export.alpha_export",
                "vitem": "combox",
                "vtype": "bool",
                "default": False
            },
        }
    },
    "KeySep":{
        "Text": "Speech Synthesis Key",
        "Command":None,
        "Content":{
            "TTSKey.UseBulitInKeys": {
                "ktext": "Use BulitIn Keys",
                "tooltip":"If disable, TTS Service will uses the following user-entered key instead of the built-in key.",
                "dtext": "(select)",
                "ditem": "label",
                "valuekey": "TTSKey.UseBulitInKeys",
                "vitem": "combox",
                "vtype": "bool",
                "default": True
            },
            "Aliyun.accesskey": {
                "ktext": "Aliyun-AccessKey",
                "tooltip":"A string length 24, obtainable in AccessKey Management page.",
                "dtext": "(input)",
                "ditem": "label",
                "valuekey": "Aliyun.accesskey",
                "vitem": "entry",
                "vtype": "str",
                "default": "Your_AccessKey"
            },
            "Aliyun.accesskey_secret": {
                "ktext": "Aliyun-AccessKeySecret",
                "tooltip":"A string length 30, obtainable in AccessKey Management page.",
                "dtext": "(input)",
                "ditem": "label",
                "valuekey": "Aliyun.accesskey_secret",
                "vitem": "entry",
                "vtype": "str",
                "default": "Your_AccessKey_Secret"
            },
            "Aliyun.appkey": {
                "ktext": "Aliyun-AppKey",
                "tooltip":"A string length 16, Obtainable in Application Management page, need to new a app.",
                "dtext": "(input)",
                "ditem": "label",
                "valuekey": "Aliyun.appkey",
                "vitem": "entry",
                "vtype": "str",
                "default": "Your_AppKey"
            },
            "Azure.azurekey": {
                "ktext": "Azure-Key",
                "tooltip": "A string length 32, obtain in [Key and Endpoint] page.",
                "dtext": "(input)",
                "ditem": "label",
                "valuekey": "Azure.azurekey",
                "vitem": "entry",
                "vtype": "str",
                "default": "Your_AzureKey"
            },
            "Azure.service_region": {
                "ktext": "Azure-ServiceRegion",
                "tooltip":"The service region selected when creating the speech service.",
                "dtext": "(input)",
                "ditem": "label",
                "valuekey": "Azure.service_region",
                "vitem": "entry",
                "vtype": "str",
                "default": "eastasia"
            },
            "Tencent.appid": {
                "ktext": "Tencent-AppId",
                "tooltip":"A digit string length 10, obtained from Tencent Cloud Permission Management.",
                "dtext": "(input)",
                "ditem": "label",
                "valuekey": "Tencent.appid",
                "vitem": "entry",
                "vtype": "str",
                "default": "0"
            },
            "Tencent.secretid": {
                "ktext": "Tencent-SecretId",
                "tooltip":"A string length 36, obtained from Tencent Cloud Permission Management.",
                "dtext": "(input)",
                "ditem": "label",
                "valuekey": "Tencent.secretid",
                "vitem": "entry",
                "vtype": "str",
                "default": "Your_SecretID"
            },
            "Tencent.secretkey": {
                "ktext": "Tencent-SecretKey",
                "tooltip":"A string length 32, obtained from Tencent Cloud Permission Management.",
                "dtext": "(input)",
                "ditem": "label",
                "valuekey": "Tencent.secretkey",
                "vitem": "entry",
                "vtype": "str",
                "default": "Your_SecretKey"
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
                "dtext": "browse",
                "ditem": "button",
                "valuekey": None,
                "vitem": "entry",
                "vtype": "str",
                "default": ""
            },
            "chartab": {
                "ktext": "角色配置：",
                "tooltip":"角色配置表，是一个tsv表格或者xlsx表格",
                "dtext": "browse",
                "ditem": "button",
                "valuekey": None,
                "vitem": "entry",
                "vtype": "str",
                "default": ""
            },
            "logfile": {
                "ktext": "剧本文件：",
                "tooltip":"也称log文件，是一个rgl文本文件",
                "dtext": "browse",
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
                "dtext": "(digit)",
                "ditem": "label",
                "valuekey": None,
                "vitem": "entry",
                "vtype": "int",
                "default": 30
            },
            "zorder":{
                "ktext": "图层顺序：",
                "tooltip":None,
                "dtext": "(input)",
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
            "Text": "Project Info",
            "Command":None,
            "Content":{
                "proj_name":{
                    "ktext": "Name:",
                    "tooltip":"Name of project, need to be a valid file name.",
                    "dtext": "",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "str",
                    "default": "new_empty_project"
                },
                "proj_cover":{
                    "ktext": "Cover:",
                    "tooltip":"Select an image for project over.",
                    "dtext": "browse",
                    "ditem": "button",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "str",
                    "default": "None"
                },
                "save_pos":{
                    "ktext": "Path:",
                    "tooltip":"Path to save project files.",
                    "dtext": "browse",
                    "ditem": "button",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "str",
                    "default": ""
                },
            }
        },
        "VideoSep":{
            "Text": "Video Options",
            "Command":None,
            "Content":{
                "preset_video":{
                    "ktext": "Preset:",
                    "tooltip":None,
                    "dtext": "",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "combox",
                    "vtype": "str",
                    "default": "FHD-H (1920x1080, 30fps)"
                },
                "video_width":{
                    "ktext": "Width:",
                    "tooltip":"The width of the video canvas, measured in pixels.",
                    "dtext": "(even)",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "int",
                    "default": 1920
                },
                "video_height":{
                    "ktext": "Height",
                    "tooltip":"The height of the video canvas, measured in pixels.",
                    "dtext": "(even)",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "int",
                    "default": 1080
                },
                "frame_rate":{
                    "ktext": "FrameRate:",
                    "tooltip":"The frame rate of the video, measured in frames per second (fps).",
                    "dtext": "(int)",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "int",
                    "default": 30
                },
            }
        },
        "LayerSep":{
            "Text": "Layer Option",
            "Command":None,
            "Content":{
                "preset_layer":{
                    "ktext": "Preset:",
                    "tooltip":None,
                    "dtext": "",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "combox",
                    "vtype": "str",
                    "default": "Background->Animation->Bubble"
                },
                "layer_zorder":{
                    "ktext": "Order",
                    "tooltip":"Warning: This is a sensitive parameter, an incorrect value may cause program crashes. Please be cautious when modifying!",
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
            "Text": "Project Info",
            "Command":None,
            "Content":{
                "proj_name":{
                    "ktext": "Name:",
                    "tooltip":"Name of project, need to be a valid file name.",
                    "dtext": "",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "str",
                    "default": "new_intel_project"
                },
                "proj_cover":{
                    "ktext": "Cover:",
                    "tooltip":"Select an image for project over.",
                    "dtext": "browse",
                    "ditem": "button",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "str",
                    "default": "无"
                },
                "save_pos":{
                    "ktext": "Path:",
                    "tooltip":"Path to save project files.",
                    "dtext": "browse",
                    "ditem": "button",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "str",
                    "default": ""
                }
            }
        },
        "TpltSep":{
            "Text": "Style Template",
            "Command":None,
            "Content":{
                "template":{
                    "ktext": "Template:",
                    "tooltip":"Select a style template for intel project.", # ，访问创意工坊获取更多预设样式模板
                    "dtext": "workshop",
                    "ditem": "button",
                    "valuekey": None,
                    "vitem": "combox",
                    "vtype": "str",
                    "default": ""
                },
            }
        },
        "LogSep":{
            "Text": "Import Logs",
            "Command":None,
            "Content":{
                "textfile":{
                    "ktext": "file:",
                    "tooltip":"Script or TRPG log file for import.\nNote: Only support original text file, NO Word docs!",
                    "dtext": "browse",
                    "ditem": "button",
                    "valuekey": None,
                    "vitem": "entry",
                    "vtype": "str",
                    "default": ""
                },
                "section_break":{
                    "ktext": "auto_split:",
                    "tooltip":"Long texts will be split into multiple RGL page.\nNote: 0 means disable splitting, but may cause lagging when text is long.",
                    "dtext": "(select)",
                    "ditem": "label",
                    "valuekey": None,
                    "vitem": "combox",
                    "vtype": "int",
                    "default": 300
                },
            }
        }
    },
    'ImportTemplate':{
        "TpltSep":{
            "Text": "Style Template",
            "Command":None,
            "Content":{
                "template":{
                    "ktext": "Template:",
                    "tooltip":"Select a style template to import.", # ，访问创意工坊获取更多预设样式模板
                    "dtext": "workshop",
                    "ditem": "button",
                    "valuekey": None,
                    "vitem": "combox",
                    "vtype": "str",
                    "default": ""
                },
            }
        }
    }
}



PortalStruct = {
    "Friends":{
        "Text": "Friends",
        "Command":None,
        "Content":{
            "1": {
                "title": "SealDice",
                "icon":"./assets/portal/sealdice.jpg",
                "describe": "An open-source chatbot for TRPG.",
                "url": "https://sealdice.com",
            },
            "2": {
                "title": "活字引擎",
                "icon":"./assets/portal/hzyq.png",
                "describe": "Also try 活字引擎!",
                "url": "https://store.steampowered.com/app/2124470/_/",
            }
        }
    },
    "Contributors":{
        "Text": "Contributors",
        "Command":None,
        "Content":{
            "1": {
                "title": "淡淡的宣喧",
                "icon":"./assets/portal/dddxx.png",
                "describe": "The author of RplGen Studio.",
                "url": "https://space.bilibili.com/12108288",
            },
            "2": {
                "title": "憧憬少",
                "icon":"github",
                "describe": "The author of vscode extension for RplGen.",
                "url": "https://github.com/ChangingSelf",
            },
            "3": {
                "title": "谢安之",
                "icon":"./assets/portal/xaz.png",
                "describe": "The author of promotional video.",
                "url": "https://space.bilibili.com/1902789",
            },
            "4": {
                "title": "地球研究分部",
                "icon":"./assets/portal/dqyjy.jpg",
                "describe": "The author of the splash screen illustration.",
                "url": "https://space.bilibili.com/7963594",
            },
            "5": {
                "title": "需要思考",
                "icon":"./assets/portal/xysk.jpg",
                "describe": "The designer of Exception's portraits.",
                "url": "https://www.mihuashi.com/profiles/1127638",
            },
            "6": {
                "title": "Wee阿其曼",
                "icon":"bilibili",
                "describe": "A participant of icon design.",
                "url": "https://space.bilibili.com/15358072",
            },
            "7": {
                "title": "ScaqhCat",
                "icon":"./assets/portal/sqcat.jpg",
                "describe": "A participant of icon and UI design.",
                "url": "https://space.bilibili.com/13661674",
            },
            "8": {
                "title": "病原体桌",
                "icon":"./assets/portal/bytz.jpg",
                "describe": "A participant of poster graphic design.",
                "url": "https://space.bilibili.com/2005143149",
            },
            "9": {
                "title": "GUlili",
                "icon":"./assets/portal/gulili.jpg",
                "describe": "The designer steam library banner.",
                "url": "https://space.bilibili.com/4136036",
            },
        }
    },
    "OpenSources":{
        "Text": "OpenSources Dependency",
        "Command":None,
        "Content":{
            "1": {
                "title": "TRPG-Replay-Generator",
                "icon":"./assets/icon.png",
                "describe": "RplGen Studio opensource repository.",
                "url": "https://github.com/DanDDXuanX/TRPG-Replay-Generator",
            },
            "2": {
                "title": "pygame",
                "icon":"./assets/portal/pygame.png",
                "describe": "Game dev in python.",
                "url": "https://www.pygame.org/",
            },
            "3": {
                "title": "numpy",
                "icon":"./assets/portal/numpy.png",
                "describe": "Python scientific computing library.",
                "url": "https://numpy.org/",
            },
            "4": {
                "title": "pandas",
                "icon":"./assets/portal/pandas.png",
                "describe": "Python data table and analysis library.",
                "url": "https://pandas.pydata.org/",
            },
            "5": {
                "title": "pydub",
                "icon":"github",
                "describe": "Practical audio processing library.",
                "url": "https://github.com/jiaaro/pydub",
            },
            "6": {
                "title": "ttkbootstrap",
                "icon":"./assets/portal/ttkbootstrap.png",
                "describe": "A modern tkinter theme extension.",
                "url": "https://ttkbootstrap.readthedocs.io/",
            },
            "7": {
                "title": "ffmpeg",
                "icon":"./assets/portal/ffmpeg.png",
                "describe": "Cross-platform multimedia processing toolset.",
                "url": "https://ffmpeg.org/",
            },
            "8": {
                "title": "ffmpeg-python",
                "icon":"./assets/portal/ffmpeg-python.png",
                "describe": "Using ffmpeg in python.",
                "url": "https://github.com/kkroening/ffmpeg-python",
            },
            "9": {
                "title": "tkextrafont",
                "icon":"github",
                "describe": "Font extension in tkinter.",
                "url": "https://github.com/TkinterEP/python-tkextrafont",
            },
            "10": {
                "title": "chlorophyll",
                "icon":"github",
                "describe": "Text editor widget based on tkinter.",
                "url": "https://github.com/rdbende/chlorophyll",
            },
            "11": {
                "title": "pinyin",
                "icon":"github",
                "describe": "Translate Chinese into pinyin.",
                "url": "https://github.com/lxyu/pinyin",
            },
            "12": {
                "title": "pyttsx3",
                "icon":"github",
                "describe": "Offline speech synthesis library.",
                "url": "https://github.com/nateshmbhat/pyttsx3",
            },
            "13": {
                "title": "思源宋体",
                "icon":"./assets/portal/source-han-serif.png",
                "describe": "An open source serif Chinese font developed by Adobe and Google.",
                "url": "https://github.com/adobe-fonts/source-han-serif",
            },
            "14": {
                "title": "更纱黑体",
                "icon":"./assets/portal/Sarasa-Gothic.png",
                "describe": "More suitable fonts for text editors.",
                "url": "https://github.com/be5invis/Sarasa-Gothic",
            },
        },
    },
    "TTSService":{
        "Text": "TTS Services",
        "Command":None,
        "Content":{
            "1": {
                "title": "Alibaba Cloud",
                "icon":"./assets/portal/aliyun.png",
                "describe": "NLS",
                "url": "https://ai.aliyun.com/nls/tts",
            },
            "2": {
                "title": "Microsoft-Azure",
                "icon":"./assets/portal/azure.png",
                "describe": "Cognitive Speech service",
                "url": "https://azure.microsoft.com/zh-cn/products/ai-services/text-to-speech/",
            },
            "3": {
                "title": "Tencent Cloud",
                "icon":"./assets/portal/tencentcloud.png",
                "describe": "Text To Speech",
                "url": "https://cloud.tencent.com/product/tts",
            },
        },
    },
}
# 给Combobox使用的key，value映射关系
label_colors = {
    "Violet"    : "'Violet'",
    "Iris"      : "'Iris'",
    "Caribbean" : "'Caribbean'",
    "Lavender"  : "'Lavender'",
    "Cerulean"  : "'Cerulean'",
    "Forest"    : "'Forest'",
    "Rose"      : "'Rose'",
    "Mango"     : "'Mango'",
    "Purple"    : "'Purple'",
    "Blue"      : "'Blue'",
    "Teal"      : "'Teal'",
    "Magenta"   : "'Magenta'",
    "Tan"       : "'Tan'",
    "Green"     : "'Green'",
    "Brown"     : "'Brown'",
    "Yellow"    : "'Yellow'"
}
projection = {
    "center"  :"'C'",
    "N"    :"'N'",
    "S"    :"'S'",
    "W"    :"'W'",
    "E"    :"'E'",
    "NW"  :"'NW'",
    "SW"  :"'SW'",
    "NE"  :"'NE'",
    "SE"  :"'SE'",
}
left_right = {
    'left' : "'left'",
    'center' : "'center'",
    'right' : "'right'"
}
alignments = {
    "left" : "'left'",
    "center": "'center'",
    "right" : "'right'",
}
vertical_alignments = {
    "top" : "'top'",
    "center": "'center'",
    "bottom" : "'bottom'",
}
chatalign = {
    "left" : "'left'",
    "right" : "'right'"
}
charactor_columns={
    "Name"      :"'Name'",
    "Subtype"   :"'Subtype'",
    "Animation" :"'Animation'",
    "Bubble"    :"'Bubble'",
    "Voice"     :"'Voice'",
    "SpeechRate":"'SpeechRate'",
    "PitchRate" :"'PitchRate'",
}
fill_mode = {
    "stretch" : "'stretch'",
    "collage" : "'collage'",
}
fit_axis = {
    "free"          : "'free'",
    "vertical"      : "'vertical'",
    "horizontal"    : "'horizontal'"
}
True_False = {
    "yes": True,
    "no" : False
}
is_enable = {
    'enable' : True,
    'disable': False
}
askyesno = {
    "ask everytime"  : 'ask',
    "always yes"    : 'yes',
    "always no"    : 'no'
}
language = {
    '中文' : 'zh',
    'English' : 'en'
}
theme = {
    'light' : 'rplgenlight',
    'dark'  : 'rplgendark'
}
progressbar = {
    'color' : 'color',
    'black' : 'black',
    'hide'  : 'hide',
}
import_mode = {
    'add' : 'add',
    'replace' : 'replace'
}
dice_mode = {
    'COC' : 'COC',
    'DND' : 'DND',
    'ruleless' : 'ruleless'
}
colorschemes = {
    "monokai"   : "monokai",
    "ayu-dark"  : "ayu-dark",
    "ayu-light" : "ayu-light",
    "dracula"   : "dracula",
    "mariana"   : "mariana",
}
# 新建媒体按钮的结构
NewElement = {
    "charactor":{
        "charactor":{
            "text":"Subtype",
            "tooltip":"[Subtype] means the different states of a character. Each Subtype have independent settings for Animation, Bubble, and Voice.",
            "icon":'./assets/icon/new/charactor.png'
        }
    },
    "Pos":{
        "Pos":{
            "text":"Pos",
            "tooltip":"[Pos] is a fix point on canvas, which can be refered by other medias.",
            "icon":'./assets/icon/new/Pos.png'
        },
        "FreePos":{
            "text":"FreePos",
            "tooltip":"[FreePos] is point which can be move by <move> command.",
            "icon":'./assets/icon/new/FreePos.png'
        },
        "PosGrid":{
            "text":"PosGrid",
            "tooltip":"[PosGrid] is a set of grid-like dots. each member of the PosGrid is a Pos.",
            "icon":'./assets/icon/new/PosGrid.png'
        },
        "BezierCurve":{
            "text":"BezierCurve",
            "tooltip":"[BezierCurve] is a curve path; used to specify the motion trajectory of a media.",
            "icon":'./assets/icon/new/BezierCurve.png'
        }
    },
    "Text":{
        "Text":{
            "text":"Text",
            "tooltip":"[Text] is the basic Text Font. Create a Text media by specifying a font file.",
            "icon":'./assets/icon/new/Text.png'
        },
        "StrokeText":{
            "text":"StrokeText",
            "tooltip":"Compared to the basic Text, [StrokeText] has an additional stroke that can specify the color and width.",
            "icon":'./assets/icon/new/StrokeText.png'
        },
        "RichText":{
            "text":"RichText",
            "tooltip":"Using [RichText], you can flexibly adjust the text's italic, bold, font size, and color in RGL page.",
            "icon":'./assets/icon/new/RichText.png'
        },
        "HPLabel":{
            "text":"HPLabel",
            "tooltip":"Using [HPLabel], specific text can be displayed as a health bar style.",
            "icon":'./assets/icon/new/HPLabel.png'
        },
    },
    "Bubble":{
        "Bubble":{
            "text":"Bubble",
            "tooltip":"[Bubble] is the basic speech text box, consisting of a image, a main text, and a header text.",
            "icon":'./assets/icon/new/Bubble.png'
        },
        "Balloon":{
            "text":"Balloon",
            "tooltip":"Compared to bubbles, [Balloon] allows for multiple header texts to display different character-specific texts.",
            "icon":'./assets/icon/new/Balloon.png'
        },
        "DynamicBubble":{
            "text":"DynamicBubble",
            "tooltip":"Compared to bubbles, the size of the of [DynamicBubble] will adjust with the main text, commonly used in chat windows.",
            "icon":'./assets/icon/new/DynamicBubble.png'
        },
        "ChatWindow":{
            "text":"ChatWindow",
            "tooltip":"[ChatWindow] is a text box styled like an instant messaging app, capable of scrolling to display multiple speech contents.",
            "icon":'./assets/icon/new/ChatWindow.png'
        },
    },
    "Animation":{
        "Animation":{
            "text":"Animation",
            "tooltip":"[Animation] is the common image media used to display character or prop images. It can also play animations.",
            "icon":'./assets/icon/new/Animation.png'
        }
    },
    "Background":{
        "Background":{
            "text":"Background",
            "tooltip":"[Background] is used as the background layer of canvas. Note: Background must fully cover the canvas to avoid any abnormal effect.",
            "icon":'./assets/icon/new/Background.png'
        }
    },
    "Audio":{
        "Audio":{
            "text":"Audio",
            "tooltip":"[Audio] are commonly used audio media that can be played in dialogue lines. Each Audio can only be played once! ",
            "icon":'./assets/icon/new/Audio.png'
        },
        "BGM":{
            "text":"BGM",
            "tooltip":"[BGM] is audio media that can be played in a loop. BGM will not affect sound effects.",
            "icon":'./assets/icon/new/BGM.png'
        }
    }
}

# 动态切换效果的结构
ABMethod = {
    "alpha":{
        "replace"      : "replace",
        "black"      : "black",
        "cross"      : "cross",
        "delay"      : "delay",
    },
    "motion":{
        "static"          :'static',
        "pass"          :'pass',
        "leap"          :'leap',
        "circular"          :'circular',
        "shake"          :'shake',
    },
    "dirction":{
        "up"            :'up',
        "down"            :'down',
        "left"            :'left',
        "right"            :'right',
        "DG45"           :'DG45',
    },
    "scale":{
        "major"            : "major",
        "minor"            : "minor",
        "entire"          : "entire",
        "100 pixel"             : '100'
    },
    'in&out':{
        "both"  : 'both',
        "in": 'in',
        "out": 'out'
    }
}
# 媒体类的帮助链接
media_help_url = {
    'Pos':      'https://www.wolai.com/6YScpfA5QJaMCtpE999stS#jMX2TuS5Zm7CGFKdsGBRgB',
    'FreePos':  'https://www.wolai.com/6YScpfA5QJaMCtpE999stS#kj6xMgRS4reR21sCNeSHwh',
    'PosGrid':  'https://www.wolai.com/6YScpfA5QJaMCtpE999stS#gVfe7mSzoemiQvCobL5jJG',
    'BezierCurve': 'https://www.wolai.com/6YScpfA5QJaMCtpE999stS#9RiK7CLiWtyvB9ZFhz7Tjo',
    'Text':     'https://www.wolai.com/vjbVNex55KGPn2oEVjoZyK#3xCZVi8hQLQUh8w8W7BJzx',
    'StrokeText':   'https://www.wolai.com/vjbVNex55KGPn2oEVjoZyK#aEUx1knDvNnfppNEVzEK8e',
    'RichText': 'https://www.wolai.com/vjbVNex55KGPn2oEVjoZyK#pdRe5EN6iyieLSfGKGPQ9x',
    'HPLabel':  'https://www.wolai.com/vjbVNex55KGPn2oEVjoZyK#rLA9yENWLZ5fB5jQZicwCM',
    'Bubble':   'https://www.wolai.com/pJg4oRzqPtkkNVCURr7eGD#kymwfSgrXyzcRZayH2t7Ng',
    'Balloon':  'https://www.wolai.com/pJg4oRzqPtkkNVCURr7eGD#mSH7QJX3HuNbGkr4R88jtP',
    'DynamicBubble':    'https://www.wolai.com/pJg4oRzqPtkkNVCURr7eGD#8UKMX9fqLi58AtmNBkV3uz',
    'ChatWindow':   'https://www.wolai.com/pJg4oRzqPtkkNVCURr7eGD#6CZ7pE2bB5uN7zn1hJy2qD',
    'Animation':    'https://www.wolai.com/uVEVypkLFRuzKqiDpE5yXv#tjqF7AATGsoVgbJ2Q3Qhgn',
    'Sprite':       'https://www.wolai.com/uVEVypkLFRuzKqiDpE5yXv#o7dYhLVbbmyi9aMfD4mYfQ',
    'Background':   'https://www.wolai.com/7r3xgHhH1Grm5Smuwrw54C#bvheC9phxeYi7zkcwUWUDv',
    'Audio':    'https://www.wolai.com/vg19WbT72VHjBGnbQ4UmgW#eaN2UDJyU3d5dj34sozhzk',
    'BGM':  'https://www.wolai.com/vg19WbT72VHjBGnbQ4UmgW#63Go1D2Nef7LoBS6J9D1zo',
}
# 状态栏
key_status_bar = {
    -1: 'TTS key service disabled, using custom keys.',
    0: 'TTS service online, welcome.',
    1: '[ERROR:1] Error occurred in response format.',
    2: '[ERROR:2] Error occurred in TTS key decrypt.',
    3: '[ERROR:3] Request failed, current client has no permission.',
    4: '[ERROR:4] Connection timed out. please check your network.',
    5: '[ERROR:5] Service IP not found!',
    6: '[ERROR:6] Communication key not found!'
}
# 曲线函数
formulas = {
    "linear":       "'linear'",
    "quadratic":    "'quadratic'",
    "quadraticR":   "'quadraticR'",
    "sigmoid":      "'sigmoid'",
    "right":        "'right'",
    "left":         "'left'",
    "sincurve":     "'sincurve'",
}