import datetime
from airflow import DAG
from airflow.decorators import task, dag
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.subdag_operator import SubDagOperator

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime.datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
}

# Create a sub-DAG function
def subdag(parent_dag_name, child_dag_name, args):
    dag_subdag = DAG(
        dag_id=f'{parent_dag_name}.{child_dag_name}',
        default_args=args,
        schedule_interval=None,  # Define your sub-DAG schedule_interval here
    )

    with dag_subdag:
        # Define tasks for the sub-DAG here
        sub_task_1 = DummyOperator(task_id='sub_task_1')
        sub_task_2 = DummyOperator(task_id='sub_task_2')

        sub_task_1 >> sub_task_2

    return dag_subdag

# Create the main DAG instance using the @dag decorator
@dag(schedule_interval='@daily', default_args=default_args, catchup=False)
def my_airflow_dag():

    # Define a Python function using the @task decorator
    @task()
    def task_hello_world():
        print("Hello, World!")

    # Define another Python function using the @task decorator
    @task()
    def task_greet(name):
        print(f"Hello, {name}!")

    # Define a Python function that generates dynamic tasks
    @task()
    def task_generate_greetings(names):
        for name in names:
            task_greet(name)

    # Define a Python function that returns values
    @task()
    def task_add_numbers(a, b):
        return a + b

    # Create DAG tasks using the PythonOperator
    start_task = DummyOperator(task_id='start_task')
    end_task = DummyOperator(task_id='end_task')

    hello_world_task = PythonOperator(
        task_id='hello_world',
        python_callable=task_hello_world,
    )

    # Task with parameters
    greet_task = PythonOperator(
        task_id='greet',
        python_callable=task_greet,
        op_args=['John'],
    )

    # Dynamic task generation
    generate_greetings_task = PythonOperator(
        task_id='generate_greetings',
        python_callable=task_generate_greetings,
        op_args=[['Alice', 'Bob', 'Charlie']],
    )

    # Task that returns values
    add_numbers_task = PythonOperator(
        task_id='add_numbers',
        python_callable=task_add_numbers,
        op_args=[3, 5],
        provide_context=True,  # To access context variables like execution date
    )

    # Set up task dependencies
    start_task >> hello_world_task >> greet_task
    start_task >> generate_greetings_task
    start_task >> add_numbers_task >> end_task

    # Define SubDAG tasks within the main DAG
    subdag_task = SubDagOperator(
        task_id='subdag_task',
        subdag=subdag('my_airflow_dag', 'subdag_task', default_args),  # Define sub-DAG here
    )

    # Set up task dependencies
    start_task >> subdag_task >> end_task

# Instantiate the DAG
dag_instance = my_airflow_dag()