"""JSONの内容をはてなブックマークにインポートする."""
import sys
import json
import hatena_api

if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)
    if argc < 6:
        print("Usage #python %s userid password consumer_key consumer_secret jsonファイル1 [jsonファイル2 ...]" % argvs[0])
        exit()
    user_id = argvs[1]
    password = argvs[2]
    consumer_key = argvs[3]
    consumer_secret = argvs[4]
    bookmarked = []

    api = hatena_api.HatenaApi()
    api.authorize(user_id, password, consumer_key, consumer_secret, "write_public")

    for path in argvs[5:]:
        print(path, "-----------------------------------------------")
        with open(path,'r') as f:
            data_list = json.load(f)
            for data in data_list:
                if not data['url'] in bookmarked:
                    print(data['title'])
                    tags = data['tag']
                    tags.append("Qiita")
                    res = api.add_bookmark(data['url'], tags=tags)
                    res.raise_for_status()
