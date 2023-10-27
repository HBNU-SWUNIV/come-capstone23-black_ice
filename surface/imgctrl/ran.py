import os
import random
import shutil

# 원본 이미지 파일이 들어있는 폴더 경로
original_folder = "C:/Users/82103/Desktop/nnnnn/wa/"

# 나눠담을 폴더 A와 폴더 B의 경로
folder_A = "C:/Users/82103/Desktop/nnnnn/wa_a/"
folder_B = "C:/Users/82103/Desktop/nnnnn/wa_b/"

# 이미지 파일 목록을 가져옴
image_files = os.listdir(original_folder)

# 랜덤으로 선택하여 이미지 파일을 폴더 A 또는 폴더 B로 복사
for filename in image_files:
    if filename.endswith(".jpg") or filename.endswith(".png"):
        source_path = os.path.join(original_folder, filename)
        destination_folder = folder_A if random.random() < 0.5 else folder_B
        destination_path = os.path.join(destination_folder, filename)
        shutil.copyfile(source_path, destination_path)