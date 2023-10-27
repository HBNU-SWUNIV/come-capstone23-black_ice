## 0. Module Import
# 클래스 힌트
from typing import List
# 입력 옵션, 인자 파싱
import argparse
# 프로그램 종료, 경로 입력
import sys
# I2C 통신, 측정
import smbus
from time import sleep
# 결과 출력 시간 지정
from datetime import datetime





## 1. EnvSensor functions
# 라이브러리 겸용 클래스, 메소드 선언
class EnvSensor:
    '''
    ## Introduction
        EnvSensor 클래스는 환경센서 동작을 설정하고, 데이터를 수집하기 위한 클래스입니다.\n
    ## Method
        __init__() : 생성자. I2C 포트 개방 및 측정 모드(default: Continuous measurement mode (Normal)) 세팅을 진행합니다.\n
        get_all_featuers() : 환경센서 측정값을 즉시(250ms) 흭득하여 리스트 형태로 반환하는 메소드입니다.
    '''
    # 클래스 상수 선언
    ENVSENSOR_ADDR = 0x42



    def __init__(
            self, 
            port_i2c: int
    ):
        # I2C 포트 개방
        self.envsensor_i2c = smbus.SMBus(port_i2c)
        # Continuous measurement mode (Normal)로 동작 설정
        self.envsensor_i2c.write_byte(self.ENVSENSOR_ADDR, 0x01)



    def get_all_features(self) -> List:
        '''
        ## Return value
            [wind_velocity, wind_direction, temperature, humidity, air_pressure, illuminance, rain_level, uva, uvb]
        '''
        # 250ms 간 측정
        self.envsensor_i2c.write_byte(self.ENVSENSOR_ADDR, 0x08)
        sleep(0.25)

        # 데이터 받아오기
        result = self.envsensor_i2c.read_i2c_block_data(self.ENVSENSOR_ADDR, 0x04, 22)
        # decode data
        error_flag = result[0]
        wind_velocity = (result[1] << 16 | result[2] << 8 | result[3]) / 1000.0
        wind_direction = (result[4] << 8 | result[5]) / 10.0
        temperature = (result[6] << 8 | result[7]) / 100.0
        humidity = (result[8] << 8 | result[9]) / 100.0
        air_pressure = (result[10] << 16 | result[11] << 8 | result[12]) / 100.0
        illuminance = result[13] << 16 | result[14] << 8 | result[15]
        rain_level = result[16] << 8 | result[17]
        uva = result[18] << 8 | result[19]
        uvb = result[20] << 8 | result[21]

        # 데이터 반환
        return [wind_velocity, wind_direction, temperature, humidity, air_pressure, illuminance, rain_level, uva, uvb]





## 2. Main
# 실행 파일 작동 시 기능
if __name__ == '__main__':
    try:
        # 입력 인자 파싱
        parser = argparse.ArgumentParser(prog=sys.argv[0], add_help=True)
        parser.add_argument('--port_i2c', type=int, nargs=1, action='store', required=True)

        args = parser.parse_args()


        # 파싱된 인자 구별/캡슐화 해재
        args.port_i2c = args.port_i2c[0]


        # 파싱 데이터 기반 클래스 생성, 메소드 실행
        envsensor = EnvSensor(port_i2c=args.port_i2c)
        result = envsensor.get_all_features()
        

        # 작업 종료 시간 포함 결과 출력
        print(f"{datetime.now().strftime('%Y%m%d%H%M%S.%f')}", *result, file=sys.stdout)
        sys.exit(0)


# 에러 발생 시 출력하고 종료
    except Exception as e:
        print(f'{e}', file=sys.stdout)
        sys.exit(1)