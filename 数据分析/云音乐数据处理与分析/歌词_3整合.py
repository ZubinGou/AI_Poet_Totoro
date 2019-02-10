import os
import re


if __name__ == '__main__':
    main_dir = '全部华语歌手_unique/'
    for root, dirs, files in os.walk(main_dir): 
        for dir in dirs:
            data_dir = main_dir + dir
            save_file = '全部华语歌手_yeah/' + dir +'.txt'
            save_data = open(save_file, 'w+', encoding='utf-8')
            if not os.path.exists(save_file):  # 保存文件
                os.mkdir(save_file)
            for root1, dirs1, files1 in os.walk(main_dir+dir):
                for file in files1:
                    data = open(main_dir+dir+'/'+file, encoding='utf-8')
                    for line in data:
                        line = line.strip(' ').strip('.').strip(',').strip('\n')
                        tag = re.findall(r'[a-zA-Z0-9＃/\～（）*《》><—︿——”」「“]|搜索|分类标签|云音乐|歌曲|下载|歌单|歌词|分享给|收藏|播放', line)
                        new_line = re.sub(r"\-\d*\-|\（.*?\）|\(.*?\)|\{.*?\}|\[.*?\]|\【.*?\】|\〖.*?\〗|\.|\#|\…|\~|\`", "", line)
                        if new_line != '' and len(new_line) > 4 and len(tag) < 1 :      # 太短歌词句子不要
                            save_data.write(new_line+'\n')
                    data.close()
            print('整合完毕：{}'.format(save_file))
            save_data.close()


