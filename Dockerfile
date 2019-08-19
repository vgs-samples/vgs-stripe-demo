FROM python:3.7.3
ADD . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 3000/tcp
CMD ["python", "src/server.py"]
