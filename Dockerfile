# Docker file
FROM python:3.14-alpine
WORKDIR /Backend
ENV DJANGO_APP=
RUN
COPY requirements.txt
RUN pip install requirements.txt
EXPOSE 5173
CMD []
