
import os 
import pyecharts
from collections import Counter
from random import seed
from random import randint


main_file = 'data/'

def pic(data, file):
    all_poet = [i[0] for i in data]
    all_num = [i[1] for i in data]
    br = pyecharts.Bar(title=file.rstrip('.txt')+'高产作家', title_top=0,  width=1200, height=700,)

    br.add('', all_poet, all_num,  label_pos='center',is_convert=True, xaxis_interval=0, yaxis_interval=0, is_yaxis_inverse=True)

    br.render(path=file.rstrip('.txt')+'高产作家'+'.html')


def analye(file):
    poets = []
    poems = open(main_file+file, encoding='utf-8')
    for poem in poems:
        poets.append(poem.split('::')[1])
    counter = Counter(poets)
    counts = counter.most_common()
    count_pairs = [i for i in counts if i[0] not in ['无名氏', '不详', '韩']]

    print("{}总诗人数:".format(file.rstrip('.txt')), len(counter))
    print("{}高产作家:".format(file.rstrip('.txt')), count_pairs[:80])
    print()
    return count_pairs


def main():
    for root, dirs, files in os.walk(main_file): 
        for file in files:
            count_pairs = analye(file)
            pic(count_pairs[:25], file)

if __name__ == '__main__':
    main()