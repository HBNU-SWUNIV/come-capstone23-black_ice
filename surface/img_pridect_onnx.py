import onnxruntime as ort
import cv2 as cv
import numpy as np
import torchvision.transforms as transforms
from datetime import datetime
import sys
import argparse

if __name__ =="__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-mp', '--model_path', type=str, required=True)
        parser.add_argument('-ip', '--image_path', type=str, required=True)

        #parser.add_argument('-a', '--movement_a', action='store_true', default=False)
        #parser.add_argument('-b', '--movement_b', action='store_true', default=False)
        #parser.add_argument('-o', '--options', nargs='*', type=str)
        args = parser.parse_args()


        # ONNX 런타임 세션 열기
        #"A10E4_Net_epoch_63.onnx"
        session = ort.InferenceSession(args.model_path, providers=['TensorrtExecutionProvider', 'CUDAExecutionProvider'])


        # 이미지 불러오기
        image_path = args.image_path # "D:/AP/surface/dataset/frozen/S11109.png"
        image = cv.imread(image_path)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)


        scr = np.zeros([4, 2], dtype=np.float32)
        scr[0] = np.array([865, 38])#'left_top'
        scr[1] = np.array([1055 ,38])#'right_top'
        scr[2] = np.array([1165, 418])#'left_bottom'
        scr[3] = np.array([755, 418])#'right_bottom'
        dst = np.float32([[0, 0], [300, 0], [0, 300], [300, 300]])

        #퍼스펙티브 변환 행렬 생성
        m = cv.getPerspectiveTransform(scr, dst)

        #퍼스펙티브 변환, 리사이즈 동시적용
        img_result = cv.warpPerspective(image, m, (300, 300))

        # 이미지 크기를 모델 입력 크기에 맞게 조정
        #텐서 변환 정의
        transform_ = transforms.Compose([
            transforms.ToTensor(),      # 이미지를 텐서로 변환
            transforms.Normalize(mean=[0.485, 0.456, 0.406],  std=[0.229, 0.224, 0.225]) #정규화, 이미지넷 데이터셋 기준값
        ])
        input_tensor = transform_(img_result)
        input_tensor = input_tensor.unsqueeze(0)  # 데이터 형식 맞추기(배치 차원 추가)


        # ONNX 모델 실행, 입력 데이터는 {'입력 이름':넘파이 배열} 형태여야 함
        outputs = session.run(None, {"image": input_tensor.numpy()})

        # 확률 계산
        probabilities = outputs[0]  # 모델 출력은 outputs 리스트의 첫 번째 요소.
        rounded_probabilities = np.round(probabilities * 1000) / 1000

        # 가장 높은 확률과 해당 클래스 인덱스 찾기
        max_probability = np.max(probabilities, axis=1)
        predicted_class = np.argmax(probabilities, axis=1)

        # 결과 출력
        #print("가장 높은 확률:", max_probability)
        #print("예측된 클래스 인덱스:", predicted_class)

        now = datetime.now().strftime('%Y%m%d%H%M%S.%f')
        print(now, *predicted_class, *max_probability)

    except Exception as e:
        print(f'{type(e)} {e}', file=sys.stderr)
        sys.exit(1)