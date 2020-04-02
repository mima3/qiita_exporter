"""
QiitaのLGTMの一覧を取得する。このスクリプトはAPIを利用していないため、リクエストに2秒ごとの待ち時間を入れている.
以下の記事も「いいね」取得のスクリプトであるが、2020年ではLGTM用のページがあるので、そこからとる.
https://qiita.com/lovemuffim114/items/a4760cfa9fc0fff15863
なお、2020/04時点で、APIでユーザに紐づくLGTMやLikeはとれない.
"""
from bs4 import BeautifulSoup
import requests
from time import sleep
import json
import sys


if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)
    if argc != 3:
        print("Usage #python %s [userid] [保存先ファイル]" % argvs[0])
        exit()
    user = argvs[1]
    dst_path = argvs[2]
    url_root = 'https://qiita.com'
    s = requests.Session()
    page = 1
    result = []
    while True:
        res = s.get("{}/{}/lgtms".format(url_root, user), params={"page":page})
        soup = BeautifulSoup(res.text, "html.parser")
        li_list = soup.select('li[class="LgtmArticleList__LgtmArticle-y1h1e7-4 lcYqW"]')
        if not li_list:
            break
        for li in li_list:
            rec = {}
            link = li.select('a[class="LgtmArticleList__ArticleTitle-y1h1e7-9 gwUuZt"]')[0]
            rec['title'] = link.text
            rec['url'] = url_root + link.attrs['href']
            rec['tag'] = []
            tags = li.select('a[class="LgtmArticleList__TagListTag-y1h1e7-6 lavYgU"]')
            for t in tags:
                rec['tag'].append(t.text)
            result.append(rec)
        page = page + 1
        sleep(2)

    with open(dst_path, mode='w', encoding='utf-8') as f:
        f.write(json.dumps(result, sort_keys = True, indent = 4))
