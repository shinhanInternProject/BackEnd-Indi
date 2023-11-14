import sys
from tkinter import messagebox as msg
import pandas as pd
import numpy as np
import GiExpertControl as gi
import GiExpertControl as giRQ
import GiExpertControl as giRT

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
        gi.StartIndi('', '', '', 'C:\\SHINHAN-i\\indi\\GiExpertStarter.exe')
        print(gi.GetErrorCode())
        print(gi.GetErrorMessage())

        gi.SetCallBack('ReceiveData', self.ReceiveData)
        gi.SetCallBack('ReceiveRTData', self.ReceiveRTData)
        gi.SetCallBack('ReceiveSysMsg', self.ReceiveSysMsg)
        gi.SetCallBack('TimerEvent', self.TimerEvent)
        gi.SetCallBack('StartIndiPython', self.StartIndiPython)

        self.rqidD = {}
        PriceInfodt = np.dtype([('Symbol', 'S10'), ('Name', 'S40'), ('Close', 'f'), ('Open', 'f'), ('High', 'f'), ('Low', 'f'),
                       ('UpLimit', 'f'), ('DownLimit', 'f'), ('PrevClose', 'f'), ('Ask1', 'f'), ('Bid1', 'f'),
                       ('Time', 'S6'), ('Vol', 'u4'), ('ContQty', 'u4'), ('Ask1Qty', 'u4'), ('Bid1Qty', 'u4')])
        self.PriceInfo = np.empty([1], dtype=PriceInfodt)

        Historicaldt = np.dtype([('Date', 'S8'), ('Time', 'S6'), ('Open', 'f'), ('High', 'f'), ('Low', 'f'), ('Close', 'f'), ('Vol', 'u4')])
        self.Historical = np.empty([10], dtype=Historicaldt)

        self.MainSymbol = ""

    def ResetPriceInfo(self):
        self.PriceInfo[0]['Symbol']     = ""
        self.PriceInfo[0]['Time']       = "00:00"
        self.PriceInfo[0]['Close']      = 0
        self.PriceInfo[0]['Vol']        = 0
        self.PriceInfo[0]['ContQty']    = 0
        self.PriceInfo[0]['Open']       = 0
        self.PriceInfo[0]['High']       = 0
        self.PriceInfo[0]['Low']        = 0
        self.PriceInfo[0]['Ask1']       = 0
        self.PriceInfo[0]['Bid1']       = 0
        self.PriceInfo[0]['Ask1Qty']    = 0
        self.PriceInfo[0]['Bid1Qty']    = 0
        self.PriceInfo[0]['PrevClose']  = 0
        self.PriceInfo[0]['UpLimit']    = 0
        self.PriceInfo[0]['DownLimit']  = 0

    def doSearch(self, symbol):
        self.ResetPriceInfo()

        Symbol = symbol

        # 기존종목 실시간 해제
        if self.MainSymbol != "":
            gi.UnRequestRTReg("SB", self.MainSymbol)
            gi.UnRequestRTReg("SC", self.MainSymbol)
            gi.UnRequestRTReg("SH", self.MainSymbol)

        self.MainSymbol = Symbol

        # 차트조회
        ret = gi.SetQueryName("TR_SCHART")
        ret = gi.SetSingleData(0, self.MainSymbol)
        ret = gi.SetSingleData(1, "D")
        ret = gi.SetSingleData(2, "1")
        ret = gi.SetSingleData(3, "00000000")
        ret = gi.SetSingleData(4, "99999999")
        ret = gi.SetSingleData(5, "100")
        rqid = gi.RequestData()

        self.rqidD[rqid] =  "TR_SCHART"
        print('rqid1: {}\n'.format(rqid))
        # 종목 기본정보 조회
        ret = gi.SetQueryName("SB")
        ret = gi.SetSingleData(0, self.MainSymbol)
        rqid = gi.RequestData()
        print('rqid2: {}\n'.format(rqid))

        self.rqidD[rqid] = "SB"

        # 종목 현재가 조회
        ret  = gi.SetQueryName("SC")
        ret  = gi.SetSingleData(0, self.MainSymbol)
        rqid = gi.RequestData()
        print('rqid3: {}\n'.format(rqid))

        self.rqidD[rqid] = "SC"

        # 종목 호가 조회
        ret  = gi.SetQueryName("SH")
        ret  = gi.SetSingleData(0, self.MainSymbol)
        rqid = gi.RequestData()
        print('rqid4: {}\n'.format(rqid))

        self.rqidD[rqid] = "SH"
    
    def CheckData(self, val, init):
        if val == "":
            return init
        return val

    def ReceiveData(self, giCtrl, rqid):
        print('recv rqid: {}->{}\n'.format( rqid, self.rqidD[rqid]));
        TRName = self.rqidD[rqid]
        if TRName == "TR_SCHART" :
            nCnt = giCtrl.GetMultiRowCount()
            print('recv nCnt: {}\n'.format( nCnt));
            if nCnt > 10:
                nCnt = 10
            np.reshape(self.Historical, nCnt)
            for i in range(0, nCnt):
                self.Historical[i]['Date']  = giCtrl.GetMultiData(i, 0)
                self.Historical[i]['Time']  = giCtrl.GetMultiData(i, 1)
                self.Historical[i]['Open']  = giCtrl.GetMultiData(i, 2)
                self.Historical[i]['High']  = giCtrl.GetMultiData(i, 3)
                self.Historical[i]['Low']   = giCtrl.GetMultiData(i, 4)
                self.Historical[i]['Close'] = giCtrl.GetMultiData(i, 5)
                self.Historical[i]['Vol']   = giCtrl.GetMultiData(i, 9)
        
            print(self.Historical)
        
        elif TRName == "SB":
            self.PriceInfo[0]['Name']       = self.CheckData(giCtrl.GetSingleData(6) , "")
            self.PriceInfo[0]['PrevClose']  = self.CheckData(giCtrl.GetSingleData(23), 0)
            self.PriceInfo[0]['UpLimit']    = self.CheckData(giCtrl.GetSingleData(27), 0)
            self.PriceInfo[0]['DownLimit']  = self.CheckData(giCtrl.GetSingleData(28), 0)
        
            print(self.PriceInfo)
            # 실시간 등록
            ret = giCtrl.RequestRTReg("SB", self.MainSymbol)
        
        elif TRName == "SC":
            self.PriceInfo[0]['Symbol']     = self.CheckData(giCtrl.GetSingleData(1), "")
            self.PriceInfo[0]['Time']       = self.CheckData(giCtrl.GetSingleData(2) , 0)
            self.PriceInfo[0]['Close']      = self.CheckData(giCtrl.GetSingleData(3) , 0)
            self.PriceInfo[0]['Vol']        = self.CheckData(giCtrl.GetSingleData(7) , 0)
            self.PriceInfo[0]['ContQty']    = self.CheckData(giCtrl.GetSingleData(9) , 0)
            self.PriceInfo[0]['Open']       = self.CheckData(giCtrl.GetSingleData(10), 0)
            self.PriceInfo[0]['High']       = self.CheckData(giCtrl.GetSingleData(11), 0)
            self.PriceInfo[0]['Low']        = self.CheckData(giCtrl.GetSingleData(12), 0)
        
            print(self.PriceInfo)
            # 실시간 등록
            ret = giCtrl.RequestRTReg("SC", self.MainSymbol)
        elif TRName == "SH":
            self.PriceInfo[0]['Ask1']       = self.CheckData(giCtrl.GetSingleData(4), 0)
            self.PriceInfo[0]['Bid1']       = self.CheckData(giCtrl.GetSingleData(5), 0)
            self.PriceInfo[0]['Ask1Qty']    = self.CheckData(giCtrl.GetSingleData(6), 0)
            self.PriceInfo[0]['Bid1Qty']    = self.CheckData(giCtrl.GetSingleData(7), 0)
        
            print(self.PriceInfo)
            # 실시간 등록
            ret = giCtrl.RequestRTReg("SH", self.MainSymbol)
        
        self.rqidD.__delitem__(rqid)
        
        
    def ReceiveRTData(self, giCtrl, RealType):
        if RealType == "SC":
            self.PriceInfo[0]['Symbol']     = giCtrl.GetSingleData(1)
            self.PriceInfo[0]['Time']       = giCtrl.GetSingleData(2)
            self.PriceInfo[0]['Close']      = giCtrl.GetSingleData(3)
            self.PriceInfo[0]['Vol']        = giCtrl.GetSingleData(7)
            self.PriceInfo[0]['ContQty']    = giCtrl.GetSingleData(9)
            self.PriceInfo[0]['Open']       = giCtrl.GetSingleData(10)
            self.PriceInfo[0]['High']       = giCtrl.GetSingleData(11)
            self.PriceInfo[0]['Low']        = giCtrl.GetSingleData(12)

        elif RealType == "SB":
            self.PriceInfo[0]['Name']       = giCtrl.GetSingleData(5)
            self.PriceInfo[0]['PrevClose']  = giCtrl.GetSingleData(23)
            self.PriceInfo[0]['UpLimit']    = giCtrl.GetSingleData(27)
            self.PriceInfo[0]['DownLimit']  = giCtrl.GetSingleData(28)
        elif RealType == "SH":
            self.PriceInfo[0]['Ask1']       = giCtrl.GetSingleData(4)
            self.PriceInfo[0]['Bid1']       = giCtrl.GetSingleData(5)
            self.PriceInfo[0]['Ask1Qty']    = giCtrl.GetSingleData(6)
            self.PriceInfo[0]['Bid1Qty']    = giCtrl.GetSingleData(7)

        print("RealType: {} ".format(RealType))
        print(self.PriceInfo[0])

    def ReceiveSysMsg(self, giCtrl, MsgID):
        print("System Message Received = ", MsgID)
        
        
    def StartIndiPython(self, giCtrl):
        id = gi.SetTimer(10, 5000)
        
    def TimerEvent(self, giCtrl, iTimerId):
        global nCount
        print('TimerEvent iTimerId: {}'.format( iTimerId))
        self.doSearch("005930")
        nCount = nCount+1
        if  nCount >= 3 :
            gi.KillTimer(iTimerId)
            gi.CloseIndi()
            gi.QuitIndiPython()
        else:
            print("Timer Count: {}".format(nCount))
            
if __name__ == "__main__":
    IndiWindow = IndiWindow()
    gi.SetQtMode(False)
    gi.RunIndiPython()


    # 기존종목 실시간 해제
    if IndiWindow.MainSymbol != "":
        gi.UnRequestRTReg("SB", IndiWindow.MainSymbol)
        gi.UnRequestRTReg("SC", IndiWindow.MainSymbol)
        gi.UnRequestRTReg("SH", IndiWindow.MainSymbol)
