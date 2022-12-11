import json
import requests
import meilisearch
import os
import re
# import sys
# sys.path.append('..')
import time
import urllib
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.flac import Picture, FLAC
from config import aria2
from modules.control import run_rclone
from bs4 import BeautifulSoup
from cls import LocalFile, NetFile, StrText

def searchbooksFromAnna(kword):
    jsontext = {'books':[]}
    html = 'https://annas-archive.org/search?lang=&content=&ext=&sort=&q='+ kword
    html = NetFile.url_to_str(html, 20, 20)
    # <div class="h-[125] " id="link-index-4">
    # <a href="/md5/c8f7aef49e49c406604bc919d29095a4" class="custom-a flex items-center relative left-[-10] px-[10] py-2 hover:bg-[#00000011] ">
    # <div class="flex-none">
    # <div class="relative overflow-hidden w-[72] h-[108] flex flex-col justify-center">
    #     <div class="absolute w-[100%] h-[90]" style="background-color: hsl(20deg 43% 73%)"></div>
    #     <img class="relative inline-block" src="https://libgen.rs/covers/2878000/c8f7aef49e49c406604bc919d29095a4-g.jpg" alt="" referrerpolicy="no-referrer"/>
    # </div>
    # </div>
    # <div class="relative top-[-1] pl-4 grow overflow-hidden">
    # <div class="truncate text-xs text-gray-500">Chinese, pdf, 6.7MB, &#34;俞平伯：红楼梦研究.pdf&#34;</div>
    # <div class="truncate text-xl font-bold">红楼梦研究</div>
    # <div class="truncate text-sm">人民文学出版社, 红楼梦, 1988</div>
    # <div class="truncate italic">俞平伯</div>
    # </div>
    # </a>
    # </div>
    # datalen = len(data)
    i = 0
    for j in html.split('<div class="h-[125] "'):
        try:
            if(j.find('id="link-index-') > -1 and i < 30):
                zid = StrText.get_str_btw(j, 'id="link-index-', '"', 0)
                md5 = StrText.get_str_btw(j, '<a href="/md5/', '"', 0)
                title = StrText.get_str_btw(j, '<div class="truncate text-xl font-bold">', '</div>', 0)
                author = StrText.get_str_btw(j, '<div class="truncate italic">', '</div>', 0)
                description = StrText.get_str_btw(j, '<div class="truncate text-sm">', '</div>', 0)
                other = StrText.get_str_btw(j, '<div class="truncate text-xs text-gray-500">', '</div>', 0)
                oth = other.split(', ')
                language = oth[0]
                extension = oth[1]
                publisher = description.split(', ')[0]
                cid = ''
                if('ipfs_cid' in j.keys()):
                    cid = j['ipfs_cid']
                    if(len(cid) >= 46 and md5 != None):
                        jsontext['books'].append({'zid': str(zid), 'md5': md5, 'title': title, 'author': author, 'language': language, 'publisher': publisher, 'description': description, 'extension': extension, 'cid': cid})
        except Exception as ex:
            print(f"{ex}")
    jsontext = json.dumps(jsontext)
    print('Book-47:\n' + jsontext)
    return jsontext

def searchbooks(kword):
    jsontext = {'books':[]}
    #client = meilisearch.Client('http://127.0.0.1:7700', 'masterKey')
    client = meilisearch.Client('https://meilisearch.zhelper.xyz/', '873886ed6df3af862751efa31334a6a3c3150ce04b77fe7b5bf0194e38d9a6c4')
    # An index is where the documents are stored.
    index = client.index('books')
    #data = index.search(kword, {'sort': ['zlibrary_id:desc']})['hits']
    data = index.search(kword)['hits']
    # datalen = len(data)
    for j in data:
        try:
            zid = j['zlibrary_id']
            md5 = j['md5']
            if(md5 == None):
                md5 = j['md5_reported']
            title = j['title']
            author = j['author']
            language = j['language']
            publisher = j['publisher']
            description = j['description']
            extension = j['extension']
            if('ipfs_cid' in j.keys()):
                cid = j['ipfs_cid']
                if(len(cid) >= 46 and md5 != None):
                    jsontext['books'].append({'zid': str(zid), 'md5': md5, 'title': title, 'author': author, 'language': language, 'publisher': publisher, 'description': description, 'extension': extension, 'cid': cid})
        except Exception as ex:
            print(f"{ex}")
    jsontext = json.dumps(jsontext)
    print('Book-47:\n' + jsontext)
    return jsontext

def libgenmd5tocid(md5):
    cid = ''
    try:
        if (len(md5) == 32):
            #http://libgen.li/file.php?md5=a9f92fe4291763110bb4beed8e70d18c
            html = NetFile.url_to_str('http://library.lol/main/' + md5.upper(), 20, 20)
            if(html != ''):
                cid = StrText.get_str_btw(html, 'https://ipfs.io/ipfs/', '"', 0)
    except Exception as e:
        print(f"{e}")
    return cid

def onebook_6803_all(sip, kword):
    jsontext = json.dumps({'books':[]})
    try:
        kword = f'http://' + sip +  ':6803/' + kword
        jsontext = NetFile.url_to_str(kword, 60, 60)
    except Exception as e:
        print(f'Book-60-Exception:{e}')
    return jsontext
    
def md5_json_anna(md5):
    jsontext = {'books':[]}
    try:
        if (len(md5) == 32):
            zid = 0
            title = ''
            author = ''
            publisher = ''
            description = ''
            extension = ''
            language = ''
            year = ''
            cid = ''
            url = 'https://annas-archive.org/md5/' + md5.upper()
            html = NetFile.url_to_str(url, 20, 20)
            if(html != ''):
                title = StrText.get_str_btw(html, '<div class="text-xl font-bold">', '</div>', 0)
                author = StrText.get_str_btw(html, '<div class="italic">', '</div>', 0)
                description = StrText.get_str_btw(html, '<div class="mt-4 line-clamp-[6]">', '</div>', 0)

                other = StrText.get_str_btw(html, '<div class="text-xs text-gray-500">', '</div>', 0)
                oth = other.split(', ')
                language = oth[0]
                extension = oth[1]
                publisher = StrText.get_str_btw(html, '<div class="text-sm">', '</div>', 0).split(', ')[0]

                cid = StrText.get_str_btw(html, 'https://ipfs.io/ipfs/', '"', 0)
                cid = cid.split('?')[0]

                if(len(cid) >= 46):
                    jsontext['books'].append({'zid': str(zid), 'md5': md5, 'title': title, 'author': author, 'language': language, 'year': year, 'publisher': publisher, 'description': description, 'extension': extension, 'cid': cid})
    except Exception as e:
        print(f"{e}")
    # jsontext = json.dumps(jsontext)
    return jsontext

def md5_json_libgen(md5):
    jsontext = {'books':[]}
    try:
        if (len(md5) == 32):
            zid = 0
            title = ''
            author = ''
            publisher = ''
            description = ''
            extension = ''
            language = ''
            year = ''
            cid = ''
            #url = 'http://libgen.li/file.php?md5=' + md5.upper()
            url = 'http://library.lol/main/' + md5.upper()
            html = NetFile.url_to_str(url, 20, 20)
            if(html != ''):
                cid = StrText.get_str_btw(html, 'https://ipfs.io/ipfs/', '"', 0)
                extension = cid.rsplit('.', 1)[1]
                cid = cid.split('?')[0]
                title = StrText.get_str_btw(html, '<h1>', '</h1>', 0)
                author = StrText.get_str_btw(html, 'Author(s):', '</p>', 0)
                if(len(cid) >= 46):
                    jsontext['books'].append({'zid': str(zid), 'md5': md5, 'title': title, 'author': author, 'language': language, 'year': year, 'publisher': publisher, 'description': description, 'extension': extension, 'cid': cid})
    except Exception as e:
        print(f"{e}")
    # jsontext = json.dumps(jsontext)
    return jsontext

def md5_to_book(sip, md5):
    rejsontext = {'books':[]}
    try:
        md5 = md5.lower()
        ustat = NetFile.url_stat(f'https://annas-archive.org/search', 6, 6)
        if(ustat == 200):
            jsontext = md5_json_anna(md5)
        else:
            jsontext = md5_json_libgen(md5)
        if(len(jsontext['books']) == 0):
            jsontext = onebook_6803_all(sip, md5)
            jsontext = json.loads(jsontext)
            # if(len(jsontext['books']) == 0):
            #     jsontext = onebook_6803_all(md5)
            #     jsontext = json.loads(jsontext)
        # 检测的记录存在时，则赋值返回
        if(len(jsontext['books']) > 0):
            rejsontext = jsontext
    except Exception as e:
        print(f"{e}")
    rejsontext = json.dumps(rejsontext)
    return rejsontext

def bookslist_libgen_all(kword):
    jsontext = {'books':[]}
    try:
        url = f'https://libgen.is/search.php?req=' + urllib.parse.quote(kword, safe='/') + '&lg_topic=libgen&open=0&view=simple&res=25&phrase=1&column=def'
        #url = f'http://localhost/1.txt'
        ustat = NetFile.url_stat(url, 6, 6)
        if(ustat == 200):
            html = NetFile.url_to_str(url, 20, 20)
            html = StrText.get_str_btw(html, '<table width=100% cellspacing=1 cellpadding=1 rules=rows', '</tr></table>', 1)
            soup = BeautifulSoup(html, 'html.parser')
            title_url_Date=soup.find('table', width='100%').find_all('tr')
            for one in title_url_Date:
                zid = 0
                md5 = ''
                title = ''
                author = ''
                publisher = ''
                description = ''
                extension = ''
                language = ''
                cid = ''
                try:
                    one = str(one).replace('"', '\'')
                    md5 = StrText.get_str_btw(one, '<a href=\'book/index.php?md5=', '\'', 0)
                    title = StrText.get_str_btw(one, '<a href=\'book/index.php?md5=', '</a>', 1)
                    title = re.sub('<[^<]+?>', '', title).replace('\n', '').strip()
                    author = StrText.get_str_btw(one, 'author\'>', '</a>', 0)
                    one = one.replace(' ', '').replace('nowrap=\'\'', '').replace('nowrap', '').replace('</td>', '<td>').split('<td>')
                    if(isinstance(one[1], int)):
                        zid = one[1]
                    language = one[12]
                    extension = one[16]
                    publisher = one[6]
                    if(len(md5) == 32):
                        jsontext['books'].append({'zid': str(zid), 'md5': md5, 'title': title, 'author': author, 'language': language, 'publisher': publisher, 'description': description, 'extension': extension, 'cid': cid})
                except Exception as ex:
                    text = f'Book-116-Exception：{ex}'
                    print(text)
                    LocalFile.write_LogFile(text)
    except Exception as ex:
        text = f'Book-121-Exception：{ex}'
        print(text)
        LocalFile.write_LogFile(text)
    #return json.dumps(jsontext)
    jsontext = json.dumps(jsontext)
    print(f'Book-122-jsontext：{jsontext}')
    LocalFile.write_LogFile('Book-Line-123-jsontext:' + str(jsontext))
    return jsontext

def searchbookshtml(name):
    zid = 0
    md5 = ''
    title = ''
    author = ''
    publisher = ''
    description = ''
    extension = ''
    language = ''
    cid = ''
    jsontext = {'books':[]}
    ustat = NetFile.url_stat(f'https://ss.zhelper.net/search/1231', 6, 6)
    if(ustat == 200):
        html = NetFile.url_to_str('https://ss.zhelper.net/search/1231', 20, 20)
        html = StrText.get_str_btw(html, '<ol class="list-group list-group-flush">', '</ol>', 1)
        soup=BeautifulSoup(html, 'html.parser')
        title_url_Date=soup.find('ol',class_='list-group list-group-flush').find_all('li')
        for one in title_url_Date:
            try:
                one = str(one)
                title = StrText.get_str_btw(one, '<b class="card-title">', '</b>', 0)
                author = StrText.get_str_btw(one, '作者：', '，', 0)
                publisher = StrText.get_str_btw(one, '出版社：', '，', 0)
                one = StrText.get_str_btw(one, 'value="', '"', 0)
                extension = one.rsplit('.', 1)[1]
                # zid = one.rsplit('_', 1)[1].split('.', 1)[0]
                md5 = one.split('#')[0]
                if (len(md5) == 32):
                    html = NetFile.url_to_str('http://library.lol/main/' + md5.upper(), 20, 20)
                    if(html != ''):
                        cid = StrText.get_str_btw(html, 'https://ipfs.io/ipfs/', '"', 0)
                if(cid != '' or len(md5) == 32):
                    jsontext['books'].append({'zid': str(zid), 'md5': md5, 'title': title, 'author': author, 'language': language, 'publisher': publisher, 'description': description, 'extension': extension, 'cid': cid, 'url': nodeurl})
            except Exception as e:
                print(f"{e}")
    return json.dumps(jsontext)

# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 5.8; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
#     "cookie": "__remember_me=true; MUSIC_U=f5798cb7775288f521fdcc5e3ce3df53b94446c1f5306aea19f4b0354b15433833a649814e309366; __csrf=b23ac1873ea3b243dbd6412b488600b1; NMTID=00O-ApuqR6H-n1NEEJFpS0RgQBBbVwAAAF6OLF0aw"
# }
# book_list_url = f"https://benchaonetease.vercel.app/playlist/detail?id={playlist}"
# print(book_list_url)
# book_list_info = requests.get(url=book_list_url, headers=headers)

def progress(current, total,client,message,name):
    print(f"{current * 100 / total:.1f}%")
    pro=f"{current * 100 / total:.1f}%"
    try:
        client.edit_message_text(chat_id=message.chat.id,message_id=message.message_id,text=f"{name}\n上传中:{pro}")
    except Exception as ex:
        print(f"{ex}")

def progessbar(new, tot):
    """Builds progressbar
    Args:
        new: current progress
        tot: total length of the download
    Returns:
        progressbar as a string of length 20
    """
    length = 20
    progress = int(round(length * new / float(tot)))
    percent = round(new/float(tot) * 100.0, 1)
    bar = '=' * progress + '-' * (length - progress)
    return '[%s] %s %s\r' % (bar, percent, '%')

def get_free_space_mb():
    result=os.statvfs('/root/')
    block_size=result.f_frsize
    total_blocks=result.f_blocks
    free_blocks=result.f_bfree
    # giga=1024*1024*1024
    giga=1000*1000*1000
    total_size=total_blocks*block_size/giga
    free_size=free_blocks*block_size/giga
    print('total_size = %s' % int(total_size))
    print('free_size = %s' % free_size)
    return int(free_size)

def hum_convert(value):
    value=float(value)
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return "%.2f%s" % (value, units[i])
        value = value / size

async def search_book_list(client, message):
    try:
        keyword = message.text.split(" ", 1)[1]
        search_book_url = f"https://benchaonetease.vercel.app/search?keywords={keyword}"
        search_book_info = requests.get(url=search_book_url)
        print(search_book_info.json()['result']['books'])
        num = 1
        new_inline_keyboard=[]
        temp_list=[]
        text=f"图书搜索结果:\n"
        for a in list(search_book_info.json()['result']['books']):
            print(f"{num}-`{a['name']}-{a['artists'][0]['name']}`\n")
            text=text+f"{num}-`{a['name']}-{a['artists'][0]['name']}`\n"
            temp_list.append(InlineKeyboardButton(
                    text=f"{num}",
                    callback_data=f"editbook {a['id']}"
                ))
            if num%5==0:
                new_inline_keyboard.append(temp_list)
                temp_list=[]
            if num==15:
                break
            num=num+1
        new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
        await client.send_message(text=text, chat_id=message.chat.id, parse_mode='Markdown', reply_markup=new_reply_markup)
    except Exception as e:
        text=f"search_book_list error:·{e}·"
        print(text)
        await client.send_message(text=text, chat_id=message.chat.id, parse_mode='Markdown')

async def edit_book_info(client, call):
    message_id = call.message.message_id
    message_chat_id = call.message.chat.id
    client.answer_callback_query(callback_query_id=call.id, text="开始获取图书信息", cache_time=3)
    try:
        keywords = str(call.data)
        book_id = int(keywords.split(" ")[1])
        book_name_info_url = f"https://benchaonetease.vercel.app/book/detail?ids={book_id}"
        book_name_info = requests.get(url=book_name_info_url)
        book_name = book_name_info.json()['books'][0]['name']
        author=book_name_info.json()['books'][0]['ar'][0]['name']
        book_img=book_name_info.json()['books'][0]['al']['picUrl']
        new_inline_keyboard = [
            [
                InlineKeyboardButton(
                    text="上传到网盘",
                    callback_data=f"neteaserclone {book_id}"
                ),
                InlineKeyboardButton(
                    text="发送给我",
                    callback_data=f"neteasetg {book_id}"
                )

            ]
        ]
        new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
        await client.send_photo(caption=f"图书:`{book_name}`\n歌手:`{author}`", photo=str(book_img), chat_id=message_chat_id,
                          parse_mode='Markdown', reply_markup=new_reply_markup)
    except Exception as e:
        print(f"edit_book_info error {e}")
        await client.edit_message_text(text=f"获取图书信息失败 {e}`", chat_id=message_chat_id,
                                 message_id=message_id,
                                 parse_mode='Markdown')

def add_flac_cover(filename, albumart):
    audio = File(filename)
    image = Picture()
    image.type = 3
    if albumart.endswith('png'):
        mime = 'image/png'
    else:
        mime = 'image/jpg'
    image.desc = 'front cover'
    with open(albumart, 'rb') as f:  # better than open(albumart, 'rb').read() ?
        image.data = f.read()

    audio.add_picture(image)
    audio.save()

def http_downloadbook(client, message,url, file_name,picpath,towhere):
    path="/books/"
    if not os.path.exists(path):   # 看是否有该文件夹，没有则创建文件夹
         os.mkdir(path)
    info = client.send_message(chat_id=message.chat.id, text="添加任务", parse_mode='Markdown')
    start = time.time()  # 下载开始时间
    response = requests.get(url, stream=True)
    size = 0  # 初始化已下载大小
    chunk_size = 1024  # 每次下载的数据大小
    content_size = int(response.headers['content-length'])  # 下载文件总大小
    try:
        if response.status_code == 200:  # 判断是否响应成功
            print('Start download,[File size]:{size:.2f} MB'.format(
                size=content_size / chunk_size / 1024))  # 开始下载，显示下载文件大小
            filepath = path + file_name  # 设置图片name，注：必须加上扩展名
            temp = time.time()
            with open(filepath, 'wb') as file:  # 显示进度条
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    size += len(data)
                    if int(time.time())-int(temp) > 1:
                        text=f'{file_name}\n'+'[下载进度]:%.2f%%' % ( float(size / content_size * 100))
                        client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                                 parse_mode='Markdown')
                        temp = time.time()
        end = time.time()  # 下载结束时间
        text = f'{file_name}\n' + f"大小:`{hum_convert(content_size)}`\n" + '[下载进度]:`%.2f%%`' % (
            float(size / content_size * 100))

        client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                 parse_mode='Markdown')
    except:
        print('Error!')
        return

    try:
        if "tg" in str(towhere):
            print("开始上传")

            client.send_audio(chat_id= info.chat.id,
                              audio=filepath,
                              caption=file_name,
                              file_name =file_name ,thumb=picpath,title=file_name ,progress=progress,
                                       progress_args=(client, info, file_name,))
            os.remove(filepath)
        elif "rclone" in str(towhere):

            run_rclone(filepath, "music", info=info, file_num=1, client=client, message=message,gid=0)
            os.remove(filepath)

    except Exception as e:
        print(e)
        print("Upload Issue!")

    return None

def downloadplaylist(client, call):
    info =  client.send_message(chat_id=call.message.chat.id, text="开始下载", parse_mode='Markdown')
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 5.8; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
        "cookie": "__remember_me=true; MUSIC_U=f5798cb7775288f521fdcc5e3ce3df53b94446c1f5306aea19f4b0354b15433833a649814e309366; __csrf=b23ac1873ea3b243dbd6412b488600b1; NMTID=00O-ApuqR6H-n1NEEJFpS0RgQBBbVwAAAF6OLF0aw"
    }
    playlist =str(call.data).split()[1]
    book_list_url = f"https://benchaonetease.vercel.app/playlist/detail?id={playlist}"
    print(book_list_url)
    book_list_info = requests.get(url=book_list_url, headers=headers)
    print(book_list_info.json())
    print(book_list_info.json()['playlist']['name'])
    book_list = list(book_list_info.json()['playlist']['trackIds'])
    book_id_list = []

    for a in book_list:
        book_id_list.append(str(a['id']))

    path = f"/playlist{playlist}/"
    if not os.path.exists(path):  # 看是否有该文件夹，没有则创建文件夹
        os.mkdir(path)
    for book_id in book_id_list:
        book_info_url = f"https://benchaonetease.vercel.app/book/url?id={book_id}"
        book_info = requests.get(url=book_info_url, headers=headers)
        try:
            if book_info.json()['data'][0]['url'] == None:
                client.edit_message_text(text=f"此图书不支持获取图书链接", chat_id=info.chat.id,
                                         message_id=info.message_id,
                                         parse_mode='Markdown')
                continue
            url = book_info.json()['data'][0]['url']
        except Exception as e:
            client.edit_message_text(text=f"无法获取刚获取图书链接:\n`{e}`", chat_id=info.chat.id,
                                         message_id=info.message_id,
                                         parse_mode='Markdown')
            continue

        book_name_info_url = f"https://benchaonetease.vercel.app/book/detail?ids={book_id}"
        book_name_info = requests.get(url=book_name_info_url)
        book_name = f"{book_name_info.json()['books'][0]['name']}.{str(book_info.json()['data'][0]['type']).lower()}"

        book_name=str(book_name).replace("\\", "").replace("/", "").replace('?', '').replace('*', '').replace('・', '').replace('！', '').replace('|', '').replace(' ', '')

        img_url = book_name_info.json()['books'][0]['al']['picUrl']
        img = requests.get(url=img_url)
        img_name = f"{info.chat.id}{info.message_id}.png"
        with open(img_name, 'wb') as f:
            f.write(img.content)
            f.close()
        picpath = img_name

        client.edit_message_text(chat_id=info.chat.id, message_id=info.message_id, text=f"{book_name}开始下载", parse_mode='Markdown')

        try:
            start = time.time()  # 下载开始时间
            response = requests.get(url, stream=True)
            size = 0  # 初始化已下载大小
            chunk_size = 2048  # 每次下载的数据大小
            content_size = int(response.headers['content-length'])  # 下载文件总大小
        
            if response.status_code == 200:  # 判断是否响应成功
                print('Start download,[File size]:{size:.2f} MB'.format(
                    size=content_size / chunk_size / 1024))  # 开始下载，显示下载文件大小
                filepath = path + book_name  # 设置图片name，注：必须加上扩展名
                temp = time.time()
                with open(filepath, 'wb') as file:  # 显示进度条
                    for data in response.iter_content(chunk_size=chunk_size):
                        file.write(data)
                        size += len(data)
                        if int(time.time()) - int(temp) > 1:
                            text = f'{book_name}\n'+f"大小:`{hum_convert(content_size)}`\n" + '[下载进度]:`%.2f%%`' % (float(size / content_size * 100))
                            client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                                     parse_mode='Markdown')
                            temp = time.time()

            end = time.time()  # 下载结束时间
            text = f'{book_name}下载完成,times: %.2f秒' % (end - start)  # 输出下载用时时间
            client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                     parse_mode='Markdown')
            if "tg" in str(call.data):
                print("开始上传")

                client.send_audio(chat_id=info.chat.id,
                                  audio=filepath,
                                  caption=book_name,
                                  file_name=book_name, thumb=picpath, title=book_name, progress=progress,
                                  progress_args=(client, info, book_name,))
                os.remove(filepath)
                os.remove(picpath)
            else:
                os.remove(picpath)
        except Exception as e:
            print(f'Error! {e}')
            client.edit_message_text(text=f'Error! `{e}`', chat_id=info.chat.id,
                                         message_id=info.message_id,
                                         parse_mode='Markdown')
            continue

    if "rclone" in str(call.data):
        run_rclone(path, f"歌单{playlist}", info=info, file_num=2, client=client, message=info,gid=0)
        os.system(f"rm -rf \"{path}\"")
    if "tg" in str(call.data):
        client.send_message(chat_id=call.message.chat.id, text="上传结束", parse_mode='Markdown')

async def get_book_info(client, message):
    try:
        sip = '54.180.99.13'
        dealcont = message.text
        if(dealcont.find(' ') > -1):
            dealcont = dealcont.split()[1]
        if(dealcont.find('/book') > -1 and dealcont.find('_') > -1):
            dealcont = StrText.get_str_btw(dealcont, '/book', '_', 0)
        elif(dealcont.find('/book') > -1 and dealcont.find('_') == -1):
            dealcont = dealcont.replace('/book', '')
        dealcont = dealcont.strip('/')
        message.text = dealcont
        dealcont = str(dealcont)
        jsontext = ''
        if(len(dealcont) == 32):
            jsontext = md5_to_book(sip, dealcont)
        elif(len(dealcont) == 46 or len(dealcont) == 62):
            jsontext = onebook_6803_all(sip, dealcont)
        else:
            if(dealcont.isdigit() == True):
                print('dealcont:' + str(dealcont))
                jsontext = onebook_6803_all(sip, dealcont)
            else:
                ustat = NetFile.url_stat(f'https://annas-archive.org/search', 6, 6)
                if(ustat == 200):
                    jsontext = searchbooksFromAnna(dealcont)
                else:
                    jsontext = searchbooks(dealcont)
                #jsontext = bookslist_libgen_all(dealcont)
        text = book_text_all(sip, jsontext)
        # else:
        #     ustat = NetFile.url_stat(f'https://ss.zhelper.net/search/1231', 6, 6)
        #     if(ustat != 200):
        #         html = NetFile.url_stat('https://ss.zhelper.net/search/1231', 6, 6)
        print(text)
        # await client.send_message(text=text, chat_id=message.chat.id, parse_mode='Markdown')
    except Exception as ex:
        text = f'Book-500-Exception:：`' + ex + '`\ndealcont:' + dealcont
        print(text)
        # await client.edit_message_text(text=text, chat_id=message.chat.id, message_id=message.id, parse_mode='Markdown')
    await client.send_message(text=text, chat_id=message.chat.id, parse_mode='Markdown')

async def get_book_list_info(client, message):
    try:
        info =await client.send_message(chat_id=message.chat.id, text="开始获取歌单信息", parse_mode='Markdown')

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 5.8; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
            "cookie": "__remember_me=true; MUSIC_U=f5798cb7775288f521fdcc5e3ce3df53b94446c1f5306aea19f4b0354b15433833a649814e309366; __csrf=b23ac1873ea3b243dbd6412b488600b1; NMTID=00O-ApuqR6H-n1NEEJFpS0RgQBBbVwAAAF6OLF0aw"
        }
        playlist = message.text.split()[1]
        book_list_url = f"https://benchaonetease.vercel.app/playlist/detail?id={playlist}"
        print(book_list_url)
        book_list_info = requests.get(url=book_list_url, headers=headers)
        #print(book_list_info.json())
        book_json=book_list_info.json()
        #print(book_list_info.json()['playlist']['name'])
        book_list = list(book_json['privileges'])
        book_id_text = ""
        num = 1
        list_num = len(book_json['playlist']['trackIds'])
        print(f"图书数:{list_num}")
        for a in book_list:
            if num < len(book_list):
                book_id_text = book_id_text + str(a['id']) + ","
            else:
                book_id_text = book_id_text + str(a['id'])
            num = num + 1
        print(book_id_text)

        book_name_info_url = f"https://benchaonetease.vercel.app/book/detail?ids={book_id_text}"
        book_name_info = requests.get(url=book_name_info_url, headers=headers)
        print(book_name_info.json())
        book_info_list = list(book_name_info.json()['books'])

        num = 1
        text=f"歌单名称:`{book_list_info.json()['playlist']['name']}`\n" \
             f"图书数:`{list_num}`\n" \
             f"只显示前15条\n"
        for a in book_info_list :

            text=text+f"{num}-`{a['name']}-{a['ar'][0]['name']}`\n"
            if num==15:
                break
            num=num+1

        new_inline_keyboard = [
            [
                InlineKeyboardButton(
                    text="上传到网盘",
                    callback_data=f"playlistrclone {playlist}"
                ),
                InlineKeyboardButton(
                    text="发送给我",
                    callback_data=f"playlisttg {playlist}"
                )
            ]
        ]
        new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
        await client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                 parse_mode='Markdown', reply_markup=new_reply_markup)
    except Exception as e:
        print(f"get_book_info error {e}")
        await client.send_message(text=f"获取歌单信息失败 {e}`", chat_id=message.chat.id,
                                 message_id=message.id,
                                 parse_mode='Markdown')

def book_text_all(sip, check_book_info):
    try:
        book_info = json.loads(check_book_info)['books']
        if(len(book_info) == 1):
            text = book_text_one(sip, book_info)
        elif(len(book_info) > 1):
            text = book_text_list(sip, book_info)
        else:
            text = f'📚 Unfortunately, nothing has been found on your request 🙁'
    except Exception as ex:
        text = f'Book-600-Exception:`' + str(ex) + '`\ncheck_book_info:\n' + str(check_book_info)
        print(text)
        LocalFile.write_LogFile(text)
        text = f'📚 600-网络连接有问题，已反馈管理员，可稍候再试。'
    return text

def book_text_one(sip, check_book_info):
    try:
        zid = int(check_book_info[0]['zid'])
        md5 = check_book_info[0]['md5']
        title = check_book_info[0]['title'].title()
        author = check_book_info[0]['author']
        publisher = check_book_info[0]['publisher']
        description = check_book_info[0]['description']
        extension = check_book_info[0]['extension']
        language = check_book_info[0]['language'].title()
        year = ''
        if('year' in check_book_info[0].keys()):
            year = check_book_info[0]['year']
        cid = check_book_info[0]['cid']
        fileurl = 'http://' + sip +  ':6805/?https://ipfs.io/ipfs/' + cid
        # 检测更优质的IPFS节点
        if(len(cid) >= 46):
            fileurl = 'http://' + sip +  ':6805/?https://ipfs.io/ipfs/' + cid
        elif(len(md5) == 32):
            cid = libgenmd5tocid(md5)
            if(len(cid) >= 46):
                fileurl = 'http://' + sip +  ':6805/?https://ipfs.io/ipfs/' + cid
        filename = ''
        if(extension != ''):
            if(title != ''):
                filename = '?filename=' + title.replace(' ', '_').replace('(', '（').replace(')', '）') + '.' + extension
            else:
                filename = '?filename=' + cid + '.' + extension
        fileurl = fileurl + filename
        if(len(description) > 4000):
            description = description[:4000]
        text = f'📚 **`{title}`**\n{description} \n{author} {publisher}\n🌐 {language} {year}\n[{md5}.{extension}]({fileurl})'
    except Exception as ex:
        text=f'📚 601-获取图书信息失败:`{ex}`'
        print(text)
    return text

def book_text_list(sip, book_json):
    text = ''
    try:
        book_list = list(book_json)
        num = 1
        list_num = len(book_list)
        print(f"图书数:{list_num}")
        # 检查数据库是否通畅，ustat == 200 是正常
        ustat = NetFile.url_to_str('http://' + sip +  ':6803/', 5, 5)
        for a in book_list:            
            #zid = int(a['zid'])
            md5 = a['md5']
            title = a['title'].title()
            author = a['author']
            publisher = a['publisher']
            #description = a['description']
            extension = a['extension']
            language = a['language'].title()
            cid = a['cid']
            text = text + f'📚 **`' + title + '`**\n' + author + ' ' + publisher + '\n🌐 ' + language
            
            ustat = NetFile.url_stat(f'https://annas-archive.org/search', 6, 6)
            if(ustat == 'index' or cid == '' or ustat == 200):
                text = text +  '\n/' + md5
            else:
                filename = ''
                if(extension != ''):
                    if(title != ''):
                        filename = '?filename=' + title.replace(' ', '_').replace('(', '（').replace(')', '）') + '.' + extension
                    else:
                        filename = '?filename=' + cid + '.' + extension
                text = text +  '\n[/' + md5 + '](http://' + sip +  ':6805/https://ipfs.io/ipfs/' + cid + '' + filename + ')'
            if('filesize' in a.keys()):
                text = text + ' (' + extension + ', ' + StrText.bytes_conversion(float(a['filesize'])) + ')'
            text = text +  '\n\n'
            if(num == 15):
                break
            num = num + 1
        text = text.strip('\n\n')
    except Exception as ex:
        text = f'Book-700-Exception:' + str(ex) + '\nbook_json:' + book_json
        LocalFile.write_LogFile(text)
    print(text)
    return text