# -*- coding: utf-8 -*-
import random
import time

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
    kind2file = {'1':'songshi', '2':'tangshi', '3':'songci', '4':'shijing', '5':'modern'}
    print('提示：直接输入序号哟')
    kind = input('您需要我创作什么？\n1.宋诗 2.唐诗 3.宋词 4.诗经 5.现代诗\n')
    while kind not in ['1', '2', '3', '4', '5']:
        kind = input('请输入序号哦：\n')

    file = kind2file[kind] + '_body.txt_关键词提取'
    mode = int(kind)
    return file, mode


def rd(typ, lenth):
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


def model_shi():
    tag = 0
    while tag not in ['1', '2', '3', '4']:
        tag = input('您需要什么格式：\n1.五言绝句 2.五言律诗 3.七言绝句 4.七言律诗\n')

    wujue = ['nnvnn，/nnvnn。/nnvvn，/nnvvn。', 'nvnvn，/nvnvn。/nnvnn，/nnvnn。']
    wulv = ['nnvvn，/nnvvn。/nnvvn，/nnvvn。/'*2, 'nvnvn，/nvnvn。/nnvnn，/nnvnn。/'*2]
    qijue = ['nvnvnnv，/nvnvnnv。/nnvvnnv，/nnvvnnv。', 'nvnnvvn，/nvnnvvn。/nnvvnnv，/nnvvnnv。']
    qilv = ['nvnvnnv，/nvnvnnv。/nnvvnnv，/nnvvnnv。/'*2, 'nvnnvvn，/nvnnvvn。/nnvvnnv，/nnvvnnv。/'*2]
    geshi = {'1': wujue, '2': wulv, '3': qijue, '4': qilv}
    model = geshi[tag][random.randrange(len(geshi[tag])-1)]  # 从预设格式中随机
    output(get_poem(model))
    return model


def model_ci():
    cipai = input('选择词牌名：\n1.浣溪沙 2.鹧鸪天 3.长相思 4.临江仙 5.梦江南\n')
    while cipai not in ['1', '2', '3', '4', '5']:
        cipai = input('机灵鬼，请输入序号：')
    浣溪沙 = 'uuvvsnn，uuvvnnv，nnvviii。/iiiivvn，nannvvs，nnddsnn。'
    鹧鸪天 = 'nnaavnn，iissvnn，aannssn，vvnniii。/iii，vnn，iiiicnn。uuvvnnv，iiiissn！'
    长相思 = 'nnv，uuv。iiiissn,nnaan。/naa，naa。nvssiii,nanvn。'
    临江仙 = 'aanniii，nnvvuu。 uunniii。 iiiii，iiiia。/aanniii，vvuuuu。 aanniii。 nniii，vvnnv。'
    梦江南 ='iii，nndda。/iiiiadd，iiiiadd。/ssvuu。'
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
                  '''.format(typ_list_n))
            mymodel = input('请输入您的格式：')
        output(get_poem(mymodel))
        play = input('还要继续自由作诗吗？1.好呀 2.不玩了\n')


def output(poem):
    lenth = len(poem.split('/')[0])*2 + 8
    print()
    print('-'*lenth)
    print()
    for i in poem.split('/'):
        print('     '+i)
    print()
    print('-'*lenth)
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
    main()