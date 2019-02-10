
import os 
import pyecharts
from collections import Counter
from random import seed
from random import randint
from pyecharts import WordCloud

main_file = 'data/'

def pic(data, file):
    all_poet = [i[0] for i in data[:30]]
    all_num = [i[1] for i in data[:30]]
    br = pyecharts.Bar(title=file.rstrip('.txt')+'最受欢迎的词牌', title_top=0,  width=1200, height=700,)

    br.add('', all_poet, all_num,  label_pos='center',is_convert=True, xaxis_interval=0, yaxis_interval=0, is_yaxis_inverse=True)
    br.use_theme('dark')
    br.render(path=file.rstrip('.txt')+'最受欢迎的词牌_条形图'+'.html')

    all_poet = [i[0] for i in data[:1000]]
    all_num = [i[1] for i in data[:1000]]
    wordcloud = WordCloud(width=1300, height=620)
    wordcloud.add("", all_poet, all_num, word_size_range=[5, 50])
    wordcloud.render(path=file.rstrip('.txt')+'最受欢迎的词牌_词云'+'.html')

def analye(file):
    poets = []
    poems = open(main_file+file, encoding='utf-8')
    for poem in poems:
        poets.append(poem.split('::')[0])
    counter = Counter(poets)
    counts = counter.most_common()
    count_pairs = [i for i in counts if i[0] not in ['无名氏', '不详', '韩']]

    print("{}语料库总词牌数:".format(file.rstrip('.txt')), len(counter))
    print("{}最受欢迎的词牌:".format(file.rstrip('.txt')), count_pairs[:80])
    print()
    return count_pairs


def main():
    file = '宋词.txt'
    count_pairs = analye(file)
    pic(count_pairs[:100], file)

if __name__ == '__main__':
    main()