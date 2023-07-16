# aria2bot修复版--TeleToAria2

TeleToAria2

# 关于本仓库

本仓库是完全基于 https://github.com/jw-star/aria2bot 项目来的，用愚蠢的办法修复了 发送http链接进行下载时，如果文件名后有参数会导致下载文件名错误的情况，其核心代码完全来源于aria2bot，我只是做了部分修改！

因为修复方法过于愚蠢，所以我自己另开一个仓库，bug和我的解决方法均有和原作者沟通，期待之后原作者修复这个bug！

### 特点

1. 基于电报机器人控制aria2，自行设置下载完成后是否上传telegram
2. ~~多用户，每个用户只能看到自己的任务~~，单用户现在，多用户没什么用
3. 支持 `批量` 添加 http、磁力、种子下载
4. 支持自定义目录下载,使用 /path 命令设置


### 缺点

1. 由于电报单个文件2G限制,超过2g文件将上传失败

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
      JSON_RPC_PORTS: 6800  # 输入你aria2的端口，一般默认是6800
      JSON_RPC_URLS: "http://1.1.11.1"  # 按格式再次输入你aria2的链接，不带端口，切勿删除""
      JSON_RPC_TOKENS: "11111"  # 按格式再次输入你aria2的秘钥，切勿删除""
      SEND_ID: 11111  #可以启动bot后发送 /start 获取，或者转发消息给 @get_id_bot 
      #      PROXY_IP:   #可选  代理ip
      #      PROXY_PORT:  #可选 代理端口
      UP_TELEGRAM: 'False' #是否上传电报
```

2.启动


安装 docker

```
curl -fsSL get.docker.com -o get-docker.sh&&sh get-docker.sh &&systemctl enable docker&&systemctl start docker
```


拉取项目

```
git pull https://github.com/snakexgc/TeleToAria2.git
cd TeleToAria2
```

删除容器（如果容器存在）
```
docker rm -f tta
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

aria2 一键安装脚本

```yaml
https://github.com/P3TERX/aria2.sh
```

### 应用截图

/help  查看帮助

### 灵感来自

https://github.com/HouCoder/tele-aria2

https://github.com/synodriver/aioaria2

多平台构建参考: https://cloud.tencent.com/developer/article/1543689


