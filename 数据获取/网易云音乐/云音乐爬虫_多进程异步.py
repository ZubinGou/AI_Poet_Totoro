import os
import json
import requests
from multiprocessing import Pool
from bs4 import BeautifulSoup
from functools import reduce

base_url = "http://music.163.com"
start_url = base_url + "/artist/album?id={}&limit=100"  # 歌手id，抓取专辑
song_url = base_url + "/api/song/lyric?id={}&lv=1&kv=1&tv=-1"  # 歌曲id，抓取歌词

# 较为完整的header
# headers = {
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#         'Accept-Encoding': 'gzip, deflate',
#         'Accept-Language': 'zh-CN,zh;q=0.9',
#         'Connection': 'keep-alive',
#         'Host': 'music.163.com',
#         'Referer': 'http://music.163.com/',
#         'Upgrade-Insecure-Requests': '1',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
#                       'Chrome/66.0.3359.181 Safari/537.36'
#             }

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    "Referer": "http://music.163.com",
    "Host": "music.163.com"
}


# 使用ip代理 防止被封，本来打算建个ip池，因时间原因未写
# proxies = {"https": "https://118.122.92.252:37901",}  # 119.101.115.211:9999  221.226.162.198:9999
# 后由于免费ip速度慢，故而放弃

def replace_char(s):  # 替换目录禁止的字符
    return reduce(lambda s, char: s.replace(char, '_'), ' *:\\/.?#<>|\"', s)


def get_html(url):  # 抓取
    resp = requests.get(url, headers=headers)
    html = str(resp.content, encoding='utf-8')
    return html


def crawl_lyrics(gender, art_id):
    '''抓取art_id歌手的全部歌词'''
    html = get_html(start_url.format(art_id))  # 抓取专辑列表
    soup = BeautifulSoup(html, 'lxml')

    artist = replace_char(soup.find('h2', id='artist-name').text)
    artist_dir = ('全部华语歌手/' + gender + '/' + artist)
    if not os.path.exists(artist_dir):  # 歌手目录
        os.mkdir(artist_dir)
    # print("歌手名：", artist)
    try:
        albums = soup.find('ul', class_='m-cvrlst').find_all('a', class_='msk')  # 专辑列表
        for album in albums:
            html = get_html(base_url + album.get('href'))  # 该专辑下歌曲列表
            soup = BeautifulSoup(html, 'lxml')

            album_title = replace_char(soup.find('h2', class_='f-ff2').text)
            album_dir = os.path.join(artist_dir, album_title)
            if not os.path.exists(album_dir):  # 专辑目录
                os.mkdir(album_dir)
            else:
                return 0
            # print("  " + artist + "---" + album_title)

            links = soup.find('ul', class_='f-hide').find_all('a')  # 歌曲列表
            for link in links:
                song_name = replace_char(link.text)
                song_id = link.get('href').split('=')[1]
                html = get_html(song_url.format(song_id))  # 抓取歌词

                try:  # 忽略无歌词的歌曲
                    lyric_json = json.loads(html)
                    lyric_text = lyric_json['lrc']['lyric']

                    open(os.path.join(album_dir, song_name + '.txt'), 'w', encoding='utf-8').write(lyric_text)
                    # print("    " + song_name + ", URL: " + song_url.format(song_id))
                except:
                    pass
                    # print("    " + song_name + ": 无歌词, URL: " + song_url.format(song_id))
            # print()
    except:
        pass
    return 1


if __name__ == '__main__':
    dir_ = ['全部华语歌手', '全部华语歌手\\华语男歌手', '全部华语歌手\\华语女歌手', '全部华语歌手\\华语组合&乐队']
    for i in dir_:
        try:
            os.mkdir(i)
        except FileExistsError:
            pass

    done_id2 = set()
    if os.path.exists('done_id2.txt'):
        print('正在从上次爬取数据中恢复...')
        done_file = open('done_id2.txt', 'r')
        done_id2 = done_file.read()
        done_id2 = eval(done_id2)
        done_file.close()
        print('之前已经爬取了{}个歌手的全部歌词了'.format(len(done_id2)))

    syn_num = 200     # 每批次放入预备放入进程池的数量
    pool = Pool(50)   # 同时进程的数量，请根据电脑性能调整防止进程过多导致死机
    # 电脑性能越高，设置同时进程越高，爬取速度越快。八代i7+16g内存 可以设置100个进程左右
    # pool = Pool(processes=os.cpu_count())
    with open('all_singer.txt', 'r', encoding='utf-8') as f:
        undo_id = list(i for i in f if i.strip().split('::')[2] not in done_id2)
        for o in range(5):  # 大概5个循环，1000个歌手左右，不采用ip代理的话，电脑会被封ip
                            # 我的解法是直接手动更换电脑ip，10s可以搞定，就又可以继续运行了
            proc = [pool.apply_async(crawl_lyrics, args=(i.strip().split('::')[0], i.strip().split('::')[2])) for i in undo_id[:syn_num]]
            results = [re.get() for re in proc]

            for i in undo_id[:syn_num]:
                done_id2.add(i.strip().split('::')[2])
            undo_id = undo_id[syn_num:]

            done_file = open('done_id2.txt', 'w')
            done_file.write(str(done_id2))
            done_file.close()
            print('已经爬取了{}个歌手的全部歌词了'.format(len(done_id2)))
        pool.close()
        pool.join()
