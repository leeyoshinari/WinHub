const params = window.location.href.split('&');
const servers = params[0].split('=')[1];
const roomParam = params[1].split('=')[1];
const roomCode = roomParam.slice(0, roomParam.length - 1);
let socketURL = 'ws://' + window.location.host + servers + '/chat/join' ;
if (window.location.protocol === 'https:') {
    socketURL = 'wss://' + window.location.host + servers + '/chat/join' ;
}
let ws;
let localStream;
let currentUser = "localVideo";
let currentVideoDeviceId;
let videoDevices = [];
let peerConnections = {};
let remoteStreams = {};
const mainVideo = document.getElementById('mainVideo');
const localVideoDiv = document.getElementById('localVideo');
const localVideo = localVideoDiv.getElementsByTagName('video')[0];
const remoteVideos = document.getElementsByClassName('remote-videos')[0];
const micButton = document.getElementById('micButton');
const cameraButton = document.getElementById('cameraButton');
const speakerButton = document.getElementById('speakerButton');
const shareScreenButton = document.getElementById('shareScreenButton');
const localVideoMic = localVideoDiv.getElementsByTagName('i')[0];
const expandAndPickup = document.getElementById('expand-img');
let micEnabled = true;
let cameraEnabled = true;
let speakerEnabled = false;
let shareScreenEnabled = false;
let stunServer;
let username;
let nickname;

window.parent.$.ajax({
    type: "GET",
    async: false,
    url: servers + '/chat/stun/' + roomParam,
    success: function (data) {
        if (data['code'] === 0) {
            stunServer = { iceServers: [{ urls: data['data']['stun'] }, { username: data['data']['user'], credential: data['data']['cred'], urls: data['data']['turn'] }]};
            username = data['data']['username'];
            socketURL += '/' + username + '/' + roomCode;
            nickname = data['data']['nickname'];
        } else {
            window.parent.$.Toast(data['msg'], 'error');
            return;
        }
    }
});

async function switchCamera() {
    const videoTracks = localStream.getVideoTracks();
    videoTracks.forEach(track => track.stop());
    const videoDevicesList = videoDevices.filter(device => device.kind === "videoinput");
    if (videoDevicesList.length > 0) {
        const nextDeviceIndex = (videoDevicesList.findIndex(device => device.deviceId === currentVideoDeviceId) + 1) % videoDevicesList.length;
        currentVideoDeviceId = videoDevicesList[nextDeviceIndex].deviceId;
        localStream = await navigator.mediaDevices.getUserMedia({video: {deviceId: currentVideoDeviceId}, audio: true});
        localVideo.srcObject = localStream;
        localVideo.muted = true;
        remoteStreams['localVideo'] = localStream;
        for (const [userId, peerConnection] of Object.entries(peerConnections)) {
            const sender = peerConnection.getSenders().find(s => s.track && s.track.kind === 'video');
            if (sender) {
                await sender.replaceTrack(localStream.getVideoTracks()[0]);
            }
        }
        const videoTrack = localStream.getVideoTracks()[0];
        if (videoTrack) {
            videoTrack.enabled = cameraEnabled;
        }
        const audioTrack = localStream.getAudioTracks()[0];
        if (audioTrack) {
            audioTrack.enabled = micEnabled;
        }
        if (currentUser === "localVideo") {
            switchVideo();
        }
    }
}

async function joinRoom() {
    videoDevices = await navigator.mediaDevices.enumerateDevices();
    const videoDevicesList = videoDevices.filter(device => device.kind === "videoinput");
    if (videoDevicesList.length > 0) {
        currentVideoDeviceId = videoDevicesList[0].deviceId;
    }
    localStream = await navigator.mediaDevices.getUserMedia({video: {deviceId: currentVideoDeviceId}, audio: true});
    localVideo.srcObject = localStream;
    localVideo.muted = true;
    remoteStreams['localVideo'] = localStream;
    localVideoDiv.getElementsByTagName('span')[0].innerText = nickname;
    currentUser = "localVideo";
    switchVideo();

    ws = new WebSocket(socketURL);
    ws.onopen = () => {
        ws.send(JSON.stringify({type: "newUser", from: username, nick: nickname, data: roomCode}));
    }
    ws.onmessage = async (message) => {
        const data = JSON.parse(message.data);
        if (data.type === "newUser") {
            if (data.data === roomCode) {
                await createOfferForNewUser(data.from, data.nick);
            }
        } else if (data.offer) {
            if (data.to === username) {
                await handleOffer(data.offer, data.from, data.nick, data.mic);
            }
        } else if (data.answer) {
            if (data.to === username) {
                await handleAnswer(data.answer, data.from);
            }
        } else if (data.iceCandidate) {
            if (data.to === username) {
                await handleIceCandidate(data.iceCandidate, data.from);
            }
        } else if (data.type === "disconnect") {
            handleCloseVideo(data.from);
        } else if (data.type === "mic") {
            await switchRemoteMic(data.from, data.data);
        } else if (data.type === "shareScreen") {
            handleSharedScreen(data.from);
        }
    };
}

async function createOfferForNewUser(userId, nick) {
    const peerConnection = new RTCPeerConnection(stunServer);
    localStream.getTracks().forEach((track) => peerConnection.addTrack(track, localStream));
    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            console.log('本地IP地址: ', event.candidate.address);
            ws.send(JSON.stringify({iceCandidate: event.candidate, from: username, to: userId}));
        }
    }
    peerConnection.ontrack = (event) => {
        const existVideo = document.getElementById(userId);
        if (existVideo) {
            existVideo.getElementsByTagName('video')[0].srcObject = event.streams[0];
        } else {
            const newVideo = document.createElement("div");
            newVideo.classList.add("video");
            newVideo.id = userId;
            newVideo.innerHTML = `<div class="user-status"><i class="fas fa-microphone"></i><span>${nick}</span></div><video autoplay muted></video>`;
            newVideo.addEventListener('click', () => {currentUser=userId;switchVideo();});
            remoteVideos.appendChild(newVideo);
            const remoteV = document.getElementById(userId).getElementsByTagName('video')[0];
            remoteV.srcObject = event.streams[0];
            remoteV.autoplay = true;
            remoteV.muted = speakerEnabled;
            remoteStreams[userId] = event.streams[0];
        }
    }

    const newOffer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(newOffer);
    ws.send(JSON.stringify({offer: newOffer, from: username, nick: nickname, mic: micEnabled, to: userId}));
    peerConnections[userId] = peerConnection;
}

async function handleOffer(offer, userId, nick, isMic) {
    const peerConnection = new RTCPeerConnection(stunServer);
    peerConnections[userId] = peerConnection;
    localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));

    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            console.log('本地IP地址: ', event.candidate.address);
            ws.send(JSON.stringify({iceCandidate: event.candidate, from: username, to: userId}));
        }
    }
    peerConnection.ontrack = (event) => {
        const existVideo = document.getElementById(userId);
        if (existVideo) {
            existVideo.getElementsByTagName('video')[0].srcObject = event.streams[0];
        } else {
            const newVideo = document.createElement("div");
            newVideo.classList.add("video");
            newVideo.id = userId;
            newVideo.innerHTML = `<div class="user-status"><i class="fas fa-microphone"></i><span>${nick}</span></div><video autoplay muted></video>`;
            newVideo.addEventListener('click', () => {currentUser=userId;switchVideo();});
            remoteVideos.appendChild(newVideo);
            const remoteV = document.getElementById(userId).getElementsByTagName('video')[0];
            remoteV.srcObject = event.streams[0];
            remoteV.autoplay = true;
            remoteV.muted = speakerEnabled;
            remoteStreams[userId] = event.streams[0];
            switchRemoteMic(userId, isMic);
        }
    }

    await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);
    ws.send(JSON.stringify({answer: answer, from: username, to: userId}));
}

async function handleAnswer(answer, userId) {
    const peerConnection = peerConnections[userId];
    await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
}

async function handleIceCandidate(candidate, userId) {
    const peerConnection = peerConnections[userId];
    await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
}

async function startScreenShare() {
    const videoTracks = localStream.getVideoTracks();
    videoTracks.forEach(track => track.stop());
    localStream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true });
    localVideo.srcObject = localStream;
    localVideo.muted = true;
    currentUser = 'localVideo';
    remoteStreams['localVideo'] = localStream;

    for (const [userId, peerConnection] of Object.entries(peerConnections)) {
        const videoSender = peerConnection.getSenders().find(s => s.track && s.track.kind === 'video');
        if (videoSender) {
            await videoSender.replaceTrack(localStream.getVideoTracks()[0]);
        }
    }
    mainVideo.srcObject = localStream;
    mainVideo.muted = true;
    ws.send(JSON.stringify({type: "shareScreen", from: username}));
}

async function stopScreenShare() {
    const videoTracks = localStream.getVideoTracks();
    videoTracks.forEach(track => track.stop());
    localStream = await navigator.mediaDevices.getUserMedia({ video: { deviceId: currentVideoDeviceId }, audio: true });
    localVideo.srcObject = localStream;
    localVideo.muted = true;
    currentUser = 'localVideo';
    remoteStreams['localVideo'] = localStream;

    for (const [userId, peerConnection] of Object.entries(peerConnections)) {
        const videoSender = peerConnection.getSenders().find(s => s.track && s.track.kind === 'video');
        if (videoSender) {
            await videoSender.replaceTrack(localStream.getVideoTracks()[0]);
        }
    }
    mainVideo.srcObject = localStream;
    mainVideo.muted = true;
}

async function switchRemoteMic(userId, micData) {
    const tmpMic = document.getElementById(userId).getElementsByTagName('i')[0];
    if (micData) {
        tmpMic.classList.remove('fa-microphone-slash');
        tmpMic.classList.add('fa-microphone');
        tmpMic.classList.remove('fa-cancel');
    } else {
        tmpMic.classList.remove('fa-microphone');
        tmpMic.classList.add('fa-microphone-slash');
        tmpMic.classList.add('fa-cancel');
    }
}

function switchVideo() {
    mainVideo.srcObject = remoteStreams[currentUser];
    mainVideo.play();
}

function handleSharedScreen(userId) {
    currentUser = userId;
    switchVideo();
}

function handleCloseVideo(userId) {
    document.getElementById(userId).remove();
    if (currentUser === userId) {
        currentUser = "localVideo";
        switchVideo();
    }
}

localVideoDiv.addEventListener('click', () => {
    currentUser = "localVideo";
    switchVideo();
})

cameraButton.addEventListener('click', () => {
    cameraEnabled = !cameraEnabled;
    const videoTrack = remoteStreams['localVideo'].getVideoTracks()[0];
    if (videoTrack) {
        videoTrack.enabled = cameraEnabled;
        if (cameraEnabled) {
            cameraButton.querySelector('i').classList.remove('fa-video-slash');
            cameraButton.querySelector('i').classList.add('fa-video');
            cameraButton.querySelector('i').classList.remove('fa-cancel');
        } else {
            cameraButton.querySelector('i').classList.remove('fa-video');
            cameraButton.querySelector('i').classList.add('fa-video-slash');
            cameraButton.querySelector('i').classList.add('fa-cancel');
        }
    }
})

micButton.addEventListener('click', () => {
    micEnabled = !micEnabled;
    const audioTrack = remoteStreams['localVideo'].getAudioTracks()[0];
    if (audioTrack) {
        audioTrack.enabled = micEnabled;
        ws.send(JSON.stringify({type:'mic', from: username, data: micEnabled}));
        if (micEnabled) {
            micButton.querySelector('i').classList.remove('fa-microphone-slash');
            micButton.querySelector('i').classList.add('fa-microphone');
            micButton.querySelector('i').classList.remove('fa-cancel');
            localVideoMic.classList.remove('fa-microphone-slash');
            localVideoMic.classList.add('fa-microphone');
            localVideoMic.classList.remove('fa-cancel');
        } else {
            micButton.querySelector('i').classList.remove('fa-microphone');
            micButton.querySelector('i').classList.add('fa-microphone-slash');
            micButton.querySelector('i').classList.add('fa-cancel');
            localVideoMic.classList.remove('fa-microphone');
            localVideoMic.classList.add('fa-microphone-slash');
            localVideoMic.classList.add('fa-cancel');
        }
    }
})

speakerButton.addEventListener('click', () => {
    speakerEnabled = !speakerEnabled;
    if (speakerEnabled) {
        speakerButton.querySelector('i').classList.remove('fa-volume-up');
        speakerButton.querySelector('i').classList.add('fa-volume-mute');
        speakerButton.querySelector('i').classList.add('fa-cancel');
    } else {
        speakerButton.querySelector('i').classList.remove('fa-volume-mute');
        speakerButton.querySelector('i').classList.add('fa-volume-up');
        speakerButton.querySelector('i').classList.remove('fa-cancel');
    }
    const videoElements = remoteVideos.getElementsByClassName('video');
    for (let video of videoElements) {
        if (video.id !== "localVideo") {
            video.getElementsByTagName('video')[0].muted = speakerEnabled;
        }
    }
})

shareScreenButton.addEventListener('click', () => {
    shareScreenEnabled = !shareScreenEnabled;
    if (shareScreenEnabled) {
        startScreenShare()
            .then(() => console.log("share screen."))
            .catch(error => {console.log("Error: ", error);window.parent.$.Toast(error, 'error');});
        ws.send(JSON.stringify({type:'shareScreen', from: username}));
        shareScreenButton.querySelector('i').classList.remove('fa-desktop');
        shareScreenButton.querySelector('i').classList.add('fa-stop');
        shareScreenButton.querySelector('i').classList.add('fa-cancel');
    } else {
        stopScreenShare()
            .then(() => console.log("stop screen."))
            .catch(error => {console.log("Error: ", error)});
        shareScreenButton.querySelector('i').classList.remove('fa-stop');
        shareScreenButton.querySelector('i').classList.add('fa-desktop');
        shareScreenButton.querySelector('i').classList.remove('fa-cancel');
    }
})

expandAndPickup.addEventListener('click', () => {
    img_src = expandAndPickup.src;
    if (img_src.indexOf("expand.svg") > 1) {
        remoteVideos.style.display = 'none';
        expandAndPickup.src = "karaoke/img/pickup.svg";
        document.getElementsByClassName("setting-video")[0].style.transform = "translateX(0)";
    } else {
        remoteVideos.style.display = '';
        expandAndPickup.src = "karaoke/img/expand.svg";
        document.getElementsByClassName("setting-video")[0].style.transform = "translateX(17px)";
    }
})

window.onbeforeunload = () => { ws.send(JSON.stringify({ type: 'disconnect', from: username })); };

window.onload = function () {
    joinRoom()
        .then(() => {console.log("Success Join.")})
        .catch(error => {console.error("Error: ", error);window.parent.$.Toast(error, 'error');})
}