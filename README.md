# 한밭대학교 컴퓨터공학과 [블랙 아이스크림] 팀

**팀 구성**
- 이재흥 지도교수님
- 20171589 오윤성
- 20207119 김현태
- 20201725 김나희
- 20191749 이현정


## 구성 환경
    Model : NVIDIA Jetson Nano Developer Kit
    Module : NVIDIA Jetson Nano (4GB RAM, B01)
    SoC : tegra210
    CUDA Arch BIN : 5.3
    Codename : Porg
    L4T : 32.7.4
    Jetpack : 4.6.4
    Machine : aarch64
    System : Linux
    Distribution : Ubuntu 18.04 Bionic Beaver
    Release : 4.9.337-tegra
    Python : 3.6.9

    CUDA : 10.2.300
    cuDNN : 8.2.1.32
    TensorRT : 8.2.1.8
    VPI : 1.2.3
    Vulkan : 1.2.70
    OpenCV : 4.1.1 with CUDA: NO

## 구성
```
    /
      └release #배포
      └surface #하위 프로젝트(dev) 이미지 모델 관련
      └system #전체 프로젝트(dev) 전체 시스템
      └cap #프로젝트 보고서 등 문서 디렉토리
```
    
## 도움을 주신 곳
  - 세종솔루텍(주)
  - 이노로드(주)
  



## START
개발환경 설치 가이드

1. 접속 후 젯슨 나노 운영체제 이미지 파일 다운로드
```
https://developer.nvidia.com/embedded/l4t/r32_release_v7.1/jp_4.6.1_b110_sd_card/jeston_nano/jetson-nano-jp461-sd-card-image.zip
```

2. Rufus, balenaEther 등 활용하여 microSD에 플래싱

3. Jetson Nano 디바이스 microSD 삽입 후 부팅

4. 기본적인 셋업 진행

5. 터미널 오픈 후
```
sudo apt-get update
```
```
sudo apt-get upgrade
```
로 업데이트 실시

6. 가상환경 생성 모듈 설치
```
sudo apt-get install python3-venv
```

7. 가상환경 생성 ((--system-site-packages를 입력해야 numpy, pandas, openCV 등등 일부 라이브러리를 사용할 수 있음))

```
python3 -m --system-site-packages <가상환경 경로>
```

8. 이외 하위 프로젝트 README.md 참조

## Project Outcome
- ### 2023 년 OO학술대회 




