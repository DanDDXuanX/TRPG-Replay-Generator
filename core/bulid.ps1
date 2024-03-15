# 打包
D:\pyenv\rplgenpy\Scripts\pyinstaller.exe .\gui.d.spec

# 改可执行文件的名字
Move-Item .\dist\gui\gui.exe  .\dist\gui\RplGenStudio.exe

# 复制到dist文件夹
Copy-Item .\assets .\dist\gui\ -r 
Copy-Item .\intel .\dist\gui\ -r 
Copy-Item .\ffmpeg.exe .\dist\gui\
Copy-Item .\ffprobe.exe .\dist\gui\

# 获取md5
certutil -hashfile .\dist\gui\RplGenStudio.exe MD5

# 压缩
7z a -tzip -mcu=on .\dist\package.zip .\dist\gui\*