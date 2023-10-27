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


class UNIONTABLE(BaseModel):
    ### SEQUENCE STANDARD TIME
    #daytime = CharField(max_length=12, null=False, index=True, unique=True)
    daytime = DateTimeField(formats='%Y%m%d%H%M', null=False, index=True, unique=True)


    ### FOR SERVER
    #서버 동기화 진행 여부
    SERVER_synchronize = BooleanField(null=False, default=False)

    ### API DATA
    API_wind_velocity = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #1분 평균 풍속 m/s
    API_air_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #1분 평균 기온 ˚C
    API_rain =  BooleanField(null=True, default=None) #강수감지
    API_r_humidity = DecimalField(decimal_places=1, max_digits=4, null=True, default=None) #1분 평균 상대습도 %
    API_air_pressure = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #1분 평균 현지기압 hpa #미사용
    API_dewpoint = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #이슬점 온도 ˚C
    API_weather = IntegerField(constraints=[Check('weather >= 0 AND weather <= 100')], null=True, default=None) #1분 순간 현천
    API_x_grid = IntegerField(null=True, default=None) #예보 구역 격자 구간 좌표(x)
    API_y_grid = IntegerField(null=True, default=None) #예보 구역 격자 구간 좌표(y)


    ### SENSOR DATA
    SENSOR_wind_direction = DecimalField(decimal_places=1, max_digits=4, null=True, default=None) #풍향 deg
    SENSOR_wind_velocity = DecimalField(decimal_places=3, max_digits=5, null=True, default=None) #풍속 m/s
    SENSOR_air_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #기온 ˚C
    SENSOR_r_humidity = DecimalField(decimal_places=2, max_digits=5, null=True, default=None) #습도 %
    SENSOR_air_pressure = DecimalField(decimal_places=2, max_digits=6, null=True, default=None) #기압 hpa
    SENSOR_illuminance = IntegerField(constraints=[Check('illuminance >= 0 AND illuminance <= 100000')], null=True, default=None) #주변광 광량 lx
    SENSOR_rain = IntegerField(constraints=[Check('rain >= 0 AND rain <= 20')], null=True, default=None) #강수레벨
    SENSOR_uva = DecimalField(decimal_places=2, max_digits=5, null=True, default=None) #자외선
    SENSOR_uvb = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #자외선
    SENSOR_err_code = IntegerField(null=True, default=None)


    ### SURFACE DATA
    SURFACE_ch1 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    SURFACE_ch2 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    SURFACE_ch3 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    SURFACE_ch4 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    SURFACE_ch5 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    SURFACE_ch6 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)

    SURFACE_ch7 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    SURFACE_ch8 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    SURFACE_ch9 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    SURFACE_ch10 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    SURFACE_ch11 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    SURFACE_ch12 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)

    SURFACE_ch13 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    SURFACE_ch14 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    SURFACE_ch15 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    SURFACE_ch16 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    SURFACE_ch17 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    SURFACE_ch18 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)


    ### WEATHER DATA
    # refer to [API DATA, SENSOR DATA]
    weather = CharField(max_length=1, null=True, default=None) #실제로 기록된 날씨코드(눈/비/그외 날씨로 분류한다)


    ### AI PREDICT 1H OUT DATA
    # refer to [*API DATA, SENSOR DATA, SURFACE DATA]
    AI1H_out_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #기온 ˚C
    AI1H_out_surface_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #노면온도 ˚C
    AI1H_out_humidity = DecimalField(decimal_places=2, max_digits=5, null=True, default=None) #습도 %
    AI1H_out_wind_velocity = DecimalField(decimal_places=3, max_digits=5, null=True, default=None) #풍속 m/s
    AI1H_out_weather = CharField(max_length=1, null=True, default=None) #날씨 코드값(강설여부 포함)

    ### AI PREDICT 2H OUT DATA
    # refer to [*API DATA, SENSOR DATA, SURFACE DATA]
    AI2H_out_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #기온 ˚C
    AI2H_out_surface_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #노면온도 ˚C
    AI2H_out_humidity = DecimalField(decimal_places=2, max_digits=5, null=True, default=None) #습도 %
    AI2H_out_wind_velocity = DecimalField(decimal_places=3, max_digits=5, null=True, default=None) #풍속 m/s
    AI2H_out_weather = CharField(max_length=1, null=True, default=None) #날씨 코드값(강설여부 포함)


    ### IMG AI DATA
    IMG_AI_IMGPATH = TextField(collation='utf8_general_ci', null=True, default=None)
    IMG_AI_CLASSIFIER = CharField(max_length=1, null=True, default=None)

    ### CLASSIFIER DATA

    ## NOW ###################
    ## 입력값은 refer to [*API DATA, SENSOR DATA, SURFACE DATA, WEATHER, CLASSIFIER DATA(NOW)]
    CLASSIFIER_NOW_past_rain = BooleanField(null=True, default=None) #
    CLASSIFIER_NOW_past_past_frozen = BooleanField(null=True, default=None) #
    # 출력값
    CLASSIFIER_NOW_surface_state = CharField(max_length=1, null=True, default=None)

    ## 1H ###################
    ## 입력값은 refer to [*API DATA, SENSOR DATA, SURFACE DATA, WEATHER, CLASSIFIER DATA(NOW), CLASSIFIER DATA(1H)]
    CLASSIFIER_1H_past_rain = BooleanField(null=True, default=None) #
    CLASSIFIER_1H_past_past_frozen = BooleanField(null=True, default=None) #
    # 출력값
    CLASSIFIER_1H_surface_state = CharField(max_length=1, null=True, default=None)

    ## 2H ###################
    ## 입력값은 refer to [*API DATA, SENSOR DATA, SURFACE DATA, WEATHER, CLASSIFIER DATA(1H), CLASSIFIER DATA(2H)]
    CLASSIFIER_2H_past_rain = BooleanField(null=True, default=None) #
    CLASSIFIER_2H_past_past_frozen = BooleanField(null=True, default=None) #
    # 출력값
    CLASSIFIER_2H_surface_state = CharField(max_length=1, null=True, default=None)

    class Meta:
        database = global_database



## test table
class TTable(BaseModel):
    ### SEQUENCE STANDARD TIME
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
            if not UNIONTABLE.table_exists():
                global_database.create_tables([UNIONTABLE])
            UNIONTABLE.print_table_schema()
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