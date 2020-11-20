const record = document.getElementById("record");
const stop = document.getElementById("stop");
const soundClips = document.getElementById("sound-clips");
const chkHearMic = document.getElementById("chk-hear-mic");

const audioCtx = new(window.AudioContext || window.webkitAudioContext)(); // 오디오 컨텍스트 정의
const analyser = audioCtx.createAnalyser()

function makeSound(stream) {
    const source = audioCtx.createMediaStreamSource(stream);

    source.connect(analyser);
    analyser.connect(audioCtx.destination);
};

function getCookie(cname) { //csrf_token 가져오는 용도
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length,c.length);
        }
    }
    return "";
}
// ======= 사용할 변수 함수 정의 =========

if (navigator.mediaDevices) {
    console.log('getUserMedia supported.'); //웹 콘솔창에 표시
    const constraints = {
        audio: true
    };
    let chunks = [];

    navigator.mediaDevices.getUserMedia(constraints)
        .then(stream => {

            const mediaRecorder = new MediaRecorder(stream);
            
            chkHearMic.onchange = e => { // 마이크 소리듣기 옵션
                if(e.target.checked == true) {
                    audioCtx.resume();
                    makeSound(stream);
                } else {
                    audioCtx.suspend();
                };
            };
            
            record.onclick = () => { //녹음버튼누르면 녹음시작
                mediaRecorder.start();
                console.log(mediaRecorder.state);
                console.log("recorder started");
                record.style.background = "red";
                record.style.color = "black";
            };

            stop.onclick = () => { //stop버튼 무르면 중지
                mediaRecorder.stop();
                console.log(mediaRecorder.state);
                console.log("recorder stopped");
                record.style.background = "";
                record.style.color = "";
            };

            mediaRecorder.onstop = e => { //mediaRecorder가 stop 상태가 되면 (stop 버튼 누르면)
                console.log("data available after MediaRecorder.stop() called.");

                // const clipName = prompt("오디오 파일 제목을 입력하세요.", new Date()); //이름지정안하면 날짜로 기본설정
                const clipName = prompt("오디오 파일 제목을 입력하세요.", 'default'); // 날짜 형식오류나서 문자열로 변경

                const clipContainer = document.createElement('article');
                const clipLabel = document.createElement('p');
                const audio = document.createElement('audio');
                const deleteButton = document.createElement('button');
                const submitButton = document.createElement('button'); //제출버튼 추가

                clipContainer.classList.add('clip');
                audio.setAttribute('controls', '');
                deleteButton.innerHTML = "삭제";
                submitButton.innerHTML = "등록";
                clipLabel.innerHTML = clipName;
                submitButton.setAttribute('type', 'submit')//제출버튼 속성추가
                submitButton.setAttribute('class', 'rt_button')
                deleteButton.setAttribute('class', 'rt_button')

                clipContainer.appendChild(audio);
                clipContainer.appendChild(clipLabel);
                clipContainer.appendChild(deleteButton);
                clipContainer.appendChild(submitButton);//제출버튼 clipcontainer에 추가
                soundClips.appendChild(clipContainer);

                audio.controls = true;
                const blob = new Blob(chunks, {'type': 'audio/ogg codecs=opus'});
                
                chunks = [];
                const audioURL = URL.createObjectURL(blob);
                audio.src = audioURL;
                console.log("recorder stopped");

                deleteButton.onclick = e => {
                    evtTgt = e.target;
                    evtTgt.parentNode.parentNode.removeChild(evtTgt.parentNode);
                };

                submitButton.onclick = () => { 
                    submitButton.innerHTML = "등록중";
                    submitButton.setAttribute('disabled', 'disabled')

                    const fd = new FormData;
                    fd.append('file', blob, clipName+".wav");

                    var headers = new Headers();
                    var csrftoken = getCookie('csrftoken');
                    headers.append('X-CSRFToken', csrftoken);

                    const audioinput = document.getElementById("audio_input");
                    const labelinput = document.getElementById("label_input");
                    const similarlistinput = document.getElementById("similarlist_input");
                    const moodinput = document.getElementById("mood_input");
                    const filepathinput = document.getElementById("file_path_input");

                    // const response = fetch("{% url 'mainapp:realtime' %}", {method:"POST", headers:headers, redirect:'follow', body:fd})
                    const response = fetch("realtime/", {method:"POST", headers:headers, redirect:'follow', body:fd})
                    .then(response => response.json())
                    .then(function(res){
                        console.log(res)
                        audioinput.setAttribute('value', res['audio']);
                        labelinput.setAttribute('value', res['label']);
                        moodinput.setAttribute('value', res['mood']);
                        similarlistinput.setAttribute('value', res['similarlist']);
                        filepathinput.setAttribute('value', res['file_path']);
                    })
                    .then(function(){
                        const realtime_search = document.getElementById("realtime_search");
                        realtime_search.style.display = "block";
                    })
                    .catch(err=> console.error(err));
                };

            };

            mediaRecorder.ondataavailable = e => {
                chunks.push(e.data);
            };
        })
        .catch(err => {
            console.log('The following error occurred: ' + err);
        })
};
