"""Qiitaの記事をWordPressに移行する

以下のことをおこなっています。
・画像をローカルにダウロードして、リンクを書き換えます。
・コードブロック以外の行にて、改行コードの前にスペース2ついれて改行を行います。
・「#タイトル」という記述があったら「# タイトル」に直します。
・コードブロックのタイトル（例：「```python:test.py」）が表示されないので対応します。

"""
import sys
import re
import urllib
import os
import time
import qiita_api
from wordpress_ctrl import WordPressCtrl,WordPressError


def fix_titlemiss(line):
    """タイトルタグのスペースの入れ忘れを修正します."""
    if not line:
        return line
    if line[0] != '#':
        return line
    if "# " in line:
        return line
    # #から開始しているが、スペースで区切られていない
    result = ''
    sts = 0
    for s in line:
        if sts == 0 and s != '#':
            # #の後にスペースを挿入
            sts = 1
            result += " "
        result += s
    return result


def has_code_block_mark(line):
    """指定の行がコードブロックのタグ（```）か検査します."""
    if len(line) < 3:
        return False
    if line[0:3] == '```':
        return True
    return False


def fix_newline(line):
    """改行コードの前にスペースを2つ追加します."""
    if line[-2:] == '  ':
        return line
    return line + '  '


def download(url, local_path):
    """ファイルをダウンロードします."""
    with urllib.request.urlopen(url) as web_file, open(local_path, 'wb') as download_file:
        download_file.write(web_file.read())


def fix_image(line, dict_images):
    """Qiitaのサーバーの画像ファイルからWordPress上のファイルを表示するように修正する."""
    images = re.findall(r'https://qiita-image-store.+?\.(?:png|gif|jpeg|jpg)', line)
    if not images:
        return line
    for url in images:
        name = url.split("/")[-1]
        ix = line.find(url)

        line = line.replace(url, dict_images[name])
    return line


def fix_mypage_link(line, dict_url):
    """自分の記事へのURLを修正する"""
    for url in dict_url.keys():
        line = line.replace(url, dict_url[url])
    return line


def fix_markdown(body, dict_url, dict_images):
    """GitHubのマークダウンで表示できるように修正します."""
    result = ''
    lines = body.splitlines()
    code_block_flg = False
    for line in lines:
        if has_code_block_mark(line):
            code_block_flg = not code_block_flg
            if code_block_flg:
                # コードブロックのタイトルを修正
                ix = line.find(":")
                if ix != -1:
                    result += "**" + line[ix+1:] + "**  \n"
        line = fix_titlemiss(line)
        line = fix_image(line, dict_images)

        # コードブロックの外では以下の処理を行う
        # ・自分の記事へのリンクの修正
        if not code_block_flg:
            line = fix_mypage_link(line, dict_url)

        result += line
        result += '\n'
    return result


def retry_image_upload(wpctrl, path, count):
    result = None
    try:
        if path.endswith('.png'):
            result = wpctrl.upload_png(path)
        elif path.endswith('.gif'):
            result = wpctrl.upload_gif(path)
        elif path.endswith('.jpg'):
            result = wpctrl.upload_jpeg(path)
        elif path.endswith('.jpeg'):
            result = wpctrl.upload_jpeg(path)
        else:
            raise
        return result['guid']['raw']
    except:
        print('失敗したのでリトライを行う 残り：' + str(count))
        if count == 0:
            raise
        time.sleep(5)
        result = retry_image_upload(wpctrl, path, count-1)
        return result

if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)
    if argc != 7:
        print("Usage #python %s [Qiitaのuserid] [Qiitaのaccesstoken] [WordPressのurl] [WordPressユーザ名] [WordPressパスワード] [カテゴリ名]" % argvs[0])
        exit()

    user = argvs[1]
    token = argvs[2]
    wp_url = argvs[3]
    wp_user = argvs[4]
    wp_pass = argvs[5]
    category = argvs[6]

    wpctrl = WordPressCtrl(wp_url, wp_user, wp_pass)

    # QiitaAPIで記事の一覧を取得
    qiitaApi = qiita_api.QiitaApi(token)
    items = qiitaApi.query_user_items(user)

    # カテゴリの登録
    wp_categories = wpctrl.get_categories()
    category_id = None
    for c in wp_categories:
        if c['name'] == category:
            category_id = c['id']
    if not category_id:
        ret = wpctrl.add_category(category)
        category_id = ret['id']

    # Qiitaで使用したタグをWordPressに登録
    qiita_tags = []
    for i in items:
        for t in i['tags']:
            if not t['name'] in qiita_tags:
                qiita_tags.append(t['name'])
    wp_tags = wpctrl.get_tags()
    dict_wp_tags = {}
    for t in wp_tags:
        dict_wp_tags[t['name']] = t['id']
    for t in qiita_tags:
        if not t in dict_wp_tags.keys():
            ret = wpctrl.add_tag(t)
            dict_wp_tags[t] = ret['id']

    # 記事の登録
    dict_id = {}
    dict_url = {}

    # Qiitaで使用している画像の登録
    print('画像の登録中...')
    dict_images = {}
    for i in items:
        print(i['title'])
        images = re.findall(r'https://qiita-image-store.+?\.(?:png|gif|jpeg|jpg)', i['body'])
        if not images:
            continue
        for url in images:
            name = url.split("/")[-1]
            download(url, name)
            image_url = retry_image_upload(wpctrl, name, 3)
            dict_images[name] = image_url
            print(url + '->' + image_url)

    # 一旦タイトルだけで記事を作成
    print('記事の新規登録...')
    for i in items:
        print(i['title'])
        ret = wpctrl.add_post(i['title'], "# test\n仮登録")
        dict_id[i['id']] = ret['id']
        dict_url[i['url']] = ret['link']

    # 本文を修正
    print('記事の本文作成...')
    for i in items:
        print(i['url'])
        tag_list = []
        for t in i['tags']:
            tag_list.append(dict_wp_tags[t['name']])
        wp_id = dict_id[i['id']]
        contents = fix_markdown(i['body'], dict_url, dict_images)
        ret = wpctrl.update_post(wp_id, i['title'], contents, [category_id], tag_list)

    
    #
    #cnt = 0
    #for i in items:
    #    text = fix_markdown(github_url, dst, i['body'], dict_title)
    #    wpctrl.add_post("test1", "# test\ntest2")
    #    cnt = cnt + 1
    #    if i > 5:
    #        break
