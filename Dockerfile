# For more information, please refer to https://aka.ms/vscode-docker-python
FROM apache/airflow:2.7.1-python3.9

# Install pip requirements
COPY requirements.txt .
RUN pip install --user --upgrade pip
RUN pip install --no-cache-dir --user -r ./requirements.txt
RUN pip install pymssql
RUN pip install pyodbc
RUN pip install apache-airflow-providers-odbc
RUN pip install apache-airflow-providers-microsoft-azure==1.2.0rc1
RUN pip install apache-airflow-providers-microsoft-mssql
RUN pip install apache-airflow-providers-http
RUN pip install apache-airflow-providers-oracle[common.sql]
RUN pip install cx_Oracle
#RUN pip install transformers
#RUN pip install torch torchvision torchaudio

WORKDIR /app
COPY . /app

USER root
RUN chmod 777 /app/*
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
RUN mkdir -p /home/airflow/.cache/huggingface/hub/models--distilbert--distilbert-base-spanish-uncased && chown -R appuser:appuser /home/airflow/.cache/huggingface/hub/models--distilbert--distilbert-base-spanish-uncased
USER appuser
ENV SHELL /bin/bash

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "-k"]


