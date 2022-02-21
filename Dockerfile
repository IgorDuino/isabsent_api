FROM python:3.10

COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN python3 -m pip install --upgrade pip

COPY . . 

CMD ["python3", "main.py"]