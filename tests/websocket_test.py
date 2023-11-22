import threading
import asyncio
import websockets
import sys

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *

import GiExpertControl as RT
import GiExpertControl as giLogin
from dotenv import load_dotenv
import os

# 종목 데이터를 저장하는 데이터 딕셔너리
stock_data = {
    # 종목들 추가
}

# load .env
load_dotenv()

INDI_ID = os.environ.get('INDI_ID')
INDI_PW = os.environ.get('INDI_PW')

nCount = 0
class indiApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # qt모드 세팅
        RT.SetQtMode(True)
        # IndiPython 실행
        RT.RunIndiPython()
        giLogin.RunIndiPython()

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

        # 실시간 응답 처리
        RT.SetCallBack('ReceiveRTData', self.RT_ReceiveData)
    
    # 실시간 현재가 조회 버튼
    def request_rt(self, stock_code):
        stbd_code = stock_code

        rqid = RT.RequestRTReg("SC",stbd_code) # 실시간 현재가
        print(type(rqid))
        print('Request Data rqid: ' + str(rqid))
    
    # 실시간 현재가 조회 중지 버튼
    def req_rt_stop(self, stock_code):
        stbd_code = stock_code
        ret = RT.UnRequestRTReg("SC",stbd_code)
        print(ret)

    def RT_ReceiveData(self, giCtrl, RealType):
        if RealType == "SC":
            stock_code = str(giCtrl.GetSingleData(1)) # 종목 코드
            stock_price = str(giCtrl.GetSingleData(3)) # 현재가
            print("error code : ", giCtrl.GetErrorCode())
            print("error msg : ", giCtrl.GetErrorMessage())
            stock_data[stock_code] = {"price" : stock_price}
            print(stock_data[stock_code])
            
            
async def handle_client(websocket, path):
    try:
        async for message in websocket:
            # 클라이언트로부터 받은 종목 명에 해당하는 데이터 전송
            stock_code = message.strip()
            indi_app_instance.request_rt(stock_code)
            while True:
                if stock_code in stock_data.keys():
                    stock_price = stock_data[stock_code]["price"]
                    await websocket.send(f"{stock_code} : {stock_price}")
                else:
                    await websocket.send("로딩중")
                await asyncio.sleep(1)
    except websockets.exceptions.ConnectionClosedOK:
        print(f"Client {websocket.remote_address} disconnected.")
        indi_app_instance.req_rt_stop(stock_code)

    finally:
        # 연결이 끊어지면 호출할 함수 작성
        indi_app_instance.req_rt_stop(stock_code)

def run_indi_app():
    global indi_app_instance
    app = QApplication(sys.argv)
    indi_app_instance = indiApp()
    sys.exit(app.exec_())

def run_websocket_server():
    print("run websocket server")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    start_server = websockets.serve(handle_client, "0.0.0.0", 8765)
    loop.run_until_complete(start_server)
    loop.run_forever()


if __name__ == "__main__":
    indi_thread = threading.Thread(target=run_indi_app)
    indi_thread.start()

    websocket_server = threading.Thread(target=run_websocket_server)
    websocket_server.start()


