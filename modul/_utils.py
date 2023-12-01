import inspect
import peewee
import re
import subprocess
import sys



'''
표준 입출력으로 모듈화 불가능한 기능 또는 광범위하게 사용되는 기능을 정의한 모듈

표준 입출력으로 전달이 불가능한 사유는 다음과 같음

1. 클래스 자체를 입출력하기 때문에 표준입출력으로 전달이 불가능
2. 입력이 올바른지 판단하기 위해 정의했으므로 에러를 발생시킴


'''

# class Error_cover(Exception):
#     def __init__(self, user_err_msg: str = None):
#         self.message = user_err_msg

#     def __str__(self):
# 		return self.message



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
