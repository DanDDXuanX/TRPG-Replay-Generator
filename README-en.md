# Overview

![logo](./doc/logo.png)

TRPG-Replay-Generator is a professional production tool dedicated to creating replay videos for tabletop role-playing games (TRPG):

This project has been released on the Steam store, with the commercial edition named `回声工坊 RplGenStudio`, and the publisher is `Betelgeuse Industry`.

## Features and Advantages

1. **Streamlined Workflow**: Significantly reduces repetitive work in the production of TRPG replay videos and visual novel-like videos, simplifying video production to be as easy as writing a document;
2. **High Customization**: Offers a variety of complex media types, supporting the customization of complex video interface layouts;
3. **Open Ecosystem**:
    1. Supports VScode plugin for script editing.
    2. Seal Dice provides dice system-level support, and logs can be directly exported to RplGenLog format.
    3. Allows project export as a PR project, preserving maximum post-production editing space.
    4. Allows export of video materials with a transparent background.
4. **Creative Sharing**: Supports the Steam Workshop, allowing users to share and download preset style templates, achieving one-click video production with templates.

# Software Download

After the official release on the Steam store, this repository no longer provides ready-to-use binary executable files, only the source code.

The source code version does not have the keys to use the built-in text-to-speech service, and you need to register for a text-to-speech account and fill in the key in **Preferences**.

## [Steam Store](https://store.steampowered.com/app/2550090/_RplGen_Studio/)
- The price of RplGenStudio in the Steam store is $13, or 50 RMB;<p>
- Features such as automatic updates, Steam Workshop, and built-in text-to-speech services are only available in the Steam platform version.<p>

## [Aifadian](https://afdian.net/item/68ed814c7df011eebefc52540025c377)
- Aifadian also sells Steam activation codes (CDkey), priced at 50 RMB;<p>
- After purchase, it needs to be activated on the Steam platform, with equivalent functionality to direct purchase in the Steam store.<p>

## System Requirements
**Minimum:**
1. System: Windows 10
2. Memory: 4GB
3. Hard Drive: 1GB

**Recommended:**
1. System: Windows 10
2. Memory: 8GB
3. Hard Drive: 1GB

# User Manual

[RplGenStudio User Manual](https://www.wolai.com/mJpcu5LUk3cECUjNXfHaqT)

# Building

## Environment Requirements:

Environment and dependencies:

1. python>=3.8
2. pygame>=2.0.1
3. numpy>=1.18.5
4. pandas>=1.0.5
5. Pillow>=7.2.0
6. ffmpeg-python>=0.2.0
7. pydub>=0.25.1
8. openpyxl>=3.0.4
9. azure-cognitiveservices-speech>=1.31.0
10. ttkbootstrap>=1.10.1
11. tkextrafont==0.6.3
12. chlorophyll==0.3.1
13. pyttsx3==2.90
14. websocket-client==1.0.1
15. pinyin==0.4.0

In addition to the above items, the following are also required:

1. Download the executable file of [ffmpeg](https://ffmpeg.org/download.html) and extract it to the root directory of this repository.
2. Install the [Alibaba Cloud NLS Python SDK](https://github.com/aliyun/alibabacloud-nls-python-sdk)
3. Install [7z](https://github.com/sparanoid/7z) and add it to the environment variables, required for packaging. (Recommended)

## Building and Packaging

Use the [Packaging Script](./bulid.ps1) to package the software.

# Open Source License

This software is open source under the [**GPL3.0**](LICENSE.md) license: it allows users to freely use and modify this software, or use parts of the code for their own projects, but please note the following points:
1. **Open Source Requirements**: If the functionality or code of this project is used in other projects, in accordance with the GPL3.0 license, that project should also be open source and properly attribute the reference relationship.
2. **Usage Restrictions**: When developing based on this project, it is not allowed to use the software's icons, names, mascots, and other copyrighted assets of third parties.
