# coding: utf-8

import os
import sys
import gensim
import shutil
import warnings

warnings.filterwarnings(action='ignore',category=UserWarning,module='gensim')


def open_file(filename, mode='r'):
    return open(filename, mode=mode, encoding='utf-8', errors='ignore')


class DocSimilarity(object):

    def __init__(self, in_dir):
        """读取所有歌词"""
        self.lyrics = []  # 所有歌词
        self.fnames = []  # 所有文件名
        for fname in sorted(os.listdir(in_dir)):  # 排序，让内容相似的更加靠近
            self.fnames.append(fname)
            self.lyrics.append(list(open_file(os.path.join(in_dir, fname)).read()))

        print("原歌词总数:", len(self.lyrics))
        self.corpus_pr()

    def corpus_pr(self):
        """gensim文档tf_idf计算"""
        dictionary = gensim.corpora.Dictionary(self.lyrics)  # 文档词汇表
        corpus = [dictionary.doc2bow(lyric) for lyric in self.lyrics]  # 文档BOW特征向量
        tf_idf = gensim.models.TfidfModel(corpus)
        corpus = list(tf_idf[corpus])  # 文档TF-IDF特征

        self.vocab_size = len(dictionary)
        self.corpus = corpus
        print("文档TF-IDF特征计算完毕。")

    def remove_sim(self, out_dir, max_similarity=0.6, last_k=20):
        """移除相似文档，保存到新目录"""
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.mkdir(out_dir)

        cnt, yes = 1, 1
        c_corpus = [self.corpus[0]]  # 第0篇直接放入
        open_file(os.path.join(out_dir, self.fnames[0]), 'w').write(''.join(self.lyrics[0]))

        for i in range(1, len(self.corpus)):
            try:
                # 注意，只对比last_k篇文档，而不是所有歌词
                sims = gensim.similarities.Similarity('./index/',
                                                      c_corpus[-last_k:],
                                                      num_features=self.vocab_size)
                if sims[self.corpus[i]].max() < max_similarity:  # 如果最相似文本的相似度小于阈值
                    c_corpus.append(self.corpus[i])
                    open_file(os.path.join(out_dir, self.fnames[i]), 'w').write(''.join(self.lyrics[i]))
                    yes += 1
                cnt += 1
            except:
                pass
            if cnt % 2000 == 0:
                print('已处理：', cnt, '保留：', yes)
        print("保留歌词数：", yes)


if __name__ == '__main__':
    for root, dirs, files in os.walk('全部华语歌手_clean/'):
        for dir in dirs:
            data_dir = '全部华语歌手_clean/'+dir
            print('正在去重：{}'.format(data_dir))
            docsim = DocSimilarity(data_dir)
            # 不断测试发现最大相似设为0.6比较合适
            docsim.remove_sim('全部华语歌手_unique/'+dir, max_similarity=0.6, last_k=20)
