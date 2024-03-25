# 概述

![logo](./doc/logo.png)

回声工坊（TRPG-Replay-Generator）是一款专注于跑团replay视频的专业制作工具：

回声工坊已发行在steam商店，商业发行版的名称为`回声工坊 RplGenStudio`，发行商名称为`Betelgeuse Industry`。

## 特点和优势

1. **简化工作**：显著减少跑团replay视频和类视觉小说视频制作中的重复工作，将视频制作简化到如同编写文档一样简单；
2. **高度自定义**：提供多种复杂的媒体类型，支持自定义复杂的视频界面布局；
3. **生态开放**：开放的上下游软件生态
    1. 支持VScode插件编辑剧本
    2. 海豹骰提供骰系级支持，log可直接导出回声工坊剧本格式
    3. 可以将项目导出为PR项目，保留最大化的后期编辑空间
    4. 允许导出透明背景视频素材
4. **创意分享**：支持创意工坊，允许用户分享和下载预设样式模板，利用模板实现一键成片

# 软件下载

正式在steam商店发行之后，本仓库不再提供开包即用的二进制可执行文件，仅提供源代码。

源代码版本不拥有内置语音合成服务的权限，需要自行注册语音合成账号，并填写key到【首选项】

## [steam商店](https://store.steampowered.com/app/2550090/_RplGen_Studio/)
- 回声工坊在steam商店的售价是13美元，或者人民币50元；<p>
- 自动更新、创意工坊、内置语音服务等，仅在steam平台版本提供。<p>

## [爱发电](https://afdian.net/item/68ed814c7df011eebefc52540025c377)
- 爱发电中同样销售steam的激活码（CDkey），定价为50元；<p>
- 购买之后需要在steam平台激活，功能等价于在steam商店直接购买。<p>

## 配置要求
**最低：**
1. 系统：Windows 10
2. 内存：4GB
3. 硬盘：1GB

**最佳：**
1. 系统：Windows 10
2. 内存：8GB
3. 硬盘：1GB

# 操作手册

[回声工坊 RplGenStudio 操作手册](https://www.wolai.com/mJpcu5LUk3cECUjNXfHaqT)

# 构建

## 环境要求：

环境和依赖项：

1. python>=3.8
1. pygame>=2.0.1
1. numpy>=1.18.5
1. pandas>=1.0.5
1. Pillow>=7.2.0
1. ffmpeg-python>=0.2.0
1. pydub>=0.25.1
1. openpyxl>=3.0.4
1. azure-cognitiveservices-speech>=1.31.0
1. ttkbootstrap>=1.10.1
1. tkextrafont==0.6.3
1. chlorophyll==0.3.1
1. pyttsx3==2.90
1. websocket-client==1.0.1
1. pinyin==0.4.0

除上述项目外，还需要：

1. 下载[ffmpeg](https://ffmpeg.org/download.html)的可执行文件，并解压到本仓库根目录。
1. 安装[阿里云智能语音服务Python SDK](https://github.com/aliyun/alibabacloud-nls-python-sdk)
1. 安装[7z](https://github.com/sparanoid/7z)，并添加到环境变量，打包时需要。（推荐）

## 构建和打包

使用[打包脚本](./bulid.ps1)，即可将软件打包。

# 开源协议

本软件采用[**GPL3.0**](LICENSE.md)协议开源：允许用户自由的使用、修改本软件，或者将本软件的部分代码用于自己的项目，但是，需要注意以下几点：
1. **开源要求**：如果在其他项目中使用了本项目的功能或代码，那么遵照GPL3.0协议的规范，该项目也应开源，并规范著名引用关系。
2. **使用限制**：在基于本项目，进行二次开发时，不允许使用本软件的图标、名称、吉祥物等第三方享有著作权的资产。