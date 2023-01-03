FROM python:3

ENV LISTEN_PORT=5000
EXPOSE 5000

ADD . /

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD [ "python", "./mainapp.py" ]

