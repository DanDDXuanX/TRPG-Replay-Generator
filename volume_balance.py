from core.TTSengines import Aliyun_TTS_engine,Azure_TTS_engine,Tencent_TTS_engine
import pandas as pd
from core.ProjConfig import Preference
from pathlib import Path
import os

tts = {
    'Aliyun': Aliyun_TTS_engine,
    'Azure' : Azure_TTS_engine,
    'Tencent': Tencent_TTS_engine
}

# 初始化key
home_dir = Path(os.path.expanduser("~"))
preference = Preference(json_input=home_dir /'.rplgen' /'preference.json')


text_for_test = '因此，在性能较为有限的电脑上，可以保证质量稳定地导出视频，不会出现由于性能不足导致的视频卡顿和掉帧。Therefore, on computers with more limited performance, it is possible to export videos with stable quality, without experiencing video stuttering and frame drops due to insufficient performance.'

voice_volume = pd.read_csv('./assets/voice_volume.tsv',sep='\t')

# 批量合成语音

# for key,values in voice_volume.iterrows():
#     service_this = values['service']
#     voice_this = values['Voice']
#     if service_this not in tts:
#         continue
#     else:
#         tts_100:Aliyun_TTS_engine = tts[service_this](name='V100',voice=voice_this,volume=100)
#         tts_20:Aliyun_TTS_engine = tts[service_this](name='V20',voice=voice_this,volume=20)
#         v100 = tts_100.volume
#         v20 = tts_20.volume
#         tts_100.start(text=text_for_test, ofile=f'./test_output/volumne_test/V100/{service_this}.{voice_this}.{v100}.wav')
#         tts_20.start(text=text_for_test, ofile=f'./test_output/volumne_test/V20/{service_this}.{voice_this}.{v20}.wav')

for key,values in voice_volume.iterrows():
    service_this = values['service']
    voice_this = values['Voice']
    if service_this not in tts:
        continue
    else:
        tts_balance:Aliyun_TTS_engine = tts[service_this](name='balance',voice=voice_this)
        tts_balance.start(text=text_for_test, ofile=f'./test_output/volumne_test/balanced/{service_this}.{voice_this}.wav')