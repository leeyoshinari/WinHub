function login_sys(evn) {
    evn.id = 'login-after';
    evn.innerText = i18next.t('login.button.login.ing') + '...';
    let qwq = window.setInterval(() => {
        if (evn.innerText.match(/\.\.\./)) {
            evn.innerText = i18next.t('login.button.login.ing') + '.';
        } else {
            evn.innerText += '.';
        }
    }, 500);
    let c = new Date().getTime().toString();
    let post_data = {
        t: c,
        username: $('#username')[0].value,
        password: parse_pwd($('#password')[0].value, c)
    }
    $.ajax({
        type: 'POST',
        url: server + '/user/login',
        data: JSON.stringify(post_data),
        contentType: 'application/json',
        success: function (data) {
            if (data['code'] === 0) {
                nickName = data['data'];
                localStorage.setItem("username", $('#username')[0].value);
                window.location.reload();
            } else {
                $.Toast(data['msg'], 'error');
                window.clearInterval(qwq);
                evn.id = 'login';
                evn.innerText = i18next.t('login.button.text');
            }
        },
        error: function (error) {
            $.Toast(error, 'error');
            window.clearInterval(qwq);
            evn.id = 'login';
            evn.innerText = i18next.t('login.button.text');
        }
    })
}

function logout() {
    $.ajax({
        type: 'GET',
        url: server + '/user/logout',
        success: function (data) {
            if (data['code'] === 0) {
                window.location.reload();
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}
