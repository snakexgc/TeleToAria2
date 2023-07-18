import asyncio
import datetime
import shutil
import aria2p

import python_socks
from telethon import TelegramClient, events, Button

from aria2client import Aria2Client
from util import *

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

JSON_RPC_URLS = os.getenv('JSON_RPC_URLS')
JSON_RPC_PORTS = os.getenv('JSON_RPC_PORTS')
JSON_RPC_TOKENS = os.getenv('JSON_RPC_TOKENS')

JSON_RPC_URL = os.getenv('JSON_RPC_URL')
JSON_RPC_TOKEN = os.getenv('JSON_RPC_TOKEN')

SEND_ID = int(os.getenv('SEND_ID'))
# 可选配置
PROXY_IP = os.getenv('PROXY_IP', None)
PROXY_PORT = os.getenv('PROXY_PORT', None)

if PROXY_PORT is None or PROXY_IP is None:
    proxy = None
else:
    proxy = (python_socks.ProxyType.HTTP, PROXY_IP, int(PROXY_PORT))

bot = TelegramClient(None, API_ID, API_HASH, proxy=proxy).start(bot_token=BOT_TOKEN)

# 自定义目录绝对路径
out_dir = ''
# 是否默认目录
is_def_dir = True

ar: Aria2Client = Aria2Client(JSON_RPC_URL, JSON_RPC_TOKEN, bot)


# 入口
async def main():
    await ar.init()
    ar.client.onDownloadStart(ar.on_download_start)
    ar.client.onDownloadPause(ar.on_download_pause)
    ar.client.onDownloadComplete(ar.on_download_complete)
    ar.client.onDownloadError(ar.on_download_error)
    bot.add_event_handler(BotCallbackHandler)
    print('bot启动了')


def get_menu():
    return [
        [
            Button.text('⬇️正在下载',resize=True),
            Button.text('⌛️ 正在等待',resize=True),
            Button.text('✅ 已完成/停止',resize=True)
        ],
        [
            Button.text('⏸️暂停任务',resize=True),
            Button.text('▶️恢复任务',resize=True),
            Button.text('❌ 删除任务',resize=True),
        ],
        [
            Button.text('❌ ❌ 清空已完成/停止',resize=True),
            Button.text('关闭键盘',resize=True),
        ],
    ]


# 内联按钮回调===============
@events.register(events.CallbackQuery)
async def BotCallbackHandler(event):
    # 按钮点击后的回调
    # print(event.data)
    d = str(event.data, encoding="utf-8")
    [type, gid] = d.split('.', 1)
    if type == 'pause-task':
        await pause(event, gid)
    elif type == 'unpause-task':
        await unpause(event, gid)
    elif type == 'del-task':
        await delToTask(event, gid)


# 消息监听开始===============
@bot.on(events.NewMessage(pattern='/menu', from_users=SEND_ID))
async def send_welcome(event):
    await event.respond('请选择一个选项', parse_mode='html', buttons=get_menu())


@bot.on(events.NewMessage(pattern="/close"))
async def handler(event):
    await event.reply("键盘已关闭", buttons=Button.clear())


@bot.on(events.NewMessage(pattern="/start"))
async def handler(event):
    await event.reply("aria2控制机器人,点击复制你的send_id:<code>%s</code>" % (str(event.chat_id)), parse_mode='html')


@bot.on(events.NewMessage(pattern="/help"))
async def handler(event):
    await event.reply('''
开启菜单: <code>/menu</code>
关闭菜单: <code>/close</code>
    ''', parse_mode='html')


@bot.on(events.NewMessage(from_users=SEND_ID))
async def send_welcome(event):
    text = event.raw_text
    print(str(datetime.datetime.now()) + ':' + text)
    if ar.client is None or ar.client.closed:
        # 重启客户端
        await ar.init()
    # 键盘消息
    if text == '⬇️正在下载':
        await downloading(event)
        return
    elif text == '⌛️ 正在等待':
        await waiting(event)
        return
    elif text == '✅ 已完成/停止':
        await stoped(event)
        return
    elif text == '⏸️暂停任务':
        await stopTask(event)
        return
    elif text == '▶️恢复任务':
        await unstopTask(event)
        return
    elif text == '❌ 删除任务':
        await removeTask(event)
        return
    elif text == '❌ ❌ 清空已完成/停止':
        await removeAll(event)
        return
    elif text == '关闭键盘':
        await event.reply("键盘已关闭,/menu 开启键盘", buttons=Button.clear())
        return

    exta_dic = dict()
    exta_dic['dir'] = out_dir

    # http 磁力链接
    if 'http' in text or 'magnet' in text:
        aria2 = aria2p.API(
            aria2p.Client(
                host=JSON_RPC_URLS,
                port=JSON_RPC_PORTS,
                secret=JSON_RPC_TOKENS
            )
        )
        download = aria2.add(text)

    try:
        if event.media and event.media.document:
            print(event.media.document.mime_type)
            if event.media.document.mime_type == 'application/x-bittorrent':
                print('收到了一个种子')
                await event.reply('收到了一个种子')
                path = await bot.download_media(event.message)
                print(path)

                gid = await ar.client.add_torrent(path, options=exta_dic, )
                print(gid)
                # os.unlink(path)
    except Exception as e:
        pass


# 消息监听结束===============


# 文本按钮回调方法=============================
async def downloading(event):
    tasks = await ar.client.tellActive()
    if len(tasks) == 0:
        await event.respond('没有正在运行的任务', parse_mode='html')
        return

    send_str = ''
    for task in tasks:
        completedLength = task['completedLength']
        totalLength = task['totalLength']
        downloadSpeed = task['downloadSpeed']
        fileName = getFileName(task)
        if fileName == '':
            continue
        prog = progress(int(totalLength), int(completedLength))
        size = byte2Readable(int(totalLength))
        speed = hum_convert(int(downloadSpeed))

        send_str = send_str + '任务名称: <b>' + fileName + '</b>\n进度: ' + prog + '\n大小: ' + size + '\n速度: ' + speed + '/s\n\n'
    if send_str == '':
        await event.respond('个别任务无法识别名称，请使用aria2Ng查看', parse_mode='html')
        return
    await event.respond(send_str, parse_mode='html')


async def waiting(event):
    tasks = await ar.client.tellWaiting(0, 30)
    # 筛选send_id对应的正在下载任务
    if len(tasks) == 0:
        await event.respond('没有正在等待的任务', parse_mode='markdown')
        return
    send_str = ''
    for task in tasks:
        completedLength = task['completedLength']
        totalLength = task['totalLength']
        downloadSpeed = task['downloadSpeed']
        fileName = getFileName(task)
        prog = progress(int(totalLength), int(completedLength))
        size = byte2Readable(int(totalLength))
        speed = hum_convert(int(downloadSpeed))

        send_str = send_str + '任务名称: ' + fileName + '\n进度: ' + prog + '\n大小: ' + size + '\n速度: ' + speed + '\n\n'
    await event.respond(send_str, parse_mode='html')


async def stoped(event):
    tasks = await  ar.client.tellStopped(0, 500)

    if len(tasks) == 0:
        await event.respond('没有已完成或停止的任务', parse_mode='markdown')
        return
    send_str = ''
    for task in tasks:
        completedLength = task['completedLength']
        totalLength = task['totalLength']
        downloadSpeed = task['downloadSpeed']
        fileName = getFileName(task)
        prog = progress(int(totalLength), int(completedLength))
        size = byte2Readable(int(totalLength))
        speed = hum_convert(int(downloadSpeed))

        send_str = send_str + '任务名称: ' + fileName + '\n进度: ' + prog + '\n大小: ' + size + '\n速度: ' + speed + '\n\n'
    await event.respond(send_str, parse_mode='html')


async def stopTask(event):
    tasks = await ar.client.tellActive()

    # 筛选send_id对应的正在下载任务
    if len(tasks) == 0:
        await event.respond('没有正在运行的任务,无暂停选项,请先添加任务', parse_mode='markdown')
        return
    # 拼接所有任务
    buttons = []
    for task in tasks:
        fileName = getFileName(task)
        gid = task['gid']
        buttons.append([Button.inline(fileName, 'pause-task.' + gid)])

    await event.respond('请选择要暂停⏸️的任务', parse_mode='html', buttons=buttons)


async def unstopTask(event):
    tasks = await ar.client.tellWaiting(0, 500)
    # 筛选send_id对应的任务
    if len(tasks) == 0:
        await event.respond('没有已暂停的任务,无法恢复下载', parse_mode='markdown')
        return
    buttons = []
    for task in tasks:
        fileName = getFileName(task)
        gid = task['gid']
        buttons.append([Button.inline(fileName, 'unpause-task.' + gid)])

    await event.respond('请选择要恢复▶️的任务', parse_mode='html', buttons=buttons)


async def removeTask(event):
    tempTask = []
    # 正在下载的任务
    tasks = await ar.client.tellActive()
    for task in tasks:
        tempTask.append(task)
    # 正在等待的任务
    tasks = await  ar.client.tellWaiting(0, 1000)
    for task in tasks:
        tempTask.append(task)
    if len(tempTask) == 0:
        await event.respond('没有正在运行或等待的任务,无删除选项', parse_mode='markdown')
        return

    # 拼接所有任务
    buttons = []
    for task in tempTask:
        fileName = getFileName(task)
        gid = task['gid']
        buttons.append([Button.inline(fileName, 'del-task.' + gid)])
    await event.respond('请选择要删除❌ 的任务', parse_mode='html', buttons=buttons)


async def removeAll(event):
    # 过滤 已完成或停止
    tasks = await   ar.client.tellStopped(0, 500)

    if len(tasks) == 0:
        await event.respond('没有要清空的任务', parse_mode='html')
        return

    for task in tasks:
        await  ar.client.removeDownloadResult(task['gid'])
        dir = task['dir']

    try:
        print('清空目录 ', dir)
        shutil.rmtree(dir, ignore_errors=True)
    except Exception as e:
        print(e)
        pass
    await event.respond('任务已清空,所有文件已删除', parse_mode='html')


# 文本按钮回调方法结束=============================


# 调用暂停
async def pause(event, gid):
    await  ar.client.pause(gid)


# 调用恢复
async def unpause(event, gid):
    await  ar.client.unpause(gid)


# 调用删除
async def delToTask(event, gid):
    await  ar.client.remove(gid)
    await bot.send_message(SEND_ID, '任务删除成功')


loop = asyncio.get_event_loop()
try:
    loop.create_task(main())
    loop.run_forever()
except KeyboardInterrupt:
    pass
