import qiita_api
import sys
import re
import urllib
import os


def fix_titlemiss(line):
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
    if len(line) < 3:
       return False
    if line[0:3] == '```':
       return True
    return False


def fix_newline(line):
    if line[-2:] == '  ':
        return line
    return line + '  '


def download(url, local_path):
    with urllib.request.urlopen(url) as web_file, open(local_path, 'wb') as download_file:
        download_file.write(web_file.read())


def fix_image(dst_folder, line):
    images = re.findall(r'https://qiita-image-store.+?\.(?:png|gif|jpeg|jpg)', line)
    if not images:
        return line
    for url in images:
        name = url.split("/")[-1]
        download(url, dst_folder + '/image/' + name)
        ix = line.find(url)

        line = line.replace(url, '/image/' + name)
    return line


def fix_markdown(dst_folder, body):
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

        # コードブロックの外では改行コードの後にスペースを２ついれる
        if not code_block_flg:
            line = fix_newline(line)

        result += line
        result += '\n'
    return result

if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)
    if argc != 4:
        print("Usage #python %s [userid] [accesstoken] [保存先フォルダ]" % argvs[0])
        exit()

    user = argvs[1]
    token = argvs[2]
    dst_folder = argvs[3]

    if not os.path.exists(dst_folder):
        os.mkdir(dst_folder)
    if not os.path.exists(dst_folder + '/image'):
        os.mkdir(dst_folder + '/image')

    qiitaApi = qiita_api.QiitaApi(token)

    items = qiitaApi.query_user_items(user)
    for i in items:
        text = fix_markdown(dst_folder, i['body'])
        with open(dst_folder + '/' + i['title'] + '.md', 'w' , encoding='utf-8') as md_file:
            md_file.write(text)

