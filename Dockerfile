FROM python:3.9.7
WORKDIR /web/mynote_api

COPY requirements.txt ./
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . ./

CMD ["gunicorn", "note:app", "-c", "./gunicorn.conf.py"]

# sudo docker build -t "mynote-api" .
# sudo docker run -d -p 5001:5001 --name mynote-api mynote-api