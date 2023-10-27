import cv2 as cv
from torchvision import transforms
import torch
torch.backends.quantized.engine = 'fbgemm'  # 'fbgemm'는 대안으로 시도할 엔진입니다.
import torch.nn.functional as F
import sys
import argparse
from datetime import datetime

from torch import nn
from torch import Tensor
from torch2trt import torch2trt  # 모듈 임포트
from torch.quantization import quantize_dynamic


class A10E4_Net(nn.Module):
    def __init__(self) -> None:
        super(A10E4_Net, self).__init__()
        self.main = nn.Sequential(
            #group1 3채널 입력(컬러이미지), 특징 추출 유형1
            nn.Conv2d(in_channels=3, out_channels=6, kernel_size=3, stride=1),
            nn.ReLU(),
            nn.Conv2d(in_channels=6, out_channels=12, kernel_size=3, stride=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout(p=0.2),

            #group2 특징 추출 유형1
            nn.Conv2d(in_channels=12, out_channels=24, kernel_size=3, stride=1),
            nn.ReLU(),
            nn.Conv2d(in_channels=24, out_channels=48, kernel_size=3, stride=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout(p=0.2),

            #group3, 특징 추출 유형2
            nn.Conv2d(in_channels=48, out_channels=48, kernel_size=3, stride=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout(p=0.2),

            #group4, 특징 추출 유형2
            nn.Conv2d(in_channels=48, out_channels=96, kernel_size=3, stride=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout(p=0.2), #flatten_size = 96 * (image_height//16) * (image_width//16)

        )

        self.fully_connected = nn.Sequential(               #group5 분류
            nn.Linear(in_features=384, out_features=384),
            nn.Dropout(p=0.2),
            nn.Linear(in_features=384, out_features=192),
            nn.Dropout(p=0.2),
            nn.Linear(192, 192),
            nn.Dropout(p=0.2),
            nn.LogSoftmax(dim=1),
        )

    def forward(self, image: Tensor) -> Tensor:
        """Returns logit for the given tensor."""
        #with torch.no_grad():
            #out = ImagePreProcessing()(image)
        out = self.main(image)
        out = out.view(out.size(0), -1)
        out = self.fully_connected(out)
        return out





if __name__ =="__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-mp', '--model_path', type=str, required=True)
        parser.add_argument('-ip', '--image_path', type=str, required=True)

        args = parser.parse_args()


        # 정보 불러오기
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        #device = torch.device("cpu")
        
        #모델 파일 로드
        loaded_info = torch.load(args.model_path, map_location=device)

        '''
        state = {
            'python_v': sys.version,
            'model': model.state_dict(),
            'optimizer': optimizer.state_dict(),
            'class_labels': folder,  # 예측할 클래스 레이블 정보
            'image_size': size,  # 이미지 크기
            'learning_rate': lr,  # 학습률
            'best_acc': best_acc,
            'epoch': epoch,
            'seed': seed_,
            'dtype': param.dtype
        }

        '''

        # 예측할 클래스 레이블 정보, 이미지 크기, 시드 등 메타데이터 로드
        try:
            python_v = loaded_info['python_v']
            class_labels = loaded_info['class_labels']
            image_size = loaded_info['image_size']
            seed = loaded_info['seed']
            dtype = loaded_info['dtype']
            torch.manual_seed(seed)
            #print(python_v, class_labels, image_size, seed, dtype)

        except KeyError as e:
            raise Exception(f'모델 메타데이터 누락')



        # 모델 형상 생성, 가중치 로드 ( 모델에 따라 수정해야 함)
        model = A10E4_Net().to(device)
        model = quantize_dynamic(model, dtype=dtype)
        model.load_state_dict(loaded_info['model'])

        '''
        #모델이 모바일넷일 경우 이 문장 사용하여 모델 형상 맞춤
        model = models.mobilenet_v3_small(pretrained=True)
        # 모델의 fully connected layer 수정 (출력 클래스 개수를 4로 변경)c
        model.classifier[3] = torch.nn.Linear(in_features=1024, out_features=4)
        model = quantize_dynamic(model, dtype=dtype)
        model.load_state_dict(loaded_info['model'])
        '''


        # 입력 데이터 로드
        image = cv.imread(args.image_path, cv.IMREAD_COLOR)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)


        #텐서 변환 정의
        transform_ = transforms.Compose([
            transforms.ToTensor(),          # 이미지를 텐서로 변환
            transforms.Normalize(mean=[0.485, 0.456, 0.406],  std=[0.229, 0.224, 0.225]) #정규화, 이미지넷 데이터셋 기준값
        ])
        # 데이터 형식 맞추기
        input_tensor = transform_(image)
        input_tensor = input_tensor.unsqueeze(0)  #배치 차원 추가

        if dtype != torch.float32: #양자화 되었을 경우
            quantize = torch.quantization.QuantStub()
            input_tensor = quantize(input_tensor)

        input_img = input_tensor.to(device).float()


        # 추론 실행
        model.eval()  # 모델을 추론 모드로 설정
        with torch.no_grad():
            outputs = model(input_img)

        probabilities = F.softmax(outputs, dim=1)
        rounded_probabilities = torch.round(probabilities * 1000) / 1000  # 소수점 아래 3자리까지 반올림

        # 가장 높은 확률과 해당 클래스 인덱스 찾기
        max_probability, predicted_class = torch.max(probabilities, dim=1) 
        #max_probability, predicted_class = outputs.topk(k=1, dim=1, largest=True, sorted=True)

        now = datetime.now().strftime('%Y%m%d%H%M%S.%f')
        print(now, predicted_class.item(), max_probability.item())


    except Exception as e:
        print(f'{type(e)} {e}', file=sys.stderr)
        sys.exit(1)


## test input
# img_pridect_torch.py -mp A10E4_Net_epoch_63_qunt.pth -ip D12028_.png
# img_pridect_torch.exe -mp models/path.pth -ip imgs/path.png
# img_pridect_torch -mp models/path.pth -ip imgs/path.png

## & C:/Users/82103/AppData/Local/Programs/Python/Python36/python.exe d:/AP/surface/img_pridect_torch.py -mp A10E4_Net_epoch_63_qunt.pth -ip D12028_.png


#https://www.wonbeomjang.kr/blog/2023/jetson-nano-tensorrt/