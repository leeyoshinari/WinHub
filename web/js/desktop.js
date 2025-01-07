// Some codes of this file are based on code from [https://github.com/tjy-gitnub/win12], which is licensed under the [EPL-2.0]. See [https://github.com/tjy-gitnub/win12] for details.
const default_icon = 'img/files/none.svg';
let icons = {};
$.ajax({type: 'GET', url: 'icon.json', success: function (data){icons = data;}})
document.querySelectorAll(`list.focs`).forEach(li => {
    li.addEventListener('click', e => {
        let _ = li.querySelector('span.focs'), la = li.querySelector('a.check'),
            las = li.querySelectorAll('a');
        $(_).addClass('cl');
        $(_).css('img/explorer/rb.png', la.offsetTop - las[las.length - 1].offsetTop);
        $(_).css('left', la.offsetLeft - li.offsetLeft);
        setTimeout(() => {
            $(_).removeClass('cl');
        }, 500);
    })
});
// 禁止拖拽图片
$('img').on('dragstart', () => {return false;});
// 右键菜单
$('html').on('contextmenu', () => {return false;});
function stop(e) {e.stopPropagation();return false;}
$('input,textarea,*[contenteditable=true]').on('contextmenu', (e) => {stop(e);return true;});
let nomax = { 'calc': 0 /* 其实，计算器是可以最大化的...*/};
let nomin = {};
let topmost = [];
let startClientX = 0;
let startClientY = 0;
let endClientX = 0;
let endClientY = 0;
let current_window = '';
let cms = {
    'titbar': [
        function (arg) {
            if (arg in nomax) {
                return 'null';
            }
            if ($('.window.' + arg).hasClass("max")) {
                return ['<i class="bi bi-window-stack"></i> '+i18next.t('restore'), `maxwin('${arg}')`];
            }
            else {
                return ['<i class="bi bi-window-fullscreen"></i> '+i18next.t('max.window'), `maxwin('${arg}')`];
            }
        },
        function (arg) {
            if (arg in nomin) {
                return 'null';
            }
            else {
                return ['<i class="bi bi-window-dash"></i> '+i18next.t('min.window'), `minwin('${arg}')`];
            }
        },
        function (arg) {
            if (arg in nomin) {
                return ['<i class="bi bi-window-x"></i> '+i18next.t('close'), `hidewin('${arg}', 'configs')`];
            }
            else {
                return ['<i class="bi bi-window-x"></i> '+i18next.t('close'), `hidewin('${arg}')`];
            }
        },
    ],
    'taskbar': [
        function (arg) {
            return ['<i class="bi bi-window-x"></i> '+i18next.t('close'), `hidewin('${arg}')`];
        }
    ],
    'desktop': [
        arg => { return ['<i class="bi bi-arrow-clockwise"></i> '+i18next.t('refresh'), `window.location.reload();`];}
    ],
    'desktop.icon': [
        function (arg) {
            return ['<i class="bi bi-folder2-open"></i> '+i18next.t('desktop.menu.open'), 'openapp(`' + arg[0] + '`)']
        }
    ],
    'desktop.file': [
        arg => {
            return ['<i class="bi bi-folder2-open"></i> '+i18next.t('desktop.menu.open'), 'apps.explorer.open_file(`' + arg[1] + '`, `' + arg[2] + '`)']
        },
        arg => {
            return ['<i class="bi bi-escape"></i> '+i18next.t('explore.window.file.tool.shortcuts.origin.path'), 'apps.explorer.open_origin_path(`' + arg[1] + '`)']
        },
        arg => {
            return ['<i class="bi bi-trash3"></i> '+i18next.t('explore.window.file.tool.shortcuts.delete'), 'apps.explorer.delete_shortcuts(`' + arg[0] + '`)']
        }
    ],
    'explorer.folder': [
        arg => {
            return ['<i class="bi bi-arrow-up-right-square"></i> '+i18next.t('tab.open'), `apps.explorer.newtab('${arg[0]}', '${arg[1]}');`];
        },
        arg => {
            if ($('#win-explorer>.path>.tit>.path>div.text').length > 1)
                return ['<i class="bi bi-trash3"></i> '+i18next.t('setting.window.shell.server.list.action.delete'), `apps.explorer.del('${arg[1]}')`];
            return 'null';
        },
        arg => {
            if ($('#win-explorer>.path>.tit>.path>div.text').length > 1)
                return ['<i class="bi bi-input-cursor-text"></i> '+i18next.t('explore.window.file.tool.rename.title'), `apps.explorer.rename('${arg[1]}')`];
            return 'null';
        },
        arg => {
            if ($('#win-explorer>.path>.tit>.path>div.text').length > 1)
                return ['<i class="bi bi-arrow-repeat"></i> '+i18next.t('explore.window.file.tool.backup.title'), `apps.explorer.syncing('${arg[1]}', 1)`];
            return 'null';
        },
        arg => {
            if ($('#win-explorer>.path>.tit>.path>div.text').length > 1)
                return ['<i class="bi bi-x-circle-fill"></i> '+i18next.t('explore.window.file.tool.cancel.backup.title'), `apps.explorer.syncing('${arg[1]}', 0)`];
            return 'null';
        }
    ],
    'explorer.file': [
        arg => {
            if ($('#win-explorer>.path>.tit>.path>div.text').length > 1)
                return ['<i class="bi bi-trash3"></i> '+i18next.t('setting.window.shell.server.list.action.delete'), `apps.explorer.del('${arg}')`];
            return 'null';
        },
        arg => {
            if ($('#win-explorer>.path>.tit>.path>div.text').length > 1)
                return ['<i class="bi bi-input-cursor-text"></i> '+i18next.t('explore.window.file.tool.rename.title'), `apps.explorer.rename('${arg}')`];
            return 'null';
        },
        arg => {
            if ($('#win-explorer>.path>.tit>.path>div.text').length > 1)
                return ['<i class="bi bi-house-door-fill"></i> '+i18next.t('explore.window.file.tool.shortcuts.add'), `apps.explorer.add_shortcuts('${arg}')`];
            return 'null';
        }
    ],
    'explorer.content': [
        arg => {
            if ($('#win-explorer>.path>.tit>.path>div.text').length > 1)
                return ['<i class="bi bi-file-earmark-plus"></i> '+i18next.t('explore.window.file.tool.file.title'), `apps.explorer.add($('#win-explorer>.path>.tit')[0].id,type='file')`];
            return 'null';
        },
        arg => {
            if ($('#win-explorer>.path>.tit>.path>div.text').length > 1)
                return ['<i class="bi bi-folder-plus"></i> '+i18next.t('explore.window.file.tool.folder.title'), `apps.explorer.add($('#win-explorer>.path>.tit')[0].id,type='folder')`];
            return 'null';
        },
        arg => {
            if ($('#win-explorer>.path>.tit>.path>div.text').length > 1)
                return ['<i class="bi bi-arrow-clockwise"></i> '+i18next.t('refresh'), `apps.explorer.goto($('#win-explorer>.path>.tit')[0].dataset.path, $('#win-explorer>.path>.tit')[0].id)`];
            return ['<i class="bi bi-arrow-clockwise"></i> '+i18next.t('refresh'), `apps.explorer.reset()`];
        }
    ],
    'explorer.tab': [
        arg => {
            return ['<i class="bi bi-x"></i> '+i18next.t('tab.close'), `m_tab.close('explorer',${arg})`];
        }
    ],
    'search.folder': [
        arg => {
            return ['<i class="bi bi-arrow-up-right-square"></i> '+i18next.t('tab.open'), `apps.explorer.newtab('${arg[0]}', '${arg[1]}');`];
        }
    ],
    'search.file': [
        arg => {
            return ['<i class="bi bi-escape"></i> '+i18next.t('explore.window.file.tool.shortcuts.origin.path'), 'apps.explorer.open_search_origin_path(`' + arg + '`)']
        }
    ],
    'edge.tab': [
        arg => {
            return ['<i class="bi bi-pencil-square"></i> '+i18next.t('tab.rename'), `apps.edge.c_rename(${arg})`];
        },
        arg => {
            return ['<i class="bi bi-x"></i> '+i18next.t('tab.close'), `m_tab.close('edge',${arg})`];
        }
    ],
}
window.onkeydown = function (event) {
    if (event.keyCode === 116/*F5被按下(刷新)*/) {
        event.preventDefault();/*取消默认刷新行为*/
    }
}

function showcm(e, cl, arg, file_type='null') {
    if ($('#cm').hasClass('show-begin')) {
        setTimeout(() => {
            $('#cm').css('left', e.clientX);
            $('#cm').css('top', e.clientY);
            let h = '';
            cms[cl].forEach(item => {
                if (typeof (item) == 'function') {
                    arg.event = e;
                    ret = item(arg);
                    if (ret === 'null') return true;
                    h += `<a class="a" onmousedown="${ret[1]}">${ret[0]}</a>\n`;
                }
                else if (typeof (item) == 'string') {
                    h += item + '\n';
                }
                else {
                    h += `<a class="a" onmousedown="${item[1]}">${item[0]}</a>\n`;
                }
            })
            if ("docx,xlsx,pptx,csv".indexOf(file_type) > -1){
                h += `<a class="a" onmousedown="apps.explorer.coediting('${arg}')"><i class="bi bi-arrow-up-right-square"></i>${i18next.t('explore.window.file.tool.co-editing')}</a>`;
            }
            $('#cm>list')[0].innerHTML = h;
            $('#cm').addClass('show-begin');
            $('#cm>.foc').focus();
            // 这个.foc是用来模拟焦点的，这句是将焦点放在右键菜单上，注释掉后果不堪设想
            // 噢 可是如果设置焦点的话在移动设备上会显示虚拟键盘啊
            setTimeout(() => {
                $('#cm').addClass('show');
            }, 0);
            setTimeout(() => {
                if (e.clientY + $('#cm')[0].offsetHeight > $('html')[0].offsetHeight) {
                    $('#cm').css('top', e.clientY - $('#cm')[0].offsetHeight);
                }
                if (e.clientX + $('#cm')[0].offsetWidth > $('html')[0].offsetWidth) {
                    $('#cm').css('left', $('html')[0].offsetWidth - $('#cm')[0].offsetWidth - 5);
                }
            }, 200);
        }, 200);
        return;
    }
    $('#cm').css('left', e.clientX);
    $('#cm').css('top', e.clientY);
    let h = '';
    cms[cl].forEach(item => {
        if (typeof (item) == 'function') {
            ret = item(arg);
            if (ret === 'null') {
                return true;
            }
            h += `<a class="a" onmousedown="${ret[1]}">${ret[0]}</a>\n`;
        } else if (typeof (item) == 'string') {
            h += item + '\n';
        } else {
            h += `<a class="a" onmousedown="${item[1]}">${item[0]}</a>\n`;
        }
    })
    $('#cm>list')[0].innerHTML = h;
    $('#cm').addClass('show-begin');
    $('#cm>.foc').focus();
    setTimeout(() => {
        $('#cm').addClass('show');
    }, 0);
    setTimeout(() => {
        if (e.clientY + $('#cm')[0].offsetHeight > $('html')[0].offsetHeight) {
            $('#cm').css('top', e.clientY - $('#cm')[0].offsetHeight);
        }
        if (e.clientX + $('#cm')[0].offsetWidth > $('html')[0].offsetWidth) {
            $('#cm').css('left', $('html')[0].offsetWidth - $('#cm')[0].offsetWidth - 5);
        }
    }, 200);
}
$('#cm>.foc').blur(() => {
    let x = event.target.parentNode;
    $(x).removeClass('show');
    setTimeout(() => {
        $(x).removeClass('show-begin');
    }, 200);
});

let dps = {}
let dpt = null, isOnDp = false;
$('#dp')[0].onmouseover = () => { isOnDp = true };
$('#dp')[0].onmouseleave = () => { isOnDp = false; hidedp() };
function showdp(e, cl, arg) {
    if ($('#dp').hasClass('show-begin')) {
        $('#dp').removeClass('show');
        setTimeout(() => {
            $('#dp').removeClass('show-begin');
        }, 200);
        if (e !== dpt) {
            setTimeout(() => {
                showdp(e, cl, arg);
            }, 400);
        }
        return;
    }
    // dpt = e;
    let off = $(e).offset();
    $('#dp').css('left', off.left);
    $('#dp').css('top', off.top + e.offsetHeight);
    let h = '';
    dps[cl].forEach(item => {
        if (typeof (item) == 'function') {
            ret = item(arg);
            if (ret === 'null') {
                return true;
            }
            h += `<a class="a" onclick="${ret[1]}">${ret[0]}</a>\n`;
        } else if (typeof (item) == 'string') {
            h += item + '\n';
        } else {
            h += `<a class="a" onclick="${item[1]}">${item[0]}</a>\n`;
        }
    })
    $('#dp>list')[0].innerHTML = h;
    $('#dp').addClass('show-begin');
    setTimeout(() => {
        $('#dp').addClass('show');
    }, 0);
    setTimeout(() => {
        if (off.top + e.offsetHeight + $('#dp')[0].offsetHeight > $('html')[0].offsetHeight) {
            $('#dp').css('top', off.top - $('#dp')[0].offsetHeight);
        }
        if (off.left + $('#dp')[0].offsetWidth > $('html')[0].offsetWidth) {
            $('#dp').css('left', $('html')[0].offsetWidth - $('#dp')[0].offsetWidth - 5);
        }
    }, 200);
}
function hidedp(force = false) {
    setTimeout(() => {
        if (isOnDp && !force) {
            return;
        }
        $('#dp').removeClass('show');
        setTimeout(() => {
            $('#dp').removeClass('show-begin');
        }, 200);
    }, 100);
}

function showdescp(e) {
    $(e.target).attr('data-descp', 'waiting');
    setTimeout(() => {
        if ($(e.target).attr('data-descp') === 'hide') {
            return;
        }
        $(e.target).attr('data-descp', 'show');
        $('#descp').css('left', e.clientX + 1);
        $('#descp').css('top', e.clientY + 2);
        $('#descp').text($(e.target).attr('win12_title'));
        $('#descp').addClass('show-begin');
        setTimeout(() => {
            if (e.clientY + $('#descp')[0].offsetHeight + 20 >= $('html')[0].offsetHeight) {
                $('#descp').css('top', e.clientY - $('#descp')[0].offsetHeight - 10);
            }
            if (e.clientX + $('#descp')[0].offsetWidth + 15 >= $('html')[0].offsetWidth) {
                $('#descp').css('left', e.clientX - $('#descp')[0].offsetWidth - 10);
            }
            $('#descp').addClass('show');
        }, 100);
    }, 500);
}
function hidedescp(e) {
    $('#descp').removeClass('show');
    $(e.target).attr('data-descp', 'hide');
    setTimeout(() => {
        $('#descp').removeClass('show-begin');
    }, 100);
}

// 提示
let nts = {
    'ZeroDivision': {//计算器报错窗口
        cnt: `<p class="tit">错误</p><p>除数不得等于0</p>`,
        btn: [{ type: 'main', text: 'submit', js: 'closenotice();' }]
    },
    'share': {
        cnt: `<p class="tit"></p><input type="text" id="share-time" placeholder="" style="width: 95%;">`,
        btn: [{ type: 'main', text: 'submit', js: 'apps.explorer.share();' },
            { type: 'detail', text: 'cancel', js: 'closenotice();' }]
    },
    'downloader': {
        cnt: `<p class="tit"></p><input type="text" id="downloader-url" placeholder="" style="width: 95%;">
            <p class="tit"></p><input type="text" id="downloader-cookie" placeholder="" style="width: 95%;">`,
        btn: [{ type: 'main', text: 'submit', js: 'apps.explorer.download_online();' },
            { type: 'detail', text: 'cancel', js: 'closenotice();' }]
    },
    'selectedFiles': {
        cnt: `<p class="tit"></p><div id="selected-file"></div>`,
        btn: [{ type: 'main', text: 'submit', js: 'apps.explorer.download_selected();' },
            { type: 'detail', text: 'cancel', js: 'closenotice();' }]
    },
    'uploadResult': {
        cnt: `<p class="tit"></p><list class="upload-result"></list>`,
        btn: [{ type: 'main', text: 'submit', js: 'closenotice();' }]}
}
function shownotice(name) {
    $('#notice>.cnt').html(nts[name].cnt);
    let tmp = '';
    nts[name].btn.forEach(btn => {
        tmp += `<a class="a btn ${btn.type}" onclick="${btn.js}">${i18next.t(btn.text)}</a>`
    });
    $('#notice>.btns').html(tmp);
    if (name === 'share') {
        $('#notice')[0].style.top = '30%';
        $('#notice>.cnt>p')[0].style.width = '500px';
        $('#notice>.cnt>p')[0].innerText = i18next.t('explore.window.file.tool.share.window.title');
        $('#notice>.cnt>input')[0].placeholder = i18next.t('explore.window.file.tool.share.window.placeholder');
    }
    if (name === 'uploadResult') {
        $('#notice>.cnt>p')[0].innerText = i18next.t('terminal.page.upload.result.tips');
    }
    if (name === 'downloader') {
        $('#notice')[0].style.top = '30%';
        $('#notice>.cnt>p')[0].innerText = i18next.t('explore.window.file.tool.downloader.window.title1');
        $('#notice>.cnt>input')[0].placeholder = i18next.t('explore.window.file.tool.downloader.window.placeholder1');
        $('#notice>.cnt>p')[1].innerText = i18next.t('explore.window.file.tool.downloader.window.title2');
        $('#notice>.cnt>input')[1].placeholder = i18next.t('explore.window.file.tool.downloader.window.placeholder2');
    }
    setTimeout(() => {
        $('#notice-back').addClass('show');
    }, 20);
}
function closenotice() {
    $('#notice')[0].style.top = '';
    $('#notice')[0].style.width = '';
    $('#notice')[0].style.height = '';
    $('#notice>.cnt').html('');
    $('#notice>.btns').html('');
    $('#notice-back').removeClass('show');
    $('#notice>.btns')[0].style.display = '';
}
// 应用
let apps = {
    setting: {
        init: () => {
            if ($('.window.setting>link').length < 1) {
                let css_link = document.createElement('link');
                css_link.setAttribute('rel', 'stylesheet');
                css_link.setAttribute('href', 'css/setting.css');
                $('.window.setting')[0].appendChild(css_link);
            }
            $('#win-setting>.menu>list>a.system')[0].click();
        },
        page: (name) => {
            $('#win-setting>.page>.cnt.' + name).scrollTop(0);
            $('#win-setting>.page>.cnt.show').removeClass('show');
            $('#win-setting>.page>.cnt.' + name).addClass('show');
            $('#win-setting>.menu>list>a.check').removeClass('check');
            $('#win-setting>.menu>list>a.' + name).addClass('check');
            if (name === 'user') {
                $('#win-setting>.page>.cnt.user>div>a>img')[0].src = 'img/pictures/' + document.cookie.split('u=')[1].split(';')[0] +'/avatar.jpg';
                $('#win-setting>.page>.cnt.user>div>a>div>p')[0].innerText = nickName;
                $('#win-setting>.page>.cnt.user>div>a>div>p')[1].innerText = document.cookie.split('u=')[1].split(';')[0];
            }
        },
    },
    whiteboard: {
        canvas: null,
        ctx: null,
        windowResizeObserver: null,
        color: 'red',
        init: () => {
            if ($('.window.whiteboard>link').length < 1) {
                let css_link = document.createElement('link');
                css_link.setAttribute('rel', 'stylesheet');
                css_link.setAttribute('href', 'css/whiteboard.css');
                $('.window.whiteboard')[0].appendChild(css_link);
            }
            apps.whiteboard.ctx.lineJoin = 'round';
            apps.whiteboard.ctx.lineCap = 'round';
            apps.whiteboard.changeColor(apps.whiteboard.color);
            if ($(':root').hasClass('dark')) {
                $('.window.whiteboard>.titbar>span>.title').text('Blackboard');
            } else {
                $('.window.whiteboard>.titbar>span>.title').text('Whiteboard');
            }
        },
        changeColor: (color) => {
            apps.whiteboard.color = color;
            if (color === 'eraser') {
                apps.whiteboard.ctx.strokeStyle = 'black';
                apps.whiteboard.ctx.lineWidth = 35;
                apps.whiteboard.ctx.globalCompositeOperation = 'destination-out';
            }
            else {
                apps.whiteboard.ctx.strokeStyle = color;
                apps.whiteboard.ctx.globalCompositeOperation = 'source-over';
                apps.whiteboard.ctx.lineWidth = 8;
            }
        },
        changePen: function () {
            const pens = $('#win-whiteboard>.toolbar>.tools>*');
            for (const elt of pens) {
                elt.classList.remove('active');
            }
            this.classList.add('active');
            apps.whiteboard.changeColor(this.dataset.color);
        },
        load: () => {
            apps.whiteboard.canvas = $('#win-whiteboard>canvas')[0];
            apps.whiteboard.ctx = apps.whiteboard.canvas.getContext('2d');
            apps.whiteboard.windowResizeObserver = new ResizeObserver(apps.whiteboard.resize);
            apps.whiteboard.windowResizeObserver.observe($('.window.whiteboard')[0], { box: 'border-box' });
        },
        resize: () => {
            try {
                const imgData = apps.whiteboard.ctx.getImageData(0, 0, apps.whiteboard.canvas.width, apps.whiteboard.canvas.height);
                apps.whiteboard.canvas.width = $('#win-whiteboard')[0].clientWidth;
                apps.whiteboard.canvas.height = $('#win-whiteboard')[0].clientHeight;
                apps.whiteboard.ctx.putImageData(imgData, 0, 0);
            }
            catch {
                apps.whiteboard.canvas.width = $('#win-whiteboard')[0].clientWidth;
                apps.whiteboard.canvas.height = $('#win-whiteboard')[0].clientHeight;
            }
            apps.whiteboard.init();
        },
        draw: (e) => {
            let offsetX, offsetY, left = $('#win-whiteboard')[0].getBoundingClientRect().left, top = $('#win-whiteboard')[0].getBoundingClientRect().top;
            if (e.type.match('mouse')) {
                offsetX = e.clientX - left, offsetY = e.clientY - top;
            }
            else if (e.type.match('touch')) {
                offsetX = e.touches[0].clientX - left, offsetY = e.touches[0].clientY - top;
            }
            apps.whiteboard.ctx.beginPath();
            apps.whiteboard.ctx.moveTo(offsetX, offsetY);
            page.onmousemove = apps.whiteboard.drawing;
            page.ontouchmove = apps.whiteboard.drawing;
            page.onmouseup = apps.whiteboard.up;
            page.ontouchend = apps.whiteboard.up;
            page.ontouchcancel = apps.whiteboard.up;
        },
        drawing: (e) => {
            let offsetX, offsetY, left = $('#win-whiteboard')[0].getBoundingClientRect().left, top = $('#win-whiteboard')[0].getBoundingClientRect().top;
            if (e.type.match('mouse')) {
                offsetX = e.clientX - left, offsetY = e.clientY - top;
            }
            else if (e.type.match('touch')) {
                offsetX = e.touches[0].clientX - left, offsetY = e.touches[0].clientY - top;
            }
            apps.whiteboard.ctx.lineTo(offsetX, offsetY);
            apps.whiteboard.ctx.stroke();
        },
        up: () => {
            apps.whiteboard.ctx.stroke();
            page.onmousemove = null;
            page.ontouchmove = null;
            page.onmouseup = null;
            page.ontouchend = null;
            page.ontouchcancel = null;
        },
        download: () => {
            const url = apps.whiteboard.canvas.toDataURL();
            $('#win-whiteboard>a.download')[0].href = url;
            $('#win-whiteboard>a.download')[0].click();
        },
        delete: () => {
            apps.whiteboard.ctx.clearRect(0, 0, apps.whiteboard.canvas.width, apps.whiteboard.canvas.height);
        }
    },
    explorer: {
        init: () => {
            apps.explorer.tabs = [];
            apps.explorer.len = 0;
            apps.explorer.newtab();
            // apps.explorer.reset();
            apps.explorer.is_use = 0;//千万不要删除它，它依托bug运行
            apps.explorer.is_use2 = 0;//千万不要删除它，它依托bug运行
            apps.explorer.clipboard = null;
            document.addEventListener('keydown', function (event) {
                if (event.key === 'Delete' && $('.window.foc')[0].classList[1] === "explorer") {
                    apps.explorer.del();
                }
            });
        },
        tabs: [],
        now: null,
        len: 0,
        newtab: (path = '', path_id = '') => {
            m_tab.newtab('explorer', '');
            apps.explorer.tabs[apps.explorer.tabs.length - 1][2] = path;
            apps.explorer.tabs[apps.explorer.tabs.length - 1][3] = path_id;
            apps.explorer.initHistory(apps.explorer.tabs[apps.explorer.tabs.length - 1][0]);
            apps.explorer.checkHistory(apps.explorer.tabs[apps.explorer.tabs.length - 1][0]);
            m_tab.tab('explorer', apps.explorer.tabs.length - 1);
        },
        settab: (t, i) => {
            return `<div class="tab ${t[0]}" onclick="m_tab.tab('explorer',${i})" oncontextmenu="showcm(event,'explorer.tab',${i});stop(event);return false" onmousedown="m_tab.moving('explorer',this,event,${i});stop(event);" ontouchstart="m_tab.moving('exploer',this,event,${i});stop(event);"><p>${t[1]}</p><span class="clbtn bi bi-x" onclick="m_tab.close('explorer',${i});stop(event);"></span></div>`;
        },
        tab: (c, load = true) => {
            if (load) {
                if (!apps.explorer.tabs[c][2].length) apps.explorer.reset();
                else apps.explorer.goto(apps.explorer.tabs[c][2], apps.explorer.tabs[c][3]);
            }
            apps.explorer.checkHistory(apps.explorer.tabs[c][0]);
        },
        reset: (clear = true) => {
            $('#win-explorer>.page>.main>.content>.view').removeClass("icon-view");
            $('#win-explorer>.page>.main>.content>.view')[0].innerHTML = `<p class="class"><img src="img/explorer/disk.svg" alt="disk.svg" loading="lazy"> ${i18next.t('explore.window.file.disk.title')} </p><div class="group"></div>`;
            $('#win-explorer>.page>.menu>.card>list>a')[0].className ='check';
            $('#win-explorer>.page>.menu>.card>list>a')[0].querySelector('span').style.display='flex';
            $('#win-explorer>.page>.menu>.card>list>a')[1].className = '';
            $('#win-explorer>.page>.menu>.card>list>a')[1].querySelector('span').style.display='none';
            $('#win-explorer>.page>.menu>.card>list>a')[2].className = '';
            $('#win-explorer>.page>.menu>.card>list>a')[2].querySelector('span').style.display='none';
            $('#win-explorer>.page>.menu>.card>list>a')[3].className = '';
            $('#win-explorer>.page>.menu>.card>list>a')[3].querySelector('span').style.display='none';
            $('#win-explorer>.page>.main')[0].style.display = 'flex';
            $('#win-explorer>.page>.main-share')[0].style.display = 'none';
            $('#win-explorer>.page>.main-download')[0].style.display = 'none';
            $('#win-explorer>.page>.main>.content>.header')[0].style.display = 'none';
            $('#win-explorer>.path>.search')[0].style.display = 'none';
            $('#win-explorer>.path>.search>input')[0].value = '';
            $('#win-explorer>.path>.back')[0].classList.remove('disabled');
            $('#win-explorer>.path>.goback')[0].classList.remove('disabled');
            $('#win-explorer>.path>.back').attr('onclick', 'apps.explorer.reset()');
            $('#win-explorer>.path>.goback').attr('onclick', 'apps.explorer.reset()');
            $('#win-explorer>.path>.tit')[0].id = '';
            $('#win-explorer>.path>.tit')[0].innerHTML = '<div class="icon" style="background-image: url(\'img/explorer/thispc.svg\')"></div><div class="path"><div class="text" onclick="apps.explorer.reset()">' + i18next.t('computer') +'</div><div class="arrow">&gt;</div></div>';
            m_tab.rename('explorer', '<img src="img/explorer/thispc.svg" alt="thispc.svg" loading="lazy"> ' + i18next.t('computer'));
            apps.explorer.tabs[apps.explorer.now][2] = '';
            apps.explorer.tabs[apps.explorer.now][3] = '';
            document.getElementById("all_files").checked = false;
            document.querySelector('#win-explorer>.page>.main>.tool').style.display = 'none'
            if (clear) {
                apps.explorer.delHistory(apps.explorer.tabs[apps.explorer.now][0]);
                apps.explorer.pushHistory(apps.explorer.tabs[apps.explorer.now][0], i18next.t('computer'));
            }
            let disk_group = '<a class="a item act" ondblclick="" oncontextmenu=""><img src="img/explorer/diskwin.svg" alt="diskwin.svg" loading="lazy"><div><p class="name">' + i18next.t('explore.window.file.disk.name') + ' (C:)</p><div class="bar"><div class="content" style="width: 1%;"></div></div><p class="info">520 MB' + i18next.t('explore.window.file.disk.size') + '521 MB</p></div></a>';
            $.get(server + '/folder/getDisk').then(res => {
                res.data.forEach(c => {
                    disk_group = disk_group + '<a class="a item act" ondblclick="apps.explorer.goto(\'' + c['disk'] + ':\'' + ',\'' + c['disk'] + '\')" ontouchend="apps.explorer.goto(\'' + c['disk'] + ':\'' + ',\'' + c['disk'] + '\')"><img src="img/explorer/disk.svg" alt="disk.svg" loading="lazy"><div><p class="name">' + i18next.t('explore.window.file.disk.name') + ' (' + c['disk'] + ':)</p><div class="bar"><div class="content" style="width: ' + c['used'] + '%;"></div></div><p class="info">' + c['free'] + i18next.t('explore.window.file.disk.size') + c['total'] + '</p></div></a>';
                });
                document.getElementsByClassName('group')[0].innerHTML = disk_group;
                if (localStorage.getItem('transparent') === '1') {
                    $('#win-explorer>.page>.main>.content>.view>.group>.item').addClass('transparent');
                } else {
                    $('#win-explorer>.page>.main>.content>.view>.group>.item').removeClass('transparent');
                }
                if (res.data[0]['enableOnlyoffice'] === '0') {
                    $('#win-explorer>.page>.main>.tool>.dropdown-container>.dropdown-list>li')[4].style.display = 'none';
                    $('#win-explorer>.page>.main>.tool>.dropdown-container>.dropdown-list>li')[5].style.display = 'none';
                    $('#win-explorer>.page>.main>.tool>.dropdown-container>.dropdown-list>li')[6].style.display = 'none';
                }
            });
        },
        garbage: () => {
            $('#win-explorer>.page>.main')[0].style.display = 'flex';
            $('#win-explorer>.page>.main-share')[0].style.display = 'none';
            $('#win-explorer>.page>.main-download')[0].style.display = 'none';
            $('#win-explorer>.page>.menu>.card>list>a')[0].className ='';
            $('#win-explorer>.page>.menu>.card>list>a')[0].querySelector('span').style.display='none';
            $('#win-explorer>.page>.menu>.card>list>a')[1].className = 'check';
            $('#win-explorer>.page>.menu>.card>list>a')[1].querySelector('span').style.display='flex';
            $('#win-explorer>.page>.menu>.card>list>a')[2].className ='';
            $('#win-explorer>.page>.menu>.card>list>a')[2].querySelector('span').style.display='none';
            $('#win-explorer>.page>.menu>.card>list>a')[3].className ='';
            $('#win-explorer>.page>.menu>.card>list>a')[3].querySelector('span').style.display='none';
            $('#win-explorer>.path>.search')[0].style.display = 'none';
            $('#win-explorer>.path>.search>input')[0].value = '';
            $('#win-explorer>.path>.back')[0].classList.add('disabled');
            $('#win-explorer>.path>.goback')[0].classList.add('disabled');
            m_tab.rename('explorer', '<img src="img/explorer/rb.png" alt="rb.png" loading="lazy"> '+i18next.t('explore.window.menu.garbage.title'));
            document.getElementById("all_files").checked = false;
            let sort_field = 'update_time';
            let sort_type = 'desc';
            document.querySelectorAll('#win-explorer>.page>.main>.content>.header>.row>span>button').forEach(item => {
                if (item.className) {
                    sort_field = item.id.split('-')[0];
                    sort_type = item.className;
                }
            })
            document.querySelector('#win-explorer>.page>.main>.tool').style.display = 'flex';
            document.querySelectorAll('#win-explorer>.page>.main>.tool>.asd').forEach(item => {
                item.style.display='none';
            })
            document.querySelectorAll('#win-explorer>.page>.main>.tool>.dsa').forEach(item => {
                item.style.display='flex';
            })
            let tmp = queryAllFiles("garbage", "", sort_field, sort_type);
            if (tmp.length === 0) {
                $('#win-explorer>.page>.main>.content>.header')[0].style.display = 'none';
                $('#win-explorer>.page>.main>.content>.view')[0].innerHTML = '<p class="info">'+i18next.t('explore.window.file.list.empty.tips')+'</p>';
            } else {
                let ht = '';
                $('#win-explorer>.page>.main>.content>.header')[0].style.display = 'flex';
                $('#win-explorer>.page>.main>.content>.view').removeClass("icon-view");
                for(let i=0; i<tmp.length; i++) {
                    if(tmp[i]['folder_type'] === 'folder') {
                        ht += `<div class="row" style="padding-left: 5px;"><input type="checkbox" id="check${tmp[i]['id']}" style="float: left; margin-top: 8px;margin-right: 8px;"><a class="a item files" id="f${tmp[i]['id']}" onclick="apps.explorer.select('${tmp[i]['id']}');" ondblclick="apps.explorer.goto('${tmp[i]['name']}', '${tmp[i]['id']}')">
                            <span style="width: 40%;"><img style="float: left;" src="img/explorer/folder.svg" alt="folder.svg" loading="lazy">${tmp[i]['name']}</span><span style="width: 10%;">${i18next.t('explore.window.file.list.folder.type.name')}</span>
                            <span style="width: 10%;"></span><span style="width: 20%;">${tmp[i]['update_time']}</span><span style="width: 20%;">${tmp[i]['create_time']}</span></a></div>`;
                    } else {
                        let f_src = icons[tmp[i]['format']] || default_icon;
                        ht += `<div class="row" style="padding-left: 5px;"><input type="checkbox" id="check${tmp[i]['id']}" style="float: left; margin-top: 8px;margin-right: 8px;"><a class="a item act file" id="f${tmp[i]['id']}" onclick="apps.explorer.select('${tmp[i]['id']}');" ondblclick="apps.explorer.open_file('${tmp[i]['id']}', '${tmp[i]['name']}')">
                            <span style="width: 40%;"><img style="float: left;" src="${f_src}" alt="file" loading="lazy">${tmp[i]['name']}</span><span style="width: 10%;">${tmp[i]['format']}</span>
                            <span style="width: 10%;">${tmp[i]['size']}</span><span style="width: 20%;">${tmp[i]['update_time']}</span><span style="width: 20%;">${tmp[i]['create_time']}</span></a></div>`;
                    }
                }
                $('#win-explorer>.page>.main>.content>.view')[0].innerHTML = ht;
                document.querySelectorAll('.a.item').forEach(item => {
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
                            item.ondblclick(e);
                        }
                    }, false);
                })
            }
        },
        share_list: () => {
            $('#win-explorer>.page>.menu>.card>list>a')[3].className ='check';
            $('#win-explorer>.page>.menu>.card>list>a')[3].querySelector('span').style.display='flex';
            $('#win-explorer>.page>.menu>.card>list>a')[2].className = '';
            $('#win-explorer>.page>.menu>.card>list>a')[2].querySelector('span').style.display='none';
            $('#win-explorer>.page>.menu>.card>list>a')[1].className = '';
            $('#win-explorer>.page>.menu>.card>list>a')[1].querySelector('span').style.display='none';
            $('#win-explorer>.page>.menu>.card>list>a')[0].className = '';
            $('#win-explorer>.page>.menu>.card>list>a')[0].querySelector('span').style.display='none';
            $('#win-explorer>.path>.search')[0].style.display = 'none';
            $('#win-explorer>.path>.search>input')[0].value = '';
            $('#win-explorer>.page>.main')[0].style.display = 'none';
            $('#win-explorer>.page>.main-download')[0].style.display = 'none';
            $('#win-explorer>.page>.main-share')[0].style.display = 'flex';
            $('#win-explorer>.path>.back')[0].classList.add('disabled');
            $('#win-explorer>.path>.goback')[0].classList.add('disabled');
            m_tab.rename('explorer', '<img src="img/explorer/share.svg" alt="share.svg" loading="lazy"> '+i18next.t('explore.window.menu.share.title'));
            $.ajax({
                type: 'GET',
                url: server + '/share/list',
                success: function (data) {
                    if (data['code'] === 0) {
                        if (data['data'].length === 0) {
                            $('#win-explorer>.page>.main-share>.content>.header')[0].style.display = 'none';
                            $('#win-explorer>.page>.main-share>.content>.view')[0].innerHTML = '<p class="info">'+i18next.t('explore.window.file.list.empty.tips')+'</p>';
                        } else {
                            $('#win-explorer>.page>.main-share>.content>.header')[0].style.display = 'flex';
                            let ht = '';
                            data['data'].forEach(item => {
                                let f_src = icons[item['format']] || default_icon;
                                ht += `<div class="row" style="padding-left: 5px;"><div class="a item act file" style="cursor: auto;">
                            <span style="width: 38%;" onclick="apps.explorer.open_share('${item['id']}','${item['format']}');"><img style="float: left;" src="${f_src}" alt="file" loading="lazy">${item['name']}</span>
                            <span style="width: 12%;">${item['times']}</span><span style="width: 10%;">${item['total_times']}</span><span style="width: 20%;">${item['create_time']}</span>
                            <span style="width: 20%;"><a style="cursor: pointer; color: blue;" onclick="delete_file([${item['id']}], 'folder', 0, 3);">${i18next.t('setting.window.shell.server.list.action.delete')}</a><a style="margin-left: 10px; cursor: pointer; color: blue;" onclick="apps.explorer.open_share('${item['id']}','${item['format']}',false);">${i18next.t('explore.window.file.share.list.view.link')}</a></span></div></div>`;
                            })
                            $('#win-explorer>.page>.main-share>.content>.view')[0].innerHTML = ht;
                        }
                    } else {
                        $.Toast(data['msg'], 'error');
                    }
                }
            })
        },
        open_share: (share_id, share_format, is_open=true) => {
            let share_url = '';
            switch (share_format) {
                case 'md':
                    share_url = '/' + window.location.href.split('/')[3] + '/module/md.html?server=' + server + '&id=' + share_id;
                    break;
                case 'xmind':
                    share_url = '/' + window.location.href.split('/')[3] + '/module/xmind.html?server=' + server + '&id=' + share_id;
                    break;
                case 'sheet':
                    share_url = '/' + window.location.href.split('/')[3] + '/module/sheet.html?server=' + server + '&id=' + share_id + '&lang=' + lang;
                    break;
                case 'docu':
                    share_url = '/' + window.location.href.split('/')[3] + '/module/document.html?server=' + server + '&id=' + share_id + '&lang=' + lang;
                    break;
                case 'py':
                    share_url = '/' + window.location.href.split('/')[3] + '/module/python.html?server=' + server + '&id=' + share_id;
                    break;
                default:
                    share_url = server + '/share/get/' + share_id;
                    break;
            }
            if (is_open) {
                window.open(share_url);
            } else {
                let url_t = window.location.href.split('/')[0] + '//' + window.location.href.split('/')[2] + share_url;
                let textarea = document.createElement('textarea');
                textarea.value = url_t;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                alert(url_t);
            }
        },
        download_list: () => {
            $('#win-explorer>.page>.menu>.card>list>a')[2].className ='check';
            $('#win-explorer>.page>.menu>.card>list>a')[2].querySelector('span').style.display='flex';
            $('#win-explorer>.page>.menu>.card>list>a')[3].className = '';
            $('#win-explorer>.page>.menu>.card>list>a')[3].querySelector('span').style.display='none';
            $('#win-explorer>.page>.menu>.card>list>a')[1].className = '';
            $('#win-explorer>.page>.menu>.card>list>a')[1].querySelector('span').style.display='none';
            $('#win-explorer>.page>.menu>.card>list>a')[0].className = '';
            $('#win-explorer>.page>.menu>.card>list>a')[0].querySelector('span').style.display='none';
            $('#win-explorer>.path>.search')[0].style.display = 'none';
            $('#win-explorer>.path>.search>input')[0].value = '';
            $('#win-explorer>.page>.main')[0].style.display = 'none';
            $('#win-explorer>.page>.main-share')[0].style.display = 'none';
            $('#win-explorer>.page>.main-download')[0].style.display = 'flex';
            $('#win-explorer>.path>.back')[0].classList.add('disabled');
            $('#win-explorer>.path>.goback')[0].classList.add('disabled');
            m_tab.rename('explorer', '<img src="img/explorer/download.svg" alt="share.svg" loading="lazy"> '+i18next.t('explore.window.menu.download.title'));
            $.ajax({
                type: 'GET',
                url: server + '/download/list',
                success: function (data) {
                    if (data['code'] === 0) {
                        if (data['data'].length === 0) {
                            $('#win-explorer>.page>.main-download>.content>.header')[0].style.display = 'none';
                            $('#win-explorer>.page>.main-download>.content>.view')[0].innerHTML = '<p class="info">'+i18next.t('explore.window.file.list.empty.tips')+'</p>';
                        } else {
                            $('#win-explorer>.page>.main-download>.content>.header')[0].style.display = 'flex';
                            let ht = '';
                            data['data'].forEach(item => {
                                ht += `<div class="row" style="padding-left: 5px;"><div class="a item act file" style="cursor: auto;">
                            <span style="width: 33%;" onclick="">${item['name']}</span><span style="width: 10%;">${item['total_size']}</span>
                            <span style="width: 10%;">${item['progress']}%</span><span style="width: 10%;">${item['status']}</span><span style="width: 10%;">${item['download_speed']}</span>
                            <span style="width: 10%;">${item['eta']}</span>`;
                                if (item['status'] === 'active') {
                                    ht += `<span style="width: 15%;"><a style="cursor: pointer; color: blue;" onclick="update_download_status('${item['gid']}', 'pause');">${i18next.t('explore.window.file.download.list.action.pause')}</a>`;
                                    // ht += `<a style="cursor: pointer; color: blue; margin-left: 10px;" onclick="update_download_status('${item['gid']}', 'cancel');">${i18next.t('explore.window.file.download.list.action.cancel')}</a>`;
                                } else if (item['status'] === 'paused') {
                                    ht += `<span style="width: 15%;"><a style="cursor: pointer; color: blue;" onclick="update_download_status('${item['gid']}', 'continue');">${i18next.t('explore.window.file.download.list.action.unpause')}</a>`;
                                    ht += `<a style="cursor: pointer; color: blue; margin-left: 10px;" onclick="update_download_status('${item['gid']}', 'cancel');">${i18next.t('explore.window.file.download.list.action.cancel')}</a>`;
                                } else {
                                    ht += `<span style="width: 15%;"><a style="cursor: pointer; color: blue;" onclick="update_download_status('${item['gid']}', 'remove');">${i18next.t('explore.window.file.download.list.action.remove')}</a>`;
                                }
                                ht += `</span></div></div>`;
                            })
                            $('#win-explorer>.page>.main-download>.content>.view')[0].innerHTML = ht;
                        }
                    } else {
                        $.Toast(data['msg'], 'error');
                    }
                }
            })
        },
        open_file: (file_id,filename) => {
            let filenames = filename.split('.');
            let format = filenames[filenames.length - 1].toLowerCase();
            switch (format) {
                case 'txt':
                    edit_text_file(file_id);
                    break;
                case 'md':
                    open_md(file_id);
                    break;
                case 'mp4':
                    apps.explorer.open_video(file_id, filename);
                    break;
                case 'mp3':
                    open_music(file_id);
                    break;
                case 'jpg':
                case 'jpeg':
                case 'png':
                case 'bmp':
                case 'gif':
                    apps.explorer.open_picture(file_id, filename);
                    break
                case 'xmind':
                    open_xmind(file_id);
                    break;
                case 'sheet':
                    open_sheet(file_id);
                    break;
                case 'docu':
                    open_document(file_id, filename);
                    break;
                case 'py':
                    open_python(file_id);
                    break;
                case 'docx':
                case 'doc':
                    open_office(file_id, 'word');
                    break;
                case 'xlsx':
                case 'xls':
                    open_office(file_id, 'excel');
                    break;
                case 'pptx':
                case 'ppt':
                    open_office(file_id, 'powerpoint');
                    break;
                case 'torrent':
                    open_torrent(file_id);
                    break;
                default:
                    apps.explorer.download(file_id);
                    break;
            }
        },
        select: (id) => {
            // let element = document.getElementById('check' + id);
            // element.checked = !element.checked;
            apps.explorer.is_use += 1;
        },
        goto: (path, path_id, clear = true) => {
            $('#win-explorer>.page>.main>.content>.view')[0].innerHTML = '';
            let pathl = path.split('/');
            let pathlid = path_id.split('/');
            let pathqwq = '';
            let pathqwqid = '';
            let sort_field = 'update_time';
            let sort_type = 'desc';
            if (path === i18next.t('computer')) {
                apps.explorer.reset(clear);
                return null;
            }
            $('#win-explorer>.path>.tit')[0].dataset.path = path;
            $('#win-explorer>.path>.tit')[0].id=path_id;
            $('#win-explorer>.path>.tit>.path')[0].innerHTML = '<div class="text" onclick="apps.explorer.reset()">' + i18next.t('computer') +'</div><div class="arrow">&gt;</div>';
            $('#win-explorer>.path>.tit>.icon')[0].style.marginTop = '0px';
            document.getElementById("all_files").checked = false;
            document.querySelectorAll('#win-explorer>.page>.main>.content>.header>.row>span>button').forEach(item => {
                if (item.className) {
                    sort_field = item.id.split('-')[0];
                    sort_type = item.className;
                }
            })
            $('#win-explorer>.path>.search')[0].style.display = 'flex';
            $('#win-explorer>.path>.search>input')[0].value = '';
            document.querySelector('#win-explorer>.page>.main>.tool').style.display = 'flex';
            document.querySelectorAll('#win-explorer>.page>.main>.tool>.asd').forEach(item => {
                item.style.display='flex';
            })
            document.querySelectorAll('#win-explorer>.page>.main>.tool>.dsa').forEach(item => {
                item.style.display='none';
            })
            if (path_id === 'C') {
                m_tab.rename('explorer', '<img src="img/explorer/diskwin.svg" style="margin-top:2.5px" alt="diskwin.svg" loading="lazy">' + pathl[pathl.length - 1]);
                return;
            }
            else if (pathlid[pathlid.length - 1].length === 1) {
                m_tab.rename('explorer', '<img src="img/explorer/disk.svg" alt="disk.svg" loading="lazy">' + pathl[pathl.length - 1]);
                tmp = queryAllFiles(pathlid[pathlid.length - 1], "", sort_field, sort_type);
            }
            else {
                m_tab.rename('explorer', '<img src="img/explorer/folder.svg" alt="folder.svg" loading="lazy">' + pathl[pathl.length - 1]);
                tmp = queryAllFiles(pathlid[pathlid.length - 1], "", sort_field, sort_type);
            }
            apps.explorer.tabs[apps.explorer.now][2] = path;
            apps.explorer.tabs[apps.explorer.now][3] = path_id;
            for(let i=0; i<pathl.length; i++) {
                pathqwq += pathl[i];
                pathqwqid += pathlid[i];
                $('#win-explorer>.path>.tit>.path')[0].innerHTML += `<div class="text" onclick="apps.explorer.goto('${pathqwq}', '${pathqwqid}')">${pathl[i]}</div><div class="arrow">&gt;</div>`;
                pathqwq += '/';
                pathqwqid += '/';
            }
            if (tmp.length === 0) {
                $('#win-explorer>.page>.main>.content>.header')[0].style.display = 'none';
                $('#win-explorer>.page>.main>.content>.view')[0].innerHTML = '<p class="info">'+i18next.t('explore.window.file.list.empty.tips')+'</p>';
            } else {
                let ht = '';
                if ($('.list_view>img')[0].src.indexOf("list_view.svg") > 0) {
                    $('#win-explorer>.page>.main>.content>.header')[0].style.display = 'none';
                    $('#win-explorer>.page>.main>.content>.view').addClass("icon-view");
                    for (let i = 0; i < tmp.length; i++) {
                        if (tmp[i]['folder_type'] === 'folder') {
                            ht += `<div class="row" title="${tmp[i]['name']}"><input type="checkbox" id="check${tmp[i]['id']}"><a class="a touchs files" style="padding-left:0;" id="f${tmp[i]['id']}" onclick="apps.explorer.select('${tmp[i]['id']}');" ondblclick="apps.explorer.goto('${path}/${tmp[i]['name']}', '${path_id}/${tmp[i]['id']}')"><img src="img/explorer/folder.svg" alt="default" loading="lazy"><div>${tmp[i]['name']}</div></a></div>`;
                        } else {
                            let f_src = icons[tmp[i]['format']] || default_icon;
                            switch (tmp[i]['format']) {
                                case 'jpg':
                                case 'jpeg':
                                case 'png':
                                case 'bmp':
                                case 'gif':
                                    f_src = server + "/file/download/" + tmp[i]['id'];
                                    break;
                            }
                            ht += `<div class="row" title="${tmp[i]['name']}"><input type="checkbox" id="check${tmp[i]['id']}"><a class="a touchs act file" style="padding-left:0;" id="f${tmp[i]['id']}" onclick="apps.explorer.select('${tmp[i]['id']}');" ondblclick="apps.explorer.open_file('${tmp[i]['id']}', '${tmp[i]['name']}')"><img src="${f_src}" alt="default" loading="lazy"><div>${tmp[i]['name']}</div></a></div>`;
                        }
                    }
                } else {
                    $('#win-explorer>.page>.main>.content>.header')[0].style.display = 'flex';
                    $('#win-explorer>.page>.main>.content>.view').removeClass("icon-view");
                    for (let i = 0; i < tmp.length; i++) {
                        if (tmp[i]['folder_type'] === 'folder') {
                            ht += `<div class="row" style="padding-left: 5px;"><input type="checkbox" id="check${tmp[i]['id']}" style="float: left; margin-top: 8px;margin-right: 8px;"><a class="a item touchs files" id="f${tmp[i]['id']}" onclick="apps.explorer.select('${tmp[i]['id']}');" ondblclick="apps.explorer.goto('${path}/${tmp[i]['name']}', '${path_id}/${tmp[i]['id']}')" oncontextmenu="showcm(event,'explorer.folder',['${path}/${tmp[i]['name']}', '${path_id}/${tmp[i]['id']}']);return stop(event);">
                                <span style="width: 40%;"><img style="float: left;" src="img/explorer/folder.svg" alt="folder.svg" loading="lazy">${tmp[i]['name']}</span><span style="width: 10%;">${i18next.t('explore.window.file.list.folder.type.name')}</span>
                                <span style="width: 10%;"></span><span style="width: 20%;">${tmp[i]['update_time']}</span><span style="width: 20%;">${tmp[i]['create_time']}</span></a></div>`;
                        } else {
                            let f_src = icons[tmp[i]['format']] || default_icon;
                            ht += `<div class="row" style="padding-left: 5px;"><input type="checkbox" id="check${tmp[i]['id']}" style="float: left; margin-top: 8px;margin-right: 8px;"><a class="a item act touchs file" id="f${tmp[i]['id']}" onclick="apps.explorer.select('${tmp[i]['id']}');" ondblclick="apps.explorer.open_file('${tmp[i]['id']}', '${tmp[i]['name']}')" oncontextmenu="showcm(event,'explorer.file','${path_id}/${tmp[i]['id']}');return stop(event);">
                                <span style="width: 40%;"><img style="float: left;" src="${f_src}" alt="file" loading="lazy">${tmp[i]['name']}</span><span style="width: 10%;">${tmp[i]['format']}</span>
                                <span style="width: 10%;">${tmp[i]['size']}</span><span style="width: 20%;">${tmp[i]['update_time']}</span><span style="width: 20%;">${tmp[i]['create_time']}</span></a></div>`;
                        }
                    }
                }
                $('#win-explorer>.page>.main>.content>.view')[0].innerHTML = ht;
                document.querySelectorAll('.a.touchs').forEach(item => {
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
                            item.ondblclick(e);
                        }
                    }, false);
                })
            }
            if (pathl.length === 1) {
                $('#win-explorer>.path>.goback').attr('onclick', 'apps.explorer.reset()');
                $('#win-explorer>.path>.back').attr('onclick', 'apps.explorer.reset()');
            } else {
                $('#win-explorer>.path>.goback').attr('onclick', `apps.explorer.goto('${path.substring(0, path.length - pathl[pathl.length - 1].length - 1)}', '${path_id.substring(0, path_id.length - pathlid[pathlid.length - 1].length - 1)}')`);
                $('#win-explorer>.path>.back').attr('onclick', `apps.explorer.goto('${path.substring(0, path.length - pathl[pathl.length - 1].length - 1)}', '${path_id.substring(0, path_id.length - pathlid[pathlid.length - 1].length - 1)}')`);
            }
            // $('#win-explorer>.path>.tit')[0].innerHTML = path;
        },
        add: (path_id, type = "file", file_type="txt") => {
            let paths = path_id.split('/');
            let post_data = {
                id: paths[paths.length - 1],
                type: type,
                file_type: file_type
            }
            let url = server + '/folder/create';
            if (type === 'file') {
                url = server + '/file/create';
            }
            $.ajax({
                type: 'POST',
                url: url,
                data: JSON.stringify(post_data),
                contentType: 'application/json',
                async: false,
                success: function (data) {
                    if (data['code'] === 0) {
                        $.Toast(data['msg'], 'success');
                    } else {
                        $.Toast(data['msg'], 'error');
                    }
                }
            })
            apps.explorer.goto($('#win-explorer>.path>.tit')[0].dataset.path, path_id);
        },
        rename: (path) => {
            let pathl = path.split('/');
            let name = pathl[pathl.length - 1];
            if ($('.list_view>img')[0].src.indexOf("list_view.svg") > 0) {
                let element = document.querySelector('#f' + name).querySelectorAll('div')[0];
                let old_name = element.innerText;
                element.innerHTML = '';
                let input = document.createElement("input");
                input.id = "new_name";
                input.className = "input";
                input.value = old_name;
                input.style.width = '100%';
                element.appendChild(input);
                setTimeout(() => {$("#new_name").focus(); $("#new_name").select();}, 200);
                element.classList.add("change");
                let input_ = document.getElementById("new_name");
                input_.addEventListener("keyup", function (event) {if (event.key === "Enter") {rename_file_and_folder(name, old_name);}});
            } else {
                let element = document.querySelector('#f' + name).querySelectorAll('span')[0];
                let old_name = element.innerText;
                element.innerHTML = element.querySelector("img").outerHTML;
                let input = document.createElement("input");
                input.id = "new_name";
                input.className = "input";
                input.value = old_name;
                input.style.width = element.clientWidth - 35 + 'px';
                element.appendChild(input);
                element.appendChild(add_button_to_input(name, old_name));
                setTimeout(() => {$("#new_name").focus(); $("#new_name").select();}, 200);
                element.classList.add("change");
                let input_ = document.getElementById("new_name");
                input_.addEventListener("keyup", function (event) {if (event.key === "Enter") {rename_file_and_folder(name, old_name);}});
            }
        },
        syncing: (path, is_backup) => {
            let pathl = path.split('/');
            let name = pathl[pathl.length - 1];
            $.ajax({
                type: 'GET',
                url: server + '/syncing/set/' + name + '/' + is_backup,
                success: function (data) {
                    if (data['code'] === 0) {
                        $.Toast(data['msg'], 'success');
                    } else {
                        $.Toast(data['msg'], 'error');
                    }
                }
            })
        },
        manual_backup: () => {
            if ($('.dp.app-color.backup')[0].classList.contains('show')) {
                $('.dp.app-color.backup').toggleClass('show');
                return;
            }
            $.ajax({
                type: 'GET',
                url: server + '/syncing/start',
                success: function (data) {
                    if (data['code'] === 0) {
                        $.Toast(data['msg'], 'success');
                    } else {
                        $.Toast(data['msg'], 'error');
                    }
                }
            })
            $.ajax({
                type: 'GET',
                url: server + '/syncing/list',
                success: function (data) {
                    if (data['code'] === 0) {
                        let s = '';
                        data['data'].forEach(item => {
                            s += `<div><div style="width: 20%;">${item['name']}</div><div style="width: 20%;">${item['create_time']}</div><div style="width: 20%;">${item['update_time']}</div><div style="width: 30%;"><a href="javascript:void(0);" onclick="apps.explorer.open_origin_path_folder(${item['id']});return false;" style="color:blue;">${i18next.t('setting.window.shell.server.list.action.open')}</a><a href="javascript:void(0);" onclick="apps.explorer.syncing('${item['id']}', 0);return false;" style="color:blue;margin-left:15px;">${i18next.t('explore.window.file.tool.cancel.backup.title')}</a></div></div><br />`;
                        })
                        $('.server-item.backup')[0].innerHTML = s;
                        $('.dp.app-color.backup').toggleClass('show');
                    } else {
                        $.Toast(data['msg'], 'error');
                    }
                }
            })
        },
        copy: (file_id) => {
            show_modal_cover();
            $.ajax({
                type: 'GET',
                url: server + '/file/copy/' + file_id,
                success: function (data) {
                    if (data['code'] === 0) {
                        $.Toast(data['msg'], 'success');
                        apps.explorer.goto($('#win-explorer>.path>.tit')[0].dataset.path, $('#win-explorer>.path>.tit')[0].id);
                        close_modal_cover();
                    } else {
                        $.Toast(data['msg'], 'error');
                        close_modal_cover();
                    }
                }
            })
        },
        del: (path) => {
            let pathl = path.split('/');
            let name = pathl[pathl.length - 1];
            let file_type = 'file';
            if (document.querySelector('#f' + name).classList.contains('files')) {
                file_type = 'folder';
            }
            delete_file([name], file_type);
            apps.explorer.goto($('#win-explorer>.path>.tit')[0].dataset.path, $('#win-explorer>.path>.tit')[0].id);
        },
        share: () => {
            let ids = getSelectedIds();
            if (ids.folder.length > 0) {
                $.Toast(i18next.t("msg.share.file.error1"), "error");
                return;
            }
            if (ids.file.length === 0) {
                $.Toast(i18next.t("msg.share.file.error2"), "error");
                return;
            }
            if (ids.file.length > 1) {
                $.Toast(i18next.t("msg.share.file.error3"), "error");
                return;
            }
            let share_times = document.getElementById('share-time').value;
            let post_data = {
                id: ids.file[0],
                times: parseInt(share_times)
            }
            $.ajax({
                type: 'POST',
                url: server + '/file/share',
                data: JSON.stringify(post_data),
                contentType: 'application/json',
                success: function (data) {
                    if (data['code'] === 0) {
                        $.Toast(data['msg'], 'success');
                        closenotice();
                    } else {
                        $.Toast(data['msg'], 'error');
                    }
                }
            })
        },
        download: (file_id) => {
            window.open(server + '/file/download/' + file_id);
        },
        coediting: (file_id) => {
            let pathl = file_id.split('/');
            let url_t = window.location.href + "module/onlyoffice.html?server=" + server + "&id=" + pathl[pathl.length - 1] + "&lang=" + lang;
            let textarea = document.createElement('textarea');
            textarea.value = url_t;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            alert(url_t);
        },
        download_online: () => {
            show_modal_cover(true, false);
            let folder_id = $('#win-explorer>.path>.tit')[0].id.split('/');
            let downloader_url = document.getElementById("downloader-url").value;
            let downloader_cookie = document.getElementById("downloader-cookie").value;
            let post_data = {
                parent_id: folder_id[folder_id.length - 1],
                url: downloader_url,
                cookie: downloader_cookie
            }
            $.ajax({
                type: 'POST',
                url: server + '/download/file',
                data: JSON.stringify(post_data),
                contentType: 'application/json',
                success: function (data) {
                    closenotice();
                    close_modal_cover();
                    if (data['code'] === 0) {
                        if (data['data'] && data['total'] > 0) {
                            shownotice("selectedFiles");
                            let ht = "";
                            data['data'].forEach(item => {
                                ht += `<div style="margin: 8px 0 8px 0;display: flex;flex-direction: row;justify-content: space-between;flex-wrap: nowrap;"><div style="width:80%;"><input name="options" type="radio" value="${item['gid']},${item['index']},${item['folder']}" id="${item['index']}"><span style="margin-left:5px;">${item['name']}</span></div><span>${item['size']}</span></div>`;
                            })
                            $('#notice>.cnt>p')[0].innerText = i18next.t('explore.window.file.tool.downloader.window.selected');
                            document.getElementById("selected-file").innerHTML = ht;
                            $('#notice>.btns>.detail').attr("onclick", `update_download_status('${data['data'][0]['gid']}', 'cancel,remove', false);closenotice();`);
                        } else {
                            $.Toast(data['msg'], 'success');
                        }
                    } else {
                        $.Toast(data['msg'], 'error');
                    }
                }
            })
        },
        download_selected: () => {
            show_modal_cover(true, false);
            let selectedRadio = document.querySelector('input[name="options"]:checked');
            let files = selectedRadio.value.split(',');
            let post_data = {
                gid: files[0],
                folder: files[2],
                index: files[1]
            }
            $.ajax({
                type: 'POST',
                url: server + '/download/selected',
                data: JSON.stringify(post_data),
                contentType: 'application/json',
                success: function (data) {
                    if (data['code'] === 0) {
                        $.Toast(data['msg'], 'success');
                        closenotice();
                    } else {
                        $.Toast(data['msg'], 'error');
                    }
                    close_modal_cover();
                }
            })
        },
        get_shortcuts: () => {
            $.ajax({
                type: 'GET',
                url: server + '/file/shortcuts',
                success: function (data) {
                    if (data['code'] === 0) {
                        let desktop = document.getElementById("desktop");
                        data.data.forEach(item => {
                            let parent_div = document.createElement('div');
                            parent_div.className = 'b';
                            parent_div.setAttribute('ondblclick', `apps.explorer.open_file('${item.file_id}', '${item.name}');`);
                            parent_div.setAttribute('ontouchstart', `apps.explorer.open_file('${item.file_id}', '${item.name}');`);
                            parent_div.setAttribute('win12_title', item.name);
                            parent_div.setAttribute('oncontextmenu', `return showcm(event,'desktop.file',['${item.id}','${item.file_id}','${item.name}']);`);
                            parent_div.setAttribute('appname', item.name);
                            parent_div.setAttribute('data-descp', 'hide');
                            let file_src = icons[item.format] || default_icon;
                            parent_div.innerHTML = `<img src="${file_src}" alt="dfault" loading="lazy"><p>${item.name}</p>`;
                            desktop.appendChild(parent_div);
                        })
                        document.querySelectorAll('*[win12_title]:not(.notip)').forEach(a => {
                            a.addEventListener('mouseenter', showdescp);
                            a.addEventListener('mouseleave', hidedescp);
                        })
                    } else {
                        $.Toast(data['msg'], 'error');
                        document.querySelectorAll('*[win12_title]:not(.notip)').forEach(a => {
                            a.addEventListener('mouseenter', showdescp);
                            a.addEventListener('mouseleave', hidedescp);
                        })
                    }
                    close_modal_cover();
                }
            })
        },
        add_shortcuts: (files) => {
            let pathl = files.split('/');
            show_modal_cover(true, false);
            $.ajax({
                type: 'GET',
                url: server + '/file/shortcuts/save/' + pathl[pathl.length - 1],
                success: function (data) {
                    if (data['code'] === 0) {
                        $.Toast(data['msg'], 'success');
                    } else {
                        $.Toast(data['msg'], 'error');
                    }
                    close_modal_cover();
                }
            })
        },
        delete_shortcuts: (file_id) => {
            show_modal_cover(true, false);
            $.ajax({
                type: 'GET',
                url: server + '/file/shortcuts/delete/' + file_id,
                success: function (data) {
                    if (data['code'] === 0) {
                        $.Toast(data['msg'], 'success');
                        window.location.reload();
                    } else {
                        $.Toast(data['msg'], 'error');
                    }
                    close_modal_cover();
                }
            })
        },
        open_search_origin_path: (file_id) => {
            show_modal_cover(true, false);
            $.ajax({
                type: 'GET',
                url: server + '/file/path/' + file_id,
                success: function (data) {
                    if (data['code'] === 0) {
                        apps.explorer.goto(data.data.name,data.data.id);
                    } else {
                        $.Toast(data['msg'], 'error');
                    }
                    close_modal_cover();
                }
            })
        },
        open_origin_path: (file_id) => {
            show_modal_cover(true, false);
            $.ajax({
                type: 'GET',
                url: server + '/file/path/' + file_id,
                success: function (data) {
                    if (data['code'] === 0) {
                        openapp('explorer');
                        apps.explorer.goto(data.data.name,data.data.id);
                    } else {
                        $.Toast(data['msg'], 'error');
                    }
                    close_modal_cover();
                }
            })
        },
        open_origin_path_folder: (folder_id) => {
            show_modal_cover(true, false);
            $.ajax({
                type: 'GET',
                url: server + '/folder/path/' + folder_id,
                success: function (data) {
                    if (data['code'] === 0) {
                        openapp('explorer');
                        apps.explorer.goto(data.data.name,data.data.id);
                    } else {
                        $.Toast(data['msg'], 'error');
                    }
                    close_modal_cover();
                }
            })
        },
        export: () => {
            let ids = getSelectedIds();
            if (ids.folder.length + ids.file.length === 0) {
                $.Toast(i18next.t('msg.export.file.error1'), "error");
                return;
            }
            if (ids.folder.length > 0 && ids.file.length > 0) {
                $.Toast(i18next.t('msg.export.file.error2'), "error");
                return;
            }
            if (ids.folder.length > 0) {
                if (ids.folder.length === 1) {
                    export_file(ids.folder, 'folder');
                } else {
                    $.Toast(i18next.t('msg.export.file.error3'), "error");
                    return;
                }
            }
            if (ids.file.length > 0) {
                if (ids.file.length === 1) {
                    apps.explorer.download(ids.file[0]);
                } else {
                    export_file(ids.file, 'file');
                }
            }
        },
        open_video: (file_id, filename) => {
            openapp('video');
            $('.window.video')[0].style.width = 'auto';
            $('.window.video>.titbar>span>.title')[0].innerText = filename;
            $('#win-video')[0].innerHTML = '<video class="my_video" controls preload="metadata" data-setup="{}" playsinline><source src="' + server + '/file/playVideo/' + file_id + '" type="video/mp4"><track src="" srcLang="'+lang+'" kind="subtitles" label="'+lang+'"></video>';
            document.getElementsByClassName('my_video')[0].addEventListener('loadedmetadata', function () {
                this.currentTime = localStorage.getItem(file_id);
            }, false);
            document.getElementsByClassName('my_video')[0].addEventListener('timeupdate', function (){
                if (this.currentTime > 0) {localStorage.setItem(file_id, this.currentTime);}
            }, false);
            document.getElementsByClassName('my_video')[0].addEventListener('ended', function () {
                localStorage.removeItem(file_id);
            }, false);
        },
        open_picture: (file_id, filename) => {
            $('#win-image>.my_video')[0].src = '';
            openapp('picture');
            $('.window.picture')[0].style.width='auto';
            $('.window.picture>.titbar>span>.title')[0].innerText = filename;
            $('#win-image>.my_video')[0].src = server + '/file/download/' + file_id;
            let viewer = new Viewer(document.querySelectorAll('#win-image>.my_video')[0], {viewed() {},});
        },
        change_view: () => {
            let view_url = $('.list_view>img')[0].src;
            if (view_url.indexOf("list_view.svg") > 0) {
                $('.list_view>img')[0].src = 'img/explorer/icon_view.svg';
            } else {
                $('.list_view>img')[0].src = 'img/explorer/list_view.svg';
            }
            apps.explorer.goto($('#win-explorer>.path>.tit')[0].dataset.path, $('#win-explorer>.path>.tit')[0].id);
        },
        history: [],
        historypt: [],
        initHistory: (tab) => {
            apps.explorer.history[tab] = [];
            apps.explorer.historypt[tab] = -1;
        },
        pushHistory: (tab, u) => {
            apps.explorer.history[tab].push(u);
            apps.explorer.historypt[tab]++;
        },
        // topHistory: (tab) => {
        //     return apps.explorer.history[tab][apps.explorer.historypt[tab]];
        // },
        // popHistory: (tab) => {
        //     apps.explorer.historypt[tab]--;
        //     return apps.explorer.history[tab][apps.explorer.historypt[tab]];
        // },
        // incHistory: (tab) => {
        //     apps.explorer.historypt[tab]++;
        //     return apps.explorer.history[tab][apps.explorer.historypt[tab]];
        // },
        delHistory: (tab) => {
            apps.explorer.history[tab].splice(apps.explorer.historypt[tab] + 1, apps.explorer.history[tab].length - 1 - apps.explorer.historypt[tab]);
        },
        // historyIsEmpty: (tab) => {
        //     return apps.explorer.historypt[tab] <= 0;
        // },
        historyIsFull: (tab) => {
            return apps.explorer.historypt[tab] >= apps.explorer.history[tab].length - 1;
        },
        checkHistory: (tab) => {
            if (apps.explorer.historyIsFull(tab)) {
                $('#win-explorer>.path>.front').addClass('disabled');
            }
            else if (!apps.explorer.historyIsFull(tab)) {
                $('#win-explorer>.path>.front').removeClass('disabled');
            }
        },
        // back: (tab) => {
        //     apps.explorer.goto(apps.explorer.popHistory(tab), false);
        //     apps.explorer.checkHistory(tab);
        // },
        // front: (tab) => {
        //     apps.explorer.goto(apps.explorer.incHistory(tab), false);
        //     apps.explorer.checkHistory(tab);
        // }
    },
    calc: {
        init: () => {
            document.getElementById('calc-input').innerHTML = "0";
            if ($('.window.calc>link').length < 1) {
                let css_link = document.createElement('link');
                css_link.setAttribute('rel', 'stylesheet');
                css_link.setAttribute('href', 'css/calc.css');
                $('.window.calc')[0].appendChild(css_link);
            }
            if ($('.window.calc>script').length < 1) {
                let script = document.createElement('script');
                script.setAttribute('src', 'js/calculator_kernel.js');
                $('.window.calc')[0].appendChild(script);
                script = document.createElement('script');
                script.setAttribute('src', 'js/big.min.js');
                $('.window.calc')[0].appendChild(script);
            }
        }
    },
    notepad: {
        init: () => {
            $('#win-notepad>.text-box').addClass('down');
            if ($('.window.notepad>link').length < 1) {
                let css_link = document.createElement('link');
                css_link.setAttribute('rel', 'stylesheet');
                css_link.setAttribute('href', 'css/notepad.css');
                $('.window.notepad')[0].appendChild(css_link);
            }
            setTimeout(() => {
                $('#win-notepad>.text-box').val('');
                $('#win-notepad>.text-box').removeClass('down')
            }, 200);
        }
    },
    markdown: {init: () => {return null;}},
    video: {init: () => {return null;}},
    music: {init: () => {return null;}},
    chat: {init: () => {return null;}},
    karaoke: {init: () => {return null;}},
    xmind: {init: () => {return null;}},
    sheet: {init: () => {return null;}},
    word: {init: () => {return null;}},
    excel: {init: () => {return null;}},
    game: {init: () => {return null;}},
    powerpoint: {init: () => {return null;}},
    docu: {init: () => {return null;}},
    picture: {init: () => {return null;}},
    pythonEditor: {init: () => {return null;}},
    python: {
        codeCache: '',
        prompt: '>>> ',
        indent: false,
        load: () => {
            if ($('.window.python>link').length < 1) {
                let css_link = document.createElement('link');
                css_link.setAttribute('rel', 'stylesheet');
                css_link.setAttribute('href', 'css/terminal.css');
                $('.window.python')[0].appendChild(css_link);
            }
            if ($('.window.python>script').length < 1) {
                let script_link = document.createElement('script');
                script_link.setAttribute('type', 'text/javascript');
                script_link.setAttribute('src', 'module/python/pyodide.js');
                script_link.onload = function () {
                    (async function () {
                        apps.python.pyodide = await loadPyodide();
                        apps.python.pyodide.runPython(`
                    import sys
                    import io
                    `);
                    })();
                }
                $('.window.python')[0].appendChild(script_link);
            } else {
                (async function () {
                    apps.python.pyodide = await loadPyodide();
                    apps.python.pyodide.runPython(`
                import sys
                import io
                `);
                })();
            }
        },
        init: () => {
            $('#win-python').html(`
        <pre>
Python 3.12.1 (main, Jul 26 2024, 14:03:47) [MSC v.1938 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
        </pre>
        <pre class="text-cmd"></pre>
        <pre style="display: flex;"><span class='prompt'>>>> </span><input type="text" onkeyup="if (event.keyCode === 13) { apps.python.run(); }"></pre>`);
        },
        run: () => {
            if (apps.python.pyodide) {
                const input = $('#win-python>pre>input');
                const _code = input.val();
                if (_code === "exit()") {
                    hidewin('python');
                    input.val('');
                }
                else {
                    const elt = $('#win-python>pre.text-cmd')[0];
                    const lastChar = _code[_code.length - 1];
                    let newD = document.createElement('div');
                    newD.innerText = `${apps.python.prompt}${_code}`;
                    elt.appendChild(newD);
                    if (lastChar !== ':' && lastChar !== '\\' && ((!apps.python.indent || _code === ''))) {
                        apps.python.prompt = '>>> ';
                        apps.python.codeCache += _code;
                        apps.python.indent = false;
                        const code = apps.python.codeCache;
                        apps.python.codeCache = '';
                        apps.python.pyodide.runPython('sys.stdout = io.StringIO()');
                        try {
                            const result = String(apps.python.pyodide.runPython(code));
                            if (apps.python.pyodide.runPython('sys.stdout.getvalue()')) {
                                newD = document.createElement('div');
                                newD.innerText = `${apps.python.pyodide.runPython('sys.stdout.getvalue()')}`;
                                elt.appendChild(newD);
                            }
                            if (result && result !== 'undefined') {
                                newD = document.createElement('div');
                                if (result === 'false') {
                                    newD.innerText = 'False';
                                }
                                else if (result === 'true') {
                                    newD.innerText = 'True';
                                }
                                else {
                                    newD.innerText = result;
                                }
                                elt.appendChild(newD);
                            }
                        }
                        catch (err) {
                            newD = document.createElement('div');
                            newD.innerText = `${err.message}`;
                            elt.appendChild(newD);
                        }
                    }
                    else {
                        apps.python.prompt = '... ';
                        if (lastChar === ':') {
                            apps.python.indent = true;
                        }
                        apps.python.codeCache += _code + '\n';
                    }
                    input.val('');

                    // 自动聚焦
                    input.blur();
                    input.focus();

                    $('#win-python .prompt')[0].innerText = apps.python.prompt;
                }
            }
        }
    },
    edge: {
        init: () => {
            $('#win-edge>iframe').remove();
            apps.edge.tabs = [];
            apps.edge.len = 0;
            apps.edge.newtab();
        },
        tabs: [],
        now: null,
        len: 0,
        history: [],
        historypt: [],
        reloadElt: '<loading class="reloading"><svg viewBox="0 0 16 16"><circle cx="8px" cy="8px" r="5px"></circle><circle cx="8px" cy="8px" r="5px"></circle></svg></loading>',
        max: false,
        fuls: false,
        b1: false, b2: false, b3: false,
        newtab: () => {
            m_tab.newtab('edge', i18next.t('tab.new'));
            apps.edge.initHistory(apps.edge.tabs[apps.edge.tabs.length - 1][0]);
            apps.edge.pushHistory(apps.edge.tabs[apps.edge.tabs.length - 1][0], 'https://bing.com');
            $('#win-edge').append(`<iframe id="iframe_edge" src="module/edge/mainpage.html" class="${apps.edge.tabs[apps.edge.tabs.length - 1][0]}">`);
            $('#win-edge>.tool>input.url').focus();
            $("#win-edge>iframe")[apps.edge.tabs.length - 1].onload = function () {
                this.contentDocument.querySelector('input').onkeyup = function (e) {
                    if (e.keyCode === 13 && $(this).val() !== '') {
                        apps.edge.goto($(this).val());
                    }
                }
                this.contentDocument.querySelector('svg').onclick = () => {
                    if ($(this.contentDocument.querySelector('input')).val() !== '') {
                        apps.edge.goto($(this.contentDocument.querySelector('input')).val())
                    }
                }
            };
            m_tab.tab('edge', apps.edge.tabs.length - 1);
            apps.edge.checkHistory(apps.edge.tabs[apps.edge.now][0]);
            $('#edge-path')[0].value = '';
        },
        fullscreen: () => {
            if (!apps.edge.max) {
                maxwin('edge');
                apps.edge.max = !apps.edge.max;
            }
            document.getElementById('fuls-edge').style.display = 'none';
            document.getElementById('edge-max').style.display = 'none';
            document.getElementById('fuls-edge-exit').style.display = '';
            document.getElementById('over-bar').style.display = '';
            $('.edge>.titbar').hide()
            $('.edge>.content>.tool').hide()
            apps.edge.fuls = !apps.edge.fuls;
        },
        exitfullscreen: () => {
            if (apps.edge.max) {
                maxwin('edge'); apps.edge.max = !apps.edge.max;
            }
            document.getElementById('fuls-edge').style.display = '';
            document.getElementById('edge-max').style.display = '';
            document.getElementById('fuls-edge-exit').style.display = 'none';
            document.getElementById('over-bar').style.display = 'none';
            $('.edge>.titbar').show()
            $('.edge>.content>.tool').show()
            apps.edge.fuls = !apps.edge.fuls;
        },
        in_div(id,event) {
            var div = document.getElementById(id);
            var x = event.clientX;
            var y = event.clientY;
            var divx1 = div.offsetLeft;
            var divy1 = div.offsetTop;
            var divx2 = div.offsetLeft + div.offsetWidth;
            var divy2 = div.offsetTop + div.offsetHeight;
            if (x < divx1 || x > divx2 || y < divy1 || y > divy2) {
                //如果离开，则执行。。
                return false;
            }
            else {
                //如检播到，则执行。。
                return true;
            }
        },
        settab: (t, i) => {
            if ($('.window.edge>.titbar>.tabs>.tab.' + t[0] + '>.reloading')[0]) {
                return `<div class="tab ${t[0]}" onclick="m_tab.tab('edge',${i})" oncontextmenu="showcm(event,'edge.tab',${i});stop(event);return false" onmousedown="m_tab.moving('edge',this,event,${i});stop(event);" ontouchstart="m_tab.moving('edge',this,event,${i});stop(event);">${apps.edge.reloadElt}<p>${t[1]}</p><span class="clbtn bi bi-x" onclick="m_tab.close('edge',${i})"></span></div>`;
            }
            else {
                return `<div class="tab ${t[0]}" onclick="m_tab.tab('edge',${i})" oncontextmenu="showcm(event,'edge.tab',${i});stop(event);return false" onmousedown="m_tab.moving('edge',this,event,${i});stop(event);" ontouchstart="m_tab.moving('edge',this,event,${i});stop(event);"><p>${t[1]}</p><span class="clbtn bi bi-x" onclick="m_tab.close('edge',${i})"></span></div>`;
            }
        },
        tab: (c) => {
            $('#win-edge>iframe.show').removeClass('show');
            $('#win-edge>iframe.' + apps.edge.tabs[c][0]).addClass('show');
            $('#win-edge>.tool>input.url').val($('#win-edge>iframe.' + apps.edge.tabs[c][0]).attr('src') === 'module/edge/mainpage.html' ? '' : $('#win-edge>iframe.' + apps.edge.tabs[c][0]).attr('src'));
            $('#win-edge>.tool>input.rename').removeClass('show');
            apps.edge.checkHistory(apps.edge.tabs[apps.edge.now][0]);
        },
        c_rename: (c) => {
            m_tab.tab('edge', c);
            $('#win-edge>.tool>input.rename').val(apps.edge.tabs[apps.edge.now][1]);
            $('#win-edge>.tool>input.rename').addClass('show');
            setTimeout(() => {
                $('#win-edge>.tool>input.rename').focus();
            }, 300);
        },
        reload: () => {
            $('#win-edge>iframe.show').attr('src', $('#win-edge>iframe.show').attr('src'));
            if (!$('.window.edge>.titbar>.tabs>.tab.' + apps.edge.tabs[apps.edge.now][0] + '>.reloading')[0]) {
                $('.window.edge>.titbar>.tabs>.tab.' + apps.edge.tabs[apps.edge.now][0])[0].insertAdjacentHTML('afterbegin', apps.edge.reloadElt);
                $('#win-edge>iframe.' + apps.edge.tabs[apps.edge.now][0])[0].onload = function () {
                    $('.window.edge>.titbar>.tabs>.tab.' + this.classList[0])[0].removeChild($('.window.edge>.titbar>.tabs>.tab.' + this.classList[0] + '>.reloading')[0]);
                }
            }
        },
        getTitle: async (url, np) => {
            const response = await fetch(server + '/forward' + `?url=${url}`);
            if (response.ok === true) {
                const text = await response.text();
                apps.edge.tabs[np][1] = text;
                m_tab.settabs('edge');
                m_tab.tab('edge', np);
            }
        },
        goto: (u, clear = true) => {
            if (!/^https?:\/\/([a-zA-Z0-9.-]+)(:\d+)?/.test(u) && !u.match(/^mainpage.html$/)) {
                // 启用必应搜索
                $('#win-edge>iframe.show').attr('src', 'https://bing.com/search?q=' + encodeURIComponent(u));
                m_tab.rename('edge', u);
            }
            // 检测网址是否带有http头
            else if (!/^https?:\/\//.test(u) && !u.match(/^mainpage.html$/)) {
                $('#win-edge>iframe.show').attr('src', 'http://' + u);
                m_tab.rename('edge', 'http://' + u);
            }
            else {
                $('#win-edge>iframe.show').attr('src', u);
                m_tab.rename('edge', u.match(/^mainpage.html$/) ? i18next.t('tab.new') : u);
            }
            if (!$('.window.edge>.titbar>.tabs>.tab.' + apps.edge.tabs[apps.edge.now][0] + '>.reloading')[0]) {
                $('.window.edge>.titbar>.tabs>.tab.' + apps.edge.tabs[apps.edge.now][0])[0].insertAdjacentHTML('afterbegin', apps.edge.reloadElt);
            }
            $('#win-edge>iframe.' + apps.edge.tabs[apps.edge.now][0])[0].onload = function () {
                $('.window.edge>.titbar>.tabs>.tab.' + this.classList[0])[0].removeChild($('.window.edge>.titbar>.tabs>.tab.' + this.classList[0] + '>.reloading')[0]);
            }
            // apps.edge.getTitle($('#win-edge>iframe.show').attr('src'), apps.edge.now);
            if (clear) {
                apps.edge.delHistory(apps.edge.tabs[apps.edge.now][0]);
                apps.edge.pushHistory(apps.edge.tabs[apps.edge.now][0], $('#win-edge>iframe.show').attr('src'));
            }
            apps.edge.checkHistory(apps.edge.tabs[apps.edge.now][0]);
        },
        initHistory: (tab) => {
            apps.edge.history[tab] = [];
            apps.edge.historypt[tab] = -1;
        },
        pushHistory: (tab, u) => {
            apps.edge.history[tab].push(u);
            apps.edge.historypt[tab]++;
        },
        topHistory: (tab) => {
            return apps.edge.history[tab][apps.edge.historypt[tab]];
        },
        popHistory: (tab) => {
            apps.edge.historypt[tab]--;
            return apps.edge.history[tab][apps.edge.historypt[tab]];
        },
        incHistory: (tab) => {
            apps.edge.historypt[tab]++;
            return apps.edge.history[tab][apps.edge.historypt[tab]];
        },
        delHistory: (tab) => {
            apps.edge.history[tab].splice(apps.edge.historypt[tab] + 1, apps.edge.history[tab].length - 1 - apps.edge.historypt[tab]);
        },
        historyIsEmpty: (tab) => {
            return apps.edge.historypt[tab] <= 0;
        },
        historyIsFull: (tab) => {
            return apps.edge.historypt[tab] >= apps.edge.history[tab].length - 1;
        },
        checkHistory: (tab) => {
            if (apps.edge.historyIsEmpty(tab)) {
                $('#win-edge>.tool>.back').addClass('disabled');
            }
            else if (!apps.edge.historyIsEmpty(tab)) {
                $('#win-edge>.tool>.back').removeClass('disabled');
            }
            if (apps.edge.historyIsFull(tab)) {
                $('#win-edge>.tool>.front').addClass('disabled');
            }
            else if (!apps.edge.historyIsFull(tab)) {
                $('#win-edge>.tool>.front').removeClass('disabled');
            }
        },
        back: (tab) => {
            apps.edge.goto(apps.edge.popHistory(tab), false);
            apps.edge.checkHistory(tab);
        },
        front: (tab) => {
            apps.edge.goto(apps.edge.incHistory(tab), false);
            apps.edge.checkHistory(tab);
        }
    },
    taskmgr: {
        init: () => {}
    }
}

// 日期、时间
let da = new Date();
let date = `${['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][da.getDay()]}, ${da.getFullYear()}-${(da.getMonth() + 1).toString().padStart(2, '0')}-${da.getDate().toString().padStart(2, '0')}`;
if (lang === 'zh-CN') {date = `星期${['日', '一', '二', '三', '四', '五', '六'][da.getDay()]}, ${da.getFullYear()}-${(da.getMonth() + 1).toString().padStart(2, '0')}-${da.getDate().toString().padStart(2, '0')}`;}
$('#s-m-r>.row1>.tool>.date').text(date);
$('.dock.date>.date').text(`${da.getFullYear()}/${(da.getMonth() + 1).toString().padStart(2, '0')}/${da.getDate().toString().padStart(2, '0')}`);
$('#datebox>.tit>.date').text(date);
function loadtime() {
    let ddd = new Date();
    let time = `${ddd.getHours().toString().padStart(2, '0')}:${ddd.getMinutes().toString().padStart(2, '0')}:${ddd.getSeconds().toString().padStart(2, '0')}`
    $('#s-m-r>.row1>.tool>.time').text(time);
    $('.dock.date>.time').text(time);
    $('#datebox>.tit>.time').text(time);
}
loadtime();
setTimeout('loadtime();setInterval(loadtime, 1000);', 1000 - da.getMilliseconds());//修复时间不精准的问题。以前的误差：0-999毫秒；现在：几乎没有
let ddd = new Date();
let today = new Date().getDate();
let start = 7 - ((ddd.getDate() - ddd.getDay()) % 7) + 1;
let daysum = new Date(ddd.getFullYear(), ddd.getMonth() + 1, 0).getDate();
for (let i = 1; i < start; i++) {
    $('#datebox>.cont>.body')[0].innerHTML += '<span></span>';
}
for (let i = 1; i <= daysum; i++) {
    if (i === today) {
        $('#datebox>.cont>.body')[0].innerHTML += `<p class="today">${i}</p>`;
        continue;
    }
    $('#datebox>.cont>.body')[0].innerHTML += `<p>${i}</p>`;
}
apps.explorer.get_shortcuts();
// 应用与窗口
let other_img = ['taskmgr', 'video', 'picture', 'markdown', 'xmind', 'game', 'sheet', 'docu', 'word', 'excel', 'powerpoint', 'pythonEditor']
let onlyoffice_width = {word: 600, excel: 736, powerpoint: 600};
function openapp(name) {
    if ($('#taskbar>.' + name).length !== 0) {
        if ($('.window.' + name).hasClass('min')) {
            minwin(name);
        }
        focwin(name);
        return;
    }
    let source_src = `img/${name}.svg`;
    if (other_img.indexOf(name) > -1) {
        source_src = icons[name];
    }
    $('.window.' + name).addClass('load');
    showwin(name);
    $('#taskbar').attr('count', Number($('#taskbar').attr('count')) + 1);
    $('#taskbar').append(`<a class="${name}" onclick="taskbarclick(\'${name}\')" win12_title="${$(`.window.${name}>.titbar>span>.title`).text()}" onmouseenter="showdescp(event)" onmouseleave="hidedescp(event)"><img src="${source_src}" alt="default" loading="lazy"></a>`);
    if ($('#taskbar').attr('count') === '1') {
        $('#taskbar').css('display', 'flex');
    }
    $('#taskbar>.' + name).addClass('foc');
    setTimeout(() => {
        $('#taskbar').css('width', 4 + $('#taskbar').attr('count') * (34 + 4));
    }, 0);
    let tmp = name.replace(/\-(\w)/g, function (all, letter) {
        return letter.toUpperCase();
    });
    if (apps[tmp].load && !apps[tmp].loaded) {
        apps[tmp].loaded = true;
        apps[tmp].load();
        apps[tmp].init();
        $('.window.' + name).removeClass('load');
        return;
    }
    apps[tmp].init();
    $('.window.' + name).removeClass('load');
    if (name === 'setting') {
        $('#win-setting>.menu>.user>img')[0].src = 'img/pictures/' + document.cookie.split('u=')[1].split(';')[0] +'/avatar.jpg';
        $('#win-setting>.menu>.user>div>p')[0].innerText = nickName;
    }
}
// 窗口操作
function showwin(name) {
    $('.window.' + name).addClass('show-begin');
    setTimeout(() => { $('.window.' + name).addClass('show'); }, 0);
    setTimeout(() => { $('.window.' + name).addClass('notrans'); }, 20);
    $('.window.' + name).attr('style', `top:10%;left:15%;`);
    $('#taskbar>.' + wo[0]).removeClass('foc');
    $('.window.' + wo[0]).removeClass('foc');
    wo.splice(0, 0, name);
    orderwindow();
    $('.window.' + name).addClass('foc');
    if (!$('#control.show')[0] && !$('#datebox.show')[0]) {
        if ($('.window.max:not(.left):not(.right)')[0]) {
            $('#dock-box').addClass('hide');
        }
        else {
            $('#dock-box').removeClass('hide');
        }
    }
    else {
        $('#dock-box').removeClass('hide')
    }
}
function hidewin(name, arg = 'window') {
    $('.window.' + name).removeClass('notrans');
    $('.window.' + name).removeClass('max');
    $('.window.' + name).removeClass('show');
    if (arg === 'window') {
        $('#taskbar').attr('count', Number($('#taskbar').attr('count')) - 1)
        $('#taskbar>.' + name).remove();
        $('#taskbar').css('width', 4 + $('#taskbar').attr('count') * (34 + 4));
        setTimeout(() => {
            if ($('#taskbar').attr('count') === '0') {
                $('#taskbar').css('display', 'none');
            }
        }, 80);
    }
    setTimeout(() => {$('.window.' + name).removeClass('show-begin');}, 20);
    $('.window.' + name + '>.titbar>div>.wbtg.max').html('<i class="bi bi-app"></i>');
    wo.splice(wo.indexOf(name), 1);
    if(wo.length > 0){focwin(wo[0]);}
    if (!$('#control.show')[0] && !$('#datebox.show')[0]) {
        if ($('.window.max:not(.left):not(.right)')[0]) {
            $('#dock-box').addClass('hide');
        }
        else {
            $('#dock-box').removeClass('hide');
        }
    }
    else {
        $('#dock-box').removeClass('hide')
    }
}
function maxwin(name, trigger = true) {
    if ($('.window.' + name).hasClass('max')) {
        $('.window.' + name).removeClass('left');
        $('.window.' + name).removeClass('right');
        $('.window.' + name).removeClass('max');
        $('.window.' + name + '>.titbar>div>.wbtg.max').html('<i class="bi bi-app"></i>');
        $('.window.' + name).addClass('notrans');
        if ($('.window.' + name).attr('data-pos-x') !== 'null' && $('.window.' + name).attr('data-pos-y') !== 'null') {
            $('.window.' + name).css('left', `${$('.window.' + name).attr('data-pos-x')}`);
            $('.window.' + name).css('top', `${$('.window.' + name).attr('data-pos-y')}`);
        }
    } else {
        if (trigger) {
            $('.window.' + name).attr('data-pos-x', `${$('.window.' + name).css('left')}`);
            $('.window.' + name).attr('data-pos-y', `${$('.window.' + name).css('top')}`);
        }
        $('.window.' + name).removeClass('notrans');
        $('.window.' + name).addClass('max');
        $('.window.' + name + '>.titbar>div>.wbtg.max').html('<svg version="1.1" width="12" height="12" viewBox="0,0,37.65105,35.84556" style="margin-top:4px;"><g transform="translate(-221.17804,-161.33903)"><g style="stroke:var(--text);" data-paper-data="{&quot;isPaintingLayer&quot;:true}" fill="none" fill-rule="nonzero" stroke-width="2" stroke-linecap="butt" stroke-linejoin="miter" stroke-miterlimit="10" stroke-dasharray="" stroke-dashoffset="0" style="mix-blend-mode: normal"><path d="M224.68734,195.6846c-2.07955,-2.10903 -2.00902,-6.3576 -2.00902,-6.3576l0,-13.72831c0,0 -0.23986,-1.64534 2.00902,-4.69202c1.97975,-2.68208 4.91067,-2.00902 4.91067,-2.00902h14.06315c0,0 3.77086,-0.23314 5.80411,1.67418c2.03325,1.90732 1.33935,5.02685 1.33935,5.02685v13.39347c0,0 0.74377,4.01543 -1.33935,6.3576c-2.08312,2.34217 -5.80411,1.67418 -5.80411,1.67418h-13.39347c0,0 -3.50079,0.76968 -5.58035,-1.33935z"/><path d="M229.7952,162.85325h16.06111c0,0 5.96092,-0.36854 9.17505,2.64653c3.21412,3.01506 2.11723,7.94638 2.11723,7.94638v18.55642"/></g></g></svg>')
    }
    if (!$('#control.show')[0] && !$('#datebox.show')[0]) {
        if ($('.window.max:not(.left):not(.right)')[0]) {
            $('#dock-box').addClass('hide');
        }
        else {
            $('#dock-box').removeClass('hide');
        }
    }
    else {
        $('#dock-box').removeClass('hide')
    }
    setTimeout(() => {if (name === 'word' || name === 'excel' || name === 'powerpoint') {
        $('.window.' + name + '>.titbar')[0].style.width = Number($('.window.' + name).css('width').split('px')[0]) - onlyoffice_width[name] + 'px';
    }},500);
}
function minwin(name) {
    if ($('.window.' + name).hasClass('min')) {
        $('.window.' + name).addClass('show-begin');
        focwin(name);
        $('#taskbar>.' + name).removeClass('min');
        $('.window.' + name).removeClass('min');
        if ($('.window.' + name).hasClass('min-max')) {
            $('.window.' + name).addClass('max');
        }
        $('.window.' + name).removeClass('min-max');
        setTimeout(() => {
            if (!$('.window.' + name).hasClass('max')) {
                $('.window.' + name).addClass('notrans');
            }
        }, 20);
    } else {
        focwin(null);
        if ($('.window.' + name).hasClass('max')) {
            $('.window.' + name).addClass('min-max');
        }
        $('.window.' + name).removeClass('foc');
        $('.window.' + name).removeClass('max');
        $('#taskbar>.' + name).addClass('min');
        $('.window.' + name).addClass('min');
        $('.window.' + name).removeClass('notrans');
        setTimeout(() => { $('.window.' + name).removeClass('show-begin'); }, 20);
    }
}

function resizewin(win, arg, resizeElt) {
    page.onmousemove = function (e) {
        resizing(win, e, arg);
    }
    page.ontouchmove = function (e) {
        resizing(win, e, arg);
    }
    function up_f() {
        page.onmousedown = null;
        page.ontouchstart = null;
        page.onmousemove = null;
        page.ontouchmove = null;
        page.ontouchcancel = null;
        page.style.cursor = 'auto';
    }
    page.onmouseup = up_f;
    page.ontouchend = up_f;
    page.ontouchcancel = up_f;
    page.style.cursor = window.getComputedStyle(resizeElt, null).cursor;
}
function resizing(win, e, arg) {
    let x, y,
        minWidth = win.dataset.minWidth ? win.dataset.minWidth : 400,
        minHeight = win.dataset.minHeight ? win.dataset.minHeight : 300,
        offsetLeft = win.getBoundingClientRect().left,
        offsetTop = win.getBoundingClientRect().top,
        offsetRight = win.getBoundingClientRect().right,
        offsetBottom = win.getBoundingClientRect().bottom;
    if (e.type.match('mouse')) {
        x = e.clientX;
        y = e.clientY;
    }
    else if (e.type.match('touch')) {
        x = e.touches[0].clientX;
        y = e.touches[0].clientY;
    }
    if (arg === 'right' && x - offsetLeft >= minWidth) {
        win.style.width = x - offsetLeft + 'px';
    }
    else if (arg === 'right') {
        win.style.width = minWidth + 'px';
    }

    if (arg === 'left' && offsetRight - x >= minWidth) {
        win.style.left = x + 'px';
        win.style.width = offsetRight - x + 'px';
    }
    else if (arg === 'left') {
        win.style.width = minWidth + 'px';
        win.style.left = offsetRight - minWidth + 'px';
    }

    if (arg === 'bottom' && y - offsetTop >= minHeight) {
        win.style.height = y - offsetTop + 'px';
    }
    else if (arg === 'bottom') {
        win.style.height = minHeight + 'px';
    }

    if (arg === 'top' && offsetBottom - y >= minHeight) {
        win.style.top = y + 'px';
        win.style.height = offsetBottom - y + 'px';
    }
    else if (arg === 'top') {
        win.style.top = offsetBottom - minHeight + 'px';
        win.style.height = minHeight + 'px';
    }

    if (arg === 'top-left') {
        if (offsetRight - x >= minWidth) {
            win.style.left = x + 'px';
            win.style.width = offsetRight - x + 'px';
        }
        else {
            win.style.left = offsetRight - minWidth + 'px';
            win.style.width = minWidth + 'px';
        }
        if (offsetBottom - y >= minHeight) {
            win.style.top = y + 'px';
            win.style.height = offsetBottom - y + 'px';
        }
        else {
            win.style.top = offsetBottom - minHeight + 'px';
            win.style.height = minHeight + 'px';
        }
    }

    else if (arg === 'top-right') {
        if (x - offsetLeft >= minWidth) {
            win.style.width = x - offsetLeft + 'px';
        }
        else {
            win.style.width = minWidth + 'px';
        }
        if (offsetBottom - y >= minHeight) {
            win.style.top = y + 'px';
            win.style.height = offsetBottom - y + 'px';
        }
        else {
            win.style.top = offsetBottom - minHeight + 'px';
            win.style.height = minHeight + 'px';
        }
    }

    else if (arg === 'bottom-left') {
        if (offsetRight - x >= minWidth) {
            win.style.left = x + 'px';
            win.style.width = offsetRight - x + 'px';
        }
        else {
            win.style.left = offsetRight - minWidth + 'px';
            win.style.width = minWidth + 'px';
        }
        if (y - offsetTop >= minHeight) {
            win.style.height = y - offsetTop + 'px';
        }
        else {
            win.style.height = minHeight + 'px';
        }
    }

    else if (arg === 'bottom-right') {
        if (x - offsetLeft >= minWidth) {
            win.style.width = x - offsetLeft + 'px';
        }
        else {
            win.style.width = minWidth + 'px';
        }
        if (y - offsetTop >= minHeight) {
            win.style.height = y - offsetTop + 'px';
        }
        else {
            win.style.height = minHeight + 'px';
        }
    }
    if (win.classList.value.indexOf('word') > 0 || win.classList.value.indexOf('excel') > 0 || win.classList.value.indexOf('powerpoint') > 0) {
        win.getElementsByClassName('titbar')[0].style.width = Number(win.style.width.split('px')[0]) - 736 + 'px';
    }
}
let wo = [];
function orderwindow() {
    for (let i = 0; i < wo.length; i++) {
        const win = $('.window.' + wo[wo.length - i - 1]);
        if (topmost.includes(wo[wo.length - i - 1])) {
            win.css('z-index', 10 + i + 50/*这里的50可以改，不要太大，不然会覆盖任务栏；不要太小，不然就和普通窗口没有什么区别了。随着版本的更新，肯定会有更多窗口，以后就可以把数字改打一点点*/);
        } else {
            win.css('z-index', 10 + i);
        }
    }
}
// 以下函数基于bug运行，切勿改动！
function focwin(name, arg = 'window') {
    // if(wo[0]==name)return;
    if (arg === 'window') {
        $('#taskbar>.' + wo[0]).removeClass('foc');
        $('#taskbar>.' + name).addClass('foc');
    }
    $('.window.' + wo[0]).removeClass('foc');
    wo.splice(wo.indexOf(name), 1);
    wo.splice(0, 0, name);
    orderwindow();
    $('.window.' + name).addClass('foc');
}
function taskbarclick(name) {
    if ($('.window.' + name).hasClass('foc')) {
        minwin(name);
        return;
    }
    if ($('.window.' + name).hasClass('min')) {
        minwin(name);
    }
    focwin(name);
}

// 选择框
let chstX, chstY;
function ch(e) {
    $('#desktop>.choose').css('left', Math.min(chstX, e.clientX));
    $('#desktop>.choose').css('width', Math.abs(e.clientX - chstX));
    $('#desktop>.choose').css('display', 'block');
    $('#desktop>.choose').css('top', Math.min(chstY, e.clientY));
    $('#desktop>.choose').css('height', Math.abs(e.clientY - chstY));
}
$('#desktop')[0].addEventListener('mousedown', e => {
    chstX = e.clientX;
    chstY = e.clientY;
    this.onmousemove = ch;
})
window.addEventListener('mouseup', e => {
    this.onmousemove = null;
    $('#desktop>.choose').css('left', 0);
    $('#desktop>.choose').css('top', 0);
    $('#desktop>.choose').css('display', 'none');
    $('#desktop>.choose').css('width', 0);
    $('#desktop>.choose').css('height', 0);
})
// 主题
function toggletheme() {
    $('.dock.theme').toggleClass('dk');
    $(':root').toggleClass('dark');
    if ($(':root').hasClass('dark')) {
        $('.window.whiteboard>.titbar>span>.title').text('Blackboard');
    } else {
        $('.window.whiteboard>.titbar>span>.title').text('Whiteboard');
    }
}
// 透明度
function toggle_transparent() {
    $('.window').toggleClass('transparent');
    $('.setting-list>*').toggleClass('transparent');
    $('.card.pinned').toggleClass('transparent');
    $('#win-explorer>.page>.main>.content').toggleClass('transparent');
    $('#win-notepad>.text-box').toggleClass('transparent');
    $('#win-explorer>.page>.main-share>.content').toggleClass('transparent');
    $('#win-explorer>.page>.main-download>.content').toggleClass('transparent');
    $('#win-whiteboard>canvas').toggleClass('transparent');
    $('#win-whiteboard>.toolbar>.tools').toggleClass('transparent');
    $('#notice').toggleClass('transparent');
    $('#notice>.btns').toggleClass('transparent');
    if ($('.window').hasClass('transparent')) {
        localStorage.setItem('transparent', '1');
    } else {
        localStorage.setItem('transparent', '0');
    }
}

const isDarkTheme = window.matchMedia("(prefers-color-scheme: dark)");
if (isDarkTheme.matches) { //是深色
    $('.dock.theme').toggleClass('dk');
    $(':root').toggleClass('dark');
    $('.window.whiteboard>.titbar>span>.title').text('Blackboard');
} else { // 不是深色
    $('.window.whiteboard>.titbar>span>.title').text('Whiteboard');
}
if (localStorage.getItem('transparent') === '1') {
    $('.window').addClass('transparent');
    $('.setting-list>*').addClass('transparent');
    $('.card.pinned').addClass('transparent');
    $('#win-notepad>.text-box').addClass('transparent');
    $('#win-explorer>.page>.main>.content').addClass('transparent');
    $('#win-explorer>.page>.main-share>.content').addClass('transparent');
    $('#win-explorer>.page>.main-download>.content').toggleClass('transparent');
    $('#win-whiteboard>canvas').addClass('transparent');
    $('#win-whiteboard>.toolbar>.tools').addClass('transparent');
    $('#notice').addClass('transparent');
    $('#notice>.btns').addClass('transparent');
}
// 拖拽窗口
const page = document.getElementsByTagName('html')[0];
const titbars = document.querySelectorAll('.window>.titbar');
const wins = document.querySelectorAll('.window');
let deltaLeft = 0, deltaTop = 0, fil = false, filty = 'none', bfLeft = 0, bfTop = 0;
function win_move(e) {
    let cx, cy;
    if (e.type === 'touchmove') {
        cx = e.targetTouches[0].clientX, cy = e.targetTouches[0].clientY;
    } else {
        cx = e.clientX, cy = e.clientY;
    }
    // $(this).css('cssText', `left:${cx - deltaLeft}px;top:${cy - deltaTop}px;`);
    $(this).css('left', `${cx - deltaLeft}px`);
    $(this).css('top', `${cy - deltaTop}px`);
    if (cy <= 0) {
        // $(this).css('cssText', `left:${cx - deltaLeft}px;top:${-deltaTop}px`);
        $(this).css('left', `${cx - deltaLeft}px`);
        $(this).css('top', `${-deltaTop}px`);
        if (!(this.classList[1] in nomax)) {
            $('#window-fill').addClass('top');
            setTimeout(() => {
                $('#window-fill').addClass('fill');
            }, 0);
            fil = this;
            filty = 'top';
        }
    }
    else if (cx <= 0) {
        $(this).css('left', `${-deltaLeft}px`);
        $(this).css('top', `${cy - deltaTop}px`);
        if (!(this.classList[1] in nomax)) {
            $('#window-fill').addClass('left');
            setTimeout(() => {
                $('#window-fill').addClass('fill');
            }, 0);
            fil = this;
            filty = 'left';
        }
    }
    else if (cx >= document.body.offsetWidth - 2) {
        $(this).css('left', `calc(100% - ${deltaLeft}px)`);
        $(this).css('top', `${cy - deltaTop}px`);
        if (!(this.classList[1] in nomax)) {
            $('#window-fill').addClass('right');
            setTimeout(() => {
                $('#window-fill').addClass('fill');
            }, 0);
            fil = this;
            filty = 'right';
        }
    }
    else if (fil) {
        $('#window-fill').removeClass('fill');
        setTimeout(() => {
            $('#window-fill').removeClass('top');
            $('#window-fill').removeClass('left');
            $('#window-fill').removeClass('right');
        }, 200);
        fil = false;
        filty = 'none';
    }
    else if ($(this).hasClass('max')) {
        deltaLeft = deltaLeft / (this.offsetWidth - (45 * 3)) * ((0.7 * document.body.offsetWidth) - (45 * 3));
        maxwin(this.classList[1], false);
        $(this).css('left', `${cx - deltaLeft}px`);
        $(this).css('top', `${cy - deltaTop}px`);
        $('.window.' + this.classList[1] + '>.titbar>div>.wbtg.max').html('<i class="bi bi-app"></i>');

        $(this).addClass('notrans');
    }
}
for (let i = 0; i < wins.length; i++) {
    const win = wins[i];
    const titbar = titbars[i];
    titbar.addEventListener('mousedown', (e) => {
        let x = Number(window.getComputedStyle(win, null).getPropertyValue('left').split("px")[0]);
        let y = Number(window.getComputedStyle(win, null).getPropertyValue('top').split("px")[0]);
        if (y !== 0) {
            bfLeft = x;
            bfTop = y;
        }
        deltaLeft = e.clientX - x;
        deltaTop = e.clientY - y;
        win.classList.add('move_transparent');
        current_window = win;
        page.onmousemove = win_move.bind(win);
    })
    titbar.addEventListener('touchstart', (e) => {
        let x = Number(window.getComputedStyle(win, null).getPropertyValue('left').split("px")[0]);
        let y = Number(window.getComputedStyle(win, null).getPropertyValue('top').split("px")[0]);
        if (y !== 0) {
            bfLeft = x;
            bfTop = y;
        }
        deltaLeft = e.targetTouches[0].clientX - x;
        deltaTop = e.targetTouches[0].clientY - y;
        win.classList.add('move_transparent');
        current_window = win;
        page.ontouchmove = win_move.bind(win);
    })
}
page.addEventListener('mouseup', (e) => {
    page.onmousemove = null;
    if (current_window) {current_window.classList.remove('move_transparent');}
    if (fil) {
        if (filty === 'top') {
            maxwin(fil.classList[1], false);
        }
        else if (filty === 'left') {
            $(fil).addClass('left');
            maxwin(fil.classList[1], false);
        }
        else if (filty === 'right') {
            $(fil).addClass('right');
            maxwin(fil.classList[1], false);
        }
        setTimeout(() => {
            $('#window-fill').removeClass('fill');
            $('#window-fill').removeClass('top');
            $('#window-fill').removeClass('left');
            $('#window-fill').removeClass('right');
        }, 200);
        $('.window.' + fil.classList[1]).attr('data-pos-x', `${bfLeft}px`);
        $('.window.' + fil.classList[1]).attr('data-pos-y', `${bfTop}px`);
        fil = false;
    }
});
page.addEventListener('touchend', (e) => {
    page.ontouchmove = null;
    if (current_window) {current_window.classList.remove('move_transparent');}
    if (fil) {
        if (filty === 'top')
            maxwin(fil.classList[1], false);
        else if (filty === 'left') {
            maxwin(fil.classList[1], false);
            $(fil).addClass('left');
        } else if (filty === 'right') {
            maxwin(fil.classList[1], false);
            $(fil).addClass('right');
        }
        setTimeout(() => {
            $('#window-fill').removeClass('fill');
            $('#window-fill').removeClass('top');
            $('#window-fill').removeClass('left');
            $('#window-fill').removeClass('right');
        }, 200);
        setTimeout(() => {
            $('.window.' + fil.classList[1]).attr('data-pos-x', `${bfLeft}px`);
            $('.window.' + fil.classList[1]).attr('data-pos-y', `${bfTop}px`);
        }, 200);
        fil.setAttribute('style', `left:${bfLeft}px;top:${bfTop}px`);
        fil = false;
    }
});
page.addEventListener('mousemove', (e) => {
    if (e.clientY >= window.innerHeight - 60) {
        $('#dock-box').removeClass('hide');
    }
    else {
        if (!$('#control.show')[0] && !$('#datebox.show')[0]) {
            if ($('.window.max:not(.left):not(.right)')[0]) {
                $('#dock-box').addClass('hide');
            }
            else {
                $('#dock-box').removeClass('hide');
            }
        }
        else {
            $('#dock-box').removeClass('hide');
        }
    }
})
// 启动
document.getElementsByTagName('body')[0].onload = function nupd() {
    setTimeout(() => {
        $('#loadback').addClass('hide');
    }, 50);
    setTimeout(() => {
        $('#loadback').css('display', 'none');
    }, 100);
    document.querySelectorAll('.window').forEach(w => {
        let qw = $(w), wc = w.classList[1];
        qw.attr('onmousedown', `focwin('${wc}')`);
        qw.attr('ontouchstart', `focwin('${wc}')`);
        qw = $(`.window.${wc}>.titbar`);
        qw.attr('oncontextmenu', `return showcm(event,'titbar','${wc}')`);
        if (!(wc in nomax)) {
            qw.attr('ondblclick', `maxwin('${wc}')`);
        }
        qw = $(`.window.${wc}>.titbar>.icon`);
        qw.attr('onclick', `let os=$(this).offset();stop(event);return showcm({clientX:os.left-5,clientY:os.top+this.offsetHeight+3},'titbar','${wc}')`);
        qw.mousedown(stop);
        $(`.window.${wc}>.titbar>div>.wbtg`).mousedown(stop);
    });
    document.querySelectorAll('.window>div.resize-bar').forEach(w => {
        for (const n of ['top', 'bottom', 'left', 'right', 'top-right', 'top-left', 'bottom-right', 'bottom-left']) {
            w.insertAdjacentHTML('afterbegin', `<div class="resize-knob ${n}" onmousedown="resizewin(this.parentElement.parentElement, '${n}', this)"></div>`);
        }
    });
};

function add_button_to_input(name, old_name) {
    let parent_div = document.createElement("div");
    parent_div.className = "input-group-append";
    let confirm_button = document.createElement("icon");
    confirm_button.innerText = "";
    confirm_button.addEventListener('click', ()=> {rename_file_and_folder(name, old_name);})
    let cancel_button = document.createElement("icon");
    cancel_button.innerHTML = "";
    cancel_button.addEventListener('click', ()=> {cancel_rename(name, old_name);})
    parent_div.appendChild(confirm_button);
    parent_div.appendChild(cancel_button);
    return parent_div;
}

function rename_file_and_folder(name, old_name) {
    let new_name = document.getElementById("new_name");
    if (old_name !== new_name.value) {
        let url = server + '/file/rename';
        if (document.querySelector('#f' + name).classList.contains('files')) {
            url = server + '/folder/rename';
        }
        let post_data = {
            id: name,
            name: new_name.value,
        }
        $.ajax({
            type: 'POST',
            url: url,
            async: false,
            data: JSON.stringify(post_data),
            contentType: 'application/json',
            success: function (data) {
                if (data['code'] === 0) {
                    $.Toast(data['msg'], 'success');
                } else {
                    $.Toast(data['msg'], 'error');
                }
            }
        })
    }
    apps.explorer.goto($('#win-explorer>.path>.tit')[0].dataset.path, $('#win-explorer>.path>.tit')[0].id);
}

function cancel_rename(name, old_name) {
    let element = document.querySelector('#f' + name).querySelectorAll('span')[0];
    element.removeChild(element.querySelector("input"));
    element.removeChild(element.querySelector("div"));
    element.append(old_name);
}

function show_modal_cover(gif=true, progress=false) {
    $('.modal_cover')[0].style.display = 'flex';
    if (gif) {
        $('.modal_cover>.modal_gif')[0].style.display = 'flex';
    }
    if (progress) {
        $('.modal_cover>#progressBar')[0].style.display = 'flex';
    }
}

function close_modal_cover() {
    $('.modal_cover')[0].style.display = 'none';
    $('.modal_cover>.modal_gif')[0].style.display = 'none';
    $('.modal_cover>#progressBar')[0].style.display = 'none';
}

function get_current_time(is_year=false) {
    let curr_date = new Date();
    let curr_t = curr_date.getHours() + ":" + curr_date.getMinutes() + ":" + curr_date.getSeconds();
    if (is_year) {
        curr_t = curr_date.getFullYear() + "-" + curr_date.getMonth() + "-" + curr_date.getDay() + " " + curr_t;
    }
    return curr_t;
}

function getSelectedIds(is_all = false) {
    let ids = {folder: [], file: []};
    let items = document.querySelectorAll('#win-explorer>.page>.main>.content>.view>.row');
    let item_id = "";
    for (let i=0; i<items.length; i++) {
        if (is_all || items[i].getElementsByTagName('input')[0].checked) {
            item_id = items[i].getElementsByTagName('a')[0].id;
            if (items[i].getElementsByTagName('a')[0].classList.contains('files')) {
                ids.folder.push(item_id.slice(1, item_id.length));
            } else {
                ids.file.push(item_id.slice(1, item_id.length));
            }
        }
    }
    return ids;
}

function delete_file(ids, file_type, is_delete= 1, delete_type = 0) {
    let post_data = {
        ids: ids,
        file_type: file_type,
        is_delete: is_delete,
        delete_type: delete_type
    }
    let url = server + '/folder/delete';
    if (delete_type === 3){
        url = server + '/share/delete';
    }
    $.ajax({
        type: 'POST',
        url: url,
        async: false,
        data: JSON.stringify(post_data),
        contentType: 'application/json',
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                if (delete_type === 3) {
                    apps.explorer.share_list();
                }
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function rename_selected() {
    let ids = getSelectedIds();
    if (ids.folder.length + ids.file.length === 1) {
        let file_id = '';
        if (ids.folder.length > 0) {
            file_id = ids.folder[0];
        } else {
            file_id = ids.file[0];
        }
        apps.explorer.rename(file_id);
    } else {
        $.Toast(i18next.t('msg.rename.file.error1'), "error");
    }
}

function copy_selected() {
    let ids = getSelectedIds();
    if (ids.folder.length > 0) {
        $.Toast(i18next.t('msg.copy.file.error1'), "error");
        return;
    }
    if (ids.file.length === 0) {
        $.Toast(i18next.t('msg.copy.file.error2'), "error");
        return;
    }
    if (ids.file.length > 1) {
        $.Toast(i18next.t('msg.copy.file.error3'), "error");
        return;
    }
    apps.explorer.copy(ids.file[0]);
}

function delete_selected(del_type = 1, is_delete= 1, delete_type = 0) {
    if (delete_type === 1 || delete_type === 3) {
        show_modal_cover();
    }
    let ids = getSelectedIds();
    if (delete_type === 2) {
        ids = getSelectedIds(true);
    }
    if (ids.folder.length + ids.file.length === 0) {
        $.Toast(i18next.t('msg.export.file.error1'), "error");
        close_modal_cover();
        return;
    }
    if (ids.folder.length > 0) {
        delete_file(ids.folder, 'folder', is_delete, delete_type);
    }
    if (ids.file.length > 0) {
        delete_file(ids.file, 'file', is_delete, delete_type);
    }
    if (del_type === 0) {
        apps.explorer.garbage();
    } else {
        apps.explorer.goto($('#win-explorer>.path>.tit')[0].dataset.path, $('#win-explorer>.path>.tit')[0].id);
    }
    if (delete_type === 1 || delete_type === 3) {
        close_modal_cover();
    }
}

document.getElementById('search-file').addEventListener("keyup", function (event) {
    if (event.key === "Enter") {
        let q = this.value;
        let sort_field = 'update_time';
        let sort_type = 'desc';
        if (q.trim() !== "") {
            document.querySelectorAll('#win-explorer>.page>.main>.content>.header>.row>span>button').forEach(item => {
                if (item.className) {
                    sort_field = item.id.split('-')[0];
                    sort_type = item.className;
                }
            })
            let tmp = queryAllFiles("search", q.trim(), sort_field, sort_type);
            if (tmp.length === 0) {
                $('#win-explorer>.page>.main>.content>.header')[0].style.display = 'none';
                $('#win-explorer>.page>.main>.content>.view')[0].innerHTML = '<p class="info">搜索结果为空。</p>';
            } else {
                let ht = '';
                if ($('.list_view>img')[0].src.indexOf("list_view.svg") > 0) {
                    $('#win-explorer>.page>.main>.content>.header')[0].style.display = 'none';
                    $('#win-explorer>.page>.main>.content>.view').addClass("icon-view");
                    for (let i = 0; i < tmp.length; i++) {
                        if (tmp[i]['folder_type'] === 'folder') {
                            ht += `<div class="row" title="${tmp[i]['name']}"><input type="checkbox" id="check${tmp[i]['id']}"><a class="a files" style="padding-left:0;" id="f${tmp[i]['id']}" onclick="apps.explorer.select('${tmp[i]['id']}');" ondblclick="apps.explorer.goto('${path}/${tmp[i]['name']}', '${path_id}/${tmp[i]['id']}')"><img src="img/explorer/folder.svg" alt="default" loading="lazy"><div>${tmp[i]['name']}</div></a></div>`;
                        } else {
                            let f_src = icons[tmp[i]['format']] || default_icon;
                            switch (tmp[i]['format']) {
                                case 'jpg':
                                case 'jpeg':
                                case 'png':
                                case 'bmp':
                                case 'gif':
                                    f_src = server + "/file/download/" + tmp[i]['id'];
                                    break;
                            }
                            ht += `<div class="row" title="${tmp[i]['name']}"><input type="checkbox" id="check${tmp[i]['id']}"><a class="a act file" style="padding-left:0;" id="f${tmp[i]['id']}" onclick="apps.explorer.select('${tmp[i]['id']}');" ondblclick="apps.explorer.open_file('${tmp[i]['id']}', '${tmp[i]['name']}')"><img src="${f_src}" alt="default" loading="lazy"><div>${tmp[i]['name']}</div></a></div>`;
                        }
                    }
                } else {
                    $('#win-explorer>.page>.main>.content>.header')[0].style.display = 'flex';
                    $('#win-explorer>.page>.main>.content>.view').removeClass("icon-view");
                    for (let i = 0; i < tmp.length; i++) {
                        if (tmp[i]['folder_type'] === 'folder') {
                            ht += `<div class="row" style="padding-left: 5px;"><input type="checkbox" id="check${tmp[i]['id']}" style="float: left; margin-top: 8px;margin-right: 8px;"><a class="a item files" id="f${tmp[i]['id']}" onclick="apps.explorer.select('${tmp[i]['id']}');" ondblclick="apps.explorer.goto('${tmp[i]['name']}', '${tmp[i]['id']}')" oncontextmenu="showcm(event,'search.folder',['${tmp[i]['name']}', '${tmp[i]['id']}']);return stop(event);">
                            <span style="width: 40%;"><img style="float: left;" src="img/explorer/folder.svg" alt="folder.svg" loading="lazy">${tmp[i]['name']}</span><span style="width: 10%;">${i18next.t('explore.window.file.list.folder.type.name')}</span>
                            <span style="width: 10%;"></span><span style="width: 20%;">${tmp[i]['update_time']}</span><span style="width: 20%;">${tmp[i]['create_time']}</span></a></div>`;
                        } else {
                            let f_src = icons[tmp[i]['format']] || default_icon;
                            ht += `<div class="row" style="padding-left: 5px;"><input type="checkbox" id="check${tmp[i]['id']}" style="float: left; margin-top: 8px;margin-right: 8px;"><a class="a item act file" id="f${tmp[i]['id']}" onclick="apps.explorer.select('${tmp[i]['id']}');" ondblclick="apps.explorer.open_file('${tmp[i]['id']}', '${tmp[i]['name']}')" oncontextmenu="showcm(event,'search.file','${tmp[i]['id']}');return stop(event);">
                            <span style="width: 40%;"><img style="float: left;" src="${f_src}" alt="file" loading="lazy">${tmp[i]['name']}</span><span style="width: 10%;">${tmp[i]['format']}</span>
                            <span style="width: 10%;">${tmp[i]['size']}</span><span style="width: 20%;">${tmp[i]['update_time']}</span><span style="width: 20%;">${tmp[i]['create_time']}</span></a></div>`;
                        }
                    }
                }
                $('#win-explorer>.page>.main>.content>.view')[0].innerHTML = ht;
                document.querySelectorAll('.a.item').forEach(item => {
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
                            item.ondblclick(e);
                        }
                    }, false);
                })
            }
        } else {
            $.Toast(i18next.t('msg.search.file.error1'), "error");
        }
    }
})

function move_files() {
    let root_disk = '';
    let ids = getSelectedIds();
    if (ids.folder.length + ids.file.length === 0) {
        $.Toast(i18next.t('msg.export.file.error1'), "error");
        return;
    }
    $.get(server + '/folder/getDisk').then(res => {
        res.data.forEach(c => {
            root_disk = root_disk + `<ul class="domtree"><li onclick="get_folders('move${c['disk']}')"><img src="img/explorer/disk.svg" alt="disk.svg" loading="lazy">${c['disk']}:</li><ul id="move${c['disk']}"></ul></ul>`;
        });
        $('#notice>.cnt').html(`
                <p class="tit">${i18next.t('explore.window.file.tool.move.window.title')}</p>
                <div><input id="folder_name" type="text" value="" name="520" readonly></div>
                <div><label>${i18next.t('explore.window.file.tool.move.window.label')}</label><div id="folder-tree" style="overflow-y: scroll;">${root_disk}</div></div>
        `);
        $('#notice>.btns').html(`<a class="a btn main" onclick="move_file_folder();">${i18next.t('submit')}</a><a class="a btn detail" onclick="closenotice();">${i18next.t('cancel')}</a>`);
        $('#notice-back').addClass('show');
        $('#notice')[0].style.width = '50%';
        $('#notice')[0].style.height = $('#notice-back')[0].clientHeight * 0.8 + 'px';
        $('#folder-tree')[0].style.height = $('#notice-back')[0].clientHeight * 0.8 - 207 + 'px';
    });
}

function add_server_window() {
    $('#notice>.cnt').html(`
            <p class="tit">${i18next.t('setting.window.shell.server.add')}</p>
            <div style="margin-top:2%;"><label style="width:80px;display:inline-flex;margin-left:2%;">${i18next.t('setting.window.shell.server.add.ip.label')}</label><input id="server-host" type="text" placeholder="${i18next.t('setting.window.shell.server.add.ip.placeholder')}" style="width:80%;height:39px;"></div>
            <div style="margin-top:2%;"><label style="width:80px;display:inline-flex;margin-left:2%;">${i18next.t('setting.window.shell.server.add.user.label')}</label><input id="server-user" type="text" placeholder="${i18next.t('setting.window.shell.server.add.user.placeholder')}" value="root" style="width:80%;height:39px;"></div>
            <div style="margin-top:2%;"><label style="width:80px;display:inline-flex;margin-left:2%;">${i18next.t('setting.window.shell.server.add.port.label')}</label><input id="server-port" type="text" placeholder="${i18next.t('setting.window.shell.server.add.port.placeholder')}" value="22" style="width:80%;height:39px;"></div>
            <div style="margin-top:2%;"><label style="width:80px;display:inline-flex;margin-left:2%;">${i18next.t('setting.window.shell.server.add.pwd.label')}</label><input id="server-pwd" type="password" autocomplete="off" placeholder="${i18next.t('setting.window.shell.server.add.pwd.placeholder')}" style="width:80%;height:39px;"></div>
    `);
    $('#notice>.btns').html(`<a class="a btn main" onclick="add_server();">${i18next.t('submit')}</a><a class="a btn detail" onclick="closenotice();">${i18next.t('cancel')}</a>`);
    $('#notice-back').addClass('show');
    $('#notice')[0].style.width = '50%';
}

function move_file_folder() {
    show_modal_cover();
    let ids = getSelectedIds();
    let path_id = $('#win-explorer>.path>.tit')[0].id.split('/');
    let to_id = document.getElementById('folder_name').name;
    let move_flag = 0;
    if (ids.folder.length > 0) {
        move_flag = move_to(ids.folder, path_id[path_id.length - 1], to_id.slice(4, to_id.length), 'folder');
    }
    if (ids.file.length > 0) {
        move_flag = move_to(ids.file, path_id[path_id.length - 1], to_id.slice(4, to_id.length), 'file');
    }
    if (move_flag !== 0) {
        apps.explorer.goto($('#win-explorer>.path>.tit')[0].dataset.path, $('#win-explorer>.path>.tit')[0].id);
    }
    close_modal_cover();
}

function move_to(from_ids, parent_id, to_id, folder_type) {
    if (parent_id === to_id) {
        $.Toast(i18next.t('msg.move.file.error1'), "error");
        return 0;
    }
    let url = server + '/file/move';
    if (folder_type === 'folder') {
        url = server + '/folder/move';
    }
    let post_data = {
        from_ids: from_ids,
        parent_id: parent_id,
        to_id: to_id
    }
    $.ajax({
        type: 'POST',
        url: url,
        async: false,
        data: JSON.stringify(post_data),
        contentType: 'application/json',
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                closenotice();
                return 1;
            } else {
                $.Toast(data['msg'], 'error');
                return 0;
            }
        }
    })
}

function get_folders(folder_id) {
    let abs_path = folder_id.slice(4, folder_id.length);
    $.ajax({
        type: "GET",
        url: server + "/folder/get/" + abs_path,
        success: function (data) {
            if (data['code'] === 0) {
                let s = '';
                data['data']['folder'].forEach(item => {
                    s = s + `<li onclick="get_folders('move${item['id']}')"><img src="img/explorer/folder.svg" alt="folder.svg" loading="lazy">${item['name']}</li><ul id="move${item['id']}"></ul>`;
                })
                document.getElementById(folder_id).innerHTML = s;
                let folder_name = document.getElementById('folder_name');
                folder_name.value = data['data']['path'];
                folder_name.name = folder_id;
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

document.getElementById("all_files").addEventListener("click", function () {
    let items = document.querySelectorAll('#win-explorer>.page>.main>.content>.view>.row');
    for (let i=0; i<items.length; i++) {
        items[i].getElementsByTagName('input')[0].checked = this.checked;
    }
})

document.getElementById("id-sort").addEventListener("click", function () {
    change_asc_desc(this);
    apps.explorer.goto($('#win-explorer>.path>.tit')[0].dataset.path, $('#win-explorer>.path>.tit')[0].id);
})

document.getElementById("name-sort").addEventListener("click", function () {
    change_asc_desc(this);
    apps.explorer.goto($('#win-explorer>.path>.tit')[0].dataset.path, $('#win-explorer>.path>.tit')[0].id);
})

document.getElementById("update_time-sort").addEventListener("click", function () {
    change_asc_desc(this);
    apps.explorer.goto($('#win-explorer>.path>.tit')[0].dataset.path, $('#win-explorer>.path>.tit')[0].id);
})

function queryAllFiles(parent_id, q="", sort_field='update_time', sort_type='desc') {
    let res = [];
    let url = server + '/file/get/' + parent_id + '?q=' + q + '&sort_field=' + sort_field + '&sort_type=' + sort_type;
    $.ajax({
        type: "GET",
        url: url,
        async: false,
        success: function (data) {
            if (data['code'] === 0) {
                res = data['data'];
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
    return res;
}

function change_asc_desc(element) {
    if (element.className) {
        if (element.className === 'asc') {
            element.className= 'desc';
        } else if (element.className === 'desc') {
            element.className= 'asc';
        }
    } else {
        element.className= 'desc';
    }
    let button_sort = document.querySelectorAll('#win-explorer>.page>.main>.content>.header>.row>span>button');
    button_sort.forEach(item => {
        if (item.id !== element.id) {
            item.className = '';
        }
    })
}

function export_file(ids, file_type) {
    show_modal_cover();
    let post_data = {
        ids: ids,
        file_type: file_type
    }
    $.ajax({
        type: 'POST',
        url: server + '/file/export',
        data: JSON.stringify(post_data),
        contentType: 'application/json',
        success: function (data) {
            if (data['code'] === 0) {
                apps.explorer.goto($('#win-explorer>.path>.tit')[0].dataset.path, $('#win-explorer>.path>.tit')[0].id);
                close_modal_cover();
                apps.explorer.download(data['data']);
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function upload_file() {
    let fileUpload_input = document.getElementById("fileUpload-input");
    let folder_ids = $('#win-explorer>.path>.tit')[0].id;
    let folder_id = folder_ids.split('/');
    fileUpload_input.click();
    fileUpload_input.onchange = function (event) {
        let progressBar = document.getElementById("progressBar");
        show_modal_cover(false, true);
        let files = event.target.files;
        let total_files = files.length;
        if (total_files < 1) {
            close_modal_cover();
            return;
        }
        let success_num = 0;
        let fast_upload_num = 0;
        let failure_num = 0;
        let failure_file = [];
        progressBar.max = total_files;
        progressBar.value = success_num;

        for (let i=0; i<total_files; i++) {
            let form_data = new FormData();
            form_data.append("file", files[i]);
            form_data.append("index", i + 1);
            form_data.append("total", total_files);
            form_data.append("parent_id", folder_id[folder_id.length - 1]);

            let xhr = new XMLHttpRequest();
            xhr.open("POST", server + "/file/upload");
            xhr.setRequestHeader("processData", "false");
            xhr.setRequestHeader("lang", localStorage.getItem('lang'));
            // xhr.upload.onprogress = function(event) {
            //     if (event.lengthComputable) {}};
            // xhr.onload = function(event) {}
            xhr.onreadystatechange = function() {
                progressBar.value = success_num;
                if (xhr.readyState === 4) {
                    if(xhr.status === 200) {
                        let res = JSON.parse(xhr.responseText);
                        if (res['code'] === 0) {
                            success_num += 1;
                        } else if (res['code'] === 2) {
                            fast_upload_num += 1;
                        } else {
                            failure_num += 1;
                            failure_file.push(res['data']);
                        }
                    }
                    if ((success_num + fast_upload_num + failure_num) === total_files) {
                        let msg = "";
                        let level = "success";
                        if (success_num > 0) {
                            msg += success_num + i18next.t('upload.file.success.tips');
                        }
                        if (fast_upload_num > 0) {
                            if (msg.length > 0) {msg += '，';}
                            msg += fast_upload_num + i18next.t('upload.file.already.tips');
                            level = "warning";
                        }
                        if (failure_num > 0) {
                            if (msg.length > 0) {msg += '，';}
                            msg += failure_num + i18next.t('upload.file.failure.tips');
                            level = "error";
                        }
                        $.Toast(msg, level);
                        if (failure_num > 0) {
                            shownotice('uploadResult');
                            let s = "";
                            for (let i=0; i<failure_file.length; i++) {
                                s += "<p>" + failure_file[i] + "</p>";
                            }
                            $('.upload-result')[0].innerHTML = s;
                        }
                        fileUpload_input.value = '';
                        apps.explorer.goto($('#win-explorer>.path>.tit')[0].dataset.path, $('#win-explorer>.path>.tit')[0].id);
                        close_modal_cover();
                    }
                }
            }
            xhr.send(form_data);
        }
    }
}

function upload_back_img(img_type) {
    let fileUpload_input = document.getElementById("back-img-input");
    fileUpload_input.click();
    fileUpload_input.onchange = function (event) {
        show_modal_cover();
        let files = event.target.files;
        let total_files = files.length;
        for (let i=0; i<total_files; i++) {
            let form_data = new FormData();
            form_data.append("file", files[i]);
            form_data.append("imgType", img_type);
            let file_type = files[i].type;
            if (file_type.indexOf('jpg') === -1 && file_type.indexOf('jpeg') === -1) {
                $.Toast(i18next.t('msg.upload.file.image.error1'), "error");
                return;
            }
            let xhr = new XMLHttpRequest();
            xhr.open("POST", server + "/file/uploadImage");
            xhr.setRequestHeader("processData", "false");
            xhr.setRequestHeader("lang", localStorage.getItem('lang'));
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if(xhr.status === 200) {
                        let res = JSON.parse(xhr.responseText);
                        if (res['code'] === 0) {
                            $.Toast(res['msg'], 'success');
                            if (img_type === 1) {
                                document.body.style.backgroundImage='url("img/pictures/' + document.cookie.split('u=')[1].split(';')[0] + '/background.jpg")';
                            }
                        } else {
                            $.Toast(res['msg'], 'error');
                        }
                    }
                    fileUpload_input.value = '';
                    close_modal_cover();
                }
            }
            xhr.send(form_data);
        }
    }
}

function play_local_video() {
    let play_local_video = document.getElementById("play_local_video");
    play_local_video.click();
    play_local_video.onchange = function (event) {
        let files = event.target.files;
        if (files.length !== 1) {
            return null;
        }
        openapp('video');
        $('.window.video')[0].style.width = 'auto';
        $('.window.video>.titbar>span>.title')[0].innerText = files[0].name;
        $('#win-video')[0].innerHTML = '<video class="my_video" controls preload="metadata" data-setup="{}" playsinline><source src="" type="video/mp4"><track src="" srcLang="'+lang+'" kind="subtitles" label="'+lang+'"></video>';
        let local_video = document.getElementsByClassName('my_video')[0];
        local_video.src = URL.createObjectURL(files[0]);
        local_video.load();
        let name_md5 = md5(files[0].name);
        local_video.addEventListener('loadedmetadata', function () {
            this.currentTime = localStorage.getItem(name_md5);
        }, false);
        local_video.addEventListener('timeupdate', function (){
            if (this.currentTime > 0) {localStorage.setItem(name_md5, this.currentTime);}
        }, false);
        local_video.addEventListener('ended', function () {
            localStorage.removeItem(name_md5);
        }, false);
    }
    play_local_video.value = '';
}

function modify_pwd() {
    let pwd1 = $('#setting-pwd1')[0].value;
    let pwd2 = $('#setting-pwd2')[0].value;
    let c = new Date().getTime().toString();
    if (!pwd1) {
        $.Toast(i18next.t('msg.modify.password.error2'), "error");
        return;
    }
    if (pwd1 !== pwd2) {
        $.Toast(i18next.t('msg.modify.password.error1'), "error");
        return;
    }
    let post_data = {
        t: c,
        username: document.cookie.split('u=')[1].split(';')[0],
        password: parse_pwd(pwd1, c),
        password1: parse_pwd(pwd2, c)
    }
    $.ajax({
        type: 'POST',
        url: server + '/user/modify/pwd',
        data: JSON.stringify(post_data),
        contentType: 'application/json',
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function modify_nickname() {
    let nickname = $('#setting-nickname')[0].value.trim();
    if (!nickname) {
        $.Toast(i18next.t('msg.modify.nickname.error'), "error");
        return;
    }
    $.ajax({
        type: 'GET',
        url: server + '/user/modify/nickname/' + nickname,
        success: function (data) {
            if (data['code'] === 0) {
                nickName = data['data'];
                $.Toast(data['msg'], 'success');
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function clear_tmp_path() {
    $.ajax({
        type: "GET",
        url: server + '/system/clean/temporary/files',
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function close_video() {$('.my_video').attr('src', '');}

let txt_interval = null;
function edit_text_file(file_id) {
    clearInterval(txt_interval);
    openapp('notepad');
    $.ajax({
        type: 'GET',
        url: server + '/file/content/' + file_id,
        success: function (data) {
            if (data['code'] === 0) {
                $('.window.notepad>.titbar>span>.title')[0].innerText = data['msg'];
                $('#win-notepad>.text-box')[0].innerText = data['data'];
                $('#win-notepad>.text-box')[0].id = file_id;
                $('#win-notepad>a')[0].download = data['msg'].replace('txt', 'html');
                $('.window.notepad>.titbar>div>.wbtg.red').attr("onclick", `close_text_editor('${file_id}');hidewin('notepad');`);
                $('#notepad-length')[0].value = data['data'].length;
                txt_interval = window.setInterval(() => {
                    let text_data = $('#win-notepad>.text-box')[0].innerText;
                    let text_length = $('#notepad-length')[0].value;
                    if (text_data.length !== parseInt(text_length)) {
                        $('.window.notepad>.titbar>span>.save-status')[0].innerText = i18next.t('edit.online.saving.tips');
                        save_text_file(file_id, text_data);
                        $('#notepad-length')[0].value = text_data.length;
                        $('.window.notepad>.titbar>span>.save-status')[0].innerText = get_current_time() + i18next.t('edit.online.saved.tips');
                    }
                }, 10000);
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function close_text_editor(file_id) {
    clearInterval(txt_interval);
    $('.window.notepad>.titbar>span>.save-status')[0].innerText = i18next.t('edit.online.saving.tips');
    let text_data = $('#win-notepad>.text-box')[0].innerText;
    let text_length = $('#notepad-length')[0].value;
    if (text_data.length !== parseInt(text_length)) {
        save_text_file(file_id, text_data);
    }
    $('.window.notepad>.titbar>span>.save-status')[0].innerText = "";
    $('#win-notepad>.text-box')[0].innerText='';
}

function save_text_file(file_id, data, is_code=true) {
    let post_data = {id: file_id, data: data};
    $.ajax({
        type: 'POST',
        url: server + '/file/save',
        data: JSON.stringify(post_data),
        contentType: 'application/json',
        success: function (data) {
            if (data['code'] !== 0) {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function create_meeting_code(chat_mode) {
    $.ajax({
        type: "GET",
        url: server + '/chat/create/' + chat_mode,
        success: function (data) {
            if (data['code'] === 0) {
                document.getElementById("meeting-code-" + chat_mode).value = data['data'];
                $.Toast(data['msg'], 'success');
            }
        }
    })
}

function join_meeting(chat_mode) {
    let code = document.getElementById("meeting-code-" + chat_mode).value.trim();
    if (!code || code === "") {
        $.Toast(i18next.t("chat.code.placeholder"), "error");
        return;
    }
    $.ajax({
        type: "GET",
        url: server + '/chat/auth/' + chat_mode + '/' + code,
        success: function (data) {
            if (data['code'] === 0) {
                openapp('chat');
                $('.window.chat>.titbar>span>.title')[0].innerText = i18next.t('chat.title');
                let html_str = 'chat';
                if (chat_mode === 0) {
                    html_str = 'voice';
                    $('.window.chat>.titbar>span>.title')[0].innerText = i18next.t('chat.voice.title');
                }
                document.getElementsByClassName("chat")[0].style.display = 'block';
                document.getElementById("iframe_chat").src = 'module/' + html_str + '.html?server=' + server + '&code=' + code + chat_mode;
                $('.window.chat>.titbar>div>.wbtg.red').attr("onclick", `document.getElementById("iframe_chat").src='about:blank';hidewin('chat');`);
            } else {
                $.Toast(data['msg'], 'error');
                return;
            }
        }
    })
}

function open_torrent(file_id) {
    show_modal_cover(true, false);
    $.ajax({
        type: 'GET',
        url: server + '/download/torrent/open/' + file_id,
        success: function (data) {
            if (data['code'] === 0) {
                shownotice("selectedFiles");
                let ht = "";
                data['data'].forEach(item => {
                    ht += `<div style="margin: 8px 0 8px 0;display: flex;flex-direction: row;justify-content: space-between;flex-wrap: nowrap;"><div style="width:80%;"><input name="options" type="radio" value="${item['gid']},${item['index']},${item['folder']}" id="${item['index']}"><span style="margin-left:5px;">${item['name']}</span></div><span>${item['size']}</span></div>`;
                })
                $('#notice>.cnt>p')[0].innerText = i18next.t('explore.window.file.tool.downloader.window.selected');
                document.getElementById("selected-file").innerHTML = ht;
                $('#notice>.btns>.detail').attr("onclick", `update_download_status('${data['data'][0]['gid']}', 'cancel,remove', false);closenotice();`);
            } else {
                $.Toast(data['msg'], 'error');
            }
            close_modal_cover();
        }
    })
}

function open_music(file_id) {
    $('.window.music>.titbar>span>.title')[0].innerText = i18next.t('music');
    openapp('music');
    document.getElementsByClassName("music")[0].style.display = 'block';
    document.getElementById("iframe_music").src = 'module/music.html?server=' + server + '&id=' + file_id;
    $('.window.music>.titbar>div>.wbtg.red').attr("onclick", `document.getElementById("iframe_music").src = 'about:blank';hidewin('music');`);
}

function open_karaoke() {
    $('.window.karaoke>.titbar>span>.title')[0].innerText = i18next.t('karaoke');
    openapp('karaoke');
    document.getElementsByClassName("karaoke")[0].style.display = 'block';
    document.getElementById("iframe_karaoke").src = 'module/karaoke/index.html?server=' + server;
    $('.window.karaoke>.titbar>div>.wbtg.red').attr("onclick", `document.getElementById("iframe_karaoke").src = 'about:blank';hidewin('karaoke');`);
}

function open_md(file_id) {
    openapp('markdown');
    document.getElementsByClassName("markdown")[0].style.display = 'block';
    document.getElementById("iframe_markdown").src = 'module/md.html?server=' + server + '&id=' + file_id;
    $('.window.markdown>.titbar>div>.wbtg.red').attr("onclick", `document.getElementById("iframe_markdown").contentWindow.close_md_editor('${file_id}');hidewin('markdown');`);
    $('.window.markdown>.titbar>div>.wbtg.export').attr("onclick", `window.open('${server}/file/export/md/${file_id}')`);
}

function open_xmind(file_id) {
    openapp('xmind');
    document.getElementsByClassName("xmind")[0].style.display = 'block';
    document.getElementById("iframe_xmind").src = 'module/xmind.html?server=' + server + '&id=' + file_id;
    $('.window.xmind>.titbar>div>.wbtg.red').attr("onclick", `document.getElementById("iframe_xmind").contentWindow.close_xmind_editor('${file_id}');hidewin('xmind');`);
}

function open_sheet(file_id) {
    openapp('sheet');
    document.getElementsByClassName("sheet")[0].style.display = 'block';
    document.getElementById("iframe_sheet").src = 'module/sheet.html?server=' + server + '&id=' + file_id + '&lang=' + lang;
    $('.window.sheet>.titbar>div>.wbtg.red').attr("onclick", `document.getElementById("iframe_sheet").contentWindow.close_sheet_editor('${file_id}');hidewin('sheet');`);
}

function open_office(file_id, name) {
    openapp(name);
    document.getElementsByClassName(name)[0].style.display = 'block';
    document.getElementById("iframe_" + name).src = 'module/onlyoffice.html?server=' + server + '&id=' + file_id + '&lang=' + lang;
    $('.window.'+name+'>.titbar>div>.wbtg.red').attr("onclick", `document.getElementById("iframe_${name}").src = 'about:blank';hidewin('${name}');`);
    $('.window.' + name + '>.titbar')[0].style.width = Number($('.window.' + name).css('width').split('px')[0]) - onlyoffice_width[name] + 'px';
}

function open_system_resource(name) {
    openapp(name);
    document.getElementById("iframe_" + name).src = 'module/systemResource/index.html?server=' + server + '&lang=' + lang;
    $('.window.taskmgr').css('height', 480);
    $('.window.taskmgr>.titbar>div>.wbtg.red').attr("onclick", `document.getElementById("iframe_taskmgr").src = 'about:blank';hidewin('taskmgr');`);
}

function open_python(file_id) {
    openapp('pythonEditor');
    document.getElementsByClassName("pythonEditor")[0].style.display = 'block';
    document.getElementById("iframe_pythonEditor").src = 'module/python.html?server=' + server + '&id=' + file_id;
    $('.window.pythonEditor>.titbar>div>.wbtg.red').attr("onclick", `document.getElementById("iframe_pythonEditor").contentWindow.close_python_editor('${file_id}');hidewin('pythonEditor');`);
}

function open_document(file_id, file_name) {
    openapp('docu');
    document.getElementsByClassName("docu")[0].style.display = 'block';
    document.getElementById("iframe_docu").src = 'module/document.html?server=' + server + '&id=' + file_id + '&lang=' + lang;
    $('.window.docu>.titbar>div>.wbtg.red').attr("onclick", `document.getElementById("iframe_docu").contentWindow.close_document_editor('${file_id}');hidewin('docu');`);
    $('#win-docu>a')[0].download = file_name.replace('docu', 'html');
}

function open_game(game_type) {
    $('.window.game>.titbar>span>span')[0].innerText = i18next.t('setting.window.game');
    openapp('game');
    $('.window.game>.titbar>img').attr('src', 'img/setting/'+ game_type +'.svg')
    document.getElementsByClassName("game")[0].style.display = 'block';
    let width = 0;
    let height = 0;
    switch (game_type) {
        case 'snake':
            width = 700;
            height = 650;
            break;
        case 'tetris':
            width = 430;
            height = 558;
            break;
        case 'rings':
            width = 420;
            height = 800;
            break;
        default:
            width = 0;
            height = 0;
            break;
    }
    $('.window.game')[0].style.width = width + 'px';
    $('.window.game')[0].style.height = height + 'px';
    $('.window.game')[0].style.left = (document.body.clientWidth - width) / 2 + 'px';
    $('.window.game')[0].style.top = (document.body.clientHeight - height - 50) / 2 + 'px';
    document.getElementById("iframe_game").src = 'module/' + game_type +'/index.html?server=' + server;
    $('.window.game>.titbar>div>.wbtg.red').attr("onclick", `document.getElementById("iframe_game").src = 'about:blank';hidewin('game');`);
}

function get_server_list(event) {
    if ($('.dp.app-color.server')[0].classList.contains('show')) {
        $('.dp.app-color.server').toggleClass('show');
        return;
    }
    $.ajax({
        type: 'GET',
        url: server + '/server/get',
        success: function (data) {
            if (data['code'] === 0) {
                let s = '';
                data['data'].forEach(item => {
                    s += `<div><div style="width: 16%;">${item['host']}</div><div>${item['port']}</div><div>${item['user']}</div><div style="width: 21%;">${item['system']}</div><div>${item['cpu']}${i18next.t('setting.window.shell.server.list.cpu.core')}</div><div>${item['mem']}G</div><div>${item['disk']}</div><div style="width:15%;"><a href="module/terminal.html?id=${item['id']}&host=${item['host']}&lang=${lang}" style="color:blue;">${i18next.t('setting.window.shell.server.list.action.open')}</a><a href="javascript:void(0);" onclick="delete_server(${item['id']});return false;" style="color:blue;margin-left:15px;">${i18next.t('setting.window.shell.server.list.action.delete')}</a></div></div><br />`;
                })
                $('.server-item')[0].innerHTML = s;
                $('.dp.app-color.server').toggleClass('show');
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function add_server() {
    let c = new Date().getTime().toString();
    if (!$('#server-host')[0].value || !$('#server-pwd')[0].value) {
        $.Toast(i18next.t('msg.server.add.error1'), "error");
        return;
    }
    let post_data = {
        t: c,
        host: $('#server-host')[0].value,
        port: $('#server-port')[0].value,
        user: $('#server-user')[0].value,
        pwd: parse_pwd($('#server-pwd')[0].value, c)
    }
    show_modal_cover();
    $.ajax({
        type: 'POST',
        url: server + '/server/add',
        data: JSON.stringify(post_data),
        contentType: 'application/json',
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                closenotice();
            } else {
                $.Toast(data['msg'], 'error');
            }
            close_modal_cover();
        }
    })
}

function delete_server(host_id) {
    $.ajax({
        type: 'GET',
        url: server + '/server/delete/' + host_id,
        success: function (data) {
            if (data['code'] === 0) {
                get_server_list(null);
                $.Toast(data['msg'], 'success');
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function update_download_status(gid, action, flag=true) {
    let post_data = {gid: gid, status: action}
    $.ajax({
        type: 'POST',
        url: server + '/download/status/update',
        data: JSON.stringify(post_data),
        contentType: 'application/json',
        success: function (data) {
            if (data['code'] === 0) {
                if (flag) {
                    $.Toast(data['msg'], 'success');
                    apps.explorer.download_list();
                }
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function get_system_info(event) {
    if ($('.dp.app-color.about')[0].classList.contains('show')) {
        $('.dp.app-color.about').toggleClass('show');
        return;
    }
    $.ajax({
        type: 'GET',
        url: server + '/system/detail',
        success: function (data) {
            if (data['code'] === 0) {
                $('.system>.setting-list>.about>div:nth-child(1)>span')[1].innerText = `${data.data.os_name}`;
                $('.system>.setting-list>.about>div:nth-child(2)>span')[1].innerText = `${data.data.os_version}`;
                $('.system>.setting-list>.about>div:nth-child(3)>span')[1].innerText = `${data.data.os_arch}${i18next.t("setting.window.system.about.system.type.bits")}${data.data.machine}${i18next.t("setting.window.system.about.system.type.cpu")}`;
                $('.system>.setting-list>.about>div:nth-child(4)>span')[1].innerText = `${data.data.cpu_model}`;
                $('.system>.setting-list>.about>div:nth-child(5)>span')[1].innerText = `${data.data.cpu_core} ${i18next.t("setting.window.system.about.system.cpu.core.num")}`;
                $('.system>.setting-list>.about>div:nth-child(6)>span')[1].innerText = `${data.data.memory} GB`;
                $('.system>.setting-list>.about>div:nth-child(7)>span')[1].innerText = `${data.data.disk}`;
                $('.system>.setting-list>.about>div:nth-child(8)>span')[1].innerText = `${data.data.run_time}`;
                $('.dp.app-color.about').toggleClass('show');
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}
