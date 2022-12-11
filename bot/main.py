#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from apscheduler.schedulers.background import BackgroundScheduler
import sys
from modules.book import get_book_info, md5_json_anna
# kword = '00acd068d438a3b088e0c94e5ea1eb90'
# kword = md5_json_anna(kword)
from modules.check import new_clock, second_clock
from config import client, Telegram_user_id, aria2,Error_user_info,App_title
from pyrogram.handlers import MessageHandler
from pyrogram import filters
from modules.control import check_upload, get_free_space_mb,odprivate_download
import datetime

starttime = datetime.datetime.now()

async def chexk_group(_, client, query):
    print("检查使用权限")
    #print(query)
    try:
        if("-" in str(Telegram_user_id)):
            info = await client.get_chat_member(chat_id=int(Telegram_user_id), user_id=query.from_user.id)
            sys.stdout.flush()
            return True
        else:
            # 仅限个人使用
            if(str(query.from_user.id) == str(Telegram_user_id)):
                return True
        # 不限制任何人使用
        return True
    except Exception as e:
        await client.send_message(chat_id=query.from_user.id, text=Error_user_info)
        print(f"获取权限失败：{e}")
        return False

async def help(client, message):
    print(client)
    print(message)
    text = '''
直接发送查询的关键词进行查询。'''
    try:
        await client.send_message(chat_id=int(message.chat.id), text=text)
    except Exception as e:
        print(f"help :{e}")


async def status(client, message):
    endtime = datetime.datetime.now()

    m, s = divmod(int((endtime - starttime).seconds), 60)
    h, m = divmod(m, 60)
    print("%02d时%02d分%02d秒" % (h, m, s))
    if h != 0:
        last_time = "%d时%d分%d秒" % (h, m, s)
    elif h == 0 and m != 0:
        last_time = "%d分%d秒" % (m, s)
    else:
        last_time = "%d秒" % s
    text = f"BOT正在运行,已运行时间:`{last_time}` 空间:`{get_free_space_mb()}GB`\n\n查询可直接发送以下类型消息:\nZlibraryID、图书MD5、图书IPFS的CID、书名、出版社等关键词。\n\n如果不能下载，请在本地电脑安装IPFS Desktop客户端，再将下载链接中的IP替换为127.0.0.1"
    await client.send_message(chat_id=message.from_user.id, text=text, parse_mode='Markdown')

def start_bot():
    # scheduler = BlockingScheduler()
    if App_title!="":
        scheduler = BackgroundScheduler()
        scheduler.add_job(new_clock, "interval", seconds=60)
        scheduler.add_job(second_clock, "interval", seconds=60)
        scheduler.start()
        print("StartBOT")
    sys.stdout.flush()
    if(Telegram_user_id != None):
        print("\nBOT-Master-ID: " + Telegram_user_id)
    else:
        print("\nBOT-Master-ID: 0")
    sys.stdout.flush()
    aria2.listen_to_notifications(on_download_complete=check_upload, threaded=True)

    start_message_handler = MessageHandler(
        status,
        filters=filters.command(["start"]) & filters.create(chexk_group) & filters.private
    )
    help_message_handler = MessageHandler(
        help,
        filters=filters.command(["help2"]) & filters.create(chexk_group) & filters.private
    )
    # 查询所有信息
    get_book_info_handler = MessageHandler(
        get_book_info,
        filters=filters.text & filters.create(chexk_group) & filters.private
    )

    odprivate_download_handler = MessageHandler(
        odprivate_download,
        filters=filters.command("odprivate") & filters.create(chexk_group) & filters.private
    )

    print(f"检查odprivate_download_handler -{App_title}-")
    if App_title == "":
        print("添加odprivate_download_handler")
        client.add_handler(odprivate_download_handler, group=1)

    client.add_handler(start_message_handler, group=1)
    client.add_handler(help_message_handler, group=1)
    client.add_handler(get_book_info_handler, group=1)

    client.run()

if __name__ == '__main__':
    start_bot()

