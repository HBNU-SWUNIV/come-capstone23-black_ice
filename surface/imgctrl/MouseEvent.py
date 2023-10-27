#openCV를 사용해 생성한 윈도우에서 발생하는 마우스 이벤트를 감지하기 위해 콜백함수를 사용 가능
#setMouseCallback 함수를 사용하여 특정 윈도우를 위한 콜백함수를 지정하면 
#마우스 이벤트가 발생할 때 마다 콜백함수가 호출된다


#네 가지 이벤트를 사용해 윈도우에 사각형/원을 그리게 된다.
#원하는 위치에서 왼쪽 버튼을 누른 채 이동하다가 손을 떼면 사각형/원을 그리게 된다.
#마우스 오른쪽 버튼을 누를때마다 설정된 도형을 바꿀수 있다.

#마우스 왼쪽 버튼 EVENT_LBUTTONDOWN 이벤트
#누르던 왼쪽버튼에서 손을 떼면 발생하는 EVENT_LBUTTONUP 이벤트
#마우스 오른쪽 버튼 EVENT_RBUTTONDOWN 이벤트
#마우스 이동 시 발생하는 EVENT_MOUSEMOVE 이벤트


import cv2 as cv
import numpy as np
import random

#마우스 왼쪽 버튼 상태 체크를 위해 사용
mouse_is_pressing = False

#현재 그리기 모드 선택을 위해 사용(원/사각형)
drawing_mode = True

#최초로 마우스 왼쪽 버튼 누른 위치를 저장하기 위해 사용
start_x, start_y = -1, -1

#도형 내부를 채울 때 사용할 색 지정시 사용
color = (255,255,255)

#그리기 결과를 저장할 이미지
img = np.zeros((512, 512, 3), np.uint8)


#마우스 이벤트 발생 시 호출될 함수 정의
def mouse_callback(event, x, y, flags, param):
    global color, start_x, start_y, drawing_mode, mouse_is_pressing

    #마우스를 이동하면 발생하는 이벤트
    if event == cv.EVENT_MOUSEMOVE:
        #마우스 왼쪽 버튼을 누른 채 이동하면
        if mouse_is_pressing == True:
            #이동된 마우스 커서 위치를 반영해서 사각형/원을 그린다.
            if drawing_mode == True:
                cv.rectangle(img, (start_x, start_y), (x, y), color, -1)
            else:
                cv.circle(img, (start_x,start_y), max(abs(start_x - x),abs(start_y - y)), color, -1)

    #마우스 왼쪽 버튼을 누르면 발생하는 이벤트
    elif event == cv.EVENT_LBUTTONDOWN:
        #랜덤으로(blue, green, red)로 사용될 색을 생성한다.
        color = (random.randrange(256), random.randrange(256), random.randrange(256))
        #마우스 왼쪽 버튼을 누른 것을 체크
        mouse_is_pressing = True
        #마우스 왼쪽 버튼을 누른 위치를 저장
        start_x, start_y = x, y


    #누르고있는 마우스 왼쪽 버튼에서 손을 떼면 발생하는 이벤트
    elif event == cv.EVENT_LBUTTONUP:
        #마우스 왼쪽 버튼에서 손뗀 것을 체크
        mouse_is_pressing = False

        #왼쪽 버튼을 누른 위치와 손뗀 위치를 사용해 사각형/원을 그린다.
        if drawing_mode == True:
            cv.rectangle(img, (start_x, start_y), (x, y), color, -1)
        else:
            cv.circle(img, (start_x,start_y), max(abs(start_x - x),abs(start_y - y)), color, -1)

    
    #마우스 오른쪽 버튼을 누를 때 발생하는 이벤트
    elif event == cv.EVENT_RBUTTONDOWN:
        drawing_mode = 1 - drawing_mode

cv.namedWindow('Image')

#지정한 윈도우를 위한 마우스 콜백함수를 지정
cv.setMouseCallback('Image', mouse_callback)

while(1):
    cv.imshow('Image',img)

    Key = cv.waitKey(1)
    if Key == 27:
        break


cv.destroyAllWindows()