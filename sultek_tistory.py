import os, requests, re, time, json
from bs4 import BeautifulSoup
import warnings
warnings.simplefilter("ignore", UserWarning)

def tistory_crawling(URL):
    print('https://sulgal.tistory.com/' + str(URL) + " 접속시도...", end='')
    headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }
    source = requests.get('https://sulgal.tistory.com/' + str(URL), headers=headers)
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
    category = title_div.find('span').get_text().strip()
    if category == '삭제':
        print("삭제 카테고리")
        return 0
    title = title_div.find('h1').get_text().strip()

    error = 0

    for l in link_list:
        status = crawling(l)
        if status == 404:
            tf = open("log.txt", "a", -1, "utf-8")
            print("삭제된 페이지 감지(" + link_list[l] + ")")
            tf.write(str(URL) + "   " + link_list[l] + " 삭제됨\n")
            tf.close()
            error = 1
        elif status == -1:
            tf = open("log.txt", "a", -1, "utf-8")
            print("접속 실패(" + link_list[l] + ")")
            tf.write(str(URL) + "   " + link_list[l] + " 접속실패\n")
            tf.close()
            error = 1
            return 2
        else:
            time.sleep(0.2)

    if error == 0:
        print("발견된 문제 없음")
    return 0

def crawling(URL):
    text = ''
    gall_num = 0
    gall_id = ''
    while True:
        try:
            if '/snowpiercer2013/' in URL:
                URL = URL.replace('/snowpiercer2013/', '/board/view/?id=snowpiercer2013&no=')
            baseURL = URL
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}

            source = requests.get(baseURL, headers=headers)
        except Exception as e:
            if 'Connection aborted' in str(e):
                print("접속 거부됨. 재시도합니다")
                time.sleep(1)
                continue
            else:
                print("데이터 수신 오류.")
                return -1

        if not source.status_code == 200:
            if source.status_code == 404:
                return 404
            print("서버 응답 없음.")
            return -1
        else:
            return 200


os.system("title 설국열차 갤러리 티스토리 검사기")
start = int(input("시작번호 : "))
end = int(input("종료번호 : "))
for i in range(start, end + 1):
    try:
        status = tistory_crawling(i)
    except Exception as e:
        print("데이터 수신 오류. 다시 시도해주세요.")
        print("에러메시지 : ", e)
    time.sleep(0.5)