"""Qiita APIを操作する.

QiitaAPIについては下記を参照してください。
https://qiita.com/api/v2/docs
"""

import json
import math
import requests


class QiitaApi:
    """QiitaAPIを操作するクラス."""

    _access_token = ''
    QIITA_API_URL = 'https://qiita.com'

    def __init__(self, access_token):
        self._access_token = access_token

    @staticmethod
    def _query_all_page(query_method, param):
        result = []
        per_page = 100
        total_count, result = query_method(param, per_page, 1)
        loop_count = math.ceil(int(total_count) / per_page)
        for page in range(2, loop_count + 1):
            total_count, items = query_method(param, per_page, page)
            if not items:
                break
            result.extend(items)
        return result

    def query_user_items(self, user_id):
        """ユーザが投稿した記事をすべて取得する

        Args:
            user_id (string): ユーザID

        Returns:
            array: 記事情報

        """
        return self._query_all_page(self._query_user_items_page, user_id)

    def _query_user_items_page(self, user_id, per_page, page):
        headers = {
            "Content-Type": "application/json",
            "charset": "UTF-8",
            "Authorization": "Bearer " + self._access_token
        }
        res = requests.get(
            "{baseUrl}/api/v2/items?per_page={per_page}&page={page}&query=+user%3A{user_id}".format(
                baseUrl=self.QIITA_API_URL,
                per_page=per_page,
                page=page,
                user_id=user_id),
            headers=headers)
        if res.status_code != 200:
            raise Exception(res.status_code, res.reason)
        items = json.loads(res.text)
        return res.headers["Total-Count"], items

    def query_comments(self, item_id):
        """指定の記事に紐づくコメントをすべて取得する

        Args:
            user_id (string): 記事のID

        Returns:
            array: コメント情報

        """
        return self._query_all_page(self._query_comments_page, item_id)

    def _query_comments_page(self, item_id, per_page, page):
        headers = {
            "Content-Type": "application/json",
            "charset": "UTF-8",
            "Authorization": "Bearer " + self._access_token
        }
        res = requests.get(
            "{baseUrl}/api/v2/items/{item_id}/comments?per_page={per_page}&page={page}".format(
                baseUrl=self.QIITA_API_URL,
                per_page=per_page,
                page=page,
                item_id=item_id),
            headers=headers)
        if res.status_code != 200:
            raise Exception(res.status_code, res.reason)
        items = json.loads(res.text)
        return res.headers["Total-Count"], items

    def query_stokers(self, item_id):
        """指定の記事をストックしたユーザをすべて取得する

        Args:
            user_id (string): 記事のID

        Returns:
            array: ユーザ情報

        """
        return self._query_all_page(self._query_stokers_page, item_id)

    def _query_stokers_page(self, item_id, per_page, page):
        headers = {
            "Content-Type": "application/json",
            "charset": "UTF-8",
            "Authorization": "Bearer " + self._access_token
        }
        res = requests.get(
            "{baseUrl}/api/v2/items/{item_id}/stockers?per_page={per_page}&page={page}".format(
                baseUrl=self.QIITA_API_URL,
                per_page=per_page,
                page=page,
                item_id=item_id),
            headers=headers)
        if res.status_code != 200:
            raise Exception(res.status_code, res.reason)
        items = json.loads(res.text)
        return res.headers["Total-Count"], items
