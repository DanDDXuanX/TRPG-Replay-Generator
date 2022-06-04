# Azure可用语音帮助文档

## 角色配置表中的voice参数

1. 所有的Azure音源都需要在语音名称前，添加`Azure::`；
2. 如果需要指定风格化和角色扮演的语音，使用`Azure::语音名称:风格化:风格强度:角色扮演`作为voice值；
3. 风格强度的取值范围为`(0-2]`，0.01为极弱，1为正常，2为较强；
4. 角色扮演的可选参数是：`YoungAdultFemale, YoungAdultMale, OlderAdultFemale, OlderAdultMale, SeniorFemale, SeniorMale, Girl, Boy`

**例子：**
```
Azure::zh-CN-XiaochenNeural
Azure::zh-CN-XiaohanNeural::affectionate::0.5:OlderAdultMale
```

## 角色配置表中的SpeechRate和PitchRate参数

1. Azure的音源，在角色表中的`SpeechRate`和`PitchRate`列，采用和阿里云语音相同的标准，取值范围为`[-500,500]`；
2. Azure预览中的语速和角色配置表中SpeechRate和PitchRate参数的对应关系，如下表所示；

|预览语速/语调|SpeechRate/PitchRate|
|:---:|:---:|
|2|500|
|1.8|400|
|1.6|300|
|1.4|200|
|1.2|100|
|1|0|
|0.8|-100|
|0.6|-200|
|0.4|-300|
|0.2|-400|
|0|-500|

> 注意：语速可用的最小值是为 0.5（SpeechRate = -250），低于 -250 时，语速也不能变得更低了；

## 普通话中文音源表
|语言|Locale|性别|语音名称|风格化|角色扮演|
|:---:|:---:|:---:|:---|:---|:---|
|中文（普通话，简体）|zh-CN|女|zh-CN-XiaochenNeural|不支持|不支持|
|中文（普通话，简体）|zh-CN|女|zh-CN-XiaohanNeural|affectionate, angry, calm, cheerful, disgruntled, embarrassed, fearful, gentle, sad, serious|不支持|
|中文（普通话，简体）|zh-CN|女|zh-CN-XiaomoNeural|affectionate, angry, calm, cheerful, depressed, disgruntled, embarrassed, envious, fearful, gentle, sad, serious|支持|
|中文（普通话，简体）|zh-CN|女|zh-CN-XiaoqiuNeural|不支持|不支持|
|中文（普通话，简体）|zh-CN|女|zh-CN-XiaoruiNeural|angry, calm, fearful, sad|不支持|
|中文（普通话，简体）|zh-CN|女|zh-CN-XiaoshuangNeural|chat|不支持|
|中文（普通话，简体）|zh-CN|女|zh-CN-XiaoxiaoNeural|affectionate, angry, assistant, calm, chat, cheerful, customerservice, disgruntled, fearful, gentle, lyrical, newscast, sad, serious|不支持|
|中文（普通话，简体）|zh-CN|女|zh-CN-XiaoxuanNeural|angry, calm, cheerful, depressed, disgruntled, fearful, gentle, serious|支持|
|中文（普通话，简体）|zh-CN|女|zh-CN-XiaoyanNeural|不支持|不支持|
|中文（普通话，简体）|zh-CN|女|zh-CN-XiaoyouNeural|不支持|不支持|
|中文（普通话，简体）|zh-CN|男|zh-CN-YunxiNeural|angry, assistant, cheerful, depressed, disgruntled, embarrassed, fearful, narration-relaxed, sad, serious|支持|
|中文（普通话，简体）|zh-CN|男|zh-CN-YunyangNeural|customerservice, narration-professional, newscast-casual|不支持|
|中文（普通话，简体）|zh-CN|男|zh-CN-YunyeNeural|angry, calm, cheerful, disgruntled, embarrassed, fearful, sad, serious|支持|
