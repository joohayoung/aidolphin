#-*-coding:utf-8-*-
#!/usr/bin/python
#
# Run sound classifier in realtime.
#
import sys
from model.common import *

import pyaudio
import time
import array
import numpy as np
import queue
from collections import deque
import argparse

from model.input3second import readInput
from collections import Counter 

# ## 파이썬 스크립트 개발시 호출 당시 인지값을 줘서 동작을 다르게 하고 싶을때 사용
# # 인자값을 받을 수 있는 인스텐스 생성
# parser = argparse.ArgumentParser(description='Run sound classifier')
# # 입력받을 인자값을 등록
# parser.add_argument('--input', '-i', default='0', type=int,
#                     help='Audio input device index. Set -1 to list devices')
#                     # -i 숫자 > 해당 번호로 실시간입력
#                     # -i -1 > 연결된 장치 리스트 출력
# parser.add_argument('--input-file', '-f', default='', type=str,
#                     help='If set, predict this audio file.')
#                     # -f 파일이름or경로 > 해당파일을 실기간처럼 분석

# # 입력받은 인자값을 args에 저장
# args = parser.parse_args()

# # Capture & pridiction jobs
raw_frames = queue.Queue(maxsize=100)
def callback(in_data, frame_count, time_info, status):
    wave = array.array('h', in_data)
    raw_frames.put(wave, True)
    return (None, pyaudio.paContinue)

def on_predicted(ensembled_pred):
    result = np.argmax(ensembled_pred)
    # print(conf.labels[result], ensembled_pred[result]) #실시간 실행결과 확인용

    return conf.labels[result]

raw_audio_buffer = []
preds_list = []

pred_queue = deque(maxlen=conf.pred_ensembles)

def main_process(model, on_predicted):
    # Pool audio data (오디오 풀링 = 대표값 뽑기)
    ## raw_frames 가 비어있지 않을 경우 작동(파일이 입력되었을때)
    global raw_audio_buffer
    while not raw_frames.empty(): #raw_frames = queue.Queue(maxsize=100)
        raw_audio_buffer.extend(raw_frames.get()) #list.extend() 리스트 끝에 iterable의 모든 항목 넣기 > raw_frames값을 하나씩 버퍼로 이동
        if len(raw_audio_buffer) >= conf.mels_convert_samples: break
    if len(raw_audio_buffer) < conf.mels_convert_samples: return
    # Convert to log mel-spectrogram
    ## conf.mels_convert_samples = 44100*1+(44100//10)*1 (common.py에 정의)
    ## conf.mels_convert_samples을 기준으로 앞-오디오변환 / 뒤 버퍼유지
    audio_to_convert = np.array(raw_audio_buffer[:conf.mels_convert_samples]) / 32767
    raw_audio_buffer = raw_audio_buffer[conf.mels_onestep_samples:]
    mels = audio_to_melspectrogram(conf, audio_to_convert)  #spectogram 반환
    # Predict, ensemble
    X = []
    for i in range(conf.rt_process_count):
        cur = int(i * conf.dims[1] / conf.rt_oversamples)
        X.append(mels[:, cur:cur+conf.dims[1], np.newaxis])
    X = np.array(X)
    samplewise_normalize_audio_X(X)
    raw_preds = model.predict(X)
    for raw_pred in raw_preds:
        pred_queue.append(raw_pred)
        ensembled_pred = geometric_mean_preds(np.array([pred for pred in pred_queue]))
        # on_predicted(ensembled_pred)
        
        preds_list.append(on_predicted(ensembled_pred))
        

# # Main controller
## 파일이 입력되었을때 돌아가는 함수
def process_file(model, filename, on_predicted=on_predicted):
    # Feed audio data as if it was recorded in realtime
    audio = read_audio(conf, filename, trim_long_data=False) * 32767 #입력파일 불러오기
    while len(audio) > conf.rt_chunk_samples:
        raw_frames.put(audio[:conf.rt_chunk_samples]) # chunk사이즈씩 raw_frames에 입력한다. 
        audio = audio[conf.rt_chunk_samples:]
        #chunk 사이즈 만큼씩 메인프로세스돌리기
        main_process(model, on_predicted)
    print("=====exit=====")

def my_exit(model):
    model.close()
    # exit(0)

def get_model(graph_file):
    model_node = {
        'alexnet': ['import/conv2d_1_input',
                    'import/batch_normalization_1/keras_learning_phase',
                    'import/output0'],
        'mobilenetv2': ['import/input_1',
                        'import/bn_Conv1/keras_learning_phase',
                        'import/output0']
    }
    return KerasTFGraph(
        conf.runtime_model_file if graph_file == '' else graph_file,
        input_name=model_node[conf.model][0],
        keras_learning_phase_name=model_node[conf.model][1],
        output_name=model_node[conf.model][2])
    # KerasTFGraph(...) 클래스 객체 common.py에 정의

def one_result_print(preds_list):

    if preds_list != []:
            cnt = Counter(preds_list)
            print(cnt.most_common(1)[0][0])
            return cnt.most_common(1)[0][0]
    else:
        # 이쪽 이쁘게 수정
        print("빈 리스트 입니다.")
        return ''

def run_predictor():
    model,= get_model(args.model_pb_graph)

    # 파이썬 호출시 -pb 옵션으로 들어온것
    # default = '' 로 입력시 conf.runtime_model_file 사용

    # file mode (-f 파일경로 )
    if args.input_file != '': 
        process_file(model, args.input_file)
        # print(preds_list)
        label_value = one_result_print(preds_list)

        my_exit(model)
        return label_value

    # device list display mode (-i -1)
    if args.input < 0:
        print_pyaudio_devices()
        my_exit(model)

    # normal: realtime mode
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    ## 음성 데이터 스트림을 연다.
    audio = pyaudio.PyAudio()
    stream = audio.open(
                format=FORMAT,#비트 깊이 =16비트
                channels=CHANNELS, #1 =mono
                rate=conf.sampling_rate, #샘플링레이트 일반적으로 44100hz
                input=True, #입력 스트림인지 아닌지
                input_device_index=args.input,#원하는 입력장치 번호(없으면 자동)
                frames_per_buffer=conf.rt_chunk_samples,#음성데이터를 불러올때 한 번에 몇개의 정수를 불러올지
                start=False,
                stream_callback=callback # uncomment for non_blocking
            )

    # main loop
    print("===start recording===")
    stream.start_stream()
    while stream.is_active() : 
        main_process(model, on_predicted)
        time.sleep(0.001)
        button = readInput('go', 0.001) # 0.001초안에 입력값이 없으면 디폴트(go)값으로 입력
        if button != 'go': # 다른값이 입력됐을 경우 루프 탈출
            break
    stream.stop_stream()
    stream.close()
    print("===finished recording===")
    # finish 
    audio.terminate()
    label_value = one_result_print(preds_list)

    my_exit(model)
    return label_value

def label_type(input_file):
    model = get_model('') 
    # 파이썬 호출시 -pb 옵션으로 들어온것
    # default = '' 로 입력시 conf.runtime_model_file 사용
    #conf.runtime_model_file = 'modelsub/mobilenetv2_fsd2018_41cls.pb'
    process_file(model, input_file)
    # print(preds_list)
    label_value = one_result_print(preds_list)
    my_exit(model)
    return label_value

if __name__ == '__main__':
    run_predictor()