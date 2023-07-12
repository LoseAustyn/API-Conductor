FROM python:3.11-slim

WORKDIR /python/src
ADD . /python/src
RUN chmod +x /python/src/main.py

# replace apt source && config pip source
RUN echo "deb http://mirrors.aliyun.com/debian $(cat /etc/os-release | grep -Po "(?<=VERSION_CODENAME=)(.+)") main" > /etc/apt/sources.list && \
  echo "deb http://mirrors.aliyun.com/debian-security $(cat /etc/os-release | grep -Po "(?<=VERSION_CODENAME=)(.+)")-security main" >> /etc/apt/sources.list && \
  apt-get update && apt-get install -y vim && apt-get clean && \
  pip config set global.index-url https://mirrors.aliyun.com/pypi/simple && \
  /bin/echo -e [easy_install]\\nindex-url=https://mirrors.aliyun.com/pypi/simple > ~/.pydistutils.cfg

# Install pip dependencies
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

ENTRYPOINT ["/python/src/main.py"]