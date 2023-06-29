import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from smm_successor.handlers import api_router

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(name)-15s %(message)s', level=logging.INFO)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, log_config=None)
