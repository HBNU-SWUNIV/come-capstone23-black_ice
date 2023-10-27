import sys
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
print(streamKey)


def read_config_file(file_path):
    config = {}

    '''
    처리 가능한 파일 형식 : .txt
    내용 예시

    ## 주석문
    REQUIRE = 4
    FROM=envsensor
    NAMES=time,temp,rh,rain

    '''
    with open(file_path, 'r', encoding='UTF8') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config



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
        parse_config = sys.argv[1]
        data = sys.argv[2:]

        how_parse = read_config_file(parse_config) #데이터 파싱 방법(설정파일)읽어오기
        #print(how_parse)

        req = how_parse.get('REQUIRE') # 필요 데이터 수
        where = how_parse.get('FROM') # 데이터 타입(환경센서, AI데이터, 분류알고리즘 출력 등 출처)
        data_columns = how_parse.get('NAMES').split(',') # 데이터명(필요 데이터 수 만큼)

        if int(req) != len(data):
            raise Exception(f'string argv err : 요구 인자 수( {req} ) 불일치 ( {len(data)} )')
        if int(req) != len(where):
            raise Exception(f'config file err : 요구 인자 수( {req} ) 불일치 ( {len(data_columns)} )')

        data_columns.insert(1, 'resource')
        data.insert(1, where)
        dictionary = dict( zip(data_columns, data) )
        '''
        dictionary 에 입력되는 정보의 형식
        {
            'key_1' : 'value_1',
            'resource' : where, # 데이터 타입(환경센서, AI데이터, 분류알고리즘 출력 등 출처)
            'key_2' : 'value_2',
            ...
            'key_n' : 'value_n'
        }
        
        '''
        push_test(dictionary)
        
        sys.exit(0)

# 에러 발생 시 출력하고 종료
    except Exception as e:
        print(f'{e}', file=sys.stderr)
        sys.exit(1)