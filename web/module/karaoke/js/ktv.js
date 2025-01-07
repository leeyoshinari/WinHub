const video = document.getElementById('myVideo');
const vocals = document.getElementById('vocals');
const accompaniment = document.getElementById('accompaniment');
const interruption = document.getElementById('interruption');
let server = localStorage.getItem("server");
let lang = localStorage.getItem("lang");
if (!server || !lang) {
    let params = window.location.href.split('&');
    server = params[0].split('=')[1];
    lang = params[1].split('=')[1];
}
$.ajaxSetup({beforeSend:function(xhr){xhr.setRequestHeader('lang', lang);}});

let videoReady = false;
let vocalsReady = false;
let accompanimentReady = false;
let vocalsVolume = localStorage.getItem("vocalsVolume")? parseFloat(localStorage.getItem("vocalsVolume")): 1;
let accompanimentVolume = localStorage.getItem("accompanimentVolume")? parseFloat(localStorage.getItem("accompanimentVolume")): 1;
let openSetting = false;
let singsList = [];
let isBindEvent = false;

localStorage.setItem('vocalsVolume', vocalsVolume.toString());
localStorage.setItem('accompanimentVolume', accompanimentVolume.toString());
video.volume = 0;
vocals.volume = vocalsVolume;
accompaniment.volume = accompanimentVolume;

getSingList = (flag = false) => {
    $.ajax({
        type: "GET",
        async: flag,
        url: server + "/karaoke/singHistory/pendingAll",
        success: function (data) {
            if (data.code === 0) {
                singsList = data.data;
            } else {
                $.Toast(data.msg, "error");
            }
        }
    })
}

loadSing = (flag=false) => {
    getSingList(false);
    if (singsList.length < 1) {return;}
    let file_name = singsList[0].name;
    let video_name = file_name + ".mp4";
    let vocals_name = file_name + "_vocals.mp3";
    let accompaniment_name = file_name + "_accompaniment.mp3";
    video.src = server + '/karaoke/download/' + video_name + '?lang=' + lang;
    vocals.src = server + '/karaoke/download/' + vocals_name + '?lang=' + lang;
    accompaniment.src = server + '/karaoke/download/' + accompaniment_name + '?lang=' + lang;
    if (flag) {
        video.addEventListener('canplaythrough', () => {videoReady = true; tryPlay();});
        vocals.addEventListener('canplaythrough', () => {vocalsReady = true; tryPlay();});
        accompaniment.addEventListener('canplaythrough', () => {accompanimentReady = true; tryPlay();});
    } else {
        video.addEventListener('canplaythrough', () => {videoReady = true;});
        vocals.addEventListener('canplaythrough', () => {vocalsReady = true;});
        accompaniment.addEventListener('canplaythrough', () => {accompanimentReady = true;});
    }
    showTips();
}

showTips = () => {
    let playinText = "暂未开始播放"
    if (singsList.length > 0) {
        if (singsList[0].is_sing === -1) {
            playinText = "当前播放：" + singsList[0].name;
            if (singsList.length > 1) {
                playinText = playinText + "，下一首：" + singsList[1].name;
            } else {
                playinText = playinText + "，暂无下一首歌曲"
            }
        } else {
            playinText = playinText + "，下一首：" + singsList[0].name;
        }
    } else {
        playinText = playinText + "，暂无下一首歌曲"
    }
    document.getElementById("playing-text").innerText = playinText;
}

tryPlay = () => {
    if (videoReady && vocalsReady && accompanimentReady) {
        video.play().catch(error => {
            console.error("视频播放失败:", error);
            $.Toast("第一次请手动点击播放按钮 ~", "error");
        });
        vocals.play().catch(error => {
            console.error("人声播放失败:", error);
            $.Toast("第一次请手动点击播放按钮 ~", "error");
        });
        accompaniment.play().catch(error => {
            console.error("伴奏播放失败:", error);
            $.Toast("第一次请手动点击播放按钮 ~", "error");
        });
    }
}

// 同步时间
video.addEventListener('timeupdate', () => {
    if (Math.abs(video.currentTime - vocals.currentTime) > 0.2 || Math.abs(accompaniment.currentTime - video.currentTime) > 0.2) {
        vocals.currentTime = video.currentTime;
        accompaniment.currentTime = video.currentTime;
    }
});

// vocals.addEventListener('timeupdate', () => {
//     if (Math.abs(vocals.currentTime - video.currentTime) > 0.2) {
//         video.currentTime = vocals.currentTime;
//         accompaniment.currentTime = vocals.currentTime;
//     }
// });

// accompaniment.addEventListener('timeupdate', () => {
//     if (Math.abs(accompaniment.currentTime - video.currentTime) > 0.2) {
//         video.currentTime = accompaniment.currentTime;
//         vocals.currentTime = accompaniment.currentTime;
//     }
// });

// 暂停和播放事件
video.addEventListener('pause', () => {
    vocals.pause();
    accompaniment.pause();
    send_message(1, 4);
});

video.addEventListener('play', () => {
    setSinging();
    tryPlay();
    send_message(1, 3);
    getSingList(false);
    showTips();
});

video.addEventListener('ended', () => {
    videoReady = false;
    vocalsReady = false;
    accompanimentReady = false;
    nextSong();
});

document.getElementById("switchVocal").addEventListener('click', () => {
    let switch_button = document.getElementById("switchVocal");
    if (switch_button.getElementsByTagName('span')[0].innerText === "原唱") {
        send_message(4, 1);
    } else {
        send_message(4, 0);
    }
})

document.getElementById("next-song").addEventListener('click', () => {send_message(3, 0);})

send_message = (code, data) => {
    $.ajax({
        type: "GET",
        url: server + "/karaoke/send/event?code=" + code + "&data=" + data,
        success: function (data) {
            if (data.code !== 0) {
                $.Toast(data.msg, 'error');
            }
        }
    })
}

switchVocal = (flag) => {
    let switch_button = document.getElementById("switchVocal");
    if (flag === 'ON') {
        switch_button.getElementsByTagName('span')[0].innerText = "原唱"
        switch_button.style.filter = "grayscale(0)";
        vocals.volume = vocalsVolume;
    } else {
        switch_button.getElementsByTagName('span')[0].innerText = "伴奏"
        switch_button.style.filter = "grayscale(1)";
        vocals.volume = 0;
    }
}

first_play = () => {
    if (singsList.length > 0) {
        loadSing();
        tryPlay();
    }
}

nextSong = () => {
    if (singsList.length > 0) {setSinged(false);}
    getSingList(false);
    if (singsList.length < 1) {
        document.getElementById("playing-text").innerText = "当前没有待播放的歌曲，快去点歌吧 ~";
        video.src = "";
        vocals.src = "";
        accompaniment.src = "";
        return;
    }
    singsList.shift();
    loadSing(true);
}

reSing = () => {
    video.currentTime = 0;
    vocals.currentTime = 0;
    accompaniment.currentTime = 0;
    video.play();
}

setSinged = (flag = false) => {
    $.ajax({
        type: "GET",
        async: flag,
        url: server + "/karaoke/setSinged/" + singsList[0].id,
        success: function (data) {
            if (data.code !== 0) {
                $.Toast(data.msg, "error");
            }
        }
    })
}

setSinging = (flag = false) => {
    $.ajax({
        type: "GET",
        async: flag,
        url: server + "/karaoke/setSinging/" + singsList[0].id,
        success: function (data) {
            if (data.code !== 0) {
                $.Toast(data.msg, "error");
            }
        }
    })
}

changeVolume = (volume, flag) => {
    if (flag === 'vocals') {
        vocalsVolume = volume;
        vocals.volume = vocalsVolume;
        localStorage.setItem('vocalsVolume', vocalsVolume.toString());
    } else {
        accompanimentVolume = volume;
        accompaniment.volume = accompanimentVolume;
        localStorage.setItem('accompanimentVolume', accompanimentVolume.toString());
    }
}

initVolume = (eleId) => {
    let mdown = false;
    let progressEle = document.getElementById(eleId);
    let startIndex = progressEle.getBoundingClientRect().left;
    if (eleId === "volume-vocals-progress") {
        vocals.volume = vocalsVolume;
        progressEle.getElementsByClassName("mkpgb-cur")[0].style.width = vocalsVolume * 100 + '%';
        progressEle.getElementsByClassName("mkpgb-dot")[0].style.left = vocalsVolume * 100 + '%';
    } else {
        accompaniment.volume = accompanimentVolume;
        progressEle.getElementsByClassName("mkpgb-cur")[0].style.width = accompanimentVolume * 100 + '%';
        progressEle.getElementsByClassName("mkpgb-dot")[0].style.left = accompanimentVolume * 100 + '%';
    }
    if (isBindEvent) {return;}
    progressEle.getElementsByClassName("mkpgb-dot")[0].addEventListener("mousedown", (e) => {
        e.preventDefault();
    })
    progressEle.addEventListener("mousedown", (e) => {
        mdown = true;
        isBindEvent = true;
        barMove(e);
    })
    progressEle.addEventListener("mousemove", (e) => {
        barMove(e);
    })
    progressEle.addEventListener("mouseup", (e) => {
        if (eleId === "volume-vocals-progress") {send_message(5, vocalsVolume);
        } else {send_message(6, accompanimentVolume);}
        mdown = false;
        isBindEvent = true;
    })
    function barMove(e) {
        if(!mdown) return;
        let percent = 0;
        if(e.clientX < startIndex){
            percent = 0;
        }else if(e.clientX > progressEle.clientWidth + startIndex){
            percent = 1;
        }else{
            percent = (e.clientX - startIndex) / progressEle.clientWidth;
        }
        if (eleId === "volume-vocals-progress") {
            vocalsVolume = percent;
            vocals.volume = vocalsVolume;
            localStorage.setItem('vocalsVolume', vocalsVolume.toString());

        } else {
            accompanimentVolume = percent;
            accompaniment.volume = accompanimentVolume;
            localStorage.setItem('accompanimentVolume', accompanimentVolume.toString());
        }
        progressEle.getElementsByClassName("mkpgb-cur")[0].style.width = percent * 100 + '%';
        progressEle.getElementsByClassName("mkpgb-dot")[0].style.left = percent * 100 + '%';
        return true;
    }
}

userInterruption = (flag) => {
    interruption.src = "./file/" + flag + ".mp3";
    interruption.volume = 0.8;
    interruption.play();
}

document.getElementsByClassName("setting-img")[0].addEventListener("click", () => {
    if (openSetting) {
        openSetting = false;
        document.getElementById("expand-img").src = "img/expand.svg";
        document.getElementsByClassName("setting-list")[0].style.display = 'none';
        document.getElementsByClassName("volume-setting")[0].style.display = 'none';
    } else {
        openSetting = true;
        document.getElementById("expand-img").src = "img/pickup.svg";
        document.getElementsByClassName("setting-list")[0].style.display = 'flex';
    }
})

document.getElementById("change-volume").addEventListener("click", () => {
    let volume_setting = document.getElementsByClassName("volume-setting")[0];
    if (volume_setting.style.display === 'flex') {
        volume_setting.style.display = 'none';
        return;
    }
    let volume_list = document.getElementsByClassName("setting")[0].offsetTop;
    volume_setting.style.top = volume_list + 72 + "px";
    volume_setting.style.display = 'flex';
    initVolume("volume-vocals-progress");
    initVolume("volume-acc-progress");
})

window.onload = function() {
    loadSing();

    const eventSource = new EventSource(server + "/karaoke/events");
    eventSource.onmessage = function(event) {
        const message = JSON.parse(event.data);
        switch (message.code) {
            case 1:
                if (message.data === '0') {video.pause();}
                if (message.data === '1') {video.play();}
                if (message.data === '5') {first_play();}
                break;
            case 2:
                reSing();
                break;
            case 3:
                nextSong();
                break;
            case 4:
                if (message.data === '0') {switchVocal("ON");}
                if (message.data === '1') {switchVocal("OFF");}
                break;
            case 5:
                changeVolume(message.data, "vocals");
                break;
            case 6:
                changeVolume(message.data, "accompaniment");
                break;
            case 7:
                userInterruption(message.data);
                break;
            case 8:
                getSingList(false);
                showTips();
                break;
        }
    };
    eventSource.onerror = function(event) {
        console.error("EventSource failed:", event);
        eventSource.close();
    };
};
