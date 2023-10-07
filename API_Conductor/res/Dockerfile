FROM python:3.11-slim

WORKDIR /python/src
ADD . /python/src
RUN chmod +x /python/src/main.py

# replace apt source && config pip source
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple && \
  /bin/echo -e [easy_install]\\nindex-url=https://mirrors.aliyun.com/pypi/simple > ~/.pydistutils.cfg

# Install pip dependencies
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

ENTRYPOINT ["/python/src/main.py"]