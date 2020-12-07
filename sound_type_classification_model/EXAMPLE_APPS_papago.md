# Example Applications and Training

`apps` 폴더에는 데이터셋과 함께, 작동하기위한 전체 프로세스를 설명하는 몇 가지 예제 애플리케이션이 있다.

## Install Before Start Training

훈련을 위해 필요한 파이썬 모듈을 설치하기

```sh
cd ext
./download.sh
```

## A. FSDKaggle2018

FSDKAggle2018은 Freesound Dataset Kaggle 2018 데이터 셋의 모델을 훈련한다.

- `mobilenetv2_fsd2018_41cls.h5` 는 500에폭으로 훈련된 모델로, Kaggle 대회에서도 경쟁력있다. 다른 작업에 사전 검정된 모델로 사용하기에 유용한 표현을 갖고있다.

- 다른 작업에 사전 검정된 모델로 사용하기에 유용한 표현을 갖고있다.
- 44.1 kHz, 1 second duration, 128 n_mels, 128 time hops.

MobileNetV2 모델을 훈련시키고 싶을 경우:

```Python
cd apps/fsdkaggle2018
python train.py
```

AlexNet 기반 모델을 훈련시키고 싶을 경우:

```Python
cd apps/fsdkaggle2018/alexnet
python train.py
```

훈련된 모델을 tensorflow.pb 파일로 저장하고 싶을 경우.

- `FSDKaggle2018-TF-Model-Coversion.ipynb`

## B. FSDKaggle2018small

작은 오디오 데이터를 다루기위한 모델을 훈련한 모델이다. Model is not small but audio, 에를 들어 FS는 16kHz 이다. 이 샘플은 오디오 처리에 있어 컴퓨팅 파워를 덜 사용한다. 

- `mobilenetv2_small_fsd2018_41cls.h5` 는 이것에 의해 만들어진 모델이다.
- 16 kHz, 1 second duration, 64 n_mels and 64 time hops.

이 모델을 훈련시키고 싶을 경우:

```Python
cd apps/fsdkaggle2018small
python train_this.py
```

AlexNet 기반 모델을 훈련시키고 싶을 경우:

```Python
cd apps/fsdkaggle2018/alexnet
python train.py
```

## C. CNN Laser Machine Listener

이것은[github/Laser Machine Listener](https://github.com/kotobuki/laser-machine-listener)의 실험 활용 예시이다. (하드웨어 실험실의 소리 분류 모델)

Originally simple NN이 분류문제에 성공적으로 적용되었는데, CNN을 적용하면 어떻게 될까?

Simple answer is too much for the provided dataset as is(제공된 데이터 셋에 대한 답변은 지금처럼 매우 많다.).
다음 경우에 효과적일 수 있다.:

- 우리는 많은 다른 FabLabs 에서 잘 작동해야하는 단일 모델이 필요하다. 그렇다면 모델을 잘 일반화해야한다.
- 그리고 우리는 다양한 FabLab과 기계로부터 충분한 데이터를 얻었다.

이 예시는 그것을 작동하기위한 3개의 notebooks 가 있다.

1. Run followings.
    ```sh
    cd apps/cnn-laser-machine-listener
    ./download.sh
    ```
2. `CNN-LML-Preprocess-Data.ipynb`를 이용하여 데이터 전처.
3. `CNN-LML-Train.ipynb`를 이용하여 모델 훈련.
4. `CNN-LML-TF-Model-Conversion.ipynb`를 이용하여 모델을 .pb 파일로 변환.
5. 그러면 realtime_predictor.py를 통해 실시간으로 예측할 수 있다
    ```sh
    python ../../realtime_predictor.py
    ```

`cnn-model-laser-machine-listener.pb` 는 빠르게 시도할 수 있도록 이 레포에 준비되어있다.

### C.1 Another attempt for CNN Laser Machine Listener

이 문제는 AlexNet 기반 모델도 적용되었다. 더 좋은 결과를 보여줄 뿐만 아니라 훨씬 더 빨리 달린다.

- `CNN-LML-Another-Attempt-AlexNetBased.ipynb` 는 훈련 방법과 결과의 시각화를 보여주는 notebook이다.
- `cnn-alexbased-laser-machine-listener.pb` 또한 빠른 시도를 하기 위해 준비 되어있다.