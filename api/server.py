from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from common import indi_core

# server app
app = FastAPI()

# 허용할 origin
origin = ["*"]

# middleware 등록
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# indi instance
indi_app_instance = None

# -----------------------------------------------------------

def run_indi_app():
    global indi_app_instance

    app = QApplication(sys.argv)
    indi_app_instance = indi_core.indiApp()
    sys.exit(app.exec_())


def run_fastapi_server():
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)


# default - test
@app.get("/")
async def root():
    return {"message": "healthy"}


# -----------------------------------------------------------
# stock Router
router_stock = APIRouter()

# 업종 관련 종목 조회 
@router_stock.get("/category/{category_code}")
async def stock_list(category_code: str):
    print("get - stock list")
    print(category_code, type(category_code))
    result = await indi_app_instance.category_stock_list(category_code)
    print("get - stock list done")
    
    return {"status": result["status"], "result": result["result"]}

# 종목 등락률, 시총 조회
@router_stock.get("/info/{stock_code}")
async def stock_info(stock_code: str):
    print("get - stock data")
    result = await indi_app_instance.stock_data(stock_code)
    print("get - stock info done")
    
    return {"status" : result["status"], "result" : result["result"]}

# 종목 현재가 조회
@router_stock.get("/curprice/{stock_code}")
async def stock_curprice(stock_code: str):
    print("get - stock cur price")
    result = await indi_app_instance.stock_cur_price(stock_code)
    print("get - stock cur price done")

    return {"status" : result["status"], "result" : result["result"]}

# 종목 ohlc 데이터 조회
# body
# st_date(str) - 조회 시작 날짜, end_date(str) - 조회 종료 날짜
@router_stock.post("/ohlc/{stock_code}")
async def stock_ohlc(stock_code: str, body: dict):
    print("post - stock ohlc")
    result = await indi_app_instance.stock_ohlc(stock_code, body["st_date"], body["end_date"])
    print("post - stock ohlc done")
    
    return {"status" : result["status"], "result" : result["result"]}



# -----------------------------------------------------------
# news Router
router_news = APIRouter()

# 종목 관련 뉴스 제목 리스트 조회
# body
# news_type(str) - 뉴스 타입, search_date(str) - 조회 날짜
@router_news.post("/{stock_code}")
async def news_list(stock_code: str, body: dict):
    print("post - news list")
    result = await indi_app_instance.search_stock_news_list(stock_code, body["news_type"], body["search_date"])
    print("post - news list done")

    return {"status": result["status"], "result": result["result"]}

# 뉴스 세부 내용 조회
# news_code - 뉴스 리스트 조회를 통해 받은 뉴스 코드
# body
# news_type_code(str) - 뉴스 리스트 조회를 통해 받은 뉴스 타입
# search_date(str) - 해당 뉴스 날짜
@router_news.post("/detail/{news_code}")
async def news_detail(news_code: str, body: dict):
    print("post - news detail")
    result = await indi_app_instance.search_stock_news_detail(body["news_type_code"], body["search_date"], news_code)
    print("post - news detail done")

    return {"message" : result}
    


# -----------------------------------------------------------
app.include_router(router_stock, prefix="/stock", tags=["stock"])
app.include_router(router_news, prefix="/news", tags=["news"])
