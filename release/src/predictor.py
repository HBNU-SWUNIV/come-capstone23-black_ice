import pandas as pd
import datetime
import joblib
import fnmatch
import sys
import os
import argparse


def read_config(file_path):
    config = {}
    with open(file_path, 'r', encoding='UTF8') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config



## Main
if __name__ =="__main__":
    try:
        parser = argparse.ArgumentParser()

        # Control
        parser.add_argument('-mp', '--models_path', type=str, required=True)
        parser.add_argument('-of', '--option_file', type=str) ##

        # Required Data
        parser.add_argument('-it', '--input_time', type=str, required=True)
        parser.add_argument('-iwd', '--input_wind_deg', type=float, required=True)
        parser.add_argument('-iwv', '--input_wind_velocity', type=float, required=True) #
        parser.add_argument('-iat', '--input_air_temperature', type=float, required=True) #
        parser.add_argument('-irh', '--input_r_humidity', type=float, required=True) #
        parser.add_argument('-ist', '--input_surface_tmp', type=float, required=True) #
        parser.add_argument('-iw', '--input_weather', type=int, required=True) #
        parser.add_argument('-id', '--input_dewpoint', type=float, required=True)
        parser.add_argument('-iu', '--input_uv', type=float, required=True)


        args = parser.parse_args()


        # Models Load
        model_paths = os.listdir(args.models_path)
        if model_paths == []:
            raise Exception(f'{args.models_path} 경로에 모델 파일이 존재하지 않습니다.')
        
        models = []
        op = read_config(args.option_file)
        sequence = op['model_squence'].split(',')

        for i in range(len(model_paths)):
            with open(args.models_path + '/' + sequence[i] + '.pkl', 'rb') as file:
                models.append(joblib.load(file))
        
        
        # Generate input data
        input_data = pd.DataFrame({
            'wind_deg': [args.input_wind_deg],
            'wind_velocity': [args.input_wind_velocity],
            'air_temperature': [args.input_air_temperature],
            'r_humidity': [args.r_humidity],
            'surface_tmp': [args.surface_tmp],
            'weather': [args.weather],
            'dewpoint': [args.dewpoint],
            'uv': [args.uv]
        })

        result = []
        for i in range(len(model_paths)):
            prediction = models[i].predict(input_data)
            result.append(*prediction)

        # excute time, input time, results
        if args.help_for_result:
            print( *model_paths ) # 모델 가동 순서 출력
            print( datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'), args.input_time, *result)
        else:
            print( datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'), args.input_time, *result)

    
# 에러 발생 시 출력하고 종료
    except Exception as e:
        print(f'{e}', file=sys.stderr)
        sys.exit(1)