## 0. Module Import
# 클래스 힌트
from typing import Iterable, List
# 입력 옵션, 인자 파싱
import argparse
# 프로그램 종료, 경로 입력
import sys
# MODBUS 통신, 측정
import minimalmodbus
import serial
from time import sleep
# 결과 출력 시간 지정
from datetime import datetime





## 1. MODBUS Reading Function
# 라이브러리 겸용 함수 선언
def groundtemperature(
        port: str, 
        logger_addr: int, 
        channels: Iterable[int], 
        baudrate: int=9600, 
        bytesize: int=8, 
        parity=serial.PARITY_NONE, 
        stopbits=serial.STOPBITS_TWO, 
        timeout: float=1.0, 
        write_timeout: float=1.0, 
        byteorder=minimalmodbus.BYTEORDER_BIG
) -> List[float]:
    '''
    ## Input arguments
        - port : \n
            - 데이터로거의 포트명 (ex. 'COM1', '/dev/ttyUSB0', ...)\n
        - logger_addr : \n
            - 데이터로거의 id(slave_addr)\n
        - channels : \n
            - 데이터로거에서 출력할 채널 번호 (ex. (1, 2, 3, 6, 12, 17), range(1, 19), ...)\n
        - baudrate : \n
            - 시리얼 통신 시 보레이트(bps)\n
        - bytesize : \n
            - 1byte 당 bit 수\n
        - parity : \n
            - 패리티 비트 사용 여부\n
        - stopbits : \n
            - 정지 비트의 길이\n
        - timeout : \n
            - 읽기 작업 최대 대기 시간\n
        - write_timeout : \n
            - 쓰기 작업 최대 대기 시간\n
        - byteorder : \n
            - 비트 순서 (리틀엔디언, 빅 엔디언 등)\n\n\n
    ## Return value
            이 함수의 반환값은 온도에 대한 리스트입니다.\n
            온도값은 소수점 한 자리까지 표기되며, 출력 순서는 channels에 명시된 채널 순서입니다.\n
            에러 발생 시 별도의 핸들러 및 예외 메시지를 포함하지 않고 있으니 사용에 유의 바랍니다.
    '''
    
    # 데이터로거 Instrument객체로 선언 및 통신 설정
    logger = minimalmodbus.Instrument(
        port=port, 
        slaveaddress=logger_addr, 
        mode=minimalmodbus.MODE_RTU
    )
    logger.serial.baudrate = baudrate
    logger.serial.bytesize = bytesize
    logger.serial.parity = parity
    logger.serial.stopbits = stopbits
    logger.serial.timeout = timeout
    logger.serial.write_timeout = write_timeout


    # 명시된 각 채널에서의 온도 측정
    temperature_results = []
    for channel_cur in channels:
        temperature = logger.read_float(
            registeraddress=(channel_cur * 2) - 1, 
            functioncode=3, 
            number_of_registers=2, 
            byteorder=byteorder
        )
        temperature_results.append(round(temperature, 1))
        sleep(0.1)


    # 측정 후 반환
    return temperature_results
        




## 2. Main
# 실행 파일로 작동 시 기능
if __name__ == '__main__':
    try:
        # 입력 인자 파싱
        parser = argparse.ArgumentParser(prog=sys.argv[0], add_help=True)
        parser.add_argument('--port', type=str, nargs=1, action='store', required=True)
        parser.add_argument('--logger_addr', type=int, nargs=1, action='store', required=True)
        parser.add_argument('--channel', type=int, nargs='+', action='store', required=True)
        parser.add_argument('--baudrate', type=int, nargs=1, default=[9600], action='store')
        parser.add_argument('--bytesize', type=int, nargs=1, default=[8], action='store')
        parser.add_argument('--parity', choices=['none', 'odd', 'even'], default='none', action='store')
        parser.add_argument('--stopbits', choices=[1, 2], default=2, action='store')
        parser.add_argument('--timeout', type=float, nargs=1, default=[1.0], action='store')
        parser.add_argument('--write_timeout', type=float, nargs=1, default=[1.0], action='store')
        parser.add_argument('--byteorder', choices=['big', 'little'], default='big', action='store')
        
        args = parser.parse_args()


        # 파싱된 인자 구별/캡슐화 해재
        args.port = args.port[0]
        args.logger_addr = args.logger_addr[0]
        args.baudrate = args.baudrate[0]
        args.bytesize = args.bytesize[0]
        args.timeout = args.timeout[0]
        args.write_timeout = args.write_timeout[0]
        
        if args.parity == 'none':
            args.parity = serial.PARITY_NONE
        elif args.parity == 'odd':
            args.parity = serial.PARITY_ODD
        elif args.parity == 'even':
            args.parity = serial.PARITY_EVEN
        
        if args.stopbits == 1:
            args.stopbits = serial.STOPBITS_ONE
        elif args.stopbits == 2:
            args.stopbits = serial.STOPBITS_TWO
        
        if args.byteorder == 'big':
            args.byteorder = minimalmodbus.BYTEORDER_BIG
        elif args.byteorder == 'little':
            args.byteorder = minimalmodbus.BYTEORDER_LITTLE


        # 파싱 데이터 기반 함수 실행
        result = groundtemperature(
            port=args.port, 
            logger_addr=args.logger_addr, 
            channels=args.channel, 
            baudrate=args.baudrate, 
            bytesize=args.bytesize, 
            parity=args.parity, 
            stopbits=args.stopbits, 
            timeout=args.timeout, 
            write_timeout=args.write_timeout, 
            byteorder=args.byteorder
        )
        

        # 작업 종료 시간 포함 결과 출력
        print(f"{datetime.now().strftime('%Y%m%d%H%M%S.%f')}", *result, file=sys.stdout, end='')
        sys.exit(0)


    # 에러 발생 시 출력하고 종료
    except Exception as e:
        print(f'{__file__}: {e}', file=sys.stderr)
        sys.exit(1)