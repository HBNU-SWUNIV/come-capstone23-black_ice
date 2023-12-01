from peewee import *
from typing import List
import sys
import argparse


# PostgreSQL 데이터베이스에 연결
global_database = PostgresqlDatabase('postgres', user='****', password='****', host='localhost', port=****)



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

    # @classmethod
    # def __str__(cls):
    #     fields = cls._meta.fields
    #     for key, value in fields.items():
    #         #print(f'{fields[i].key} :{fields[i].value}')
    #         print(f'{print(value)}, ')
            
        


class UNIONTABLE(BaseModel):
    ### SEQUENCE STANDARD TIME
    #daytime = CharField(max_length=12, null=False, index=True, unique=True)
    daytime = DateTimeField(formats='%Y%m%d%H%M%S.%f', null=False, index=True, unique=True)


    ### FOR SERVER
    #서버 동기화 진행 여부
    server_synchronize = BooleanField(null=False, default=False)

    ### API DATA
    api_wind_velocity = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #1분 평균 풍속 m/s
    api_air_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #1분 평균 기온 ˚C
    api_rain =  BooleanField(null=True, default=None) #강수감지
    api_r_humidity = DecimalField(decimal_places=1, max_digits=4, null=True, default=None) #1분 평균 상대습도 %
    api_air_pressure = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #1분 평균 현지기압 hpa #미사용
    api_dewpoint = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #이슬점 온도 ˚C
    api_weather = IntegerField(constraints=[Check('api_weather >= 0 AND api_weather <= 100')], null=True, default=None) #1분 순간 현천
    api_x_grid = IntegerField(null=True, default=None) #예보 구역 격자 구간 좌표(x)
    api_y_grid = IntegerField(null=True, default=None) #예보 구역 격자 구간 좌표(y)


    ### SENSOR DATA
    sensor_wind_direction = DecimalField(decimal_places=1, max_digits=4, null=True, default=None) #풍향 deg
    sensor_wind_velocity = DecimalField(decimal_places=3, max_digits=5, null=True, default=None) #풍속 m/s
    sensor_air_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #기온 ˚C
    sensor_r_humidity = DecimalField(decimal_places=2, max_digits=5, null=True, default=None) #습도 %
    sensor_air_pressure = DecimalField(decimal_places=2, max_digits=6, null=True, default=None) #기압 hpa
    sensor_illuminance = IntegerField(constraints=[Check('sensor_illuminance >= 0 AND sensor_illuminance <= 100000')], null=True, default=None) #주변광 광량 lx
    sensor_rain = IntegerField(constraints=[Check('sensor_rain >= 0 AND sensor_rain <= 20')], null=True, default=None) #강수레벨
    sensor_uva = DecimalField(decimal_places=2, max_digits=5, null=True, default=None) #자외선
    sensor_uvb = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #자외선
    sensor_err_code = IntegerField(null=True, default=None)


    ### SURFACE DATA
    surface_ch1 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    surface_ch2 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    surface_ch3 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    surface_ch4 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    surface_ch5 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    surface_ch6 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)

    surface_ch7 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    surface_ch8 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    surface_ch9 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    surface_ch10 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    surface_ch11 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    surface_ch12 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)

    surface_ch13 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    surface_ch14 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    surface_ch15 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    surface_ch16 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    surface_ch17 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    surface_ch18 = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)


    ### WEATHER DATA
    # refer to [API DATA, SENSOR DATA]
    weather = CharField(max_length=1, null=True, default=None) #실제로 기록된 날씨코드(눈/비/그외 날씨로 분류한다)


    ### AI PREDICT 1H OUT DATA
    # refer to [*API DATA, SENSOR DATA, SURFACE DATA]
    ai1h_out_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #기온 ˚C
    ai1h_out_surface_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #노면온도 ˚C
    ai1h_out_humidity = DecimalField(decimal_places=2, max_digits=5, null=True, default=None) #습도 %
    ai1h_out_wind_velocity = DecimalField(decimal_places=3, max_digits=5, null=True, default=None) #풍속 m/s
    ai1h_out_weather = CharField(max_length=1, null=True, default=None) #날씨 코드값(강설여부 포함)

    ### AI PREDICT 2H OUT DATA
    # refer to [*API DATA, SENSOR DATA, SURFACE DATA]
    ai2h_out_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #기온 ˚C
    ai2h_out_surface_temperature = DecimalField(decimal_places=2, max_digits=4, null=True, default=None) #노면온도 ˚C
    ai2h_out_humidity = DecimalField(decimal_places=2, max_digits=5, null=True, default=None) #습도 %
    ai2h_out_wind_velocity = DecimalField(decimal_places=3, max_digits=5, null=True, default=None) #풍속 m/s
    ai2h_out_weather = CharField(max_length=1, null=True, default=None) #날씨 코드값(강설여부 포함)


    ### IMG AI DATA
    #img_ai_imgpath = TextField(null=True, default=None)
    img_ai_img = BlobField(null=True, default=None) # 입출력 시 파일의 경로(문자열)를 통해 동작함에 유의
    img_ai_classifier = CharField(max_length=1, null=True, default=None)

    ### CLASSIFIER DATA

    ## NOW ###################
    ## 입력값은 refer to [*API DATA, SENSOR DATA, SURFACE DATA, WEATHER, CLASSIFIER DATA(NOW)]
    classifier_now_past_rain = BooleanField(null=True, default=None) #
    classifier_now_past_past_frozen = BooleanField(null=True, default=None) #
    # 출력값
    classifier_now_surface_state = CharField(max_length=1, null=True, default=None)

    ## 1H ###################
    ## 입력값은 refer to [*API DATA, SENSOR DATA, SURFACE DATA, WEATHER, CLASSIFIER DATA(NOW), CLASSIFIER DATA(1H)]
    classifier_1h_past_rain = BooleanField(null=True, default=None) #
    classifier_1h_past_past_frozen = BooleanField(null=True, default=None) #
    # 출력값
    classifier_1h_surface_state = CharField(max_length=1, null=True, default=None)

    ## 2H ###################
    ## 입력값은 refer to [*API DATA, SENSOR DATA, SURFACE DATA, WEATHER, CLASSIFIER DATA(1H), CLASSIFIER DATA(2H)]
    classifier_2h_past_rain = BooleanField(null=True, default=None) #
    classifier_2h_past_past_frozen = BooleanField(null=True, default=None) #
    # 출력값
    classifier_2h_surface_state = CharField(max_length=1, null=True, default=None)

    class Meta:
        database = global_database


class TPR_CTRL(BaseModel):
    '''
    이 테이블은 3상 전력제어기의 전력제어 정보를 위한 테이블입니다.
    메인 프로세스와 다른 주기로(비동기 동작) 동작하기 때문에 UNIONTABLE 과는 별도로 정의하였습니다.
    '''
    ### SEQUENCE STANDARD TIME
    daytime = DateTimeField(formats='%Y%m%d%H%M%S.%f', null=False, index=True)

    ### FOR SERVER
    #서버 동기화 진행 여부
    server_synchronize = BooleanField(null=False, default=False)

    ###

    # to do

    ###

    class Meta:
        database = global_database




class ERR_LOG(BaseModel):
    '''
    이 테이블은 시스템의 에러 정보를 위한 테이블입니다.
    메인 프로세스와 다른 주기로(비동기 동작) 동작하기 때문에 UNIONTABLE 과는 별도로 정의하였습니다.
    '''
    #daytime = CharField(max_length=21, null=False, index=True)
    err_daytime = DateTimeField(formats='%Y%m%d%H%M%S.%f', null=False, index=True)
    err_process = TextField(null=False)
    err_msg = TextField(null=False)
    err_sync = BooleanField(null=False, default=False)

    class Meta:
        database = global_database



## test table
class TTable(BaseModel):
    ### SEQUENCE STANDARD TIME
    daytime = DateTimeField(formats='%Y%m%d%H%M%S.%f', null=False, index=True)
    a = CharField(max_length=3, null=False)
    b = DecimalField(decimal_places=2, max_digits=4, null=True, default=None)
    c = BlobField(null=True, default=None) # 입출력 시 파일의 경로(문자열)를 통해 동작함에 유의
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
            if not TPR_CTRL.table_exists():
                global_database.create_tables([TPR_CTRL])
            TPR_CTRL.print_table_schema()
            global_database.close()

            global_database.connect() ##
            if not ERR_LOG.table_exists():
                global_database.create_tables([ERR_LOG])
            ERR_LOG.print_table_schema()
            global_database.close()

            global_database.connect() ##
            if not TTable.table_exists():
                global_database.create_tables([TTable])
            TTable.print_table_schema()
            global_database.close()


        sys.exit(0)



    # 에러 발생 시 출력하고 종료
    except OperationalError as e:
        print(f'{__file__} :\n데이터베이스 연산 실패 {e}', file=sys.stderr)
        sys.exit(1)

    except IntegrityError as e:
        print(f'{__file__} :\n데이터베이스 무결성 오류 {e}', file=sys.stderr)
        sys.exit(1)

    except DoesNotExist as e:
        print(f'{__file__} :\n해당 객체가 존재하지 않음 {e}', file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f'{__file__} :\n {e}', file=sys.stderr)
        sys.exit(1)