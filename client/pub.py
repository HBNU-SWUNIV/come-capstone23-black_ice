import paho.mqtt.client as mqtt
import datetime
import json
import numpy as np
import random
import threading
import time

# 브로커 설정
broker_address = "121.124.124.20"
port = 1883
topic = "innoroad/window/pub_test"

# 새로운 클라이언트 생성
client = mqtt.Client()
client.connect(broker_address, port)

# 연결
client.loop_start()

'''
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

'''

# 메시지 발행
#message = "서버 변경 적용 테스트" ### sunscriver 는 json 형태만 해석 가능. 전송 시 에러로 간주됨
def my_function():
    # 실행할 함수 내용 작성
    message = {
        'edge_time' : datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'),
        'device_name' : 'Envsensor',
        'device' : 'windows10_test',
        'wind_velocity': np.round(np.random.uniform(-10, 25), 3),
        'wind_direction': np.round(np.random.uniform(-10, 25), 3),
        'temperature': np.round(np.random.uniform(-10, 25), 3),
        'humidity': np.round(np.random.uniform(-10, 25), 3),
        'air_pressure': np.round(np.random.uniform(-10, 25), 3),
        'illuminance': np.round(np.random.uniform(-10, 25), 3),
        'rain_level': np.round(np.random.uniform(-10, 25), 3),
        'uva': np.round(np.random.uniform(-10, 25), 3),
        'uvb': np.round(np.random.uniform(-10, 25), 3),
    }
    client.publish(topic, str(message))

    message = {
        'edge_time' : datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'),
        'device_name' : 'GroundTemperature', 
        'device' : 'windows10_test',
        'surface_temperature_1': np.round(np.random.uniform(-10, 25), 3),
        'surface_temperature_2': np.round(np.random.uniform(-10, 25), 3),
        'surface_temperature_3': np.round(np.random.uniform(-10, 25), 3),
        'surface_temperature_4': np.round(np.random.uniform(-10, 25), 3),
        'surface_temperature_5': np.round(np.random.uniform(-10, 25), 3),
        'surface_temperature_6': np.round(np.random.uniform(-10, 25), 3),
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
    client.publish(topic, str(message))

    message = {
        'edge_time' : datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'),
        'device_name' : '기상청API(날씨)',
        'device' : 'windows10_test',
        'API_time': datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'),
        # 'STN': raw[2], 
        'longitude': 127,
        'latitude': 61,
        # 'S': raw[5],
        # 'visibility': raw[6], 
        # 'visibility_10m': raw[7], 
        'weather': 0, 
        'weather_15m': 0,
    }
    client.publish(topic, str(message))

    message = {
        'edge_time' : datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'),
        'device_name' : 'AI 예측',
        'device' : 'windows10_test',

        'temperature_1h': np.round(np.random.uniform(-10, 25), 1),
        'humidity_1h': np.round(np.random.uniform(-10, 25), 1),
        'surface_temperature_1h': np.round(np.random.uniform(-10, 25), 1),
        'weather_1h':  random.choice(['0', '1', '2', '3']),

        'temperature_2h': np.round(np.random.uniform(-10, 25), 1),
        'humidity_2h': np.round(np.random.uniform(-10, 25), 1),
        'surface_temperature_2h': np.round(np.random.uniform(-10, 25), 1),
        'weather_2h':  random.choice(['0', '1', '2', '3']),
    }
    client.publish(topic, str(message))


    message = {
        'edge_time' : datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'),
        'device_name' : 'AI 빙결분류',
        'device' : 'windows10_test',
        'frozen_classification_0h': random.choice(['F', 'D', 'W']), 
        'frozen_classification_1h': random.choice(['F', 'D', 'W']), 
        'frozen_classification_2h': random.choice(['F', 'D', 'W']), 
    }
    client.publish(topic, str(message))

    message = {
        'edge_time' : datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'),
        'device_name' : '보조 분류AI용 USB카메라 이미지',
        'device' : 'windows10_test',
        'encoding': 'ASCII, base64, PNG', 
        'binary': 'datas!',
    }
    client.publish(topic, str(message))

    message = {
        'edge_time' : datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'),
        'device_name' : '이미지 기반 보조 AI 빙결분류',
        'device' : 'windows10_test',
        'frozen_classification_0h': random.choice(['F', 'D', 'W'])
    }
    client.publish(topic, str(message))
    print('더미데이터 전송기가 실행되었습니다.')
    threading.Timer(5, my_function).start()  # 5초 후에 다시 함수 실행

# 처음 함수 실행
my_function()

# 다른 작업을 계속할 수 있습니다.
seq_num = 0

while True:
    time.sleep(5)
    print(f'{seq_num} 번째 더미데이터 전송됨.')

# 연결 종료
client.loop_stop()