import os, requests, re, time, json, warnings, math, sys
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PIL import Image, ImageQt

warnings.simplefilter("ignore", UserWarning)

class WindowClass(QMainWindow) :
    def __init__(self):
        super().__init__()
        self.setWindowTitle("설국열차 갤러리 텍본 제조기")
        self.setWindowIcon(QIcon("sultek.ico"))
        self.setFixedSize(500, 600)

def createFolder(directory):
    for i in '\/:*?"<>|':
        if i in directory:
            directory = directory.replace(i, '')
    directory = directory.strip()

    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

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

* 'imageDownload' 옵션
* - '0' 지정 시 주소 입력할 때마다 묻기
* - '1' 지정 시 이미지를 다운로드하지 않음 (자동)
* - '2' 지정 시 이미지를 다운로드함 (자동)

* 'comment' 옵션
* - '0' 지정 시 주소 입력할 때마다 묻기
* - '1' 지정 시 댓글을 저장하지 않음 (자동)
* - '2' 지정 시 댓글을 저장함 (자동)

onefile = 0
title = 0
imageDownload = 0
comment = 0""")
        return [0, 0]
    lines = optionFile.readlines()
    onefile = 0
    title = 0
    imageDownload = 0
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
        if 'imageDownload' in line:
            line = line.replace('imageDownload', '')
            line = line.replace('=', '')
            line = line.strip()
            if line.isdigit():
                imageDownload = int(line)
        if 'comment' in line:
            line = line.replace('comment', '')
            line = line.replace('=', '')
            line = line.strip()
            if line.isdigit():
                comment = int(line)
    if onefile > 2 or onefile < 0:
        onefile = 0
    if title > 1 or title < 0:
        title = 0
    if imageDownload > 2 or imageDownload < 0:
        imageDownload = 0
    if comment > 2 or comment < 0:
        comment = 0
    return [onefile, title, imageDownload, comment]

def tistory_crawling(URL, option, startCount, endCount):
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

    imagecrawl = False
    if option[2] == 0:
        while True:
            option_temp = input("* (1) 이미지를 다운로드하지 않음 (2) 이미지를 다운로드함\n(1 또는 2 입력) : ")
            if option_temp.isdigit():
                if int(option_temp) < 1 or int(option_temp) > 2:
                    print("1 또는 2로 입력해 주세요")
                    continue
                option_temp = int(option_temp)
            else:
                print("1 또는 2로 입력해 주세요")
                continue
            break
        option[2] = option_temp
    if option[2] == 2:
        imagecrawl = True

    commentcrawl = False
    if option[3] == 0:
        while True:
            option_temp = input("* (1) 댓글을 저장하지 않음 (2) 댓글을 저장함\n(1 또는 2 입력) : ")
            if option_temp.isdigit():
                if int(option_temp) < 1 or int(option_temp) > 2:
                    print("1 또는 2로 입력해 주세요")
                    continue
                option_temp = int(option_temp)
            else:
                print("1 또는 2로 입력해 주세요")
                continue
            break
        option[3] = option_temp
    if option[3] == 2:
        commentcrawl = True

    if startCount < 0:
        startCount = 1
        endCount = len(link_list)

    count = 0
    if len(link_list) > 1:
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
            title_count = 1
            temp_title = title
            while True:
                if not os.path.exists(temp_title + ".txt"):
                    textfile = open(temp_title + ".txt", "w", -1, 'utf-8')
                    break
                else:
                    temp_title = title + "_(%d)" % title_count
                    title_count += 1
            for l in link_list:
                count += 1
                if count < startCount:
                    continue
                if count > endCount:
                    break

                print("%-3d " % count, end='')
                status = crawling(l, 1, multiFile=textfile, imagecrawl=imagecrawl, imagetitle=title, commentcrawl=commentcrawl)
                if status == 404:
                    print(link_list[l] + " ...삭제된 페이지입니다")
                time.sleep(0.8)
            textfile.close()

        else:
            for l in link_list:
                count += 1
                if count < startCount:
                    continue
                if count > endCount:
                    break

                print("%4d" % count, end='')
                status = crawling(l, 1, imagecrawl=imagecrawl, imagetitle=title, commentcrawl=commentcrawl)
                if status == 404:
                    print(link_list[l] + " ...삭제된 페이지입니다")
                time.sleep(0.8)

    else:
        for l in link_list:
            status = crawling(l, 1, imagecrawl=imagecrawl, commentcrawl=commentcrawl)
            if status == 404:
                print(link_list[l] + " ...삭제된 페이지입니다")
            time.sleep(0.8)

def blog_crawling(URL, d, option, startCount, endCount):
    if 'blogId' in URL:
        blogId = re.search('blogId=(.+?)&', URL)
        if blogId:
            blogId = blogId.group(1)
        logNo = re.search('logNo=(\d+)?', URL)
        if logNo:
            logNo = logNo.group(1)
        URL = "https://blog.naver.com/"+blogId+"/"+logNo
    headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }
    source = requests.get(URL, headers=headers)
    if not source.status_code == 200:
        print("블로그 접속 실패")
        return 0

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
        post_div = iframe_soup.find('div', id='postViewArea')
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

    imagecrawl = False
    if option[2] == 0:
        while True:
            option_temp = input("* (1) 이미지를 다운로드하지 않음 (2) 이미지를 다운로드함\n(1 또는 2 입력) : ")
            if option_temp.isdigit():
                if int(option_temp) < 1 or int(option_temp) > 2:
                    print("1 또는 2로 입력해 주세요")
                    continue
                option_temp = int(option_temp)
            else:
                print("1 또는 2로 입력해 주세요")
                continue
            break
        option[2] = option_temp
    if option[2] == 2:
        imagecrawl = True

    commentcrawl = False
    if option[3] == 0:
        while True:
            option_temp = input("* (1) 댓글을 저장하지 않음 (2) 댓글을 저장함\n(1 또는 2 입력) : ")
            if option_temp.isdigit():
                if int(option_temp) < 1 or int(option_temp) > 2:
                    print("1 또는 2로 입력해 주세요")
                    continue
                option_temp = int(option_temp)
            else:
                print("1 또는 2로 입력해 주세요")
                continue
            break
        option[3] = option_temp
    if option[3] == 2:
        commentcrawl = True

    if startCount < 0:
        startCount = 1
        endCount = len(link_list)

    count = 0
    if len(link_list) > 1:
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
            title_count = 1
            temp_title = title
            while True:
                if not os.path.exists(temp_title + ".txt"):
                    textfile = open(temp_title + ".txt", "w", -1, 'utf-8')
                    break
                else:
                    temp_title = title + "_(%d)" % title_count
                    title_count += 1
            for l in link_list:
                count += 1
                if count < startCount:
                    continue
                if count > endCount:
                    break

                print("%-3d " % count, end='')
                status = crawling(l, 1, multiFile=textfile, imagecrawl=imagecrawl, imagetitle=title, commentcrawl=commentcrawl)
                if status == 404:
                    print(link_list[l] + " ...삭제된 페이지입니다")
                time.sleep(0.8)
            textfile.close()

        else:
            for l in link_list:
                count += 1
                if count < startCount:
                    continue
                if count > endCount:
                    break

                print("%-3d " % count, end='')
                status = crawling(l, 1, imagecrawl=imagecrawl, imagetitle=title, commentcrawl=commentcrawl)
                if status == 404:
                    print(link_list[l] + " ...삭제된 페이지입니다")
                time.sleep(0.8)

    else:
        for l in link_list:
            status = crawling(l, 1, imagecrawl=imagecrawl, commentcrawl=commentcrawl)
            if status == 404:
                print(link_list[l] + " ...삭제된 페이지입니다")
                time.sleep(0.8)

def single_crawling(URL, option):
    imagecrawl = False
    if option[2] == 0:
        while True:
            option_temp = input("* (1) 이미지를 다운로드하지 않음 (2) 이미지를 다운로드함\n(1 또는 2 입력) : ")
            if option_temp.isdigit():
                if int(option_temp) < 1 or int(option_temp) > 2:
                    print("1 또는 2로 입력해 주세요")
                    continue
                option_temp = int(option_temp)
            else:
                print("1 또는 2로 입력해 주세요")
                continue
            break
        option[2] = option_temp
    if option[2] == 2:
        imagecrawl = True

    commentcrawl = False
    if option[3] == 0:
        while True:
            option_temp = input("* (1) 댓글을 저장하지 않음 (2) 댓글을 저장함\n(1 또는 2 입력) : ")
            if option_temp.isdigit():
                if int(option_temp) < 1 or int(option_temp) > 2:
                    print("1 또는 2로 입력해 주세요")
                    continue
                option_temp = int(option_temp)
            else:
                print("1 또는 2로 입력해 주세요")
                continue
            break
        option[3] = option_temp
    if option[3] == 2:
        commentcrawl = True

    if URL.isdigit():
        status = crawling(URL, 0, imagecrawl=imagecrawl, commentcrawl=commentcrawl)
        if status == 404:
            print("삭제된 페이지입니다")
        time.sleep(0.8)
    else:
        status = crawling(URL, 1, imagecrawl=imagecrawl, commentcrawl=commentcrawl)
        if status == 404:
            print("삭제된 페이지입니다")
        time.sleep(0.8)

def comm_crawling(url, gall_id, gall_num):
    page_count = 1
    comment_list = []
    while True:
        temp_comment_list = []
        if gall_id == 'snowpiercer2013':
            data = {
                'id': gall_id,
                'no': gall_num,
                'cmt_id': gall_id,
                'cmt_no': gall_num,
                'e_s_n_o': '3eabc219ebdd65f4',
                'comment_page': page_count,
                'sort': "",
                '_GALLTYPE_': 'G'
            }
        else:
            return []

        headers = {
            'Referer': url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

        comment = requests.post('https://gall.dcinside.com/board/comment/', headers=headers, data=data).text
        json_data = json.loads(comment)

        if json_data['comments'] is None:
            return comment_list

        for i in json_data['comments']:
            text = ''
            if i['no'] == 0:
                continue
            if i['depth'] > 0:
                text += '↳ '
            text += "[" + i['name']
            if i['ip'] != '':
                text += "(" + i['ip'] + ")"

            memo_soup = BeautifulSoup(i['memo'], 'html.parser')
            if memo_soup.find('img') is not None:
                i['memo'] = '(디시콘)'
            elif i['vr_player'] is not False:
                i['memo'] = '(보이스리플)'
            else:
                i['memo'] = memo_soup.get_text()

            text += "]  " + i['memo']
            temp_comment_list.append(text)
        comment_list = temp_comment_list.copy() + comment_list
        page_count += 1

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

def image_crawling(url, imgtag, imgttl=None):
    gall_id = re.search('id=(.+?)&', url)
    if gall_id:
        gall_id = gall_id.group(1)

    gall_num = re.search('no=(\d+)?', url)
    if gall_num:
        gall_num = gall_num.group(1)

    fail = 0

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Referer': url
    }

    for i in range(len(imgtag)):
        #try:
        img_url = imgtag[i].attrs['src']
        img_file = requests.get(img_url, headers=headers)
        img_data = img_file.content
        #except:
        #    fail += 1
        #    continue
        if imgttl is None:
            f = open(gall_id + "-" + gall_num + "-%03d.png" % (i + 1), 'wb')
        else:
            createFolder(imgttl)
            f = open(imgttl+"/"+gall_id + "-" + gall_num + "-%03d.png" % (i + 1), 'wb')

        f.write(img_data)
        f.close()
        time.sleep(0.2)

    return [len(imgtag), fail]

def crawling(URL, mode, multiFile=None, imagecrawl=False, imagetitle=None, commentcrawl=False):
    text = ''
    gall_num = 0
    gall_id = ''
    while True:
        try:
            if mode == 0:
                gall_num = int(URL)
                gall_id = 'snowpiercer2013'
                baseURL = "https://gall.dcinside.com/board/view/"
                params = {'id': 'snowpiercer2013', 'no': URL}
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
                source = requests.get(baseURL, params=params, headers=headers)
            else:
                if '/snowpiercer2013/' in URL:
                    URL = URL.replace('/snowpiercer2013/', '/board/view/?id=snowpiercer2013&no=')

                gall_num = re.search('no=(\d+)?', URL)
                if gall_num:
                    gall_num = gall_num.group(1)

                gall_id = re.search('id=(.+?)&', URL)
                if gall_id:
                    gall_id = gall_id.group(1)

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
        url = re.search('(.+?no=\d+)?', source.url)
        if url:
            url = url.group(1)

        textfile.write(title)
        textfile.write("\n-------------------------------------------\n"+url+"\n\n\n")

        write_div = soup.select_one('div.write_div')

        con_list = write_div.contents[1:-1]
        for con in con_list:
            htmltree(con, 0, textfile)
        textfile.write('\n\n')

        if commentcrawl is True:
            comment = comm_crawling(url, gall_id, gall_num)
            len_comment = len(comment)

            if len_comment > 0:
                textfile.write("전체 댓글 %d개 ▼\n" % len_comment)

            for l in range(len_comment):
                textfile.write(comment[l] + '\n')
            textfile.write('\n\n')

        if multiFile is None:
            textfile.close()
        print("변환완료", end='')

        if imagecrawl is True:
            write_view = soup.select_one('div.writing_view_box')

            if write_view is not None:
                imgtag = write_view.find_all('img')
                if len(imgtag) > 0:
                    imageCrawlData = image_crawling(url, imgtag, imgttl=imagetitle)
                    if imageCrawlData[0] > 0:
                        print(" (이미지 %d개 다운로드 성공" % (imageCrawlData[0]-imageCrawlData[1]), end='')
                        if imageCrawlData[1] > 0:
                            print(", \033[31m" + "{0}개 실패".format(str(imageCrawlData[1])) + "\033[0m", end='')
                        print(')', end='')

        print('')

    except Exception as e:
        if multiFile is None:
            textfile.close()
        print(e)
        print("\033[31m"+"실패"+"\033[0m")


if __name__ == "__main__" :
    try:
        os.chdir(sys._MEIPASS)
    except:
        os.chdir(os.getcwd())

    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()

    """
    os.system("title 설국열차 갤러리 텍본 제조기")
    option_origin = user_ask()
    while True:
        option = option_origin.copy()
        buffer = 0
        inputCommand = input("URL 또는 글번호 입력 : ").split()
        getURL = inputCommand[0]
        startCount = -1
        endCount = -1
        status = 0

        if len(inputCommand) > 1:
            if inputCommand[1].isdigit() and int(inputCommand[1]) > 0:
                startCount = int(inputCommand[1])
            else:
                print("커맨드 오류. 다시 입력해주세요.")
                continue
            if len(inputCommand) > 2:
                if inputCommand[2].isdigit() and startCount <= int(inputCommand[2]):
                    endCount = int(inputCommand[2])
                else:
                    print("커맨드 오류. 다시 입력해주세요.")
                    continue
            else:
                endCount = startCount

        try:
            if 'vega_note' in getURL:
                blog_crawling(getURL, 'v', option, startCount, endCount)
            elif 'lsh4710711' in getURL:
                blog_crawling(getURL, 'l', option, startCount, endCount)
            elif 'sulgal' in getURL:
                tistory_crawling(getURL, option, startCount, endCount)
            else:
                single_crawling(getURL, option)
        except Exception as e:
            print("데이터 수신 오류. 다시 시도해주세요.")
            print("에러메시지 : ", e)
        print('')
    """