FROM python:3-alpine

RUN apk add postgresql-dev musl libffi-dev musl-dev gcc

COPY start.sh /start.sh

RUN pip install sandman2 psycopg2 pymysql

EXPOSE 5000

CMD ["/start.sh"]
