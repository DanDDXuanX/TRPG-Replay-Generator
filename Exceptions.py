# 异常定义

class ParserError(Exception):
    def __init__(self,*description):
        self.description = ' '.join(map(str,description))
    def __str__(self):
        return self.description

class MediaError(ParserError):
    pass