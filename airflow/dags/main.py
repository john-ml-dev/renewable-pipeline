from extract_util import extract_transform # type: ignore
from load_csv_utils import load_csv_sql  # type: ignore
from zip_directory_util import zip_directory  # type: ignore
from upload_s3_util import upload_directory_to_s3 # type: ignore
from creat_redshift_table_util import create_rds_table # type: ignore
from copy_s3_data_util import lambda_handler # type: ignore

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator # type: ignore
from airflow.operators.python_operator import PythonOperator # type: ignore
from airflow.operators.postgres_operator import PostgresOperator  # type: ignore
import os

input_data = "/opt/airflow/input/Renewable.csv"
output = "/opt/airflow/output"

default_args = {
    'owner': 'John',
    'depends_on_past': False,
    'start_date': datetime(2024, 5, 28),
    'email': ['jtamakloe6902@gmal.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'Renewable',
    default_args=default_args,
    description='Renewable energy pipeline',
    schedule_interval='@daily',
)


extract_data = PythonOperator(
    task_id="extract_data",
    python_callable=extract_transform,
    op_kwargs = {"output_path": output,
                 "file_path": input_data},
    dag = dag
)

load_to_db = PythonOperator(
    task_id="load_to_db",
    python_callable=load_csv_sql,
    op_kwargs={
        "file_dir": output,
        "output_directory":output,
        "username": os.getenv("username"),
        "password": os.getenv("password"),
        "database": os.getenv("database"),
        "host": os.getenv("host"),
        "port": os.getenv("port")
        },
    dag = dag
)

zip_files = PythonOperator(
    task_id="zip_files",
    python_callable=zip_directory,
    op_kwargs = {"directory_path":output,
                 "zip_path":os.path.join(output,"data.zip")
                 },
    dag = dag )


load_to_s3 = PythonOperator(
    task_id="load_to_s3",
    python_callable=upload_directory_to_s3,
    op_kwargs = {"directory_path": output},
    dag = dag
)   

# create_rds_table_task = PythonOperator(
#     task_id="create_rds_table_task",
#     python_callable=create_rds_table,
#     dag=dag
# )

# copy_s3 = PythonOperator(
#     task_id="copy_s3",
#     python_callable=lambda_handler,
#     dag=dag
# )

extract_data >> load_to_db 
extract_data >> zip_files >> load_to_s3 
# load_to_s3 >> create_rds_table_task >> copy_s3