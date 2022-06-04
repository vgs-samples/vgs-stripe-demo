FROM python:3.11.0b1
ADD . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 3000/tcp
CMD ["python", "src/server.py"]
