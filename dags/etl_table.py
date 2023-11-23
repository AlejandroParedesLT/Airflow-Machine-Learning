from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
import traceback

from airflow.models.connection import Connection
from airflow.models import Variable
from airflow import DAG
from airflow.decorators import task
from airflow.utils.task_group import TaskGroup

from airflow.operators.python import PythonOperator
from airflow.hooks.base_hook import BaseHook
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.sensors.http import HttpSensor

import requests
from airflow import DAG
from airflow.decorators import task
from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook
#from airflow.providers.oracle.hooks.oracle import OracleHook

default_args = {
    'owner' : 'alejandro',
    'retries' : 5,
    'retry_delay' : timedelta(minutes=2)
}

@task
def task_1():    
    mssql_hook = MsSqlHook("example_db")
    try:
        #conn = mssql_hook.get_conn()
        #cursor = conn.cursor()
        print('Inicio Importación')
        target_fields = [
        'id'
        ,'date_ini'
        ,'date_end'
        ,'concept'
        ]
        records = mssql_hook.get_records(f"select {', '.join(target_fields)} from dbo.example_table where date_ini = '20230822' ")
        #df = hook.get_pandas_df(sql='')
        mssql_hook.insert_rows('temp.example_table', records, target_fields)
        #cursor.close()
        #conn.close()
    except Exception as e:
        #cursor.close()
        #conn.close()
        traceback.print_exc()
        print("There is a problem with SQL Server:", e)
    else:
        print(f'Sucess Importing Data')
        

with DAG(
    dag_id='etl_table',
    description = 'etl_table',
    start_date = datetime(2023, 6, 21, 8),
    #schedule_interval = '@daily',
    schedule_interval = '30 11 * * *',
    catchup = False
    ) as dag :

    get_data = task_1()
    
    get_data 