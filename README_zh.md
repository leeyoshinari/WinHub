# WinHub
[English Document](https://github.com/leeyoshinari/WinHub/blob/main/README.md)

[更多内容详见博客](https://blog.ihuster.top/p/940241891.html)

## 功能
- 文件夹的新建、删除、重命名、移动、导出
- 文件的上传、下载、新建、删除、移动、重命名、分享
- 支持 OnlyOffice (Word、Excel、PowerPoint) 在线编辑和多人协作
- 支持 txt、markdown、xmind脑图、表格、文档的在线编辑功能
- 支持 python 脚本在线编辑和运行
- 支持给文件添加桌面快捷方式
- 支持自动备份指定文件夹中的所有文件
- 支持远程连接 Linux 服务器
- 支持点对点视频聊天和屏幕分享(基于 WebRTC)
- 音乐播放器，支持播放云盘（服务端）和本地（客户端）的音乐
- 支持 KTV，自建曲库，想唱就唱
- 集成 aria2，支持 HTTP、FTP、BitTorrent 等多种下载协议
- 增加游戏中心，支持贪吃蛇、俄罗斯方块、套圈圈游戏（会陆续支持更多小游戏）
- 支持重启，支持自动更新
- 支持多语言，支持配置多语言
- 单点登录，不同用户的数据完全隔离
- 支持 PWA，可以“安装”到手机上
- 可任意挂载多个磁盘


## 技术选型
- 后端框架：FastApi<br>
- 数据库：SQLite3 or MySQL<br>
- 前端：html + js + css<br>

## 部署
1、克隆 `git clone https://github.com/leeyoshinari/WinHub.git` ；

2、进入目录 `cd WinHub`，核对配置`config.conf`；<br>
注意：如果你需要重启和自动更新的功能，那么你需要把 `config.conf` 中的需要修改的配置设置成系统环境变量。详细的配置请往下看。

3、安装第三方包
```shell script
pip3 install -r requirements.txt
```
特别注意：如果你使用的是 Windows 系统，那么还要安装 pywin32 包，执行 `pip install pywin32`。

4、初始化数据库，依次执行下面命令；
```shell script
aerich init -t settings.TORTOISE_ORM
aerich init-db
```

5、安装文件下载工具 [aria2](https://github.com/aria2/aria2/releases)，执行 `aria2c -v` 验证是否安装成功。

6、启动服务；
```shell script
sh startup.sh
```

7、创建账号；
为了避免被其他人恶意创建账号，页面未放开创建账号的入口；可以通过在API接口文档中创建用户，进入 swagger-ui 页面，找到 `createUser` 接口即可。
```shell script
http://IP:Port/配置文件中的prefix/swagger-ui
```

8、配置并启动 `nginx`，location相关配置如下：<br>
（1）前端配置：前端文件在 `web` 目录里, `/Windows`可任意修改成你喜欢的名字
```shell script
location /Windows {
    alias /home/WinHub/web/;
    index  index.html;
}
```
（2）后端请求：`proxy_pass`是配置文件`config.conf`中的 IP 和 端口, `/mycloud`必须和`config.conf`中的`prefix`一样
```shell script
location /mycloud {
     proxy_pass  http://127.0.0.1:15200;
     proxy_set_header Host $proxy_host;
     proxy_set_header lang $http_lang;
     proxy_set_header X-Real-IP $remote_addr;
     proxy_set_header Upgrade $http_upgrade;
	 proxy_set_header Connection $proxy_connection;
     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```
（3）在 `http` 模块中，需要添加一个映射关系
```shell
map $http_upgrade $proxy_connection {
    default upgrade;
    "" close;
}
```
（4）Swagger 接口页面
```shell
location /api/openapi {
    proxy_pass  http://127.0.0.1:15200;
}
```

通常nginx会限制请求体大小，需要增加配置`client_max_body_size 4096M;`，还有其他超时时间的配置，可自行上网查找资料修改；

如果你不了解 nginx，请先去[nginx 官方网站](http://nginx.org/en/download.html)下载对应系统的nginx安装包，并按照网上的教程安装。安装完成后用本项目中的`nginx.conf`替换掉安装完成后的`nginx.conf`，然后重启nginx即可。如果你使用的是`https`，直接修改端口并配置 ssl 即可。

9、访问页面，url是 `http://IP:Port/Windows`（这里的 IP 和 端口是 Nginx 中设置的 IP 和 端口。`Windows`就是第8步中的前端配置的名字）
![](https://github.com/leeyoshinari/WinHub/blob/main/web/img/pictures/login.jpg)
![](https://github.com/leeyoshinari/WinHub/blob/main/web/img/pictures/home.jpg)

10、如果想把当前服务器上已有的文件导入系统中，可访问后台 api 接口页面，找到 `file/import` 接口，请求参数分别是需要导入的文件夹的绝对路径和目标的目录Id。

## 配置解释
以下配置，如果需要修改的话，一定要配置到系统环境变量中，如果没有设置环境变量，则默认会使用 `config.conf` 中的配置。设置环境变量后，如果没有生效，请重新打开命令行窗口或重新 ssh 服务器。

### winHubHost 和 winHubPort
后端服务监听的 ip 和 端口

### winHubFrontEndPrefix
前端 prefix，和 nginx 中的一样，只用于 swagger 页面展示。如果不需要 prefix，那么请配置为空。

### winHubBackEndPrefix
后端 prefix，nginx 中的配置要和这里的一样。如果不需要 prefix，那么请配置为空。

### winHubDbUrl
数据库连接，只支持 sqlite3 和 MySQL

### winHubRootPath
每个磁盘文件的根目录，如下配置，网盘的 D 盘里的文件全部放在 `home/WinHub/data` 目录里，网盘的 E 盘里的文件全部放在 `/opt/Windows/data` 目录里。这里配置的目录必须存在。
`{"D": "/home/WinHub/data", "E": "/opt/Windows/data", "F": "/data/data"}`

### winHubPwaUrl
PWA 的启动 url，如果前端的 prefix 配置为空，那么这里也可以配置为空，否则就需要配置访问前端的 url。注意：PWA 只支持 https 协议。

### winHubEnableOnlyoffice
是否启用 OnlyOffice，0 不启用，1 启用

### winHubOnlyOfficeServer 和 winHubOnlyOfficeSecret
分别为 OnlyOffice 的访问地址和 OnlyOffice 的 jwt secret

### winHubHistoryVersionPath
OnlyOffice 文件编辑过程中的历史版本存放目录

### winHubEnableBackup
是否启用备份功能，0 不启用，1 启用

### winHubBackupPath
备份目录，必须存在

### winHubBackupInterval
备份周期，单位：天，即每隔x天备份一次

### winHubTrackerUrls
可用 tracker 获取连接，aria2c 下载 BT 种子需要 tracker

### winHubSTUN
STUN 服务器地址，主要用于音视频通话

### winHubTURN
TURN 服务器地址，主要用于音视频通话

### winHubTURNUserName 和 winHubCredential
TURN 服务的用户名和密码

### winHubLevel
日志级别

## 其他
1、支持 `Linux`、`Windows`、`MacOS` 等多个平台，建议在 `Linux` 系统部署； 

2、因为是在操作本地文件，所以不支持集群部署和分布式存储；

3、在线播放视频，基本上都是用的是流式播放（边缓存边播放），这就要求视频的元数据必须在视频文件的最前面，而有些视频的元数据在视频文件的末尾，这就需要浏览器把整个视频加载完成后才能播放，体验极差。因此需要手动将视频的元数据移动到视频文件的最前面，然后再上传至云盘，这里使用 [ffmpeg](https://github.com/BtbN/FFmpeg-Builds/releases) 工具移动视频的元数据，命令：`ffmpeg -i input_video.mp4 -map_metadata 0 -c:v copy -c:a copy -movflags +faststart output_video.mp4`。

4、所有页面和操作已尽可能的适配手机端了，使用手机浏览器打开页面，手机横屏展示，使用体验还是不错的；

5、更好的使用体验建议：不管你用的是PC端浏览器还是手机端浏览器，设置浏览器全屏展示，使用体验更好；

## 开源协议
此项目使用 GPL-2.0 许可证。当您使用此项目时，请遵守 GPL-2.0 许可证的条款。请自觉尊重我们的工作成果。

如果您不愿意遵守 GPL-2.0 许可证的条款，请在 Issues 中联系我以获取商业许可信息。

## 鸣谢
鸣谢以下项目
- [win12](https://github.com/tjy-gitnub/win12)
- [i18next](https://github.com/i18next/i18next)
- [viewerjs](https://github.com/fengyuanchen/viewerjs)
- [kityminder](https://github.com/fex-team/kityminder)
- [editor.md](https://github.com/pandao/editor.md)
- [Luckysheet](https://github.com/dream-num/Luckysheet)
- [wangEditor](https://github.com/wangeditor-team/wangEditor)
- [snake](https://github.com/SunQQQ/snake)
