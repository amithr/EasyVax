FROM ubuntu
  
COPY ./ /EasyVax
WORKDIR /EasyVax
# copy over our requirements.txt file
COPY requirements.txt /tmp/
# upgrade pip and install required python packages
RUN apt update
RUN apt-get install python3-pip -y
RUN pip install -U pip
RUN pip install gunicorn
RUN pip install --upgrade setuptools
RUN pip install -r /tmp/requirements.txt
ENV FLASK_ENV production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "run:app"]