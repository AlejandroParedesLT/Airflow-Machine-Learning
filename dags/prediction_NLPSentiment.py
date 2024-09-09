from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np


from airflow import DAG
from airflow.decorators import task
from airflow.hooks.base_hook import BaseHook
import requests
from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook

default_args = {
    'owner' : 'alejandro',
    'retries' : 5,
    'retry_delay' : timedelta(minutes=2)
}

@task
def nlp_process():
    hook_api = BaseHook.get_connection('api_cred')

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
            # Handle errors here, e.g., raise an exception or return None
            print(f"Error: {response.status_code}, {response.text}")
            return None
    
    def predict_with_api(text, token):
        api_endpoint = 'nlp_huggingFace/'
        headers = {'Content-Type': 'application/json'
                   , 'Authorization': 'Bearer '+token}
        payload = {"comentario": text}
        
        api_url = f'http://{hook_api.host}:{hook_api.port}/api/'
        response = requests.post(api_url + api_endpoint, json=payload, headers=headers)
        
        if response.status_code == 200:
            prediction_result = response.json()
            return prediction_result
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None

    hook = MsSqlHook("cred")
    try:
        conn = hook.get_conn()
        cursor = conn.cursor()
        
        FECHA_INI = datetime.today() - timedelta(days=1)
        FECHA_FIN = datetime.today() - timedelta(days=1)

        cursor.callproc("dbo.response", (FECHA_INI, FECHA_FIN))
        
        rows = []
        for row in cursor:
            rows.append(row)

        df = pd.DataFrame(rows, columns= ['RESPONSEID', 'COMENT', 'DATE', 'NOTE', 'CHANEL'])
        print(df.dtypes)
        print(df.head(10))

        cursor.close()
        conn.close()
    except Exception as e:
        cursor.close()
        conn.close()
        import traceback
        traceback.print_exc()
        print("There is a problem with SQL Server:", e)
    else:
        print(f'exito importacion')
    
    cred = backend_login('cred')
    for index, row in df.iterrows():
        texto = row['NEW_COMPLEX']
        
        predictions = predict_with_api(texto, cred['access'])
        
        row['pred'] = predictions['prediction']
        row['output'] = predictions['output']
        row['version'] = predictions['version']
    
    try:
        df.to_sql('dbo.example')

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        import traceback
        traceback.print_exc()
        print("There is a problem with SQL Server:", e)
    else:
        print(f'success insertion')

with DAG(
    dag_id='BERT_pred',
    description = 'BERT_pred',
    start_date = datetime(2023, 6, 21, 8),
    schedule_interval = '30 7 * * *',
    catchup = False
    ) as dag :

    get_data = nlp_process()
    
    get_data