import re
import json
import requests
from lxml import etree
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70'
}
session = requests.session()


def spider(url: str, method: str = 'get', file_name: str = 'index.html', save: bool = False,
           params: dict = None, data: dict = None):
    if method == 'get':
        response = session.get(url=url, params=params, headers=headers)
    elif method == 'post':
        response = session.post(url=url, data=data, headers=headers)
    else:
        return None
    if response.status_code != 200:
        return None
    suffix = re.findall(f"\\.(.*)", file_name)[0]
    if suffix == 'html':
        # To dispose the messy code
        # 1)Set the encoding mode
        response.encoding = response.apparent_encoding
        # 2)Set the decoding mode manually
        # return response.content.decode(current_file_encoding: str)
        # 3)encode and decode again
        # return response.text.encoding('ISO-8859-1').decoding(current_file_encoding: str)
        if save:
            with open('download/' + file_name, 'w', encoding='utf-8') as fp:
                fp.write(response.text)
            return None
        return response.text
    elif suffix == 'json':
        if save:
            with open('download/' + file_name, 'w', encoding='utf-8') as fp:
                json.dump(obj=response.json(), fp=fp, ensure_ascii=False)
            return None
        return response.json()
    elif suffix == 'rar' or suffix == 'jpg' or suffix == 'jpeg' or suffix == 'png':
        if save:
            with open('download/' + file_name, 'wb') as fp:
                fp.write(response.content)
            return None
        return response.content


def download_multiple_picture(url: str):
    # re_expression
    urls = re.findall(
        f'<picture>.*?src="(.*?)".*?</picture>',
        spider(url=url),
        re.S
    )
    for term in urls:
        print(re.findall(f'.*/(.*)', term)[0])
        spider(
            url=term,
            file_name=re.findall(f'.*/(.*)', term)[0],
            save=True
        )

    # bs4
    soup = BeautifulSoup(spider(url=url), 'lxml')
    images = soup.select('picture img')
    for img in images:
        print(re.findall(f'.*/(.*)', img['src'])[0])
        spider(
            url=img['src'],
            file_name=re.findall(f'.*/(.*)', img['src'])[0],
            save=True
        )

    # xPath
    tree = etree.HTML(spider(url=url))
    paths = tree.xpath('//picture/img/@src')
    for path in paths:
        print(path)
        spider(
            url=path,
            file_name=re.findall(f'.*/(.*)', path)[0],
            save=True
        )


def download_one_ppt(href):
    tree = etree.HTML(spider(url='https://sc.chinaz.com' + href))
    rar = tree.xpath('//div[@class="download-url"]//a/@href')[0]
    spider(
        url=rar,
        file_name=re.findall(f'.*/(.*)', rar)[0],
        save=True
    )
    print(re.findall(f'.*/(.*)', rar)[0])


def download_multiple_ppt(url: str, pages: int):
    pool = Pool(10)
    url_list = re.findall(f'(.*)(\\..*)', url)
    for page in range(1, pages):
        tree = etree.HTML(spider(url=url_list[0][0] + '_' + str(page + 1) + url_list[0][1]))
        hrefs = tree.xpath('//div[@class="item"]//a/@href')
        pool.map(download_one_ppt, hrefs)
    pool.close()


if __name__ == '__main__':
    download_multiple_ppt('https://sc.chinaz.com/ppt/free.html', 800)
