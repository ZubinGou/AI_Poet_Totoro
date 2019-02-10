import aiohttp
import asyncio
import time
import re
import os
import random
import multiprocessing as mp
from bs4 import BeautifulSoup


file_obj = open("gsww_all.txt", 'a', encoding='utf-8')
seen = set()
useen = {'324652b6ac3d', }
count = 0


def parse(html):
    soup = BeautifulSoup(html, 'lxml')
    item = soup.find('div', class_="main3")
    items = item.find('div', class_="cont")

    dynasty = items.find('a').text
    writer = items.find_all('a')[1].text
    poem = items.find('div', class_="contson").text
    poem_data = dynasty+'::'+writer+'::'+poem.replace('\n', '')+'\n'

    urls = soup.find_all('a', style="font-size:18px; line-height:22px; height:22px;", href=re.compile(r'shiwenv_'))
    page_urls = set()
    for i in urls:
        page_url = i.get('href')[9:21]
        page_urls.add(page_url)
    return page_urls, poem_data


def restore():
    global seen, useen
    if os.path.exists('seen.txt'):
        print('正在从上次爬取数据中恢复...')
        seen_file = open('seen.txt', 'r')
        seen_data = seen_file.read()
        seen = eval(seen_data)
        seen_file.close()
        print('此前已经爬取了{}首诗啦！'.format(len(seen)))

    if os.path.exists('useen.txt'):
        print('继续从上次爬取数据中恢复...')
        useen_file = open('useen.txt', 'r')
        useen_data = useen_file.read()
        useen = eval(useen_data)
        useen_file.close()


async def fetch(session, url):
    base_url = "https://so.gushiwen.org/shiwenv_"
    http = base_url + url + '.aspx'
    # UA_LIST = [
    #     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    #     "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    #     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    #     "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    #     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    #     "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    #     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    #     "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    #     "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    #     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    #     "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    #     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
    # ]
    # headers = {
    #     ':authority': 'yijiuningyib.gushiwen.org',
    #     ':method': 'GET',
    #     ':scheme': 'https',
    #     'accept': '*/*',
    #     'accept-encoding': 'gzip, deflate, br',
    #     'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    #     # 'cookie': '''Hm_lvt_04660099568f561a75456483228a9516=1546439165,
    #     #             1546523730,1546770347; POSMEDIAID=b32abace4e2a6131cd50754870a
    #     #             53ec851cee4405862dc646b6347d287ea40401f7b338e27cc5a26d1821e19
    #     #             80087d87:FG=1; Hm_lpvt_04660099568f561a75456483228a9516=1546781911''',
    #     # 'user-agent': random.choice(UA_LIST)
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    #     'upgrade-insecure-requests': '1',
    # }
    r = await session.get(http)
    html = await r.text()
    return html


async def main(loop):
    global count, seen, useen
    pool = mp.Pool(mp.cpu_count())


    async with aiohttp.ClientSession() as session:
        while count < 100000:
            if len(useen) > 10:
                toseen = set(list(useen)[:10])
            else:
                toseen = useen

            useen = useen - toseen
            tasks = [loop.create_task(fetch(session, url)) for url in toseen]
            finished, unfinished = await asyncio.wait(tasks)
            htmls = [r.result() for r in finished]

            parse_jobs = [pool.apply_async(parse, args=(html, )) for html in htmls]
            results = [re.get() for re in parse_jobs]

            seen.update(toseen)
            toseen.clear()

            for page_urls, poem_data in results:
                useen.update(page_urls - seen)

                if poem_data is not None:   # save poem
                    file_obj.write(poem_data)
                    count += 1

            print('已经爬取{}首诗 Downloading ......'.format(count))

            seen_file = open('seen.txt', 'w')
            seen_file.write(str(seen))
            seen_file.close()

            useen_file = open('useen.txt', 'w')
            useen_file.write(str(useen))
            useen_file.close()


if __name__ == '__main__':
    t1 = time.time()
    restore()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
    file_obj.close()

    print('爬取{}首诗，用时{}秒'.format(count, time.time()-t1))
    input('input any to exit')
