import os
import requests
from bs4 import BeautifulSoup
import time

def htmltree(content, d, textfile):
    global buffer
    cname = content.name
    if cname == 'br':
        textfile.write('\n')
        buffer = 0

    if 'contents' in dir(content):
        content_list = content.contents
        for con in content_list:
            htmltree(con, d+1, textfile)
    else:
        textfile.write(content)
        if content.string != '':
            buffer = 1
    if cname == 'p' or cname == 'div':
        if buffer > 0:
            textfile.write('\n')
        buffer = 0

def crowling(URL, mode):
    text = ''
    while(True):
        if mode == 0:
            baseURL = "https://gall.dcinside.com/board/view/"
            params = {'id': 'snowpiercer2013', 'no': URL}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
            source = requests.get(baseURL, params=params, headers=headers)
        else:
            baseURL = URL
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
            source = requests.get(baseURL, headers=headers)

        if not source.status_code == 200:
            print("서버 응답 없음. 재시도합니다")
            time.sleep(1)
            continue

        soup = BeautifulSoup(source.content, 'html.parser')
        error = soup.find('div', class_='box_infotxt over_user')

        if not error == None:
            print("서버 혼잡. 재시도합니다")
            time.sleep(1)
            continue
        break

    url = (source.url)
    title = soup.select_one('span.title_subject').text
    textfile = open(title + ".txt", "w", -1, 'utf-8')

    write_div = soup.select_one('div.write_div')
    con_list = write_div.contents[1:-1]
    for con in con_list:
        htmltree(con, 0, textfile)

    textfile.close()
    print("파일 변환 완료")

os.system("title 설국열차 갤러리 텍본 제조기")
while(True):
    buffer = 0
    getURL = input("URL 또는 글번호 입력 : ")
    if getURL.isdigit():
        crowling(getURL, 0)
    else:
        crowling(getURL, 1)