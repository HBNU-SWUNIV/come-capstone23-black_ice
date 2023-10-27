import cv2 as cv
from torchvision import transforms
import torchvision
import torch
import torch.nn.functional as F
import sys
import argparse
from datetime import datetime
#import tensorflow as tf
#import tf2onnx #####
#from torch2trt import TRTModule
import tensorrt as trt #https://wikidocs.net/158553

import onnxruntime
from torch import nn
from torch import Tensor
import onnx
import pycuda as cuda


#rint (torchvision.__version__)
print(cv.__version__)
print(torch.__version__)
print(torchvision.__version__)
print(sys.version)
#print(tf.__version__)
#print(tf2onnx.__version__)
print(onnxruntime.__version__)
print(onnx.__version__)
print(trt.__version__) ## 8.2.1.8 or 7.2.3
print('pp')
print(torch.version.cuda)
print(cuda.VERSION)


'''
img = cv.imread('D12028.png', cv.IMREAD_COLOR)

# 이미지를 300x300 크기로 리사이즈합니다.
resized_image = cv.resize(img, (300, 300))

# 저장할 파일 경로와 파일 이름을 설정합니다.
output_path = 'D12028_.png'

# 리사이즈된 이미지를 저장합니다.
cv.imwrite(output_path, resized_image)'''


'''
import onnx
from onnx import helper, numpy_helper

# 1. ONNX 모델 로드
model_path = 'A10E4_Net_epoch_63.onnx'
model = onnx.load(model_path)

# 2. 모델 구조 확인
print(model)

# 3. 모델 구조 수정
# 예시: 모델의 첫 번째 레이어의 입력 크기를 변경하는 경우
# (이 예시는 모델 구조를 이해하는 데 도움이 될 수 있습니다. 실제로 필요한 수정에 따라 다르게 적용되어야 합니다.)

new_input_size = [3, 300, 300]

# 첫 번째 레이어의 입력 크기 변경
if len(model.graph.input) > 0:
    model.graph.input[0].type.tensor_type.shape.dim[1].dim_value = new_input_size[0]
    model.graph.input[0].type.tensor_type.shape.dim[2].dim_value = new_input_size[1]
    model.graph.input[0].type.tensor_type.shape.dim[3].dim_value = new_input_size[2]


# 4. 가중치 수정
# 예시: 가중치를 INT32로 변환
# (가중치의 데이터 타입이 float32일 경우)

for i in range(len(model.graph.initializer)):
    tensor = model.graph.initializer[i]
    if tensor.data_type == 1:  # 데이터 타입이 float32인 경우
        tensor.data_type = 6    # 데이터 타입을 int32로 변경

        # float32 배열을 int32로 변환
        tensor.float_data[:] = [int(x) for x in tensor.float_data]

# 5. 수정된 모델 저장
output_model_path = 'A10E4_Net_epoch_63_int32.onnx'
onnx.save(model, output_model_path)

# 6. 수정된 모델을 사용하여 추론 또는 추가 작업 수행 가능

'''

import onnx
from onnx import helper, numpy_helper

# 1. ONNX 모델 로드
model_path = 'A10E4_Net_epoch_63.onnx'
model = onnx.load(model_path)

# 2. 모델 구조 확인
print(model)

# 3. 모델 구조 수정
# 예시: 모델의 첫 번째 레이어의 입력 크기를 변경하는 경우
# (이 예시는 모델 구조를 이해하는 데 도움이 될 수 있습니다. 실제로 필요한 수정에 따라 다르게 적용되어야 합니다.)

new_input_size = [3, 300, 300]

# 첫 번째 레이어의 입력 크기 변경
if len(model.graph.input) > 0:
    model.graph.input[0].type.tensor_type.shape.dim[1].dim_value = new_input_size[0]
    model.graph.input[0].type.tensor_type.shape.dim[2].dim_value = new_input_size[1]
    model.graph.input[0].type.tensor_type.shape.dim[3].dim_value = new_input_size[2]


# 4. 가중치 수정
# 예시: 가중치를 INT32로 변환
# (가중치의 데이터 타입이 float32일 경우)

for i in range(len(model.graph.initializer)):
    tensor = model.graph.initializer[i]
    if tensor.data_type == 1:  # 데이터 타입이 float32인 경우
        tensor.data_type = 6    # 데이터 타입을 int32로 변경

        # float32 배열을 int32로 변환
        tensor.float_data[:] = [int(x) for x in tensor.float_data]

# 5. 수정된 모델 저장
output_model_path = 'A10E4_Net_epoch_63_int32.onnx'
onnx.save(model, output_model_path)

# 6. 수정된 모델을 사용하여 추론 또는 추가 작업 수행 가능

#/usr/src/tensorrt/samples/trtexec --onnx=A10E4_Net_epoch_63.onnx --saveEngine=A10E4_Net_epoch_63.engine --verbose
#python img_pridect_tensorrt.py -mp A10E4_Net_epoch_63.onnx -ip D12028_.png