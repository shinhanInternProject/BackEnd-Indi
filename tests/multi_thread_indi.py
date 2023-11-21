import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
import pandas as pd
import GiExpertControl as giLogin  # 통신모듈 - 로그인
import GiExpertControl as giStockRTTRShow
import GiExpertControl as TRShow
from dotenv import load_dotenv
import os
import time

# load .env
load_dotenv()

INDI_ID = os.environ.get('INDI_ID')
INDI_PW = os.environ.get('INDI_PW')
# INDI_GOPW = os.environ.get('INDI_GOPW')

# 초기 로그인 및 함수 연결
class indi(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.setWindowTitle("IndiExample")
        TRShow.SetQtMode(True) 
        print('finish qt mode set')
        # giStockRTTRShow.RunIndiPython()
        TRShow.RunIndiPython()
        giLogin.RunIndiPython()
        print('run python')

        self.rqidD = {}

        print(giLogin.GetCommState())
        if giLogin.GetCommState() == 0:  # 정상
            print('정상')
        elif giLogin.GetCommState() == 1:  # 비정상
            print('비정상')
            # 본인의 ID 및 PW 넣으셔야 합니다.
            login_return = giLogin.StartIndi(
                INDI_ID, INDI_PW, '', 'C:\\SHINHAN-i\\indi\\GiExpertStarter.exe')
            if login_return == True:
                print("INDI 로그인 정보", "INDI 정상 호출")
                print(giLogin.GetCommState())
            else:
                print("INDI 로그인 정보", "INDI 호출 실패")

        self.search_stock_news()
        # time.sleep(5)
        TRShow.SetCallBack('ReceiveData', self.TRShow_ReceiveData)

    # 뉴스 목록 조회 
    def search_stock_news(self):
        stbd_code = '005930' # 종목코드
        search_date = '20231103' # 조회일자
        news_type = '1' # 뉴스타입

        TR_Name = "TR_3100_D"
        ret = TRShow.SetQueryName(TR_Name)
        ret = TRShow.SetSingleData(0,stbd_code) # 종목코드
        ret = TRShow.SetSingleData(1,news_type) # 뉴스 구분
        ret = TRShow.SetSingleData(2,search_date) # 조회 일자

        rqid = TRShow.RequestData() # 보내기(리퀘스트)

        print(TRShow.GetErrorCode())
        print(TRShow.GetErrorMessage())
        
        print(type(rqid))
        print('Request Data rqid: ' + str(rqid))
        self.rqidD[rqid] = TR_Name  

    # TR data 처리
    def TRShow_ReceiveData(self,giCtrl,rqid):
        print("in receive_Data:",rqid)
        print('recv rqid: {}->{}\n'.format(rqid, self.rqidD[rqid]))
        TR_Name = self.rqidD[rqid]
        tr_data_output = []
        output = []

        print("TR_name : ",TR_Name)
        
        # 종목 뉴스 목록 조회
        if TR_Name == "TR_3100_D":
            nCnt = giCtrl.GetMultiRowCount()
            print("c")
            print(nCnt)

            for i in range(0, nCnt):
                tr_data_output.append([])
                tr_data_output[i].append((str(giCtrl.GetMultiData(i, 0)))) # 뉴스 일자
                tr_data_output[i].append((str(giCtrl.GetMultiData(i, 4)))) # 뉴스 기사번호
                tr_data_output[i].append((str(giCtrl.GetMultiData(i, 3)))) # 뉴스 구분
                tr_data_output[i].append((str(giCtrl.GetMultiData(i, 2)))) # 뉴스 제목
            print(TRShow.GetErrorCode())
            print(TRShow.GetErrorMessage())

        # 뉴스 내용 조회
        if TR_Name == "TR_3100":
            nCnt = giCtrl.GetMultiRowCount()
            print("c")
            print(nCnt)
            news_article = """"""
            for i in range(0, nCnt):
                news_article += str(giCtrl.GetMultiData(i,4))
                news_article += str(giCtrl.GetMultiData(i,5))
                news_article += str(giCtrl.GetMultiData(i,6))
            print(TRShow.GetErrorCode())
            print(TRShow.GetErrorMessage())

# main - 실행
app = QApplication(sys.argv)
indi = indi()
app.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    indi = indi()
    app.exec_()
