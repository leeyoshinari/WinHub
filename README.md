# WinHub
A multi-functional platform integrating file storage, editing, communication, entertainment and system management.

[中文文档](https://github.com/leeyoshinari/WinHub/blob/main/README_zh.md)

[更多内容详见博客](https://blog.ihuster.top/p/940241891.html)

## Function
- Create, Delete, Rename, Move, and Export folders
- Upload, Download, Create, Delete, Move, Rename, and Share files
- Supports OnlyOffice (Word, Excel, PowerPoint) online editing and multi-user collaborative editing
- Supports online editing functions of txt, markdown, xmind, sheet, and document
- Support online editing and running of python scripts
- Support add desktop shortcuts for files
- Support auto-backup of all files in the specified folder
- Support remote connection to Linux server
- Support peer-to-peer video chat and screen sharing (based on WebRTC)
- Music player, supports playing music from this cloud-drive (Server) and local (Client)
- Karaoke, supports building your own song library
- Integrate aria2, and support multiple download protocols such as HTTP, FTP, BitTorrent, etc.
- Add game center, supports Snake, tetris games (plans to support more games in the future).
- Supports multiple languages and supports configuration of multiple languages
- Single sign-on, data of different users is completely isolated
- Support PWA, it can be installed on the mobile
- Multiple disks can be mounted arbitrarily

View detailed page style, [Please click me.](https://github.com/leeyoshinari/WinHub/blob/main/web/detail.md)

## Technology
- Framework: FastApi
- Database: SQLite3 or MySQL
- Front-end: html + js + css

## Deploy
1.Clone `git clone https://github.com/leeyoshinari/WinHub.git` ；

2.`cd WinHub`, and modify `config.conf`；

3.Install third-party packages
```shell script
pip3 install -r requirements.txt
```
Note: If you use Windows system, you need to install pywin32 package, run command: `pip install pywin32`。

4.Initialize the database and execute the following commands in sequence
```shell script
aerich init -t settings.TORTOISE_ORM
aerich init-db
```

5.Install download tool [aria2](https://github.com/aria2/aria2/releases), running `aria2c -v` to verify whether the installation is successful.

6.Startup
```shell script
sh startup.sh
```

7.Create user<br>
In order to avoid malicious creation of users by others, the page does not open the entrance to create users. So, you can create a user in the API interface documentation, entering the `swagger-ui` page and finding the `createUser` interface.
```shell script
http://IP:Port/配置文件中的prefix/swagger-ui
```

8.Configure and start `nginx`, the location configuration is as follows:<br>
(1)Front-end configuration: The front-end file is in `web`, `/Windows` can be modified to any name you like.
```shell script
location /Windows {
    alias /home/WinHub/web/;
    index  index.html;
}
```
(2)Backend request: `proxy_pass` is the IP and port in `config.conf`, `/mycloud` must be the same as `prefix` in `config.conf`.
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
(3) In the `http` module, a mapping need to be add.
```shell
map $http_upgrade $proxy_connection {
    default upgrade;
    "" close;
}
```
（4）Swagger page
```shell
location /api/openapi {
    proxy_pass  http://127.0.0.1:15200;
}
```

Usually nginx will limit the size of the request body, and you need to add `client_max_body_size 4096M;` to `nginx.conf`. There are other configurations, you can search for information and modify them online by yourself.

If you don’t know nginx, please go to [nginx official website](http://nginx.org/en/download.html) to download nginx and install it. After the installation is completed, replace the installed `nginx.conf` with the `nginx.conf` in this project, and then restart nginx.

9.Page, the url is `http://IP:Port/Windows` (the IP and port are the IP and port set in Nginx. `Windows` is the name of the front-end configuration in step 7)
![](https://github.com/leeyoshinari/WinHub/blob/main/web/img/pictures/login.jpg)
![](https://github.com/leeyoshinari/WinHub/blob/main/web/img/pictures/home.jpg)

10.If you want to import existing files on the current server into the system, you can access the background api interface page and find the `file/import` interface. The request parameters are the absolute path of the folder to be imported and the Id of the target catalog.

11.If you need to configure multiple languages, [Please click me](https://github.com/leeyoshinari/WinHub/blob/main/web/detail.md).

12.If you want to know more, [Please click me](https://github.com/leeyoshinari/WinHub/blob/main/web/detail.md).

## Others
1.Supports multiple platforms such as `Linux`, `Windows`, `MacOS`, etc. It is recommended to deploy on `Linux`.

2.Cluster deployment and distributed storage are not supported.

3.Playing videos online uses streaming playback, which requires that the metadata of the video must be at the front of the video file. So, you need to manually move the metadata of the video to the front of the video file. Using the [ffmpeg](https://github.com/BtbN/FFmpeg-Builds/releases) to move the metadata of the video. The command: `ffmpeg -i input_video.mp4 -map_metadata 0 -c:v copy -c:a copy -movflags +faststart output_video.mp4`.

4.Whether you are using a PC browser or a mobile browser, setting the browser to display in full screen will provide a better user experience.

## License
This repository uses the GPL-2.0 License. When you use this repository, please comply with the terms of the GPL-2.0 License. Please respect our work results consciously.

If you don't wish to comply with the terms of the GPL-2.0 License, please contact me in the Issues for commercial licensing information.

## Thanks
Thanks to the following projects
- [win12](https://github.com/tjy-gitnub/win12)
- [i18next](https://github.com/i18next/i18next)
- [viewerjs](https://github.com/fengyuanchen/viewerjs)
- [kityminder](https://github.com/fex-team/kityminder)
- [editor.md](https://github.com/pandao/editor.md)
- [Luckysheet](https://github.com/dream-num/Luckysheet)
- [wangEditor](https://github.com/wangeditor-team/wangEditor)
- [snake](https://github.com/SunQQQ/snake)
