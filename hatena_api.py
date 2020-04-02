"""はてなREST APIを操作する.

はてなのRESTAPIについては下記を参照してください。
http://developer.hatena.com/ja/documents/bookmark/apis/rest

また、OAuthの認証方法については下記のページを参考にしています.
https://www.iruca21.com/entry/2017/05/24/090000
"""

import requests
# https://github.com/requests/requests-oauthlib
from requests_oauthlib import OAuth1Session

class HatenaApiError(Exception):
    """HatenaApiErrorのエラーが発生したことを知らせる例外クラス"""


class HatenaApi:
    """はてなAPIを操作するクラス."""
    LOGIN_URL = 'https://www.hatena.ne.jp/login'
    session = None

    def _get_rk(self, hatena_id, password):
        """はてなIDとログインパスワードからrkを取得します。
        以下のコードを利用しています
        https://www.iruca21.com/entry/2017/05/24/090000
        https://github.com/iruca/hatena-oauth-python/blob/master/get_access_token_util.py

        Args:
            hatena_id:  はてなID文字列
            password: はてなIDに対応するはてなログイン用のパスワード
        Returns:
            rk文字列
        Raises:
            HatenaApiError: rk文字列が取得できなかったとき。ID/パスワードが間違っているか、rkを取得するためのはてなAPIの仕様が変わった
        """
        payload = {'name': hatena_id, 'password': password}
        response = requests.post(self.LOGIN_URL, data=payload)
        if not "Set-Cookie" in response.headers:
            raise HatenaApiError("cannot get rk.ID/Password is wrong, or Hatena API spec changed.")
        if not "rk=" in response.headers['Set-Cookie']:
            raise HatenaApiError("cannot get rk.ID/Password is wrong, or Hatena API spec changed.")
        rk = response.headers["Set-Cookie"].split("rk=")[1].split(";")[0]
        return rk

    def _get_authorization_redirect_url(self, user_id, password, authorization_url):
        """authorization_urlにアクセスしてアプリケーションの許可を行う."""
        rk = self._get_rk(user_id, password)
        res_auth = requests.get(authorization_url, headers={"Cookie" : "rk="+ rk}).text
        rkm = res_auth.split("<input type=\"hidden\" name=\"rkm\" value=\"")[1].split("\"")[0]
        oauth_token = res_auth.split("<input type=\"hidden\" name=\"oauth_token\" value=\"")[1].split("\"")[0]
        res_redirect = requests.post(
            authorization_url,
            headers={"Cookie": "rk="+ rk},
            params={
                "rkm": rkm,
                "oauth_token": oauth_token,
                "name": "%E8%A8%B1%E5%8F%AF%E3%81%99%E3%82%8B"
            }
        )
        return res_redirect.url

    def authorize(self, user_id, password, consumer_key, consumer_secret, scope):
        """OAuth認証を行う.

        Args:
            hatena_id:  はてなID文字列
            password: はてなIDに対応するはてなログイン用のパスワード
            consumer_key: 「OAuth 開発者向け設定ページ」にて作成したアプリケーションのconsumer_key
            consumer_secret:「OAuth 開発者向け設定ページ」にて作成したアプリケーションのconsumer_secret
            scope : 取得権限. ex "read_public,write_public"
        """
        self.session = OAuth1Session(
            consumer_key,
            consumer_secret,
            callback_uri="http://localhost/hogehoge"  # このURLは実際にアクセスできる必要はありません.
        )
        self.session.fetch_request_token(
            "https://www.hatena.com/oauth/initiate?scope={}".format(scope)
        )
        authorization_url = self.session.authorization_url("https://www.hatena.ne.jp/oauth/authorize")
        redirect_response = self._get_authorization_redirect_url(
            user_id,
            password,
            authorization_url
        )
        self.session.parse_authorization_response(redirect_response)
        self.session.fetch_access_token("https://www.hatena.com/oauth/token")


    def add_bookmark(self, url, comment="", tags=None):
        """はてなブックマークの追加または更新を行う.
        このメソッドを実行する前に、authorizeを呼び出す必要がある.

        Args:
            url:  ブックマーク対象のURL
            comment: コメント
            tags: タグの一覧
        """
        if not self.session:
            raise HatenaApiError("call authorize method.")
        if tags:
            for t in tags:
                comment += "[{}]".format(t)
        return self.session.post(
            "https://bookmark.hatenaapis.com/rest/1/my/bookmark?url=",
            params={
                "url": url,
                "comment" : comment,
            }
        )
