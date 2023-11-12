from fastapi import FastAPI
from tests import indi_core

app = FastAPI()

indi_app = indi_core.indi()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/indi/stock/news")
async def news_list():
    result_data = indi_app.search_stock_news()
    print(result_data)
    
    return {"message": "success"}