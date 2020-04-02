"""Qiitaにて指定のユーザがストックしている記事をJSONで出力する."""
import sys
import re
import urllib
import os
import qiita_api
import json


if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)
    if argc != 4:
        print("Usage #python %s [userid] [accesstoken] [保存先ファイル]" % argvs[0])
        exit()

    user = argvs[1]
    token = argvs[2]
    dst_path = argvs[3]

    qiitaApi = qiita_api.QiitaApi(token)
    result = []
    items = qiitaApi.query_stock(user)
    for i in items:
        rec = {
            'title' : i['title'],
            'url' : i['url'],
            'tag' : []
        }
        for t in i['tags']:
            rec['tag'].append(t['name'])
        result.append(rec)

    with open(dst_path, mode='w', encoding='utf-8') as f:
        f.write(json.dumps(result, sort_keys = True, indent = 4))
