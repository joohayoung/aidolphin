import numpy as np
from python_speech_features import mfcc
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
import os
import librosa
import soundfile as sf # 리샘플링한 음악을 저장
import pandas as pd
import csv

# print()


# 사용한 음향데이터가 16000hz가 아니라 경고가 나므로 음향의 샘플링을 16000hz로 변환
def resampling(file,origin_sr,resample_sr):
    #     resample_sr = 16000
    #     origin_sr = 44100
    #     resample_sr= resample_sr
    #     origin_sr = origin_sr
    
    # 리샘플링을 해줘야하니 input으로 넣어줄 sound파일이 있는 경로 지정
    # os.chdir("C:/Users/husky/Documents/기업프로젝트/data/freesound-audio-tagging/audio_test")
    file_path = './media/upload_music/'+ file
    # C:\Users\26162\TeamProject\Aloha\Ai_Dolphin\ai-dolphin\web\dolphinProject\media\upload_music

    # file 예시: 00063640.wav ,  (type: 'str')
    # y, sr = librosa.load(file, sr=origin_sr)
    y, sr = librosa.load(file_path, sr=origin_sr)
    resample = librosa.resample(y, sr, resample_sr)
    #print("original wav sr: {}, original wav shape: {}, resample wav sr: {}, resmaple shape: {}".format(origin_sr, y.shape, resample_sr, resample.shape))
    # 리샘플링이 된 wav 로 파일 저장 경로 설정
    # sf.write('../test_music/' + file, resample, resample_sr, format='WAV', endian='LITTLE', subtype='PCM_16')
    sf.write('./similarModel/test_music/' + file, resample, resample_sr, format='WAV', endian='LITTLE', subtype='PCM_16')
    # 모든 파일을 리샘플링(44100hz->16000hz) 해주었다면 더이상 실행시키지 않아도 됨
    # 추후 새로 입력이 들어오는 데이터가 있다면 해당 파일의 샘플링을 알아야하고,
    # 16000이 아니라면 샘플링을 해주어야 함(샘플링이 다르면 경고가 발생하는데 근대 무시해도 문제는 없다고 ..)
    print("리샘플링 성공")


#  ElasticSearch는 저장해야할 picture가 늘어나면 강제종료되는 버그가 있기에 파일에 저장하는 방식을 선택
def feature_save(file):
     # 리샘플링이 된 wav 파일의 경로를 가져옴
    # os.chdir("../test_music/")
    file_path = './similarModel/test_music/' + file
    # wav파일에서 MFCC 특성 추출
    # (rate,sig) = wav.read(file)
    (rate,sig) = wav.read(file_path)
    
    mfcc_feat = mfcc(sig,rate)
    feat_mean = np.mean(mfcc_feat, axis = 0)
    feat_cov = np.cov(mfcc_feat,rowvar=0)
    feat_cov_up = np.triu(feat_cov, k=0)# 상삼각행렬(Upper triangular matrix)을 반환
    feat_flat = feat_cov_up.flatten()
    index = np.arange(len(feat_flat))[feat_flat==0]
    feat_cov = list(np.delete(feat_flat, index))
    
    # 모든 특성 벡터를 더한 값 
    feat = []
    sum1= np.sum(feat_mean)+sum(feat_cov)
    sum2=np.float64(sum1).item() # 리스트에 넣기 위해 np float64 -> list형식으로 변환
    
#       생성되는 csv 형태
#             name         sum         vector1     vector2     vector3  ... vector104
#       1번째 wav파일   벡터 합       벡터 값1    벡터 값2   벡터 값3 ...   벡터 값104
#       2번재 wav파일   벡터 합        ... 
    feat.append(file) # wav파일 이름 저장
    feat.append(sum2) # extend는 list에 여러 이터레이터를 인풋, append는 한개의 항목 인풋
    feat.extend(feat_mean)#<class 'numpy.ndarray'>   # 이 값은 들어가짐. extend()라 그런듯
    feat.extend(feat_cov) # <class 'list'>
    
    # 'test.csv' 파일은 9000개 가량의 음향을 MFCC 특성추출해서 저장한 csv파일임
    # 생성되어있는 csv파일의 마지막에 MFCC로 특성추출해준 새로운 음향 벡터를 기록
    with open('./similarModel/test.csv', 'a', newline='\n') as f:
        writer = csv.writer(f)
        writer.writerow(feat)

    print("특성 추출 성공")


def music_search(file):
    print("뮤직서치 실행")
    # csv 읽기
    music_df=pd.read_csv('./similarModel/test.csv',encoding="utf-8")

    # 마지막에 추가된 값(비교할 값)의 sum을 compare_sum에 저장
    compare_sum=music_df.iloc[-1]['sum']
    # 유사도 비교해줄 행을 compare에 저장
    compare=music_df.iloc[-1]

    # 1차 필터링
    # sum값이 인접한 10%들을 검색하여 filter1에 저장
    filter1=music_df[(music_df['sum']>(compare_sum*0.95)) & (music_df['sum']<(compare_sum*1.05))]
    # 비교해야할 값도 filter1에 포함되었기에 filter1에선 삭제
    filter1=filter1.drop(filter1.index[-1])
    
    
    # 2차 필터링
    hap=0
    filter_list=[]
    for i in range(len(filter1)):
        for j in range(2,len(filter1.columns)): # 2부터 시작
            hap+= (compare[j]-filter1.iloc[i][j])**2 # 유클리드 거리 
        filter_list.append(hap)
        hap=0

    # 정렬을 위해 dict로 생성 
    filter_dict={}
    for i in range(len(filter_list)):
        filter_dict[filter1.iloc[i]['name']]=filter_list[i]

    # 값(value)을 기준으로 오름차순 정렬
    sorted(filter_dict.items(), key=lambda x:x[1])

    # 3차 필터링
    # 해당 딕셔너리에 서로 똑같은 value값이 있다면 제외( 똑같은 음향파일을 중복해서 추천해주는 경우 제외 )
    dict_len=len(filter_dict)
    list_del=[]
    
    for idx, (key,element) in enumerate(filter_dict.items()):
        for sub_idx in range(idx+1, dict_len):
            if(element == list(filter_dict.values())[sub_idx]):
                list_del.append(list(filter_dict.keys())[sub_idx])
                
    if(list_del):# 비어있지않다면 실행
        for d in list_del:
            del filter_dict[d]
    
    # 유사한 음향 500개 반환
    result=[]
    cnt=0
    for key in filter_dict.keys():
        if(cnt>=500):
            break
        # file이름이 똑같다면 넘김
        if(file==filter_dict.keys):
            continue
        result.append(key)
        cnt+=1
    # print(result)
    return result


# view.py 에서 실행시킬 함수
def similarAnalysis(file):
    # try:
    # 유사음향을 찾을 file이름을 줘야함
    #     file='00ae03f6.wav'
    resampling(file,44100,16000) # 44100은 input 샘플링, 16000은 바꿀 샘플링
    # print("리샘플링 성공")
    feature_save(file)
    # print("특성 추출 성공")
    music_list=music_search(file)

    return music_list
    # except:
    #     print(file,'error')
    #     return 'error'
