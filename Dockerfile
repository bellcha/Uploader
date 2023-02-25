FROM python:3.10.6
COPY . /app
WORKDIR /app
RUN mkdir -p /app/static/files
RUN ["apt-get", "update"]
RUN ["apt-get", "-y", "install", "vim"]
RUN pip install -r requirements.txt
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]