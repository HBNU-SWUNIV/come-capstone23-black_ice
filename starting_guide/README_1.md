## BLACK_ICE_D

젯슨 나노 구동을 위한 라이브러리 빌드 가이드,
리눅스 우분투 18.04LTS, 파이썬 3.6.9 버전에서 동작함을 확인


설치 시 라이브러리간 의존성 확인이 어렵다면 순수 파이썬 환경의 가상환경을 생성하여
의존성 모듈을 확인해가며 설치를 진행하는 것을 권장합니다. 아래의 명령어는 해당 명령어입니다.


가상환경 가동(젯슨 나노 지원 패키지 사용)
```
python3 -m venv env_ --system-site-packages
source env_/bin/activate
```

가상환경 가동(순수 파이썬 환경, 라이브러리 제공x)
```
python3 -m venv env_
source env_/bin/activate
```


가상환경 중단
```
deactivate
```


jetpack 버전 확인
(해당 버전에 따라서 엔비디아에서 기본으로 제공해주는 파이썬 라이브러리가 다름에 유의)
```
cat /etc/nv_tegra_release
```




## pridictor 모듈의 경우

순수 가상환경을 만들어 가동합니다(라이브러리 코드의 수정이 필요하므로 반드시 가상환경으로 진행합니다.)
```
python3 -m venv env_
source env_/bin/activate
```

pip 업그레이드(미진행시 이후 작업에 차질이 생깁니다.)
```
pip install --upgrade pip
```


Cython 설치
```
pip install Cython
```


판다스와 넘파이를 설치합니다.
```
pip install pandas==1.1.5 numpy==1.16.0
```

사이킷 런을 설치합니다.
```
pip install scikit-learn
```



모델을 로드하기 위한 joblib를 설치합니다.
```
pip install joblib==1.1.1
```

이 시점에서 가상환경 내부의 파이썬 패키지 목록은 다음과 같습니다(pip freeze 로 확인)
```
Cython==3.0.5
dataclasses==0.8
joblib==1.1.1
lightgbm==4.1.0
numpy==1.16.0
pandas==1.1.5
pkg_resources==0.0.0
python-dateutil==2.8.2
pytz==2023.3.post1
scikit-learn==0.24.2
scipy==1.5.4
six==1.16.0
threadpoolctl==3.1.0
```

이후에 가상환경의 joblib 라이브러리 코드의 수정이 필요합니다. 
가상환경 정보가 담긴 디렉토리의 다음 경로에 해당하는 파일을 수정해야 합니다.
```
[가상환경 폴더명]/lib/python3.6/site-packages/joblib/externals/loky/backend/context.py
```

해당 context.py 의 221, 222 번 라인의 내용은 다음과 같습니다.
```
cpu_info = subprocess.run(
    "lscpu --parse=core".split(" "), capture_output=True)
```

이제 221번, 222번 라인의 코드를 다음 내용으로 대체합니다.
```
cpu_info = subprocess.run(["lscpu", "--parse=core"], stdout=subprocess.PIPE)
```


이후 가상환경 내에서 테스트를 진행할 수 있습니다.
```
python predictor.py -of resource/M1.conf -iwd 81.0 -iwv 0.8 -iat 5.8 -irh 71.6 -ist 7.9 -iw 0 -id 1.0599028746970034 -iu 0.0
```





## 이미지 처리 AI 모듈의 경우
surface 하위 리포지토리를 참조하십시오 https://github.com/L-dana/surface


## 데이터베이스 모듈의 경우

데이터베이스 설치(postgres)
```
sudo apt install postgresql postgresql-contrib
```

가상환경 가동(젯슨 나노 지원 패키지 사용)
jetpack 에서 지원하는 라이브러리 이외에 추가 설치가 필요한 내용만을 언급합니다.
```
python3 -m venv env_ --system-site-packages
source env_/bin/activate
```


peewee 설치
```
pip install peewee
```


psycopg2 설치
```
pip install psycopg2-binary
```



## 통신 관련 모듈의 경우


데이터 송수신을 위한 mqtt설치
```
pip install paho-mqtt
```


