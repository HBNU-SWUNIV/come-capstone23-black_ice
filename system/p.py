import datetime
import time
import peewee
import datetime as dt
import pandas as pd
import datetime
import joblib
import sys
import os
import datatables
import inspect
import subprocess



''''
연습장 파일. 맨 아래 getattr 가 아주 유용함

'''

def pattern(date: str) -> str:
    # 요구 인풋
    # datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f')

    # 출력
    # 240분 전 과거 시간(4시간 전)
    now = date[:-9]
    now = datetime.datetime.strptime(now,'%Y%m%d%H%M')
    past = (now + datetime.timedelta(minutes=-240)).strftime('%Y%m%d%H%M')

    return past


print(datetime.datetime.now().strftime('%Y%m%d%H%M'))

now = datetime.datetime.now()
past = (now + datetime.timedelta(minutes=-120)).strftime('%Y%m%d%H%M')
print(past)
#datatables.Classifier_Q.get_after_data(past)

import re

text = "2214.5m"
pattern = r'(\d+\.\d+)mm'

match = re.match(pattern, text)
if match:
    value = float(match.group(1))
    print(value)
else:
    print("No match found.")



def sub_module_call(kid_process_path :str = '', kid_process_args :str = ''):
    result = subprocess.Popen(
        args=(kid_process_path, str(kid_process_args)),
        stdout=sys.stdout,
        universal_newlines=True, 
        encoding='utf-8'
    )
    #while not all(kid_cur.poll() != None for kid_cur in kid_results):
        #pass
    return result


def get_models(module) -> list:
    '''
    어떤 모듈 내부의 peewee.Model 클래스 인스턴스 리스트를 반환
    '''
    models = []
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, peewee.Model) and name != 'Model':
            #model_name = f"<Model: {name}>"
            #print(model_name, obj)
            models.append(obj)
    return models



def find_model(models, table_name: str):
    '''
    클래스 인스턴스 리스트와 클래스 이름을 입력받아서, 리스트 내부에 해당 이름의 클래스를 탐색해 리턴
    '''
    table = None
    models = models
    for i in range(len(models)):
        if models[i].__name__ == table_name:
            table = models[i]
            return table
    return None



def form_check(str_list):
    '''
    입력받은 문자열이 올바른 시간 형식 입력인지 판별, 올바르지 않을 시 에러를 발생시킴
    '''
    for i in str_list:
        if not bool(re.fullmatch(r'\d+(\.\d+)?', i)):
            raise Exception(f'올바른 시간 형식을 입력해 주십시오. (YYYYMMDDHHMMSS.SSSSSS 와 같이 한글을 제외한 숫자열 형식 입력)')


models = get_models(datatables)
print('tables')
for i in range(len(models)):
    print(models[i].__name__)

table_name = 'TTable'
table = find_model(models, table_name)
if table == None:
    raise Exception(f'{table_name} 테이블이 없습니다.')

field_ = table._meta.fields
field_.pop('id')
field_ = list(field_.keys())
print(field_ , type(field_))

'''
for i in field_:
    mf = getattr(table, 'i')
    print(type(i), i)
    print(type(mf), mf)
print()
'''

query = table.select().where((table.daytime >= '0'))
r1 = []
r2 = []
for row in query:
    mf = getattr(row, 'b')
    r1.append(mf)
    r2.append(row.b)
    #print(type(mf), mf)
print('a',r1)
print()
print('b',r2)


print(type(getattr(datatables, 'TTable')))
print(type( getattr(getattr(datatables, 'TTable')(), 'daytime' )) )
print(getattr(getattr(datatables, 'TTable')(), 'daytime' ))

print(getattr(datatables, 'TTable')._meta.fields) #####
print(type(getattr(getattr(datatables, 'TTable'), 'd'))) #####
print( getattr(getattr(datatables, 'TTable'), 'd') )


query = getattr(datatables, 'TTable').select().join(getattr(datatables, 'Weather')).where(getattr(datatables, 'Weather').username >= '1000')