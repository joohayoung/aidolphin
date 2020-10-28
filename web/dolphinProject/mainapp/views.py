from django.shortcuts import render, redirect
from .models import MusicDB, UploadMusicDB
from django.db.models import Q, Count
from django.http import HttpResponse
import json
from model.type_predictor import label_type

# Create your views here.

def home(request):
    return render(request, 'mainapp/home.html')

def realtime(request):
    context = {}
    if request.method=='POST':
        if 'file' in request.FILES:
            audio = request.FILES['file']
            uploadfile = UploadMusicDB(audio=audio)
            uploadfile.save()
            context['audio'] = audio.name
            print('views.py realtime audioname : ', audio.name)
            # audio 파일을 모델 함수에 입력 아웃풋 lagel값
            file_path = f"media/upload_music/{audio}"
            label = label_type(file_path) # 모델활용
            # label = 'Telephone' #확인용
            context['label'] = label
            print('views.py realtime label : ', label)
            uploadfile.delete()
        else:
            context['audio'] = 'audio_none'
            context['label'] = 'label_none'
    else:
        context['audio'] = 'audio_none'
        context['label'] = 'label_none'

    return HttpResponse(json.dumps(context))

def search(request):
    context = {}
    audio = None
    label = None

    ####파일검색
    if request.method=='POST':
        if 'file' in request.FILES:
            audio = request.FILES['file']
            uploadfile = UploadMusicDB(audio=audio)
            uploadfile.save()

            context['audio'] = audio
            # audio 파일을 모델 함수에 입력 아웃풋 lagel값
            file_path = f"media/upload_music/{audio}"
            label = label_type(file_path) # 모델활용
            # label = 'Telephone' #확인용
            context['label'] = label
            uploadfile.delete()
    else:
        label = request.GET.get('label', '')
        context['label'] = label
        audio = request.GET.get('audio', '')
        context['audio'] = audio


# if request.method == "GET"
    ## DB 불러와서 정렬하기
    sort = request.GET.get('sort', 'like') #나중에 기본설정 similar로 바꾸기
    context['sort'] = sort

    if sort == 'like': #좋아요순
        music_list = MusicDB.objects.annotate(num_like=Count('like')).order_by('-num_like','-date')
    elif sort == 'download': #다운로드순
        music_list = MusicDB.objects.order_by('-downloads', '-date')
    elif sort == 'similar': #유사도(기본)
        #유사도 추가하기
        pass
    else: #recent 최신순
        music_list = MusicDB.objects.order_by('-date')

    ## 검색결과
    kw = request.GET.get('kw', '')
    context['kw'] = kw

    if label: #키워드 검색이 아니고 파일검색에서 라벨을 입력(?)받았을때
        kw = label 

    if kw != '' : # 키워드 검색 파일명이나 라벨명으로 검색
        music_list = music_list.filter(
            Q(fname__contains=kw) | Q(label__contains=kw)
        )#.distinct()
    elif label: #kw가 ''인데 label 값이 있을경우 label로 검색
        music_list = music_list.filter(label__contains=label)#.distinct()
    else:
        #kw가 ''이고 label값도 없을경우 => 키워드검색, 키워드 입력안함 => 전체 
        pass

    ## 라이센스 필터링
    licenses = request.GET.getlist('license[]', 'all')
    print(licenses)
    if 'all' in licenses:
        #all 이 같이 입력되거나 아무것도 입력되지 않았을때
        context['license']='all'
        context['music_list'] = music_list
    else:
        context['license'] = licenses
        # author commercial work
        if 'author' in licenses:
            #저작자 표기안함 : cc0
            music_list = music_list.filter(licenses='CreativeCommons0')
        
        if 'commercial' in licenses:
            # 상업적 이용가능 : cc0 / by-nb / by-sa / by
            # by-nc / by-nc-sa / by-nc-nd
            music_list = music_list.exclude(licenses__contains='Noncommercial')

        if 'work' in licenses:
            # 변경가능 : cc0 / by-nc / by-sa / by-nc-sa / by
            # 변경불가능 : by-nd / by-nc-nd
            music_list = music_list.exclude(licenses__contains='Derivative Works')

        context['music_list'] = music_list

    return render(request, 'mainapp/search.html', context)