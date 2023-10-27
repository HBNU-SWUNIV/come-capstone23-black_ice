## Module Import
# 프로그램 실행
import subprocess
# 프로그램 종료, 입출력 스트림
import sys
# 반복 대기
import time
# 예외 처리
import traceback

import os
import redis
import json
from datetime import datetime
from typing import List
from dotenv import load_dotenv





## Setup, rpush functions
r = redis.Redis(host='localhost', port=6379, db=0)
load_dotenv(dotenv_path="/webservice/.env.innoroad", verbose=True)
streamKey = os.getenv('device.id') + ":stream"
#print(streamKey)


def envsensor_to_json(raw: List[str]):
    obj = {
        'type': '환경센서',
        'time': raw[0],
        'wind_velocity': raw[1],
        'wind_direction': raw[2],
        'temperature': raw[3],
        'humidity': raw[4],
        'air_pressure': raw[5],
        'illuminance': raw[6],
        'rain_level': raw[7],
        'uva': raw[8],
        'uvb': raw[9],
    }
    return obj


def groundtemperature_to_json(raw: List[str]):
    obj = {
        'type': '노면온도 로거',
        'time': raw[0],
        'surface_temperature_1': raw[1],
        'surface_temperature_2': raw[2],
        'surface_temperature_3': raw[3],
        'surface_temperature_4': raw[4],
        'surface_temperature_5': raw[5],
        'surface_temperature_6': raw[6],
    }
    return obj


def push_test(obj):
    now = datetime.now()

    current_time = now.strftime("%y-%m-%d %H:%M:%S.%f")
    print("PUSH Current Time =", current_time)

    json_object = obj

    json_string = json.dumps(json_object)
    print(json_string)
    r.rpush(streamKey, json_string)





## Main
if __name__ =="__main__":
    try:
        while True:
            # 동작시간 측정
            running_time = time.time()


            # envsensor 실행
            envsensor_result = subprocess.Popen(
                (
                    '/home/nano/Desktop/Project/ARTOA/Road_Frost_Prevention-Edge/Compiled_Programs/EnvSensor/Ubuntu18.04_aarch64/dist/envsensor', 
                    '--port_i2c', '1', 
                ), 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                universal_newlines=True, 
                encoding='utf-8'
            )
            # print(f'---envsensor---\nSTDOUT: {envsensor_result.stdout}\nSTDERR: {envsensor_result.stderr}\nRETURNCODE: {envsensor_result.returncode}\n')

            # groundtemperature 실행
            groundtemperature_result = subprocess.Popen(
                (
                    '/home/nano/Desktop/Project/ARTOA/Road_Frost_Prevention-Edge/Compiled_Programs/GroundTemperature/Ubuntu18.04_aarch64/dist/groundtemperature', 
                    '--port', '/dev/ttyTHS1', 
                    '--logger_addr', '6', 
                    '--channel', '1', '2', '3', '4', '5', '6', 
                ), 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                universal_newlines=True, 
                encoding='utf-8'
            )
            # print(f'---groundtemperature---\nSTDOUT: {groundtemperature_result.stdout}\nSTDERR: {groundtemperature_result.stderr}\nRETURNCODE: {groundtemperature_result.returncode}\n')


            while not all([envsensor_result.poll() != None, groundtemperature_result.poll() != None]):
                pass
            envsensor_result.stdout, envsensor_result.stderr = map(str.strip, envsensor_result.communicate())
            groundtemperature_result.stdout, groundtemperature_result.stderr = map(str.strip, groundtemperature_result.communicate())
            print(f'---envsensor---\nSTDOUT: {envsensor_result.stdout}\nSTDERR: {envsensor_result.stderr}\nRETURNCODE: {envsensor_result.returncode}\n')
            print(f'---groundtemperature---\nSTDOUT: {groundtemperature_result.stdout}\nSTDERR: {groundtemperature_result.stderr}\nRETURNCODE: {groundtemperature_result.returncode}\n')


            # output data -> JSON
            # envsensor
            if envsensor_result.stderr or envsensor_result.returncode != 0:
                envsensor_obj = envsensor_to_json([None] * 10)
            else:
                envsensor_obj = envsensor_to_json(envsensor_result.stdout.split())
            
            # groundtemperature
            if groundtemperature_result.stderr or groundtemperature_result.returncode != 0:
                groundtemperature_obj = groundtemperature_to_json([None] * 7)
            else:
                groundtemperature_obj = groundtemperature_to_json(groundtemperature_result.stdout.split())

            
            # JSON -> client
            push_test(envsensor_obj)
            print()
            push_test(groundtemperature_obj)


            # 동작시간 측정
            running_time = round(time.time() - running_time, 6)
            print(running_time)
            # 1분 대기
            print()
            time.sleep(float(sys.argv[1]) - running_time)



    # 예외 발생 시 출력하고 종료
    except KeyboardInterrupt:
        print('\n---Exit program---', file=sys.stdout)
        sys.exit(0)

    except:
        print(traceback.print_exc(), file=sys.stderr)
        sys.exit(1)
