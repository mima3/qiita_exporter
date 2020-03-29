"""WORDPRESSの操作"""
import json
import os
import base64
import requests


class WordPressError(Exception):
    """WordPressのエラー情報"""
    def __init__(self, ctrl, status_code, reason, message):
        super(WordPressError, self).__init__()
        self.ctrl = ctrl
        self.status_code = status_code
        self.reason = reason
        self.message = message


class WordPressCtrl:
    """WordPressの操作"""

    def __init__(self, url, user, password):
        """初期化処理"""
        self.url = url
        auth_str = f"{user}:{password}"
        auth_base64_bytes = base64.b64encode(auth_str.encode(encoding='utf-8'))
        self.auth = auth_base64_bytes.decode(encoding='utf-8')

    def check_response(self, res, success_code):
        """WordPressからの応答をチェック"""
        try:
            json_object = json.loads(res.content)
        except ValueError as ex:
            print(res)
            raise WordPressError(self, res.status_code, res.reason, str(ex))
        if res.status_code != success_code:
            print(res)
            raise WordPressError(self, res.status_code, res.reason, json_object['message'])
        return json_object

    def add_post(self, title, content, categorie_ids=[], tag_ids=[]):
        """WordPressに記事を投稿"""
        headers = {
            'Authorization': 'Basic ' + self.auth
        }
        data = {
            'title': title,
            'content': content,
            'format': 'standard',
            'categories' : categorie_ids,
            'tags' : tag_ids
        }
        res = requests.post(f'{self.url}/wp-json/wp/v2/posts', json=data, headers=headers)
        return self.check_response(res, 201)

    def update_post(self, id, title, content, categorie_ids=[], tag_ids=[]):
        """WordPressの既存記事を更新"""
        headers = {
            'Authorization': 'Basic ' + self.auth
        }
        data = {
            'title': title,
            'content': content,
            'format': 'standard',
            'categories' : categorie_ids,
            'tags' : tag_ids
        }
        res = requests.post(f'{self.url}/wp-json/wp/v2/posts/{id}', json=data, headers=headers)
        return self.check_response(res, 200)

    def upload_media(self, path, content_type):
        """メディアのアップロード"""
        file_name = os.path.basename(path)
        headers = {
            'Authorization': 'Basic ' + self.auth,
            'Content-Type': content_type,
            'Content-Disposition' : 'attachiment; filename={filename}'.format(filename=file_name)
        }
        with open(path, 'rb') as media_file:
            data = media_file.read()
        res = requests.post(f'{self.url}/wp-json/wp/v2/media', data=data, headers=headers)
        return self.check_response(res, 201)

    def upload_png(self, path):
        """メディアにPNG画像を追加"""
        return self.upload_media(path, 'image/png')

    def upload_jpeg(self, path):
        """メディアにJPEG画像を追加"""
        return self.upload_media(path, 'image/jpeg')

    def upload_gif(self, path):
        """メディアにGIF画像を追加"""
        return self.upload_media(path, 'image/gif')

    def _get_tags_page(self, page):
        """WordPressのタグを取得"""
        headers = {
            'Authorization': 'Basic ' + self.auth
        }
        res = requests.get(f'{self.url}/wp-json/wp/v2/tags?per_page=100&page={page}', headers=headers)
        return self.check_response(res, 200)

    def get_tags(self):
        """WordPressのタグを取得"""
        result = []
        page = 1
        while True:
            res = self._get_tags_page(page)
            if not res:
                return result
            result.extend(res)
            page = page + 1

    def add_tag(self, name):
        """WordPressにタグを追加"""
        headers = {
            'Authorization': 'Basic ' + self.auth
        }
        data = {
            'name': name
        }
        res = requests.post(f'{self.url}/wp-json/wp/v2/tags', json=data, headers=headers)
        return self.check_response(res, 201)


    def get_categories(self):
        """WordPressのカテゴリを取得"""
        headers = {
            'Authorization': 'Basic ' + self.auth
        }
        res = requests.get(f'{self.url}/wp-json/wp/v2/categories', headers=headers)
        return self.check_response(res, 200)

    def add_category(self, name):
        """WordPressにカテゴリーを追加"""
        headers = {
            'Authorization': 'Basic ' + self.auth
        }
        data = {
            'name': name
        }
        res = requests.post(f'{self.url}/wp-json/wp/v2/categories', json=data, headers=headers)
        return self.check_response(res, 201)

