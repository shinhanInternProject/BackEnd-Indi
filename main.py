from fastapi import FastAPI
from tests import indi_core

app = FastAPI()

indi_app = indi_core.indi()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/indi/stock/news")
async def news_list():
    print("call news list")
    indi_app.search_stock_news()
    print("called news list")
    
    return {"message": "success"}