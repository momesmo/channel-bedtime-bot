FROM --platform=linux/x86-64 public.ecr.aws/amazonlinux/amazonlinux:latest

RUN yum update -y && \
    yum install -y httpd

# https://docs.aws.amazon.com/dms/latest/sbs/chap-mongodb2documentdb.02.html
    # https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-amazon/
COPY docker/setup_files/mongodb.repo /etc/yum.repos.d/mongodb-org-7.0.repo

RUN yum install -y mongodb-org

# TODO: add script to setup db

# RUN systemctl start mongod

# RUN sudo amazon-linux-extras install -y python3

COPY src /app

WORKDIR /app

# RUN pip3 install -r requirements.txt

EXPOSE 27017

# ENTRYPOINT ["python", "bot.py"]


### docker-compose example ###
# https://github.com/compwright/amazonlinux-2023-systemd/tree/master
#  TODO: figure out how to manange file location discrepancies with docker-compose
RUN dnf install -y systemd kernel-libbpf
CMD ["/usr/sbin/init"]

### TESTING ###
# COPY docker/setup_files/start-systemd.sh /usr/sbin/start-systemd.sh
# CMD ["/usr/sbin/start-systemd.sh"]
