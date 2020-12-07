import subprocess
import pandas as pd
import numpy as np


# 파일경로 수정
# data = pd.read_csv("../../input/freesound-audio-tagging/train.csv")
data = pd.read_csv("../../input/freesound-audio-tagging/test_post_competition.csv")
# path = "../../input/freesound-audio-tagging/audio_train/"
path = "../../input/freesound-audio-tagging/audio_test/"

# print(data)

wavfile = data["fname"]

cnt = 0

# 입력된 음향의 초 마다 카테고리 예측!
# ex) 1초에는 XX : 0.94949494 , 2초에는 AA : 0.55556436

for row in wavfile.tolist():
    
    if cnt == 3:
        break

    subprocess.call("python realtime_predictor.py"+" -f " + path + row, shell=True)
    
    cnt += 1

    

