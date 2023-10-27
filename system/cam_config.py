import cv2 as cv
import numpy as np
import os
import sys

#print(cv.__version__)
def write_data_to_file(filename, data_dict):
    with open(filename, "w") as file:
        for key, values in data_dict.items():
            line = f"{key}={','.join(map(str, values))}\n"
            file.write(line)



if __name__ == "__main__":
    camera = cv.VideoCapture(0)  # 0=기본 카메라. 여러 카메라가 연결되어 있는 경우 다른 번호 할당 가능
    if not camera.isOpened():
        print("카메라를 열 수 없습니다.")
        exit(1)

    #카메라 이미지 로딩과 보여주기를 반복하면 영상이 됨
    while(True):
    
        #카메라에서 이미지를 읽어옵니다.
        ret, img_frame = camera.read()

        #ret 리턴값이 False이면 캡처 실패
        if ret == False:
            print("영상을 읽을 수 없습니다.")
            camera.release()
            exit(1)
    
        #윈도우에 보여주기
        cv.imshow('camera',img_frame)

        #키보드 입력 대기
        key = cv.waitKey(0) 

        #ESC키가 입력시 반복 중지
        if key == 27:
            print('카메라 이미지 고정')
            break
        else:
            print('재촬영')

    camera.release()
    cv.destroyWindow('camera')


    ## 2. esc로 와일문 나온 후 영역 지정
    #마우스 클릭한 좌표를 저장할 리스트(입력 이미지에서 지정할 사각형 꼭짓점)
    src = np.zeros([4, 2], dtype=np.float32)
    idx = 0

    def mouse_callback(event, x, y, flags, param):
        global point_list, idx

        #마우스 왼쪽 버튼을 누를 때마다 좌표를 리스트에 저장
        if event == cv.EVENT_LBUTTONDOWN:
            if idx < 4:
                src[idx] = (x,y)
                idx = idx + 1

                #print("(%d , %d)" %(x,y))
                cv.circle(img_original, (x,y), 3, (0,0,255), -1)


    #마우스 콜백함수 등록
    cv.namedWindow('fix img')
    cv.setMouseCallback('fix img', mouse_callback)

#사용할 이미지를 불러온다.
    img_original = img_frame.copy()
    height, width = img_frame.shape[:2]

    #반복하면서 마우스 클릭으로 네 점을 지정
    while(True):
        cv.imshow('fix img', img_original)

        #space바를 누르면 루프에서 나온다.
        if cv.waitKey(1) == 32:
            break

    if idx <= 2:
        print('좌표값이 올바르게 지정되지 않았습니다')
        print('좌측 상단, 우측 상단, 좌측 하단, 우측 하단 순서로 올바르게 좌표를 지정해 주십시오')
        exit(1)

    #퍼스펙티브 변환 결과 미리보기
    #출력 이미지의 사각형 꼭짓점
    dst = np.float32([[0, 0], [width, 0], [0, height], [width, height]])

    #퍼스펙티브 변환 행렬 생성
    m = cv.getPerspectiveTransform(src, dst)

    #퍼스펙티브 변환,리사이즈 적용
    img_result = cv.warpPerspective(img_frame, m, (width, height))
    img_result = cv.resize(img_result, dsize=(400, 400), interpolation=cv.INTER_AREA)

    #결과 보기
    cv.imshow('result', img_result)


    print('저장 : \'y\', 저장하지 않음 : 나머지 키')
    save = cv.waitKey(0)
    if save == ord('y'):
        data = {
            "left_top": src[0],
            "right_top": src[1],
            "left_bottom": src[2],
            "right_bottom": src[3]
        }
        if getattr(sys, 'frozen', False):
            #실행파일로 실행한 경우, 실행파일을 보관한 디렉토리의 full path를 취득
            file_path = (os.path.dirname(os.path.abspath(sys.executable)) +'/resource/cam_config.txt')
            #print('exe', file_path)
        else:
            file_path = (os.path.dirname(os.path.abspath(__file__)) + '/resource/cam_config.txt')
        write_data_to_file(file_path, data)
        print('저장 후 종료')
    else:
        print('저장하지 않고 종료')
    cv.destroyAllWindows()
    exit(0)