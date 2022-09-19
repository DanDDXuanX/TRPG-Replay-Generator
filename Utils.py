import numpy as np

# UF : 将2个向量组合成"x,y"的形式
concat_xy = np.frompyfunc(lambda x,y:'('+'%d'%x+','+'%d'%y+')',2,1)

# 截断字符串
def cut_str(str_,len_):
    return str_[0:int(len_)]
UF_cut_str = np.frompyfunc(cut_str,2,1)

# 设定合理透明度范围
def alpha_range(x):
    if x>100:
        return 100
    if x<0:
        return 0
    else:
        return x