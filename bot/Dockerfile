FROM --platform=linux/x86-64 public.ecr.aws/amazonlinux/amazonlinux:latest

RUN yum update -y
RUN yum install -y httpd
RUN yum install -y python3.11
RUN yum install -y python3.11-pip

WORKDIR /app

COPY ./src /app
COPY requirements.txt /app
RUN pip3.11 install -r requirements.txt

ENTRYPOINT [ "python3.11", "bot.py" ]