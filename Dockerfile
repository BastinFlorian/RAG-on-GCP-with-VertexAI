FROM python:3.10

WORKDIR /src

ENV PYTHONUNBUFFERED True

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade -r /requirements.txt

ENV PORT 8080

EXPOSE ${PORT}

COPY ./src/chatbot ./chatbot

ENTRYPOINT streamlit run --server.port ${PORT} chatbot/app.py –-server.address=0.0.0.0 --server.enableCORS=false --server.enableWebsocketCompression=false --server.headless=true

