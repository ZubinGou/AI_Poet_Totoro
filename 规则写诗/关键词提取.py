# -*- coding: utf-8 -*-
import os
import jieba_fast as jieba
import jieba_fast.analyse

# 可用文件名：lyricstest_body gsww_body modern_body poems_body shijing_body songci_body songshi_body tangshi_body
dataset = 'tangshi_body.txt'    # 只需更改这里的需要分析的文件名，即可一键分析保存
dataset_file = dataset+'_关键词提取'
if not os.path.exists(dataset_file):
    os.mkdir(dataset_file)
poem_file = open('数据\\'+dataset, encoding='utf-8').read()

typ = [('a', 'ag', 'ad', 'al', 'an', 'b'), ('c', 'cc'), ('i', 'l'), ('y', 'e'),
       ('o'), ('p'), ('q', 'qv', 'qt'),  ('n', 'r', 's', 'nr', 'ns', 'nt', 'nl', 'ng', 'nz', 'm'),
       ('d', 'dg'), ('v', 'vg', 'vd', 'vn', 'vf', 'vx', 'vi'), ('un'), ('f'),
       ('s', 'a', 'ag', 'ad', 'an', 'b', 'c', 'i', 'l', 'y',
        'e', 'j', 'p', 'q', 'n', 'r', 's', 'nr', 'ns', 'nt', 'nl', 'ng'
        'nz', 'm', 'd', 'dg', 'v', 'vg', 'vd', 'vn', 'un', 'f')]
'''
s 所有
n 名
v 动
a 形
d 副
c 连词
i 成语 习语
y 语气词 叹词
o 拟声词
p 介词
q 量词
f 方位词
u 未知高频词
'''
for i in typ:
    if i[0] in ['a', 'd', 'u', 'q', 'c', 'i', 'y', 'o']:  # 根据需要的词性修改，可参考excel表格中设定
        file = os.path.join(dataset_file, dataset_file+'_'+i[0]+'.txt')
        print('start analysing... {}'.format(file))
        file_obj = open(file, 'w+', encoding='utf-8')
        # rank = jieba_fast.analyse.textrank(poem_file, topK=1000, allowPOS=i)
        rank = jieba.analyse.extract_tags(poem_file, topK=1000, allowPOS=i)
        for word in rank:
            file_obj.writelines(word+' ')
        file_obj.close()
        print('Done : {}'.format(file))

print('finish analyse the whole file: {}'.format(dataset))
