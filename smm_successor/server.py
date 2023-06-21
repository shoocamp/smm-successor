import logging

from fastapi import FastAPI
from handlers import api_router

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(name)-15s %(message)s', level=logging.INFO)

app = FastAPI()

app.include_router(api_router)

'''
закомментировал чтобы запускать сервер в режиме --reload из терминала (uvicorn server:app --reload)
не понял как сделать это в коде
'''
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000, log_config=None)

