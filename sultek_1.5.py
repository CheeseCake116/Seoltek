import os, requests, re, time, json, datetime, random
from bs4 import BeautifulSoup
import warnings
import filetype
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
import pdfkit
import tempfile

warnings.simplefilter("ignore", UserWarning)
currentDir = os.getcwd()

try:
    meipassDir = sys._MEIPASS
except:
    meipassDir = currentDir

os.chdir(meipassDir)
form_class = uic.loadUiType("sultek1.5.ui")[0]


# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    buffer = 0
    tB_text = ''

    def __init__(self) :
        super().__init__()
        self.setupUi(self)  # UI 로딩
        self.setFixedSize(1060, 420)
        self.setWindowTitle("설텍")
        self.setWindowIcon(QIcon("sultek.ico"))

        self.loadSetting()  # 설정된 옵션 불러오기
        self.pushButton_input.clicked.connect(self.addrInput)  # 입력버튼 이벤트 연결
        self.pushButton_stop.clicked.connect(self.stopCrawling)
        self.inputThread_var = None

        # 댓글 익명화를 위한 익명 리스트 미리 로딩
        anony_prefix = ['비옷입은', '시무룩한', '신난', '째려보는', '힙합', '베게를 든', '빈털터리', '응원하는', '멋쟁이', '일하는', '부끄러워하는', '인사하는',
                        '울고있는', '일하기 싫은', '소심한', '부탁하는', '단호한', '애교뿜뿜', '졸린', '먹보', '물 마시는', '피자 먹는', '퇴근하는', '치맥하는',
                        '말썽쟁이', '좌절하는', '화난', '건배하는', '호호 부는', '불 뿜는', '눈물 흘리는', '라면먹는', '티비보는', '블럭쌓는', '건방진', '화난',
                        '피스메이커', '벌 서는', '웃긴', '울고있는', '리듬타는', '청소하는', '휘파람', '음악듣는', '불 붙은', '얼어붙은']
        anony_suffix = ['엘사', '안나', '올라프', '카이', '겔다', '이두나', '아그나르', '불다', '파비', '오큰', '마시멜로', '스노기', '교황', '아렌델 시민',
                        '노덜드라인', '마티아스', '옐레나', '조안', '사만다', '아렌델 근위병', '아렌델 시녀']
        self.anony_list = []
        for pre in anony_prefix:
            for suf in anony_suffix:
                self.anony_list.append(pre + ' ' + suf)

    def loadSetting(self):
        saveData = []
        try:
            with open(currentDir + "/data.bin", "rb") as f:
                data = f.read()
                for d in data:
                    saveData.append(d)
        except Exception as e:
            return

        additionData = 10 - len(saveData)
        for i in range(additionData):
            saveData.append(0)

        if saveData[0] == 2:
            self.radioButton_txt_save_2.setChecked(True)
            self.groupBox_txt_filename.setEnabled(False)
            self.textFrame.setEnabled(True)
        elif saveData[0] == 3:
            self.radioButton_txt_save_3.setChecked(True)
            self.groupBox_txt_filename.setEnabled(True)
            self.textFrame.setEnabled(True)
        else:
            self.radioButton_txt_save_1.setChecked(True)
            self.groupBox_txt_filename.setEnabled(False)
            self.textFrame.setEnabled(False)

        if saveData[1] == 2:
            self.radioButton_txt_filename_2.setChecked(True)
            self.lineEdit_txt_filename.setEnabled(True)
        else:
            self.radioButton_txt_filename_1.setChecked(True)
            self.lineEdit_txt_filename.setEnabled(False)

        if saveData[2] == 1:
            self.checkBox_txt_img.setChecked(True)
        else:
            self.checkBox_txt_img.setChecked(False)

        if saveData[3] == 1:
            self.checkBox_txt_com.setChecked(True)
            self.checkBox_txt_com_anony.setEnabled(True)
        else:
            self.checkBox_txt_com.setChecked(False)
            self.checkBox_txt_com_anony.setEnabled(False)

        if saveData[8] == 1:
            self.checkBox_txt_com_anony.setChecked(True)
        else:
            self.checkBox_txt_com_anony.setChecked(False)

        if saveData[4] == 2:
            self.radioButton_pdf_save_2.setChecked(True)
            self.groupBox_pdf_filename.setEnabled(False)
            self.pdfFrame.setEnabled(True)
        elif saveData[4] == 3:
            self.radioButton_pdf_save_3.setChecked(True)
            self.groupBox_pdf_filename.setEnabled(True)
            self.pdfFrame.setEnabled(True)
        else:
            self.radioButton_pdf_save_1.setChecked(True)
            self.groupBox_pdf_filename.setEnabled(False)
            self.pdfFrame.setEnabled(False)

        if saveData[5] == 2:
            self.radioButton_pdf_filename_2.setChecked(True)
            self.lineEdit_pdf_filename.setEnabled(True)
        else:
            self.radioButton_pdf_filename_1.setChecked(True)
            self.lineEdit_pdf_filename.setEnabled(False)

        if saveData[6] == 1:
            self.checkBox_pdf_img.setChecked(True)
        else:
            self.checkBox_pdf_img.setChecked(False)

        if saveData[7] == 1:
            self.checkBox_pdf_com.setChecked(True)
            #self.checkBox_pdf_com_anony.setEnabled(True)
        else:
            self.checkBox_pdf_com.setChecked(False)
            #self.checkBox_pdf_com_anony.setEnabled(False)

        # PDF 익명화 버튼은 익명화가 자동 적용되면서 삭제됨
        # if saveData[9] == 1:
        #     self.checkBox_pdf_com_anony.setChecked(True)
        # else:
        #     self.checkBox_pdf_com_anony.setChecked(False)

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
            'pdfFileName_str': '',
            'textCommentAnony': 0,
            'pdfCommentAnony': 0
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

        if self.checkBox_txt_com_anony.isChecked():
            settings['textCommentAnony'] = 1

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

        # if self.checkBox_pdf_com_anony.isChecked():
        #     settings['pdfCommentAnony'] = 1

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
            option['pdfComment'],
            option['textCommentAnony'],
            option['pdfCommentAnony']
        ]

        with open(currentDir + "/data.bin", "wb") as f:
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
        self.inputThread_var.anony_list = self.anony_list  # 익명 리스트를 스레드에 전달
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
    anony_list = []
    tmpdir = ''

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
            random.shuffle(self.anony_list)  # 댓글 익명 리스트 셔플

            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    self.tmpdir = tmpdir
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

    def createFolder(self, directory, baseFolder=''):
        for i in '\/:*?"<>|':
            if i in directory:
                directory = directory.replace(i, '')
        directory = directory.strip()
        directory = baseFolder + '/' + directory

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

        title_div = soup.find('div', class_='post-cover').find('div', class_='inner')
        if option['textFileName'] == 1:
            title = title_div.find('h1').get_text().strip()
        else:
            title = option['textFileName_str']

        if option['pdfFileName'] == 1:
            pdftitle = title_div.find('h1').get_text().strip()
        else:
            pdftitle = option['pdfFileName_str']

        for i in '\/:*?"<>|':
            if i in title:
                title = title.replace(i, '')
            if i in pdftitle:
                pdftitle = pdftitle.replace(i, '')

        title = title.strip()
        pdftitle = pdftitle.strip()

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
        imagecrawl = option['imageDownload'] == 1
        commentcrawl = textcrawl and option['textComment'] == 1
        commentcrawlanony = commentcrawl and option['textCommentAnony'] == 1
        pdfcrawl = option['savePdfFile'] != 1
        pdfimagecrawl = pdfcrawl and option['pdfImage'] == 1
        pdfcommentcrawl = pdfcrawl and option['pdfComment'] == 1
        pdfcommentcrawlanony = pdfcommentcrawl and option['pdfCommentAnony'] == 1

        textfile = None
        pdffile = None
        # 한 파일에 저장
        if option['saveTextFile'] == 3:
            title_count = 2
            temp_title = title

            # 중복 파일 발견시 파일명에 숫자 붙이기
            while True:
                if not os.path.exists(currentDir + '/' + temp_title + ".txt"):
                    textfile = open(currentDir + '/' + temp_title + ".txt", "w", -1, 'utf-8')
                    break
                else:
                    temp_title = title + "_(%d)" % title_count
                    title_count += 1

        if option['savePdfFile'] == 3:
            pdffile = open(meipassDir + "/pdfHtml.html", "w", -1, 'utf-8')
            pdffile.write('<style>@font-face { font-family: "KoPub"; src: url(font/KoPub.ttf) format("truetype"); }')
            pdffile.write('div { font-family: KoPub; }')
            pdffile.write('.new_page { page-break-before: always; }</style>')

        # 창작물 리스트에서 하나씩 크롤링
        for l in link_list:
            count += 1
            if count < startCount:
                continue
            if count > endCount:
                break

            if self.stopProcess:
                if textfile:
                    textfile.close()
                if pdffile:
                    pdffile.close()
                self.paintEvent.emit("다운로드 중단됨\n")
                self.pbarRenew.emit(0)
                fail += endCount - count + 1
                return [endCount - startCount, fail]

            self.paintEvent.emit(str(count) + ' ')
            status = self.crawling(l, 1, multiFile=textfile, textcrawl=textcrawl, imagecrawl=imagecrawl,
                                   imagetitle=title, commentcrawl=commentcrawl,
                                   commentcrawlanony=commentcrawlanony, pdfMultiFile=pdffile,
                                   pdfcrawl=pdfcrawl, pdfimagecrawl=pdfimagecrawl,
                                   pdfcommentcrawl=pdfcommentcrawl,
                                   pdfcommentcrawlanony=pdfcommentcrawlanony)

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

        if textfile:
            textfile.close()

        if pdffile:
            pdffile.close()
            self.paintEvent.emit("PDF 파일 병합 중 ...")

            options = {
                'quiet': '',
                'page-size': 'A7',
                'page-width': '74mm',
                'page-height': '135.1mm',
                'margin-top': '0.1in',
                'margin-bottom': '0.1in',
                'margin-right': '0.1in',
                'margin-left': '0.1in',
                'encoding': "UTF-8",
                'custom-header': [
                    ('Accept-Encoding', 'gzip')
                ],
                'cookie': [
                    ('cookie-name1', 'cookie-value1'),
                    ('cookie-name2', 'cookie-value2'),
                ],
                'no-outline': None,
                'dpi': 400,
                'enable-local-file-access': None
            }

            config = pdfkit.configuration(wkhtmltopdf=meipassDir + r'\seoltekPDF\wkhtmltopdf.exe')

            title_count = 2
            temp_title = pdftitle

            # 중복 파일 발견시 파일명에 숫자 붙이기
            while True:
                if not os.path.exists(currentDir + '/' + temp_title + ".pdf"):
                    pdfkit.from_file(meipassDir + '/pdfHtml.html', currentDir + '/' + temp_title + '.pdf', options=options, configuration=config)
                    break
                else:
                    temp_title = pdftitle + "_(%d)" % title_count
                    title_count += 1

            self.paintEvent.emit("완료\n")

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

        iframe_soup = BeautifulSoup(iframe_source.content, 'html.parser')
        if d == 'v':
            post_div = iframe_soup.find('div', id='postViewArea')
            title_div = iframe_soup.find('div', id='title_1')
            title = title_div.find('span', class_='pcol1 itemSubjectBoldfont').get_text().strip()
            pdftitle = title_div.find('span', class_='pcol1 itemSubjectBoldfont').get_text().strip()
        else:
            post_div = iframe_soup.find('div', class_='se-module se-module-text')
            if post_div is None:
                post_div = iframe_soup.find('div', id='postViewArea')
                title_div = iframe_soup.find('div', class_='htitle')
            else:
                title_div = iframe_soup.find('div', class_='pcol1')
            title = title_div.find('span').get_text().strip()
            pdftitle = title_div.find('span').get_text().strip()

        if option['textFileName'] == 2:
            title = option['textFileName_str']

        if option['pdfFileName'] == 2:
            pdftitle = option['pdfFileName_str']

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
        imagecrawl = option['imageDownload'] == 1
        commentcrawl = textcrawl and option['textComment'] == 1
        commentcrawlanony = commentcrawl and option['textCommentAnony'] == 1
        pdfcrawl = option['savePdfFile'] != 1
        pdfimagecrawl = pdfcrawl and option['pdfImage'] == 1
        pdfcommentcrawl = pdfcrawl and option['pdfComment'] == 1
        pdfcommentcrawlanony = pdfcommentcrawl and option['pdfCommentAnony'] == 1

        textfile = None
        pdffile = None
        # 한 파일에 저장
        if option['saveTextFile'] == 3:
            title_count = 2
            temp_title = title

            # 중복 파일 발견시 파일명에 숫자 붙이기
            while True:
                if not os.path.exists(currentDir + '/' + temp_title + ".txt"):
                    textfile = open(currentDir + '/' + temp_title + ".txt", "w", -1, 'utf-8')
                    break
                else:
                    temp_title = title + "_(%d)" % title_count
                    title_count += 1

        if option['savePdfFile'] == 3:
            pdffile = open(meipassDir + "/pdfHtml.html", "w", -1, 'utf-8')
            pdffile.write('<style>@font-face { font-family: "KoPub"; src: url(font/KoPub.ttf) format("truetype"); }')
            pdffile.write('div { font-family: KoPub; }')
            pdffile.write('.new_page { page-break-before: always; }</style>')

        # 창작물 리스트에서 하나씩 크롤링
        for l in link_list:
            count += 1
            if count < startCount:
                continue
            if count > endCount:
                break

            if self.stopProcess:
                if textfile:
                    textfile.close()
                if pdffile:
                    pdffile.close()
                self.paintEvent.emit("다운로드 중단됨\n")
                self.pbarRenew.emit(0)
                fail += endCount - count + 1
                return [endCount - startCount, fail]

            self.paintEvent.emit(str(count) + ' ')
            status = self.crawling(l, 1, multiFile=textfile, textcrawl=textcrawl, imagecrawl=imagecrawl,
                                   imagetitle=title, commentcrawl=commentcrawl,
                                   commentcrawlanony=commentcrawlanony, pdfMultiFile=pdffile,
                                   pdfcrawl=pdfcrawl, pdfimagecrawl=pdfimagecrawl,
                                   pdfcommentcrawl=pdfcommentcrawl,
                                   pdfcommentcrawlanony=pdfcommentcrawlanony)
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

        if textfile:
            textfile.close()

        if pdffile:
            pdffile.close()
            self.paintEvent.emit("PDF 파일 병합 중 ...")

            options = {
                'page-size': 'A7',
                'page-width': '74mm',
                'page-height': '135.1mm',
                'margin-top': '0.1in',
                'margin-bottom': '0.1in',
                'margin-right': '0.1in',
                'margin-left': '0.1in',
                'encoding': "UTF-8",
                'custom-header': [
                    ('Accept-Encoding', 'gzip')
                ],
                'cookie': [
                    ('cookie-name1', 'cookie-value1'),
                    ('cookie-name2', 'cookie-value2'),
                ],
                'no-outline': None,
                'dpi': 400,
                'enable-local-file-access': None
            }

            config = pdfkit.configuration(wkhtmltopdf=meipassDir + r'\seoltekPDF\wkhtmltopdf.exe')

            title_count = 2
            temp_title = pdftitle

            # 중복 파일 발견시 파일명에 숫자 붙이기
            while True:
                if not os.path.exists(currentDir + '/' + temp_title + ".pdf"):
                    pdfkit.from_file(meipassDir + '/pdfHtml.html', currentDir + '/' + temp_title + '.pdf', options=options, configuration=config)
                    break
                else:
                    temp_title = pdftitle + "_(%d)" % title_count
                    title_count += 1

            self.paintEvent.emit("완료\n")

        success = endCount - startCount + 1 - fail
        self.paintEvent.emit("결과 : {0}개 성공, {1}개 실패\n\n".format(success, fail))

    def single_crawling(self, URL, option):

        self.pbarSet.emit(1)

        textcrawl = option['saveTextFile'] != 1
        imagecrawl = option['imageDownload'] == 1
        commentcrawl = textcrawl and option['textComment'] == 1
        commentcrawlanony = commentcrawl and option['textCommentAnony'] == 1
        pdfcrawl = option['savePdfFile'] != 1
        pdfimagecrawl = pdfcrawl and option['pdfImage'] == 1
        pdfcommentcrawl = pdfcrawl and option['pdfComment'] == 1
        pdfcommentcrawlanony = pdfcommentcrawl and option['pdfCommentAnony'] == 1

        if URL.isdigit():
            status = self.crawling(URL, 0, textcrawl=textcrawl, imagecrawl=imagecrawl, commentcrawl=commentcrawl,
                                   commentcrawlanony=commentcrawlanony, pdfcrawl=pdfcrawl, pdfimagecrawl=pdfimagecrawl,
                                   pdfcommentcrawl=pdfcommentcrawl,pdfcommentcrawlanony=pdfcommentcrawlanony)
            if status and status['error'] == 404:
                self.paintEvent.emit("<b>삭제된 페이지입니다</b>\n")
        else:
            status = self.crawling(URL, 1, textcrawl=textcrawl, imagecrawl=imagecrawl, commentcrawl=commentcrawl,
                                   commentcrawlanony=commentcrawlanony, pdfcrawl=pdfcrawl, pdfimagecrawl=pdfimagecrawl,
                                   pdfcommentcrawl=pdfcommentcrawl,pdfcommentcrawlanony=pdfcommentcrawlanony)
            if status and status['error'] == 404:
                self.paintEvent.emit("<b>삭제된 페이지입니다</b>\n")

        self.pbarRenew.emit(1)

    def comm_crawling(self, url, gall_id, gall_num, dcconcrawl=False):

        commentWriter = {}
        anonyNameIndex = 0

        page_count = 1
        comment_list = {'list': [], 'cnt': 0}
        imgtagList = []
        imgsrcList = []
        while True:
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
                return {}

            headers = {
                'Referer': url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }

            comment = requests.post('https://gall.dcinside.com/board/comment/', headers=headers, data=data).text
            json_data = json.loads(comment)
            comment_list['cnt'] = json_data['total_cnt']

            if json_data['comments'] is None:  # 댓글 크롤링 완료
                if dcconcrawl:
                    imageCrawlData = self.image_crawling(url, imgsrcList, imagename='/dccon' + str(gall_num), baseFolder=self.tmpdir)
                    fail = imageCrawlData['fail']
                    for i in range(len(imgtagList)):
                        filename = imageCrawlData['fnList'][i]
                        imgtagList[i]['src'] = 'file:///' + filename
                        imgtagList[i]['width'] = "75px"
                        imgtagList[i]['height'] = "auto"

                return comment_list

            temp_list = []
            for i in json_data['comments']:
                temp_comment = {}
                text = ''
                if i['no'] == 0:
                    continue

                temp_comment['depth'] = i['depth']
                temp_comment['name'] = i['name']
                temp_comment['ip'] = i['ip']

                if i['is_delete'] == '0':
                    if i['user_id']:  # 고닉
                        if not i['name'] in commentWriter:
                            commentWriter[i['name']] = self.anony_list[anonyNameIndex]
                            anonyNameIndex += 1
                        temp_comment['anonyName'] = commentWriter[i['name']]
                    else:  # 유동
                        temp_comment['anonyName'] = self.anony_list[anonyNameIndex]
                        anonyNameIndex += 1
                else:
                    temp_comment['anonyName'] = ''


                if anonyNameIndex >= len(self.anony_list):
                    anonyNameIndex = 0
                    random.shuffle(self.anony_list)

                temp_comment['delete'] = i['is_delete']
                if len(i['reg_date']) < 15:
                    temp_comment['date'] = str(datetime.datetime.now().year) + '.' + i['reg_date']
                else:
                    temp_comment['date'] = i['reg_date']

                memo_soup = BeautifulSoup(i['memo'], 'html.parser')
                imgtag = memo_soup.find('img')
                giftag = memo_soup.find('video')
                if imgtag:
                    temp_comment['type'] = 'dccon'
                    temp_comment['memo'] = imgtag
                    imgsrcList.append(imgtag.attrs['src'])
                    imgtagList.append(imgtag)
                elif giftag:
                    temp_comment['type'] = 'dccon'
                    temp_comment['memo'] = giftag
                    gifsrc = giftag.attrs['data-src']
                    imgsrcList.append(gifsrc)
                    giftag.name = 'img'  # change <video> tag into <img> tag
                    giftag.attrs = {'src': gifsrc}
                    try:  # delete source tag in giftag
                        giftag.source.decompose()
                    except Exception as e:
                        pass
                    imgtagList.append(giftag)
                elif i['vr_player'] is not False:
                    temp_comment['type'] = 'voice'
                    temp_comment['memo'] = '(보이스리플)'
                else:
                    temp_comment['type'] = 'text'
                    temp_comment['memo'] = memo_soup.get_text()

                temp_list.append(temp_comment)
            comment_list['list'] = temp_list.copy() + comment_list['list']
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

    def image_crawling(self, url, imgtag, imgttl=None, imagename='image', baseFolder = ''):
        fail = 0

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            'Referer': url
        }

        filenameList = []
        for i in range(len(imgtag)):
            try:
                img_file = requests.get(imgtag[i], headers=headers)
                img_data = img_file.content
            except Exception as e:
                fail += 1
                filenameList.append('')
                continue

            if imgttl is None:
                filename = baseFolder + "/" + imagename + "-%03d" % (i + 1)
                f = open(filename, 'wb')
            else:
                self.createFolder(imgttl, baseFolder=baseFolder)
                filename = baseFolder + "/" + imgttl + "/" + imagename + "-%03d" % (i + 1)
                f = open(filename, 'wb')

            f.write(img_data)
            f.close()


            kind = filetype.guess(filename)
            if kind is None:
                fail += 1
                os.remove(filename)
                filenameList.append('')
                continue

            if os.path.exists(filename + '.' + kind.extension):
                os.remove(filename + '.' + kind.extension)
            os.rename(filename, filename + '.' + kind.extension)

            filenameList.append(filename + '.' + kind.extension)
            time.sleep(0.2)
        return {'amount': len(imgtag), 'fail': fail, 'fnList': filenameList }

    def crawling(self, URL, mode, multiFile=None, textcrawl=True, imagecrawl=False, imagetitle=None, commentcrawl=False,
                 commentcrawlanony=False, pdfMultiFile=None, pdfcrawl=False, pdfimagecrawl=False, pdfcommentcrawl=False,
                 pdfcommentcrawlanony=True):

            # PDF 댓글 익명화 항상 적용
            pdfcommentcrawlanony = True
            
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

            title = soup.find('span', class_='title_subject').text
            pdftitle = soup.find('span', class_='title_subject').text

            for i in '\/:*?"<>|':
                if i in title:
                    title = title.replace(i, '')
                if i in pdftitle:
                    pdftitle = pdftitle.replace(i, '')

            title = title.strip()
            pdftitle = pdftitle.strip()

            self.paintEvent.emit(title + " ...")

            textfile = None
            pdffile = None

            try:
                url = re.search('(.+?no=\d+)?', source.url)
                if url:
                    url = url.group(1)

                comment = None

                if textcrawl:
                    if multiFile is not None:
                        textfile = multiFile
                    else:
                        textfile = open(currentDir + '/' + title + ".txt", "w", -1, 'utf-8')

                    textfile.write(title)
                    textfile.write("\n-------------------------------------------\n" + url + "\n\n\n")

                    write_div = soup.select_one('div.write_div')

                    con_list = write_div.contents[1:-1]
                    for con in con_list:
                        self.htmltree(con, 0, textfile)
                    textfile.write('\n\n')

                    if commentcrawl is True:
                        comment = self.comm_crawling(url, gall_id, gall_num, dcconcrawl=pdfcommentcrawl)
                        len_comment = comment['cnt']

                        if len_comment > 0:
                            textfile.write("전체 댓글 %d개 ▼\n" % len_comment)

                        for comm in comment['list']:
                            text = ''
                            if comm['depth'] > 0:
                                text += '↳ '
                            if comm['delete'] == '0':
                                if commentcrawlanony:
                                    text += '[' + comm['anonyName']
                                else:
                                    text += '[' + comm['name']
                                    if comm['ip'] != '':
                                        text += '(' + comm['ip'] + ')'

                                if comm['type'] == 'dccon':
                                    text += ']  (디시콘)'
                                else:
                                    text += ']  ' + comm['memo']
                            else:
                                text += '(' + comm['memo'] + ')'

                            textfile.write(text + '\n')
                        textfile.write('\n\n')

                    if multiFile is None:
                        textfile.close()
                    self.paintEvent.emit("변환완료")

                success = 0
                fail = 0
                filenameList = []
                imgtag = None
                if imagecrawl is True:
                    write_view = soup.select_one('div.writing_view_box')

                    if write_view is not None:
                        giftag = write_view.find_all('video')  # change DCcon with <video> tag into <img> tag
                        for gif in giftag:
                            if gif.attrs['class'][0] != 'dc_mv':
                                gifsrc = gif.attrs['data-src']
                                gif.name = 'img'
                                gif.attrs = {'src': gifsrc}

                        imgtag = write_view.find_all('img')
                        imgsrcList = []
                        for img in imgtag:
                            try:
                                src = re.search("(https.+?)\'", img.attrs['onclick'])  # original image-web source
                                src = (src.group(1)).replace('viewimagePop.php?', 'viewimage.php?id=&')  # retrieve image source
                            except Exception as e:
                                src = img.attrs['src']
                            imgsrcList.append(src)
                        if len(imgtag) > 0:
                            imageCrawlData = self.image_crawling(url, imgsrcList, imgttl=imagetitle,
                                                                 imagename=gall_id + '-' + gall_num, baseFolder=currentDir)
                            success = imageCrawlData['amount'] - imageCrawlData['fail']
                            fail = imageCrawlData['fail']
                            filenameList = imageCrawlData['fnList']
                            self.paintEvent.emit(" (이미지 {0}개 다운로드".format(success))
                            if fail > 0:
                                self.paintEvent.emit(", <b>{0}개 실패</b>".format(fail))
                            self.paintEvent.emit(')')
                        elif textcrawl is False:
                            self.paintEvent.emit("이미지 없음")

                if textcrawl is True or imagecrawl is True:
                    self.paintEvent.emit('\n')

                if pdfcrawl:
                    try:
                        write_view = soup.select_one('div.writing_view_box')
                        pdfdata = ''

                        if pdfMultiFile is not None:
                            pdffile = pdfMultiFile
                        else:
                            pdffile = open(meipassDir + '/pdfHtml.html', "w", -1, 'utf-8')
                            pdfdata += '<style>@font-face { font-family: "KoPub"; src: url(font/KoPub.ttf) format("truetype"); }'
                            pdfdata += 'div { font-family: KoPub; }'
                            pdfdata += '.new_page { page-break-before: always; }</style>'

                        write_div = soup.select_one('div.write_div')  # 본문
                        for obj in write_div.find_all('object'):
                            obj.decompose()
                        for img in write_div.find_all('img'):
                            img['style'] = "max-width: 100%; height: auto;"
                        write_div[
                            'style'] = 'font-family: KoPub; font-size: 10pt;'  # text-indext: 10px; <br>들어가면 들여쓰기 안해서 뺌

                        if pdfimagecrawl is False:
                            for img in write_div.find_all('img'):
                                img.decompose()
                        else:
                            if imagecrawl and imgtag:
                                for i in range(len(imgtag)):
                                    imgtag[i]['src'] = 'file:///' + filenameList[i]
                            else:
                                giftag = write_view.find_all('video')  # change DCcon with <video> tag into <img> tag
                                for gif in giftag:
                                    if gif.attrs['class'][0] != 'dc_mv':
                                        gifsrc = gif.attrs['data-src']
                                        gif.name = 'img'
                                        gif.attrs = {'src': gifsrc}

                                imgtag = write_view.find_all('img')
                                imgsrcList = []
                                for img in imgtag:
                                    try:
                                        src = re.search("(https.+?)\'",
                                                        img.attrs['onclick'])  # original image-web source
                                        src = (src.group(1)).replace('viewimagePop.php?',
                                                                     'viewimage.php?id=&')  # retrieve image source
                                    except Exception as e:
                                        src = img.attrs['src']
                                    imgsrcList.append(src)
                                if len(imgtag) > 0:
                                    imageCrawlData = self.image_crawling(url, imgsrcList,
                                                                         imagename='/temp' + gall_num, baseFolder=self.tmpdir)
                                    success = imageCrawlData['amount'] - imageCrawlData['fail']
                                    fail = imageCrawlData['fail']
                                    filenameList = imageCrawlData['fnList']

                                    for i in range(len(imgtag)):
                                        imgtag[i]['src'] = 'file:///' + filenameList[i]

                        write_div = str(write_div)

                        options = {
                            'quiet': '',
                            'page-size': 'A7',
                            'page-width': '74mm',
                            'page-height': '135.1mm',
                            'margin-top': '0.1in',
                            'margin-bottom': '0.1in',
                            'margin-right': '0.1in',
                            'margin-left': '0.1in',
                            'encoding': "UTF-8",
                            'custom-header': [
                                ('Accept-Encoding', 'gzip')
                            ],
                            'cookie': [
                                ('cookie-name1', 'cookie-value1'),
                                ('cookie-name2', 'cookie-value2'),
                            ],
                            'no-outline': None,
                            'dpi': 400,
                            'enable-local-file-access': None
                        }

                        config = pdfkit.configuration(wkhtmltopdf=meipassDir + r'\seoltekPDF\wkhtmltopdf.exe')

                        head_html = '<head><meta charset="utf-8"></head><div class="new_page">'  # 헤더
                        header_div = soup.find('div', 'gallview_head clear ub-content')
                        header_title = header_div.find('span', 'title_subject')
                        head_html += '<table width=100%><tr><td style="border-bottom: 0.5px solid #d3d3d3; font-family: KoPub; font-size: 10pt;">'
                        head_html += '<p style="padding: 5px 0px 5px 0px;"><a href="{0}" style="text-decoration: none;"><font color=black><b>{1}</b></font></a></p>'.format(url, header_title)
                        head_html += '</td></tr></table></div><br/>'


                        comm_html = ''  # 댓글
                        if pdfcommentcrawl is True:
                            if not comment:
                                comment = self.comm_crawling(url, gall_id, gall_num, dcconcrawl=True)
                            comm_html = '<br/><br/><div style="font-family: KoPub;">'
                            comm_html += '<table width=100% style="font-size: 9pt;"><tr bgcolor="#f3f3f3" style="border: 0.5px solid #d3d3d3">' \
                                         '<td>댓글 {0}</td></tr>'.format(comment['cnt'])
                            for comm in comment['list']:
                                # PDF 익명댓글 항상 적용
                                # if pdfcommentcrawlanony:
                                if True:
                                    name = comm['anonyName']
                                else:
                                    name = comm['name']
                                    if comm['ip'] != '':
                                        name += '<font color="grey">(' + comm['ip'] + ')</font>'

                                name = '<b>' + name + '</b>'

                                comm_html += '<tr><td style="border-bottom: 0.5px solid #d3d3d3;"><table style="font-size: 9pt;">'
                                if comm['depth'] > 0:
                                    if comm['delete'] == '0':
                                        comm_html += '<tr><td width="15px"><img width=8px height=auto src="file:///'+meipassDir+'/arrow.png" style="padding: 5px 0px 0px 0px;"/></td><td style="font-size: 8pt;">{0}</td></tr>'.format(name)
                                        comm_html += '<tr><td></td><td>{0}</td></tr>'.format(comm['memo'])
                                        comm_html += '<tr><td></td><td style="font-size: 8pt;"><font face="맑은 고딕" color="grey">{0}</font></td></tr>'.format(comm['date'][:-3])
                                    else:
                                        comm_html += '<tr rowspan="3"><td width="15px"><img width=10px height=auto src="file:///'+meipassDir+'/arrow.png"/ style="padding: 5px 0px 0px 0px;"></td><td><font color="grey">{0}</font></td></tr>'.format(comm['memo'])

                                else:
                                    if comm['delete'] == '0':
                                        comm_html += '<tr><td colspan="2" style="font-size: 8pt;">{0}</td></tr>'.format(name)
                                        comm_html += '<tr><td colspan="2">{0}</td></tr>'.format(comm['memo'])
                                        comm_html += '<tr><td colspan="2" style="font-size: 8pt;"><font face="맑은 고딕" color="grey">{0}</font></td></tr>'.format(comm['date'][:-3])
                                    else:
                                        comm_html += '<tr rowspan="3"><td colspan="2"><font color="grey">{0}</font></td></tr>'.format(comm['memo'])
                                comm_html += '</table></td></tr>'

                            comm_html += '</table></div>'
                        pdfdata += head_html + write_div + comm_html
                        pdffile.write(pdfdata)
                        if pdfMultiFile is None:
                            pdffile.close()
                            pdfkit.from_file(meipassDir + '/pdfHtml.html', currentDir + '/' + pdftitle + '.pdf', options=options, configuration=config)

                        self.paintEvent.emit("PDF 변환완료")
                        if fail > 0:
                            self.paintEvent.emit("(<b>{0}개 이미지 첨부 실패</b>)".format(fail))
                        self.paintEvent.emit('\n')

                    except Exception as e:
                        self.paintEvent.emit("<b>PDF 변환실패</b>\n")
                        self.paintEvent.emit("에러메시지 : " + str(e) + '\n')

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
