# simple_videoconv_webrtc
本项目实现了局域网内的**简单视频通话系统**，使用 Python 的 Flask 框架作为后端，SocketIO 实现实时通信，WebRTC 完成点对点音视频传输，支持浏览器间双人通话。本项目支持本地部署，代码较少，适合学习和了解应用原理。

项目的部署方式和介绍可以查看这里：[Freexpress](https://yolowoo.icu/2025/04/15/video-conv-instruct/)，项目的具体代码可以直接从此处下载。

如果视频流显示/连接遇到问题，可以查看是否是 getUserMedia 函数的限制。
