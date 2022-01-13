# 概述
这是一基于python3 和pygame2.1 的自动replay生成工具，旨在降低replay视频制作中的重复工作，节约时间提升效率。使用简单处理后的log文件即可生成replay视频，同时也有较大的自定义空间。适合有一定编程基础和视频剪辑基础的用户使用。<br>

环境要求：
1. python &gt; 3.8.3
2. pygame &gt; 2.0.1
3. numpy &gt; 1.18.5
4. pandas &gt; 1.0.5

# 快速上手
1. 下载包含了源代码和示例文件（"./toy/"）的release压缩包并解压；
2. 在解压路径，使用终端运行下列命令，即可开始放映示例项目；<br>
```bash
python replay_generator.py -l LogFileTest.txt -d MediaObject.txt -t CharactorTable.csv
```
3. 进入程序后，按空格键（SPACE）开始播放，播放的过程中，按A键跳转到前一小节，D键跳转到后一小节，ESC键终止播放并退出。

# 参考文档

## 主程序参数
1. **--LogFile, -l** ：log文件的路径，文件格式要求详见 *文件格式.log文件*；
2. **--MediaObjDefine, -d** ：媒体定义文件的路径，文件格式要求参考 *文件格式.媒体定义文件*；
3. **--CharacterTable, -t** ：角色表文件的路径，格式为制表符分隔的数据表，包含至少Name、Subtype、Animation、Bubble4列；
4. ***--OutputPath, -o*** ：可选的参数，输出文件的目录；如果输入了该标志，则项目的时间轴和断点文件将输出到指定点目录，格式为.pkl，是pandas.DataFrame 格式，可以在python中使用pd.read_pickle()函数读取；
5. ***--FramePerSecond -F*** ：可选的参数，播放的帧率，单位是fps；默认值是30fps；
6. ***--Width –W*** ：可选的参数，窗体的宽；默认值是1920；
7. ***--Height -H*** ：可选的参数，窗体的高；默认值是1080；
8. ***--Zorder –Z*** ： 可选的参数，渲染的图层顺序；通常不建议修改这个参数，除非必要。格式要求详见 进阶使用.图层顺序。

**主程序命令例子：**
```bash
python replay_generator.py --LogFile LogFile.txt --MediaObjDefine MediaDefine.txt --CharacterTable CharactorTable.csv --FramePerSecond 30
```

## 1. 媒体定义文件
媒体定义文件用于定义项目中使用的媒体对象，及其引用的文件；媒体定义文件使用的python代码的格式。<p>
目前版本中，可用的对象包括下列：

1.	**文本 Text**
```python 
Text(fontfile='C:/Windows/Fonts/simhei.ttf',fontsize=40,color=(0,0,0,255),line_limit=20)
```

- 文本是气泡对象的一部分，不可单独使用；
- fontfile	可选参数，指定一个字体文件的路径；默认参数是系统的微软雅黑字体；
- fontsize	可选参数，设置字体的字号，合理的参数是大于0的整数；默认为40；
- color	可选参数，设置字体的颜色，是一个4元素的tuple，对应(R,G,B,A)，四个元素应为0-255的整数；默认值是黑色；
- line_limit	可选参数，设置单行显示的字符数量上限，超过上限会触发自动换行；默认为20字。
> 注意：由于气泡对象需要引用文本对象，因此，文本对象的定义必须在气泡对象的定义之前。

2.	**气泡 Bubble**
```python
Bubble(filepath,Main_Text=Text(),Header_Text=None,pos=(0,0),mt_pos=(0,0),ht_pos=(0,0),line_distance=1.5)
```

- 气泡是一个文本框，在角色发言时显示，包含了主文本、头文本、底图三个组成部分。
- filepath	必要参数，指定一个图片文件的路径；即使不需要底图，也需要指定一个空白底图的路径；
- Main_Text	可选参数，为主文本指定一个*文本*对象，主文本对应中的 *发言文本*；默认值是默认参数的Text对象，也可以设置为None；
- Header_Text	可选参数，为头文本指定一个*文本*对象，头文本对应发言者的角色名；默认为None，既无头文本；
- pos	可选参数，设置*气泡*在屏幕上的位置，是一个2元素的tuple，对应(X,Y)；默认为(0,0)，即左上角；
- mt_pos	可选参数，设置主文本相对于气泡底图的位置，是一个2元素的tuple，对应(X,Y)；默认为(0,0)，即左上角；
- ht_pos	可选参数，设置头文本相对于气泡底图的位置，是一个2元素的tuple，对应(X,Y)；默认为(0,0)，即左上角；
- line_distance	可选参数，设置了多行显示时的行距，默认值为1.5倍行距。

3.	**背景 Background**
```python
Background(filepath,pos = (0,0))
```

- 背景指整个屏幕的背景，通常位于最下的图层，可以在log文件中的 *背景行* 中设置背景及其切换效果
- filepath	必要参数，指定一个图片文件的路径，或者指定{'black','white','greenscreen'}中的一个。
- pos	可选参数，指定了背景在屏幕上的位置，是一个2元素的tuple，对应(X,Y)，默认为(0,0)，即左上角。
> 注意：由于背景图通常都是全屏的图片，因此不建议修改Background的pos的默认值。

4.	**立绘 Animation**
```python
Animation(filepath,pos = (0,0))
```

- 立绘指和角色绑定的个人形象图片，通常位于背景的上层，气泡的下层。
- filepath	必要参数，指定一个图片文件的路径；
- pos	可选参数，指定了立绘在屏幕上的位置，是一个2元素的tuple，对应(X,Y)，默认为(0,0)，即左上角。
> 注意：一个角色可以在不同的subtype下指定不同的立绘，用于实现差分效果；使用时在log文件的对话行里指定到不同的subtype。<p>
> 注意：如果希望实现多人同框效果，建议为同框时的立绘另外建立Animation对象，并在定义时指定合适的位置。

5.	**背景音乐 BGM**
```python
BGM(filepath,volume=100,loop=True)
```

- BGM指长的，一直位于后台循环播放的音频；支持的格式是.ogg，如果是.mp3格式的背景音乐，建议先进行格式转换。
- filepath	必要参数，指定一个音频文件的路径。
- volume	可选参数，设置背景音乐的音量，合理的参数是0-100的整数；默认为100；
- loop	可选参数，设置背景音乐是否会循环播放；默认为单曲循环；如果需要不循环，设置为False；
> 注意：BGM建议使用.ogg格式的音频，否则有可能出现程序的不稳定。另外，建议在后期制作软件中手动加入BGM。<p>
> 注意：BGM和audio的逻辑不同，不可混用！

6.	**音效 Audio**
```python
Audio(filepath)
```

- 音效指短音频，音效通常只会完整地播放一次。
- filepath	必要参数，指定一个音频文件的路径。
> 注意：replay视频中通常包含大量的语音文件，不建议全建立Audio对象，会消耗较大的内存，在Log文件的*对话行*的*音效框*里指定文件路径即可。

> 注意：本提及的*文件路径*的格式均为字符串，即需要引号引起来。例子："./pic/zhang.png"

**媒体定义文件例子：**<p>
参考./toy/MediaObject.txt

## 2. 角色设置文件
- 角色设置文件是一个制表符“\t”分隔的数据表文件，用于确定角色和*立绘、气泡*等媒体对象的对应关系；
- 需要包括Name、Subtype、Animation、Bubble四个列；
- 每个Name需要一个Subtype是default；
- Animation和Bubble需要指向相应的媒体对象，或者使用 NA 表示缺省。

角色设置文件例子：

|Name|Subtype|Animation|Bubble|
|:---|:---:|:---:|:---:|
|张安翔|default|zhang|bubble1|
|张安翔|scared|zhang_scared|bubble1|
|KP|default|drink|bubble2|

> 注意：骰子、旁白等弹窗型气泡，也可以以“角色”的形式定义在本文件中。

## 3. Log文件
log文件是整个演示的主文件，决定了展示的内容和效果；<p>
log文件有3种有效行，对话行，背景行和设置行，分别有其对应的格式。

### A. 对话行
```HTML
[name1(100).default,name2(60).default,name3(60).default]<replace=0>:Talk#Text.<all=0>{"./audio/1.ogg";30}{Audio;30}
```

通过对话行，在播放中显示角色的*立绘*，并用相应的*气泡*显示*发言文本*中的文字。对应关系在*角色设置文件*中定义。
1.	**角色框：\[name(alpha).subtype;...\]**
	- 角色框内最多指定3个角色，同框角色的立绘都将展示出来；
	- 只有顺位第一个角色的立绘的透明度为100，其余角色会自动被设置为半透明，在角色名后使用(alpha)可以手动指定立绘的透明度；
	- 同一个角色如果有差分立绘，可以在角色名后使用.subtype来指定差分；未指定的将默认使用.default的立绘。
2.	**切换效果修饰符：&lt;method=time&gt;**
	- 目前可用的切换效果有replace和black，若语句中未指定切换效果，则参考 *method_default*；
	- 持续时长指渐变持续的帧数；可以缺省持续时长，此时持续时长将参考 *method_dur_default*；
	- Replace：直接替换，持续时长指切换延后时间；
	- Black：黑场，以渐变为切换，持续时长指渐变时长。
3.	**发言文本：^Talk#Text**
	- 发言文本可以是大部分文本，但不建议包括英文方括号“[]”、英文尖括号“&lt;&gt;”和英文花括号“{}”，否则可能导致程序的不稳定或报错；
	- 发言文本中可以使用井号“#”作为手动换行符，或在句首使用“^”声明手动换行模式；在手动指定换行符的行内，自动换行是失效。
4.	**文本效果修饰符：&lt;method=time&gt;**
	- 文本展示的效果有all，w2w，l2l，若语句中未指定展示效果，则参考 *text_method_default*；
	- 单位时间指每显示一个字需要的帧数；可以缺省单位时间，此时单位时间将参考 *text_dur_default*；
	- all，一次性展示所有文本，参数此时指延迟帧数；
	- w2w，逐字展示文本；
	- l2l，逐行展示文本。
5.	**音效框：{file_or_obj;\*time}**
	- 音效可以指定一个Audio对象，或者一个文件的路径；
	- 延迟时间指这个音效相对于本小节第一帧所延迟的帧数；
	- 通常来说，对白的音效框因由程序自动添加；
	- 一个对话行可以有多个音效框。

> 注意：在使用“#”进行手动换行的句子里，如果第一行长度超过line_limit，在&lt;w2w&gt;模式仍会触发自动换行，直到第一个“#”被触发为止。为了避免这种情况的发生，在句首声明“^”。<p>
> 注意：若在音效框的time数值前添加星号“*”，则本小节将和星标音效设置为相同的时长。星标音效通常由音频准备程序自动生成，请谨慎地手动设置星标音效。

**对话行例子：**
```HTML
[张安翔]:最基本的对话行
[张安翔]<black>:指定了切换方式
[张安翔]<black=30>:指定了切换时间
[张安翔]<black=30>:指定了文字显示模式<w2w>
[张安翔]<black=30>:指定了文字显示单位时间<w2w=5>
[张安翔,KP]<black=30>:设置了多人同框<w2w=5>
[张安翔(60),KP(30)]<black=30>:手动设置了立绘透明度<w2w=5>
[张安翔(60).scared,KP(30)]<black=30>:显示角色的差分立绘<w2w=5>
[张安翔(60).scared,KP(30)]<black=30>:设置手动换行模式#以井号作为换行符#逐行显示内容<l2l=5>
[张安翔(60).scared,KP(30)]<black=30>:播放语音<all=5>{'./voice/1.ogg'}
[张安翔(60).scared,KP(30)]<black=30>:播放音效<all=5>{SE1;30}
```

### B. 背景行
```HTML
<background><replace=0>:Background
```

通过背景行，切换播放的背景图片。
1.	**背景行的识别标志：&lt;background&gt;** 是背景行的必要组成部分。
2.	**切换效果修饰符：&lt;replace=time&gt;** 背景展示修饰方法包括：
	- cover：覆盖，新的背景会逐渐覆盖原背景，参数是整个渐变的时长
	- black，黑场，原背景先隐入黑场，然后新背景再逐渐出现，参数是整个渐变的时长。
	- white，白场，原背景先隐入白场，然后新背景再逐渐出现，参数是整个渐变的时长。
	- replace，替换，瞬间替换，参数是替换发生的延迟时间。默认值是replace=0

**背景行例子：**
```HTML
<background>:BG1
<background><cover>:BG2
<background><black=30>:BG3
```

### C. 设置行
```HTML
<set:method_default>:<replace=0>
```

通过设置行，动态地改变全局变量；
set:后跟需要设置的全局变量名；
可以通过set动态修改的全局变量有：
1.	**method_default**：默认展示方法，初始值是：&lt;replace=0&gt;。
	- 当对话行和背景行中缺省 *切换效果修饰符* 时，则使用该默认值
	- 不建议将该默认值设置为仅背景行可用的修饰符，例如cover
2.	**text_method_default**：默认文本展示方法，初始值是：&lt;all=1&gt;。
	- 当对话行中缺省 *文本效果修饰符* 时，使用该默认值
	- 例如[name]:talk，等价于[name]&lt;replace=0&gt;:talk&lt;all=1&gt;
3.	**method_dur_default**：默认展示时间，初始值是：10。
	- 当对话行和背景行的 *切换效果修饰符* 中未指定时间，则使用该默认值
	- 例如 &lt;replace&gt;，等价于&lt;replace=10&gt;
4.	**text_dur_default**：默认文本展示时间，初始值是：8。
	- 当对话行的&lt;文本效果修饰符&gt;中未指定时间，则使用该默认值；
	- 例如 talk&lt;l2l&gt;，等价于talk&lt;l2l=8&gt;。
5.	**speech_speed**：语速，初始值是：220。
	- 语速主要影响每个小节的持续时间，需要调整语速和语音文件相一致。
6.	**BGM**：背景音乐
	- 使用&lt;set:BGM&gt;: 设置背景音乐时，需要指定一个BGM对象，或一个.ogg音频文件的路径；
> 注意：使用非.ogg文件作为背景音乐，可能导致程序的不稳定，或者卡死！

**设置行例子：**
```HTML
<set:method_default>:<black=30>
<set:text_dur_default>:10
<set:BGM>:'.\BGM\test.ogg'
<set:BGM>:BGM1
```

### D. 注释行、空白行
`#annotation`
1.	当一个行的第一个字符是井号“#”，则这个行被认作为注释，行内的任何内容都不会被执行；
2.	log文件可以任意地添加空白行，且不会影响程序的正常使用。

## 进阶使用

### 修改timeline和breakpoint文件
- timeline.pkl 和 breakpoint.pkl 文件是由 *--OutputPath* 标志输出的文件，包含了整个工程的画面和音频的时间轴信息。
- 主程序的parser()函数解析log文件之后，生成render_timeline表格，提供给render()函数逐帧渲染；breakpoint文件记录了各个小节的断点，用于在播放过程中向前向后导航。
- 因此，熟悉pandas库的使用者可以自行修改timeline，以实现到高度自定义的显示效果。
- timeline.pkl 的type是pandas.DataFrame，breakpoint.pkl的type是pandas.Series；使用`pandas.read_pickle(filepath)`可以读取这些文件。
- `timeline.columns`为：

|BG1|BG1_a|BG2|BG2_a|BG3|BG3_a|Am1|Am1_a|Am2|Am2_a|Am3|Am3_a|Bb|Bb_main|Bb_header|Bb_a|BGM|Voice|SE|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

- 分别表示：三层背景图层及其透明度，三个立绘图层及其透明度，一个气泡图层及其主文本、头文本、透明度，背景音乐，语音，音效。
- `timeline.index`为帧序号。出于节约性能的考虑，与前一帧相同的帧被舍弃且不重复渲染，因此timeline.index是不连续的。
- `breakpoint.index`为原始log文件中的行，`breakpoint.values`为各个断点对应的帧序号。

> 在未来的更新中，将支持用timeline+breakpoint文件，替代 *--LogFile* 标志，作为程序的输入。

### --Zorder 图层顺序
- 修改图层顺序参数，可以改变各个图层的重叠关系。
- 默认的图层顺序为`-Z "BG3,BG2,BG1,Am3,Am2,Am1,Bb"`，顺序为从下到上，即*背景*在最下层，*气泡*在最上层，*立绘*在中间，其中主立绘在其他立绘上层。
- 主要的修改需求可能是要求立绘覆盖在气泡的上层，因此，可以将 *--Zorder* 参数设置为`"-Z BG3,BG2,BG1,Bb,Am3,Am2,Am1"`

> 注意：不建议修改3个BG图层的顺序，否则会导致多个切换效果的不正常表现！
