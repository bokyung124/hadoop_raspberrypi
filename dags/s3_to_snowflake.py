from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import s3fs

from datetime import datetime, timedelta

import logging
import json
import pandas as pd

def get_snowflake_conn():
    hook = SnowflakeHook(snowflake_conn_id='raspberry-db')
    conn = hook.get_conn()
    cursor = conn.cursor()
    return cursor

@task
def temp_parquet_to_csv():
    hook = S3Hook('s3_upload')
    s3_access_key = Variable.get('s3_access_key')
    s3_access_secret = Variable.get('s3_access_secret')
    fs = s3fs.S3FileSystem(key=s3_access_key, secret=s3_access_secret)

    bucket_name = "raspberrypi-dacos"
    today = datetime.now().strftime('%Y-%m-%d')
    files = fs.glob(bucket_name + f"/*{today}*.parquet")
    dfs = [pd.read_parquet('s3://' + file, storage_options={'key':s3_access_key, 'secret':s3_access_secret}) for file in files]


    df = pd.concat(dfs, ignore_index=True)

    csv_file = f"temp_{today}.csv"
    df.to_csv(csv_file, index=False)
    hook.load_file(filename=csv_file, key=csv_file, bucket_name=bucket_name, replace=True)

@task
def gas_parquet_to_csv():
    hook = S3Hook('s3_upload')
    s3_access_key = Variable.get('s3_access_key')
    s3_access_secret = Variable.get('s3_access_secret')
    fs = s3fs.S3FileSystem(key=s3_access_key, secret=s3_access_secret)

    bucket_name = "raspberrypi-gas"
    today = datetime.now().strftime('%Y-%m-%d')
    files = fs.glob(bucket_name + f"/*{today}*.parquet")
    dfs = [pd.read_parquet('s3://' + file, storage_options={'key':s3_access_key, 'secret':s3_access_secret}) for file in files]


    df = pd.concat(dfs, ignore_index=True)

    csv_file = f"gas_{today}.csv"
    df.to_csv(csv_file, index=False)
    hook.load_file(filename=csv_file, key=csv_file, bucket_name=bucket_name, replace=True)

@task
def temp_s3_to_snowflake(schema, table):
    cur = get_snowflake_conn()
    key = Variable.get('s3_access_key')
    secret = Variable.get('s3_access_secret')

    today = str(datetime.now())
    i = 1

    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table} (
            time            datetime,
            temperature     float,
            humidity        float
        );
    """

    create_t_sql = f"""CREATE TEMP TABLE t AS SELECT * FROM {schema}.{table};"""

    copy_sql = f"""
        COPY INTO t
        FROM 's3://raspberrypi-dacos/temp_{today}.csv'
        CREDENTIALS = (aws_key_id='{key}' aws_secret_key='{secret}')
        ON_ERROR = CONTINUE;
    """

    insert_sql = f"""
        INSERT INTO {schema}.{table}
        SELECT * FROM t;
    """ 

    try:
        cur.execute(create_table_sql)
        logging.info(create_table_sql)

        cur.execute(create_t_sql)
        logging.info(create_t_sql)

        cur.execute("BEGIN;")
        cur.execute(copy_sql)
        logging.info(copy_sql)

        cur.execute(insert_sql)
        cur.execute("COMMIT;")

    except Exception as e:
        logging.error(e)
        cur.execute("ROLLBACK;")
        raise

@task
def gas_s3_to_snowflake(schema, table):
    cur = get_snowflake_conn()
    key = Variable.get('s3_access_key')
    secret = Variable.get('s3_access_secret')

    today = str(datetime.now())

    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table} (
            time        datetime,
            methane     float,
            lpg         float,
            smoke       float,
            alcohol     float,
            carbon      float
        );
    """

    create_t_sql = f"""CREATE TEMP TABLE t AS SELECT * FROM {schema}.{table};"""

    copy_sql = f"""
        COPY INTO t
        FROM 's3://raspberrypi-gas/gas_{today}.csv'
        CREDENTIALS = (aws_key_id='{key}' aws_secret_key='{secret}')
        ON_ERROR = CONTINUE;
    """

    insert_sql = f"""
        INSERT INTO {schema}.{table}
        SELECT * FROM t;
    """ 

    try:
        cur.execute(create_table_sql)
        logging.info(create_table_sql)

        cur.execute(create_t_sql)
        logging.info(create_t_sql)

        cur.execute("BEGIN;")
        cur.execute(copy_sql)
        logging.info(copy_sql)

        cur.execute(insert_sql)
        cur.execute("COMMIT;")

    except Exception as e:
        logging.error(e)
        cur.execute("ROLLBACK;")
        raise


with DAG(
    dag_id = 'temperature_to_snowflake',
    start_date = datetime(2024, 1, 17),
    schedule_interval = '*/10 * * * *',
    catchup = False,
    default_args = {
        'retries': 2,
        'retry_delay': timedelta(minutes=1),
    }
) as dag:
    
    temp_parquet_to_csv() >> temp_s3_to_snowflake('raw_data', 'temperature')
    gas_parquet_to_csv() >> gas_s3_to_snowflake('raw_data', 'gas')