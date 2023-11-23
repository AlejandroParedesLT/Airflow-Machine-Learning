from airflow.models.connection import Connection
from airflow.models import Variable
from airflow import DAG
from airflow.decorators import task
from airflow.utils.task_group import TaskGroup

from airflow.operators.python import PythonOperator
from airflow.hooks.base_hook import BaseHook
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.sensors.http import HttpSensor

import json

from datetime import date, datetime, timedelta

@task(task_id="extract")
def extract():
    data_string = '{"1001": 301.27, "1002": 433.21, "1003": 502.22}'
    return json.loads(data_string)


@task(task_id="transform")
def transform(order_data):
    print(type(order_data))
    for value in order_data.values():
        total_order_value += value
    return {"total_order_value": total_order_value}


with DAG(
    dag_id='etl_xcoms',
    description = 'etl_xcoms',
    start_date = datetime(2023, 6, 21, 8),
    #schedule_interval = '@daily',
    schedule_interval = '30 11 * * *',
    catchup = False
    ) as dag :

    extract_task = extract()

    transform_task = PythonOperator(
        task_id="transform",
        op_kwargs={"order_data": "{{ti.xcom_pull('extract')}}"},
        python_callable=transform,
    )

    extract_task >> transform_task