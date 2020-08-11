FROM python:3.7.6
RUN mkdir /app
WORKDIR /app 
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
ENV dash_debug="True"
ENV dash_host="0.0.0.0"
ENV dash_port=8051
EXPOSE 8051
CMD ["python", "app.py"]

