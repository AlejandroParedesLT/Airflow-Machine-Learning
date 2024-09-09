import sys
import os
sys.path.append(os.path.dirname(__file__))

from datetime import date, datetime, timedelta
#from sqlalchemy import create_engine
#from sqlalchemy.engine import URL
import pandas as pd
import numpy as np
from Cls_mailing_conector import EnviosMail


from airflow import DAG
from airflow.decorators import task
from airflow.hooks.base_hook import BaseHook

import requests
def global_failure():
    fecha_actual = datetime.now()
    fecha_actual_str = fecha_actual.strftime("%Y-%m-%d")  # Formato YYYY-MM-DD
    print("Mail start", fecha_actual_str)
    mailing.enviar_correo_base('Notification', f"Failure {fecha_actual_str}", 'Owner')

default_args = {
    'owner' : 'alejandro',
    'retries' : 5,
    'retry_delay' : timedelta(hours=6),
    "on_failure_callback": global_failure
}

mailing = EnviosMail()

@task
def mail_start():
    fecha_actual = datetime.now()
    fecha_actual_str = fecha_actual.strftime("%Y-%m-%d")  # Formato YYYY-MM-DD
    print("Mail start", fecha_actual_str)
    mailing.enviar_correo_base('Notification', f"Process started {fecha_actual_str}", 'Owner')

@task
def mail_end():
    fecha_actual = datetime.now()
    fecha_actual_str = fecha_actual.strftime("%Y-%m-%d")  # Formato YYYY-MM-DD
    print("Mail end", fecha_actual_str)
    mailing.enviar_correo_base('Notification', f"Process started {fecha_actual_str}", 'Owner')


@task
def default_credit_risk():
    hook_api = BaseHook.get_connection('ml_api')
    
    def backend_login(username, password):
        api_endpoint = 'token/'
        headers = {'Content-Type': 'application/json'}
        payload = {"username": username, "password": password}
        
        api_url = f'http://{hook_api.host}:{hook_api.port}/api/'
        response = requests.post(api_url + api_endpoint, json=payload, headers=headers)
        
        if response.status_code == 200:
            keys = response.json()
            return keys
        else:
            header = "Failure Authenticating to the Backend, Check the Server"
            body = "Error"
            footer = "Owner"
            print('Post request backend login')
            mailing.enviar_correo_base(header, body, footer)
            print('Hola mundo')
            raise Exception(f"{str(response.status_code)}: Incorrect Credentials, {response.text}")
    
    def post_request_process(trigger, token):
        api_endpoint = 'default_credit_risk/'
        headers = {'Content-Type': 'application/json'
                   , 'Authorization': 'Bearer '+token}
        payload = {"trigger": trigger}
        
        api_url = f'http://{hook_api.host}:{hook_api.port}/api/'
        response = requests.post(api_url + api_endpoint, json=payload, headers=headers)
        
        if response.status_code == 200:
            # Successful API call
            prediction_result = response.json()
            return prediction_result
        else:
            header = "Error"
            body = "Error Prediction"
            footer = "Alejandro"
            mailing.enviar_correo_base(header, body, footer)
            raise Exception(f"{str(response.status_code)}: Failed to process, {response.text}")
    
    try:
        predictions = post_request_process('execute_default_credit_risk', cred['access'])
    except Exception as e:
        header = "Failure Authenticating to the Backend, Check the Server"
        body = "Failure general"
        footer = "Alejandro"
        mailing.enviar_correo_base(header, body, footer)
        raise Exception(f"{e}")

with DAG(
    dag_id='default_credit_risk',
    description = 'default_credit_risk',
    start_date = datetime(2023, 6, 21, 8),
    default_args=default_args,
    schedule_interval = '0 11 1 * *',
    catchup = False
    ) as dag :
    init_process_mailing = mail_start()
    get_data = default_credit_risk()
    end_process_mailing = mail_end()
    
    init_process_mailing >> get_data >> end_process_mailing