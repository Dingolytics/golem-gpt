FROM python:3.10.11-alpine3.17

WORKDIR /src/app

ADD requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ADD golemgpt ./golemgpt

CMD ["python", "-m", "golemgpt"]
