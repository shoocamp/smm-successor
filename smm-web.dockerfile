FROM python:3.10

RUN mkdir "/app"
WORKDIR "/app"

COPY . .

RUN python3.10 -m pip install -r requirements.txt

CMD uvicorn --host 0.0.0.0 smm_successor.server:app
