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
    count = 0
    while key not in result:
        await asyncio.sleep(0.2)
        count += 1
        if count > 15:
            return 0
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
    # TR : upjong_code_mst -> indi상에서 문제가 있는 것 같아보임
    # TR : TR_1871_2
    async def category_stock_list(self, req_category_code):
        TR_Name = "TR_1871_2"
        market_type = req_category_code[0]
        st_date = "20231116"
        end_date = "20231116"
        c_code = req_category_code[1:]

        ret = TRShow.SetQueryName(TR_Name)
        ret = TRShow.SetSingleData(0, market_type)  # 시장구분
        ret = TRShow.SetSingleData(1, st_date)  # 기준일
        ret = TRShow.SetSingleData(2, end_date)  # 비교일
        ret = TRShow.SetSingleData(3, c_code)  # 업종코드

        # # TR 명
        # TR_Name = "upjong_code_mst"
        # category_code = req_category_code
        # # Input Field
        # ret = TRShow.SetQueryName(TR_Name)
        # ret = TRShow.SetSingleData(0, "0006")  # 업종코드 -> 고정해도 안됨

        # 보내기(리퀘스트)
        rqid = TRShow.RequestData()

        # Error
        err_code = print(TRShow.GetErrorCode())
        err_msg = print(TRShow.GetErrorMessage())

        print(type(rqid))
        print('Request Data rqid: ' + str(rqid))

        if str(rqid) == '0':
            return {"status": 502, "result": "전달 오류"}

        # ReceiveData 구분용
        self.rqidD[rqid] = TR_Name

        # Response 전달용
        result = await wait_data(rqid, self.callback_result)
        self.callback_result = {}

        # error handling
        if result == 0:
            return {"status": 500, "result": "error"}
        elif err_code == '0':
            return {"status": 500, "result": err_msg}
        else:
            return {"status": 200, "result": result}

    # 종목 현재가 조회
    async def stock_cur_price(self, req_stock_code):
        # TR 명
        TR_Name = "SC"

        # Input Field
        ret = TRShow.SetQueryName(TR_Name)
        ret = TRShow.SetSingleData(0, req_stock_code)  # 종목코드

        # 보내기(리퀘스트)
        rqid = TRShow.RequestData()

        # Error
        err_code = print(TRShow.GetErrorCode())
        err_msg = print(TRShow.GetErrorMessage())

        print(type(rqid))
        print('Request Data rqid: ' + str(rqid))

        if str(rqid) == '0':
            return {"status": 502, "result": "전달 오류"}

        # ReceiveData 구분용
        self.rqidD[rqid] = TR_Name

        # Response 전달용
        result = await wait_data(rqid, self.callback_result)
        self.callback_result = {}

        # error handling
        if result == 0:
            return {"status": 500, "result": "error"}
        elif err_code == '0':
            return {"status": 500, "result": err_msg}
        else:
            return {"status": 200, "result": result}

    # 종목 등락률, 시가총액 조회
    # TR : TR_1110_11
    async def stock_data(self, req_stock_code):
        # TR 명
        TR_Name = "TR_1110_11"

        # Input Field
        ret = TRShow.SetQueryName(TR_Name)
        ret = TRShow.SetSingleData(0, req_stock_code)  # 종목코드

        # 보내기(리퀘스트)
        rqid = TRShow.RequestData()

        # Error
        err_code = print(TRShow.GetErrorCode())
        err_msg = print(TRShow.GetErrorMessage())

        print(type(rqid))
        print('Request Data rqid: ' + str(rqid))

        if str(rqid) == '0':
            return {"status": 502, "result": "전달 오류"}

        # ReceiveData 구분용
        self.rqidD[rqid] = TR_Name

        # Response 전달용
        result = await wait_data(rqid, self.callback_result)
        self.callback_result = {}

        # error handling
        if result == 0:
            return {"status": 500, "result": "error"}
        elif err_code == '0':
            return {"status": 500, "result": err_msg}
        else:
            return {"status": 200, "result": result}

    # 종목 ohlc 데이터 조회
    # TR : TR_SCHART
    async def stock_ohlc(self, req_stock_code, req_start_date, req_end_date):
        # TR 명
        TR_Name = "TR_SCHART"

        # Input Field
        ret = TRShow.SetQueryName(TR_Name)
        ret = TRShow.SetSingleData(0, req_stock_code)  # 종목코드
        ret = TRShow.SetSingleData(1, 'D')  # 그래프 종류
        ret = TRShow.SetSingleData(2, '1')  # 시간간격
        ret = TRShow.SetSingleData(3, req_start_date)  # 시작일
        ret = TRShow.SetSingleData(4, req_end_date)  # 종료일
        ret = TRShow.SetSingleData(5, '1500')  # 조회갯수

        # 보내기(리퀘스트)
        rqid = TRShow.RequestData()

        # Error
        err_code = print(TRShow.GetErrorCode())
        err_msg = print(TRShow.GetErrorMessage())

        print(type(rqid))
        print('Request Data rqid: ' + str(rqid))

        if str(rqid) == '0':
            return {"status": 502, "result": "전달 오류"}

        # ReceiveData 구분용
        self.rqidD[rqid] = TR_Name

        # Response 전달용
        result = await wait_data(rqid, self.callback_result)
        self.callback_result = {}

        # error handling
        if result == 0:
            return {"status": 500, "result": "error"}
        elif err_code == '0':
            return {"status": 500, "result": err_msg}
        else:
            return {"status": 200, "result": result}

# -----------------------------------------------------------
# 뉴스 데이터

    # 뉴스 목록 조회
    # TR : TR_3100_D
    async def search_stock_news_list(self, req_stock_code, req_news_type, req_search_date):
        # TR 명
        TR_Name = "TR_3100_D"

        # Input Field
        ret = TRShow.SetQueryName(TR_Name)
        ret = TRShow.SetSingleData(0, req_stock_code)  # 종목코드
        ret = TRShow.SetSingleData(1, req_news_type)  # 구분
        ret = TRShow.SetSingleData(2, req_search_date)  # 조회일자

        # 보내기(리퀘스트)
        rqid = TRShow.RequestData()

        # Error
        err_code = print(TRShow.GetErrorCode())
        err_msg = print(TRShow.GetErrorMessage())

        print(type(rqid))
        print('Request Data rqid: ' + str(rqid))

        if str(rqid) == '0':
            return {"status": 502, "result": "전달 오류"}

        # ReceiveData 구분용
        self.rqidD[rqid] = TR_Name

        # Response 전달용
        result = await wait_data(rqid, self.callback_result)
        self.callback_result = {}

        # error handling
        if result == 0:
            return {"status": 500, "result": "error"}
        elif err_code == '0':
            return {"status": 500, "result": err_msg}
        else:
            return {"status": 200, "result": result}

    # 뉴스 내용 조회
    # TR : TR_3100
    async def search_stock_news_detail(self, req_news_type_code, req_search_date, req_news_code):
        # TR 명
        TR_Name = "TR_3100"

        # Input Field
        ret = TRShow.SetQueryName(TR_Name)
        ret = TRShow.SetSingleData(0, req_news_type_code)  # 뉴스 구분
        ret = TRShow.SetSingleData(1, req_search_date)  # 뉴스 일자
        ret = TRShow.SetSingleData(2, req_news_code)  # 뉴스 기사번호

        # 보내기(리퀘스트)
        rqid = TRShow.RequestData()

        # Error
        err_code = print(TRShow.GetErrorCode())
        err_msg = print(TRShow.GetErrorMessage())

        print(type(rqid))
        print('Request Data rqid: ' + str(rqid))

        if str(rqid) == '0':
            return {"status": 502, "result": "전달 오류"}

        # ReceiveData 구분용
        self.rqidD[rqid] = TR_Name

        # Response 전달용
        result = await wait_data(rqid, self.callback_result)
        self.callback_result = {}

        # error handling
        if result == 0:
            return {"status": 500, "result": "error"}
        elif err_code == '0':
            return {"status": 500, "result": err_msg}
        else:
            return {"status": 200, "result": result}


# -----------------------------------------------------------
    # TR data 처리
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
        # CASE 업종 종목 조회
        if TR_Name == "TR_1871_2":
            nCnt = giCtrl.GetMultiRowCount()
            print("c")
            print(nCnt)
            try:
                for i in range(0, nCnt):
                    tr_data_output.append({})
                    tr_data_output[i]["stbd_code"] = str(
                        giCtrl.GetMultiData(i, 0))
                    tr_data_output[i]["stbd_nm"] = str(
                        giCtrl.GetMultiData(i, 1)).strip()
                    print(TRShow.GetErrorCode())
                    print(TRShow.GetErrorMessage())
                    if len(tr_data_output) == 0:
                        raise ValueError("에러 발생 로그 확인")
                else:
                    # 반환 값 저장
                    self.callback_result[rqid] = tr_data_output
            except ValueError as e:
                self.callback_result[rqid] = 0

        # CASE 업종 종목 조회 - 현재 사용 X
        if TR_Name == "upjong_code_mst":
            nCnt = giCtrl.GetMultiRowCount()
            print("c")
            print(nCnt)
            try:
                for i in range(0, nCnt):
                    tr_data_output.append({})
                    tr_data_output[i]["stbd_code"] = str(
                        giCtrl.GetMultiData(i, 0))
                    tr_data_output[i]["stbd_nm"] = str(
                        giCtrl.GetMultiData(i, 1))
                    # tr_data_output.append([])
                    # tr_data_output[i].append(
                    #     (str(giCtrl.GetMultiData(i, 0))))  # 종목 코드
                    # tr_data_output[i].append(
                    #     (str(giCtrl.GetMultiData(i, 1))))  # 종목 이름
                print(TRShow.GetErrorCode())
                print(TRShow.GetErrorMessage())
                if len(tr_data_output) == 0:
                    raise ValueError("에러 발생 로그 확인")
                else:
                    # 반환 값 저장
                    self.callback_result[rqid] = tr_data_output
            except ValueError as e:
                self.callback_result[rqid] = 0
        
        # CASE 종목 정보 조회
        if TR_Name == "TR_1110_11":
            nCnt = giCtrl.GetMultiRowCount()
            print("c")
            print(nCnt)
            try:
                tr_data_output.append({})
                tr_data_output[0]["day_range"] = str(
                    giCtrl.GetSingleData(3))  # 등락률
                tr_data_output[0]["market_cap"] = str(
                    giCtrl.GetSingleData(15))  # 시가총액

                if len(tr_data_output) == 0:
                    raise ValueError("에러 발생 로그 확인")
                else:
                    self.callback_result[rqid] = tr_data_output
            except ValueError as e:
                self.callback_result[rqid] = 0

        # CASE 종목 현재가 조회
        if TR_Name == "SC":
            nCnt = giCtrl.GetMultiRowCount()
            print("c")
            print(nCnt)
            try:
                tr_data_output.append({})
                tr_data_output[0]["cur_price"] = str(giCtrl.GetSingleData(3))  # 현재가


                if len(tr_data_output) == 0:
                    raise ValueError("에러 발생 로그 확인")
                else:
                    self.callback_result[rqid] = tr_data_output
            except ValueError as e:
                self.callback_result[rqid] = 0

        #  CASE 종목 ohlc 조회
        if TR_Name == "TR_SCHART":
            nCnt = giCtrl.GetMultiRowCount()
            print("c")
            print(nCnt)
            try:
                for i in range(0, nCnt):
                    tr_data_output.append({})
                    tr_data_output[i]["date"] = str(giCtrl.GetMultiData(i, 0))
                    tr_data_output[i]["open"] = str(giCtrl.GetMultiData(i, 2))
                    tr_data_output[i]["high"] = str(giCtrl.GetMultiData(i, 3))
                    tr_data_output[i]["low"] = str(giCtrl.GetMultiData(i, 4))
                    tr_data_output[i]["close"] = str(giCtrl.GetMultiData(i, 5))

                print(TRShow.GetErrorCode())
                print(TRShow.GetErrorMessage())
                if len(tr_data_output) == 0:
                    raise ValueError("에러 발생 로그 확인")
                else:
                    # 반환 값 저장
                    self.callback_result[rqid] = tr_data_output
            except ValueError as e:
                self.callback_result[rqid] = 0

        # News
        # 종목 뉴스 목록 조회
        if TR_Name == "TR_3100_D":
            nCnt = giCtrl.GetMultiRowCount()
            print("c")
            print(nCnt)
            try:
                for i in range(0, nCnt):
                    tr_data_output.append({})
                    tr_data_output[i]['date'] = str(giCtrl.GetMultiData(i, 0))  # 뉴스 일자
                    tr_data_output[i]['news_code'] = str(giCtrl.GetMultiData(i, 4))  # 뉴스 기사번호
                    tr_data_output[i]['news_type'] = str(giCtrl.GetMultiData(i, 3))  # 뉴스 구분
                    tr_data_output[i]['news_title'] = str(giCtrl.GetMultiData(i, 2))  # 뉴스 제목
                
                print(TRShow.GetErrorCode())
                print(TRShow.GetErrorMessage())
                if len(tr_data_output) == 0:
                    raise ValueError("에러 발생 로그 확인")
                else:
                    # 반환 값 저장
                    self.callback_result[rqid] = tr_data_output
            except ValueError as e:
                self.callback_result[rqid] = 0

        # 뉴스 내용 조회
        if TR_Name == "TR_3100":
            nCnt = giCtrl.GetMultiRowCount()
            print("c")
            print(nCnt)
            news_article = """"""
            try:
                for i in range(0, nCnt):
                    # tr_data_output.append(str(giCtrl.GetMultiData(i, 4)))
                    # tr_data_output.append(str(giCtrl.GetMultiData(i, 5)))
                    # tr_data_output.append(str(giCtrl.GetMultiData(i, 6)))
                    news_article += str(giCtrl.GetMultiData(i, 4))
                    news_article += str(giCtrl.GetMultiData(i, 5))
                    news_article += str(giCtrl.GetMultiData(i, 6))
                    tr_data_output.append(news_article)

                print(TRShow.GetErrorCode())
                print(TRShow.GetErrorMessage())
                if len(tr_data_output) == 0:
                    raise ValueError("에러 발생 로그 확인")
                else:
                    # 반환 값 저장
                    self.callback_result[rqid] = tr_data_output
            except ValueError as e:
                self.callback_result[rqid] = 0
