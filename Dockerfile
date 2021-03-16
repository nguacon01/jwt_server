# download main image from docker hub
FROM python:3

#create work directoy which contains app
WORKDIR /jwt_server

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

#bundle app source then copy the current folder into work directory folder in container
COPY . .

#port of container by default
EXPOSE 5000

# #run app in container
# CMD [ "python","wsgi.py" ]

# The code to run when container is started:
# COPY run.py .
ENTRYPOINT ["sh", "entrypoint.sh"]
