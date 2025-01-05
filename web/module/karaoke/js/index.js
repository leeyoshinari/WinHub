const server = localStorage.getItem("server");
const lang = localStorage.getItem("lang");
let songListTimeout = null;
let history_type = "history";
let i18nList = document.getElementsByClassName('i18n');
for (let i=0; i<i18nList.length; i++) {i18nList[i].innerText = window.parent.i18next.t(i18nList[i].getAttribute('key'));}
i18nList = document.getElementsByClassName('i18n_p');
for (let i=0; i<i18nList.length; i++) {i18nList[i].placeholder = window.parent.i18next.t(i18nList[i].getAttribute('key'));}

document.getElementById("file-upload").addEventListener('click', () => {
    let fileUpload_input = document.getElementById("file-input");
    fileUpload_input.click();
    fileUpload_input.onchange = function (event) {
        show_modal_cover();
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

        for (let i=0; i<total_files; i++) {
            let form_data = new FormData();
            form_data.append("file", files[i]);
            form_data.append("index", (i + 1).toString());
            form_data.append("total", total_files.toString());

            let xhr = new XMLHttpRequest();
            xhr.open("POST", server + "/karaoke/upload");
            xhr.setRequestHeader("processData", "false");
            xhr.setRequestHeader("lang", localStorage.getItem('lang'));
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if(xhr.status === 200) {
                        let res = JSON.parse(xhr.responseText);
                        if (res['code'] === 0) {
                            success_num += 1;
                        } else {
                            failure_num += 1;
                            failure_file.push(res['data']);
                        }
                    }
                    if ((success_num + fast_upload_num + failure_num) === total_files) {
                        let msg = "";
                        let level = "success";
                        if (success_num > 0) {
                            msg += success_num + window.parent.i18next.t("upload.file.success.tips");
                        }
                        if (failure_num > 0) {
                            if (msg.length > 0) {msg += '，';}
                            msg += failure_num + window.parent.i18next.t("upload.file.failure.tips");
                            level = "error";
                        }
                        window.parent.$.Toast(msg, level);
                        if (failure_num > 0) {
                            let s = "";
                            for (let i=0; i<failure_file.length; i++) {
                                s += failure_file[i] + "，";
                            }
                            window.parent.$.Toast(s, 'error');
                        }
                        close_modal_cover();
                        get_song_list();
                    }
                }
                fileUpload_input.value = '';
            }
            xhr.send(form_data);
        }
    }
})

document.getElementById("file-search").addEventListener('input', () => {
    clearTimeout(songListTimeout);
    songListTimeout = setTimeout(() => {get_song_list();}, 500)
})

document.getElementById("generate_code").addEventListener('click', () => {
    let qrcodeEle = document.getElementsByClassName("qrcode")[0];
    let path_list = window.location.pathname.split('/');
    if (qrcodeEle.style.display !== "block") {
        let qrcode = new QRCode(document.getElementById("qrcode"), {
            text: window.location.protocol + "//" + window.location.host + window.location.pathname.replace(path_list[path_list.length - 1], 'client.html') + "?server=" + server + "&lang=" + lang,
            width: 200,
            height: 200,
            colorDark: "#000000",
            colorLight: "#ffffff",
            correctLevel: QRCode.CorrectLevel.H
        });
        qrcodeEle.style.display = "block";
    } else {
        qrcodeEle.style.display = "none";
        document.getElementById("qrcode").innerHTML = '';
    }
})

function get_song_list(page=1) {
    let q = document.getElementById("file-search").value;
    let params = "page=" + page;
    if (q && q !== "" && q !== null) {
        params = params + "&q=" + q;
    }
    window.parent.$.ajax({
        type: "GET",
        url: server + "/karaoke/list?" + params,
        success: function (data) {
            let s = '';
            if (data.code === 0) {
                if (data.total === 0) {
                    if (q && q !== "" && q !== null) {
                        return;
                    }
                    window.parent.$.Toast(window.parent.i18next.t("karaoke.no.song"), "error");
                    return;
                }
                data.data.forEach(item => {
                    s = s + `<tr><td>${item.name}</td><td>${item.create_time}</td>
                            <td><a onclick="sing_song(${item.id})">${window.parent.i18next.t("karaoke.add.song")}</a><a onclick="delete_song(${item.id})">${window.parent.i18next.t("setting.window.shell.server.list.action.delete")}</a></td></tr>`;
                })
                PagingManage(document.getElementById("paging"), data.total, page, window.parent.i18next.t("page.pre"), window.parent.i18next.t("page.next"));
                document.getElementsByTagName("table")[0].style.display = "";
                document.getElementById("create-time").style.display = "";
                document.getElementsByTagName("tbody")[0].innerHTML = s;
            } else {
                window.parent.$.Toast(data.msg, 'error');
            }
        }
    })
}

function get_history_list(queryType) {
    history_type = queryType;
    window.parent.$.ajax({
        type: "GET",
        url: server + "/karaoke/singHistory/" + queryType,
        success: function (data) {
            let s = '';
            if (data.code === 0) {
                if (data.total === 0) {
                    window.parent.$.Toast(window.parent.i18next.t("karaoke.no.song"), "error");
                    return;
                }
                data.data.forEach(item => {
                    s = s + `<tr><td>${item.name}</td><td><a onclick="sing_song(${item.id})">${window.parent.i18next.t("karaoke.add.song")}</a><a onclick="delete_from_list(${item.id})">${window.parent.i18next.t("setting.window.shell.server.list.action.delete")}</a></td></tr>`;
                })
                PagingManage(document.getElementById("paging"), 1, 1);
                document.getElementsByTagName("table")[0].style.display = "";
                document.getElementById("create-time").style.display = "none";
                document.getElementsByTagName("tbody")[0].innerHTML = s;
            } else {
                window.parent.$.Toast(data.msg, 'error');
            }
        }
    })
}

function delete_song(file_id) {
    window.parent.$.ajax({
        type: "GET",
        url: server + "/karaoke/delete/" + file_id,
        success: function (data) {
            if (data.code === 0) {
                window.parent.$.Toast(data.msg, "success");
                get_song_list();
                get_added_songs();
            } else {
                window.parent.$.Toast(data.msg, "error");
            }
        }
    })
}

function sing_song(file_id) {
    window.parent.$.ajax({
        type: "GET",
        url: server + "/karaoke/sing/" + file_id,
        success: function (data) {
            if (data.code === 0) {
                get_added_songs();
                window.parent.$.Toast(data.msg, "success");
            } else {
                window.parent.$.Toast(data.msg, "error");
            }
        }
    })
}

function get_added_songs() {
    window.parent.$.ajax({
        type: "GET",
        url: server + "/karaoke/singHistory/pendingAll",
        success: function (data) {
            if (data.code === 0) {
                document.getElementById("control-center").innerText = window.parent.i18next.t("karaoke.control.name") + data.total + ")";
            } else {
                window.parent.$.Toast(data.msg, "error");
            }
        }
    })
}

function delete_from_list(file_id) {
    window.parent.$.ajax({
        type: "GET",
        url: server + "/karaoke/deleteHistory/" + file_id,
        success: function (data) {
            if (data.code !== 0) {
                window.parent.$.Toast(data.msg, "error");
                get_history_list(history_type);
            }
        }
    })
}

function show_modal_cover() {
    document.getElementsByClassName('modal_cover')[0].style.display = 'flex';
    document.getElementsByClassName('modal_cover')[0].getElementsByClassName('modal_gif')[0].style.display = 'flex';
}

function close_modal_cover() {
    document.getElementsByClassName('modal_cover')[0].style.display = 'none';
    document.getElementsByClassName('modal_cover')[0].getElementsByClassName('modal_gif')[0].style.display = 'none';
}

window.onload = function() {
    get_song_list();
    setTimeout(() => {get_added_songs();}, 500);
    document.getElementById("start-sing").href = "./playing.html?server=" + server + "&lang=" + lang;
    document.getElementById("control-center").href = "./client.html?server=" + server + "&lang=" + lang;
};
