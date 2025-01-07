let params = window.location.href.split('&');
let servers = params[0].split('=')[1];
let file_id = params[1].split('=')[1];
if (localStorage.getItem('transparent') === '1') {
    $('.blur-mask')[0].style.backgroundColor = '#00000000';
}
$('#btn-area>span')[0].innerText = window.parent.i18next.t('music.btn.box.playing.text');
$('#btn-area>span')[0].title = window.parent.i18next.t('music.btn.box.playing.title');
$('#btn-area>span')[1].innerText = window.parent.i18next.t('music.btn.box.history.text');
$('#btn-area>span')[1].title = window.parent.i18next.t('music.btn.box.history.title');
$('#btn-area>span')[2].innerText = window.parent.i18next.t('music.btn.box.usual.text');
$('#btn-area>span')[2].title = window.parent.i18next.t('music.btn.box.usual.title');
$('#btn-area>span')[3].innerText = window.parent.i18next.t('music.btn.box.adds.text');
$('#btn-area>span')[3].title = window.parent.i18next.t('music.btn.box.adds.title');
$('#btn-area>span')[4].innerText = window.parent.i18next.t('music.btn.box.addc.text');
$('#btn-area>span')[4].title = window.parent.i18next.t('music.btn.box.addc.title');
$('.player-btn.btn-prev')[0].title = window.parent.i18next.t('music.control.preview.title');
$('.player-btn.btn-next')[0].title = window.parent.i18next.t('music.control.next.title');
$('.player-btn.btn-play')[0].title = window.parent.i18next.t('music.control.pause.title');
$('.player-btn.btn-order')[0].title = window.parent.i18next.t('music.control.circle.title');
$('.player-btn.btn-quiet')[0].title = window.parent.i18next.t('music.control.mute.title');
var isMobile = {
    Android: function() {return !!navigator.userAgent.match(/Android/i);},
    BlackBerry: function() {return !!navigator.userAgent.match(/BlackBerry/i);},
    iOS: function() {return !!navigator.userAgent.match(/iPhone|iPad|iPod/i);},
    Windows: function() {return !!navigator.userAgent.match(/IEMobile/i);},
    any: function() {return (isMobile.Android() || isMobile.BlackBerry() || isMobile.iOS() || isMobile.Windows());}
};
if (isMobile.any()) {$('#play_local_mp3')[0].setAttribute('accept', '*');}
var musicList = [{name: "正在播放", item: []}, {name: "播放历史", item: []}, {name: "经常听的", item: []}];
let startClientX = 0;
let startClientY = 0;
let endClientX = 0;
let endClientY = 0;
$(function(){
    rem.webTitle = document.title;      // 记录页面原本的标题
    rem.errCount = 0;         // 连续播放失败的歌曲数归零
    initProgress();     // 初始化音量条、进度条（进度条初始化要在 Audio 前，别问我为什么……）
    initAudio();    // 初始化 audio 标签，事件绑定
    $("#main-list,#sheet").mCustomScrollbar({
        theme:"minimal",
        advanced:{updateOnContentResize: true}  // 数据更新后自动刷新滚动条
    });
    rem.mainList = $("#main-list .mCSB_container");
    addListhead();  // 列表头
    addListbar("loading");  // 列表加载中
    // 顶部按钮点击处理
    $(".btn").click(function(){
        switch($(this).data("action")) {
            case "history":
                $(".btn[data-action='history']").addClass("btn-select");
                $(".btn[data-action='playing']").removeClass("btn-select");
                $(".btn[data-action='usual']").removeClass("btn-select");
                get_history(1);
            break;
            case "playing": // 正在播放
                $(".btn[data-action='playing']").addClass("btn-select");
                $(".btn[data-action='history']").removeClass("btn-select");
                $(".btn[data-action='usual']").removeClass("btn-select");
                loadList(0); // 显示正在播放列表
            break;
            case "usual":   // 播放列表
                $(".btn[data-action='usual']").addClass("btn-select");
                $(".btn[data-action='playing']").removeClass("btn-select");
                $(".btn[data-action='history']").removeClass("btn-select");
                get_history(2);
            break;
            case "adds":
                add_files_s();
            break;
            case "addc":
                play_local_mp3();
            break;
        }
    });
    
    // 列表项双击播放
    $(".music-list").on("dblclick",".list-item", function() {
        var num = parseInt($(this).data("no"));
        if(isNaN(num)) return false;
        listClick(num);
    });
    // 点击加载更多
    // $(".music-list").on("click",".list-loadmore", function() {
    //     $(".list-loadmore").removeClass('list-loadmore');
    //     $(".list-loadmore").html('加载中...');
    //     ajaxSearch();
    // });
    
    $(".btn-play").click(function(){pause();}); // 播放、暂停按钮的处理
    $(".btn-order").click(function(){orderChange();});  // 循环顺序的处理
    $(".btn-prev").click(function(){prevMusic();}); // 上一首歌
    $(".btn-next").click(function(){nextMusic();}); // 下一首
    
    // 静音按钮点击事件
    $(".btn-quiet").click(function(){
        var oldVol;     // 之前的音量值
        if($(this).is('.btn-state-quiet')) {
            oldVol = $(this).data("volume");
            oldVol = oldVol? oldVol: mkPlayer.volume;  // 没找到记录的音量，则重置为默认音量
            $(this).removeClass("btn-state-quiet");     // 取消静音
        } else {
            oldVol = volume_bar.percent;
            $(this).addClass("btn-state-quiet");        // 开启静音
            $(this).data("volume", oldVol); // 记录当前音量值
            oldVol = 0;
        }
        localStorage.setItem('mp3_volume', oldVol);  // 存储音量信息
        volume_bar.goto(oldVol);    // 刷新音量显示
        if(rem.audio[0] !== undefined) rem.audio[0].volume = oldVol;  // 应用音量
    });
    // 初始化播放列表
    initList(); 
});

// 向列表中载入某个播放列表
function loadList(list) {
    rem.dislist = list;     // 记录当前显示的列表
    dataBox("list");    // 在主界面显示出播放列表
    rem.mainList.html('');   // 清空列表中原有的元素
    addListhead();      // 向列表中加入列表头
    
    if(musicList[list].item.length === 0) {
        addListbar("nodata");   // 列表中没有数据
    } else {
        // 逐项添加数据
        for(var i=0; i<musicList[list].item.length; i++) {
            var tmpMusic = musicList[list].item[i];
            addItem(i + 1, tmpMusic.name, tmpMusic.duration);
        }
        // 列表加载完成后的处理
        if(list === 0) {    // 历史记录和正在播放列表允许清空
            addListbar("clear");    // 清空列表
        }

        if(rem.playlist === undefined) {    // 未曾播放过
            if(mkPlayer.autoplay === true) pause();  // 设置了自动播放，则自动播放
        } else {
            refreshList();  // 刷新列表，添加正在播放样式
        }
        listToTop();    // 播放列表滚动到顶部
        document.querySelectorAll('.list-item').forEach(item => {
            item.addEventListener('touchstart', function (e) {
                startClientX = e.touches[0].clientX;
                startClientY = e.touches[0].clientY;
                endClientX = startClientX;
                endClientY = startClientY;
            }, false);
            item.addEventListener('touchmove', function (e) {
                endClientX = e.touches[0].clientX;
                endClientY = e.touches[0].clientY;
            }, false);
            item.addEventListener('touchend', function (e) {
                if (Math.abs(endClientX - startClientX) < 2 || Math.abs(endClientY - startClientY) < 2) {
                    if (this.classList.contains('list-clickable')) return;
                    var num = parseInt($(this).data("no"));
                    if (isNaN(num)) return;
                    listClick(num);
                }
            }, false);
        })
    }
}

// 播放列表滚动到顶部
function listToTop() {
    // $("#main-list").animate({scrollTop: 0}, 200);
    $("#main-list").mCustomScrollbar("scrollTo", 0, "top");
}

// 向列表中加入列表头
function addListhead() {
    var html = '<div class="list-item list-head">' +
    '<span class="music-album">' + window.parent.i18next.t('music.list.header.duration') + '</span>' +
    '<span class="music-name">' + window.parent.i18next.t('music.list.header.song') + '</span></div>';
    rem.mainList.append(html);
}

// 列表中新增一项
// 参数：编号、名字、歌手、专辑
function addItem(no, name, album) {
    var html = '<div class="list-item" data-no="' + (no - 1) + '">' +
    '    <span class="list-num">' + no + '</span>' +
    '    <span class="music-album">' + album + '</span>' +
    '    <span class="music-name">' + name + '</span>' +
    '</div>'; 
    rem.mainList.append(html);
}

// 加载列表中的提示条
// 参数：类型（more、nomore、loading、nodata、clear）
function addListbar(types) {
    var html
    switch(types) {
        case "more":    // 还可以加载更多
            html = '<div class="list-item text-center list-loadmore list-clickable" title="点击加载更多数据" id="list-foot">点击加载更多...</div>';
        break;
        case "nomore":  // 数据加载完了
            html = '<div class="list-item text-center" id="list-foot">全都加载完了</div>';
        break;
        case "loading": // 加载中
            html = '<div class="list-item text-center" id="list-foot">' + window.parent.i18next.t('music.list.loading.loading') + '...</div>';
        break;
        case "nodata":  // 列表中没有内容
            html = '<div class="list-item text-center" id="list-foot">' + window.parent.i18next.t('music.list.loading.nodata') + '...</div>';
        break;
        case "clear":   // 清空列表
            html = '<div class="list-item text-center list-clickable" id="list-foot" onclick="clearDislist();">' + window.parent.i18next.t('music.list.loading.clear') + '</div>';
        break;
    }
    rem.mainList.append(html);
}

// 刷新当前显示的列表，如果有正在播放则添加样式
function refreshList() {
    // 还没播放过，不用对比了
    if(rem.playlist === undefined) return true;
    if(rem.mp3_id === undefined) return true;
    $(".list-playing").removeClass("list-playing");        // 移除其它的正在播放
    if(rem.paused !== true) {   // 没有暂停
        for(var i=0; i<musicList[rem.dislist].item.length; i++) {
            // 与正在播放的歌曲 id 相同
            if((musicList[rem.dislist].item[i].id !== undefined) && (musicList[rem.dislist].item[i].id === rem.mp3_id)) {
                $(".list-item[data-no='" + i + "']").addClass("list-playing");  // 添加正在播放样式
                rem.playid = i;
                rem.playlist = rem.dislist;
                return true;    // 一般列表中只有一首，找到了赶紧跳出
            }
        }
    }
    
}
// 选择要显示哪个数据区
// 参数：要显示的数据区（list、sheet、player）
function dataBox(choose) {
    $('.btn-box .active').removeClass('active');
    switch(choose) {
        case "list":    // 显示播放列表
            if ($("#player").css('display') === 'none') {
                $("#player").fadeIn();
            }
            $("#main-list").fadeIn();
            $("#history").fadeOut();
            if(rem.dislist === 0 || rem.dislist === rem.playlist) {  // 正在播放
                $(".btn[data-action='playing']").addClass('active');
            }
        break;
    }
}

// 初始化播放列表
function initList() {
    if(file_id) {
        window.parent.$.ajax({
            type: 'GET',
            url: servers + '/music/info/get/' + file_id,
            success: function (data){
                if (data['code'] === 0) {
                    musicList[0].item = [{
                        id: data['data']['id'],
                        name: data['data']['name'],
                        duration: data['data']['duration'],
                        url: servers + '/file/download/' + data['data']['id'],
                        lyric_url: servers + '/music/lyric/get/' + data['data']['id']
                    }];
                    let html = '<div class="sheet-item" data-no="0"><p class="sheet-name">' +musicList[0].name+ '</p></div>';
                    rem.mainList.append(html);
                    $(".btn[data-action='playing']").addClass("btn-select");
                    loadList(0);
                } else {
                    window.parent.$.Toast(data['msg'], 'error');
                    return;
                }
            }
        })
    } else {
        get_history(1);
        $(".btn[data-action='history']").addClass("btn-select");
        $(".btn[data-action='playing']").removeClass("btn-select");
        $(".btn[data-action='usual']").removeClass("btn-select");
    }
}

// 清空当前显示的列表
function clearDislist() {
    musicList[rem.dislist].item.length = 0;  // 清空内容
    loadList(rem.dislist);
}

// 刷新播放列表，为正在播放的项添加正在播放中的标识
function refreshSheet() {
    $(".sheet-playing").removeClass("sheet-playing");        // 移除其它的正在播放
    $(".sheet-item[data-no='" + rem.playlist + "']").addClass("sheet-playing"); // 添加样式
}

function get_history(flag = 1) {
    window.parent.$.ajax({
        type: "GET",
        url: servers + '/music/history/get/' + flag,
        success: function (data) {
            if (data['code'] === 0) {
                musicList[flag].item = [];
                for (let nn = 0; nn < data['data'].length; nn++) {
                    musicList[flag].item.push({
                        id: data['data'][nn]['file_id'],
                        name: data['data'][nn]['name'],
                        duration: data['data'][nn]['duration'],
                        url: servers + '/file/download/' + data['data'][nn]['file_id'],
                        lyric_url: servers + '/music/lyric/get/' + data['data'][nn]['file_id']
                    });
                }
                loadList(flag);
            } else {
                window.parent.$.Toast(data['msg'], 'error');
            }
        }
    })
}

function add_files_s() {
    let root_disk = '';
    window.parent.$.get(servers + '/folder/getDisk').then(res => {
        res.data.forEach(c => {
            root_disk = root_disk + `<ul class="domtree"><li onclick="window.parent.get_folders('move${c['disk']}')"><img src="img/explorer/disk.svg" alt="">${c['disk']}:</li><ul id="move${c['disk']}"></ul></ul>`;
        });
        window.parent.$('#notice>.cnt').html(`
                <p class="tit">${window.parent.i18next.t('music.add.music.window.title')}</p>
                <div><input id="folder_name" type="text" value="" name="520" readonly></div>
                <div><label>${window.parent.i18next.t('explore.window.file.tool.move.window.label')}</label><div id="folder-tree" style="overflow-y: scroll;">${root_disk}</div></div>
        `);
        window.parent.$('#notice>.btns').html(`<a class="a btn main" onclick="document.getElementById('iframe_music').contentWindow.load_files_s();">${window.parent.i18next.t('submit')}</a><a class="a btn detail" onclick="window.parent.closenotice();">${window.parent.i18next.t('cancel')}</a>`);
        window.parent.$('#notice-back').addClass('show');
        window.parent.$('#notice')[0].style.width = '50%';
        window.parent.$('#notice')[0].style.height = window.parent.$('#notice-back')[0].clientHeight * 0.8 + 'px';
        window.parent.$('#folder-tree')[0].style.height = window.parent.$('#notice-back')[0].clientHeight * 0.8 - 207 + 'px';
    });
}

function load_files_s() {
    window.parent.show_modal_cover();
    let folder_id = window.parent.document.getElementById('folder_name').name;
    window.parent.$.ajax({
        type: 'GET',
        url: servers + '/music/get/' + folder_id.slice(4, folder_id.length),
        success: function (data) {
            if (data['code'] === 0) {
                musicList[0].item = [];
                for (let i=0; i<data['data'].length; i++) {
                    musicList[0].item.push({
                        id: data['data'][i]['id'],
                        name: data['data'][i]['name'],
                        duration: data['data'][i]['duration'],
                        url: servers + '/file/download/' + data['data'][i]['id'],
                        lyric_url: servers + '/music/lyric/get/' + data['data'][i]['id']
                    });
                }
                $(".btn[data-action='playing']").addClass("btn-select");
                $(".btn[data-action='history']").removeClass("btn-select");
                $(".btn[data-action='usual']").removeClass("btn-select");
                loadList(0);
            } else {
                window.parent.$.Toast(data['msg'], 'error');
            }
        }
    })
    window.parent.close_modal_cover();
    window.parent.closenotice();
}

function play_local_mp3() {
    let play_local_mp3 = document.getElementById("play_local_mp3");
    play_local_mp3.click();
    play_local_mp3.onchange = function (event) {
        let files = event.target.files;
        if (files.length < 1) {
            return null;
        }
        let music_list_index = [];
        musicList[0].item = [];
        for (let i=0; i<files.length; i++) {
            let file_name = files[i].name;
            let file_name_no = file_name.slice(0, file_name.length-4);
            let music_index = music_list_index.indexOf(file_name_no);
            if (music_index > -1) {
                if (file_name.indexOf('.mp3')>0) {
                    musicList[0].item[music_index].url = URL.createObjectURL(files[i]);
                    musicList[0].item[music_index].name = file_name;
                } else {
                    musicList[0].item[music_index].lyric_url = URL.createObjectURL(files[i]);
                }
            } else {
                if (file_name.indexOf('.mp3') > 0) {
                    musicList[0].item.push({
                        id: window.parent.md5(file_name_no),
                        name: file_name,
                        duration: '',
                        url: URL.createObjectURL(files[i]),
                        lyric_url: ''
                    });
                } else if (file_name.indexOf('.lrc') > 0) {
                    musicList[0].item.push({
                        id: window.parent.md5(file_name_no),
                        duration: '',
                        url: '',
                        lyric_url: URL.createObjectURL(files[i])
                    });
                }
                music_list_index.push(file_name_no);
            }
        }
        $(".btn[data-action='playing']").addClass("btn-select");
        $(".btn[data-action='history']").removeClass("btn-select");
        $(".btn[data-action='usual']").removeClass("btn-select");
        loadList(0);
    }
    play_local_mp3.value = '';
}
