import math
import datetime
import sys
import argparse


class Classifier:

    def __init__(
        self,
        air_temperature: float,
        wind_velocity: float,
        r_humidity: float,
        surface_temperature: float,
        delta_surface_temperature: float,
        #water_film: float,
        now_weather: str,
        past_frozen: bool,
        past_rain: bool
    ):

        # From EnvSensor, GroundSensor
        self.air_temperature = air_temperature
        self.wind_velocity = wind_velocity
        self.r_humidity = r_humidity
        self.surface_temperature = surface_temperature

        # From Coculated
        self.dewpoint = self.coculate_dewpoint()

        # From API or EnvSensor Data
        self.now_weather = now_weather

        # From Past record (required preprocessing)
        self.delta_surface_temperature = delta_surface_temperature
        #self.water_film = water_film
        self.past_frozen = past_frozen
        self.past_rain = past_rain





    def coculate_dewpoint(self) -> float:
        ##### 이슬점 근사치를 계산한다. 
        ## 입력 : 온도, 습도
        ## 출력 : 이슬점 온도
    
        ## 상수 ## 
        b = 17.62
        c = 243.12

        gamma = ( b * self.air_temperature / ( c + self.air_temperature ) ) + math.log( self.r_humidity / 100.0 )
        dewpoint = ( c * gamma ) / ( b - gamma )

        return dewpoint



    def road_congelation(self) -> int:
        ##응결에 의한 결빙
        ## 입력 : 습도, 노면온도, 대기온도, 시간당 노면온도 변화량
        ## 출력 : 0 = 건조, 1 = 습윤, 2 = 빙결

        input = f'상대습도: {self.r_humidity}, 노면온도: {self.surface_temperature}, 대기온도: {self.air_temperature}, 습도: {self.dewpoint} ,노면온도 변화(1시간) : {self.delta_surface_temperature}'
        #print(input)


        if self.r_humidity < 65.0 : 
            #습도 65% 미만일 경우 건조
            return 0

        if self.surface_temperature > self.dewpoint + 5: 
            #습도 65% 이상이나 노면온도가 이슬점 + 5 도 보다 높을 경우 건조
            return 0

        if self.surface_temperature > self.air_temperature : 
            # 습도가 65% 이상이고 노면온도가 이슬점 + 5도 보다 낮지만, 대기 온도보다 높다면 건조
            return 0

        if self.air_temperature > 5 :
            # 습도가 65% 이상, 노면온도가 (이슬점온도 + 5도) 보다 낮음,
            # 이때 대기온도가 5도보다 크면 습윤
            return 1

        if self.surface_temperature <= 0 :
            # 습도가 65% 이상, 노면온도가 (이슬점온도 + 5도) 보다 낮음,
            # 이때 대기온도가 5도보다 작은 경우, 노면온도가 0도 이하이면 빙결
            return 2

        else:
            # 습도가 65% 이상, 노면온도가 (이슬점온도 + 5도) 보다 낮음,
            # 이때 대기온도가 5도보다 작지만 0도보다는 클 때
            if self.surface_temperature <= 1 :
                # 노면온도가 1도 이하일 경우
                if self.delta_surface_temperature <= -1 : 
                    #시간당 노면온도 변화량이 -1 도 이하일 경우 ( 1시간에 1도 이상 낮아진다면) 빙결
                    return 2
                else:
                    #시간당 노면온도 변화량이 -1 도 이상일 경우 습윤
                    return 1
            else :
                # 노면온도가 1도 초과일 경우 습윤
                return 1



    def road_precipitation(self) -> int:
        ##강수에 의한 결빙
        ## 입력 : 강수량, 강수 후3시간 이내 대기온도, 강수 후 3시간이내 노면온도
        ## 출력 : 0 = 건조, 1 = 습윤, 2 = 빙결
        
        inp = f'현재 날씨: {self.now_weather}, 3시간 이내 강수 여부: {self.past_rain}, 대기온도: {self.air_temperature}, 노면온도: {self.surface_temperature}'
        #print(inp)

        if self.now_weather == 'rain' or self.now_weather == 'r' or self.now_weather == 'R': # 현재 비가 내리는 경우
            if self.air_temperature <= 0 and self.surface_temperature <= 0 : #노면온도와 대기온도가 0도 이하일 경우 빙결
                return 2
            else:
                return 1 #노면온도와 대기온도 중 하나가 0도 초과일 경우 습윤
            
        else: # 현재는 비가 안 올 경우
            if self.past_rain: #과거에 비가 온 적 있는지?(3시간 이전)
                if self.air_temperature <= 0 and self.surface_temperature <= 0 : #노면온도와 대기온도가 0도 이하일 경우 빙결
                    return 2
                else:
                    return 1 #노면온도와 대기온도 중 하나가 0도 초과일 경우 습윤
        return 0

    

    ###### 현재 사용하지 않음. ######
    def road_water_film(self) -> int:
        ##수막에 의한 결빙
        ## 입력 : 수막두께, 노면온도
        ## 출력 : 2 = 빙결, 3 = 빙결이 아니지만 상태를 모름
        
        inp = f'수막 두께: {self.water_film}, 노면온도: {self.surface_temperature}'
        #print(inp)

        if(self.water_film >= 1 and self.surface_temperature <= 0):
            #print('수막두께 >= 1mm && 노면온도 <= 0  ▶ 빙결')
            return 2
        else:
            #print('빙결이 아니지만 상태 알 수 없음.')
            return 3
        
        

    def road_snow(self) -> int:
        ##강설에 의한 결빙
        ## 입력 : 강설여부
        ## 출력 : 2 = 빙결, 3 = 빙결이 아니지만 상태를 모름

        if self.now_weather == 'snow' or self.now_weather == 's' or self.now_weather == 'S':  #강설일 경우 빙결
            inp = f'강설여부: True'
            #print(inp)
            return 2
        else:
            inp = f'강설여부: False'
            #print(inp)
            return 3



    def road_keep_frozen(self) -> int:
        ##빙결 유지
        ## 입력 : 4시간 이내 결빙여부, 노면온도, 대기온도
        ## 출력 : 2 = 빙결, 3 = 빙결이 아니지만 상태를 모름
        
        inp = f'4시간 이내 빙결상태 존재 여부: {self.past_frozen}, 노면온도: {self.surface_temperature}, 대기온도: {self.air_temperature}'
        #print(inp)

        if self.past_frozen : # 4시간 전에 빙결상태가 있는 경우
            if self.surface_temperature <= 0 or self.air_temperature <= 0: #노면온도 또는 대기온도가 0도 이하일 경우 빙결
                return 2
            else:
                return 3
        else:
            return 3



    def road_wind(self) -> int:
        ##풍속에 의한 결빙
        ## 입력 : 노면온도, 이슬점, 풍속
        ## 출력 : 0 = 건조, 1 = 습윤, 2 = 빙결

        inp = f'노면온도: {self.surface_temperature}, 이슬점: {self.dewpoint}, 풍속: {self.wind_velocity}'
        #print(inp)

        if self.surface_temperature > 0 : #노면온도가 0도 초과일 경우 건조
            return 0
        
        else: # 노면온도 0도 이하
            if ( (self.dewpoint - self.surface_temperature) < 0.5 ) :
                #노면온도가 0도 이하인 상태에서, (이슬점 - 노면온도) 가 0.5도 미만이면 건조
                return 0
            else: #이슬점과 노면온도의 차이가 0.5도 이상일 경우
                if self.wind_velocity > 2: # 풍속이 2m/s 보다 크면 빙결
                    return 2
                else:
                    return 1 # 풍속이 2m/s 보다 작으면 습윤 


def str_to_bool(value: str ) -> bool:
    if value.lower() in ('true', 'True', 'T', 't', '1'):
        return True
    elif value.lower() in ('False', 'false', 'F', 'f', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('잘못된 bool 값입니다. True 또는 False를 입력하세요.')


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()

        # Normal Data
        parser.add_argument('-at', '--air_temperature', type=float, required=True)
        parser.add_argument('-wv', '--wind_velocity', type=float, required=True)
        parser.add_argument('-rh', '--r_humidity', type=float, required=True)
        parser.add_argument('-st', '--surface_temperature', type=float, required=True)

        # API Data or Normal(EnvSensor) Data
        parser.add_argument('-nw', '--now_weather', type=str, required=True)

        # Coculated Data
        parser.add_argument('-dst', '--delta_surface_temperature', type=float, required=True)
        parser.add_argument('-pf', '--past_frozen', type=str_to_bool, required=True)
        parser.add_argument('-pr', '--past_rain', type=str_to_bool, required=True)

        args = parser.parse_args()

        pridict = Classifier(
            air_temperature = args.air_temperature,
            wind_velocity = args.wind_velocity,
            r_humidity = args.r_humidity,
            surface_temperature = args.surface_temperature,
            delta_surface_temperature = args.delta_surface_temperature,
            now_weather = args.now_weather,
            past_frozen = args.past_frozen,
            past_rain = args.past_rain
        )

        re = [
            pridict.road_congelation(),#응결
            pridict.road_precipitation(),#강수
            #pridict.road_water_film(),#수막
            pridict.road_snow(),#강설
            pridict.road_keep_frozen(),#빙결 유지
            pridict.road_wind()#풍속
        ]

        if re.count(2) > 0: #빙결 상태 1개 이상 감지 시
            state = 'F'
            print(datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'), state, *re, file=sys.stdout)
            sys.exit(0)
        if re.count(1) > 0: #빙결 상태가 없고 습윤 상태가 1개 이상 감지 시
            state = 'W' 
            print(datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'), state, *re, file=sys.stdout)
            sys.exit(0)
        
        #빙결 상태, 습윤 상태가 모두 없을 시
        state = 'D'
        print(datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'), state, *re, file=sys.stdout)
        sys.exit(0)


    # 에러 발생 시 출력하고 종료
    except Exception as e:
        print(f'{__file__} :\n {e}', file=sys.stderr)
        sys.exit(1)


## test
# python Classifier.py -at 24.4 -wv 0.88 -rh 86.17 -st 25.4 -dst 0.5 -nw rain -pf False -pr True  // return 0
# python Classifier.py -at 24.4 -wv 0.88 -rh 86.17 -dst 0.5 -nw rain -pf False -pr True           // return 1 (err)
# python Classifier.py -at 24.4 -wv 0.88 -rh 86.17 -st 25.4 -dst 0.5 -nw rain -pf 0 -pr 1         // return 0

# ./Classifier -at 24.4 -wv 0.88 -rh 86.17 -st 25.4 -dst 0.5 -nw rain -pf False -pr True  // return 0
# ./Classifier -at 24.4 -wv 0.88 -rh 86.17 -dst 0.5 -nw rain -pf False -pr True           // return 1 (err)
# ./Classifier -at 24.4 -wv 0.88 -rh 86.17 -st 25.4 -dst 0.5 -nw rain -pf 0 -pr 1         // return 0