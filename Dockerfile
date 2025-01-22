FROM python:3.13-slim

WORKDIR /src/app

ADD requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ADD golemgpt ./golemgpt

CMD ["python", "-m", "golemgpt"]
