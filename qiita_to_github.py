"""Qiitaの記事をGitHubのマークダウンのファイルに出力する

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
import qiita_api


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


def fix_image(dst_folder, line):
    """Qiitaのサーバーの画像ファイルから自分のリポジトリのファイルを表示するように修正する."""
    images = re.findall(r'https://qiita-image-store.+?\.(?:png|gif|jpeg|jpg)', line)
    if not images:
        return line
    for url in images:
        name = url.split("/")[-1]
        download(url, dst_folder + '/image/' + name)
        ix = line.find(url)

        line = line.replace(url, '/image/' + name)
    return line


def fix_mypage_link(github_url, line, dict_title):
    """自分の記事へのURLを修正する"""
    for url in dict_title.keys():
        line = line.replace(url, github_url + '/' + dict_title[url] + '.md')
    return line


def fix_markdown(github_url, dst_folder, body, dict_title):
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
        line = fix_image(dst_folder, line)

        # コードブロックの外では以下の処理を行う
        # ・自分の記事へのリンクの修正
        # ・改行コードの後にスペースを２ついれる
        if not code_block_flg:
            line = fix_mypage_link(github_url, line, dict_title)
            line = fix_newline(line)

        result += line
        result += '\n'
    return result

if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)
    if argc != 5:
        print("Usage #python %s [userid] [accesstoken] [保存先フォルダ] [GitHubのブロブのルートURL ex.https://github.com/mima3/note/blob/master]" % argvs[0])
        exit()

    user = argvs[1]
    token = argvs[2]
    dst = argvs[3]
    github_url = argvs[4]

    if not os.path.exists(dst):
        os.mkdir(dst)
    if not os.path.exists(dst + '/image'):
        os.mkdir(dst + '/image')

    qiitaApi = qiita_api.QiitaApi(token)

    items = qiitaApi.query_user_items(user)
    dict_title = {}
    for i in items:
        dict_title[i['url']] = i['title']

    for i in items:
        text = fix_markdown(github_url, dst, i['body'], dict_title)
        with open(dst + '/' + i['title'] + '.md', 'w', encoding='utf-8') as md_file:
            md_file.write(text)
