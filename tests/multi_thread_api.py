from fastapi import FastAPI
import threading
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
import indi_core

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

@app.get("/news")
async def news_list():
    print("call news list")
    result = await indi_app_instance.search_stock_news()
    print(result)
    print("called news list")
    
    return {"message": result}

@app.get("/info")
async def info():
    print("call info")
    result = await indi_app_instance.pushButton_search_stock_info()
    print(result)
    print("called info")
    
    return {"message": result}

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