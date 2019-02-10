
import os 
import pyecharts
from pyecharts import Pie
from collections import Counter
from random import seed
from random import randint


main_file = 'data_body/'

def pic(data, file):
    all_poet = [i[0] for i in data]
    all_num = [i[1] for i in data]
    pie = Pie(title=file.rstrip('2.txt')+'中的四季', title_pos='center')
    pie.add(
        "",
        all_poet,
        all_num,
        radius=[40, 75],
        label_text_color=None,
        is_label_show=True,
        legend_orient="vertical",
        legend_pos="left",
    )

    pie.render(path=file.rstrip('2.txt')+'中的四季'+'.html')


def analye(file):
    seasons = ['春', '夏', '秋', '冬']
    seasons_count = {'春':0, '夏':0, '秋':0, '冬':0}
    poems = open(main_file+file, encoding='utf-8')
    for poem in poems:
        for i in seasons:
            seasons_count[i] += poem.count(i)
    seasons_count_list = [(x,y) for x,y in seasons_count.items()]

    print("{}中的四季:".format(file.rstrip('2.txt')), seasons_count_list)
    print()
    return seasons_count_list


def main():
    for root, dirs, files in os.walk(main_file): 
        for file in files:
            count_pairs = analye(file)
            pic(count_pairs, file)

if __name__ == '__main__':
    main()