
import os 
import random
import pyecharts
from pyecharts import Pie
from collections import Counter
from random import seed
from random import randint
from pyecharts import WordCloud


main_file = 'data_cut/'

def pic(data, file):
    
    pyecharts.configure(
    jshost=None,
    echarts_template_dir=None,
    force_js_embed=None,
    output_image=None,
    global_theme='infographic'
    )
    all_poet = [i[0] for i in data[:30]]
    all_num = [i[1] for i in data[:30]]
    br = pyecharts.Bar(title=file.rstrip('.txt')+'最常见的地名', title_top=0,  width=1200, height=700,)

    br.add('', all_poet, all_num,  label_pos='center',is_convert=True, xaxis_interval=0, yaxis_interval=0, is_yaxis_inverse=True)
    br.use_theme('infographic')
    br.render(path=file.rstrip('.txt')+'最常见的地名_条形图'+'.html')

    all_poet = [i[0] for i in data[:700]]
    all_num = [i[1] for i in data[:700]]
    wordcloud = WordCloud(title=file.rstrip('.txt')+'最常见的地名'+'\n\n', title_pos='center', width=1500, height=800, )
    shape = ['circle', 'cardioid', 'diamond', 'triangle-forward', 'triangle', 'pentagon', 'star']
    wordcloud.add('', all_poet,  all_num,
                    shape= random.choice(shape),
                    word_gap=20,
                    word_size_range=[10, 120],  
                    rotate_step=70)
    wordcloud.render(path=file.rstrip('.txt')+'最常见的地名_词云'+'.html')


def analye(file):
    avi_l = ['ns', 'nsf']
    word_count = []
    word_c = []
    poems = eval(open(main_file+file, encoding='utf-8').read())
    for word,tag in poems:
        if tag[0] in avi_l and len(word) > 1:
            word_count.append((word, tag[1]))
            word_c.append((word, tag))

    print("{}最常见的地名:".format(file.rstrip('.txt')), word_c[:100])
    print()
    return word_count


def main():
    for root, dirs, files in os.walk(main_file): 
        for file in files:
            count_pairs = analye(file)
            pic(count_pairs, file)

if __name__ == '__main__':
    main()