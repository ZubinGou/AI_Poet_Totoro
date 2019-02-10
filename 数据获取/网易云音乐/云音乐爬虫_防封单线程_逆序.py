import os
import json
import requests
# from multiprocessing import Pool
from bs4 import BeautifulSoup
from functools import reduce

base_url = "http://music.163.com"
start_url = base_url + "/artist/album?id={}&limit=100"  # 根据歌手的id，抓取其专辑列表
song_url = base_url + "/api/song/lyric?id={}&lv=1&kv=1&tv=-1"  # 根据歌曲的id，抓取歌词

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

# proxies = {"https": "https://118.122.92.252:37901",}  # 119.101.115.211:9999    221.226.162.198:9999


def replace_char(s):  # 替换目录禁止的字符
    return reduce(lambda s, char: s.replace(char, '_'), ' *:\\/.?#<>|\"', s)


def get_html(url):  # requests抓取
    resp = requests.get(url, headers=headers)
    html = str(resp.content, encoding='utf-8')
    return html


def crawl_lyrics(gender, art_id):
    """抓取一整个歌手的所有歌词"""
    html = get_html(start_url.format(art_id))  # 先抓该歌手的专辑列表
    soup = BeautifulSoup(html, 'lxml')

    artist = replace_char(soup.find('h2', id='artist-name').text)
    artist_dir = ('全部华语歌手/' + gender + '/' + artist)
    if not os.path.exists(artist_dir):  # 歌手目录
        os.mkdir(artist_dir)
    print("歌手名：", artist)
    try:
        albums = soup.find('ul', class_='m-cvrlst').find_all('a', class_='msk')  # 专辑列表
        for album in albums:
            html = get_html(base_url + album.get('href'))  # 再抓取该专辑下歌曲列表
            soup = BeautifulSoup(html, 'lxml')

            album_title = replace_char(soup.find('h2', class_='f-ff2').text)
            album_dir = os.path.join(artist_dir, album_title)
            if not os.path.exists(album_dir):  # 专辑目录
                os.mkdir(album_dir)
            print("  " + artist + "---" + album_title)

            links = soup.find('ul', class_='f-hide').find_all('a')  # 歌曲列表
            for link in links:
                song_name = replace_char(link.text)
                song_id = link.get('href').split('=')[1]
                html = get_html(song_url.format(song_id))  # 抓取歌词

                try:  # 存在无歌词的歌曲，直接忽略
                    lyric_json = json.loads(html)
                    lyric_text = lyric_json['lrc']['lyric']

                    open(os.path.join(album_dir, song_name + '.txt'), 'w', encoding='utf-8').write(lyric_text)
                    print("    " + song_name + ", URL: " + song_url.format(song_id))
                except:
                    pass
                    print("    " + song_name + ": 无歌词, URL: " + song_url.format(song_id))
            print()
    except:
        pass

if __name__ == '__main__':
    dir_ = ['全部华语歌手', '全部华语歌手\\华语男歌手', '全部华语歌手\\华语女歌手', '全部华语歌手\\华语组合&乐队']
    for i in dir_:
        try:
            os.mkdir(i)
        except FileExistsError:
            pass

    done_id = set()
    if os.path.exists('done_id.txt'):
        print('正在从上次爬取数据中恢复...')
        done_file = open('done_id.txt', 'r')
        done_id = done_file.read()
        done_id = eval(done_id)
        done_file.close()
        print('之前已经爬取了{}个歌手的全部歌词了'.format(len(done_id)))

    with open('all_singer.txt', 'r', encoding='utf-8') as f:
        a = reversed(f.readlines())
        for line in a:
            gender = line.strip().split('::')[0]
            art_id = line.strip().split('::')[2]

            if art_id not in done_id:
                crawl_lyrics(gender, art_id)
                done_id.add(art_id)
                done_file = open('done_id.txt', 'w')
                done_file.write(str(done_id))
                done_file.close()
                print('已经爬取了{}个歌手的全部歌词了'.format(len(done_id)))
