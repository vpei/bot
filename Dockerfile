# FROM ubuntu
FROM debian:unstable-slim

RUN sed -ri -e 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources
# RUN sed -ri -e 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
# RUN sed '$a deb http://archive.ubuntu.com/ubuntu/ trusty main universe restricted multiverse' /etc/apt/sources.list
RUN apt update
RUN apt upgrade -y
RUN apt install -y sudo
RUN apt install -y tzdata
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone

RUN apt install -y gcc libffi-dev libssl-dev 
RUN apt install -y gconf-service libasound2 libatk1.0-0 libatk-bridge2.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils
RUN apt install -y libxml2-dev libxslt-dev

RUN apt install -y wget
RUN apt install -y git
RUN apt install -y curl
RUN apt install -y unzip

# 安装python3及相关
RUN apt install -y python3
RUN apt install -y python3-dev
RUN apt install -y python3-pip
RUN apt install -y python3-pillow
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple requests
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -U pyrogram tgcrypto
# RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pillow
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple telegraph
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple aria2p
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple mutagen
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -U yt-dlp
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple apscheduler
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pyromod
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple psutil
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple nest_asyncio
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pyppeteer

RUN apt install -y ffmpeg

COPY root /
RUN chmod 777 /install.sh
RUN sed -i 's/\r//' /install.sh
RUN bash install.sh

RUN apt install -y nginx
RUN mv /nginx.conf /etc/nginx/

RUN apt install -y aria2
RUN mkdir /root/.aria2
COPY config /root/.aria2/


# 解析网页内容
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple beautifulsoup4   #li格式
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple lxml
# RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple bs4            # 默认lxml，修改bs4超链接
# RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple html5lib       # 默认lxml，修改bs4超链接
# RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pandas         #table格式
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple nhentai          # nhentai爬虫  --upgrade

# pyrogram 新版参数问题补丁
RUN sed -ri -e 's/enums.ParseMode.MARKDOWN/"Markdown"/g' /usr/local/lib/python3.10/dist-packages/pyrogram/parser/parser.py

# 数据库插件
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple meilisearch        #meilisearch

RUN mkdir /index
COPY /index.html /index

RUN mkdir /bot
COPY bot /bot
RUN chmod 0777 /bot/ -R

RUN sudo chmod 777 /root/.aria2/

COPY /config/upload.sh /
RUN chmod 0777 /upload.sh

# COPY /start.sh /
# CMD chmod 0777 start.sh && bash start.sh
CMD wget https://ghproxy.com/https://raw.githubusercontent.com/vpei/bot/main/start.sh -O start.sh && chmod 0777 start.sh && bash start.sh

# 打包命令
# docker login && docker buildx build -t vpei/bot:latest --platform linux/amd64 --push .

# 批量打包命令
# docker buildx install
# docker buildx create --use --name build --node build --driver-opt network=host
# docker login && docker buildx build -t vpei/bot:latest --platform linux/arm/v7,linux/arm64/v8,linux/386,linux/amd64 --push .
