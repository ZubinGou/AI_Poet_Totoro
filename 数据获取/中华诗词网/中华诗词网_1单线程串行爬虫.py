import requests
import time
from bs4 import BeautifulSoup

url = "http://my.bupt.edu.cn/index.portal?.p=Znxjb20ud2lzY29tLnBvcnRhbC5zaXRlLnYyLmltcGwuRnJhZ21lbnRXaW5kb3d8ZjE3MzN8dmlld3xub3JtYWx8Z3JvdXBpZD0xODMzMTMwMDAmZ3JvdXBuYW1lPeiuoeeul%2BacuuWtpumZoiZhY3Rpb249YnVsbGV0aW5QYWdlTGlzdA__#anchorf1733"
t1 = time.time()
count = 1
while count < 1000:
    print('第{}首 Downloading from {}...'.format(count, url))
    response = requests.get(url)
    soup = BeautifulSoup(response.content.decode('utf-8'), 'lxml')
    # title = soup.find('h3').text
    # writer = soup.find('div', class_="col-xs-12").find('span').text.split()[1]
    poem = soup.find('div', class_="m-lg font14").get_text('\n', 'br/')
    url = "http://www.zgshige.com/"+soup.find('ul', class_="list-unstyled m-sm lh20 font14").find_all('a')[1].get('href')
    # print(url)
    # print(writer)
    # print(title+'\n')
    # print(poem)

    file_obj = open("zgsg1.txt", 'a', encoding='utf-8')
    # file_obj.write(title+'::'+writer+'::'+poem)
    file_obj.write(poem)
    count += 1
    print('正在龟速爬取第{}首诗'.format(count))
file_obj.close()
print('1号爬虫爬取{}首诗，用时{}秒'.format(count, time.time()-t1))
input('input any to exit')
