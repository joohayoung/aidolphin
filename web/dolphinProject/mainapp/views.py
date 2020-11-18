from django.shortcuts import render, redirect
from .models import MusicDB, UploadMusicDB, UserMusicDB
from django.db.models import Q, Count
from django.http import HttpResponse
import json
from django.contrib.auth.decorators import login_required
from similarModel.similarmodel import similarAnalysis
#from model.type_predictor import label_type #라벨 분류
#from model.mood_predictor import mood_type #분위기 분류

# Create your views here.

def home(request):
    return render(request, 'mainapp/home.html')

@login_required(login_url='/accountapp/login')
def upload(request):
    context = {}
    if request.method=='POST':
        if 'file' in request.FILES :
            ## 파일을 music_sample에 저장
            audio = request.FILES['file']
            userfile = UserMusicDB(audio=audio)
            userfile.save()

            ##파일정보를 DB에 저장
            # 파일이름
            fname = request.POST.get('fname_', '')
            if fname =='rename':
                fname = request.POST.get('fname_')
            else:
                fname = audio.name

            #라벨종류
            label = request.POST.get('label')
            if label == 'self':
                label = request.POST.get('label_')
            else:
                file_path = f"media/music_sample/{audio}"
                label = 'Telephone' #확인용
                #label = label_type(file_path)#모델이용하기

            #분위기 종류
            mood = request.POST.get('mood')
            if label == 'self':
                label = request.POST.get('mood_')
            else:
                file_path = f"media/music_sample/{audio}"
                mood = '슬픔' #확인용
                #mood = mood_type(file_path)#모델이용하기
            #라이센스 
            licenses = request.POST.get('license')
            # 업로더?
            author = request.user
            # 작가
            author_op = request.POST.get('author')
            if author_op == 'user_': #본인
                real_author = request.user.username
            elif author_op == 'author': #직접입력
                real_author = request.POST.get('author_')
            else : #알수 없음
                newmusic = MusicDB(fname = fname, label = label, licenses = licenses, downloads = 0, mood=mood)
                newmusic.save()
                linkpk = MusicDB.objects.get(fname=fname).pk
                return redirect('subapp:detail', linkpk )
                # return redirect('mainapp:home') # 또는 마이페이지?

            newmusic = MusicDB(fname = fname, label = label, licenses = licenses,
            downloads = 0, author = author, mood=mood)
            newmusic.save()

            linkpk = MusicDB.objects.get(fname=fname).pk
            return redirect('subapp:detail', linkpk )
            # return redirect('mainapp:home') # 또는 마이페이지?
        else:
            context['error'] = '파일 입력 없음'
    else:
        pass

    return render(request, 'mainapp/upload.html', context)


def realtime(request):
    context = {}
    if request.method=='POST':
        if 'file' in request.FILES:
            audio = request.FILES['file']
            uploadfile = UploadMusicDB(audio=audio)
            uploadfile.save()
            context['audio'] = audio.name
            # print('views.py realtime audioname : ', audio.name)

            # audio 파일을 모델 함수에 입력 아웃풋 lagel값
            file_path = f"media/upload_music/{audio}"
            label = label_type(file_path) # 모델활용
            # label = 'Telephone' #확인용
            context['label'] = label

            # 분위기 분류
            mood = mood_type(file_path)#모델활용
            # mood = '슬픔' #확인용
            context['mood'] = mood 
            
            # 파일을 지우기 전에 유사도 분석까지 해야한다
            similarlist = similarAnalysis(audio.name)
            #############################################################################
            music_list = MusicDB.objects.filter(fname = similarlist[0])
            for name in similarlist[1:] :
                item = MusicDB.objects.filter(fname = name)
                # music_list = music_list.union(item)
                music_list = music_list | item

            #라벨 (분위기?) 필터링
            music_list = music_list.filter(label__contains = label)
            # music_list = music_list.filter(mood__contains = mood)
            # print("라벨 뮤직리스트 : ", music_list)
            name_list = []
            for item in music_list:
                print("name_list : ", item.fname)
                name_list.append(item.fname)
            # context['name_list'] = name_list
            context['similarlist'] = name_list #similarlist
            #############################################################################

            uploadfile.delete()
        else:
            context['audio'] = 'audio_none'
            context['label'] = 'label_none'
            context['mood'] = 'mood_none'
    else:
        context['audio'] = 'audio_none'
        context['label'] = 'label_none'
        context['mood'] = 'mood_none'

    return HttpResponse(json.dumps(context))

def search(request):
    context = {}
    audio = None
    label = None
    search_type = None
    similarlist = None
    check = True
    mood = None

    ####파일검색(최초)
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

            mood = mood_type(file_path)#모델활용
            # mood = '슬픔' #확인용
            context['mood'] = mood 

            # 파일을 지우기 전에 유사도 분석까지 해야한다
            similarlist = similarAnalysis(audio.name)
            music_list = MusicDB.objects.filter(fname = similarlist[0])
            for name in similarlist[1:] :
                item = MusicDB.objects.filter(fname = name)
                # music_list = music_list.union(item)
                music_list = music_list | item

            #라벨 (분위기?) 필터링
            music_list = music_list.filter(label__contains = label)
            # music_list = music_list.filter(mood__contains = mood)
            # print("라벨 뮤직리스트 : ", music_list)
            name_list = []
            for item in music_list:
                print("name_list : ", item.fname)
                name_list.append(item.fname)
            # context['name_list'] = name_list
            context['similarlist'] = name_list #similarlist 
            print("첫 파일검색 namelist : ", type(name_list), name_list)

            check = False        
            uploadfile.delete()
            
            search_type='filesearch'
            context['search_type'] = search_type
    else:
        label = request.GET.get('label', '')
        context['label'] = label
        audio = request.GET.get('audio', '')
        context['audio'] = audio
        mood = request.GET.get('mood', '')
        context['mood'] = mood

    ### GET 요청으로 들어올 경우 ##############################################
    # 검색 유형 확인하기
    if search_type == None:
        search_type = request.GET.get('search_type', 'keyword')
        context['search_type'] = search_type

    if (search_type == 'filesearch') or (search_type == 'realtimesearch') :
        if check: #파일 두번째 검색 또는 실시간 검색
            name_list = request.GET.get('similarlist')
            context['similarlist'] = name_list
            if search_type == 'realtimesearch':
                new_name_list = list(name_list.split(','))
            else:
                new_name_list = list(name_list[1:-1].replace("'", "").replace(" ", "").split(','))

            print("두번째 파일검색")
            print(new_name_list)
            print(type(new_name_list))
            music_list = MusicDB.objects.filter(fname = new_name_list[0])
            print("첫번째 객체 : ", music_list)
            for name in new_name_list[1:] :
                item = MusicDB.objects.filter(fname = name)
                # music_list = music_list.union(item)
                print(item)
                music_list = music_list | item
            print('여기 : ', music_list)
        else: #첫 파일 검색일 경우 
            pass
        print('파일/실시간 name_list 가져오기 완료')

        sort = request.GET.get('sort', 'similar') #나중에 기본설정 similar로 바꾸기
        context['sort'] = sort

        if sort == 'like': #좋아요순
            music_list = music_list.annotate(num_like=Count('like')).order_by('-num_like','-date')
        elif sort == 'download': #다운로드순
            music_list = music_list.order_by('-downloads', '-date')
        elif sort == 'similar': #유사도(기본)
            pass
        else: #recent 최신순 
            music_list = music_list.order_by('-date')

        print("파일/실시간 검색 sort 적용")
        print(music_list)
        
    else: #키워드 검색일때 (+ 유사도 안되는 실시간)
        ## DB 불러와서 정렬하기
        sort = request.GET.get('sort', 'like') # 키워드 검색은 기본 좋아요로 검색
        if sort == 'similar' : sort='like' # 만약 키워드가 유사도 검색이면 좋아요 순으로 변경
        context['sort'] = sort

        if sort == 'like': #좋아요순
            music_list = MusicDB.objects.annotate(num_like=Count('like')).order_by('-num_like','-date')
        elif sort == 'download': #다운로드순
            music_list = MusicDB.objects.order_by('-downloads', '-date')
        else: #recent 최신순
            music_list = MusicDB.objects.order_by('-date')

        ## 검색결과
        kw = request.GET.get('kw', '')
        context['kw'] = kw

        if kw != '' : # 키워드 검색 : 파일명or라벨명or분위기로 검색
            music_list = music_list.filter(
                Q(fname__contains=kw) | Q(label__contains=kw) | Q(mood__contains=kw)
            ).distinct()
        
        print('키워드 검색 라벨 필터링 완료')
    print(music_list)
    ## 라이센스 필터링
    licenses = request.GET.getlist('license[]', 'all')
    # print(licenses)
    if 'all' in licenses:
        #all 이 같이 입력되거나 아무것도 입력되지 않았을때
        context['license']='all'
    else:
        context['license'] = licenses
        # author commercial work
        if 'author' in licenses:
            #저작자 표기안함 : cc0
            music_list = music_list.filter(licenses='Creative Commons 0')
        
        if 'commercial' in licenses:
            # 상업적 이용가능 : cc0 / by-nb / by-sa / by
            # by-nc / by-nc-sa / by-nc-nd
            music_list = music_list.exclude(licenses__contains='Noncommercial')

        if 'work' in licenses:
            # 변경가능 : cc0 / by-nc / by-sa / by-nc-sa / by
            # 변경불가능 : by-nd / by-nc-nd
            music_list = music_list.exclude(licenses__contains='Derivative Works')

    print('라이센스필터링 완료')
    print(music_list)
    context['music_list'] = music_list[:20]
    return render(request, 'mainapp/search.html', context)