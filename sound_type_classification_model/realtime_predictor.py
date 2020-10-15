#-*-coding:utf-8-*-
#!/usr/bin/python
#
# Run sound classifier in realtime.
#
import sys
from common import *

import pyaudio
import time
import array
import numpy as np
import queue
from collections import deque
import argparse

from input3second import readInput
from collections import Counter 

parser = argparse.ArgumentParser(description='Run sound classifier')
parser.add_argument('--input', '-i', default='0', type=int,
                    help='Audio input device index. Set -1 to list devices')
                    # -i 숫자 > 해당 번호로 실시간입력
                    # -i -1 > 연결된 장치 리스트 출력
parser.add_argument('--input-file', '-f', default='', type=str,
                    help='If set, predict this audio file.')
                    # -f 파일이름or경로 > 해당파일을 실기간처럼 분석

#parser.add_argument('--save_file', default='recorded.wav', type=str,
#                    help='File to save samples captured while running.')
parser.add_argument('--model-pb-graph', '-pb', default='', type=str,
                    help='Feed model you want to run, or conf.runtime_weight_file will be used.')
args = parser.parse_args()

# # Capture & pridiction jobs
raw_frames = queue.Queue(maxsize=100)
def callback(in_data, frame_count, time_info, status):
    wave = array.array('h', in_data)
    raw_frames.put(wave, True)
    return (None, pyaudio.paContinue)

def on_predicted(ensembled_pred):
    result = np.argmax(ensembled_pred)
    print(conf.labels[result], ensembled_pred[result])

    return conf.labels[result]

raw_audio_buffer = []
preds_list = []

pred_queue = deque(maxlen=conf.pred_ensembles)

def main_process(model, on_predicted):
    # Pool audio data
    global raw_audio_buffer
    while not raw_frames.empty():
        raw_audio_buffer.extend(raw_frames.get())
        if len(raw_audio_buffer) >= conf.mels_convert_samples: break
    if len(raw_audio_buffer) < conf.mels_convert_samples: return
    # Convert to log mel-spectrogram
    audio_to_convert = np.array(raw_audio_buffer[:conf.mels_convert_samples]) / 32767
    raw_audio_buffer = raw_audio_buffer[conf.mels_onestep_samples:]
    mels = audio_to_melspectrogram(conf, audio_to_convert)
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
        
        # list에 추가
        preds_list.append(on_predicted(ensembled_pred))

# # Main controller
## 파일이 입력되었을때 돌아가는 함수
def process_file(model, filename, on_predicted=on_predicted):
    # Feed audio data as if it was recorded in realtime
    audio = read_audio(conf, filename, trim_long_data=False) * 32767
    while len(audio) > conf.rt_chunk_samples:
        raw_frames.put(audio[:conf.rt_chunk_samples])
        audio = audio[conf.rt_chunk_samples:]
        main_process(model, on_predicted)
    print("=====exit=====")

def my_exit(model):
    model.close()
    exit(0)

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

def one_result_print(preds_list):

    if preds_list != []:
            cnt = Counter(preds_list)
            print(cnt.most_common(1)[0][0])
    else:
        # 이쪽 이쁘게 수정
        print("빈 리스트 입니다.")

def run_predictor():
    model = get_model(args.model_pb_graph)

    # file mode (-f 파일경로 )
    if args.input_file != '':
        process_file(model, args.input_file)
        # print(preds_list)
        one_result_print(preds_list)

        my_exit(model)

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
        time.sleep(0.1)
        button = readInput('go', 0.1) # 0.1초안에 입력값이 없으면 디폴트(go)값으로 입력
        if button != 'go': # 다른값이 입력됐을 경우 루프 탈출
            break
    stream.stop_stream()
    stream.close()
    print("===finished recording===")
    # finish 
    audio.terminate()
    one_result_print(preds_list)

    my_exit(model)

if __name__ == '__main__':
    run_predictor()