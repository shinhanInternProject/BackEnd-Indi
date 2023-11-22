import threading
from api import server

# indi 실행
def run_app():
    server.run_indi_app()
    pass

# api server 실행
def run_server():
    server.run_fastapi_server()
    pass

# main
if __name__ == "__main__":
    indi_thread = threading.Thread(target=run_app)
    indi_thread.start()

    server_thread = threading.Thread(target=run_server)
    server_thread.start()
