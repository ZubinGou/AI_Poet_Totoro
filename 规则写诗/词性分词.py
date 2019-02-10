# -*- coding: utf-8 -*-
import os
import jieba
from collections import Counter  # 可以直接Counter统计重复，得到高频词，但我还是手动造轮子...
import jieba.posseg as psg


def cut(dataset):
    store_file = '分词后文件\\'
    if not os.path.exists(store_file):
        os.mkdir(store_file)

    store_data = open(store_file + dataset+'_分词.txt', 'w', encoding='utf-8')
    data = open('数据\\'+dataset+'.txt', encoding='utf-8').read()

    # 没有人工去停用词，因为虚词连词甚至标点后面分析都可能用到
    words = psg.cut(data, HMM=True)

    words_dict = {}
    for word, flag in words:
        if word in words_dict.keys():
            words_dict[word][1] += 1
        else:
            words_dict[word] = [flag, 1]

    words_dict = sorted(words_dict.items(), key=lambda item: item[1][1], reverse=True)
    store_data.write(str(words_dict))


if __name__ == '__main__':
    # 可用文件名：lyricstest_body gsww_body modern_body shijing_body songci_body songshi_body tangshi_body
    dataset = 'tangshi_body'    # 只需更改此处为上述可用文件名之一，即可一键分词统计词频并保存
    cut(dataset)
    print('Done : {}'.format(1))
    print('finish analyse the whole file: {}'.format(dataset))
