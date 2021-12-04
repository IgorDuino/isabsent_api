FROM python:3.9

COPY ./req.txt .
RUN pip3 install -r req.txt

RUN python3 -m pip install --upgrade pip

COPY . . 

CMD ["python3", "main.py"]