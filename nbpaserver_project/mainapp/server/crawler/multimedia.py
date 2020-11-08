import string

# 멀디미디어 정보를 저장하는 객체
# multimedia_type에는 문자열이 저장되며, image, imoticon, video, hyperlink, etc가 저장됨.
class MultiMedia():
    def __init__(self, multimedia_type, src, width, height):
        self._multimedia_type = multimedia_type
        self._src = src
        self._width = width
        self._height = height
        pass

    def __str__(self):
        s = ''
        s = self._multimedia_type + ', ' + self._src + ', ' + str(self._width) + 'x' + str(self._height)
        return s