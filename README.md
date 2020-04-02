# はじめに  
コンプライアンス的に黒いサービスに依存するのは、リスクだと思うので現在の記事を別サービスに移行するためのスクリプトです。 

以下の機能をサポートしています。

 - Qiitaの記事をGitHubに移行する
 - Qiitaの記事をWordPressに移行する
 - LGTMやストックについては、はてなブックマークに移行する。  

  
なお、私の記事は以下のようになりました。  

**元の記事**  
https://qiita.com/mima_ita

**GitHubへの移行のサンプル**  
https://github.com/mima3/note  

**WordPressへの移行のサンプル** 
http://needtec.sakura.ne.jp/wod07672/category/qiita%e3%81%8b%e3%82%89%e3%81%ae%e7%a7%bb%e8%a1%8c/


  
# 動作環境  
Python 3.7.4  
Windows10  

WordPress 5.3.2  
・[WP Githuber MD – WordPress Markdown Editor](https://wordpress.org/plugins/wp-githuber-md/)  
・[Application Passwords](https://ja.wordpress.org/plugins/application-passwords/)  

# 事前準備  
## Qiitaのアクセストークンの準備  
Qiitaのアクセストークンを取得します。  
  
(1)設定画面のアプリケーションタブから「新しいトークンを発行する」を押下します。  
  
![image.png](https://qiita-image-store.s3.amazonaws.com/0/47856/1027591c-3943-b695-c493-615457408997.png)  
  
(2)読み取り権限を付けて「発行」を押下します  
![image.png](https://qiita-image-store.s3.amazonaws.com/0/47856/cc957b75-91f7-9f5e-7fd8-2be56c38061f.png)  
  
(3)アクセストークンをメモしておきます  
![image.png](https://qiita-image-store.s3.amazonaws.com/0/47856/d28c2a4f-19a6-6255-7e30-3d1bbfaf2d42.png)  
  
## WordPressのRESTAPIを使用する準備  
以下を参照してください。  

https://github.com/mima3/note/blob/master/WordPress%E3%81%A7%E7%94%BB%E5%83%8F%E4%BB%98%E3%81%8D%E3%81%AE%E8%A8%98%E4%BA%8B%E3%82%92%E8%87%AA%E5%8B%95%E3%81%A7%E6%8A%95%E7%A8%BF%E3%81%99%E3%82%8B.md#%E4%BA%8B%E5%89%8D%E6%BA%96%E5%82%99

## はてなブックマークのOAuthAPIの準備  
以下を参照してください。  

http://needtec.sakura.ne.jp/wod07672/2020/04/02/%e3%81%af%e3%81%a6%e3%81%aa%e3%83%96%e3%83%83%e3%82%af%e3%83%9e%e3%83%bc%e3%82%af%e3%81%aerest-api%e3%82%92%e5%88%a9%e7%94%a8%e3%81%99%e3%82%8b/

# 使用方法  
## QiitaからGitHubへの移行方法
(1)以下のリポジトリからスクリプトを取得する  
https://github.com/mima3/qiita_exporter  
  
(2)下記の形式でスクリプトを実行する。  
  
```
python qiita_to_github.py [userid] [accesstoken] [保存先フォルダ] [GitHubのブロブのルートURL ex.https://github.com/mima3/note/blob/master]  
```  
  
(3)保存先フォルダをGitHubに登録します。  

## QiitaからWordPressへの移行方法
(1)以下のリポジトリからスクリプトを取得する  
https://github.com/mima3/qiita_exporter  
  
(2)下記の形式でスクリプトを実行する。  
  
```
python qiita_to_wp.py qiitaのユーザ名 qiitaのAPIキー WORDPRESSのURLex.https://needtec.sakura.ne.jp/wod07672 WORDPRESSのユーザ名 WORDPRESSのApplicationPassword カテゴリの名前
```

(3)しばらくすると処理が完了するのでWordPressの管理画面から記事を公開していく。  

## QiitaのLGTMとストックを、はてなブックマークに移行する方法
(1)LGTMをJSON形式でエクスポートします  

```
python export_qiita_lgtm.py QiitaのID lgtm.json
```

(2)ストックをJSON形式でエクスポートします  

```
python export_qiita_stock.py  QiitaのID "Qiitaのアクセストークン" stock.json
```

(3)作成したJSONを、はてなブックマークに登録します。

```
python import_hatena_bookmark.py はてなユーザID はてなパスワード はてなのConsumerKey はてなのConsumerSecret lgtm.json stock.json
```

ブックマークに登録の際、Qiitaの記事にあったタグのほかに[Qiita]というタグを付与して登録しています。

# やっていること  
・画像をローカルにダウロードして、リンクを書き換えます。  
・コードブロック以外の行にて、改行コードの前にスペース2ついれて改行を行います。  
・「#タイトル」という記述があったら「# タイトル」に直します。  
・コードブロックのタイトル（例：「```python:test.py」）が表示されないので対応します。  
・自分の記事へのURLを修正する  
・WordPressについてはタグも移行します。

