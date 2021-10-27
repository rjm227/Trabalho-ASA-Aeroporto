FROM ubuntu:latest

RUN apt-get update\ 
    && apt-get install -y python3-pip \
    && pip3 install --upgrade pip\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip3 --no-cache-dir install -r requirements.txt

EXPOSE 5000

CMD ["python3", "app.py"]