import sys
from tkinter import messagebox as msg
import pandas as pd
import numpy as np
import GiExpertControl as gi
import GiExpertControl as giRQ
import GiExpertControl as giRT
from dotenv import load_dotenv
import os
import time


# load .env
load_dotenv()

INDI_ID = os.environ.get('INDI_ID')
INDI_PW = os.environ.get('INDI_PW')
'''
    신한아이 인디 국내주식 예제입니다:
    코드를 입력하시고 Search 버튼을 누르시면
    종목코드에 해당하는 일별 차트 데이터 100개와
    종목 가격정보를 조회하여 출력합니다.
'''
nCount = 0
    
class IndiWindow():
    def __init__(self):
        super().__init__()

        print('gi = {}, RQ = {}, RT = {}'.format(gi.GetSlotId(), giRQ.GetSlotId(), giRT.GetSlotId()))
        gi.StartIndi(INDI_ID, INDI_PW, '', 'C:\\SHINHAN-i\\indi\\GiExpertStarter.exe')
        print(gi.GetErrorCode())
        print(gi.GetErrorMessage())

        self.rqidD = {}
        self.request_rt()
        
        gi.SetCallBack('ReceiveRTData', self.ReceiveRTData)

    def request_rt(self):
        stbd_code = '005930'

        rqid = gi.RequestRTReg("SC",stbd_code) # 실시간 현재가
        print(type(rqid))
        print('Request Data rqid: ' + str(rqid))
             
    # 실시간 현재가 조회 중지 버튼
    def req_rt_stop(self):
        stbd_code = '005930'
        ret = gi.UnRequestRTReg("SC",stbd_code)
        print(ret)

    def ReceiveRTData(self, giCtrl, RealType):
        if RealType == "SC":
            print(str(giCtrl.GetSingleData(3))) # 현재가
            print(giCtrl.GetErrorCode())
            print(giCtrl.GetErrorMessage())

            
if __name__ == "__main__":
    IndiWindow = IndiWindow()
    gi.SetQtMode(False)
    gi.RunIndiPython()


