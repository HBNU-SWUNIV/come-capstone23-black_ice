import argparse
import re
import sys
import time
import datetime
import numpy as np
import requests
from bs4 import BeautifulSoup
from typing import List



def read_config(file_path):
    config = {}
    with open(file_path, 'r', encoding='UTF8') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config


def api_data_get(url: str, timeout: int = 30):
    try:
        res = requests.get(url, timeout=timeout)
    except requests.exceptions.Timeout as e:
        print(e)
        raise Exception('리퀘스트 시간 초과')
    
    if res.status_code != 200:
        print(res.status_code)
        print(res.text)
        raise Exception('요청이 처리되지 않음')
    
    return res.text


def api_data_process(api_data, features):
    soup = BeautifulSoup(api_data, features=features)
    front = soup.text.split('\n')

    real  = []
    for i in range(len(front)-1): #마지막에 줄바꿈 문자가 있어서 인덱싱 에러가 나므로 마지막줄을 빼준다.
        if(front[i][0] != "#"):
            real.append(front[i])
    
    processed_list = str(real).split()
        
    #첫번째 원소, 마지막 원소에  대괄호가 붙으므로 잘라준다.
    processed_list[0] = processed_list[0][2:]
    processed_list[-1] = processed_list[-1][:-2]

    return processed_list




def now_data_load(stn: str, api_key: str, timeout: int = 30) -> list:
    '''
    현재 기상 데이터를 리턴한다

    제공되는 항목, (이름)_(단위)\n
    'YYMMDDHHMI_KST', 'STN_ID', 'WD1_deg', 'WS1_m/s', 'WDS_deg', 'WSS_m/s', 'WS10_deg', 'WS10_m/s', 'TA_C', 
    'RE_1', 'RN-15m_mm', 'RN-60m_mm', 'RN-12H_mm', 'RN-DAY_mm', 'HM_%', 'PA_hPa', 'PS_hPa', 'TD_C'


    START7777
    #--------------------------------------------------------------------------------------------------
    #  WD1    : 1분 평균 풍향 (degree) : 0-N, 90-E, 180-S, 270-W, 360-무풍 
    #  WS1    : 1분 평균 풍속 (m/s) 
    #  WDS    : 최대 순간 풍향 (degree) 
    #  WSS    : 최대 순간 풍속 (m/s) 
    #  WD10   : 10분 평균 풍향 (degree) 
    #  WS10   : 10분 평균 풍속 (m/s) 
    #  TA     : 1분 평균 기온 (C) 
    #  RE     : 강수감지 (0-무강수, 0이 아니면-강수) 
    #  RN-15m : 15분 누적 강수량 (mm) 
    #  RN-60m : 60분 누적 강수량 (mm) 
    #  RN-12H : 12시간 누적 강수량 (mm) 
    #  RN-DAY : 일 누적 강수량 (mm) 
    #  HM     : 1분 평균 상대습도 (%) 
    #  PA     : 1분 평균 현지기압 (hPa) 
    #  PS     : 1분 평균 해면기압 (hPa) 
    #  TD     : 이슬점온도 (C) 
    #  *) -50 이하면 관측이 없거나, 에러처리된 것을 표시 
    #--------------------------------------------------------------------------------------------------
    # YYMMDDHHMI   STN    WD1    WS1    WDS    WSS   WS10   WS10     TA     RE RN-15m RN-60m RN-12H RN-DAY     HM     PA     PS     TD
    #        KST    ID    deg    m/s    deg    m/s    deg    m/s      C      1     mm     mm     mm     mm      %    hPa    hPa     C
    202302010900   548  314.0    0.5  300.9    1.3  304.3    0.6    1.7    0.0    0.0    0.0    0.0    0.0   91.7  -99.7  -99.7    0.5
    #7777END

    https://apihub.kma.go.kr/api/typ01/cgi-bin/url/nph-aws2_min?tm2=202302010900&stn=548&disp=0&help=1&authKey=LcdJI2t7SuCHSSNrexrgGA

    '''


    url = f'https://apihub.kma.go.kr/api/typ01/cgi-bin/url/nph-aws2_min?stn={stn}&authKey={api_key}'
    api_data = api_data_get(url, timeout)
    data = api_data_process(api_data, 'lxml')
    return data
    

def pointed_data_load(stn: str, api_key: str, date: str, timeout: int = 30) -> list:
    '''
    지정받은 시간(date)의 기상 데이터를 리턴한다. 

    제공되는 항목, (이름)_(단위)\n
    'YYMMDDHHMI_KST', 'STN_ID', 'WD1_deg', 'WS1_m/s', 'WDS_deg', 'WSS_m/s', 'WS10_deg', 'WS10_m/s', 'TA_C', 
    'RE_1', 'RN-15m_mm', 'RN-60m_mm', 'RN-12H_mm', 'RN-DAY_mm', 'HM_%', 'PA_hPa', 'PS_hPa', 'TD_C'


    START7777
    #--------------------------------------------------------------------------------------------------
    #  WD1    : 1분 평균 풍향 (degree) : 0-N, 90-E, 180-S, 270-W, 360-무풍 
    #  WS1    : 1분 평균 풍속 (m/s) 
    #  WDS    : 최대 순간 풍향 (degree) 
    #  WSS    : 최대 순간 풍속 (m/s) 
    #  WD10   : 10분 평균 풍향 (degree) 
    #  WS10   : 10분 평균 풍속 (m/s) 
    #  TA     : 1분 평균 기온 (C) 
    #  RE     : 강수감지 (0-무강수, 0이 아니면-강수) 
    #  RN-15m : 15분 누적 강수량 (mm) 
    #  RN-60m : 60분 누적 강수량 (mm) 
    #  RN-12H : 12시간 누적 강수량 (mm) 
    #  RN-DAY : 일 누적 강수량 (mm) 
    #  HM     : 1분 평균 상대습도 (%) 
    #  PA     : 1분 평균 현지기압 (hPa) 
    #  PS     : 1분 평균 해면기압 (hPa) 
    #  TD     : 이슬점온도 (C) 
    #  *) -50 이하면 관측이 없거나, 에러처리된 것을 표시
    #--------------------------------------------------------------------------------------------------
    # YYMMDDHHMI   STN    WD1    WS1    WDS    WSS   WS10   WS10     TA     RE RN-15m RN-60m RN-12H RN-DAY     HM     PA     PS     TD
    #        KST    ID    deg    m/s    deg    m/s    deg    m/s      C      1     mm     mm     mm     mm      %    hPa    hPa     C
    202302010900   548  314.0    0.5  300.9    1.3  304.3    0.6    1.7    0.0    0.0    0.0    0.0    0.0   91.7  -99.7  -99.7    0.5
    #7777END

    https://apihub.kma.go.kr/api/typ01/cgi-bin/url/nph-aws2_min?tm2=202302010900&stn=548&disp=0&help=1&authKey=LcdJI2t7SuCHSSNrexrgGA

    '''
    
    url = f'https://apihub.kma.go.kr/api/typ01/cgi-bin/url/nph-aws2_min?tm2={date}&stn={stn}&disp=0&help=1&authKey={api_key}'
    api_data = api_data_get(url, timeout)
    data = api_data_process(api_data, 'lxml')
    return data






def now_weather_load(stn: str, api_key: str, timeout: int = 30) -> list:
    '''
    현재 시정과 현천 데이터를 리턴한다.

    제공되는 항목, (이름)_(단위)\n
    'YYMMDDHHMI_KST',  'STN_ID', 'LON_deg', 'LAT_deg  S', 'VIS1_m', 'VIS10_m', 'WW1', 'WW15'


    #START7777
    #--------------------------------------------------------------------------------------------------
    #  S     : 장비구분 (1:안개관측망, 2:첨단화장비)
    #  VIS1  : 1분 평균 시정(m)
    #  VIS10 : 10분 평균 시정(m)
    #  WW1   : 1분 순간 현천(코드)
    #  WW15  : 15분 평균 현천(코드)
    #--------------------------------------------------------------------------------------------------
    # 현천코드 : 0~2(맑음), 4(연무), 10(박무), 30(안개), 40~42(비), 50~59(안개비), 60~68(비), 71~76(눈)
    #--------------------------------------------------------------------------------------------------
    # YYMMDDHHMI   STN         LON.         LAT.  S   VIS1  VIS10    WW1   WW15
    #        KST    ID        (deg)        (deg)       (m)    (m)              
    202304141510   548 127.63955688  37.26882935  2  42790   -999      0   -999
    #7777END

    https://apihub.kma.go.kr/api/typ01/cgi-bin/url/nph-aws2_min_vis?tm2=202304141510&stn=548&disp=0&help=1&authKey=LcdJI2t7SuCHSSNrexrgGA
    
    '''

    url = f'https://apihub.kma.go.kr/api/typ01/cgi-bin/url/nph-aws2_min_vis?stn={stn}&authKey={api_key}'
    api_data = api_data_get(url, timeout)
    data = api_data_process(api_data, 'lxml')
    return data


def pointed_weather_load(stn: str, api_key: str, date: str, timeout: int = 30) -> list:
    '''
    지정받은 시간의(date) 시정과 현천 데이터를 리턴한다.

    제공되는 항목, (이름)_(단위)\n
    'YYMMDDHHMI_KST',  'STN_ID', 'LON_deg', 'LAT_deg  S', 'VIS1_m', 'VIS10_m', 'WW1', 'WW15'


    #START7777
    #--------------------------------------------------------------------------------------------------
    #  S     : 장비구분 (1:안개관측망, 2:첨단화장비)
    #  VIS1  : 1분 평균 시정(m)
    #  VIS10 : 10분 평균 시정(m)
    #  WW1   : 1분 순간 현천(코드)
    #  WW15  : 15분 평균 현천(코드)
    #--------------------------------------------------------------------------------------------------
    # 현천코드 : 0~2(맑음), 4(연무), 10(박무), 30(안개), 40~42(비), 50~59(안개비), 60~68(비), 71~76(눈)
    #--------------------------------------------------------------------------------------------------
    # YYMMDDHHMI   STN         LON.         LAT.  S   VIS1  VIS10    WW1   WW15
    #        KST    ID        (deg)        (deg)       (m)    (m)              
    202304141510   548 127.63955688  37.26882935  2  42790   -999      0   -999
    #7777END

    https://apihub.kma.go.kr/api/typ01/cgi-bin/url/nph-aws2_min_vis?tm2=202304141510&stn=548&disp=0&help=1&authKey=LcdJI2t7SuCHSSNrexrgGA
    
    '''
    

    url = f'https://apihub.kma.go.kr/api/typ01/cgi-bin/url/nph-aws2_min_vis?tm2={date}&stn={stn}&disp=0&help=1&authKey={api_key}'
    api_data = api_data_get(url, timeout)
    data = api_data_process(api_data, 'lxml')
    return data




def find_after_min(now: str, delta_min: int) -> str:
    '''
    now 에서 delta_min 만큼 변화한 시간을 문자열로 리턴한다\n
    now = '202304151420' 와 같은 형식의 문자열\n
    delta_min = 시간 변화(분 단위의 정수)
    '''
    now = datetime.datetime.strptime(now,'%Y%m%d%H%M')
    past = (now + datetime.timedelta(minutes=delta_min)).strftime('%Y%m%d%H%M')
    
    return past



def past_weather_load(stn: str, api_key: str, date: str, timeout: int = 30) -> tuple:
    '''
    date 기준으로 과거 4시간 동안의 기록을 분 단위로 얻어와서\n
    가변길이 튜플로 정리된 정보를 리턴한다\n
    첫번째 원소 => 넘파이 배열(현천의 고유값들)\n
    두번째 원소 => 넘파이 배열(해당 고유값 별 갯수)
    '''
    now = datetime.datetime.strptime(date,'%Y%m%d%H%M')
    past = (now + datetime.timedelta(hours=-4)).strftime('%Y%m%d%H%M')

    url = f'https://apihub.kma.go.kr/api/typ01/cgi-bin/url/nph-aws2_min_vis?tm1={past}&tm2={date}&stn={stn}&disp=0&help=1&authKey={api_key}'
    api_data = api_data_get(url, timeout)
    
    soup = BeautifulSoup(api_data, features='lxml')
    front = soup.text.split('\n')

    real  = []
    for i in range(len(front)-1): #마지막 '\n' 인덱싱 에러 발생 방지
        if(front[i][0] != "#"):
            front[i] = front[i].split()
            #print(front[i])
            real.append(front[i][-2])
            

    return np.unique(real, return_counts=True)




def predict_time_fix(time_str: str) -> tuple:
    # 기상청 예보 생성 시간별로 제공해주는 예보 시각이 다르다.
    # 단기예보
    # Base_time : 0200, 0500, 0800, 1100, 1400, 1700, 2000, 2300 (1일 8회)
    # API 제공 시간(~이후) : 02:10, 05:10, 08:10, 11:10, 14:10, 17:10, 20:10, 23:10
    time_str = str(time_str)
    day = time_str[:8]
    time = time_str[8:]

    if int(time) < 210:
        day = ( datetime.datetime.now() - datetime.timedelta(1) ).strftime('%Y%m%d')
        time = '2300'

    if 210 <= int(time) <= 510:
        time = '0200'
    if 511 <= int(time) <= 810:
        time = '0500'
    if 811 <= int(time) <= 1110:
        time = '0800'
    if 1111 <= int(time) <= 1410:
        time = '1100'
    if 1411 <= int(time) <= 1710:
        time = '1400'
    if 1711 <= int(time) <= 2010:
        time = '1700'
    if 2011 <= int(time) <= 2310:
        time = '2000'
    if 2311 <= int(time) <= 2359:
        time = '2300'

    return day, time



def fcstValue_fix_PCP(pcp: str) -> float:
    replace = None

    if pcp == '강수없음':
        replace = 0
    if pcp == '1.0mm 미만':
        replace = 0.5

    match = re.match(r'(\d+\.\d+)mm', pcp) # '실수mm' 형태의 문자열이 감지되면 실수부 추출
    if match:
        replace = float(match.group(1))

    if pcp == '30.0~50.0mm':
        replace = 30.0
    if pcp == '50.0mm 이상':
        replace = 51.0
    
    return replace



def fcstValue_fix_SNO(sno: str) -> float:
    replace = None

    if sno == '적설없음':
        replace = 0
    if sno == '1.0cm 미만':
        replace = 0.5

    match = re.match(r'(\d+\.\d+)cm', sno)
    if match:
        replace = float(match.group(1))

    if sno == '5.0cm 이상':
        replace = 5.1
    
    return replace




    
def predict_data_load(datalist: List[str], timeout:int = 30)-> np.ndarray:
    '''
    ## List[str] 요구 입력
    ## api_key2: str, today: str, today_time: str, lx: str, ly: str


    기준 시간으로부터(현재시간 x) 5시간치의 일기 예보를 얻어온다 \n
    http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst \n
    api_key2 = 'eqTbu5tgsBlxHlliXVpp4A6FZyGJCS6ct%2FQWVPZuhRy3x05IGhAHlr0U9b%2B4qPEUNfrWVf2n5FtdffkCi33MQg%3D%3D'\n
    today = '20230421' # 현재 날짜로 설정할 값, 2~3일 전 날짜 사용시 api 리턴 결과 없음 주의\n
    today_time = '0537' # 현재 시간으로 설정할 값\n
    location_x = '55'  # 격자구역 x 정보\n
    location_y = '127' # 격자구역 y 정보\n

    
    api 리턴값 예시
    <items>
        <item>
            <baseDate>20230422</baseDate> #공통
            <baseTime>0500</baseTime> #공통
            <category>TMP</category> #카테고리, 유일값
            <fcstDate>20230422</fcstDate> #공통
            <fcstTime>0600</fcstTime> #공통
            <fcstValue>9</fcstValue> #실제 값
            <nx>55</nx> #공통
            <ny>127</ny> #공통
        </item>
    <item> 

    # 이상이 시간, 카테고리별로 반복된다. 매 시간(정시) 별 자료를 받을 수 있으며, 각 시간당 12개의 항목이 있다. 
    예시. # data = soup.select('item')
    202304220500 TMP 202304220600 9 55 127 #1시간 기온/ 10 / ºC
    202304220500 UUU 202304220600 -1.3 55 127 #풍속(동서성분)/ 12 / m/s
    202304220500 VVV 202304220600 -0.9 55 127 #풍속(남북성분)/ 12 / m/s
    202304220500 VEC 202304220600 57 55 127 #풍향/ 10/ deg
    202304220500 WSD 202304220600 1.7 55 127 #풍속/ 10/ m/s
    202304220500 SKY 202304220600 4 55 127 #하늘 상태/ 4/ 코드값
    202304220500 PTY 202304220600 0 55 127 #강수형태/ 4 / 코드값
    202304220500 POP 202304220600 30 55 127 #강수확률/ 8 / %
    202304220500 WAV 202304220600 0 55 127 #파고/ 8/ M
    202304220500 PCP 202304220600 강수없음 55 127 #1시간 강수량/ 8/ 범주(1 mm)
    202304220500 REH 202304220600 60 55 127 #습도/ 8 / %
    202304220500 SNO 202304220600 적설없음 55 127 #1시간 신적설/ 8/ 범주(1 cm)


    결과 값을 넘파이 배열 형태로 정리해서 넘겨준다.
    [[10   0.1     0  269  0.1  1  0  0  0  강수없음  65  적설없음]
      [9  -0.5  -0.2   72  0.6  1  0  0  0  강수없음  70  적설없음]
      [9    -1  -0.1   85  1.1  1  0  0  0  강수없음  70  적설없음]
      [7  -1.5     0   90  1.6  1  0  0  0  강수없음  75  적설없음]]
    
    하늘상태(SKY) 코드 : 맑음(1), 구름많음(3), 흐림(4)
    강수형태(PTY) 코드 : (단기) 없음(0), 비(1), 비/눈(2), 눈(3), 소나기(4) 


    강수량(RN1, PCP) 범주 및 표시방법(값)
    0.1 ~ 1.0mm 미만 -> 1.0mm 미만
    1.0mm 이상 30.0mm 미만 -> 실수값+mm (1.0mm~29.9mm)
    30.0 mm 이상 50.0 mm 미만 -> 30.0~50.0mm 
    50.0 mm 이상 -> 50.0mm 이상

    예) PCP = 6.2 일 경우 강수량은 6.2mm
    PCP = 30 일 경우 강수량은 30.0~50.0mm


    동서바람성분(UUU) : 동(+표기), 서(-표기)
    남북바람성분(VVV) : 북(+표기), 남(-표기)



    '''
    api_key2, today, today_time, lx, ly = datalist
    today, today_time = predict_time_fix(today + today_time)
    print(today, today_time)

    url = f'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst?serviceKey={api_key2}&numOfRows=61&pageNo=1&base_date={today}&base_time={today_time}&nx={lx}&ny={ly}'  
    #print(url)
    api_data = api_data_get(url, timeout)

    soup = BeautifulSoup(api_data, features='xml')
    category = soup.select('category')
    fcstValue = soup.select('fcstValue')

    data = []
    cut = 0
    for it in range(len(category)):
        if category[it].text == 'TMP':
            cut = cut + 1
            if cut > 5: break

        if category[it].text == 'TMN' or category[it].text == 'TMX':  #일 최저기온 최고기온 항목 제거(언제 제공될 지 알수없음)
            pass
        else:
            if category[it].text == 'PCP':
                data.append(fcstValue_fix_PCP(fcstValue[it].text))
            elif category[it].text == 'SNO':
                data.append(fcstValue_fix_SNO(fcstValue[it].text))
            else:
                data.append(fcstValue[it].text)

    data = np.array(data).reshape(-1, 12)
    data = data.tolist()

    for i in range(len(data)):
        #print(find_after_min(today+today_time, i*60))
        data[i].insert(0, today+today_time)
        data[i].insert(1, find_after_min(today+today_time, i*60))
        data[i].append(lx)
        data[i].append(ly)
        #tmp = np.insert(data[i], 0, find_after_min(today+today_time, i*60))
        #tmp = np.insert(tmp, 0, today+today_time)
        #ret.append(tmp)

    return data
    







if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(prog=sys.argv[0], add_help=True)
        parser.add_argument('-tn', '--table_name', type=str)

        subparser = parser.add_subparsers(dest='mode', help='mode help')

        ## subparser for command 'subparser'
        # insert
        parser_insert = subparser.add_parser('insert', add_help=True)
        parser_insert.add_argument('--data', nargs='*', type=str)
        parser_insert.add_argument('--columns', nargs='*', type=str)

        # output
        parser_output = subparser.add_parser('output', add_help=True)
        parser_output.add_argument('--columns', nargs='*', action='store', type=str, default=[])
        group_output = parser_output.add_mutually_exclusive_group() ##
        group_output.add_argument('--range', nargs=2, type=str)
        group_output.add_argument('--before', action='store', type=str)
        group_output.add_argument('--after', action='store', type=str)
        group_output.add_argument('--pointer', action='store', type=str)

        # delete
        parser_delete = subparser.add_parser('delete', add_help=True)
        group_delete = parser_delete.add_mutually_exclusive_group(required=True) ##
        group_delete.add_argument('--range', nargs=2, type=str)
        group_delete.add_argument('--before', action='store', type=str)
        group_delete.add_argument('--after', action='store', type=str)
        group_delete.add_argument('--pointer', action='store', type=str)

        # update
        parser_update = subparser.add_parser('update', add_help=True)
        parser_update.add_argument('--pointer', action='store', type=str, required=True)
        parser_update.add_argument('--data', nargs='+', type=str, required=True)
        parser_update.add_argument('--columns', nargs='+', type=str, required=True)

        args = parser.parse_args()

        # STN = '548'
        # API_KEY = 'aaZrhx_QRmyma4cf0PZsug'
        # API_KEY2 = 'eqTbu5tgsBlxHlliXVpp4A6FZyGJCS6ct%2FQWVPZuhRy3x05IGhAHlr0U9b%2B4qPEUNfrWVf2n5FtdffkCi33MQg%3D%3D'

        sys.exit(0)

    except Exception as e:
        print(f'{e}', file=sys.stderr)
        sys.exit(1)