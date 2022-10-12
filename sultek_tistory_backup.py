import os, requests, re, time, json
from bs4 import BeautifulSoup
import warnings
from datetime import datetime
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

    title_div = soup.find('div', class_='post-cover').find('div', class_='inner')
    category = title_div.find('span').get_text().strip()
    title = title_div.find('h1').get_text().strip()
    d = datetime.now()

    file = open("tistory_backup.txt", "a", -1, "utf-8")
    file.write('https://sulgal.tistory.com/' + str(URL) + '\n')
    file.write(title + '\n')
    file.write(category + '\n')
    file.write(str(d) + '\n')

    for c in post_div:
        for s in str(c).split('\n'):
            try:
                if 'container_postbtn' in s:
                    file.write('\n\n')
                    file.close
                    print('백업완료')
                    return
            except:
                continue
            if s:
                file.write(s + '\n')

    file.write('\n\n')
    file.close
    print('백업완료')


os.system("title 설국열차 갤러리 티스토리 백업")
start = int(input("시작번호 : "))
end = int(input("종료번호 : "))
for i in range(start, end + 1):
    try:
        status = tistory_crawling(i)
    except Exception as e:
        print("데이터 수신 오류. 다시 시도해주세요.")
        print("에러메시지 : ", e)
    time.sleep(0.8)