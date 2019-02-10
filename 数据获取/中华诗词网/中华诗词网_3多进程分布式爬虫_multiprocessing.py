import requests
import time
import re
import os
import multiprocessing as mp
from bs4 import BeautifulSoup


def main(url):
    base_url = "http://www.zgshige.com//c/"
    http = base_url + url + '.shtml'

    response = requests.get(http)
    soup = BeautifulSoup(response.content.decode('utf-8'), 'lxml')
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

    urls = soup.find_all('a', {'href': re.compile(r'\d{4}-\d{2}-\d{2}/\d{7}')})
    page_urls = set()
    for i in urls:
        page_urls.add(re.search(r'\d{4}-\d{2}-\d{2}/\d{7}', str(i)).group())
    return page_urls, poem


if __name__ == '__main__':
    t1 = time.time()
    if os.path.exists('seen_data.txt'):
        print('正在从上次爬取数据中恢复...')
        seen_file = open('seen_data.txt', 'r')
        seen_data = seen_file.read()
        seen = eval(seen_data)
        seen_file.close()

    file_obj = open("zgsg3.txt", 'a', encoding='utf-8')
    seen = set()
    useen = {'2018-12-28/8100703', }   # {''}2018-12-18/7993321
    pool = mp.Pool(mp.cpu_count())
    count = 0
    while count < 100:
        proc = [pool.apply_async(main, args=(url,)) for url in useen]
        res = [j.get() for j in proc]
        seen.update(useen)
        useen.clear()
        for page_urls, poem in res:
            if poem is not None:   # save poem
                file_obj.write(poem)
                count += 1
                print('正在爬取第{}首 Downloading ......'.format(count))
            useen.update(page_urls-seen)
            if len(useen) > 80:
                useen = set(list(useen)[:80])     # 不断测试发现 80 个一起效率最高
    file_obj.close()
    seen_file = open('seen_data.txt', 'w')
    seen_file.write(str(seen))
    seen_file.close()
    
    print('3号爬虫爬取{}首诗，用时{}秒'.format(count, time.time()-t1))
    input('input any to exit')
