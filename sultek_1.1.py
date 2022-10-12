import os
import requests, re
from bs4 import BeautifulSoup
import time

def user_ask():
    try:
        optionFile = open('option.txt', 'r', -1, 'utf-8')
    except:
        optionFile = open('option.txt', 'w', -1, 'utf-8')
        optionFile.write(
        """* 'onefile' 옵션
* - '0' 지정 시 주소 입력할 때마다 묻기
* - '1' 지정 시 게시물마다 파일을 따로 저장 (자동)
* - '2' 지정 시 게시물을 한 파일에 모아서 저장 (자동)

* 'title' 옵션
* - '0' 지정 시 주소 입력할 때마다 묻기
* - '1' 지정 시 블로그 게시글 제목으로 저장 (자동)

onefile = 0
title = 0""")
        return [0, 0]
    lines = optionFile.readlines()
    onefile = 0
    title = 0
    for line in lines:
        if line[0] == '*':
            continue
        if 'onefile' in line:
            line = line.replace('onefile', '')
            line = line.replace('=', '')
            line = line.strip()
            if line.isdigit():
                onefile = int(line)
        if 'title' in line:
            line = line.replace('title', '')
            line = line.replace('=', '')
            line = line.strip()
            if line.isdigit():
                title = int(line)
    if onefile > 2 or onefile < 0:
        onefile = 0
    if title > 1 or title < 0:
        title = 0
    return [onefile, title]

def tistory_crowling(URL):
    headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }
    source = requests.get(URL, headers=headers)
    if not source.status_code == 200:
        print("블로그 접속 실패")
        return 0

    soup = BeautifulSoup(source.content, 'html.parser')
    post_div = soup.find('div', class_='tt_article_useless_p_margin')
    a_list = post_div.find_all('a')
    link_list = {}
    for a in a_list:
        link = a.attrs['href']
        if not 'gall.dcinside.com' in link:
            continue
        text = a.get_text()
        if not link in link_list:
            link_list[link] = text
        else:
            link_list[link] += text


    title_div = soup.find('div', class_='post-cover').find('div', class_='inner')
    title = title_div.find('h1').get_text().strip()

    if len(link_list) > 1:
        option = user_ask()
        if option[0] == 0:
            while True:
                option_temp = input("* (1) 각 게시물을 따로 저장 (2) 모아서 저장\n(1 또는 2 입력) : ")
                if option_temp.isdigit():
                    if int(option_temp) < 1 or int(option_temp) > 2:
                        print("1 또는 2로 입력해 주세요")
                        continue
                    option_temp = int(option_temp)
                else:
                    print("1 또는 2로 입력해 주세요")
                    continue
                break
            option[0] = option_temp

        if option[1] == 0 and option[0] == 2:
            title_temp = input("저장할 파일명을 입력해 주세요 : ")
            if not title_temp == '':
                title = title_temp

        # 한 파일에 저장
        if option[0] == 2:
            textfile = open(title + ".txt", "w", -1, 'utf-8')
            for l in link_list:
                status = crowling(l, 1, textfile)
                if status == 404:
                    print(link_list[l] + " ...삭제된 페이지입니다")
                else:
                    time.sleep(0.3)
            textfile.close()

        else:
            for l in link_list:
                status = crowling(l, 1)
                if status == 404:
                    print(link_list[l] + " ...삭제된 페이지입니다")
                else:
                    time.sleep(0.3)

    else:
        for l in link_list:
            status = crowling(l, 1)
            if status == 404:
                print(link_list[l] + " ...삭제된 페이지입니다")

def blog_crowling(URL, d):
    headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }
    source = requests.get(URL, headers=headers)
    if not source.status_code == 200:
        print("블로그 접속 실패")
        return 0

    postnum = re.findall('\d+', URL)[0]

    soup = BeautifulSoup(source.content, 'html.parser')
    iframe_list = soup.find_all('iframe')
    iframe = iframe_list[0]
    src = iframe.attrs["src"]

    iframe_source = requests.get('https://blog.naver.com' + src, headers=headers)
    if not iframe_source.status_code == 200:
        print("블로그 접속 실패")
        return 0

    iframe_soup = BeautifulSoup(iframe_source.content, 'html.parser')
    if d == 'v':
        post_div = iframe_soup.find('div', id='post-view' + postnum)
        title_div = iframe_soup.find('div', id='title_1')
        title = title_div.find('span', class_='pcol1 itemSubjectBoldfont').get_text().strip()
    else:
        post_div = iframe_soup.find('div', class_='se-module se-module-text')
        if post_div is None:
            post_div = iframe_soup.find('div', id='postViewArea')
            title_div = iframe_soup.find('div', class_='htitle')
        else:
            title_div = iframe_soup.find('div', class_='pcol1')
        title = title_div.find('span').get_text().strip()

    a_list = post_div.find_all('a')
    link_list = {}
    for a in a_list:
        link = a.attrs['href']
        if not 'gall.dcinside.com' in link:
            continue
        text = a.get_text()
        text = text.replace('\r', '')
        text = text.replace('\n', '')
        if not link in link_list:
            link_list[link] = text
        else:
            link_list[link] += text

    if len(link_list) > 1:
        option = user_ask()
        if option[0] == 0:
            while True:
                option_temp = input("* (1) 각 게시물을 따로 저장 (2) 모아서 저장\n(1 또는 2 입력) : ")
                if option_temp.isdigit():
                    if int(option_temp) < 1 or int(option_temp) > 2:
                        print("1 또는 2로 입력해 주세요")
                        continue
                    option_temp = int(option_temp)
                else:
                    print("1 또는 2로 입력해 주세요")
                    continue
                break
            option[0] = option_temp

        if option[1] == 0 and option[0] == 2:
            title_temp = input("저장할 파일명을 입력해 주세요 : ")
            if not title_temp == '':
                title = title_temp

        # 한 파일에 저장
        if option[0] == 2:
            textfile = open(title + ".txt", "w", -1, 'utf-8')
            for l in link_list:
                status = crowling(l, 1, textfile)
                if status == 404:
                    print(link_list[l] + " ...삭제된 페이지입니다")
                else:
                    time.sleep(0.3)
            textfile.close()

        else:
            for l in link_list:
                status = crowling(l, 1)
                if status == 404:
                    print(link_list[l] + " ...삭제된 페이지입니다")
                else:
                    time.sleep(0.3)

    else:
        for l in link_list:
            status = crowling(l, 1)
            if status == 404:
                print(link_list[l] + " ...삭제된 페이지입니다")


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

def crowling(URL, mode, multiFile=None):
    text = ''
    while True:
        if mode == 0:
            baseURL = "https://gall.dcinside.com/board/view/"
            params = {'id': 'snowpiercer2013', 'no': URL}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
            source = requests.get(baseURL, params=params, headers=headers)
        else:
            if '/snowpiercer2013/' in URL:
                URL = URL.replace('/snowpiercer2013/', '/board/view/?id=snowpiercer2013&no=')
            baseURL = URL
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}

            source = requests.get(baseURL, headers=headers)
        if not source.status_code == 200:
            if source.status_code == 404:
                return 404
            print("서버 응답 없음. 재시도합니다")
            time.sleep(1)
            continue

        soup = BeautifulSoup(source.content, 'html.parser')
        if soup == '':
            print("수신 차단됨")
            return

        error = soup.find('div', class_='box_infotxt over_user')

        if error is not None:
            print("서버 혼잡. 재시도합니다")
            time.sleep(1)
            continue
        break

    url = source.url
    title = soup.select_one('span.title_subject').text
    for i in '\/:*?"<>|':
        if i in title:
            title = title.replace(i, '')
    title = title.strip()

    if multiFile is not None:
        textfile = multiFile
    else:
        textfile = open(title + ".txt", "w", -1, 'utf-8')
    print(title + " ...", end='')
    try:
        textfile.write(title)
        textfile.write("\n-------------------------------------------\n\n")
        write_div = soup.select_one('div.write_div')
        con_list = write_div.contents[1:-1]
        for con in con_list:
            htmltree(con, 0, textfile)
        textfile.write('\n')
        if multiFile is None:
            textfile.close()
        print("변환완료")
    except:
        if multiFile is None:
            textfile.close()
        print("\033[31m"+"실패"+"\033[0m")

os.system("title 설국열차 갤러리 텍본 제조기")

while True:
    buffer = 0
    getURL = input("URL 또는 글번호 입력 : ")
    status = 0
    try:
        if getURL.isdigit():
            status = crowling(getURL, 0)
        else:
            if 'vega_note' in getURL:
                blog_crowling(getURL, 'v')
            elif 'lsh4710711' in getURL:
                blog_crowling(getURL, 'l')
            elif 'sulgal' in getURL:
                tistory_crowling(getURL)
            else:
                status = crowling(getURL, 1)

        if status == 404:
            print("삭제된 페이지입니다")
    except Exception as e:
        if 'Connection aborted' in str(e):
            print("트래픽 과다. 다시 시도해주세요.")
        else:
            print("데이터 수신 오류. 다시 시도해주세요.")
            print("에러메시지 : ", e)
    print('')