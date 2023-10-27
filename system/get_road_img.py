import cv2 as cv
import numpy as np
import os
import sys
import argparse
import datetime

def read_data_from_file(filename):
    data_dict = {}
    with open(filename, "r") as file:
        for line in file:
            key, values_str = line.strip().split("=")
            values = list(map(float, values_str.split(',')))
            data_dict[key] = values
    
    return data_dict


def capture_and_save_bitmap_image():
    camera = cv.VideoCapture(0)  # 0=기본 카메라. 여러 카메라가 연결되어 있는 경우 다른 번호 할당 가능

    if not camera.isOpened():
        print("카메라를 열 수 없습니다.")
        sys.exit(1)

    # 카메라로부터 영상 읽기
    ret, frame = camera.read()

    if not ret:
        print("영상을 읽을 수 없습니다.")
        camera.release()
        sys.exit(1)
    camera.release()

    return frame

    



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--all_type_save', action='store_true', default=False) #두 형식 모두 저장
    parser.add_argument('-b', '--bmp_type_save', action='store_true', default=False) #비트맵 형식 저장
    parser.add_argument('-p', '--png_type_save', action='store_true', default=False) #png 형식 저장

    parser.add_argument('-path', '--result_path', nargs=1, type=str, help='저장경로 지정')

    try:
        args = parser.parse_args() #명령줄 입력을 인자로 변환
    except argparse.ArgumentError as e:
        print(f"Error: {e}")
        sys.exit(1)


    img = capture_and_save_bitmap_image()
    width, height = img.shape[:2]

    if getattr(sys, 'frozen', False):
        #실행파일로 실행한 경우, 실행파일을 보관한 디렉토리의 full path를 취득
        file_path = (os.path.dirname(os.path.abspath(sys.executable)) +'/resource/cam_config.txt')
    else:
        file_path = (os.path.dirname(os.path.abspath(__file__)) + '/resource/cam_config.txt')
    config = read_data_from_file(file_path)

    scr = np.zeros([4, 2], dtype=np.float32)
    scr[0] = np.array(config['left_top'])
    scr[1] = np.array(config['right_top'])
    scr[2] = np.array(config['left_bottom'])
    scr[3] = np.array(config['right_bottom'])
    dst = np.float32([[0, 0], [width, 0], [0, height], [width, height]])

    #퍼스펙티브 변환 행렬 생성
    m = cv.getPerspectiveTransform(scr, dst)

    #퍼스펙티브 변환,리사이즈 적용
    img_result = cv.warpPerspective(img, m, (width, height))
    img_result = cv.resize(img_result, dsize=(400, 400), interpolation=cv.INTER_AREA)


    # 영상 저장
    times = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'))
    if args.all_type_save:
        if args.result_path:
            try:
                cv.imwrite(f'{args.result_path[0]}/{times}.png', img_result)
                cv.imwrite(f'{args.result_path[0]}/{times}.bmp', img_result)
                print(f"영상이 {args.result_path[0]} 위치에 png, bmp 형식으로 저장되었습니다.")
            except:
                print('저장 실패')
                sys.exit(1)
            sys.exit(0)
        else:
            try:
                cv.imwrite(f'{times}.png', img_result)
                cv.imwrite(f'{times}.bmp', img_result)
                print("영상이 png, bmp 형식으로 저장되었습니다.")
            except:
                print('저장 실패')
                sys.exit(1)
            sys.exit(0)
    
    if args.bmp_type_save:
        if args.result_path:
            try:
                cv.imwrite(f'{args.result_path[0]}/{times}.bmp', img_result)
                print(f"영상이 {args.result_path[0]} 위치에 bmp 형식으로 저장되었습니다.")
            except:
                print('저장 실패')
                sys.exit(1)
            sys.exit(0)
        else:
            try:
                cv.imwrite(f'{times}.bmp', img_result)
                print("영상이 bmp 형식으로 저장되었습니다.")
            except:
                print('저장 실패')
                sys.exit(1)
            sys.exit(0)

    if args.png_type_save:
        if args.result_path:
            try:
                cv.imwrite(f'{args.result_path[0]}/{times}.png', img_result)
                print(f"영상이 {args.result_path[0]} 위치에 png 형식으로 저장되었습니다.")
            except:
                print('저장 실패')
                sys.exit(1)
            sys.exit(0)
        else:
            try:
                cv.imwrite(f'{times}.png', img_result)
                print("영상이 png 형식으로 저장되었습니다.")
            except:
                print('저장 실패')
                sys.exit(1)
            sys.exit(0)

    parser.print_help()
    sys.exit(0)