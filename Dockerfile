FROM python:3.6

ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir /app
WORKDIR /app
ADD . /app/

RUN pip install --no-cache-dir -r requirements.txt

CMD python run.py

EXPOSE 5000
