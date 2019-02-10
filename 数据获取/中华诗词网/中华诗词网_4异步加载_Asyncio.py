import aiohttp
import asyncio
import time
import re
import os
import multiprocessing as mp
from bs4 import BeautifulSoup


file_obj = open("zgsg4.txt", 'a', encoding='utf-8')
seen = set()
useen = {'2019-01-04/8168390', }   # {''}2018-12-29/8100631 2018-12-18/7993321
count = 0


def parse(html):
    soup = BeautifulSoup(html, 'lxml')      # .content.decode('utf-8')
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
    add_count = 0
    if poem is not None:   # save poem
        file_obj.write(poem)
        add_count += 1

    urls = soup.find_all('a', {'href': re.compile(r'\d{4}-\d{2}-\d{2}/\d{7}')})
    page_urls = set()
    for i in urls:
        page_urls.add(re.search(r'\d{4}-\d{2}-\d{2}/\d{7}', str(i)).group())
    return page_urls, add_count


async def fetch(session, url):
    base_url = "http://www.zgshige.com//c/"
    http = base_url + url + '.shtml'
    r = await session.get(http)
    html = await r.text()
    return html


async def main(loop):
    global count
    global seen, useen
    pool = mp.Pool(mp.cpu_count())
    async with aiohttp.ClientSession() as session:
        while count < 10000:
            tasks = [loop.create_task(fetch(session, url)) for url in useen]
            finished, unfinished = await asyncio.wait(tasks)
            htmls = [r.result() for r in finished]

            parse_jobs = [pool.apply_async(parse, args=(html, )) for html in htmls]
            results = [re.get() for re in parse_jobs]

            seen.update(useen)
            useen.clear()
            for page_urls, add_count in results:
                useen.update(page_urls - seen)
                if len(useen) > 200:
                    useen = set(list(useen)[:200])
                count += add_count
                print('高速爬取到第{}首 Downloading ......'.format(count))

if __name__ == '__main__':
    t1 = time.time()
    if os.path.exists('seen_data.txt'):
        print('正在从上次爬取数据中恢复...')
        seen_file = open('seen_data.txt', 'r')
        seen_data = seen_file.read()
        seen = eval(seen_data)
        seen_file.close()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
    file_obj.close()

    seen_file = open('seen_data.txt', 'w')
    seen_file.write(str(seen))
    seen_file.close()

    print('4号爬虫爬取{}首诗，用时{}秒'.format(count, time.time()-t1))
    input('input any to exit')
