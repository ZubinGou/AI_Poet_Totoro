# -*- coding: utf-8 -*-

import os 
import pyecharts
from collections import Counter
from random import seed
from random import randint


main_file = '全部华语歌手_分词/'


def show(data, file):
    es = pyecharts.Bar(title=file.rstrip('.txt')+'字频', title_top=100,  width=1300, height=700,)
    flag = 1
    for title, num in data:
        if num < 10000:
            pass
        else:
            es.add(title, [flag], [num],xaxis_interval=0, yaxis_interval=0)
            flag += 1
    es.render(path=file.rstrip('.txt')+'_字频'+'.html')


def analye(file):

    lyrics = open(main_file+file, encoding='utf-8').read().strip().replace('\n', ' ').split()
    counter = Counter(lyrics)
    count_pairs_o = counter.most_common()
    count_pairs = []
    for i in count_pairs_o:
        if i[0] not in ['，', '。'] and len(i[0]) == 1:  # 过滤标点
            count_pairs.append(i)

    print("{}总词数:".format(file.rstrip('.txt')), len(lyrics))
    print("{}词汇量:".format(file.rstrip('.txt')), len(counter))
    print("{}高频字:".format(file.rstrip('.txt')), count_pairs[:50])
    print('\n')
    return count_pairs


def main():
    for root, dirs, files in os.walk(main_file): 
        for file in files:
            count_pairs = analye(file)
            # show_pairs = [i for i in count_pairs if i[0] != '，' ]
            show(count_pairs[:30], file)

if __name__ == '__main__':
    main()
