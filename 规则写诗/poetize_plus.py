# -*- coding: utf-8 -*-
import random
import time
from pypinyin import pinyin, Style
from snownlp import SnowNLP

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
typ_list = ['s', 'a', 'c', 'd', 'f', 'i', 'n', 'o', 'p', 'q', 'u', 'v', 'y']
typ_list_n = []     # 用于存储可用的词性tpy
typ_dict = dict(zip(typ_list, typ_list))
longest = {}  # 储存每类词中最长词长度


def get_kind():
    '''获取用户所需语料库'''
    kind2file = {'1':'songshi', '2':'tangshi', '3':'songci', '4':'shijing', '5':'modern'}
    print('提示：直接输入序号哟')
    kind = input('您需要我创作什么？\n1.宋诗 2.唐诗 3.宋词 4.诗经 5.现代诗\n')
    while kind not in ['1', '2', '3', '4', '5']:
        kind = input('请输入序号哦：\n')

    file = kind2file[kind] + '_body.txt_关键词提取'
    mode = int(kind)
    return file, mode


def rd(typ, lenth):
    '''按照词性和词长随机匹配最佳的词'''
    ci = ''  # 获取随机词
    if lenth > longest[typ]:
        ci = rd(typ, 2)+rd(typ, lenth-2)  # 递归
    elif lenth == 1:
        rand = random.randint(0, len(typ_dict[typ])-1)
        ci = typ_dict[typ][rand]
        ci = ci[random.randrange(len(ci))]
    else:
        count = 0
        while len(ci) != lenth:
            rand = random.randint(0, len(typ_dict[typ])-1)
            ci = typ_dict[typ][rand]
            count += 1
    return ci


def get_poem(model):
    '''根据词性模式获取诗句'''
    model = model.strip('/')+'/'
    i = 0
    poem = ''
    while i < len(model)-1:  # 获取同字符最长匹配
        if model[i] in typ_list_n:
            length = 1
            j = i+1
            while j < len(model)-1:
                if model[j] == model[i]:
                    length += 1
                else:
                    break
                j += 1
            ci = rd(model[i], length)
            i += length

        else:
            ci = model[i]
            i += 1
        poem += ci
    return poem


def get_line_tone(model, tone):
    '''按照词性模式和平仄模式得到诗句'''
    line = ''
    i = 0
    while i < len(model):
        length = 1
        j = i+1
        while j < len(model):
            if model[j] == model[i]:
                length += 1
            else:
                break
            j += 1
        ci = rd(model[i], length)
        while not match_tone(ci, tone[i:j]):
            ci = rd(model[i], length)
        i += length
        line += ci
    return line

    
def match_tone(ci, tone_ci):  
    '''判断字词是否符合相应平仄'''
    judge = True
    for i in range(len(ci)):
        diao = pinyin(ci[i], style=9, errors='ignore')[0][0][-1]
        if tone_ci[i] == 'x':
            pass
        elif tone_ci[i] == '0' and diao in ['1', '2']:
            pass
        elif tone_ci[i] == '1' and diao in ['3', '4', 'i']:
            pass
        else:
            judge = False
    return judge

    # yn:首行是否押韵，0押，1不押
def get_tone(tag, yn=random.randint(0, 1)):     
    '''以下平仄模式码，由平仄.txt文件处理后获取，详见规则写诗目录'''
    # pz_dict = {       # 1仄 0平 x任意  10:仄起平收 01:平起仄收 y首句押韵 n首句不押韵
    # 'wujue_10_y': 'x1100/00110/x0011/x1100/',
    # 'wujue_10_n': 'x1001/00110/x0011/x1100/',
    # 'wujue_01_y': '00110/x1100/x1001/00110/',
    # 'wujue_01_n': 'x0011/x1100/x1001/00110/',

    # 'wulv_10_y': 'x1100/00x10/x0x11/x1100/x1x01/00x10/x0x11/x1100/',
    # 'wulv_10_n': 'x1x01/00x10/x0x11/x1100/x1x01/00x10/x0x11/x1100/',
    # 'wulv_01_y': '00x10/x1100/x1x01/00x10/x0x11/x1100/x1x01/00x10/',
    # 'wulv_01_n': 'x0x11/x1100/x1x01/00x10/x0x11/x1100/x1x01/00x10/',

    # 'qijue_10_y': 'x100110/x0x1100/x0x1001/x100110/',
    # 'qijue_10_n': 'x1x0011/x0x1100/x0x1001/x100110/',
    # 'qijue_01_y': 'x0x1100/x100110/x1x0011/x0x1100/',
    # 'qijue_01_n': 'x0x1001/x100110/x1x0011/x0x1100/',

    # 'qilv_10_y': 'x100x10/x0x1100/x0x1x01/x100x10/x1x0x11/x0x1100/x0x1x01/x100x10/',
    # 'qilv_10_n': 'x1x0x11/x0x1100/x0x1x01/x100x10/x1x0x11/x0x1100/x0x1x01/x100x10/',
    # 'qilv_01_y': 'x0x1100/x100x10/x1x0x11/x0x1100/x0x1x01/x100x10/x1x0x11/x0x1100/',
    # 'qilv_01_n': 'x0x1x01/x100x10/x1x0x11/x0x1100/x0x1x01/x100x10/x1x0x11/x0x1100/'
    # }
    pz_dict = {             # 古诗平仄表  1仄 0平 x任意
    '1': [['x1100/00110/x0011/x1100/',
           'x1001/00110/x0011/x1100/',],
          ['00110/x1100/x1001/00110/',
           'x0011/x1100/x1001/00110/',]],
    '2': [['x1100/00x10/x0x11/x1100/x1x01/00x10/x0x11/x1100/',
           'x1x01/00x10/x0x11/x1100/x1x01/00x10/x0x11/x1100/',],
          ['00x10/x1100/x1x01/00x10/x0x11/x1100/x1x01/00x10/',
           'x0x11/x1100/x1x01/00x10/x0x11/x1100/x1x01/00x10/',]],
    '3': [['x100110/x0x1100/x0x1001/x100110/',
           'x1x0011/x0x1100/x0x1001/x100110/',],
          ['x0x1100/x100110/x1x0011/x0x1100/',
           'x0x1001/x100110/x1x0011/x0x1100/',]],
    '4': [['x100x10/x0x1100/x0x1x01/x100x10/x1x0x11/x0x1100/x0x1x01/x100x10/',
           'x1x0x11/x0x1100/x0x1x01/x100x10/x1x0x11/x0x1100/x0x1x01/x100x10/',],
          ['x0x1100/x100x10/x1x0x11/x0x1100/x0x1x01/x100x10/x1x0x11/x0x1100/',
           'x0x1x01/x100x10/x1x0x11/x0x1100/x0x1x01/x100x10/x1x0x11/x0x1100/',]]
    }
    # print('yn:', yn)
    return pz_dict[tag][yn][random.randint(0, 1)], yn


def rhyme(foot):
    '''获取韵脚所在辙'''    
    rhyme_list = [['a', 'ua', 'ia'],    # 十三辙韵母表
                  ['e', 'o', 'uo'],
                  ['ie', 've'],
                  ['i', 'v', 'er'],
                  ['u', 'uu'],
                  ['ai','uai'],
                  ['ei','uei','ui'],
                  ['ao', 'iao'],
                  ['ou', 'iou', 'iu'],
                  ['an', 'ian', 'uan', 'van'],
                  ['en', 'in', 'uen', 'un', 'vn'],
                  ['ang', 'iang', 'uang'],
                  ['eng', 'ing', 'ueng', 'ong', 'iong']]
    zhe = None
    for i in range(len(rhyme_list)):
        if foot in rhyme_list[i]:
            zhe = i
            break
    return zhe


def plus_point(item):  
    '''为诗句加标点'''
    item_list = item.split('/')
    i = 0
    for j in range(len(item_list)-1):
        if i%2 == 0:
            item_list[j]+='，'
        else:
            item_list[j]+='。'
        i+=1
    res = '/'.join(i for i in item_list)
    return res


def get_foot(line):
    '''获取诗句韵脚'''
    return pinyin(line, style=9, errors='ignore')[-1][0][:-1]


def isChinese(s):
    '''判断输入是否为中文'''
    for c in s:
        if not('\u4e00' <= c <= '\u9fa5'):
            return False
    return True


def model_shi():
    '''创作古诗'''
    wujue = ['nnvss/nnvss/nnvvn/nnvvn/', 'nvnvn/nvnvn/nnvss/nnvss/']
    wulv = ['nnvvn/nnvvn/nnvvn/nnvvn/'*2, 'nvnvn/nvnvn/nnvss/nnvss/'*2]
    qijue = ['nvnvnnv/nvnvnnv/nnvvnnv/nnvvnnv/', 'nvnnvvn/nvnnvvn/nnvvnns/nnvvnss/']
    qilv = ['nvnvnnv/nvnvnss/nnvvnnv/nnvvnss/'*2, 'nvnnvvn/nvnnvvn/nnvvnnv/nnvvnss/'*2]

    tune_ = '0'
    while tune_ not in ['1', '2', '3']:
        tune_ = input('需要平仄且押韵么？\n1.yao！切克闹 2.不为难你啦 3.不仅押，还要自定义韵脚！\n')

    # rhyme_ = '0'
    # while rhyme_ not in ['1', '2']:
    #     rhyme_ = input('是否押韵？\n1.鸭 2.不用了\n')

    tag = '0'
    while tag not in ['1', '2', '3', '4']:
        tag = input('您需要什么格式：\n1.五言绝句 2.五言律诗 3.七言绝句 4.七言律诗\n')

    geshi = {'1': wujue, '2': wulv, '3': qijue, '4': qilv}
    model = geshi[tag][random.randrange(len(geshi[tag])-1)]  # 从预设格式中随机
    if tune_ == '2':
        output(get_poem(plus_point(model)))

    elif tune_ == '1':
        tune, yn = get_tone(tag, yn=random.randint(0, 1))    # yn 表示首行是否押韵
        # print(tune, model)
        tune = tune.strip('/').split('/')
        model = model.strip('/').split('/')
        poem = ''
        for i in range(len(model)):
            foot_list = []
            # print('第{}句创作中...\n'.format(i+1))
            foot = ''
            line = get_line_tone(model[i], tune[i])

            if i == yn:      # 获取韵脚，这里很巧妙的是yn正好对应0或者1处获取韵脚
                foot = get_foot(line)

                # print(foot, line)

            count = 0
            while i%2 == 1 and rhyme(foot) != rhyme(get_foot(line)) and count < 2000:
                # print('不押韵，再来：')
                line = get_line_tone(model[i], tune[i])     # 循环匹配韵脚，1000次匹配不到就结束
                # print(line+'\n')
                count += 1
            poem += line + '/'
        poem = plus_point(poem)
        output(poem)

    else:
        word = input('请输字、词或句，将其尾韵作为韵脚:\n')
        while not isChinese(word):
            word = input('俺不认识这玩意儿，输入汉字哟：\n')
        foot = get_foot(word)
        model = model.strip('/').split('/')
        poem = ''
        for i in range(len(model)):
            line = get_poem(model[i])
            count = 0
            while i%2 == 1 and rhyme(foot) != rhyme(get_foot(line)) and count <2000:
                line = get_poem(model[i])
                count += 1
            poem += line + '/'
        poem = plus_point(poem)
        output(poem)
    return 0


def model_ci():
    '''创作宋词'''
    cipai = input('选择词牌名：\n1.浣溪沙 2.鹧鸪天 3.长相思 4.临江仙 5.梦江南\n')
    while cipai not in ['1', '2', '3', '4', '5']:
        cipai = input('机灵鬼，请输入序号：')
    浣溪沙 = 'uuvvsnn，uuvvnns，nnvviii。/iiiivvn，nannvss，nnddssv。'
    鹧鸪天 = 'nnaavnn，iissvnn，aannssv，vvnniii。/iii，vnn，iiiicnn。uuvvsnn，iiiivss！'
    长相思 = 'nnv，uuv。iiiissv,nnaan。/naa，naa。nvssiii,nanvn。'
    临江仙 = 'aanniii，nnvvuu。 uunniii。 iiiii，iiiia。/aanniii，vvuuuu。 aanniii。 nniii，vvnnv。'
    梦江南 ='ssn，nndda。/iiiiadd，iiiiadd。/ssvuu。'
    geshi = {'1': 浣溪沙,'2': 鹧鸪天,'3': 长相思, '4': 临江仙, '5': 梦江南}
    name = {'1': '浣溪沙','2': '鹧鸪天', '3': '长相思', '4': '临江仙', '5': '梦江南'}
    model = geshi[cipai]
    poem = get_poem(model)
    print()
    title = name[cipai]+'·'+poem.split('，')[0]
    print(title.center(len(poem.split('/')[0])*2 + 2))
    output(poem)
    return model


def model_jing():
    '''创作诗经'''
    models = ['nnvv，ssnn？/', 'ddnn，ssuu。/', 'uuss，nnss。/', 'aann，aann。/',
              'vvuu，uuss。/', 'ssnn，vvuu。/', 'ssuu，iiii。/', 'iiii，nnss。/',
              'ssuu，iiii。/', 'uuss，nnss。/', 'nnvv，ssnn。/', 'aann，aann。/',
              'vvuu，uuss。/', 'ssnn，vvuu。/', 'ssuu，iiii。/', 'iiii，nnss。/',
              'ssuu，iiii。/', 'uuss，nnss。/', 'nnvv，ssnn。/', 'aann，aann。/']
    model = ''
    for i in range(int(input('输入诗经行数，我可以无限创作哟！\n'))):
        model += models[random.randint(0, len(models)-1)]
    output(get_poem(model))



def model_modern():
    '''创作现代诗'''
    models = ['iii', 'iiii', 'iiii', 'nvviiii', 'yy', 'aa的nn', 'cc', 'nnvvoo',
              'ppnn', 'qqnnaayy', 'aaaannaa', 'nnvvnn', 'iiiaa', 'cccc', 'nn，aa而aa',
              'oo', 'vnn，vnn', 'iii', 'nnvviii', 'ssnnvvsss', 'iiy', 'iiiy', 'ssnnvvnn',
              'iii', 'iii']
    line = input('为你写诗，君要几句呢？\n')
    while not line.isdigit() or int(line) >= 500:
        line = input('请输入小于500数字：')
    model = ''
    for i in range(int(line)):
        model += models[random.randint(0, len(models)-1)]
        if random.random() > 0.6:
            model += '，'
        elif random.random() > 0.7:
            model += '。/'
        else:
            model += '/'
    output(get_poem(model))


def free_poem():
    '''自由创作'''
    play = '1'
    while play == '1':
        mymodel = input('输入您需要的格式:(输入“h”，获取帮助)\n')
        if mymodel == 'h':
            print('''
            欢迎使用自由创作功能！
            /：换行
            s：随机词语
            n：名词
            v：动词
            a：形容词
            d：副词
            c:连词
            i:成语 习语
            y:语气词 叹词
            o:拟声词
            p:介词
            q:量词
            f:方位词
            u:未知神秘高频词
            本语料库可用词性有{}
            您可以输入您想要的格式来创作诗歌：
            比如，输入“nnvnn，/nnvnn。/nnvvn，/nnvvn。” 会写出五言绝句。
            (可以在句中加入标点、藏头、藏尾、藏字)
                  '''.format(typ_list_n))
            mymodel = input('请输入您的格式：')
        output(get_poem(mymodel))
        play = input('还要继续自由作诗吗？1.好呀 2.不玩了\n')


def output(poem):
    '''美化输出格式'''
    poem = poem.strip('/')
    lenth = len(poem.split('/')[0])*2 + 8
    print()
    print('-'*lenth)
    print()
    for i in poem.split('/'):
        print('     '+i)
    print()
    print('-'*lenth)
    print()
    snow = SnowNLP(poem)
    print("情感倾向：{}".format(snow.sentiments))
    print()
    print()
    time.sleep(random.random()*2)



def main():
    file, mode = get_kind()
    print('正在读取语料库中...\n')
    
    for key in typ_list:
        try:
            typ_dict[key] = open(file+'\\'+file+'_'+key+'.txt', encoding='utf-8').read().split()
            if len(typ_dict[key]) > 0:
                length = 0
                for i in typ_dict[key]:     # 获取同一词性的最长词语的长度
                    if len(i) > length:
                        length = len(i)
                longest[key] = length
                typ_list_n.append(key)
        except:
            pass

    free = input('想要自由定义格式吗？\n1.用内置格式 2.自己作诗！\n')
    while free not in ['1', '2']:
        free = input('请输入序号：')
    if free == '2':
        free_poem()
    else:
        cont = '1'
        while cont == '1':
            if mode in (1, 2):
                model_shi()
            elif mode == 3:
                model_ci()
            elif mode == 4:
                model_jing()
            else:
                model = model_modern()

            cont = input('想继续赏析我的作品吗？\n1.再来一首 2.你太棒了，我不看了\n')


if __name__ == '__main__':
    goon = '1'
    while goon == '1':
        typ_list_n = []     # 再次初始化，以便重新统计
        longest = {}
        main()
        goon = input('1.返回最开始 2.退出\n')
    exit()