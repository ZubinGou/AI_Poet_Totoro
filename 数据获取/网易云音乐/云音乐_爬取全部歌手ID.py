import requests
import re


class SingerSpider(object):
    def __init__(self):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'music.163.com',
            'Referer': 'http://music.163.com/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/66.0.3359.181 Safari/537.36'
        }

    def get_index(self, url):
        try:
            resp = requests.get(url, headers=self.headers)
            if resp.status_code == 200:
                self.parse_re(resp.text)
            else:
                print('error')
        except ConnectionError:
            self.get_index(url)

    def parse_re(self, resp):
        tags = re.findall(r'<a href=".*?/artist\?id=(\d+)" class="nm nm-icn f-thide s-fc0" title=".*?的音乐">(.*?)</a>', resp, re.S)
        title = re.findall(r'<title>(.*?)-.*?</title>', resp, re.S)
        for tag in tags:
            self.save_txt(tag, title)

    def save_txt(self, tag, title):
        with open('all_singer.txt', 'a', encoding='utf-8') as f:
            f.write((title[0].rstrip().replace('/', '&')+'::'+tag[1]+'::'+tag[0]+'\n'))

if __name__ == '__main__':
    # 歌手分类id
    list1 = [1001, 1002, 1003]
    # initial的值
    list2 = [0, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76,
             77, 78, 79, 80,81, 82, 83, 84, 85, 86, 87, 88, 89, 90]
    for i in list1:
        for j in list2:
            url = 'http://music.163.com/discover/artist/cat?id=' + str(i) + '&initial=' + str(j)
            print('finding id from {}'.format(url))
            SingerSpider().get_index(url)