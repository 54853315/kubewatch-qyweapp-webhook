FROM python:3-alpine
COPY . /
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
CMD python3 main.py
