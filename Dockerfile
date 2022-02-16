FROM python:3
RUN apt-get update
# Set the home directory to /root
ENV HOME /root
# cd into the home directory
WORKDIR /root
COPY . .
EXPOSE 80:80

