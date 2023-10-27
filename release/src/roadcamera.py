## 0. Module Import
# 클래스 힌트, iterable 확인
from typing import List, Iterable
# 입력 옵션, 인자 파싱
import argparse
# 프로그램 종료, 경로 입력
import sys
# 파일 저장, 디렉토리 생성
import os
# 카메라 제어, 이미지 저장, 원근 변환
import numpy as np
import cv2
from datetime import datetime
import time
# 에러 출력
import traceback





## 1. import camera configure function, export camera configure function, image filming function
# 라이브러리 겸용 함수 클래스, 메소드 선언
class RoadCamera:
    '''
    '''

    def __init__(
            self, 
            port_cam: int=None, 
            img_save_name: str=None, 
            img_save_force: bool=False, 
            img_format: str=None, 
            perspective_locations: List[float]=None, 
            perspective_after_size: List[int]=None, 
            configure_save_name: str=None, 
            configure_save_force: bool=False, 

            configure_load_path:str = None,
    ) -> None:
        '''
        ## Input arguments
            - 생성자의 인수로는 각 카메라 마다 전역적으로 사용될 변수가 입력됩니다.
            - port_cam : \n
                - 카메라의 포트 번호 (ex. 0, 1, 2, ...)\n
            - img_save_path : \n
                - 이미지 저장 경로 (ex. '../Data/saved_images/')
            - perspective_locations : \n
                - 원근 변환 시 좌표[8] (ex.(0.0, 0.0, 100.0, 0.0, 0.0, 100.0, 100.0, 100.0)) \n
                - 좌표는 X->Y, 좌상단, 우상단, 좌하단, 우하단 순으로 설정해주십시오. \n
            - after_perspective_size : \n
                - 원근 변환 후 이미지 크기(width, height)[2] (ex.(400, 400)) \n

        ## 주의사항
            - 생성자 및 인자 할당 메서드 외 다른 메서드는 self 인자만 사용해주십시오.
        '''

        # 매개변수 -> 인스턴스 변수
        self.port_cam = port_cam
        self.img_save_name = img_save_name
        self.img_save_force = img_save_force
        self.img_format = img_format
        self.perspective_locations = perspective_locations
        self.perspective_after_size = perspective_after_size
        self.configure_save_name = configure_save_name
        self.configure_save_force = configure_save_force

        self.configure_load_path = configure_load_path
        


    def import_configure_file(
            self, 
    ) -> None:
        '''
        ## Introduction
            - configure_path에 존재하는 설정 파일을 파싱해 객체에 저장합니다.\n

        ### Configure file introduction
                port_cam: 카메라 포트 번호입니다.\n
                perspective_locations: 원근 변환 기준점 좌표입니다.\n
                after_perspective_size: 원근 변환 후 이미지 크기입니다. (width, height)\n
                img_save_path: 이미지 저장 경로입니다.\n

        ### Configure file format example
                port_cam = 0\n
                perspective_locations = 0.0, 0.0, 0.0, 100.0, 100.0, 0.0, 100.0, 100.0\n
                after_perspective_size = 400, 400\n
                img_save_path = ~/Desktop/Data/\n
                ...
        '''

        # 파일 파싱
        # 파일 형식은 <option>=<value1>, <value2>, ...
        args_list = []
        with open(self.configure_load_path, 'r') as configure_file:
            for line in configure_file:
                option, values = line.split('=')
                args_list.append('--' + option.strip())
                args_list.extend(value.strip() for value in values.split(','))
    

        # 옵션 형식 정의
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('--port_cam', type=int, nargs=1, action='store')
        parser.add_argument('--img_save_name', type=str, nargs=1, action='store')
        parser.add_argument('--img_save_force', type=bool, choices=[True, False], action='store')
        parser.add_argument('--img_format', type=str, choices=['png', 'bmp'], action='store')
        parser.add_argument('--perspective_locations', type=float, nargs=8, action='store')
        parser.add_argument('--perspective_after_size', type=int, nargs=2, action='store')
        parser.add_argument('--configure_save_name', type=str, nargs=1, action='store')
        parser.add_argument('--configure_save_force', type=bool, choices=[True, False], action='store')

        args = parser.parse_args(args_list)

        
        # 올바른 옵션값 -> 인스턴스 내부 데이터
        # iterable, string -> 그대로 삽입
            # 허나 단일 객체가 iterable 클래스에 캡슐화된 경우는 캡슐화 해제한다.
        for key, value in vars(args).items():
            if key in vars(self) and value != None:
                if isinstance(value, Iterable) and not isinstance(value, str) and len(value) == 1:
                    self.__dict__[key] = value[0]
                else:
                    self.__dict__[key] = value
        

    
    def export_configure(
            self, 
    ) -> str:
        '''
        ## Introduce
            - 객체 내의 설정값을 출력하는 메소드입니다. \n
            - 여러 줄의 문자열로 반환되며, 각 줄마다 각 설정값에 대한 정보가 반환됩니다. \n
            - 설정 파일과 형식(format)이 같습니다. \n
            - 따로 파일을 생성하지 않고 문자열로 반환합니다.

        ### Configure file format example
                port_cam = 0\n
                perspective_locations = 0.0, 0.0, 0.0, 100.0, 100.0, 0.0, 100.0, 100.0\n
                after_perspective_size = 400, 400\n
                img_save_path = ~/Desktop/Data/\n
                ...
        '''

        # 인스턴스 내부 데이터 형식화
        # Nonetype은 기록하지 않음
        # 단일 데이터 객체 및 단일 string 등은 <key>=<value>
        # iterable 데이터 형식은 <key>=<value1>, <value2>, ...
        configure_text = ''
        for key, value in vars(self).items():
            if isinstance(value, Iterable) and not isinstance(value, str):
                configure_text += f'{key}={", ".join(map(str, value))}\n'
            elif value != None:
                configure_text += f'{key}={str(value)}\n'


        # 결과 반환
        return configure_text
    


    def export_configure_file(
            self, 
    ) -> str:
        '''
        ## Introduce
            - 객체 내의 설정값을 파일에 출력하는 메소드입니다. \n
            - 파일의 형식은 export_configure()의 반환값과 같습니다. \n
            - 설정 파일과 형식(format)이 같습니다. \n
            - 파일 생성에 성공하면 파일 경로를 반환합니다.
        '''

        # 디렉토리명 분리 (디렉토리 표기가 없으면 현재 터미널 위치에 작성)
        if '/' in self.configure_save_name:
            pivot = self.configure_save_name.rfind('/') + 1
            configure_directory = self.configure_save_name[:pivot]
        else:
            configure_directory = './'
            self.configure_save_name = configure_directory + self.configure_save_name

        # configure_save_force == True이고 디렉토리 없으면 생성
        if self.configure_save_force and not os.path.exists(configure_directory):
            os.makedirs(configure_directory)
        
        # 설정값 파일에 쓰기
        with open(self.configure_save_name, 'w') as configure_file:
            configure_file.write(self.export_configure())

        
        # 결과(파일명) 반환
        return self.configure_save_name
    


    def configure_perspective_locations(
            self
    ) -> None:
        '''
        ## Introduce
            - GUI를 통해 직접 이미지 촬영 후 원근변환 좌표(perspective_locations)를 설정하는 메소드입니다. \n
            - 반환값은 없으며, export_configure()를 이용하기 바랍니다. \n
            - 변환 후 미리보기는 없으며, get_transformed_image()를 이용하기 바랍니다. \n
        ## Usage
            - 1. 사전에 설정한 port_cam으로 카메라를 오픈합니다. \n
            - 2. 샘플 이미지를 촬영 후 표시합니다. \n
            - 3. 정렬된 이미지 기준 좌표는 좌상단, 우상단, 좌하단, 우하단 순으로 설정해주십시오. \n
            - 4. 좌표 설정: 마우스_L / 재촬영, 좌표 초기화: 마우스_R 입니다.
            - 5. 4개의 좌표 설정 후 마우스_L 클릭시 설정이 완료됩니다.
        '''

        # 마우스 콜백 함수 정의
        def mouse_callback(event, x, y, flags, param):
            # 마우스 왼쪽 버튼 이벤트 설정 ( 좌표 설정 )
            if event == cv2.EVENT_LBUTTONUP and 0 <= param['idx'] < 4:
                # 마우스 좌표 -> perspective_locations[8]를 순회하며 저장
                param['perspective_locations'][param['idx']] = [x, y]
                # 인덱스 증가
                param['idx'] += 1
                # 표시 이미지에 클릭된 좌표 표시
                cv2.circle(img=param['image_displayed'], center=(x, y), radius=3, color=(0, 0, 255), thickness=-1)
                # 변경된 이미지 표시
                cv2.imshow(param['winname'], param['image_displayed'])
            
            # 마우스 왼쪽 버튼 이벤트 설정 ( 설정 완료 )
            elif event == cv2.EVENT_LBUTTONUP and param['idx'] >= 4:
                param['flag_configuring'] = False
            
            # 마우스 오른쪽 버튼 이벤트 설정
            if event == cv2.EVENT_RBUTTONUP:
                # perspective_locations[4][2] 초기화
                param['perspective_locations'] = [[-1.0, -1.0]] * 4
                # 인덱스 초기화
                param['idx'] = 0
                # 원본 이미지 재촬영
                param['image_original'] = param['camera'].read()[1]
                # 표시 이미지 원본으로 초기화
                param['image_displayed'] = param['image_original']
                # 변경된 이미지 표시
                cv2.imshow(param['winname'], param['image_displayed'])


        # 함수 실행 관련 리소스 저장 디렉토리 선언
        resources = {
            'camera': None, 
            'image_original': None, 
            'image_displayed': None, 
            'winname': '', 
            'perspective_locations': [], 
            'idx': None, 
            'flag_configuring': None
        }

        # 리소스 내용 설정, 초기화
        resources['camera'] = cv2.VideoCapture(self.port_cam, cv2.CAP_V4L)
        time.sleep(1) ## 카메라 조리개 대기
        resources['image_original'] = resources['camera'].read()[1]
        resources['image_displayed'] = resources['image_original'].copy()
        resources['winname'] = 'set ) Mouse_L  /  reset ) Mouse_R  /  complete ) Mouse_L after set 4 locations'
        resources['perspective_locations'] = [[-1.0, -1.0]] * 4
        resources['idx'] = 0
        resources['flag_configuring'] = True

        # 원근변환 좌표 설정
        cv2.namedWindow(resources['winname'])
        cv2.imshow(resources['winname'], resources['image_displayed'])
        cv2.setMouseCallback(resources['winname'], mouse_callback, param=resources)
        # 좌표 설정 완료 대기
        while resources['flag_configuring']:
            cv2.waitKey(1)
        # 설정 완료 후 창 닫기, 카메라 해제
        cv2.destroyWindow(resources['winname'])
        resources['camera'].release()


        # 결과 perspective_locations 설정
        self.perspective_locations = sum(resources['perspective_locations'], [])



    def get_transformed_image(
            self, 
    ) -> str:
        '''
        ## Introduce
            - 사전에 설정한 port_cam, perspective_locations를 이용해 이미지 촬영 후 원근 변환하여 저장합니다. \n
            - 실행에 성공하면 파일의 이름을 출력합니다. \n

        ## Input argument
            - img_filename : \n
                - 입력하면 생성되는 파일이 f'{img_save_path}/{img_filename}.{'png', 'bmp'}'로 저장됩니다. \n
                - 인자 미입력 시 파일 생성 시간으로 이름 설정됩니다. \n
            - img_format : \n
                - 이미지 파일의 포맷을 결정합니다.
            - img_save_force (default=False) : \n
                - True면 경로의 디렉토리가 존재하지 않아도 생성 후 저장합니다. \n
                - False면 경로가 유효하지 않을 시 에러가 발생합니다. \n
        '''

        # 사진 촬영
        camera = cv2.VideoCapture(self.port_cam, cv2.CAP_V4L)
        time.sleep(1) ## 카메라 조리개 대기
        image_original = camera.read()[1]
        camera.release()


        # 원근 변환
        W = self.perspective_after_size[0]
        H = self.perspective_after_size[1]
        dst = np.float32([[0, 0], [W, 0], [0, H], [W, H]])
        src = np.float32(self.perspective_locations).reshape((4, 2))

        matrix = cv2.getPerspectiveTransform(src, dst)
        image_transformed = cv2.warpPerspective(image_original, matrix, (W, H))


        # 디렉토리명 분리 (디렉토리 표기가 없으면 현재 터미널 위치에 작성)
        if '/' in self.img_save_name:
            pivot = self.img_save_name.rfind('/') + 1
            img_directory = self.img_save_name[:pivot]
        else:
            img_directory = './'
            self.img_save_name = img_directory + self.img_save_name

        # img_save_force == True이고 디렉토리 없으면 생성
        if self.img_save_force and not os.path.exists(img_directory):
            os.makedirs(img_directory)
        
        # 변환된 이미지 저장
        cv2.imwrite(self.img_save_name + '.' + self.img_format, image_transformed)


        # 이미지 파일 이름 반환
        return self.img_save_name + '.' + self.img_format
    




## 2. Main
# 실행 파일로 작동 시 기능
if __name__ == '__main__':
    try:
        # 입력 인자 파싱
        parser = argparse.ArgumentParser(prog=sys.argv[0], add_help=True)
        subparser = parser.add_subparsers(dest='mode', help='mode help')

        # subparser for command "configure"
        parser_configure = subparser.add_parser('configure', add_help=True, help='configure help')
        parser_configure.add_argument('--port_cam', type=int, nargs=1, action='store', required=True)
        parser_configure.add_argument('--img_save_name', type=str, nargs=1, action='store', required=True)
        parser_configure.add_argument('--img_save_force', type=bool, choices=[True, False], action='store', default=False)
        parser_configure.add_argument('--img_format', type=str, choices=['png', 'bmp'], action='store', default='png')
        parser_configure.add_argument('--perspective_locations', type=float, nargs=8, action='store')
        parser_configure.add_argument('--perspective_after_size', type=int, nargs=2, action='store', required=True)
        parser_configure.add_argument('--configure_save_name', type=str, nargs=1, action='store', required=True)
        parser_configure.add_argument('--configure_save_force', type=bool, choices=[True, False], action='store', default=False)
        # subparser for command "getimage"
        parser_getimage = subparser.add_parser('getimage', add_help=True, help='getimage help')
        parser_getimage.add_argument('--configure_load_path', type=str, nargs=1, action='store', required=True)

        args = parser.parse_args()


        # 캡슐화 해제
        # iterable, string -> 그대로 삽입
            # 허나 단일 객체가 iterable 클래스에 캡슐화된 경우는 캡슐화 해제한다.
        for key, value in vars(args).items():
            if isinstance(value, Iterable) and not isinstance(value, str) and len(value) == 1:
                args.__dict__[key] = value[0]
            else:
                args.__dict__[key] = value

        
        # mode 따라 실행
        # configure
        if args.mode == 'configure':
            result = RoadCamera(
                port_cam=args.port_cam, 
                img_save_name=args.img_save_name, 
                img_save_force=args.img_save_force, 
                img_format=args.img_format, 
                perspective_locations=args.perspective_locations, 
                perspective_after_size=args.perspective_after_size, 
                configure_save_name=args.configure_save_name, 
                configure_save_force=args.configure_save_force, 
            )

            if args.perspective_locations == None:
                result.configure_perspective_locations()
            
            # 설정파일 생성 후 경로 출력하고 종료
            print(f"{datetime.now().strftime('%Y%m%d%H%M%S.%f')}", result.export_configure_file(), file=sys.stdout)
            sys.stdout.flush()
            sys.exit(0)
        

        # getimage
        elif args.mode == 'getimage':
            result = RoadCamera(
                configure_load_path=args.configure_load_path
            )

            result.import_configure_file()

            # 변환 이미지 생성 후 경로 출력하고 종료
            print(f"{datetime.now().strftime('%Y%m%d%H%M%S.%f')}", result.get_transformed_image(), file=sys.stdout)
            if sys.stdout:
                sys.stdout.flush()
            sys.exit(0)



    # 에러 발생 시 출력하고 종료
    except Exception as e:
        print(f'{__file__}: {e}', file=sys.stderr)
        if sys.stderr:
            sys.stderr.flush()
        sys.exit(1)

    # except:
    #     print(traceback.print_exc(), file=sys.stderr)
    #     if sys.stderr:{"device": "roadcamera", "device_name": "\ubcf4\uc870 \ubd84\ub958AI\uc6a9 USB\uce74\uba54\ub77c \uc774\ubbf8\uc9c0", "edge_time": null, "encoding": "ASCII, base64, PNG", "binary": null}

    #         sys.stderr.flush()
    #     sys.exit(1)

    # python Sources/Main/Data_collection/Camera/roadcamera.py configure --port_cam 0 --img_save_name testimg --img_format png --perspective_after_size 300 300 --configure_save_name roadcamera.conf
    # python Sources/Main/Data_collection/Camera/roadcamera.py getimage --configure_load_path Sources/Main/TEST_RESOURCE/roadcamera.conf 