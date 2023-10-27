import datetime
import sys
import argparse
from typing import List, Dict, Any

import datatables
from _utils import form_check




def tables_range_select(
    table_1: Any = None,
    table_2: Any = None,
    start_f: str = 'datime_1',
    start_b: str = 'datime_2',
    end: str = 'datime_3'
):

    if (table_1 == None) or (table_1 == None and table_2 == None):
        raise Exception('테이블을 1개 이상 지정하십시오')
    
    elif (table_1 != None) and (table_2 == None):
        form_check(start_f)
        form_check(end)

        datatables.global_database.connect()
        query = table_1.select().where((table_1.daytime >= start_f) & (table_1.daytime < end)).order_by(table_1.daytime)
        datatables.global_database.close()
        return query
    
    elif (table_1 != None) and (table_2 != None):
        form_check(start_f)
        form_check(start_b)
        form_check(end)
        
        datatables.global_database.connect()
        query_front = table_1.select().where((table_1.daytime >= start_f) & (table_1.daytime < end)).order_by(table_1.daytime)
        query_back = table_2.select().where((table_2.daytime >= start_b) & (table_2.daytime < end)).order_by(table_2.daytime)
        datatables.global_database.close()
        return query_front + query_back
    
    else:
        print('정의되지 않은 동작 발생')
        pass




def query_parse(
    query,
    target_field_1: str,
    target_field_2: str = None
) -> List:
    '''
    입력받은 데이터에서 시간과 지정한 컬럼1개만 선택함
    '''
    result_list = []
    if target_field_2 == None:
        for row in query:
            result_list.append([row.daytime, getattr(row, target_field_1)])
    else:
        for row in query:
            try:
                result_list.append([row.daytime, getattr(row, target_field_1)])
            except:
                #AttributeError:
                result_list.append([row.daytime, getattr(row, target_field_2)])

    return result_list



def road_state_classifier_logs(
    time: int,
    real_classifier_table: str = 'Classifier_now',
    predict_classifier_table_1h: str = 'Classifier_1h',
    predict_classifier_table_2h: str = 'Classifier_2h'
) -> List:

    '''
    ## 도로 노면 상태 분류 이력(노면상태 분류 알고리즘의 출력)을 불러온다.

    '''

    #datatable_models = get_models(datatables)
    real_table = getattr(datatables, real_classifier_table)
    if time == 1:
        predict_table = getattr(datatables, predict_classifier_table_1h)
    elif time == 2:
        predict_table = getattr(datatables, predict_classifier_table_2h)


    now = datetime.datetime.now()
    full_times = -240
    if time == 0:
        start = (now + datetime.timedelta(minutes=full_times)).strftime('%Y%m%d%H%M')
        end = now.strftime('%Y%m%d%H%M')
        query = tables_range_select(table_1=real_table, start_f=start, end=end)
        return query_parse(query=query, target_field_1='surface_state')
            
    elif time <= 2:
        d = full_times + time * 60
        d2 = -1*(time*60)
        # if time == 1 -> d == -180
        # if time == 2 -> d == -120
        start_f = (now + datetime.timedelta(minutes= d)).strftime('%Y%m%d%H%M')
        start_b = (now + datetime.timedelta(minutes= d2)).strftime('%Y%m%d%H%M')
        end = now.strftime('%Y%m%d%H%M')
        query = tables_range_select(table_1=real_table, table_2=predict_table, start_f=start_f, start_b=start_b,end=end)

        return query_parse(query=query, target_field_1='surface_state')
        
    else:
        raise Exception('입력 시간이 잘못되었습니다.')
    



def state_counts(past_states) -> Dict:
    state_count = {}
    for row in past_states:
        char = row[1]
        if char in state_count:
             state_count[char] += 1
        else:
             state_count[char] = 1
    return state_count



def request_past_frozen(
    beginning: bool, 
    time: int, 
    missing: int = 230
) -> tuple:

    '''
    ## 과거에 빙결 판정 이력이 존재하는지 판단

    1. 초기 가동
    초기 가동의 경우(4시간 이전 가동 이력이 없거나 가동한지 4시간이 되지 못한 경우)에는
    과거 빙결 판정 기록이 4시간이 되지 못하므로 존재하는 기록만으로 과거 빙결 판정 이력의 유무를 리턴,
    경우의 수는 다음과 같다.
    현재 상태 분류 -> 4시간 전까지의 실제 분류 기록
    1시간 후 미래 상태 분류 -> 3시간 전까지의 실제 분류 기록 / 1시간 후까지의 예측 분류 기록
    2시간 후 미래 상태 분류 -> 2시간 전까지의 실제 분류 기록 / 2시간 후까지의 예측 분류 기록

    2. 일반 가동
    일반적인 경우 4시간 이전 가동수치를 조회하게 되며 경우의 수는 다음과 같다.
    현재 상태 분류 -> 4시간 전까지의 실제 분류 기록
    1시간 후 미래 상태 분류 -> 3시간 전까지의 실제 분류 기록 / 1시간 후까지의 예측 분류 기록
    2시간 후 미래 상태 분류 -> 2시간 전까지의 실제 분류 기록 / 2시간 후까지의 예측 분류 기록
    
    '''
    past_states = road_state_classifier_logs(time)
    state_count = state_counts(past_states)

    if beginning: # 초기 가동
        states = [item[1] for item in past_states]
        if state_count['F'] > 0: #빙결 이력 존재
            return (True, states)
        else: #빙결 이력 부재
            return (False, states)
        
    else: # 일반 가동
        if state_count['F'] > 0: #빙결 이력 존재
            if len(past_states) <= missing: # 과거 이력에 결측치가 일정이상 존재함
                return (True, [item[1] for item in past_states])
            
            else: # 과거 이력에 결측치가 일정 이하로 존재함
                return (True, len(past_states))
            
        else: #빙결 이력 부재
            if len(past_states) <= missing: # 과거 이력에 결측치가 일정이상 존재함
                return (False, [item[1] for item in past_states])
            
            else: # 과거 이력에 결측치가 일정 이하로 존재함
                return (False, len(past_states))
    





def request_past_rain(
    time: int,
    real_weather_table: str = 'Weather',
    predict_weather_table_1h: str = 'AIdata_1h',
    predict_weather_table_2h: str = 'AIdata_2h'
) -> bool:
    '''
    ## 과거에 강수 이력이 존재하는지 판단

    초기 가동의 경우(3시간 이전 가동 이력이 없거나 가동한지 3시간이 되지 못한 경우)에는
    디바이스의 날씨 기록이 없거나 모자라므로 기상청 데이터를 조회하여 결측치를 보정후 3시간 이내에 강수여부를 리턴

    일반 가동의 경우에도 기상청 데이터로 결측치를 보정 후 3시간 이내에 강수여부를 리턴

    현재로부터 3시간 이전의 강수 판단 -> (디바이스에 기록된 날씨3h + 기상청에서 로드한 날씨3h) 결측치 보정
    1시간후 미래로부터 3시간 이전의 강수 판단 -> (디바이스에 기록된 날씨2h + 기상청에서 로드한 날씨2h) 결측치 보정 + 일기예보1시간치
    2시간후 미래로부터 3시간 이전의 강수 판단 -> (디바이스에 기록된 날씨2h + 기상청에서 로드한 날씨2h) 결측치 보정 + 일기예보2시간치
    '''

    #datatable_models = get_models(datatables)
    real_table = getattr(datatables, real_weather_table)
    if time == 1:
        predict_table = getattr(datatables, predict_weather_table_1h)
    elif time == 2:
        predict_table = getattr(datatables, predict_weather_table_2h)
 
    now = datetime.datetime.now()
    full_times = -180

    if time == 0: # 현재로부터 3시간 이전
        start = (now + datetime.timedelta(minutes=full_times)).strftime('%Y%m%d%H%M') #기록된 날씨3시간
        end = now.strftime('%Y%m%d%H%M')

        query = tables_range_select(table_1=real_table, start_f=start, end=end)
        past_weathers = query_parse(query=query, target_field_1='weather')
        weather_count = state_counts(past_weathers)

        if weather_count['R'] > 0: #강우 이력 존재
            return True
        else:
            return False

    elif time <= 2: # 1시간 미래로부터 3시간 이전 또는 2시간 미래로부터 3시간 이전

        d = full_times + time * 60
        d2 = -1*(time*60)
        # if time == 1 -> d == -120
        # if time == 2 -> d == -60
        start_f = (now + datetime.timedelta(minutes= d)).strftime('%Y%m%d%H%M')
        start_b = (now + datetime.timedelta(minutes= d2)).strftime('%Y%m%d%H%M')
        end = now.strftime('%Y%m%d%H%M')
        query = tables_range_select(table_1=real_table, table_2=predict_table, start_f=start_f, start_b=start_b,end=end)
        weathers = query_parse(query=query, target_field_1='weather', target_field_2='out_weather')
        weather_count = state_counts(weathers)
        
        if weather_count['R'] > 0: #강우 이력 존재
            return True
        else:
            return False
        
    else:
        raise Exception('입력 시간이 잘못되었습니다.')






def _extract_temperature(temperature_list):
    '''
    temperature_list 의 형태 예시
    [['202307280012', 23.74],
     ['202307280012', 23.74],
     ['202307280012', 23.74],
     ['202307280012', 23.74]]
    '''
    results = []
    for i in temperature_list:
        results.append(float(i[1]))
    return results


def _get_surface_temperatures(
    time: int,
    time_range: int,
    table_1: Any,
    table_2: Any,
    target_field_1: str,
    target_field_2: str
):
    '''
    먼저 들어간 테이블 데이터가 리턴 데이터의 앞에 위치하는 것을 유의.
    '''

    ## time coculate
    now = datetime.datetime.now()
    now_f = (now + datetime.timedelta(minutes= -time_range)).strftime('%Y%m%d%H%M')
    now = now.strftime('%Y%m%d%H%M')

    ## get temperature datas and parse
    surface_temperatures_1 = tables_range_select(table_1=table_1, start_f=now_f, end=now)
    surface_temperatures_1 = query_parse(query=surface_temperatures_1, target_field_1=target_field_1)
    surface_temperatures_1 = _extract_temperature(surface_temperatures_1)

    surface_temperatures_2 = tables_range_select(table_1=table_2, start_f=now_f, end=now)
    surface_temperatures_2 = query_parse(query=surface_temperatures_2, target_field_1=target_field_2)
    surface_temperatures_2 = _extract_temperature(surface_temperatures_2)

    if time == 1:
        if surface_temperatures_1 == [] or surface_temperatures_2 == []:
            future = (now + datetime.timedelta(minutes=60)).strftime('%Y%m%d%H%M')
            raise Exception(f'{time}시간 후({future}) 데이터베이스 데이터 또는 현재({now}) 데이터가 존재하지 않습니다.')
    elif time == 2:
        if surface_temperatures_1 == [] or surface_temperatures_2 == []:
            future = (now + datetime.timedelta(minutes=60)).strftime('%Y%m%d%H%M')
            future2 = (now + datetime.timedelta(minutes=120)).strftime('%Y%m%d%H%M')
            raise Exception(f'{time}시간 후({future}) 또는 {time-1}시간 후({future2})의 데이터가 데이터베이스에 존재하지 않습니다.')
    
    surface_temperature_1 = surface_temperatures_1[len(surface_temperatures_1)-1] #가장 최근값
    surface_temperature_2 = surface_temperatures_2[len(surface_temperatures_2)-1] #가장 최근값
    
    return surface_temperature_1, surface_temperature_2


def request_delta_surface_temperature(
    time: int,
    time_window: bool = False,
    channel: int = 1,
    real_surface_table: str = 'Surface',
    predict_surface_table_1h: str = 'AIdata_1h',
    predict_surface_table_2h: str = 'AIdata_2h'
) -> float:
    '''
    ## 시간당 노면온도 변화량
    현재 시간당 노면온도 변화량 -> (현재 노면온도 - 1시간 전 노면온도)
    1시간 후의 시간당 노면온도 변화량 -> (미래 노면온도 예측(1h) - 현재 노면온도)
    2시간 후의 시간당 노면온도 변화량 -> (미래 노면온도 예측(2h) - 미래 노면온도 예측(1h))

    해당 시각의 데이터가 결측일 경우에 대비하여, 해당 시간 기준으로 +-1분 또는 +-2분을 범위로
    데이터를 조회한다. 이 범위는 time_window 로 입력받도록 하며 False 일 경우 +-1분을 범위로 한다.

    '''

    #datatable_models = get_models(datatables)
    real_table = getattr(datatables, real_surface_table)

    if time_window:
        time_range = 2
    else:
        time_range = 1

    if time == 0:
        ## time coculate
        now = datetime.datetime.now()
        hour = -60
        past_f = (now + datetime.timedelta(minutes= (hour-time_range) )).strftime('%Y%m%d%H%M')
        past = (now + datetime.timedelta(minutes=hour)).strftime('%Y%m%d%H%M')
        past_b = (now + datetime.timedelta(minutes= (hour+time_range) )).strftime('%Y%m%d%H%M')

        now_f = (now + datetime.timedelta(minutes= -time_range)).strftime('%Y%m%d%H%M')
        now = now.strftime('%Y%m%d%H%M')

        ## get temperature datas and parse
        past_surface_temperatures = tables_range_select(table_1=real_table, start_f=past_f, end=past_b)
        past_surface_temperatures = query_parse(query=past_surface_temperatures, target_field_1=f'surface_ch{channel}')
        past_surface_temperatures =_extract_temperature(past_surface_temperatures)

        now_surface_temperatures = tables_range_select(table_1=real_table, start_f=now_f, end=now)
        now_surface_temperatures = query_parse(query= now_surface_temperatures, target_field_1=f'surface_ch{channel}')
        now_surface_temperatures =_extract_temperature(now_surface_temperatures)

        if past_surface_temperatures == [] or now_surface_temperatures == []:
            raise Exception(f'{time}시간 전({past}) 데이터베이스 데이터 또는 현재({now}) 데이터가 존재하지 않습니다.')
        
        if time_window: #5
            if len(past_surface_temperatures) <= time_range * 2:
                past_surface_temperature = sum(past_surface_temperatures)/len(past_surface_temperatures)
            else:
                past_surface_temperature = past_surface_temperatures[2] # == past
            now_surface_temperature = now_surface_temperatures[len(now_surface_temperatures)-1] #가장 최근값

        else: #3
            if len(past_surface_temperatures) <= time_range * 2:
                past_surface_temperature = sum(past_surface_temperatures)/len(past_surface_temperatures)
            else:
                past_surface_temperature = past_surface_temperatures[1] # == past
            now_surface_temperature = now_surface_temperatures[len(now_surface_temperatures)-1] #가장 최근값
        
        return now_surface_temperature - past_surface_temperature
    

    elif time == 1:
        predict_table = getattr(datatables, predict_surface_table_1h)
        future_surface_temperature_1h, now_surface_temperature = _get_surface_temperatures(
            time = time,
            time_range = time_range,
            table_1 = predict_table,
            table_2 = real_table, 
            target_field_1 = f'surface_ch{channel}',
            target_field_2 = 'out_surface_temperature'
        )
        return future_surface_temperature_1h - now_surface_temperature
    

    elif time == 2:
        predict_table_1 = getattr(datatables, predict_surface_table_1h)
        predict_table_2 = getattr(datatables, predict_surface_table_2h)
        future_surface_temperature_2h, future_surface_temperature_1h = _get_surface_temperatures(
            time = time,
            time_range = time_range,
            table_1 = predict_table_2,
            table_2 = predict_table_1, 
            target_field_1 = 'out_surface_temperature',
            target_field_2 = 'out_surface_temperature'
        )
        return future_surface_temperature_2h - future_surface_temperature_1h

    else:
        raise Exception('입력 시간이 잘못되었습니다.')



if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()

        # 메인 인자
        parser.add_argument('-rpf', '--request_past_frozen', action='store_true', default=False)
        parser.add_argument('-rpr', '--request_past_rain', action='store_true', default=False)
        parser.add_argument('-rdst', '--request_delta_surface_temperature', action='store_true', default=False)

        # 필수 인자(메인 인자와 조합)
        parser.add_argument('-t', '--time_hour', type=int, required=True, default=None)

        # 보조인자(메인 인자와 조합)
        parser.add_argument('-b', '--beginning_run', action='store_true', default=False) #초기 가동 여부
        parser.add_argument('-m', '--miss', type=int, default=0) #결측치 허용 정도(최대는 240이고 여기에서 허용할 만큼의 수를 빼서 입력)
        parser.add_argument('-c', '--channel', type=int, default=1) # 노면온도 로거의 채널 지정

        args = parser.parse_args()

 
        if args.request_past_frozen:
            if args.time_hour != None:
                if args.miss:
                    if args.miss < 0 or args.miss >= 240:
                        raise Exception('결측치 허용 범위가 잘못 입력되었습니다. 1~239 범위의 정수를 입력해 주십시오')
                    print( *request_past_frozen(beginning = args.beginning_run, time = args.time_hour, missing = args.miss) )
                else:
                    print( *request_past_frozen(beginning = args.beginning_run, time = args.time_hour) )
                sys.exit(0)
            else:
                raise Exception('판단 대상 시간을 입력해 주십시오')
        
        if args.request_past_rain:
            if args.time_hour != None:
                print( *request_past_rain(beginning = args.beginning_run, time = args.time_hour) )
                sys.exit(0)
            else:
                raise Exception('판단 대상 시간을 입력해 주십시오')
            
        if args.request_delta_surface_temperature:
            if args.time_hour != None:
                if args.miss < 0 or args.miss >= 19:
                    raise Exception('존재하지 않는 채널입니다')
                print( *request_delta_surface_temperature(time = args.time_hour, channel = args.channel) )
                sys.exit(0)
            else:
                raise Exception('판단 대상 시간을 입력해 주십시오')

    # 에러 발생 시 출력하고 종료
    except Exception as e:
        print(f'{e}', file=sys.stderr)
        sys.exit(1)