FROM python:3.9-buster 


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ARG MLG_VER


RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install mlgame==$MLG_VER 
COPY requirements.txt /tmp/ 
COPY requirements-ml.txt /tmp/ 
RUN pip install -r /tmp/requirements-ml.txt
RUN pip install -r /tmp/requirements.txt

CMD ["/bin/bash"]
