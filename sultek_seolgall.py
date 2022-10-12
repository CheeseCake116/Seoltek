import os, requests, re, time, json
from bs4 import BeautifulSoup
import warnings
warnings.simplefilter("ignore", UserWarning)

def seolgall_crawling(num):
    while True:
        try:
            #"https://gall.dcinside.com/board/lists/?id=snowpiercer2013&page=321&exception_mode=recommend"
            page_num = int(num)
            gall_id = 'snowpiercer2013'
            baseURL = "https://gall.dcinside.com/board/lists/"
            params = {'id': 'snowpiercer2013', 'page': str(page_num), 'exception_mode': 'recommend'}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
            source = requests.get(baseURL, params=params, headers=headers)

        except Exception as e:
            if 'Connection aborted' in str(e):
                print("접속 거부됨. 재시도합니다")
                time.sleep(1)
                continue
            else:
                print("데이터 수신 오류. 다시 시도해주세요.")
                print("에러메시지 : ", e)

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

    title = soup.select_one('tbody')
    lists = title.find_all('tr', class_='ub-content us-post')
    print(lists)

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


os.system("title 설국열차 갤러리 설갤 념글 검사기")
start = int(input("시작번호 : "))
end = int(input("종료번호 : "))
for i in range(start, end + 1):
    try:
        status = seolgall_crawling(i)
    except Exception as e:
        print("데이터 수신 오류. 다시 시도해주세요.")
        print("에러메시지 : ", e)
    time.sleep(0.5)