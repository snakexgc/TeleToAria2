# TeleToAria2

TeleToAria2

# 关于本仓库

本仓库是完全基于 https://github.com/jw-star/aria2bot 项目来的，修复了一些bug，删除了一些我用不到的功能，并将它向我的目标需求开发。

# 本项目最终目标
本项目最后的目标是实现多个项目的整合，实现aria2控制，转发telegram到bot后，自动下载并通过rclone上传到网盘。 

目前我的python水平很差，只能借助gpt等语言模型摸索式进行，可能最终能实现功能，但是代码成了屎山，也希望有大佬能够来帮助我完善这个项目，感激不尽！ 

# 更新日志
- 23.11.27 简化参数，删除重复输入的参数，但是目前只支持IP
- 23.7.18 删除 自定义目录 功能，因为对于docker安装的aria2来说，这项功能无用
- 23.7.17 删除原项目将下载后的文件上传telegram的功能，简化项目，500+MB-->160+MB 为下一步项目合并做铺垫
- 23.7.14 修复了文件名尾缀含参数时，下载文件名错误的bug。

### 特点

1. 基于电报机器人控制aria2
2. 单用户现在，多用户没什么用
3. 支持 `批量` 添加 http、磁力、种子下载


### 如何安装

---
参考教程：https://snakexgc.ml/article/230716
---


1.编辑docker-compose.yml

```yaml
    environment:
      TZ: Asia/Shanghai
      API_ID: 11111  # https://my.telegram.org 获取
      API_HASH: 11111  # https://my.telegram.org 获取
      BOT_TOKEN: 11111:11111  # 在telegram @BotFather 获取
      JSON_RPC_URL: http://11111:6800/jsonrpc # 输入你aria2的链接
      JSON_RPC_TOKEN: 11111  # 输入你aria2的秘钥
      SEND_ID: 11111  #可以启动bot后发送 /start 获取，或者转发消息给 @get_id_bot 
      #PROXY_IP:   #可选  代理ip
      #PROXY_PORT:  #可选 代理端口

```

2.启动


安装 docker

```
curl -fsSL get.docker.com -o get-docker.sh&&sh get-docker.sh &&systemctl enable docker&&systemctl start docker
```


拉取项目

```
git clone https://github.com/snakexgc/TeleToAria2.git

cd TeleToAria2
```

删除容器（如果容器存在）
```
docker rm -f tta
```

删除镜像（如果镜像存在）
```
docker images
```
查看老版本镜像ID后
```
docker rmi ID
```

后台启动
```yaml
docker compose up -d
```

查看日志

```yaml
docker logs -f tta
```

### 可选安装

aria2 安装推荐使用以下项目

```yaml
https://github.com/P3TERX/Aria2-Pro-Docker
```

### 应用截图

/help  查看帮助

### 灵感来自

https://github.com/HouCoder/tele-aria2 

https://github.com/synodriver/aioaria2 

多平台构建参考: https://cloud.tencent.com/developer/article/1543689 

telegram文件下载：https://github.com/EverythingSuckz/TG-FileStreamBot 

aria2-pro：https://github.com/P3TERX/Aria2-Pro-Docker/


