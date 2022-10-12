import os, requests, re, time, json
from bs4 import BeautifulSoup
import warnings
import filetype
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
warnings.simplefilter("ignore", UserWarning)
currentDir = os.getcwd()
try:
    meipassDir = sys._MEIPASS
except:
    meipassDir = currentDir

# UI파일 연결
# 단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.

os.chdir(meipassDir)
form_class = uic.loadUiType("sultek1.4.ui")[0]

# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    buffer = 0
    tB_text = ''

    def __init__(self) :
        super().__init__()
        self.setupUi(self)  #UI 로딩
        self.setFixedSize(840, 420)  #sultek.ico
        self.setWindowTitle("설텍")
        self.setWindowIcon(QIcon("sultek.ico"))
        
        os.chdir(currentDir)  # data.bin을 사용하기 위해 현재 폴더로 돌아옴
        self.loadSetting()  # 설정된 옵션 불러오기
        self.pushButton_input.clicked.connect(self.addrInput)  # 입력버튼 이벤트 연결
        self.pushButton_stop.clicked.connect(self.stopCrawling)
        self.inputThread_var = None

    def loadSetting(self):
        saveData = []
        try:
            with open("data.bin", "rb") as f:
                data = f.read()
                for d in data:
                    saveData.append(d)
        except Exception as e:
            return

        if saveData[0] == 1:
            self.radioButton_txt_save_1.setChecked(True)
        elif saveData[0] == 2:
            self.radioButton_txt_save_2.setChecked(True)
        elif saveData[0] == 3:
            self.radioButton_txt_save_3.setChecked(True)
        else:
            self.radioButton_txt_save_1.setChecked(True)

        if saveData[1] == 1:
            self.radioButton_txt_filename_1.setChecked(True)
        elif saveData[1] == 2:
            self.radioButton_txt_filename_2.setChecked(True)
        else:
            self.radioButton_txt_filename_1.setChecked(True)

        if saveData[2] == 1:
            self.checkBox_txt_img.setChecked(True)
        else:
            self.checkBox_txt_img.setChecked(False)

        if saveData[3] == 1:
            self.checkBox_txt_com.setChecked(True)
        else:
            self.checkBox_txt_com.setChecked(False)

        if saveData[4] == 1:
            self.radioButton_pdf_save_1.setChecked(True)
        elif saveData[4] == 2:
            self.radioButton_pdf_save_2.setChecked(True)
        elif saveData[4] == 3:
            self.radioButton_pdf_save_3.setChecked(True)
        else:
            self.radioButton_pdf_save_1.setChecked(True)

        if saveData[5] == 1:
            self.radioButton_pdf_filename_1.setChecked(True)
        elif saveData[5] == 2:
            self.radioButton_pdf_filename_2.setChecked(True)
        else:
            self.radioButton_pdf_filename_1.setChecked(True)

        if saveData[6] == 1:
            self.checkBox_pdf_img.setChecked(True)
        else:
            self.checkBox_pdf_img.setChecked(False)

        if saveData[7] == 1:
            self.checkBox_pdf_com.setChecked(True)
        else:
            self.checkBox_pdf_com.setChecked(False)

    def readSetting(self):
        settings = {
            'saveTextFile': 0,
            'textFileName': 0,
            'imageDownload': 0,
            'textComment': 0,
            'savePdfFile': 0,
            'pdfFileName': 0,
            'pdfImage': 0,
            'pdfComment': 0,
            'textFileName_str': '',
            'pdfFileName_str': ''
        }

        if self.radioButton_txt_save_1.isChecked():
            settings['saveTextFile'] = 1
        elif self.radioButton_txt_save_2.isChecked():
            settings['saveTextFile'] = 2
        elif self.radioButton_txt_save_3.isChecked():
            settings['saveTextFile'] = 3
        else:
            self.radioButton_txt_save_1.setChecked(True)
            settings['saveTextFile'] = 1

        if self.radioButton_txt_filename_1.isChecked():
            settings['textFileName'] = 1
        elif self.radioButton_txt_filename_2.isChecked():
            settings['textFileName'] = 2
            if self.lineEdit_txt_filename.text().strip():
                settings['textFileName_str'] = self.lineEdit_txt_filename.text()
            else:
                return {'error': '텍스트 파일명을 지정해주세요.'}
        else:
            self.radioButton_txt_filename_1.setChecked(True)
            settings['textFileName'] = 1

        if self.checkBox_txt_img.isChecked():
            settings['imageDownload'] = 1

        if self.checkBox_txt_com.isChecked():
            settings['textComment'] = 1

        if self.radioButton_pdf_save_1.isChecked():
            settings['savePdfFile'] = 1
        elif self.radioButton_pdf_save_2.isChecked():
            settings['savePdfFile'] = 2
        elif self.radioButton_pdf_save_3.isChecked():
            settings['savePdfFile'] = 3
        else:
            self.radioButton_pdf_save_1.setChecked(True)
            settings['savePdfFile'] = 1

        if self.radioButton_pdf_filename_1.isChecked():
            settings['pdfFileName'] = 1
        elif self.radioButton_pdf_filename_2.isChecked():
            settings['pdfFileName'] = 2
            if self.lineEdit_pdf_filename.text().strip():
                settings['pdfFileName_str'] = self.lineEdit_pdf_filename.text()
            else:
                return {'error': 'PDF 파일명을 지정해주세요.'}
        else:
            self.radioButton_pdf_filename_1.setChecked(True)
            settings['pdfFileName'] = 1

        if self.checkBox_pdf_img.isChecked():
            settings['pdfImage'] = 1

        if self.checkBox_pdf_com.isChecked():
            settings['pdfComment'] = 1

        return settings

    @pyqtSlot()
    def stopCrawling(self):
        if self.inputThread_var is not None:
            self.inputThread_var.stopProcess = True

    @pyqtSlot()  # 입력버튼 이벤트
    def addrInput(self):
        option = self.readSetting()
        if 'error' in option:
            reply = QMessageBox.warning(self, '알림', option['error'], QMessageBox.Ok, QMessageBox.Ok)
            return

        saveData = [
            option['saveTextFile'],
            option['textFileName'],
            option['imageDownload'],
            option['textComment'],
            option['savePdfFile'],
            option['pdfFileName'],
            option['pdfImage'],
            option['pdfComment']
        ]

        with open("data.bin", "wb") as f:
            f.write(bytes(saveData))
            f.close()

        self.thread = QThread()
        self.inputThread_var = InputThread()  # 작업 처리하는 스레드 생성
        self.inputThread_var.moveToThread(self.thread)
        self.thread.started.connect(self.inputThread_var.run)
        self.inputThread_var.threadEvent.connect(self.thread.quit)
        self.inputThread_var.threadEvent.connect(self.inputThread_var.deleteLater)
        self.inputThread_var.paintEvent.connect(self.QTprint)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.afterOutput)  # 작업처리 스레드 핸들러

        self.inputThread_var.option = option # 현재 옵션 스레드에 전달
        self.inputThread_var.pbarRenew.connect(self.progressRenew)
        self.inputThread_var.pbarSet.connect(self.setProgress)
        self.inputThread_var.inputCommand = self.lineEdit_input.text().split()
        self.lineEdit_input.clear()
        self.lineEdit_input.setDisabled(True)
        self.pushButton_input.setDisabled(True)
        self.pushButton_stop.setDisabled(False)
        self.thread.start()

    @pyqtSlot(int)
    def setProgress(self, maximum):
        self.progressBar.setRange(0, maximum)

    @pyqtSlot(int)
    def progressRenew(self, int):
        self.progressBar.setValue(int)

    @pyqtSlot(str)  # 스레드 핸들러
    # 받은 문자열을 QtextBrowser에 출력하는 함수
    def QTprint(self, inputText):
        text = inputText.replace('\n', '<br/>')
        self.tB_text += text
        self.textBrowser_output.clear()
        self.textBrowser_output.append(self.tB_text)

    @pyqtSlot()  # 스레드 핸들러
    def afterOutput(self):
        self.lineEdit_input.setDisabled(False)
        self.pushButton_input.setDisabled(False)
        self.pushButton_stop.setDisabled(True)

class InputThread(QObject):  # 작업처리 스레드. 대부분 함수가 이 스레드에 들어감
    threadEvent = pyqtSignal()
    paintEvent = pyqtSignal(str)
    pbarRenew = pyqtSignal(int)
    pbarSet = pyqtSignal(int)
    inputCommand = ''
    buffer = 0
    option = {}  # 입력버튼 눌릴 때 전달받음
    stopProcess = False

    def __init__(self):
        super().__init__()

    @pyqtSlot()
    def signalText(self):
        self.paintEvent.emit("작업을 중단합니다.\n")
        self.stopProcess = True

    def run(self):  # 입력버튼 누르면 작동
        while self.inputCommand:  # inputCommand가 빈 리스트가 아닌 경우에만
            if self.option['saveTextFile'] == 1 and self.option['imageDownload'] == 0 and self.option['savePdfFile'] == 1:
                break

            getURL = self.inputCommand[0]
            startCount = -1
            endCount = -1

            if len(self.inputCommand) > 1:
                if self.inputCommand[1].isdigit() and int(self.inputCommand[1]) > 0:
                    startCount = int(self.inputCommand[1])
                else:
                    self.paintEvent.emit("커맨드 오류. 다시 입력해주세요.\n")
                    break
                if len(self.inputCommand) > 2:
                    if self.inputCommand[2].isdigit() and startCount <= int(self.inputCommand[2]):
                        endCount = int(self.inputCommand[2])
                    else:
                        self.paintEvent.emit("커맨드 오류. 다시 입력해주세요.\n")
                        break
                else:
                    endCount = startCount

            self.pbarSet.emit(0)  # progressBar를 진행중 상태로 만들기

            try:
                if 'vega_note' in getURL:
                    self.blog_crawling(getURL, 'v', self.option, startCount, endCount)
                elif 'lsh4710711' in getURL:
                    self.blog_crawling(getURL, 'l', self.option, startCount, endCount)
                elif 'sulgal' in getURL:
                    self.tistory_crawling(getURL, self.option, startCount, endCount)
                else:
                    self.single_crawling(getURL, self.option)
            except Exception as e:
                self.paintEvent.emit("데이터 수신 오류. 다시 시도해주세요.\n")
                self.paintEvent.emit("에러메시지 : " + str(e) + '\n')
                self.pbarSet.emit(100)  # progressBar를 0%로 초기화
                self.pbarRenew.emit(0)

            break
        self.threadEvent.emit()

    def createFolder(self, directory):
        for i in '\/:*?"<>|':
            if i in directory:
                directory = directory.replace(i, '')
        directory = directory.strip()

        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            self.paintEvent.emit('Error: Creating directory. ' + directory + '\n')

    def tistory_crawling(self, URL, option, startCount, endCount):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        }
        source = requests.get(URL, headers=headers)
        if not source.status_code == 200:
            self.paintEvent.emit("블로그 접속 실패\n")
            return 0

        soup = BeautifulSoup(source.content, 'html.parser')
        post_div = soup.find('div', class_='tt_article_useless_p_margin')
        a_list = post_div.find_all('a')
        link_list = {}
        for a in a_list:
            link = a.attrs['href']  # 'http://m.dcinside.com/view.php?id=snowpiercer2013&no=177564'
            if not ('gall.dcinside.com' in link or 'm.dcinside.com' in link):
                continue
            text = a.get_text()
            if not link in link_list:
                link_list[link] = text
            else:
                link_list[link] += text

        if option['textFileName'] == 1:
            title_div = soup.find('div', class_='post-cover').find('div', class_='inner')
            title = title_div.find('h1').get_text().strip()
        else:
            title = option['textFileName_str']

        for i in '\/:*?"<>|':
            if i in title:
                title = title.replace(i, '')
        title = title.strip()

        imagecrawl = False
        if option['imageDownload'] == 1:
            imagecrawl = True

        commentcrawl = False
        if option['textComment'] == 1:
            commentcrawl = True

        # startCount, endCount 지정을 안 한 경우 -1로 넘어옴
        if startCount < 0:
            startCount = 1
            endCount = len(link_list)

        if endCount > len(link_list):
            endCount = len(link_list)

        self.pbarSet.emit(endCount - startCount + 1)

        count = 0
        success = 0
        fail = 0
        success_img = 0
        fail_img = 0
        textcrawl = option['saveTextFile'] != 1

        # 한 파일에 저장
        if option['saveTextFile'] == 3:
            title_count = 2
            temp_title = title

            # 중복 파일 발견시 파일명에 숫자 붙이기
            while True:
                if not os.path.exists(temp_title + ".txt"):
                    textfile = open(temp_title + ".txt", "w", -1, 'utf-8')
                    break
                else:
                    temp_title = title + "_(%d)" % title_count
                    title_count += 1

            # 창작물 리스트에서 하나씩 크롤링
            for l in link_list:
                count += 1
                if count < startCount:
                    continue
                if count > endCount:
                    break

                if self.stopProcess:
                    textfile.close()
                    self.paintEvent.emit("다운로드 중단됨\n")
                    self.pbarRenew.emit(0)
                    fail += endCount - count + 1
                    return [endCount - startCount, fail]

                self.paintEvent.emit(str(count) + ' ')
                status = self.crawling(l, 1, multiFile=textfile, textcrawl=textcrawl, imagecrawl=imagecrawl,
                                       imagetitle=title,
                                       commentcrawl=commentcrawl)
                if status:
                    if status['error'] == 404:
                        self.paintEvent.emit(link_list[l] + " ...<b>삭제된 페이지입니다</b>\n")
                        fail += 1

                self.pbarRenew.emit(count - startCount + 1)

                if count < endCount:
                    time.sleep(0.8)

            textfile.close()

        else:
            for l in link_list:
                count += 1
                if count < startCount:
                    continue
                if count > endCount:
                    break

                if self.stopProcess:
                    self.paintEvent.emit("다운로드 중단됨\n")
                    self.pbarRenew.emit(0)
                    fail += endCount - count + 1
                    return [endCount - startCount, fail]

                self.paintEvent.emit(str(count) + ' ')
                status = self.crawling(l, 1, textcrawl=textcrawl, imagecrawl=imagecrawl, imagetitle=title,
                                       commentcrawl=commentcrawl)
                if status:
                    if status['error'] == 404:
                        self.paintEvent.emit(link_list[l] + " ...<b>삭제된 페이지입니다</b>\n")
                        fail += 1

                    else:
                        success_img += status['success']
                        fail_img += status['fail']

                self.pbarRenew.emit(count - startCount + 1)

                if count < endCount:
                    time.sleep(0.8)

        success = endCount - startCount + 1 - fail
        self.paintEvent.emit("결과 : {0}개 성공, {1}개 실패\n\n".format(success, fail))

    def blog_crawling(self, URL, d, option, startCount, endCount):
        if 'blogId' in URL:
            blogId = re.search('blogId=(.+?)&', URL)
            if blogId:
                blogId = blogId.group(1)
            logNo = re.search('logNo=(\d+)?', URL)
            if logNo:
                logNo = logNo.group(1)
            URL = "https://blog.naver.com/" + blogId + "/" + logNo
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        }
        source = requests.get(URL, headers=headers)
        if not source.status_code == 200:
            self.paintEvent.emit("블로그 접속 실패\n")
            return 0

        soup = BeautifulSoup(source.content, 'html.parser')
        iframe_list = soup.find_all('iframe')
        iframe = iframe_list[0]
        src = iframe.attrs["src"]

        iframe_source = requests.get('https://blog.naver.com' + src, headers=headers)
        if not iframe_source.status_code == 200:
            self.paintEvent.emit("블로그 접속 실패\n")
            return 0

        if option['textFileName'] == 1:
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
        else:
            title = option['textFileName_str']

        a_list = post_div.find_all('a')
        link_list = {}
        for a in a_list:
            link = a.attrs['href']
            if not ('gall.dcinside.com' in link or 'm.dcinside.com' in link):
                continue
            text = a.get_text()
            text = text.replace('\r', '')
            text = text.replace('\n', '')
            if not link in link_list:
                link_list[link] = text
            else:
                link_list[link] += text

        imagecrawl = False
        if option['imageDownload'] == 1:
            imagecrawl = True

        commentcrawl = False
        if option['textComment'] == 1:
            commentcrawl = True

        # startCount, endCount 지정을 안 한 경우 -1로 넘어옴
        if startCount < 0:
            startCount = 1
            endCount = len(link_list)

        if endCount > len(link_list):
            endCount = len(link_list)

        self.pbarSet.emit(endCount - startCount + 1)

        count = 0
        success = 0
        fail = 0
        success_img = 0
        fail_img = 0
        textcrawl = option['saveTextFile'] != 1

        # 한 파일에 저장
        if option['saveTextFile'] == 3:
            title_count = 2
            temp_title = title

            # 중복 파일 발견시 파일명에 숫자 붙이기
            while True:
                if not os.path.exists(temp_title + ".txt"):
                    textfile = open(temp_title + ".txt", "w", -1, 'utf-8')
                    break
                else:
                    temp_title = title + "_(%d)" % title_count
                    title_count += 1

            # 창작물 리스트에서 하나씩 크롤링
            for l in link_list:
                count += 1
                if count < startCount:
                    continue
                if count > endCount:
                    break

                if self.stopProcess:
                    textfile.close()
                    self.paintEvent.emit("다운로드 중단됨\n")
                    self.pbarRenew.emit(0)
                    fail += endCount - count + 1
                    return [endCount - startCount, fail]

                self.paintEvent.emit(str(count) + ' ')
                status = self.crawling(l, 1, multiFile=textfile, textcrawl=textcrawl, imagecrawl=imagecrawl,
                                       imagetitle=title,
                                       commentcrawl=commentcrawl)
                if status:
                    if status['error'] == 404:
                        self.paintEvent.emit(link_list[l] + " ...<b>삭제된 페이지입니다</b>\n")
                        fail += 1

                self.pbarRenew.emit(count - startCount + 1)
                if count < endCount:
                    time.sleep(0.8)
            textfile.close()

        else:  # 각 파일에 저장
            for l in link_list:
                count += 1
                if count < startCount:
                    continue
                if count > endCount:
                    break

                if self.stopProcess:
                    self.paintEvent.emit("다운로드 중단됨\n")
                    self.pbarRenew.emit(0)
                    fail += endCount - count + 1
                    return [endCount - startCount, fail]

                self.paintEvent.emit(str(count) + ' ')
                status = self.crawling(l, 1, textcrawl=textcrawl, imagecrawl=imagecrawl, imagetitle=title,
                                       commentcrawl=commentcrawl)

                if status:
                    if status['error'] == 404:
                        self.paintEvent.emit(link_list[l] + " ...<b>삭제된 페이지입니다</b>\n")
                        fail += 1

                    else:
                        success_img += status['success']
                        fail_img += status['fail']

                self.pbarRenew.emit(count - startCount + 1)
                if count < endCount:
                    time.sleep(0.8)

        success = endCount - startCount + 1 - fail
        self.paintEvent.emit("결과 : {0}개 성공, {1}개 실패\n\n".format(success, fail))

    def single_crawling(self, URL, option):
        imagecrawl = False
        if option['imageDownload'] == 1:
            imagecrawl = True

        commentcrawl = False
        if option['textComment'] == 1:
            commentcrawl = True

        self.pbarSet.emit(1)
        textcrawl = option['saveTextFile'] != 1

        if URL.isdigit():
            status = self.crawling(URL, 0, textcrawl=textcrawl, imagecrawl=imagecrawl, commentcrawl=commentcrawl)
            if status and status['error'] == 404:
                self.paintEvent.emit("<b>삭제된 페이지입니다</b>\n")
        else:
            status = self.crawling(URL, 1, textcrawl=textcrawl, imagecrawl=imagecrawl, commentcrawl=commentcrawl)
            if status and status['error'] == 404:
                self.paintEvent.emit("<b>삭제된 페이지입니다</b>\n")

        self.pbarRenew.emit(1)

    def comm_crawling(self, url, gall_id, gall_num):
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

    def htmltree(self, content, d, textfile):
        cname = content.name
        if cname == 'br':
            textfile.write('\n')
            self.buffer = 0

        if 'contents' in dir(content):
            content_list = content.contents
            for con in content_list:
                self.htmltree(con, d + 1, textfile)
        else:
            textfile.write(content)
            if content.string != '':
                self.buffer = 1
        if cname == 'p' or cname == 'div':
            if self.buffer > 0:
                textfile.write('\n')
            self.buffer = 0

    def image_crawling(self, url, imgtag, imgttl=None):
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
            try:
                img_url = imgtag[i].attrs['src']
                img_file = requests.get(img_url, headers=headers)
                img_data = img_file.content
            except Exception as e:
                fail += 1
                continue

            if imgttl is None:
                filename = gall_id + "-" + gall_num + "-%03d" % (i + 1)
                f = open(filename, 'wb')
            else:
                self.createFolder(imgttl)
                filename = imgttl + "/" + gall_id + "-" + gall_num + "-%03d" % (i + 1)
                f = open(filename, 'wb')

            f.write(img_data)
            f.close()


            kind = filetype.guess(filename)
            if kind is None:
                fail += 1
                os.remove(filename)
                continue

            if os.path.exists(filename + '.' + kind.extension):
                os.remove(filename + '.' + kind.extension)
            os.rename(filename, filename + '.' + kind.extension)
            time.sleep(0.2)

        return [len(imgtag), fail]

    def crawling(self, URL, mode, multiFile=None, textcrawl=True, imagecrawl=False, imagetitle=None, commentcrawl=False):

        resultStatus = {
            'error': 0,
            'success': 0,
            'fail': 0
        }

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
                    if '/snowpiercer2013/' in URL:  # 공유 전용 주소인 경우
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
                    self.paintEvent.emit("접속 거부됨. 재시도합니다\n")
                    time.sleep(1)
                    continue
                else:
                    self.paintEvent.emit("데이터 수신 오류. 다시 시도해주세요.\n")
                    self.paintEvent.emit("에러메시지 : " + str(e) + '\n')
                    return

            if not source.status_code == 200:
                if source.status_code == 404:
                    resultStatus['error'] = 404
                    return resultStatus
                self.paintEvent.emit("서버 응답 없음. 재시도합니다\n")
                time.sleep(1)
                continue

            soup = BeautifulSoup(source.content, 'html.parser')
            if soup == '':
                self.paintEvent.emit("수신 차단됨\n")
                return

            error = soup.find('div', class_='box_infotxt over_user')

            if error is not None:
                self.paintEvent.emit("서버 혼잡. 재시도합니다\n")
                time.sleep(1)
                continue
            break

        title = soup.select_one('span.title_subject').text

        for i in '\/:*?"<>|':
            if i in title:
                title = title.replace(i, '')
        title = title.strip()
        self.paintEvent.emit(title + " ...")

        try:
            url = re.search('(.+?no=\d+)?', source.url)
            if url:
                url = url.group(1)

            if textcrawl:
                if multiFile is not None:
                    textfile = multiFile
                else:
                    textfile = open(title + ".txt", "w", -1, 'utf-8')


                textfile.write(title)
                textfile.write("\n-------------------------------------------\n" + url + "\n\n\n")

                write_div = soup.select_one('div.write_div')

                con_list = write_div.contents[1:-1]
                for con in con_list:
                    self.htmltree(con, 0, textfile)
                textfile.write('\n\n')

                if commentcrawl is True:
                    comment = self.comm_crawling(url, gall_id, gall_num)
                    len_comment = len(comment)

                    if len_comment > 0:
                        textfile.write("전체 댓글 %d개 ▼\n" % len_comment)

                    for l in range(len_comment):
                        textfile.write(comment[l] + '\n')
                    textfile.write('\n\n')

                if multiFile is None:
                    textfile.close()
                self.paintEvent.emit("변환완료")

            success = 0
            fail = 0
            if imagecrawl is True:
                write_view = soup.select_one('div.writing_view_box')

                if write_view is not None:
                    imgtag = write_view.find_all('img')
                    if len(imgtag) > 0:
                        imageCrawlData = self.image_crawling(url, imgtag, imgttl=imagetitle)
                        success = imageCrawlData[0] - imageCrawlData[1]
                        fail = imageCrawlData[1]
                        self.paintEvent.emit(" (이미지 {0}개 다운로드".format(success))
                        if fail > 0:
                            self.paintEvent.emit(", <b>{0}개 실패</b>".format(fail))
                        self.paintEvent.emit(')')
                    elif textcrawl is False:
                        self.paintEvent.emit("이미지 없음")

            self.paintEvent.emit('\n')
            resultStatus['success'] = success
            resultStatus['fail'] = fail
            return resultStatus

        except Exception as e:
            if multiFile is None and textcrawl:
                textfile.close()
            self.paintEvent.emit("<b>실패</b>\n")
            self.paintEvent.emit("에러메시지 : " + str(e) + '\n')

if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
