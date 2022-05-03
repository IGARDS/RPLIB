# front end build environment
FROM python:3 as RPLib

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr 
ENV PYTHONUNBUFFERED=1

WORKDIR /app/site

RUN apt-get update
RUN apt-get install -y libgraphviz-dev

COPY requirements.txt /app/

# install pip requirements
RUN pip install --upgrade pip
RUN python -m pip install -r /app/requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/app"

ENV RPLIB_DATA_PREFIX "/app/data"

# application entry point
CMD [ "/app/site/run.sh", "7001"] 
#CMD [ "/usr/local/bin/pip", "freeze" ] 
