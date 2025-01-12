const server = '/mycloud';
localStorage.setItem('server', server);
if (!localStorage.getItem('username')) {
    localStorage.setItem('username', 'undefined');
}
let nickName = '';
function change_language(flag) {
    if (flag === 0){
        lang = $('#loginback>div>select')[0].value;
    } else {
        lang = $('#win-setting>.page>.appearance>.setting-list>a>.languageSelect')[0].value;
    }
    localStorage.setItem('lang', lang);
    fetch(`language/${lang}.json`)
        .then(response => response.json())
        .then(data => {
            i18next.addResourceBundle(lang, 'translation', data, true);
            i18next.changeLanguage(lang, function (){window.location.reload();})
    });
}
function get_status() {
    $.ajax({
        type: 'GET',
        async: false,
        url: server + '/user/status',
        success: function (data) {
            if (data['code'] === 0) {
                nickName = data['data'];
                $('#loginback').css('opacity', '0');
                $('#loginback').css('display', 'none');
                $('#dock-box').css('display', 'flex');
                $('#desktop').css('display', 'flex');
                document.body.style.backgroundImage = `url("img/pictures/${localStorage.getItem("username")}/background.jpg")`;
            } else {
                $('#loginback').css('opacity', '1');
                $('#loginback').css('display', 'flex');
                $('#dock-box').css('display', 'none');
                $('#desktop').css('display', 'none');
                document.getElementById('loginback').style.backgroundImage = `url("img/pictures/${localStorage.getItem("username")}/login.jpg")`;
            }
        },
        error: function (xhr, status, msg) {
            console.error(msg);
            $('#loginback').css('opacity', '1');
            $('#loginback').css('display', 'flex');
            $('#dock-box').css('display', 'none');
            $('#desktop').css('display', 'none');
            document.getElementById('loginback').style.backgroundImage = `url("img/pictures/${localStorage.getItem("username")}/login.jpg")`;
        }
    })
}
