import math
import argparse
import sys

NX = 149 # X축 격자점 수
NY = 253 # Y축 격자점 수

# 위도 latitude(가로줄), 경도 longitude(세로줄)
# lamc 파라미터
Re = 6371.00877 # 사용할 지구반경 [ km ]
grid = 5.0 # 격자간격 [ km ]
slat1 = 30.0 # 표준위도1 [degree]
slat2 = 60.0 # 표준위도2 [degree]
olon = 126.0 # 기준점의 경도 [degree]
olat = 38.0 # 기준점의 위도 [degree]
xo = 210 / grid # 기준점의 X좌표 [격자거리]
yo = 675 / grid # 기준점의 Y좌표 [격자거리]


PI = math.asin(1.0) * 2.0
DEGRAD = PI / 180.0
RADDEG = 180.0 / PI

re = Re / grid
slat1 = slat1 * DEGRAD
slat2 = slat2 * DEGRAD
olon = olon * DEGRAD
olat = olat * DEGRAD

sn = math.tan(PI * 0.25 + slat2 * 0.5) / math.tan(PI * 0.25 + slat1 * 0.5)
sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
sf = math.tan(PI * 0.25 + slat1 * 0.5)
sf = pow(sf, sn) * math.cos(slat1) / sn
ro = math.tan(PI * 0.25 + olat * 0.5)
ro = re * sf / pow(ro, sn)



def grid_conv_lonlat(ix: int, iy: int) -> tuple:
    #(X,Y) -> 위경도

    theta = (float)(0.0)
    ix = ix - 1
    iy = iy - 1

    xn = ix - xo
    yn = ro - iy + yo
    ra = math.sqrt(xn * xn + yn * yn)
    if (sn < 0.0): - ra #값 버림, 디버깅 용도로 추정
    alat = pow((re * sf /ra), (1.0 / sn))
    alat = 2.0 * math.atan(alat) - PI * 0.5

    if (math.fabs(xn) <= 0.0):
        theta = 0.0
    else:
        if (math.fabs(yn) <= 0.0):
            theta = PI * 0.5
            if (xn < 0.0): - theta #값 버림, 디버깅 용도로 추정
            else:
                theta = math.atan2(xn, yn)
    alon = theta / sn + olon
    lat = (float)(alat * RADDEG)
    lon = (float)(alon * RADDEG)

    return lat, lon


def lonlat_conv_grid(lon: float, lat: float) -> tuple:
    #위경도 -> (X,Y)
    #위경도 순서 틀리지 말 것. 연산 결과가 복소수가 되어 에러 발 생.
    #lon = 경도, lat = 위도

    ra = math.tan(PI * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / pow(ra, sn)
    theta = lon * DEGRAD - olon
    if (theta > PI): 
        theta -= 2.0 * PI
    if (theta < -PI): 
        theta += 2.0 * PI
    theta *= sn
    x = int(float(ra * math.sin(theta)) + xo + 1.5)
    y = int(float(ro - ra * math.cos(theta)) + yo + 1.5)

    return x, y



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    #위치정보 인자 받기(위경도)
    parser.add_argument('-g', '--location_grid', nargs=2, type=int, help='격자구간 입력')
    #위치정보 인자 받기(격자)
    parser.add_argument('-l', '--location_lonlat', nargs=2, type=float, help='위경도 입력')


    try:
        args = parser.parse_args() #명령줄 입력을 인자로 변환
    except argparse.ArgumentError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # -g 옵션
    if args.location_grid:
        print(*grid_conv_lonlat(args.location_grid[0],args.location_grid[1]))
        sys.exit(0)
    
    # -l 옵션
    if args.location_lonlat:
        print(*lonlat_conv_grid(args.location_lonlat[0],args.location_lonlat[1]))
        sys.exit(0)

    
'''
사용 예시.

lat1, lon2 = grid_conv_lonlat(59, 125)
print(lat1, lon2)   # 37.488199604262704 126.0

x, y = lonlat_conv_grid(126.929810, 37.488201)
print(x, y) #59 125

'''