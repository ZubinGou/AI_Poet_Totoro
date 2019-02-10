# -*- coding: utf-8 -*-

import os 
import pyecharts
from collections import Counter
from random import seed
from random import randint


main_file = '全部华语歌手_分词/'


def show(data, file):
    '''展示图表'''
    all_ci = [i[0] for i in data]
    all_num = [i[1] for i in data]

    rank_bar = pyecharts.Bar('\n{}词频榜'.format(file.rstrip('.txt')), width=1400, height=750, title_pos='center', title_top=3)  # 初始化图表
    # all_names是所有电影名，作为X轴, all_lovers是关注者的数量，作为Y轴。二者数据一一对应。  is_label_show=True,
    # is_convert=True设置x、y轴对调,。is_label_show=True 显示y轴值。 label_pos='right' Y轴值显示在右边
    rank_bar.add('', all_ci, all_num,  label_pos='center',is_convert=True, xaxis_interval=0, yaxis_interval=0, is_yaxis_inverse=True)

    rank_bar.render(path=file.rstrip('.txt')+'_词频'+'.html')  


def analye(file):

    lyrics = open(main_file+file, encoding='utf-8').read().strip().replace('\n', ' ').split()
    counter = Counter(lyrics)
    count_pairs_o = counter.most_common()
    count_pairs = []
    for i in count_pairs_o:
        if len(i[0]) > 1:
            count_pairs.append(i)

    print("{}词数总计:".format(file.rstrip('.txt')), len(lyrics))
    print("{}词汇总量:".format(file.rstrip('.txt')), len(counter))
    print("{}高频词汇:".format(file.rstrip('.txt')), count_pairs[:50])
    print('\n')
    return count_pairs


def main():
    for root, dirs, files in os.walk(main_file): 
        for file in files:
            count_pairs = analye(file)

            show(count_pairs[:30], file)

if __name__ == '__main__':
    main()
