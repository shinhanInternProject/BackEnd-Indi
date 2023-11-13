from fastapi import FastAPI
import multi_thread_indi
import threading

app = FastAPI()

# indi_app = multi_thread_indi.indi()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/indi/stock/news")
async def news_list():
    print("call news list")
    indi_app.search_stock_news()
    print("called news list")
    
    return {"message": "success"}

def run_server():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    server_thread.start()