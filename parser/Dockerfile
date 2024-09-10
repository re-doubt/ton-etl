FROM python:3.9

COPY requirements.txt /opt/app/
RUN pip3 install -r /opt/app/requirements.txt

COPY model /opt/app/model
COPY parsers /opt/app/parsers
COPY db.py /opt/app/
COPY main.py /opt/app/


WORKDIR /opt/app/
CMD ["python", "main.py"]