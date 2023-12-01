import sys
import argparse
import datetime

import database_iod
import predictor
import Classifier
import numpy as np
#import apiutils


def main(args_tuple: tuple = None):
    parser = argparse.ArgumentParser(prog=sys.argv[0], add_help=True)

    # Required Path(Model Files Paths)
    parser.add_argument('-mp1', '--model_path_1h', type=str)
    parser.add_argument('-mp2', '--model_path_2h', type=str)

    # Required Path(IMG_Model File and IMG File Path)
    parser.add_argument('-imp', '--img_model_path', type=str)
    parser.add_argument('-idp', '--img_data_path', type=str)

    # DataBase request info
    parser.add_argument('-c', '--surface_ch', type=int, required=True)
    parser.add_argument('-pk', '--primary_key', type=str, required=True) #database datetime


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


    #### predict ENV
    if args.model_path_1h or args.model_path_2h:
        #import predictor
        input_tmp = [
            '-iwd', f'{args.input_wind_deg}',
            '-iwv', f'{args.input_wind_velocity}',
            '-iat', f'{args.input_air_temperature}',
            '-irh', f'{args.input_r_humidity}',
            '-ist', f'{args.input_surface_tmp}',
            '-iw', f'{args.input_weather}',
            '-id', f'{args.input_dewpoint}',
            '-iu', f'{args.input_uv}',
        ]
        if args.model_path_1h:
            result_1h = predictor.main( tuple(['-of', f'{args.model_path_1h}'] + input_tmp) ) # AI예측모델 가동
            #print(result_1h)
            update_data = (
                'database_iod.py',
                '-tn', 'UNIONTABLE',
                'update',
                '--pointer', f'{args.primary_key}',
                '--columns', 'ai1h_out_temperature', 'ai1h_out_surface_temperature', 'ai1h_out_humidity', 'ai1h_out_wind_velocity', 'ai1h_out_weather',
                '--data',
            )
            try:
                database_iod.main(update_data + tuple(result_1h)) # DB에 입력
            except:
                pass

        if args.model_path_2h:
            result_2h = predictor.main( tuple(['-of', f'{args.model_path_2h}'] + input_tmp) ) # AI예측모델 가동
            #print(result_2h)
            update_data = (
                'database_iod.py',
                '-tn', 'UNIONTABLE',
                'update',
                '--pointer', f'{args.primary_key}',
                '--columns', 'ai2h_out_temperature', 'ai2h_out_surface_temperature', 'ai2h_out_humidity', 'ai2h_out_wind_velocity', 'ai2h_out_weather',
                '--data',
            )
            try:
                database_iod.main(update_data + tuple(result_2h)) # DB에 입력
            except:
                pass
        return result_1h+ result_2h

    #### Classifier

    ## preprocessing
    ## 과거 빙결 이력 조회 [현재, 미래1시간, 미래2시간]기준\
    try:
        past_frozen = database_iod.main(('database_iod.py', '-tn', 'UNIONTABLE', 'request_past_frozen', '--pointer', f'{args.primary_key}'))
    #print(past_froaen)
    except:
        past_frozen = [False, False, False]
        pass
    
    ## 과거 강수 이력 조회 [현재, 미래1시간, 미래2시간]기준
    try:
        past_rain = database_iod.main(('database_iod.py', '-tn', 'UNIONTABLE', 'request_pase_rain', '--pointer', f'{args.primary_key}'))
    #print(past_rain)
    except:
        past_rain = [False, False, False]
        pass
    
    ## 시간당 노면온도 변화량 조회 [현재, 미래1시간, 미래2시간]기준
    try:
        past_delta_surface = database_iod.main(('database_iod.py', '-tn', 'UNIONTABLE', 'request_delta_surface_temperature', '--pointer', f'{args.primary_key}', '--channel', f'{args.surface_ch}'))
    #print(past_delta_surface)
    except:
        past_delta_surface(np.round(np.random.uniform(-1, 2), 3), np.round(np.random.uniform(-1, 2), 3), np.round(np.random.uniform(-1, 2), 3))
        pass

    update_data = (
        'database_iod.py',
        '-tn', 'UNIONTABLE',
        'update',
        '--pointer', f'{args.primary_key}',
        '--columns', 
        'classifier_now_past_past_frozen', 'classifier_now_past_rain', 'classifier_now_delta_surface_temperature',
        'classifier_1h_past_past_frozen', 'classifier_1h_past_rain', 'classifier_1h_delta_surface_temperature',
        'classifier_2h_past_past_frozen', 'classifier_2h_past_rain', 'classifier_2h_delta_surface_temperature',
        '--data',
        f'{past_frozen[0]}', f'{past_rain[0]}', f'{past_delta_surface[0]}',
        f'{past_frozen[1]}', f'{past_rain[1]}', f'{past_delta_surface[1]}',
        f'{past_frozen[2]}', f'{past_rain[2]}', f'{past_delta_surface[2]}',
    )
    try:
        database_iod.main(update_data)
    except:
        pass


    ## Classifier
    #Classifier.py -at 24.4 -wv 0.88 -rh 86.17 -st 25.4 -dst 0.5 -nw rain -pf False -pr True
    input_datas = []

    input_datas.append(( ## 현재
        'Classifier.py',
        '-at', f'{args.input_air_temperature}', #
        '-wv', f'{args.input_wind_velocity}',
        '-rh', f'{args.input_r_humidity}', #
        '-st', f'{args.input_surface_tmp}', #
        '-dst', f'{past_delta_surface[0]}',
        '-nw', f'{args.input_weather}', # 'rain' or 'r' or 'R', 'snow' or 's' or 'S', 이외의 문자열로 표기되는 날씨 상태는 'other' 로 취급됨 #
        '-pf', f'{past_frozen[0]}',
        '-pr', f'{past_rain[0]}',
    ))

    input_datas.append(( ## 미래 (1시간 후 예측치로 대체)
        'Classifier.py',
        '-at', f'{result_1h[1]}', #
        '-wv', f'{result_1h[0]}',
        '-rh', f'{result_1h[2]}', #
        '-st', f'{result_1h[3]}', #
        '-dst', f'{past_delta_surface[1]}',
        '-nw', f'{result_1h[4]}', # 'rain' or 'r' or 'R', 'snow' or 's' or 'S', 이외의 문자열로 표기되는 날씨 상태는 'other' 로 취급됨 #
        '-pf', f'{past_frozen[1]}',
        '-pr', f'{past_rain[1]}',
    ))

    input_datas.append(( ## 미래 (2시간 후 예측치로 대체)
        'Classifier.py',
        '-at', f'{result_2h[1]}', #
        '-wv', f'{result_2h[0]}',
        '-rh', f'{result_2h[2]}', #
        '-st', f'{result_2h[3]}', #
        '-dst', f'{past_delta_surface[2]}',
        '-nw', f'{result_2h[4]}', # 'rain' or 'r' or 'R', 'snow' or 's' or 'S', 이외의 문자열로 표기되는 날씨 상태는 'other' 로 취급됨 #
        '-pf', f'{past_frozen[2]}',
        '-pr', f'{past_rain[2]}',
    ))

    res = []
    for input_data in input_datas:
        state, re = Classifier.main(input_data)
        res.append(state)
    
    update_data = (
        'database_iod.py',
        '-tn', 'UNIONTABLE',
        'update',
        '--pointer', f'{args.primary_key}',
        '--columns', 
        'classifier_now_surface_state', 'classifier_1h_surface_state', 'classifier_2h_surface_state',
        '--data', 
        f'{res[0]}', f'{res[1]}', f'{res[2]}',
    )
    try:
        database_iod.main(update_data)
    except:
        pass
    
    

    if args.img_model_path:
        import img_pridect_tensorrt
        if args.img_data_path:
            imput = (
                'img_pridect_tensorrt.py',
                '-mp', f'{args.img_model_path}', # model
                '-ip', f'{args.img_data_path}', # img data
            )
            _, p_class, max_prob = img_pridect_tensorrt.main(imput)
            update_data = (
                'database_iod.py',
                '-tn', 'UNIONTABLE',
                'update',
                '--pointer', f'{args.primary_key}',
                '--columns', 'img_ai_classifier'
                '--data', f'{p_class}',
            )
            try:
                database_iod.main(update_data)
            except:
                pass

            res.append(p_class)
            return res

        else:
            raise Exception('이미지 파일 경로가 없습니다.')
    
    return res
    



if __name__ =="__main__":
    try:
        main()
        sys.exit(0)


    except Exception as e:
        print(f'{__file__} :\n {e}', file=sys.stderr)
        #traceback.print_exc()
        sys.exit(1)