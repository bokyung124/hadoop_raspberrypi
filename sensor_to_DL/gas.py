import RPi.GPIO as GPIO
import time
import smbus
from datetime import datetime, timedelta
from dateutil.parser import parse

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import boto3
import json

bus = smbus.SMBus(1)

DEVICE_ADDR = 0x48  # PCF8591 모듈의 I2C 주소 (기본값: 0x48)
GP2Y1014AU_PIN = 0   # PCF8591 AIN0 pin
MQ5_PIN = 1

def read_adc(pin):
    """Read analog input from the specified pin."""
    bus.write_byte(DEVICE_ADDR, pin)  # set PCF8591 control byte to select the specified pin
    value = bus.read_byte(DEVICE_ADDR) # read the analog input value
    return value

# Define GP2Y1014AU dust sensor parameters
VCC = 5.0  # Supply voltage

# Define MQ-5 gas sensor parameters
RL_VALUE = 10.0  # Load resistance on the board, in kilo ohms
RO_CLEAN_AIR = 9.83  # Clean air resistance, in kilo ohms
GAS_HYDROGEN = 0  # Hydrogen gas
GAS_LPG = 1  # LPG gas
GAS_METHANE = 2  # Methane gas
GAS_CARBON_MONOXIDE = 3  # Carbon Monoxide gas
GAS_ALCOHOL = 4  # Alcohol gas
GAS_SMOKE = 5  # Smoke gas

# Define MQ-5 gas sensor read function
def read_gas(gas_type):
    raw = read_adc(MQ5_PIN)
    voltage = raw / 255.0 * VCC
    RS = RL_VALUE * (VCC - voltage) / voltage
    if gas_type == GAS_HYDROGEN:
        print("Hydrogen gas")
        GAS_R0 = 4.4
        GAS_SLOPE = -1.03
    elif gas_type == GAS_LPG:
        #print("LPG gas")
        GAS_R0 = 3.5
        GAS_SLOPE = -0.76
    elif gas_type == GAS_METHANE:
        #print("Methane gas")
        GAS_R0 = 4.4
        GAS_SLOPE = -1.03
    elif gas_type == GAS_CARBON_MONOXIDE:
        print("Carbon Monoxide gas")
        GAS_R0 = 4.4
        GAS_SLOPE = -1.03
    elif gas_type == GAS_ALCOHOL:
        print("Alcohol gas")
        GAS_R0 = 3.5
        GAS_SLOPE = -0.86
    elif gas_type == GAS_SMOKE:
        #print("Smoke gas")
        GAS_R0 = 3.5
        GAS_SLOPE = -0.86
    else:
        return -1
    ratio = RS / RO_CLEAN_AIR
    gas = GAS_R0 * (ratio ** GAS_SLOPE)
    return gas

def gas_concentration():
    """Calculate and return the gas concentration."""
    V_OC = read_adc(MQ5_PIN) / 255 * 3.3  # output voltage of MQ-5 gas sensor
    R_load = 10  # load resistor value (unit: kohm)
    R_s = (3.3 - V_OC) / V_OC * R_load  # sensor resistance (unit: kohm)
    gas_concentration = 0.4 * R_s  # gas concentration calculation (unit: ppm)
    return gas_concentration

s3 = boto3.client('s3')
bucket_name = 'raspberrypi-dacos'

kine = boto3.client('kinesis', region_name='ap-northeast-2')


data = {'Time': [],
        'Methane': [],
        'LPG': [],
        'Smoke': [],
        'Alcohol': [],
        'Carbon': []}

now = datetime.now()
prev_time = now.strftime('%Y-%m-%dT%H:%M:%S')

def upload_to_s3(df, filename):
    table = pa.Table.from_pandas(df)
    pq.write_table(table, filename)
    s3.upload_file(filename, bucket_name, filename)

while True:
    try:
        now = datetime.now()
        now_time = now.strftime('%Y-%m-%dT%H:%M:%S')
        gas_methane = float(read_gas(GAS_METHANE))
        gas_lpg = float(read_gas(GAS_LPG))
        gas_smoke = float(read_gas(GAS_SMOKE))
        gas_alcohol = float(read_gas(GAS_ALCOHOL))
        gas_carbon = float(read_gas(GAS_CARBON_MONOXIDE))

        data['Time'].append(now_time)
        data['Methane'].append(gas_methane)
        data['LPG'].append(gas_lpg)
        data['Smoke'].append(gas_smoke)
        data['Alcohol'].append(gas_alcohol)
        data['Carbon'].append(gas_carbon)

        # If date has changed, upload previous day's data to S3 and start new DataFrame
        if now >= parse(prev_time) + timedelta(minutes=10):
            df = pd.DataFrame(data)
            filename = 'gas_data_{}.parquet'.format(prev_time)
            table = pa.Table.from_pandas(df)
            pq.write_table(table, filename)
            s3.upload_file(filename, bucket_name, filename)

            print('Uploaded to S3')

            # Start new DataFrame
            data = {'Time': [],
                    'Methane': [],
                    'LPG': [],
                    'Smoke': [],
                    'Alcohol': [],
                    'Carbon': []}

        prev_time = now_time

        time.sleep(1)

    except KeyboardInterrupt:
        print("KeyboardInterrupt")