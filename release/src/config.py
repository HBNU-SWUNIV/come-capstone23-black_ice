#read config.txt
import os
import sys

def read_config(file_path):
    config = {}
    with open(file_path, 'r', encoding='UTF8') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config




# 텍스트 파일의 경로
'''
for debug
print(os.path.dirname(os.path.abspath(__file__)))
print(os.getcwd())
print(__file__)
https://eehoeskrap.tistory.com/496
https://www.zinnunkebi.com/python-exe-cwd-error/
'''
########################################################################################
# 하드코딩 고쳐야함 (file_path 에서 data.txt 하드코딩)
########################################################################################
if getattr(sys, 'frozen', False):
    #실행파일로 실행한 경우, 실행파일을 보관한 디렉토리의 full path를 취득
    file_path = (os.path.dirname(os.path.abspath(sys.executable)) +'/data.txt')
    #print('exe', file_path)
else:
    file_path = (os.path.dirname(os.path.abspath(__file__)) + '/data.txt')

#print(os.listdir(file_path))
# 파일에서 설정 읽어오기
try:
    config_data = read_config(file_path)
except:
    print(f'{file_path} 설정 파일을 읽을 수 없음')
    exit(1)


DEVICE = config_data.get('DEVICE')
DATA_PATH = config_data.get('DATA_PATH')
STN = config_data.get('STN')
API_KEY = config_data.get('API_KEY')
API_KEY2 = config_data.get('API_KEY2')

if __name__ == "__main__":
    # 읽어온 설정 출력
    print("config \n")
    print("DEVICE:", config_data.get('DEVICE'))
    print("DATA_PATH:", config_data.get('DATA_PATH'))
    print("STN:", config_data.get('STN'))
    print("API_KEY:", config_data.get('API_KEY'))
    print("API_KEY2:", config_data.get('API_KEY2'))
    print("\nconfig end\n")