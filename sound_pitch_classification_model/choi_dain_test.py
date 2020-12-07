# import librosa
# from scipy import signal
# import numpy as np

import librosa
from python_speech_features import mfcc
import os
import matplotlib.pyplot as plt
import librosa.display
import numpy as np

def compute_mfcc(audio_data, sample_rate):
    # audio_data = audio_data - np.mean(audio_data)
    # audio_data = audio_data / np.max(audio_data)
    mfcc_feat = mfcc(audio_data, sample_rate, winlen=0.010, winstep=0.01,
                     numcep=13, nfilt=26, nfft=512, lowfreq=0, highfreq=None,
                     preemph=0.97, ceplifter=22, appendEnergy=True)
    return mfcc_feat 

FOLDER_PATH = 'C:/Users/dain8/Desktop/29_4번(아이엠알)기업프로젝트/freesound-audio-tagging/audio_train'
FILE_LIST = os.listdir(FOLDER_PATH)

for file in FILE_LIST:
    FILE_PATH=FOLDER_PATH + '/' + file

    print('get MFCC Feature of'+file+'...')

    # file='fff81f55.wav'
    # FILE_PATH='C:/Users/dain8/Desktop/29_4번(아이엠알)기업프로젝트/freesound-audio-tagging/audio_train/fff81f55.wav'

    audio_sample, sampling_rate = librosa.load(FILE_PATH, sr = None)
    mfcc = compute_mfcc(audio_sample, sampling_rate)
    librosa.display.specshow(mfcc.T, x_axis='time')
    plt.colorbar()
    plt.tight_layout()
    #범례 제외
    # plt.legend()
    #축 제외
    plt.axis('off')
    # plt.legend()
    plt.savefig('C:/Users/dain8/Desktop/29_4번(아이엠알)기업프로젝트/MFCC Feature result/'+file+'.png')

# audio_sample, sampling_rate = librosa.load("sine.wav", sr = None)
# # audio_sample, sampling_rate = librosa.load("test_voice.wav", sr = None)

# S = np.abs(librosa.stft(audio_sample, n_fft=1024, hop_length=512, win_length = 1024, window=signal.hann))
# pitches, magnitudes = librosa.piptrack(S=S, sr=sampling_rate)

# shape = np.shape(pitches)
# nb_samples = shape[0]
# nb_windows = shape[1]

# for i in range(0, nb_windows):
#     index = magnitudes[:,i].argmax()
#     pitch = pitches[index,i]
#     print(pitch)

# # FFT 결과를 plot
# import matplotlib.pyplot as plt
# import librosa.display

# #normalize_function
# min_level_db = -100
# def _normalize(S):
#     return np.clip((S-min_level_db)/(-min_level_db), 0, 1)

# mag_db = librosa.amplitude_to_db(S)
# mag_n = _normalize(mag_db)
# plt.subplot(311)
# librosa.display.specshow(mag_n, y_axis='linear', x_axis='time', sr=sampling_rate)
# plt.title('spectrogram')

# t = np.linspace(0, 24000, mag_db.shape[0])
# plt.subplot(313)
# plt.plot(t, mag_db[:, 100].T)
# plt.title('magnitude (dB)')
# plt.show()



# import librosa
# import librosa.display
# import matplotlib.pyplot as plt
# from dtw import dtw
# from numpy.linalg import norm

# #Loading audio files
# y1, sr1 = librosa.load('sine.wav') 
# y2, sr2 = librosa.load('test_voice.wav') 

# #Showing multiple plots using subplot
# plt.subplot(1, 2, 1) 
# mfcc1 = librosa.feature.mfcc(y1,sr1)   #Computing MFCC values
# librosa.display.specshow(mfcc1)

# plt.subplot(1, 2, 2)
# mfcc2 = librosa.feature.mfcc(y2, sr2)
# librosa.display.specshow(mfcc2)

# dist, cost, acc_cost, path = dtw(mfcc1.T, mfcc2.T, dist=lambda x, y: norm(x - y, ord=1))
# print("The normalized distance between the two : ",dist)   # 0 for similar audios 

# plt.imshow(cost.T, origin='lower', cmap=plt.get_cmap('gray'), interpolation='nearest')
# plt.plot(path[0], path[1], 'w')   #creating plot for DTW

# plt.show()  #To display the plots graphically