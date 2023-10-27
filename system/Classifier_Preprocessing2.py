import datetime
import sys
import argparse
from typing import List, Dict

import datatables





def past_states_sum(time: int) -> List:
    ## request_past_frozen() 에서 사용

    now = datetime.datetime.now()
    if time == 0:
        past = (now + datetime.timedelta(minutes=-240)).strftime('%Y%m%d%H%M')
        past_states = datatables.Classifier_q.get_after_data( past )   # 실제값 분류 이력
            
    elif time == 1:
        past = (now + datetime.timedelta(minutes=-180)).strftime('%Y%m%d%H%M')
        real_past_states = datatables.Classifier_q.get_after_data( past )   # 실제값 분류 이력

        past = (now + datetime.timedelta(minutes=-60)).strftime('%Y%m%d%H%M')
        pridict_past_states = datatables.Classifier_q_1h.get_after_data( past )  # 예측치 분류 이력

        past_states = real_past_states + pridict_past_states

    elif time == 2:
        past = (now + datetime.timedelta(minutes=-120)).strftime('%Y%m%d%H%M')
        real_past_states = datatables.Classifier_q.get_after_data( past )   # 실제값 분류 이력

        past = (now + datetime.timedelta(minutes=-120)).strftime('%Y%m%d%H%M')
        pridict_past_states = datatables.Classifier_q_2h.get_after_data( past )  # 예측치 분류 이력

        past_states = real_past_states + pridict_past_states
        
    else:
        raise Exception('입력 시간이 잘못되었습니다.')
    
    return past_states



def state_counts(past_states) -> Dict:
    ## request_past_frozen(), request_past_rain() 에서 사용

    state_count = {}
    for row in past_states:
        char = row[1]
        if char in state_count:
             state_count[char] += 1
        else:
             state_count[char] = 1
    return state_count



def request_past_frozen(beginning: bool, time: int, missing: int = 230) -> tuple:
    ## past_states_sum(), request_past_frozen()

    '''
    과거에 빙결 판정 이력이 존재하는지 판단

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

    if beginning: # 초기 가동
        past_states = past_states_sum(time)
        state_count = state_counts(past_states)
        
        if state_count['F'] > 0: #빙결 이력 존재
            return (True ,[item[1] for item in past_states])
        else: #빙결 이력 부재
            return (False ,[item[1] for item in past_states])
        
    else: # 일반 가동
        past_states = past_states_sum(time)
        state_count = state_counts(past_states)

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
    





def request_past_rain(time: int) -> bool:
    ## state_counts() 사용
    '''
    과거에 강수 이력이 존재하는지 판단

    초기 가동의 경우(3시간 이전 가동 이력이 없거나 가동한지 3시간이 되지 못한 경우)에는
    디바이스의 날씨 기록이 없거나 모자라므로 기상청 데이터를 조회하여 결측치를 보정후 3시간 이내에 강수여부를 리턴

    일반 가동의 경우에도 기상청 데이터로 결측치를 보정 후 3시간 이내에 강수여부를 리턴

    현재로부터 3시간 이전의 강수 판단 -> (디바이스에 기록된 날씨3h + 기상청에서 로드한 날씨3h) 결측치 보정
    1시간후 미래로부터 3시간 이전의 강수 판단 -> (디바이스에 기록된 날씨2h + 기상청에서 로드한 날씨2h) 결측치 보정 + 일기예보1시간치
    2시간후 미래로부터 3시간 이전의 강수 판단 -> (디바이스에 기록된 날씨2h + 기상청에서 로드한 날씨2h) 결측치 보정 + 일기예보2시간치
    '''
 
    now = datetime.datetime.now().strftime('%Y%m%d%H%M')

    if time == 0: # 현재로부터 3시간 이전
        past = (now + datetime.timedelta(minutes=-180)).strftime('%Y%m%d%H%M') #기록된 날씨3시간
        past_weathers = datatables.weather_q.get_after_data(past)
        weather_count = state_counts(past_weathers)

        if weather_count['R'] > 0: #강우 이력 존재
            return True
        else:
            return False

    elif time == 1: # 1시간 미래로부터 3시간 이전
        past = (now + datetime.timedelta(minutes=-120)).strftime('%Y%m%d%H%M') #기록된 날씨2시간
        past_weathers = datatables.Weather.get_after_weather( past )

        past = (now + datetime.timedelta(minutes=-60)).strftime('%Y%m%d%H%M') #예측된 날씨1시간
        pridict_weathers = datatables.AIdata_1h.get_after_weather( past )

        weathers = past_weathers + pridict_weathers
        weather_count = state_counts(weathers)
        
        if weather_count['R'] > 0: #강우 이력 존재
            return True
        else:
            return False

    elif time == 2: # 2시간 미래로부터 3시간 이전
        past = (now + datetime.timedelta(minutes=-60)).strftime('%Y%m%d%H%M') #기록된 날씨1시간
        past_weathers = datatables.Weather.get_after_weather(past)

        past = (now + datetime.timedelta(minutes=-120)).strftime('%Y%m%d%H%M') #예측된 날씨2시간
        pridict_weathers = datatables.AIdata_2h.get_after_weather( past )

        weathers = past_weathers + pridict_weathers
        weather_count = state_counts(weathers)

        if weather_count['R'] > 0: #강우 이력 존재
            return True
        else:
            return False
    else:
        raise Exception('입력 시간이 잘못되었습니다.')



def request_delta_surface_temperature(time: int, channel: int) -> bool:
    ## 시간당 노면온도 변화량
    '''

    현재 시간당 노면온도 변화량 -> (현재 노면온도 - 1시간 전 노면온도)
    1시간 후의 시간당 노면온도 변화량 -> (미래 노면온도 예측(1h) - 현재 노면온도)
    2시간 후의 시간당 노면온도 변화량 -> (미래 노면온도 예측(2h) - 미래 노면온도 예측(1h))

    '''
    now = datetime.datetime.now().strftime('%Y%m%d%H%M')
    past = (now + datetime.timedelta(minutes=-60)).strftime('%Y%m%d%H%M')

    if time == 0:
        past_surface_temperature = datatables.Surface.get_surface_one(past)[channel-1]
        now_surface_temperature = datatables.Surface.get_surface_one(now)[channel-1]

        if past_surface_temperature == [] or now_surface_temperature == []:
            raise Exception(f'{time}시간 전({past}) 데이터베이스 데이터 또는 현재({now}) 데이터가 존재하지 않습니다.')
        
        return now_surface_temperature - past_surface_temperature
    
    elif time == 1:
        now_surface_temperature = datatables.Surface.get_surface_one(now)[channel-1]
        future_surface_temperature_1h = datatables.AIdata_1h.get_surface_one(now)

        if future_surface_temperature_1h == [] or now_surface_temperature == []:
            future = (now + datetime.timedelta(minutes=60)).strftime('%Y%m%d%H%M')
            raise Exception(f'{time}시간 후({future}) 데이터베이스 데이터 또는 현재({now}) 데이터가 존재하지 않습니다.')
        
        return future_surface_temperature_1h - now_surface_temperature
    
    elif time == 2: 
        future_surface_temperature_1h = datatables.AIdata_1h.get_surface_one(now)
        future_surface_temperature_2h = datatables.AIdata_2h.get_surface_one(now)

        if future_surface_temperature_1h == [] or future_surface_temperature_2h == []:
            future = (now + datetime.timedelta(minutes=60)).strftime('%Y%m%d%H%M')
            future2 = (now + datetime.timedelta(minutes=120)).strftime('%Y%m%d%H%M')
            raise Exception(f'{time}시간 후({future}) 또는 {time-1}시간 후({future2})의 데이터가 데이터베이스에 존재하지 않습니다.')
        
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
        parser.add_argument('-t', '--time_hour', type=int, required=True, default=0)

        # 보조인자(메인 인자와 조합)
        parser.add_argument('-b', '--beginning_run', action='store_true', default=False) #초기 가동 여부
        parser.add_argument('-m', '--miss', type=int, default=0) #결측치 허용 정도(최대는 240이고 여기에서 허용할 만큼의 수를 빼서 입력)
        parser.add_argument('-c', '--channel', type=int, required=True, default=1) # 노면온도 로거의 채널 지정

        args = parser.parse_args()

 
        if args.request_past_frozen:
            if args.time_hour:
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
            if args.time_hour:
                print( *request_past_rain(beginning = args.beginning_run, time = args.time_hour) )
                sys.exit(0)
            else:
                raise Exception('판단 대상 시간을 입력해 주십시오')
            
        if args.request_delta_surface_temperature:
            if args.time_hour:
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