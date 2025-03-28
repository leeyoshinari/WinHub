#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

class MsgObj:
    zh_CN = None
    en = None

    def get_text(self, lang: str = 'en') -> str:
        return getattr(self, lang)


class Msg:
    Success = MsgObj()
    Success.zh_CN = "成功"
    Success.en = " successfully"

    Failure = MsgObj()
    Failure.zh_CN = "失败"
    Failure.en = " failed"

    CommonLog = MsgObj()
    CommonLog.zh_CN = "{}, 用户: {}, IP: {}"
    CommonLog.en = "{}, User: {}, IP: {}"

    DateFormatPretty = MsgObj()
    DateFormatPretty.zh_CN = "{}天 {}时 {}分 {}秒"
    DateFormatPretty.en = "{} days {} hours {} minutes {} seconds"

    CommonLog1 = MsgObj()
    CommonLog1.zh_CN = "{}, Id: {}, 用户: {}, IP: {}"
    CommonLog1.en = "{}, Id: {}, User: {}, IP: {}"

    Folder = MsgObj()
    Folder.zh_CN = "新建文件夹"
    Folder.en = "New Folder"

    File = MsgObj()
    File.zh_CN = "{} 文件"
    File.en = "{} file"

    FileTxt = MsgObj()
    FileTxt.zh_CN = "新建文本文件"
    FileTxt.en = "New Text"

    FileMd = MsgObj()
    FileMd.zh_CN = "新建markdown文档.md"
    FileMd.en = "New Markdown.md"

    FileXmind = MsgObj()
    FileXmind.zh_CN = "新建脑图文件.xmind"
    FileXmind.en = "New xmind.xmind"

    FileSheet = MsgObj()
    FileSheet.zh_CN = "新建在线表格.sheet"
    FileSheet.en = "New Online Sheet.sheet"

    FileDocu = MsgObj()
    FileDocu.zh_CN = "新建在线文档.docu"
    FileDocu.en = "New Online Document.docu"

    FileExcel = MsgObj()
    FileExcel.zh_CN = "新建 Excel 工作表.xlsx"
    FileExcel.en = "New Excel Worksheet.xlsx"

    FileWord = MsgObj()
    FileWord.zh_CN = "新建 Word 文档.docx"
    FileWord.en = "New Word Document.docx"

    FilePowerPoint = MsgObj()
    FilePowerPoint.zh_CN = "新建 PowerPoint 演示文稿.pptx"
    FilePowerPoint.en = "New PowerPoint Presentation.pptx"

    FilePy = MsgObj()
    FilePy.zh_CN = "新建python文件.py"
    FilePy.en = "New Python.py"

    ParamError = MsgObj()
    ParamError.zh_CN = "参数错误"
    ParamError.en = "Parameter error"

    Query = MsgObj()
    Query.zh_CN = "查询"
    Query.en = "Query"

    Login = MsgObj()
    Login.zh_CN = "{} 登陆"
    Login.en = "{} login"

    Logout = MsgObj()
    Logout.zh_CN = "{} 退出"
    Logout.en = "{} logout"

    LoginUserOrPwdError = MsgObj()
    LoginUserOrPwdError.zh_CN = "用户名或密码错误"
    LoginUserOrPwdError.en = "Username or password is incorrect."

    CreateUser = MsgObj()
    CreateUser.zh_CN = "用户 {} 创建"
    CreateUser.en = "Create {}"

    ExistUserError = MsgObj()
    ExistUserError.zh_CN = "用户 {} 已存在"
    ExistUserError.en = "User {} already exists."

    UserCheckUsername = MsgObj()
    UserCheckUsername.zh_CN = "用户名只能包含英文字母和数字"
    UserCheckUsername.en = "Username can only contain English letters and numbers."

    UserCheckPassword = MsgObj()
    UserCheckPassword.zh_CN = "两个密码不一样，请重新输入"
    UserCheckPassword.en = "The two passwords are different, please re-enter."

    ModifyPwd = MsgObj()
    ModifyPwd.zh_CN = "{} 密码修改"
    ModifyPwd.en = "{} modify password"

    ModifyStr = MsgObj()
    ModifyStr.zh_CN = "{} 修改"
    ModifyStr.en = "{} modify"

    DownloadError = MsgObj()
    DownloadError.zh_CN = "文件下载失败，请重试"
    DownloadError.en = "File download failed, please try again."

    ExportError1 = MsgObj()
    ExportError1.zh_CN = "请先选择文件或文件夹再导出"
    ExportError1.en = "Please select the file or folder before exporting."

    ExportError2 = MsgObj()
    ExportError2.zh_CN = "暂时只支持一个文件夹导出"
    ExportError2.en = "Only one folder export is supported."

    ExportError3 = MsgObj()
    ExportError3.zh_CN = "文件导出失败，请重试"
    ExportError3.en = "File export failed, please try again."

    VideoError = MsgObj()
    VideoError.zh_CN = "播放失败，请重试"
    VideoError.en = "Failed to play, please try again."

    SSHExport = MsgObj()
    SSHExport.zh_CN = "请输入正确完整的文件绝对路径"
    SSHExport.en = "Please enter the correct and complete absolute path."

    FileTypeError = MsgObj()
    FileTypeError.zh_CN = "不是标准的 {} 文件格式"
    FileTypeError.en = "Not standard {} format"

    Save = MsgObj()
    Save.zh_CN = "{}保存"
    Save.en = "{} save"

    Move = MsgObj()
    Move.zh_CN = "移动"
    Move.en = "Move"

    Upload = MsgObj()
    Upload.zh_CN = "{} 上传"
    Upload.en = "{} upload"

    Download = MsgObj()
    Download.zh_CN = "{} 下载中"
    Download.en = "{} downloading"

    GetFilePath = MsgObj()
    GetFilePath.zh_CN = "查询文件路径"
    GetFilePath.en = "Query file path"

    DownloadOnline = MsgObj()
    DownloadOnline.zh_CN = "正在下载中，请去下载列表中查看进度"
    DownloadOnline.en = "Downloading, please check the progress in the download list"

    DownloadOnlineRemove = MsgObj()
    DownloadOnlineRemove.zh_CN = "已取消下载，{}"
    DownloadOnlineRemove.en = "Downloading has been cancelled, {}"

    DownloadOnlineProtocol = MsgObj()
    DownloadOnlineProtocol.zh_CN = "暂不支持下载"
    DownloadOnlineProtocol.en = "Download is not supported yet"

    Create = MsgObj()
    Create.zh_CN = "{} 创建"
    Create.en = "{} create"

    FileExist = MsgObj()
    FileExist.zh_CN = "{}已存在"
    FileExist.en = "{} already exists."

    FileNotExist = MsgObj()
    FileNotExist.zh_CN = "{}不存在"
    FileNotExist.en = "{} does not exist."

    Rename = MsgObj()
    Rename.zh_CN = "{} 重命名"
    Rename.en = "{} rename"

    RenameError = MsgObj()
    RenameError.zh_CN = "名字重复，请重新输入 ~"
    RenameError.en = "The name is duplicated, please re-enter ~"

    Delete = MsgObj()
    Delete.zh_CN = "{} 删除"
    Delete.en = "{} delete"

    Deal = MsgObj()
    Deal.zh_CN = "{} 处理"
    Deal.en = "{} is done"

    Copy = MsgObj()
    Copy.zh_CN = "{} 复制"
    Copy.en = "{} copy"

    CopyName = MsgObj()
    CopyName.zh_CN = "副本"
    CopyName.en = "copy"

    Restore = MsgObj()
    Restore.zh_CN = "{} 还原"
    Restore.en = "{} restore"

    Export = MsgObj()
    Export.zh_CN = "{} 导出"
    Export.en = "{} export"

    Share = MsgObj()
    Share.zh_CN = "{} 分享"
    Share.en = "{} share"

    ShareOpen = MsgObj()
    ShareOpen.zh_CN = "分享链接打开"
    ShareOpen.en = "Open shared link"

    ShareTimes = MsgObj()
    ShareTimes.zh_CN = "分享链接打开次数太多"
    ShareTimes.en = "The shared link has been opened too many times"

    MusicRecord = MsgObj()
    MusicRecord.zh_CN = "{} 正在播放"
    MusicRecord.en = "{} is playing."

    GameScore = MsgObj()
    GameScore.zh_CN = "游戏得分设置{}"
    GameScore.en = "Set game score {}"

    UpdateStatus = MsgObj()
    UpdateStatus.zh_CN = "更新状态成功"
    UpdateStatus.en = "Update status successful"

    AccessPermissionNon = MsgObj()
    AccessPermissionNon.zh_CN = "未经授权的访问"
    AccessPermissionNon.en = "Unauthorized access"

    OnlyOfficeCreateTips = MsgObj()
    OnlyOfficeCreateTips.zh_CN = "暂不支持在这里创建文件"
    OnlyOfficeCreateTips.en = "File creation is not supported here"

    OnlyOfficeOpenFile = MsgObj()
    OnlyOfficeOpenFile.zh_CN = "{} 文件打开成功"
    OnlyOfficeOpenFile.en = "{} is opened successfully."

    FileTypeNotSupport = MsgObj()
    FileTypeNotSupport.zh_CN = "文件类型暂不支持"
    FileTypeNotSupport.en = "File type is not supported yet."

    OnlyOfficeTrack = MsgObj()
    OnlyOfficeTrack.zh_CN = "{} 正在保存，状态是 {}。"
    OnlyOfficeTrack.en = "{} is tracking. Status is {}."

    HistoryRecord = MsgObj()
    HistoryRecord.zh_CN = "查询历史记录"
    HistoryRecord.en = "Query history record"

    RestoreFromHistory = MsgObj()
    RestoreFromHistory.zh_CN = "从历史记录中恢复"
    RestoreFromHistory.en = "Restore from history record"

    HistoryRecords = MsgObj()
    HistoryRecords.zh_CN = "历史记录"
    HistoryRecords.en = " history record"

    SystemInfo = MsgObj()
    SystemInfo.zh_CN = "查询操作系统信息"
    SystemInfo.en = "Get OS Detail"

    SystemResource = MsgObj()
    SystemResource.zh_CN = "查询系统资源使用率"
    SystemResource.en = "Get System Resource usage"

    SystemCPUInfo = MsgObj()
    SystemCPUInfo.zh_CN = "查询CPU硬件信息"
    SystemCPUInfo.en = "Get CPU hardware detail"

    SystemDiskInfo = MsgObj()
    SystemDiskInfo.zh_CN = "查询磁盘信息"
    SystemDiskInfo.en = "Get Disks detail"

    SystemNetWorkInfo = MsgObj()
    SystemNetWorkInfo.zh_CN = "查询网卡信息"
    SystemNetWorkInfo.en = "Get Network Card detail"

    SystemVersionInfo = MsgObj()
    SystemVersionInfo.zh_CN = "查询系统版本信息"
    SystemVersionInfo.en = "Get System Version"

    SystemUpdateInfo = MsgObj()
    SystemUpdateInfo.zh_CN = "系统更新"
    SystemUpdateInfo.en = "System update"

    SystemRestartInfo = MsgObj()
    SystemRestartInfo.zh_CN = "系统重启"
    SystemRestartInfo.en = "System restart"

    ShortCutsInfo = MsgObj()
    ShortCutsInfo.zh_CN = "查询快捷方式列表"
    ShortCutsInfo.en = "Query Shortcuts List"

    ShortCutsSave = MsgObj()
    ShortCutsSave.zh_CN = "添加快捷方式"
    ShortCutsSave.en = "Add Shortcuts"

    ShortCutsDelete = MsgObj()
    ShortCutsDelete.zh_CN = "删除快捷方式"
    ShortCutsDelete.en = "Delete Shortcuts"

    ShortCutsNotExist = MsgObj()
    ShortCutsNotExist.zh_CN = "快捷方式不存在 ~"
    ShortCutsNotExist.en = "The shortcuts is not exist ~"

    Video = MsgObj()
    Video.zh_CN = "视频"
    Video.en = "Video"

    Vocal = MsgObj()
    Vocal.zh_CN = "人声"
    Vocal.en = "Vocal"

    Accompaniment = MsgObj()
    Accompaniment.zh_CN = "伴奏"
    Accompaniment.en = "Accompaniment"

    RequestSong = MsgObj()
    RequestSong.zh_CN = "点歌"
    RequestSong.en = " Request Song"

    SetTop = MsgObj()
    SetTop.zh_CN = "置顶"
    SetTop.en = " set top"

    Singed = MsgObj()
    Singed.zh_CN = " K歌"
    Singed.en = " sing"

    Setting = MsgObj()
    Setting.zh_CN = "设置"
    Setting.en = "Set"

    SyncManual = MsgObj()
    SyncManual.zh_CN = "手动备份"
    SyncManual.en = "Manual Sync"

    SyncDataNo = MsgObj()
    SyncDataNo.zh_CN = "未启用备份功能~"
    SyncDataNo.en = "Backup function is not enabled."

    MeetingCreate = MsgObj()
    MeetingCreate.zh_CN = "创建会议码"
    MeetingCreate.en = "Create Meeting Code"

    MeetingJoin = MsgObj()
    MeetingJoin.zh_CN = "正在加入聊天中..."
    MeetingJoin.en = "Joining Chatting..."

    MeetingQuit = MsgObj()
    MeetingQuit.zh_CN = "退出会议"
    MeetingQuit.en = "Quit Meeting"

    ChatStatus = MsgObj()
    ChatStatus.zh_CN = ["未开始", "聊天中", "已结束"]
    ChatStatus.en = ["NotStart", "Chatting", "Stopped"]

    ChatMode = MsgObj()
    ChatMode.zh_CN = ["语音聊天", "视频聊天", "文件传输"]
    ChatMode.en = ["VoiceChat", "VideoChat", "FileTransfer"]

    HealthSetData = MsgObj()
    HealthSetData.zh_CN = "设置"
    HealthSetData.en = "Set data"

    HealthNoData = MsgObj()
    HealthNoData.zh_CN = "数据缺失"
    HealthNoData.en = "No data"

    HealthBloodPressureErr = MsgObj()
    HealthBloodPressureErr.zh_CN = "收缩压和舒张压填错了~"
    HealthBloodPressureErr.en = "Systolic blood pressure and diastolic blood pressure are wrong~"
