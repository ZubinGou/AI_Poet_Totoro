# -*- coding: utf-8 -*-
import os

poets = ['李白', '杜甫', '苏轼', '辛弃疾', '白居易', '陆游', '杨万里', '刘克庄', '王安石', '黄庭坚']
poem = open('all.txt', encoding='utf-8').read().split('\n')
for i in range(len(poets)):
    if not os.path.exists(poets[i]):
        os.mkdir(poets[i])
    file_obj = open(poets[i]+ '\\' +poets[i]+'.txt', 'w+', encoding='utf-8')
    for line in poem:
        try:
            if line.split('::')[1].strip() == poets[i]:
                file_obj.write(line+'\n')
        except:
            print(line, poets[i])
            pass
