# Black_Ice_D 의 하위 프로젝트



젯슨 나노 구동을 위한 라이브러리 빌드 가이드
이 가이드는 리눅스 우분투 18.04LTS, 파이썬 3.6.9 버전에서 동작함



*** 참조 ***
https://forums.developer.nvidia.com/t/pytorch-for-jetson/72048



가상환경 가동
```
python3 -m venv env_ --system-site-packages
source env_/bin/activate
```

가상환경 중단
```
deactivate
```

jetpack 버전 확인
```
cat /etc/nv_tegra_release
```

onnxruntime 설치, 
onnxruntime_gpu-1.11.0-cp36-cp36m-linux_aarch64.whl 파일은 준비되어 있어야 함 jetpack 버전마다 토치 버전이 다름에 유의
```
pip install onnxruntime_gpu-1.11.0-cp36-cp36m-linux_aarch64.whl
```

onnx 설치
```
pip install onnx==1.4.1
```


파이토치 설치,
설치를 하기위한 라이브러리 설치
```
sudo apt-get install python3-pip libopenblas-base libopenmpi-dev libomp-dev
pip install Cython
```

torch-1.7.0-cp36-cp36m-linux_aarch64.whl 파일은 미리 준비되어 있어야 함, jetpack 버전마다 토치 버전이 다름에 유의
참조(https://forums.developer.nvidia.com/t/pytorch-for-jetson/72048)
```
pip install numpy torch-1.7.0-cp36-cp36m-linux_aarch64.whl
```


토치비전 설치
```
sudo apt-get install libjpeg-dev zlib1g-dev libpython3-dev libopenblas-dev libavcodec-dev libavformat-dev libswscale-dev
```

참조(https://forums.developer.nvidia.com/t/pytorch-for-jetson/72048)에 있는 PyTorch 버전에 따라서 vX.X.X 를 바꿔야 함
```
git clone --branch v0.8.1 https://github.com/pytorch/vision torchvision
cd torchvision
export BUILD_VERSION=0.8.1
python setup.py install --user
cd ../
```

Python 2.7에서는 항상 필요 Python 3.6에서는 torchvision v0.5.0+부터 필요하지 않음.
```
pip install 'pillow<7'
```



pycuda 설치하기 ( 이 가이드에서는 v10.2 )
설치 전에 cuda 버전을 확인, .py 에서
```
import torch
print(torch.version.cuda) 
```

이후 vim 또는 vi
```
vim ~/.bashrc
```

맨 아래로 가서 다음을 추가(버전에 맞게 수정할 것)
```
export PATH="/usr/local/cuda-10.2/bin:$PATH"
export LD_LIBRARY_PATH="/usr/local/cuda-10.2/lib64:$LD_LIBRARY_PATH"
```

다시 터미널에서
```
sudo source ~/.bashrc
```


이후
```
wget https://files.pythonhosted.org/packages/5e/3f/5658c38579b41866ba21ee1b5020b8225cec86fe717e4b1c5c972de0a33c/pycuda-2019.1.2.tar.gz
tar xvf pycuda-2019.1.2.tar.gz
cd pycuda-2019.1.2
python configure.py --cuda-root=/usr/local/cuda-10.2
python setup.py install
```