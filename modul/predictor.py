import pandas as pd
import datetime
import joblib
import sys
import os
import argparse

#import traceback



def read_config(file_path):
    config = {}
    with open(file_path, 'r', encoding='UTF8') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config




def main(args_tuple: tuple = None):
    parser = argparse.ArgumentParser()

    # Control
    parser.add_argument('-of', '--option_file', type=str) ## IN MODELS_PATH INFORMATIONS

    # Required Data(NOW ENV STATE)
    parser.add_argument('-iwd', '--input_wind_deg', type=float, required=True)
    parser.add_argument('-iwv', '--input_wind_velocity', type=float, required=True) #
    parser.add_argument('-iat', '--input_air_temperature', type=float, required=True) #
    parser.add_argument('-irh', '--input_r_humidity', type=float, required=True) #
    parser.add_argument('-ist', '--input_surface_tmp', type=float, required=True) #
    parser.add_argument('-iw', '--input_weather', type=int, required=True) #
    parser.add_argument('-id', '--input_dewpoint', type=float, required=True)
    parser.add_argument('-iu', '--input_uv', type=float, required=True)

    if args_tuple == None:
        ## 명령줄 인자로 실행할 때
        args = parser.parse_args()
    else:
        ## 외부모듈에서 main을 import 로 실행할 때
        args = parser.parse_args(args = args_tuple[1:])


    # python modul/predictor.py -of M1.conf -iwd 81.0 -iwv 0.8 -iat 5.8 -irh 71.6 -ist 7.9 -iw 0 -id 1.059 -iu 0.0


    # Models Load
    op = read_config(args.option_file)
    model_paths = [
        #op['wind_velocity'],
        op['air_temperature'],
        op['r_humidity'],
        op['surface_tmp'],
        op['weather'],
        #op['dewpoint'],
        #op['uv'],
    ]
    print(model_paths)

    models = []
    for i in model_paths:
        with open(i, 'rb') as file:
            print(i)
            models.append(joblib.load(file))
            print(i)
    
    
    # Generate input data
    #print('pp')
    input_data = pd.DataFrame({
        'wind_deg': [args.input_wind_deg],
        'wind_velocity': [args.input_wind_velocity],
        'air_temperature': [args.input_air_temperature],
        'r_humidity': [args.input_r_humidity],
        'surface_tmp': [args.input_surface_tmp],
        'weather': [args.input_weather],
        'dewpoint': [args.input_dewpoint],
        'uv': [args.input_uv]
    })

    result = []
    for i in range(len(model_paths)):
        prediction = round(models[i].predict(input_data)[0], 2) ## 데이터베이스 필드에 선언된 정밀도에 맞춤
        #print(prediction)
        result.append(prediction)

    # excute time, input time, results
    print()
    print(result)
    print()
    return result



## Main
if __name__ =="__main__":
    try:
        result = main()
        print( datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'), *result)
        sys.exit(0)

    
# 에러 발생 시 출력하고 종료
    except Exception as e:
        print(f'{__file__} :\n {e}', file=sys.stderr)
        #traceback.print_exc()
        sys.exit(1)