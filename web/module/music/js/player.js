// 播放器功能配置
var mkPlayer = {
    autoplay: false,    // 是否自动播放(true/false) *此选项在移动端可能无效
    volume: 0.6,        // 默认音量值(0~1之间)
};
// 存储全局变量
var rem = [];
// 音频错误处理函数
function audioErr() {
    // 没播放过，直接跳过
    if(rem.playlist === undefined) return true;
    
    if(rem.errCount > 10) { // 连续播放失败的歌曲过多
        layer.msg(window.parent.i18next.t('music.play.multi.error.text'));
        rem.errCount = 0;
    } else {
        rem.errCount++;     // 记录连续播放失败的歌曲数目
        layer.msg(window.parent.i18next.t('music.play.error.text'));
        nextMusic();    // 切换下一首歌
    } 
}

// 点击暂停按钮的事件
function pause() {
    if(rem.paused === false) {  // 之前是播放状态
        rem.audio[0].pause();  // 暂停
    } else {
        // 第一次点播放
        if(rem.playlist === undefined) {
            rem.playlist = rem.dislist;
            musicList[1].item = musicList[rem.playlist].item; // 更新正在播放列表中音乐
            listClick(0);
        }
        rem.audio[0].play();
    }
}

// 循环顺序
function orderChange() {
    var orderDiv = $(".btn-order");
    orderDiv.removeClass();
    switch(rem.order) {
        case 1:     // 单曲循环 -> 列表循环
            orderDiv.addClass("player-btn btn-order btn-order-list");
            orderDiv.attr("title", window.parent.i18next.t('music.control.circle.title'));
            layer.msg(window.parent.i18next.t('music.control.circle.title'));
            rem.order = 2;
            break;
            
        case 3:     // 随机播放 -> 单曲循环
            orderDiv.addClass("player-btn btn-order btn-order-single");
            orderDiv.attr("title", window.parent.i18next.t('music.control.circle.single.title'));
            layer.msg(window.parent.i18next.t('music.control.circle.single.title'));
            rem.order = 1;
            break;
            
        // case 2:
        default:    // 列表循环(其它) -> 随机播放
            orderDiv.addClass("player-btn btn-order btn-order-random");
            orderDiv.attr("title", window.parent.i18next.t('music.control.circle.random.title'));
            layer.msg(window.parent.i18next.t('music.control.circle.random.title'));
            rem.order = 3;
    }
}

// 播放
function audioPlay() {
    rem.paused = false;     // 更新状态（未暂停）
    refreshList();      // 刷新状态，显示播放的波浪
    $(".btn-play").addClass("btn-state-paused");        // 恢复暂停
    
    var music = musicList[rem.playlist].item[rem.playid];   // 获取当前播放的歌曲信息
    var msg = window.parent.i18next.t('music.play.window.title') + music.name ;  // 改变浏览器标题
    // 清除定时器
    if (rem.titflash !== undefined ) {clearInterval(rem.titflash);}
    // 标题滚动
    titleFlash(msg);
}
// 标题滚动
function titleFlash(msg) {
    // 截取字符
    var tit = function() {
        msg = msg.substring(1,msg.length)+ msg.substring(0,1);
        window.parent.document.querySelectorAll('.window.music>.titbar>span>.title')[0].innerText = msg;
    };
    // 设置定时间 300ms滚动
    rem.titflash = setInterval(function(){tit()}, 300);
}
// 暂停
function audioPause() {
    rem.paused = true;      // 更新状态（已暂停）
    $(".list-playing").removeClass("list-playing");        // 移除其它的正在播放
    $(".btn-play").removeClass("btn-state-paused");     // 取消暂停

     // 清除定时器
    if (rem.titflash !== undefined ) 
    {
        clearInterval(rem.titflash);
    }
    window.parent.document.querySelectorAll('.window.music>.titbar>span>.title')[0].innerText = rem.webTitle;    // 改变浏览器标题
}

// 播放上一首歌
function prevMusic() {
    playList(rem.playid - 1);
}

// 播放下一首歌
function nextMusic() {
    switch (rem.order ? rem.order : 1) {
        case 1,2: 
            playList(rem.playid + 1);
        break;
        case 3: 
            if (musicList[0] && musicList[0].item.length) {
                var id = parseInt(Math.random() * musicList[0].item.length);
                playList(id);
            }
        break;
        default:
            playList(rem.playid + 1); 
        break;
    }
}
// 自动播放时的下一首歌
function autoNextMusic() {
    if(rem.order && rem.order === 1) {
        playList(rem.playid);
    } else {
        nextMusic();
    }
}

// 歌曲时间变动回调函数
function updateProgress(){
    // 暂停状态不管
    if(rem.paused !== false) return true;
    // 同步进度条
    let process_play = rem.audio[0].currentTime / rem.audio[0].duration;
    if (process_play > 0.3 && rem.set_history) {
        rem.set_history = false;
        if (rem.post_data.file_id.length > 16) {return;}
        window.parent.$.ajax({
            type: 'POST',
            url: servers + '/music/record/set',
            data: JSON.stringify(rem.post_data),
            contentType: 'application/json',
            success: function (data) {
                if (data['code'] !== 0) {
                    window.parent.$.Toast(data['msg'], 'error');
                }
            }
        })
    }
	music_bar.goto(process_play);
    $('#play-time')[0].innerText = formatSeconds(rem.audio[0].currentTime);
    // 同步歌词显示	
	scrollLyric(rem.audio[0].currentTime);
}

// 显示的列表中的某一项点击后的处理函数
// 参数：歌曲在列表中的编号
function listClick(no) {
    // 记录要播放的歌曲的id
    var tmpid = no;

    // 与之前不是同一个列表了（在播放别的列表的歌曲）或者是首次播放
    if((rem.dislist !== rem.playlist && rem.dislist !== 0) || rem.playlist === undefined) {
        rem.playlist = rem.dislist;     // 记录正在播放的列表
        musicList[0].item = musicList[rem.playlist].item; // 更新正在播放列表中音乐
        // 刷新正在播放的列表的动画
        refreshSheet();     // 更改正在播放的列表的显示
    }
    playList(tmpid);
    return true;
}

// 播放正在播放列表中的歌曲
// 参数：歌曲在列表中的ID
function playList(id) {
    // 第一次播放
    if(rem.playlist === undefined) {
        pause();
        return true;
    }
    if (rem.dislist === undefined) {rem.dislist = 0;}
    
    // 没有歌曲，跳出
    if(musicList[rem.dislist].item.length <= 0) return true;
    // ID 范围限定
    if(id >= musicList[rem.dislist].item.length) id = 0;
    if(id < 0) id = musicList[rem.dislist].item.length - 1;
    // 记录正在播放的歌曲在正在播放列表中的 id
    rem.playid = id;
    play(musicList[rem.dislist].item[id]);
}

// 初始化 Audio
function initAudio() {
    rem.audio = $('<audio></audio>').appendTo('body');
    // 应用初始音量
    rem.audio[0].volume = volume_bar.percent;
    // 绑定歌曲进度变化事件
    rem.audio[0].addEventListener('timeupdate', updateProgress);   // 更新进度
    rem.audio[0].addEventListener('play', audioPlay); // 开始播放了
    rem.audio[0].addEventListener('pause', audioPause);   // 暂停
    $(rem.audio[0]).on('ended', autoNextMusic);   // 播放结束
    rem.audio[0].addEventListener('error', audioErr);   // 播放器错误处理
}


// 播放音乐
// 参数：要播放的音乐数组
function play(music) {
    // 遇到错误播放下一首歌
    if(music.url === "err") {
        audioErr(); // 调用错误处理函数
        return false;
    }
    
    try {
        rem.audio[0].pause();
        rem.audio.attr('src', music.url);
        rem.audio[0].play();
        rem.mp3_id = music.id
        rem.post_data = {
            file_id: music.id,
            name: music.name,
            duration: music.duration
        };
        rem.set_history = true;
    } catch(e) {
        audioErr(); // 调用错误处理函数
        return;
    }
    
    rem.errCount = 0;   // 连续播放失败的歌曲数归零
    music_bar.goto(0);  // 进度条强制归零
    ajaxLyric(music, lyricCallback);     // ajax加载歌词
    music_bar.lock(false);  // 取消进度条锁定
}

// 音乐进度条拖动回调函数
function mBcallback(newVal) {
    var newTime = rem.audio[0].duration * newVal;
    // 应用新的进度
    rem.audio[0].currentTime = newTime;
    refreshLyric(newTime);  // 强制滚动歌词到当前进度
}

// 音量条变动回调函数
// 参数：新的值
function vBcallback(newVal) {
    if(rem.audio[0] !== undefined) {   // 音频对象已加载则立即改变音量
        rem.audio[0].volume = newVal;
    }
    if($(".btn-quiet").is('.btn-state-quiet')) {
        $(".btn-quiet").removeClass("btn-state-quiet");     // 取消静音
    }
    
    if(newVal === 0) $(".btn-quiet").addClass("btn-state-quiet");
    localStorage.setItem('mp3_volume', newVal); // 存储音量信息
}

// 下面是进度条处理
var initProgress = function(){  
    // 初始化播放进度条
    music_bar = new mkpgb("#music-progress", 0, mBcallback);
    music_bar.lock(true);   // 未播放时锁定不让拖动
    // 初始化音量设定
    var tmp_vol = localStorage.getItem('mp3_volume');
    tmp_vol = (tmp_vol != null)? tmp_vol: mkPlayer.volume;
    if(tmp_vol < 0) tmp_vol = 0;    // 范围限定
    if(tmp_vol > 1) tmp_vol = 1;
    if(tmp_vol === 0) $(".btn-quiet").addClass("btn-state-quiet"); // 添加静音样式
    volume_bar = new mkpgb("#volume-progress", tmp_vol, vBcallback);
};  

// mk进度条插件
// 进度条框 id，初始量，回调函数
mkpgb = function(bar, percent, callback){  
    this.bar = bar;
    this.percent = percent;
    this.callback = callback;
    this.locked = false;
    this.init();  
};

mkpgb.prototype = {
    // 进度条初始化
    init : function(){  
        var mk = this,mdown = false;
        // 加载进度条html元素
        $(mk.bar).html('<div class="mkpgb-bar"></div><div class="mkpgb-cur"></div><div class="mkpgb-dot"></div>');
        // 获取偏移量
        mk.minLength = $(mk.bar).offset().left; 
        mk.maxLength = $(mk.bar).width() + mk.minLength;
        // 窗口大小改变偏移量重置
        $(window).resize(function(){
            mk.minLength = $(mk.bar).offset().left; 
            mk.maxLength = $(mk.bar).width() + mk.minLength;
        });
        // 监听小点的鼠标按下事件
        $(mk.bar + " .mkpgb-dot").mousedown(function(e){
            e.preventDefault();    // 取消原有事件的默认动作
        });
        // 监听进度条整体的鼠标按下事件
        $(mk.bar).mousedown(function(e){
            if(!mk.locked) mdown = true;
            barMove(e);
        });
        // 监听鼠标移动事件，用于拖动
        $("html").mousemove(function(e){
            barMove(e);
        });
        // 监听鼠标弹起事件，用于释放拖动
        $("html").mouseup(function(e){
            mdown = false;
        });
        
        function barMove(e) {
            if(!mdown) return;
            var percent = 0;
            if(e.clientX < mk.minLength){ 
                percent = 0; 
            }else if(e.clientX > mk.maxLength){ 
                percent = 1;
            }else{  
                percent = (e.clientX - mk.minLength) / (mk.maxLength - mk.minLength);
            }
            mk.callback(percent);
            mk.goto(percent);
            return true;
        }
        
        mk.goto(mk.percent);
        
        return true;
    },
    // 跳转至某处
    goto : function(percent) {
        if(percent > 1) percent = 1;
        if(percent < 0) percent = 0;
        this.percent = percent;
        $(this.bar + " .mkpgb-dot").css("left", (percent*100) +"%"); 
        $(this.bar + " .mkpgb-cur").css("width", (percent*100)+"%");
        return true;
    },
    // 锁定进度条
    lock : function(islock) {
        if(islock) {
            this.locked = true;
            $(this.bar).addClass("mkpgb-locked");
        } else {
            this.locked = false;
            $(this.bar).removeClass("mkpgb-locked");
        }
        return true;
    }
};  

// 快捷键切歌，代码来自 @茗血(https://www.52benxi.cn/)
document.onkeydown = function showkey(e) {
    var key = e.keyCode || e.which || e.charCode;
    var ctrl = e.ctrlKey || e.metaKey;
    var isFocus = $('input').is(":focus");  
    if (ctrl && key === 37) playList(rem.playid - 1);    // Ctrl+左方向键 切换上一首歌
    if (ctrl && key === 39) playList(rem.playid + 1);    // Ctrl+右方向键 切换下一首歌
    if (key === 32 && isFocus === false) pause();         // 空格键 播放/暂停歌曲
}

// ajax加载歌词
function ajaxLyric(music, callback) {
    lyricTip(window.parent.i18next.t('music.lyric.loading.error.text'));
    if (music.lyric_url === ''){callback('');return;}
    window.parent.$.ajax({
        type: 'GET',
        url: music.lyric_url,
        success: function(data){
            if (data['code'] === 0) {
                callback(data['data']);
            } else if(data['code'] > 0) {
                callback('');
            } else {
                callback(data);
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            layer.msg(XMLHttpRequest.status);
            console.error(XMLHttpRequest + textStatus + errorThrown);
            callback('');
        }
    });
}

function formatSeconds(totalSeconds) {
    let minutes = Math.floor(totalSeconds / 60);
    let seconds = Math.floor(totalSeconds % 60);
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}
