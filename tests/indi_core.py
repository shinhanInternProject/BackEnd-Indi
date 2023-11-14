import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
import pandas as pd
import GiExpertControl as giLogin  # 통신모듈 - 로그인
import GiExpertControl as RTShow
import GiExpertControl as TRShow
from dotenv import load_dotenv
import os
import time
import asyncio

# load .env
load_dotenv()

INDI_ID = os.environ.get('INDI_ID')
INDI_PW = os.environ.get('INDI_PW')

async def wait_data(key, result):
    while key not in result:
        await asyncio.sleep(1)
    return result[key]


class indiApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.setWindowTitle("IndiExample")
        TRShow.SetQtMode(True) 
        print('finish qt mode set')
        TRShow.RunIndiPython()
        giLogin.RunIndiPython()
        RTShow.RunIndiPython()

        print('run python')

        self.rqidD = {}
        self.tempResult = {}
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

        # 실시간 데이터 callback
        RTShow.SetCallBack('ReceiveRTData', self.RTShow_ReceiveRTData)


    
    # 뉴스 목록 조회 
    async def search_stock_news(self):
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
        
        temp = await wait_data(rqid, self.tempResult)
        self.tempResult = {}
        
        return temp
    
    

    # 종목 정보 조회
    async def pushButton_search_stock_info(self):
        stbd_code = '005930' # 종목코드
        
        # 1. 재무데이터 조회
        TR_Name = "TR4_FUNDA3"
        ret = TRShow.SetQueryName(TR_Name)          
        ret = TRShow.SetSingleData(0,stbd_code) # 종목코드
        ret = TRShow.SetSingleData(1,'0') # 개별/연결 구분
        ret = TRShow.SetSingleData(2,'0') # 결산/분기 구분

        rqid = TRShow.RequestData() # 보내기(리퀘스트)

        print(TRShow.GetErrorCode())
        print(TRShow.GetErrorMessage())
        
        print(type(rqid))
        print('Request Data rqid: ' + str(rqid))
        self.rqidD[rqid] = TR_Name

        temp = await wait_data(rqid, self.tempResult)
        self.tempResult = {}
        
        return temp  

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
            self.tempResult[rqid] = tr_data_output

        # 뉴스 내용 조회
        if TR_Name == "TR_3100":    
            nCnt = giCtrl.GetMultiRowCount()
            print("c")
            print(nCnt)
            news_article = """"""
            for i in range(0, nCnt):
                tr_data_output.append(str(giCtrl.GetMultiData(i,4)))
                tr_data_output.append(str(giCtrl.GetMultiData(i,5)))
                tr_data_output.append(str(giCtrl.GetMultiData(i,6)))
                news_article += str(giCtrl.GetMultiData(i,4))
                news_article += str(giCtrl.GetMultiData(i,5))
                news_article += str(giCtrl.GetMultiData(i,6))
            print(TRShow.GetErrorCode())
            print(TRShow.GetErrorMessage())
            self.tempResult[rqid] = tr_data_output

        # 재무데이터 조회
        if TR_Name == "TR4_FUNDA3":
            nCnt = giCtrl.GetMultiRowCount()
            print("c")
            print(nCnt)
            
            for i in range(0, nCnt):
                tr_data_output.append([])
                tr_data_output[i].append(str(giCtrl.GetMultiData(i, 1))) # 기간구분
                tr_data_output[i].append(str(giCtrl.GetMultiData(i, 10))) # EPS
                tr_data_output[i].append(str(giCtrl.GetMultiData(i, 9))) # ROE
                tr_data_output[i].append(str(giCtrl.GetMultiData(i, 13))) # PER
                tr_data_output[i].append(str(giCtrl.GetMultiData(i, 12))) # BPS
                tr_data_output[i].append(str(giCtrl.GetMultiData(i, 15))) # PBR
                tr_data_output[i].append(str(giCtrl.GetMultiData(i, 6))) # 당기순이익
            print(TRShow.GetErrorCode())
            print(TRShow.GetErrorMessage())
            self.tempResult[rqid] = tr_data_output

    # 실시간 현재가 조회 버튼
    def request_rt(self):
        stbd_code = '005930'

        rqid = RTShow.RequestRTReg("SC",stbd_code) # 실시간 현재가
        print(type(rqid))
        print('Request Data rqid: ' + str(rqid))
             
    # 실시간 현재가 조회 중지 버튼
    def req_rt_stop(self):
        stbd_code = '005930'
        ret = RTShow.UnRequestRTReg("SC",stbd_code)
        print(ret)

    # 실시간 데이터 처리
    def RTShow_ReceiveRTData(self,giCtrl,RealType):
        if RealType == "SC":
            print(str(giCtrl.GetSingleData(3))) # 현재가
            print(RTShow.GetErrorCode())
            print(RTShow.GetErrorMessage())
            # print(str(giCtrl.GetSingleData(3))) # 현재가
            # print(str(giCtrl.GetSingleData(10))) # 시가
            # print(str(giCtrl.GetSingleData(11))) # 고가
            # print(str(giCtrl.GetSingleData(12))) # 저가