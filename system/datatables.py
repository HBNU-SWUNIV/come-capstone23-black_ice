from peewee import *
from typing import List
import sys
import argparse


# PostgreSQL 데이터베이스에 연결
global_database = PostgresqlDatabase('postgres', user='postgres', password='0425', host='localhost', port=5432)



class BaseModel(Model):
    class Meta:
        database = global_database
    
    '''
    공통 동작 정의 클래스

    @classmethod 표기가 붙으면 클래스 메서드가 됨 
    클래스 메서드는 첫번째 인자인 cls 매개변수로 클래스 자체에 접근이 가능함
    클래스 메서드의 형태는 다음과 같음

    @classmethod
    def func(cls, 인자1, 인자2, ...):
        ...
        return 0
    '''
    
    @classmethod
    def print_table_schema(cls):
        '''
        테이블 이름과 스키마 조회
        '''
        fields = cls._meta.fields
        print(f"Table : {cls.__name__} / ", f"schema({cls.__name__}):")
        print()
        for key, value in fields.items():
            #print(f'{fields[i].key} :{fields[i].value}')
            print(f'    {key} : {value}')
        print()
        print()


## API 데이터
class APIPridict(BaseModel):
    daytime = CharField(max_length=12, null=False) ##일기 예보 로드 기준 시간
    target_daytime = CharField(max_length=12, null=False) ##기준 시간으로부터 지난 시간(예측 대상 시간)

    #stn = CharField(max_length=3, null=False)

    air_temperature = DecimalField(decimal_places=1, max_digits=4, null=True, default=None) #1시간 기온 ˚C
    wind_velocity_ew = DecimalField(decimal_places=1, max_digits=4, null=True, default=None) #풍속(동서 성분) m/s
    wind_velocity_sn = DecimalField(decimal_places=1, max_digits=4, null=True, default=None) #풍속(남북 성분) m/s
    wind_direction = IntegerField(constraints=[Check('wind_direction >= 0 AND wind_direction <= 360')], null=True, default=None) #풍향 deg
    wind_velocity = DecimalField(decimal_places=1, max_digits=4, null=True, default=None) #풍속 m/s
    sky = IntegerField(constraints=[Check('sky >= 0 AND sky <= 100')], null=True, default=None) #하늘 상태(날씨) 코드값
    rain = IntegerField(null=True, default=None) #강수형태 코드값
    rain_probability = IntegerField(constraints=[Check('rain_probability >= 0 AND rain_probability <= 100')], null=True, default=None) #강수확률 %
    wave = IntegerField(null=True, default=None) #파고 M, 사용 안함
    rain_hour = DecimalField(decimal_places=1, max_digits=4, null=True, default=None) #1시간 강수량(1mm)
    r_humidity = IntegerField(constraints=[Check('r_humidity >= 0 AND r_humidity <= 100')], null=True, default=None) #습도 %
    snow_hour = DecimalField(decimal_places=1, max_digits=4, null=True, default=None) #1시간 신적설(1cm)
    
    x_grid = IntegerField(null=False) #예보 구역 격자 구간 좌표(x)
    y_grid = IntegerField(null=False) #예보 구역 격자 구간 좌표(y)

    class Meta:
        database = global_database


    def get_target_daytime5(cls, target_time: str) -> List:
        '''
        특정 시간 이후의 가장 최근 데이터5개를 조회해 리턴, 일반적인 경우 현재시간으로부터 가장 최근이 됨
        '''
        query = cls.select().where( cls.target_daytime >= target_time).order_by(cls.target_daytime.desc()).limit(5)

        result_list = []
        for row in query:
            result_list.append([row.daytime, row.target_daytime, row.stn, row.air_temperture, row.wind_direction, row.wind_velocity, row.sky, row.rain, row.rain_probability, row.rain_hour, row.r_humidity, row.snow_hour, row.x_grid, row.y_grid])
        cls._meta.database.close() # or global_database.close()
        return result_list


class APIstate(BaseModel):
    daytime = CharField(max_length=12, null=False) #날짜, 시간
    #stn = CharField(max_length=3, null=False)

    wind_direction = DecimalField(decimal_places=1, max_digits=4, null=True, default=None) #1분 평균 풍향 deg
    wind_velocity = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #1분 평균 풍속 m/s
    wind_direction_max = DecimalField(decimal_places=1, max_digits=4, null=True, default=None) #최대 순간 풍향 deg
    wind_velocity_max = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #최대 순간 풍속 m/s
    wind_direction_10m = DecimalField(decimal_places=1, max_digits=4, null=True, default=None) #10분 평균 풍향 deg
    wind_velocity_10m = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #10분 평균 풍속 m/s

    air_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #1분 평균 기온 ˚C
    rain =  BooleanField(null=True, default=None) #강수감지
    rain_15m = DecimalField(decimal_places=1, max_digits=4, null=True, default=None) #15분 누적 강수량 mm
    rain_60m = DecimalField(decimal_places=1, max_digits=4, null=True, default=None) #60분 누적 강수량 mm
    rain_12h = DecimalField(decimal_places=1, max_digits=4, null=True, default=None) #12시간 누적 강수량 mm
    rain_1d = DecimalField(decimal_places=1, max_digits=4, null=True, default=None) #1일 누적 강수량 mm

    r_humidity = DecimalField(decimal_places=1, max_digits=4, null=True, default=None) #1분 평균 상대습도 %
    air_pressure = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #1분 평균 현지기압 hpa #미사용
    sea_pressure = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #1분 평균 해면기압 hpa #미사용
    dewpoint = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #이슬점 온도 ˚C

    class Meta:
        database = global_database


class APIweather(BaseModel):
    daytime = CharField(max_length=12, null=False) #날짜,시간
    #stn = CharField(max_length=3, null=False)

    lon = DecimalField(decimal_places=14, max_digits=17, null=True, default=None) #위경도
    lat = DecimalField(decimal_places=14, max_digits=17, null=True, default=None) #위경도
    
    visibility =  IntegerField(null=True, default=None) #1분 평균 시정
    visibility_10m = IntegerField(null=True, default=None) #10분 평균 시정
    
    weather = IntegerField(constraints=[Check('weather >= 0 AND weather <= 100')], null=True, default=None) #1분 순간 현천
    weather_15m = IntegerField(constraints=[Check('weather_15m >= 0 AND weather_15m <= 100')], null=True, default=None) #15분 평균 현천

    class Meta:
        database = global_database





## 실제 측정값
class Sensor(BaseModel):
    daytime = CharField(max_length=21, null=False) #날짜,시간(밀리초 단위까지)
    #device = CharField(max_length=3, null=False)

    wind_direction = DecimalField(decimal_places=1, max_digits=4, null=True, default=None) #풍향 deg
    wind_velocity = DecimalField(decimal_places=3, max_digits=5, null=True, default=None) #풍속 m/s
    air_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #기온 ˚C
    r_humidity = DecimalField(decimal_places=2, max_digits=5, null=True, default=None) #습도 %
    air_pressure = DecimalField(decimal_places=2, max_digits=6, null=True, default=None) #기압 hpa
    illuminance = IntegerField(constraints=[Check('illuminance >= 0 AND illuminance <= 100000')], null=True, default=None) #주변광 광량 lx
    rain = IntegerField(constraints=[Check('rain >= 0 AND rain <= 20')], null=True, default=None) #강수레벨
    uva = DecimalField(decimal_places=2, max_digits=5, null=True, default=None) #자외선
    uvb = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #자외선
    
    err_code = IntegerField(null=False)
    err_log = CharField(max_length=64, null=True)

    class Meta:
        database = global_database


class Surface(BaseModel):
    daytime = CharField(max_length=21, null=False) #날짜,시간(밀리초 단위까지)
    #device = CharField(max_length=3, null=False)

    surface_ch1 = DecimalField(decimal_places=2, max_digits=4, null=True, default=-99.99)
    surface_ch2 = DecimalField(decimal_places=2, max_digits=4, null=True, default=-99.99)
    surface_ch3 = DecimalField(decimal_places=2, max_digits=4, null=True, default=-99.99)
    surface_ch4 = DecimalField(decimal_places=2, max_digits=4, null=True, default=-99.99)
    surface_ch5 = DecimalField(decimal_places=2, max_digits=4, null=True, default=-99.99)
    surface_ch6 = DecimalField(decimal_places=2, max_digits=4, null=True, default=-99.99)

    surface_ch7 = DecimalField(decimal_places=2, max_digits=4, null=True, default=-99.99)
    surface_ch8 = DecimalField(decimal_places=2, max_digits=4, null=True, default=-99.99)
    surface_ch9 = DecimalField(decimal_places=2, max_digits=4, null=True, default=-99.99)
    surface_ch10 = DecimalField(decimal_places=2, max_digits=4, null=True, default=-99.99)
    surface_ch11 = DecimalField(decimal_places=2, max_digits=4, null=True, default=-99.99)
    surface_ch12 = DecimalField(decimal_places=2, max_digits=4, null=True, default=-99.99)

    surface_ch13 = DecimalField(decimal_places=2, max_digits=4, null=True, default=-99.99)
    surface_ch14 = DecimalField(decimal_places=2, max_digits=4, null=True, default=-99.99)
    surface_ch15 = DecimalField(decimal_places=2, max_digits=4, null=True, default=-99.99)
    surface_ch16 = DecimalField(decimal_places=2, max_digits=4, null=True, default=-99.99)
    surface_ch17 = DecimalField(decimal_places=2, max_digits=4, null=True, default=-99.99)
    surface_ch18 = DecimalField(decimal_places=2, max_digits=4, null=True, default=-99.99)

    class Meta:
        database = global_database

    


class Weather(BaseModel):
    daytime = CharField(max_length=12, null=False) #날짜,시간
    #device = CharField(max_length=3, null=False)

    weather = CharField(max_length=1, null=True) #날씨코드

    class Meta:
        database = global_database




## 인공지능 입출력
class AIdata_1h(BaseModel):

    #입력시간(기준, 연산 수행시간)
    daytime = CharField(max_length=21, null=False) #날짜,시간(밀리초 단위까지)

    #출력시간(예측대상시간)
    pridict_daytime = CharField(max_length=12, null=False) #날짜,시간

    #입력된 데이터
    air_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #기온 ˚C
    surface_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #노면온도 ˚C
    r_humidity = DecimalField(decimal_places=2, max_digits=5, null=True, default=None) #습도 %
    wind_velocity = DecimalField(decimal_places=3, max_digits=5, null=True, default=None) #풍속 m/s
    #wind_direction = IntegerField(constraints=[Check('vec >= 0 AND vec <= 360')], null=True, default=None) #풍향 deg
    #air_pressure = DecimalField(decimal_places=2, max_digits=6, null=True, default=None) #기압 hpa

    sky = IntegerField(constraints=[Check('sky >= 0 AND sky <= 100')], null=True, default=None) #날씨 코드값(강설여부 포함)
    dewpoint = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #이슬점 온도 ˚C

    #출력된 데이터
    out_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #기온 ˚C
    out_surface_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #노면온도 ˚C
    out_humidity = DecimalField(decimal_places=2, max_digits=5, null=True, default=None) #습도 %
    out_wind_velocity = DecimalField(decimal_places=3, max_digits=5, null=True, default=None) #풍속 m/s
    out_weather = CharField(max_length=1, null=False) #날씨 코드값(강설여부 포함)

    class Meta:
        database = global_database

    


class AIdata_2h(BaseModel):

    #입력시간(기준, 연산 수행시간)
    daytime = CharField(max_length=21, null=False) #날짜,시간(밀리초 단위까지)

    #출력시간(예측대상시간)
    pridict_daytime = CharField(max_length=12, null=False) #날짜,시간

    #입력된 데이터
    air_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #기온 ˚C
    surface_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #노면온도 ˚C
    r_humidity = DecimalField(decimal_places=2, max_digits=5, null=True, default=None) #습도 %
    wind_velocity = DecimalField(decimal_places=3, max_digits=5, null=True, default=None) #풍속 m/s
    #wind_direction = IntegerField(constraints=[Check('vec >= 0 AND vec <= 360')], null=True, default=None) #풍향 deg
    #air_pressure = DecimalField(decimal_places=2, max_digits=6, null=True, default=None) #기압 hpa

    sky = IntegerField(constraints=[Check('sky >= 0 AND sky <= 100')], null=True, default=None) #날씨 코드값(강설여부 포함)
    dewpoint = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #이슬점 온도 ˚C

    #출력된 데이터
    out_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #기온 ˚C
    out_surface_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #노면온도 ˚C
    out_humidity = DecimalField(decimal_places=2, max_digits=5, null=True, default=None) #습도 %
    out_wind_velocity = DecimalField(decimal_places=3, max_digits=5, null=True, default=None) #풍속 m/s
    out_weather = CharField(max_length=1, null=False) #날씨 코드값(강설여부 포함) 

    class Meta:
        database = global_database

    

class ImgAIdata(BaseModel):
    #입력시간(기준, 연산 수행시간)
    daytime = CharField(max_length=21, null=False) #날짜,시간(밀리초 단위까지)

    #입력된 데이터 위치
    road_imgfile_path = TextField(null=False) # 이미지 파일 경로

    #출력된 데이터
    out_road_state = IntegerField(constraints=[Check('out_road_state >= 0 AND out_road_state <= 100')], null=True, default=None) #코드값(설명참조)

    class Meta:
        database = global_database



## 노면상태 분류 알고리즘
## now
class Classifier_now(BaseModel):
    daytime = CharField(max_length=21, null=False) #날짜,시간(밀리초 단위까지)

    # 센서 측정값, 결측치는 기상청 정보로 대체
    air_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    surface_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    r_humidity = DecimalField(decimal_places=2, max_digits=5, null=True, default=None) #습도 %
    wind_velocity = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #풍속 m/s
    dewpoint = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) # 계산 불가능시 기상청 정보로 대체 또는 대체이후 연산
    now_weather = CharField(max_length=6, null=True, default=None) # snow, rain, sun, other 의 4가지 상태의 날씨, 센서의  측정 우선, 기상청 정보 참조

    # 이전 기록값, 결측치는 기상청 정보로 대체하거나 발생한 적 없음으로 간주하고 연산
    past_rain = BooleanField(null=True, default=None)
    past_past_frozen = BooleanField(null=True, default=None)

    # 출력 결과값
    surface_state = CharField(max_length=1, null=False)
 
    class Meta:
        database = global_database

    


class Classifier_q(BaseModel):
    '''
    simplified 'Classifier_now table'
    '''
    daytime = CharField(max_length=21, null=False) #날짜,시간(밀리초 단위까지)
    surface_state = CharField(max_length=1, null=False) # 분류 결과

    class Meta:
        database = global_database
    
    


## 1h pridict
class Classifier_1h(BaseModel):
    daytime = CharField(max_length=21, null=False) #날짜,시간(밀리초 단위까지)

    # 센서 측정값, 결측치는 기상청 정보로 대체
    air_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    surface_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    r_humidity = DecimalField(decimal_places=2, max_digits=5, null=True, default=None) #습도 %
    wind_velocity = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #풍속 m/s
    dewpoint = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) # 계산 불가능시 기상청 정보로 대체 또는 대체이후 연산
    now_weather = CharField(max_length=6, null=True, default=None) # snow, rain, sun, other 의 4가지 상태의 날씨, 센서의  측정 우선, 기상청 정보 참조

    # 이전 기록값, 결측치는 기상청 정보로 대체하거나 발생한 적 없음으로 간주하고 연산
    past_rain = BooleanField(null=True, default=None)
    past_past_frozen = BooleanField(null=True, default=None)

    # 출력 결과값
    surface_state = CharField(max_length=1, null=False)
 
    class Meta:
        database = global_database

    
    

    
class Classifier_q_1h(BaseModel):
    '''
    simplified 'Classifier_1h table'
    '''
    daytime = CharField(max_length=21, null=False) #날짜,시간(밀리초 단위까지)
    surface_state = CharField(max_length=1, null=False) # 분류 결과

    class Meta:
        database = global_database
    


## 2h pridict
class Classifier_2h(BaseModel):
    daytime = CharField(max_length=21, null=False) #날짜,시간(밀리초 단위까지)

    # 센서 측정값, 결측치는 기상청 정보로 대체
    air_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    surface_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    r_humidity = DecimalField(decimal_places=2, max_digits=5, null=True, default=None) #습도 %
    wind_velocity = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #풍속 m/s
    dewpoint = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) # 계산 불가능시 기상청 정보로 대체 또는 대체이후 연산
    now_weather = CharField(max_length=6, null=True, default=None) # snow, rain, sun, other 의 4가지 상태의 날씨, 센서의  측정 우선, 기상청 정보 참조

    # 이전 기록값, 결측치는 기상청 정보로 대체하거나 발생한 적 없음으로 간주하고 연산
    past_rain = BooleanField(null=True, default=None)
    past_past_frozen = BooleanField(null=True, default=None)

    # 출력 결과값
    surface_state = CharField(max_length=1, null=False)
 
    class Meta:
        database = global_database

    
class Classifier_q_2h(BaseModel):
    '''
    simplified 'Classifier_2h table'
    '''
    daytime = CharField(max_length=21, null=False) #날짜,시간(밀리초 단위까지)
    surface_state = CharField(max_length=1, null=False) # 분류 결과

    class Meta:
        database = global_database



## test table
class TTable(BaseModel):
    daytime = CharField(max_length=21, null=False)
    a = CharField(max_length=3, null=False)
    b = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    c = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    d = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    e = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    f = DecimalField(decimal_places=2, max_digits=5, null=True, default=None)
    g = IntegerField(null=True, default=None)
    h = IntegerField(null=True, default=None)

    class Meta:
        database = global_database
        


if __name__ =="__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-tc', '--table_check', action='store_true', default=False)

        args = parser.parse_args()

        if args.table_check:

            global_database.connect() ##
            if not APIPridict.table_exists():
                global_database.create_tables([APIPridict])
            APIPridict.print_table_schema()
            global_database.close()

            global_database.connect() ##
            if not APIstate.table_exists():
                global_database.create_tables([APIstate])
            APIstate.print_table_schema()
            global_database.close()

            global_database.connect() ##
            if not APIweather.table_exists():
                global_database.create_tables([APIweather])
            APIweather.print_table_schema()
            global_database.close()

            global_database.connect() ##
            if not Sensor.table_exists():
                global_database.create_tables([Sensor])
            Sensor.print_table_schema()
            global_database.close()

            global_database.connect() ##
            if not Surface.table_exists():
                global_database.create_tables([Surface])
            Surface.print_table_schema()
            global_database.close()

            global_database.connect() ##
            if not Weather.table_exists():
                global_database.create_tables([Weather])
            Weather.print_table_schema()
            global_database.close()

            global_database.connect() ##
            if not AIdata_1h.table_exists():
                global_database.create_tables([AIdata_1h])
            AIdata_1h.print_table_schema()
            global_database.close()

            global_database.connect() ##
            if not AIdata_2h.table_exists():
                global_database.create_tables([AIdata_2h])
            AIdata_2h.print_table_schema()
            global_database.close()

            global_database.connect() ##
            if not ImgAIdata.table_exists():
                global_database.create_tables([ImgAIdata])
            ImgAIdata.print_table_schema()
            global_database.close()

            global_database.connect() ##
            if not Classifier_now.table_exists():
                global_database.create_tables([Classifier_now])
            Classifier_now.print_table_schema()
            global_database.close()

            global_database.connect() ##
            if not Classifier_q.table_exists():
                global_database.create_tables([Classifier_q])
            Classifier_q.print_table_schema()
            global_database.close()

            global_database.connect() ##
            if not Classifier_1h.table_exists():
                global_database.create_tables([Classifier_1h])
            Classifier_1h.print_table_schema()
            global_database.close()

            global_database.connect() ##
            if not Classifier_q_1h.table_exists():
                global_database.create_tables([Classifier_q_1h])
            Classifier_q_1h.print_table_schema()
            global_database.close()
            
            global_database.connect() ##
            if not Classifier_2h.table_exists():
                global_database.create_tables([Classifier_2h])
            Classifier_2h.print_table_schema()
            global_database.close()

            global_database.connect() ##
            if not Classifier_q_2h.table_exists():
                global_database.create_tables([Classifier_q_2h])
            Classifier_q_2h.print_table_schema()
            global_database.close()

            global_database.connect() ##
            if not TTable.table_exists():
                global_database.create_tables([TTable])
            TTable.print_table_schema()
            global_database.close()

        sys.exit(0)

    # 에러 발생 시 출력하고 종료
    except OperationalError as e:
        print(f'데이터베이스 연산 실패 {e}', file=sys.stderr)
        sys.exit(1)

    except IntegrityError as e:
        print(f'데이터베이스 무결성 오류 {e}', file=sys.stderr)
        sys.exit(1)

    except DoesNotExist as e:
        print(f'해당 객체가 존재하지 않음 {e}', file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f'{e}', file=sys.stderr)
        sys.exit(1)