# coding: utf-8

import re
import os
import shutil


def open_file(filename, mode='r'):
    return open(filename, mode=mode, encoding='utf-8', errors='ignore')


def is_chinese(text):
    text = ''.join([x.strip() for x in text.split('\n')])
    res = ' '.join([r for r in re.findall(r"[\u4e00-\u9fa5]+", text)])  # 中文字符区间
    return len(res) >= 0.8 * len(text)  # 8成以上是中文


def clean_text(filename):
    text = open_file(filename).read()
    text = re.sub(r"\[.*\]", "", text)  # 过滤时间轴
    text = re.sub(r"作词.*\n", "", text)  # 过滤掉工作人员
    text = re.sub(r"作曲.*\n", "", text)
    text = re.sub(r"编曲.*\n", "", text)
    text = re.sub(r"演唱.*\n", "", text)
    text = re.sub(r"制作人.*\n", "", text)
    text = re.sub(r".*:", "", text)
    text = re.sub(r".*：", "", text).strip()
    return text


def read_convert_words(filename):
    """读取繁简字体转换表"""
    tr_to_cn = {}
    with open_file(filename) as f:
        for line in f:
            value, key = line.strip().split('→')
            tr_to_cn[key] = value
    return tr_to_cn


def convert_tr_to_cn(sentence, tr_to_cn):
    """繁简转换"""
    cn_s = ''
    for x in sentence:
        if x in tr_to_cn:
            x = tr_to_cn[x]
        cn_s += x
    return cn_s


def lyric_filter():
    global base_dir, new_dir
    if os.path.exists(new_dir):
        shutil.rmtree(new_dir)
    os.mkdir(new_dir)

    cnt = 0  # 编号
    tr_to_cn = read_convert_words('tr-to-cn.txt')
    for cur_dir in os.walk(base_dir):  # 遍历所有文档
        for filename in cur_dir[2]:
            try:
                data = clean_text(os.path.join(cur_dir[0], filename))
                if is_chinese(data) and len(data) >= 50:  # 中文，50字符以上
                    data = convert_tr_to_cn(data, tr_to_cn)  # 转换为简体
                    filename = convert_tr_to_cn(filename, tr_to_cn)

                    new_file = ''.join(filename.split('.')[:-1]) + ' - ' + str(cnt) + '.txt'  # 防止重名覆盖，打个编号
                    open_file(os.path.join(new_dir, new_file), 'w').write(data)   # 汇总写入新目录
                    cnt += 1
            except:
                pass


if __name__ == '__main__':
    main_dir = "全部华语歌手"
    main_new_dir = "全部华语歌手_clean"
    if not os.path.exists(main_new_dir):
        os.mkdir(main_new_dir)
    for i in ['华语组合&乐队', '华语男歌手', '华语女歌手']:
        base_dir = main_dir + '\\' + i
        new_dir = main_new_dir + '\\'+ i
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
        lyric_filter()
