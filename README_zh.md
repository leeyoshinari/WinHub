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
1、[详细的部署步骤见博客](https://blog.ihuster.top/p/940241891.html#%E9%83%A8%E7%BD%B2)

2、所有配置在 `config.conf` 中，详细的配置请往下看；

3、访问页面，url是 `http://IP:Port/Windows`（这里的 IP 和 端口是 Nginx 中设置的 IP 和 端口。`Windows`就是第8步中的前端配置的名字）
![](https://github.com/leeyoshinari/WinHub/blob/main/web/img/pictures/login.jpg)
![](https://github.com/leeyoshinari/WinHub/blob/main/web/img/pictures/home.jpg)

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
是否启用自动备份功能，0 不启用，1 启用

### winHubBackupPath
备份目录，必须存在

### winHubBackupInterval
备份周期，单位：天，即每隔x天备份一次

### winHubEnabledAutoUpdate
是否启动自动更新，0 不启用，1 启用

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
