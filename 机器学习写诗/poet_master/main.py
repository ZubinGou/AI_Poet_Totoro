# -*- coding: utf-8 -*-
import os
import sys
from write_poem import WritePoem,start_model


writer = start_model()

def write_poem(poem_style, word):

    if poem_style == 1:
        return  writer.free_verse()    # 自由诗
    elif poem_style == 2:
        return writer.rhyme_verse()    # 押韵诗
    elif poem_style == 3:
        return  writer.cangtou(word)    # 藏头诗+押韵
    elif poem_style == 4:
        return writer.hide_words(word)  # 藏字诗+押韵
    return 0

def output(poem):
    '''美化输出格式'''
    poem = poem.strip('。')
    lenth = len(poem.split('。')[0])*2 + 10
    print()
    print('-'*lenth)
    print()
    for i in poem.split('。'):
        print('     ' + i + '。')
    print()
    print('-'*lenth)
    print()


if __name__ == "__main__":
    help = '''
    自由诗： python main.py 1
    押韵诗： python main.py 2
    藏头诗： python main.py 3 四个汉字
    藏字诗： python main.py 4 汉字
    '''
    word = '输入汉字'
    try:
        poem_style = int(sys.argv[1])
        if poem_style not in [1,2,3,4]:
            print(help)
    except:
        print(help)
        exit(1)
    try:
        word = sys.argv[2]
    except:
        pass
    poem = write_poem(poem_style, word)
    output(poem)
    
