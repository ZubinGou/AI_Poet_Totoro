import os
import jieba


main_dir = '全部华语歌手_yeah/'
save_dir = '全部华语歌手_分词/'
for root, dirs, files in os.walk(main_dir): 
    for file in files:
        data = open(main_dir+file, encoding='utf-8').read()
        save_data = open(save_dir+file, 'w+', encoding='utf-8')
        words = jieba.cut(data, HMM=True)
        save_data.write(' '.join(words)+'\n')
        save_data.close()
        print('done with{}'.format(file))

