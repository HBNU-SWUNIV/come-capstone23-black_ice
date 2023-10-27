## Module Import
# 입출력 스트림, argv 등
import sys
# 옵션 인자 파싱
import argparse
# 프로그램 실행
import subprocess



import traceback
from datetime import datetime
import json
import redis
from dotenv import load_dotenv
import os
from typing import List
import time




## Main module class, functions


## Setup, rpush functions
r = redis.Redis(host='localhost', port=6379, db=0)
load_dotenv(dotenv_path='/webservice/.env', verbose=True)
streamKey = f'innoroad:{os.getenv("device.id")}:mqtt:event:up'



def push_test(obj):
    now = datetime.now()

    current_time = now.strftime("%y-%m-%d %H:%M:%S.%f")
    print("PUSH Current Time =", current_time)

    json_object = obj

    json_string = json.dumps(json_object)
    print(json_string)
    r.rpush(streamKey, json_string)


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
    return obj


def roadcamera_to_json(raw: List[str]):
    obj = {
        'device': 'roadcamera', 
        'device_name': '보조 분류AI용 USB카메라 이미지', 
        'edge_time': raw[0],
        'encoding': 'ASCII, base64, PNG', 
        'binary': raw[1], 
    }
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
    return obj


def subfrozen_to_json(raw: List[str]):
    obj = {
        'device': 'AI', 
        'device_name': '이미지 기반 보조 AI 빙결분류', 
        'edge_time': raw[0],
        'frozen_classification_0h': raw[1],
    }
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




            ## 2. DB 입출력
            '''
            ## 파일 형식 예시
                    envsensor = ~/database_iod -i -tn Sensor -ds ?\n
                    groundtemperature = ~/database_iod -i -tn Surface -ds ?\n
                    ...
                    (데이터 수집 모듈의 결과가 필요한 부분은 '?'로 표기할 것)
            '''
            # 프로세스, 실행 결과 저장 딕셔너리 선언 (key = 기기명(구분자))
            database_dict = {}

            with open(args.database[0], 'r') as database_commands:
                for line in database_commands:
                    if not line.strip().startswith('#'):
                        key, command = map(str.strip, line.split('='))

                        if key in collect_dict.keys():
                            command = command.replace('?', collect_dict[key]['stdout'])

                            database_dict[key] = {'process': None, 'stdout': None, 'stderr': None}
                            database_dict[key]['process'] = subprocess.Popen(
                                args=[arg_cur for arg_cur in command.split()], 
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True, 
                                encoding='utf-8'
                            )

            # # 하위 프로세스 실행 완료까지 대기
            # while not all(database_dict[key]['process'].poll() != None for key in database_dict.keys()):
            #     pass

            # 하위 프로세스 실행 결과 가져오기
            for key in database_dict.keys():
                stdout_cur, stderr_cur = map(str.strip, database_dict[key]['process'].communicate())

                database_dict[key]['stdout'] = stdout_cur
                database_dict[key]['stderr'] = stderr_cur

                print(f'CUR: {key}')
                print(f'stdout ) {stdout_cur}') # ---확인용---
                print(f'stderr ) {stderr_cur}\n\n') # ---확인용---




            ## 3. 빙결예측
            ###############################################################################################################
            time.sleep(8.32)
            try:
                frozen_obj = frozen_to_json([datetime.now().strftime('%Y%m%d%H%M%S.%f'), 'D', 'D', 'D'])
            except:
                frozen_obj = frozen_to_json(FAILED_DATA)
            push_test(frozen_obj)

            # 보조모델
            time.sleep(13.96)
            try:
                subfrozen_obj = subfrozen_to_json([datetime.now().strftime('%Y%m%d%H%M%S.%f'), 'F'])
            except:
                subfrozen_obj = subfrozen_to_json(FAILED_DATA)
            push_test(subfrozen_obj)
            ###############################################################################################################



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