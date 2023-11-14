from fastapi import FastAPI
import threading
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
import pandas as pd
from dotenv import load_dotenv
import os
import indi_core
import time

# load .env
load_dotenv()

INDI_ID = os.environ.get('INDI_ID')
INDI_PW = os.environ.get('INDI_PW')

app = FastAPI()

indi_app_instance = None
            
def run_indi_app():
    global indi_app_instance

    app = QApplication(sys.argv)
    indi_app_instance = indi_core.indiApp()
    sys.exit(app.exec_())

def run_fastapi_server():
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/indi/stock/news")
async def news_list():
    print("call news list")
    indi_app_instance.search_stock_news()
    print("called news list")
    
    return {"message": "success get stock news"}

@app.get("/indi/stock/info")
async def info():
    print("call info")
    indi_app_instance.pushButton_search_stock_info()
    print("called info")
    
    return {"message": "success get stock info"}

@app.get("/realtime")
async def rt():
    print("call rt")
    indi_app_instance.request_rt()
    return {"messge": "succcess get rt data"}

@app.get("/realtime/stop")
async def st_rt():
    print("call rt stop")
    indi_app_instance.req_rt_stop()
    return {"message": "success stop rt data"}

if __name__ == "__main__":
    indi_thread = threading.Thread(target=run_indi_app)
    indi_thread.start()

    server_thread = threading.Thread(target=run_fastapi_server)
    server_thread.start()