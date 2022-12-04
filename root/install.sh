#!/bin/bash

OS_type="$(uname -m)"
case "$OS_type" in
  x86_64|amd64)
    OS_type='amd64'
    ;;
  i?86|x86)
    OS_type='386'
    ;;
  aarch64|arm64)
    OS_type='arm64'
    ;;
  arm*)
    OS_type='arm'
    ;;
  *)
    echo 'OS type not supported'
    exit 2
    ;;
esac

echo $OS_type
#download_link="https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-${OS_type}-static.tar.xz"
#wget "$download_link"
#tar xvf ffmpeg-git-*-static.tar.xz && rm -rf ffmpeg-git-*-static.tar.xz
#mv ffmpeg-git-*/ffmpeg  ffmpeg-git-*/ffprobe /usr/bin/

# curl https://rclone.org/install.sh | sudo bash
curl https://ghproxy.com/https://raw.githubusercontent.com/vpei/bot/master/root/rclone_install.sh | sudo bash

# curl -fsSL https://ghproxy.com/https://raw.githubusercontent.com/filebrowser/get/master/get.sh | bash
curl -fsSL https://ghproxy.com/https://raw.githubusercontent.com/vpei/bot/master/root/filebrowser_get.sh | bash