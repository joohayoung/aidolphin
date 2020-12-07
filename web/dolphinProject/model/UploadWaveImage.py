import os
import pandas as pd
import numpy as np
# import seaborn as sns
import matplotlib.pyplot as plt

from scipy.io import wavfile
# from glob import glob
# from tqdm import tqdm

import librosa.display, librosa

# %matplotlib inline

# sns.set_style('darkgrid')

# print(os.getcwd())


# 기본 경로를 음악파일이 있는 경로로 변경
# os.chdir("C:/Users/husky/Documents/Enterprise_project/data/freesound-audio-tagging/audio_train")
# print("after: %s"%os.getcwd())

# FOLDER_PATH=os.getcwd()
# FILE_LIST = os.listdir(FOLDER_PATH)
# print(FILE_LIST[0])

# 사진이 저장될 폴더경로 설정 
# PICTURE_PATH = 'C:/Users/husky/Documents/Enterprise_project/data/freesound-audio-tagging/test'

# print(PICTURE_PATH)


def makeWaveimg(fname):
    file_path = "media/music_sample/" + fname
    print('file_path', file_path)
    PICTURE_PATH = 'media/wave_image'
    #sig: 음향 데이터 경로
    #sr : sampling rate (주파수 분석 및 파형의 시간 간격을 결정, 숫자가 들어가며, 이때 'None'을 주면 기본 샘플링 속도로 사용)
    sig, sr = librosa.load(file_path)
    fig=plt.figure()
    librosa.display.waveplot(sig, sr, alpha=0.5)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.title("Waveform")
    
    plt.savefig(PICTURE_PATH+'/'+fname+'.png')
    plt.close(fig)#메모리 누수를 막기 위해, 만들었던 fig 삭제