#openCV 에서는 키보드 입력을 받기 위해 waitKey() 함수를 제공한다.
#waitKey() 함수는 요소로 주어지는 시간동안 사용자의 키보드 입력을 기다린다.
#0 이면 입력이 주어질 때까지 무제한으로 기다리고, 1이상이면 주어진 시간(ms) 동안 기다리고 다음줄에 있는 코드를 실행한다.



#에지 검출을 처리하는 코드를 
#키보드 입력에 따라 원하는 단계의 모습을 화면에 출력한다.
#1이면 원본, 2이면 그레이 스케일, 3이면 에지검출을 보여준다.

import cv2 as cv
import sys

cap = cv.VideoCapture(0)
if cap.isOpened() == False:
    print('카메라가 연결되지 않습니다.')
    sys.exit(1)

#보여줄 결과를 지정하기 위한 변수
step = 1

while(True):

    #img_frame 변수에 대입된 이미지를 윈도우에 보여주게 됩니다.
    #처음에는 카메라에서 캡처된 컬러 이미지입니다.
    ret, img_frame = cap.read()

    if ret == False:
        print('캡처 실패. ')
        break

    #step이 2 이상이면 img_frame 에는 그레이 스케일 이미지가 대입된다.
    if step > 1:
        img_frame = cv.cvtColor(img_frame, cv.COLOR_BGR2GRAY)

        #step 이 3이면 img_frame 에는 에지 이미지가 대입됩니다.
        if step > 2:
            img_frame = cv.Canny(img_frame, 30 ,90)
        

    #앞에서 처리된 결과에 따라 다른 이미지가 Result 윈도우에 보여지게 됩니다.
    cv.imshow('Result', img_frame)

    #1ms 동안 키보드 입력을 대기합니다.
    key = cv.waitKey(1)

    if key == 27:  #ESC 키
        break

    #입력된 키에 따라서 step 변수에 다른 값을 대입합니다.
    #파이썬에서는 ord 함수를 사용하여 문자를 아스키 코드로 바꿀수 있다.
    elif key == ord('1'):
        step = 1
    elif key == ord('2'):
        step = 2
    elif key == ord('3'):
        step = 3

cap.release()
cv.destroyAllWindows()