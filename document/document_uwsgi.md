# uwsgi.iniを作成する
ここではuwsgiの起動時のコマンドラインオプション等を、uwsgi.iniファイルを作成して定義する方法を見ていきます。

## uwsgi.iniへの切り出し

### uwsgi.iniファイルの作成
まずはuwsgi.iniファイルを作成します。Webコンテナ内から見える場所がいいので、今回はwsgi.pyと同じディレクトリに作成します。

```ini:./src/docker_django/uwsgi.ini
chdir = /code
socket = :8001
module = docker_django.wsgi:application
```

先にdocker-compose.ymlのcommand部分で指定していたものをこちらに書き写しました。

### docker-compose.ymlの変更
次にこの作成したiniファイルを、webコンテナ起動時にuwsgiモジュールが実行するように指定します。

```yml:docker-compose.yml
services:
  web:
    build: ./web
    container_name: web
    command: uwsgi --ini /code/docker_django/uwsgi.ini  # 変更
```
`--ini`オプションの後に、iniファイルの場所を指定してあげます。Webコンテナ内の絶対パスで指定してあげるのが良いと思います。

### 動作確認
これで準備は完了です。`docker-compose up`を実行し、正しく起動することを確認してください。

## wsgiの手動リロードの実装
開発をしていて思ったのですが、exceptionがDjangoから送出されると、Djangoアプリケーションが停止してしまい、コンテナ自体を再起動しないと動かなくなってしまうようです。
しかしこれは開発効率が悪いので、手動でuwsgiをreloadし、Djangoを再起動できるようにします。（これでコンテナまで再起動する必要はなくなります。）

ここではuwsgiの`--touch-reload`オプションを使います。これは指定したファイルがtouchコマンド等で変更された場合、再びuwsgiを再起動するというものです。これを使って、HOSTから対象のファイルの変更を起こし、再起動を実現します。

### uwsgi.iniへの`--touch-reload`オプションの追記
先ほどのuwsgi.iniに`--touch-reload`オプションを追加します。

```ini:./src/docker_django/uwsgi.ini
chdir = /code
socket = :8001
module = docker_django.wsgi:application
touch-reload = /tmp/reload.triger    # 追加
```

これで`/tmp/reload.triger`が変更された場合、uwsgiの再起動が起こります。

### 再起動の実行
webコンテナが動作している状態で、実際に再起動を行ってみましょう。

まずは`docker-compose up`でコンテナを起動します。

次にもう1つterminalを開き、docker-compose.ymlのディレクトリに移動した後、次のコマンドを実行します。
```
$ docker-compose exec web touch /tmp/reload.triger
```
`docker-compose exec <コンテナ名> <実行コマンド>`で、該当のコンテナ内で指定されたコマンドを実行します。今回はコマンドが`touch /tmp/reload.triger`なので、上記の通りuwsgiの監視対象のファイルを書き換えます。
```
            *** /tmp/reload.triger has been touched... grace them all !!! ***
web       | ...gracefully killing workers...
```
のような出力が、`docker-compose up`を行った方のterminalで表示されたらOKです。