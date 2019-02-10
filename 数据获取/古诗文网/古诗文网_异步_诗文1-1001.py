import aiohttp
import asyncio
import time
import re
import os
import random
import multiprocessing as mp
from bs4 import BeautifulSoup


file_obj = open("gsww_1001.txt", 'a', encoding='utf-8')

urls = ['https://www.gushiwen.org/shiwen/default.aspx?page='+str(i) for i in range(1, 1001)]
count = 0


def parse(html):
    soup = BeautifulSoup(html, 'lxml')
    contents = soup.select('div[class="left"]')[1]
    contents = list(contents.select('div[class="sons"]'))
    poem_datas = []
    rex=re.compile(r'\(.*?\)')
    for c in contents:
        # title = c.select('b')[0].text
        writer = c.select('p[class="source"]')[0].text.replace('：', '::')
        poem = c.select('div[class="contson"]')[0].text.replace('　', '')
        poem = re.sub(rex, "", poem)
        poem_datas.append(str(writer.replace('\n', '')+'::'+poem.replace('\n', '')+'\n'))
    return poem_datas


async def fetch(session, url):

    UA_LIST = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
    ]

    headers = {
        'authority': 'yijiuningyib.gushiwen.org',
        'method': 'GET',
        'scheme': 'https',
        'accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        # 'cookie': '''Hm_lvt_04660099568f561a75456483228a9516=1546439165,
        #             1546523730,1546770347; POSMEDIAID=b32abace4e2a6131cd50754870a
        #             53ec851cee4405862dc646b6347d287ea40401f7b338e27cc5a26d1821e19
        #             80087d87:FG=1; Hm_lpvt_04660099568f561a75456483228a9516=1546781911''',
        'user-agent': random.choice(UA_LIST),
        # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'upgrade-insecure-requests': '1',
    }

    r = await session.get(url)    # headers=headers
    html = await r.text()
    return html


async def main(loop):
    global count, urls
    pool = mp.Pool(mp.cpu_count())

    async with aiohttp.ClientSession() as session:
        while len(urls) > 0:
            urls_to = urls[:5]
            urls = urls[5:]
            tasks = [loop.create_task(fetch(session, url)) for url in urls_to]
            finished, unfinished = await asyncio.wait(tasks)
            htmls = [r.result() for r in finished]

            parse_jobs = [pool.apply_async(parse, args=(html, )) for html in htmls]
            poem_datas = [re.get() for re in parse_jobs]
            for poem_data in poem_datas:
                for i in poem_data:
                    print(i[:10])
                    file_obj.write(i)
                    count += 1
            print('已经爬取{}首诗 Downloading ......'.format(count))
            time.sleep(random.random()*5)

if __name__ == '__main__':
    t1 = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
    file_obj.close()

    print('爬取{}首诗，用时{}秒'.format(count, time.time()-t1))
    input('input any to exit')
