FROM python:3.6-alpine

RUN adduser -D biobank

WORKDIR /home/biobank

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY run.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP run.py

RUN chown -R biobank:biobank ./
USER biobank

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
