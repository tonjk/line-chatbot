FROM python:3.11.5-slim

WORKDIR /usr/src/app

COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

ENV NAME venv

CMD [ "python", "main.py" ]