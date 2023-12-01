## Module Import
# 입출력 스트림, argv 등
import sys
# 옵션 인자 파싱
import argparse
# 프로그램 실행
import subprocess


import paho.mqtt.client as mqtt
import traceback
from datetime import datetime
import json
import numpy as np
import random
#import redis
#from dotenv import load_dotenv
import os
from typing import List
import time
import math




## Main module class, functions


## Setup, rpush functions
# r = redis.Redis(host='localhost', port=****, db=0)
# load_dotenv(dotenv_path='/***************', verbose=True)
# streamKey = f'*******:{os.getenv("device.id")}:****:****:****'




# 브로커 설정
broker_address = "***.***.***.***"
port = '****'
topic = "***********************"

# 새로운 클라이언트 생성
client = mqtt.Client()
client.connect(broker_address, port)

# 연결
client.loop_start()




def push_test(obj):
    now = datetime.now()

    current_time = now.strftime("%y-%m-%d %H:%M:%S.%f")
    print("PUSH Current Time =", current_time)

    json_object = obj

    json_string = json.dumps(json_object)
    print(json_string)
    #r.rpush(streamKey, json_string)


def envsensor_to_json(raw: List[str]):
    obj = {
        'device': '01',
        'device_name': 'Envsensor',
        'edge_time': raw[0],
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
    try:
        client.publish(topic, str(obj))
    except:
        pass
    return obj


def groundtemperature_to_json(raw: List[str]):
    obj = {
        'device': '02',
        'device_name': 'GroundTemperature',
        'edge_time': raw[0],
        'surface_temperature_1': raw[1],
        'surface_temperature_2': raw[2],
        'surface_temperature_3': raw[3],
        'surface_temperature_4': raw[4],
        'surface_temperature_5': raw[5],
        'surface_temperature_6': raw[6],
        'surface_temperature_7': None,
        'surface_temperature_8': None,
        'surface_temperature_9': None,
        'surface_temperature_10': None,
        'surface_temperature_11': None,
        'surface_temperature_12': None,
        'surface_temperature_13': None,
        'surface_temperature_14': None,
        'surface_temperature_15': None,
        'surface_temperature_16': None,
        'surface_temperature_17': None,
        'surface_temperature_18': None,
    }
    try:
        client.publish(topic, str(obj))
    except:
        pass
    return obj


def apiweathercode_to_json(raw: List[str]):
    obj = {
        'device': 'weather', 
        'device_name': '기상청API(날씨)', 
        'edge_time': raw[0],
        'API_time': raw[1],
        # 'STN': raw[2], 
        'longitude': raw[3],
        'latitude': raw[4],
        # 'S': raw[5],
        # 'visibility': raw[6], 
        # 'visibility_10m': raw[7], 
        'weather': raw[8], 
        'weather_15m': raw[9], 
    }
    try:
        client.publish(topic, str(obj))
    except:
        pass
    return obj


def roadcamera_to_json(raw: List[str]):
    obj = {
        'device': 'roadcamera', 
        'device_name': '보조 분류AI용 USB카메라 이미지', 
        'edge_time': raw[0],
        'encoding': 'ASCII, base64, PNG', 
        'binary': raw[1], 
    }
    try:
        client.publish(topic, str(obj))
    except:
        pass
    return obj

def coculate_dewpoint(air_temperature, r_humidity) -> float:
    ##### 이슬점 근사치를 계산한다. 
    ## 입력 : 온도, 습도
    ## 출력 : 이슬점 온도

    ## 상수 ## 
    b = 17.62
    c = 243.12

    gamma = ( b * air_temperature / ( c + air_temperature ) ) + math.log( r_humidity / 100.0 ) 
    dewpoint = ( c * gamma ) / ( b - gamma )

    return dewpoint

def predict_to_json(raw: List[str]):
    # DATE
    #'ai1h_out_temperature', 'ai1h_out_surface_temperature', 'ai1h_out_humidity', 'ai1h_out_wind_velocity', 'ai1h_out_weather',
    #'ai1h_out_temperature', 'ai1h_out_surface_temperature', 'ai1h_out_humidity', 'ai1h_out_wind_velocity', 'ai1h_out_weather',
    obj = {
        'device': 'AI', 
        'device_name': 'AI 예측', 
        'edge_time': raw[0],  
        'temperature_1h': raw[2],
        'humidity_1h': raw[3],
        'surface_temperature_1h' : raw[1],
        'weather_1h' : raw[4],

        'temperature_2h': raw[2],
        'humidity_2h': raw[3],
        'surface_temperature_2h' : raw[1],
        'weather_2h' : raw[4],
    }
    try:
        client.publish(topic, str(obj))
    except:
        pass
    return obj




def frozen_to_json(raw: List[str]):
    obj = {
        'device': 'AI', 
        'device_name': 'AI 빙결예측', 
        'edge_time': raw[0], 
        'frozen_classification_0h': raw[1], 
        'frozen_classification_1h': raw[2], 
        'frozen_classification_2h': raw[3], 
    }
    try:
        client.publish(topic, str(obj))
    except:
        pass
    return obj


def subfrozen_to_json(raw: List[str]):
    obj = {
        'device': 'AI', 
        'device_name': '이미지 기반 보조 AI 빙결분류', 
        'edge_time': raw[0],
        'frozen_classification_0h': raw[1],
    }
    try:
        client.publish(topic, str(obj))
    except:
        pass
    return obj





## Main
if __name__ == '__main__':
    ###############################################################################################################
    DATA_MAX_LENGTH = 256
    FAILED_DATA = [None] * DATA_MAX_LENGTH
    ###############################################################################################################

    # 입력 인자 파싱
    parser = argparse.ArgumentParser(prog=sys.argv[0], add_help=True)
    parser.add_argument('--collect', type=str, nargs=1, action='store', required=True)
    parser.add_argument('--database', type=str, nargs=1, action='store', required=True)
    parser.add_argument('--frost', type=str, nargs=1, action='store', required=True)
    parser.add_argument('--power', type=str, nargs=1, action='store', required=True)
    parser.add_argument('--classifi', type=str, nargs=1, action='store', required=True)
    parser.add_argument('--cycle_minute', type=int, nargs=1, action='store', required=True)

    args = parser.parse_args()



    try:
        while True:
            ###############################################################################################################
            # 동작시간 측정
            running_time = time.time()
            ###############################################################################################################



            ## 1. 데이터 수집
            '''
            ## 파일 형식 예시
                    envsensor = ~/envsensor --port_i2c 1\n
                    groundtemperature = ~/groundtemperature --port /dev/ttyTHS1 --logger_addr 6 ...\n
                    roadcamera = ~/roadcamera --configure_load_path ~/roadcamera_configure.conf\n
                    ... 
            '''
            # 프로세스, 실행 결과 저장 딕셔너리 선언 (key = 기기명(구분자))
            collect_dict = {}
            print('dad')

            # 옵션 파일 파싱 후 하위 프로세스 실행
            with open(args.collect[0], 'r') as collect_commands:
                for line in collect_commands:
                    if not line.strip().startswith('#'):
                        key, command = map(str.strip, line.split('='))

                        collect_dict[key] = {'process': None, 'stdout': None, 'stderr': None}
                        collect_dict[key]['process'] = subprocess.Popen(
                            args=[arg_cur for arg_cur in command.split()], 
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True, 
                            encoding='utf-8'
                        )
                
            # 하위 프로세스 실행 완료까지 대기
            while not all(collect_dict[key]['process'].poll() != None for key in collect_dict.keys()):
                pass

            # 하위 프로세스 실행 결과 가져오기
            for key in collect_dict.keys():
                stdout_cur, stderr_cur = map(str.strip, collect_dict[key]['process'].communicate())

                collect_dict[key]['stdout'] = stdout_cur
                collect_dict[key]['stderr'] = stderr_cur
                print(f'CUR: {key}')
                print(f'stdout ) {stdout_cur}') # ---확인용---
                print(f'stderr ) {stderr_cur}\n\n') # ---확인용---
            
            ###############################################################################################################
            try:
                envsensor_obj = envsensor_to_json(collect_dict['envsensor']['stdout'].split())
            except:
                envsensor_obj = envsensor_to_json(FAILED_DATA)
            push_test(envsensor_obj)

            try:
                groundtemperature_obj = groundtemperature_to_json(collect_dict['groundtemperature']['stdout'].split())
            except:
                groundtemperature_obj = groundtemperature_to_json(FAILED_DATA)
            push_test(groundtemperature_obj)

            try:
                apiweathercode_obj = apiweathercode_to_json(collect_dict['apiweathercode']['stdout'].split())
            except:
                apiweathercode_obj = apiweathercode_to_json(FAILED_DATA)
            push_test(apiweathercode_obj)

            import base64
            try:
                edge_time, image_path = collect_dict['roadcamera']['stdout'].split()
                with open(image_path, 'rb') as image_raw:
                    roadcamera_obj = roadcamera_to_json([edge_time, base64.b64encode(image_raw.read()).decode('ascii')])
            except:
                roadcamera_obj = roadcamera_to_json(FAILED_DATA)
            push_test(roadcamera_obj)
            ###############################################################################################################




            


            ## 3. 빙결예측
            ###############################################################################################################
            #time.sleep(8.32)
            # 프로세스, 실행 결과 저장 딕셔너리 선언 (key = 기기명(구분자))
            frost_dict = {}
            #print(collect_dict['envsensor']['stdout'].split())
            col = collect_dict['envsensor']['stdout'].split()[1:9]
            print(col)
            dew = coculate_dewpoint(air_temperature= float(col[5]), r_humidity=float(col[4]))
            nd = datetime.now().strftime('%Y%m%d%H%M')
            com = f'--input_wind_deg {col[1]} --input_wind_velocity {col[2]} ' + \
                f'--input_air_temperature {col[3]} --input_r_humidity {col[4]} '+ \
                f'--input_surface_tmp {col[5]} --input_weather {col[7]} '+ \
                f'--input_dewpoint {dew} --input_uv {col[-1]}'
            print(com)
            print()

            # 옵션 파일 파싱 후 하위 프로세스 실행
            with open(args.frost[0], 'r') as collect_commands:
                for line in collect_commands:
                    if not line.strip().startswith('#'):
                        key, command = map(str.strip, line.split('='))
                        print(key, command)

                        
                        command = command.replace('?', com)
                        print(args.frost[0])
                        print(command)

                        frost_dict[key] = {'process': None, 'stdout': None, 'stderr': None}
                        frost_dict[key]['process'] = subprocess.Popen(
                            args=[arg_cur for arg_cur in command.split()], 
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True, 
                            encoding='utf-8'
                        )
                
            # 하위 프로세스 실행 완료까지 대기
            while not all(frost_dict[key]['process'].poll() != None for key in frost_dict.keys()):
                pass

            # 하위 프로세스 실행 결과 가져오기
            for key in frost_dict.keys():
                stdout_cur, stderr_cur = map(str.strip, frost_dict[key]['process'].communicate())

                frost_dict[key]['stdout'] = stdout_cur
                frost_dict[key]['stderr'] = stderr_cur
                print(f'CUR: {key}')
                print(f'stdout ) {stdout_cur}') # ---확인용---
                print(f'stderr ) {stderr_cur}\n\n') # ---확인용---
            try:
                print()
                #print(frost_dict['past_frozen']['stdout'])
                reee = frost_dict['predictor_1']['stdout'].split()[1:] + frost_dict['predictor_2']['stdout'].split()[1:]
                print(reee)
                frozen_obj = predict_to_json([datetime.now().strftime('%Y%m%d%H%M%S.%f')] + reee)
            except:
                frozen_obj = predict_to_json(FAILED_DATA)
            push_test(frozen_obj)

            ###############################################################################################################



            class_dict = {}
            #print(collect_dict['envsensor']['stdout'].split())
            col = collect_dict['envsensor']['stdout'].split()[1:9]
            print(col)
            dew = coculate_dewpoint(air_temperature= float(col[5]), r_humidity=float(col[4]))
            nd = datetime.now().strftime('%Y%m%d%H%M')
            #f'-at {col[3]} -wv {col[2]} -rh {col[4]} -st {col[5]} -dst {np.round(np.random.uniform(-10, 25), 1)} ' + \
            #f'-nw {random.choice(['R', 'S', 'O'])} -pf {random.choice([True, False])} -pr {random.choice([True, False])}'

            com = f'-at {col[3]} -wv {col[2]} -rh {col[4]} -st {col[5]} -dst {np.round(np.random.uniform(-10, 25), 1)} ' + \
                f'-nw {random.choice(["R", "S", "O"])} -pf {random.choice([True, False])} -pr {random.choice([True, False])}'
            com_1 = f'-at {col[3]} -wv {col[2]} -rh {col[4]} -st {col[5]} -dst {np.round(np.random.uniform(-10, 25), 1)} ' + \
                f'-nw {random.choice(["R", "S", "O"])} -pf {random.choice([True, False])} -pr {random.choice([True, False])}'
            com_2 = f'-at {col[3]} -wv {col[2]} -rh {col[4]} -st {col[5]} -dst {np.round(np.random.uniform(-10, 25), 1)} ' + \
                f'-nw {random.choice(["R", "S", "O"])} -pf {random.choice([True, False])} -pr {random.choice([True, False])}'
            print(com)
            print()

            # 옵션 파일 파싱 후 하위 프로세스 실행
            with open(args.classifi[0], 'r') as collect_commands:
                for line in collect_commands:
                    if not line.strip().startswith('#'):
                        key, command = map(str.strip, line.split('='))
                        print(key, command)

                        if key == 'classfication':
                            command = command.replace('?', com)
                        elif key == 'classfication_1':
                            command = command.replace('?', com_1)
                        elif key == 'classfication_2':
                            command = command.replace('?', com_2)
                        else:
                            pass
                        print(args.frost[0])
                        print(command)

                        class_dict[key] = {'process': None, 'stdout': None, 'stderr': None}
                        class_dict[key]['process'] = subprocess.Popen(
                            args=[arg_cur for arg_cur in command.split()], 
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True, 
                            encoding='utf-8'
                        )
                
            # 하위 프로세스 실행 완료까지 대기
            while not all(class_dict[key]['process'].poll() != None for key in class_dict.keys()):
                pass

            # 하위 프로세스 실행 결과 가져오기
            for key in class_dict.keys():
                stdout_cur, stderr_cur = map(str.strip, class_dict[key]['process'].communicate())

                class_dict[key]['stdout'] = stdout_cur
                class_dict[key]['stderr'] = stderr_cur
                print(f'CUR: {key}')
                print(f'stdout ) {stdout_cur}') # ---확인용---
                print(f'stderr ) {stderr_cur}\n\n') # ---확인용---
            try:
                print()
                #print(frost_dict['past_frozen']['stdout'])
                reee = [class_dict['classfication']['stdout'][1], class_dict['classfication_1']['stdout'][1], class_dict['classfication_2']['stdout'][1]]
                print(reee)
                frozen_obj = frozen_to_json([datetime.now().strftime('%Y%m%d%H%M%S.%f')] + reee)
            except:
                frozen_obj = frozen_to_json(FAILED_DATA)
            push_test(frozen_obj)


            ###############################################################################################################
            # 동작시간 측정
            running_time = round(time.time() - running_time, 6)
            print(running_time)
            # 1분 대기
            print()
            sleep_time = (args.cycle_minute[0] * 60.0) - running_time
            if sleep_time > 0.:
                time.sleep(sleep_time)
            else:
                print(f'\n-----TIMEOUT: {abs(sleep_time)}ms-----\n')
                continue
            ###############################################################################################################



    # 예외 발생 시 출력하고 종료
    except KeyboardInterrupt:
        print('\n---Exit program---', file=sys.stdout)
        sys.exit(0)

    except:
        print(traceback.print_exc(), file=sys.stderr)
        sys.exit(1)









    ## 예문
    # python Sources/Main/main_module.py --cycle_minute 1 --collect Sources/Main/TEST_RESOURCE/collection.conf --database Sources/Main/TEST_RESOURCE/database.conf --frost _ --power _