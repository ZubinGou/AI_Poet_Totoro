import requests
import pyperclip
import time
import re
from bs4 import BeautifulSoup

seen = set()
useen = {'2018-11-22/8146223'}   # {''}2018-12-18/7993321
file_obj = open("zgsg2.txt", 'a', encoding='utf-8')


def url2http(url):
    base_url = "http://www.zgshige.com//c/"
    return base_url + url + '.shtml'


def getsoup(url):
    http = url2http(url)
    response = requests.get(http)
    soup = BeautifulSoup(response.content.decode('utf-8'), 'lxml')
    return soup


def parse(soup):
    # title = soup.find('h3').text
    # writer = soup.find('div', class_="col-xs-12").find('span').text.split()[1]
    poems = soup.find('div', class_="m-lg font14", style=None)
    if poems is None:
        poems = soup.find(lambda tag: tag.name == 'div' and tag.get('class') == ['p-l-sm'])
    if poems is None:
        poems = soup.find('span', style="font-family: 宋体, SimSun; font-size: 16px;")
    if poems:
        poem = poems.get_text('\n', 'br/')
        if poem.count('\n') < 1 or len(poem) > 3000:
            poem = None
    else:
        poem = None
    if poem is None:
        print(url2http(url))

    urls = soup.find_all('a', {'href': re.compile(r'\d{4}-\d{2}-\d{2}/\d{7}')})
    return poem, urls


def update_useen(urls):
        for i in urls:
            if i not in seen:
                useen.add(re.search(r'\d{4}-\d{2}-\d{2}/\d{7}', str(i)).group())


t1 = time.time()
count = 0
while count < 100:
    url = useen.pop()
    seen.add(url)
    soup = getsoup(url)
    poem, urls = parse(soup)

    if poem is not None:
        file_obj.write(poem)
        count += 1
        print('正在慢速爬取第{}首诗'.format(count))
        print('第{}首 Downloading from {}...'.format(count, url2http(url)))
    update_useen(urls)

    # file_obj.write(title+'::'+writer+'::'+poem)
file_obj.close()
print('2号爬虫爬取{}首诗，用时{}秒'.format(count, time.time()-t1))
input('input any to exit')