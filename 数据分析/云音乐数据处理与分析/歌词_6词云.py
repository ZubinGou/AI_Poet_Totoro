# -*- coding: utf-8 -*-

import os
import wordcloud
import numpy as np
import matplotlib.pyplot as plt
from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


main_dir = '全部华语歌手_分词/'
pic = '云音乐.png'

'''
！！注意: 每次分析并且绘制完成一类歌手的词云图后需要关闭展示的词云才可以进行下一类的绘制
'''


def show(file, pic):
    global main_dir
    d = path.dirname(__file__)
    text = open(path.join(d, main_dir+file), encoding='utf-8').read()
    # 自定义图片
    my_coloring = np.array(Image.open(path.join(d, pic)))

    # 设置停用词
    stopwords = set(STOPWORDS)
    stopwords.add("")

    # 设置词云形状
    wc = WordCloud(font_path='simhei.ttf', width=800, height= 600, background_color="white", max_words=300, mask=my_coloring,
                   stopwords=stopwords, max_font_size=110, random_state=200)
    # 运行统计
    wc.generate(text)

    # 获取color
    image_colors = ImageColorGenerator(my_coloring)

    # 展示
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.figure()
    wc.to_file(file+'_1.png')

    # 按照给定的图片颜色布局生成字体颜色
    plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
    plt.axis("off")
    plt.figure()
    wc.to_file(file+'_2.png')

    plt.imshow(my_coloring, cmap=plt.cm.gray, interpolation="bilinear")
    plt.axis("off")
    plt.show()


def main():

    for root, dirs, files in os.walk(main_dir): 
        for file in files:
            print('begin with: {}'.format(file))
            show(file, pic)
            print('done with: {}'.format(file))

if __name__ == '__main__':
    main()

    print('完成词云咯！')
