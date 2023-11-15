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
import asyncio

# load .env
load_dotenv()

INDI_ID = os.environ.get('INDI_ID')
INDI_PW = os.environ.get('INDI_PW')


async def wait_data(key, result):
    while key not in result:
        await asyncio.sleep(1)
    return result[key]

# -----------------------------------------------------------

class indiApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # qt모드 세팅
        TRShow.SetQtMode(True)
        # IndiPython 실행
        TRShow.RunIndiPython()
        giLogin.RunIndiPython()
        RTShow.RunIndiPython()

        print('run python')

        # RecieveData를 위한 dict
        self.rqidD = {}
        # api response용 dict
        self.callback_result = {}

        # 로그인
        print(giLogin.GetCommState())
        if giLogin.GetCommState() == 0:  # 정상
            print('정상')
        elif giLogin.GetCommState() == 1:  # 비정상
            print('비정상')
            # 본인의 ID 및 PW
            login_return = giLogin.StartIndi(
                INDI_ID, INDI_PW, '', 'C:\\SHINHAN-i\\indi\\GiExpertStarter.exe')
            if login_return == True:
                print("INDI 로그인 정보", "INDI 정상 호출")
                print(giLogin.GetCommState())
            else:
                print("INDI 로그인 정보", "INDI 호출 실패")

        # TR 응답 처리
        TRShow.SetCallBack('ReceiveData', self.TRShow_ReceiveData)

# -----------------------------------------------------------
# 주식 데이터
    
    # 업종 관련 종목 조회
    # TR : upjong_code_mst
    async def category_stock_list(self, req_category_code):
        # TR 명
        TR_Name = "upjong_code_mst"

        # Input Feild
        ret = TRShow.SetQueryName(TR_Name)
        ret = TRShow.SetSingleData(0, req_category_code)  # 업종코드
        
        # 보내기(리퀘스트)
        rqid = TRShow.RequestData()
        
        # Error 
        print(TRShow.GetErrorCode())
        print(TRShow.GetErrorMessage())

        print(type(rqid))
        print('Request Data rqid: ' + str(rqid))
        
        # ReceiveData 구분용
        self.rqidD[rqid] = TR_Name

        # Response 전달용
        result = await wait_data(rqid, self.callback_result)
        self.callback_result = {}
        print(result)
        return result
    
    # 종목 등락률, 시가총액 조회
    # TR : TR_1110_11
    async def stock_data(self, req_stock_code):
        pass
    
    # 종목 ohlc 데이터 조회
    # TR : TR_SCHART
    async def stock_ohlc(self, req_stock_code, req_start_date, req_end_date):
        pass

# -----------------------------------------------------------
# 뉴스 데이터
    
    # 뉴스 목록 조회
    # TR : TR_3100_D
    async def search_stock_news_list(self, req_stock_code, req_search_date, req_news_type):
        pass
    
    # 뉴스 내용 조회
    # TR : TR_3100
    async def search_stock_news_detail(self, req_stock_code, req_news_code, req_search_date, req_news_type_code):
        pass


# -----------------------------------------------------------
    # TR data 처리 - 참고용
    def TRShow_ReceiveData(self, giCtrl, rqid):
        # receive시 출력
        print("in receive_Data:", rqid)
        print('recv rqid: {}->{}\n'.format(rqid, self.rqidD[rqid]))
        TR_Name = self.rqidD[rqid]
        tr_data_output = []
        output = []

        # 받은 TR 명
        print("TR_name : ", TR_Name)
        
        # Stock
        # case 업종 종목 조회
        if TR_Name == "upjong_code_mst":
            nCnt = giCtrl.GetMultiRowCount()
            print("c")
            print(nCnt)

            for i in range(0, nCnt):
                tr_data_output.append({})
                tr_data_output[i]["stbd_code"] = str(giCtrl.GetMultiData(i, 0))
                tr_data_output[i]["stbd_nm"] = str(giCtrl.GetMultiData(i, 1))
                # tr_data_output.append([])
                # tr_data_output[i].append(
                #     (str(giCtrl.GetMultiData(i, 0))))  # 종목 코드
                # tr_data_output[i].append(
                #     (str(giCtrl.GetMultiData(i, 1))))  # 종목 이름
            print(TRShow.GetErrorCode())
            print(TRShow.GetErrorMessage())
            
            # 반환 값 저장
            self.callback_result[rqid] = tr_data_output

        
        # News
        # 종목 뉴스 목록 조회
        if TR_Name == "TR_3100_D":
            nCnt = giCtrl.GetMultiRowCount()
            print("c")
            print(nCnt)

            for i in range(0, nCnt):
                tr_data_output.append([])
                tr_data_output[i].append(
                    (str(giCtrl.GetMultiData(i, 0))))  # 뉴스 일자
                tr_data_output[i].append(
                    (str(giCtrl.GetMultiData(i, 4))))  # 뉴스 기사번호
                tr_data_output[i].append(
                    (str(giCtrl.GetMultiData(i, 3))))  # 뉴스 구분
                tr_data_output[i].append(
                    (str(giCtrl.GetMultiData(i, 2))))  # 뉴스 제목
            print(TRShow.GetErrorCode())
            print(TRShow.GetErrorMessage())
            self.callback_result[rqid] = tr_data_output

        # 뉴스 내용 조회
        if TR_Name == "TR_3100":
            nCnt = giCtrl.GetMultiRowCount()
            print("c")
            print(nCnt)
            news_article = """"""
            for i in range(0, nCnt):
                tr_data_output.append(str(giCtrl.GetMultiData(i, 4)))
                tr_data_output.append(str(giCtrl.GetMultiData(i, 5)))
                tr_data_output.append(str(giCtrl.GetMultiData(i, 6)))
                news_article += str(giCtrl.GetMultiData(i, 4))
                news_article += str(giCtrl.GetMultiData(i, 5))
                news_article += str(giCtrl.GetMultiData(i, 6))
            print(TRShow.GetErrorCode())
            print(TRShow.GetErrorMessage())
            self.callback_result[rqid] = tr_data_output

        # 재무데이터 조회
        if TR_Name == "TR4_FUNDA3":
            nCnt = giCtrl.GetMultiRowCount()
            print("c")
            print(nCnt)

            for i in range(0, nCnt):
                tr_data_output.append([])
                tr_data_output[i].append(
                    str(giCtrl.GetMultiData(i, 1)))  # 기간구분
                tr_data_output[i].append(
                    str(giCtrl.GetMultiData(i, 10)))  # EPS
                tr_data_output[i].append(str(giCtrl.GetMultiData(i, 9)))  # ROE
                tr_data_output[i].append(
                    str(giCtrl.GetMultiData(i, 13)))  # PER
                tr_data_output[i].append(
                    str(giCtrl.GetMultiData(i, 12)))  # BPS
                tr_data_output[i].append(
                    str(giCtrl.GetMultiData(i, 15)))  # PBR
                tr_data_output[i].append(
                    str(giCtrl.GetMultiData(i, 6)))  # 당기순이익
            print(TRShow.GetErrorCode())
            print(TRShow.GetErrorMessage())
            self.callback_result[rqid] = tr_data_output
