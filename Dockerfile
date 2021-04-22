FROM python:3.9

WORKDIR /usr/src/app

RUN pip install --upgrade pip
COPY . /usr/src/app/
RUN pip install -r requirements.txt

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
