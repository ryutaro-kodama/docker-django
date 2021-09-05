# Dockerを使ってDjango + uwsgi + nginx + mysqlの開発環境を構築

## 概要
Django + uwsgi + nginx + mysqlの環境をDockerを使って構築するステップを見ていきます。

メインで使用したのは以下のサイトです。
[docker-compose + Django + postgreSQL + nginxで開発環境を構築](https://www.macky-studio.com/entry/2019/07/01/132337)

## docker desktopのインストール
今回の話題の中心ではないため大幅に省略します。自分のPCのOSはWindowsであるため、以下のサイトを参考にWSL2とdocker desktopをインストールしました。
- WSL2のインストール
  - [Win10にWSL2とUbuntu 20.04をインストールする](https://astherier.com/blog/2020/07/install-wsl2-on-windows-10-may-2020/)
- docker desktopのインストール
  - [Windows 10＋WSL2環境にDocker Desktopをインストール](https://astherier.com/blog/2020/08/install-docker-desktop-on-windows10-with-wsl2/)

## Django + mysqlの開発環境をDockerで作成
まずはシンプルにDjango + mysqlの環境をDockerで作成します。

### ディレクトリ構成
```
.
├── .env
├── docker-compose.yml
├── mysql
│   ├── data
│   └── init
├── src
└── web
    ├── Dockerfile
    └── requirements.txt
```

### docker-compose.ymlの作成
docker-composeを使用して、serviceの基本の構成を作っていきます。

```yml:docker-compose.yml
version: "3"

services:
  web:
    build: ./web
    # command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./src:/code
    ports:
      - "8000:8000"
    depends_on:
      - db
    env_file:
      - .env

  db:
    container_name: mysql_db
    image: mysql:5.7
    restart: always
    volumes:
      - ./mysql/data:/var/lib/mysql
      - ./mysql/init:/docker-entrypoint-initdb.d
    ports:
      - 3306:3306
    environment:
      MYSQL_DATABASE: ${MYSQL_DATABASE_NAME}
      MYSQL_USER: ${MYSQL_USER_NAME}
      MYSQL_PASSWORD: ${MYSQL_USER_PASSWORD}
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      TZ: "Asia/Tokyo"
```
webコンテナにDjangoのコンテナを、dbコンテナにmysqlのコンテナを作成します。ポイントは以下の点です。
- web
  - `command: python manage.py runserver 0.0.0.0:8000`
    - コンテナ起動時に実行するコマンドを指定します
    - 今回はコンテナ起動時にDjangoの開発サーバーが自動で起動するようにします
      - 初回のコンテナ起動では、まだサーバーを動かさず、Djangoのプロジェクトを作成するだけなので、まずはコメントアウトしておきます。
  - `env_file: .env`
    - .envファイルの中身を展開し、そのコンテナの環境変数として設定します。
- db
  - `volumes: - ./src:/code`
    - HOSTの`./src`ディレクトリをGUESTコンテナの`/code`ディレクトリにマウントします
  - `volumes: - ./mysql/data:/var/lib/mysql`
    - HOSTの`./mysql/data`ディレクトリをGUESTコンテナの`/var/lib/mysql`ディレクトリにマウントします
    - dockerでDatabaseを使用した開発を行う際の注意点ですが、データベースのコンテナを停止させると、中身のデータも消えてしまうという問題があります。
      - そこでDatabase内のデータをコンテナの外部(HOSTのストレージ上)に保存しなくてはなりません。
      - このマウントによってHOSTの`./mysql/data`ディレクトリにデータが保存されるため、コンテナを停止してもデータが消える心配がなくなります
  - `volumes: - ./mysql/init:/docker-entrypoint-initdb.d`
    - HOSTの`./mysql/init`ディレクトリをGUESTコンテナの`/docker-entrypoint-initdb.d`ディレクトリにマウントします。
    - この`/docker-entrypoint-initdb.d`はmysql起動時にデータの初期化を行うスクリプトを保存しますが、今回は使用しません。
      - 参考: [Docker で MySQL 起動時にデータの初期化を行う](https://qiita.com/moaikids/items/f7c0db2c98425094ef10)
  - `environment: MYSQL_DATABASE: ${MYSQL_DATABASE_NAME}`
    - コンテナ内に環境変数を作成します。
    - その値は環境変数設定ファイル(.envファイル)から読み込むようにします。
      - MYSQL_USERやMYSQL_USER_PASSWORD, MYSQL_ROOT_PASSWORDも同じです
      - 参考: [Compose における環境変数](https://docs.docker.jp/compose/environment-variables.html)

### .envファイルの作成
先ほど、コンテナ内の環境変数を.envファイルから読み込むように設定したので、実際に.envファイルを作成します。

```.env:.env
MYSQL_DATABASE_NAME=<任意のDB名>
MYSQL_USER_NAME=<任意のMYSQLユーザー名>
MYSQL_USER_PASSWORD=<任意のMYSQLパスワード>
MYSQL_ROOT_PASSWORD=<任意のROOTユーザーMYSQLパスワード>
```

### Dockerfileの作成
webコンテナを作成するためのDockerfileを作成します。
```Dockerfile:web/Dockerfile
FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
```
python 3.8のイメージをベースに、requireents.txtから必要なモジュールをインストールします。

### requirements.txtの作成
Django等の必要なモジュールを定義します。
```txt:web/requirements.txt
Django==2.1.1
mysqlclient==1.4.6
```
mysqlclientはmysqlへの接続に必要なモジュールです。またdotenvはPythonスクリプトで.envファイルを読み込むことができるようになるモジュールです。

### Djangoプロジェクトの作成
以上の作成が終わったら、まずはDjangoのプロジェクトを作成します。
```
$ docker-compose run web django-admin startproject <任意のプロジェクト名> .
```
今回はdocker_djangoというプロジェクト名にします。実行後HOSTの`./src`ディレクトリ内が以下のようになっていれば完了です。
```
├── src
    ├── docker_django
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── manage.py
```

### DjangoのDB設定の変更
今作成されたsettings.pyにおいて、Djangoが使用するデータベースの設定を行います。
```py:src/docker_django/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get("MYSQL_DATABASE_NAME"),
        'USER': os.environ.get("MYSQL_USER_NAME"),
        'PASSWORD': os.environ.get("MYSQL_USER_PASSWORD"),
        'HOST': 'db',
        'PORT': '3306',
    }
}
```
mysqlへの接続に必要な情報は全て.envファイルから読み込みこむようにします。また`HOST`項目では`'db'`を設定します。ここがdocker-composeを使用して環境構築をする場合の注意点です。

(参考:[Can't connect to MySQL while building docker-compose image](https://stackoverflow.com/questions/57407940/cant-connect-to-mysql-while-building-docker-compose-image))

### 動作確認
このセクションの最後に動作確認を行います。docker-compose.ymlのwebコンテナのコマンドのコメントアウトを外しましょう。
```yml:docker-compose.yml
    # command: python manage.py runserver 0.0.0.0:8000
```

そして次のコマンドを、docker-compose.ymlがあるディレクトリで実行します。
```
$ docker-compose up
```
```
web_1     | Starting development server at http://0.0.0.0:8000/
web_1     | Quit the server with CONTROL-C.
```
のような出力を確認したのち、`http://localhost:8000/`にアクセスするとおなじみのDjangoのロケットの画面が出たら成功です。

## nginxの追加
続いて上で作成したserviceにnginxとuwsgiをを追加していきます。設定内容についてはこちらの記事がとても分かりやすかったので、参考にしていただきたいと思います。
(参考: [nginxでDjangoを使うときの設定ファイル：クライアント、nginx、uwsgiの流れを整理しよう](https://www.mathpython.com/ja/django-nginx-conf/))

### ディレクトリ構成
まずは以下のように、`nginx`ディレクトリ以下を作成します。

```
.
├── .env
├── docker-compose.yml
├── nginx                  // 追加
│   ├── conf               // 追加
│   │   └── nginx.conf     // 追加
│   └── uwsgi_params       // 追加
├── mysql
│   ├── data
│   └── init
├── src
│   └── static             // 追加
└── web
    ├── Dockerfile
    └── requirements.txt
```

### nginxの設定
docker-composeにnginx用のコンテナを作成します。
```yml:docker-compose.yml
services:
  web:
    build: ./web
    container_name: web
    command: uwsgi --socket :8001 --module <プロジェクト名>.wsgi  # 変更
    volumes:
      - ./src:/code
      - ./src/static:/static  # 追加
    expose:  # portsを削除してexposeを追加
      - "8001"
    depends_on:
      - db
    env_file:
      - .env

  # dbは変更なしのため省略

  # 以下は全て新規追加
  nginx:
    image: nginx:alpine
    container_name: nginx
    ports:
      - "8000:8000"
    volumes:
      - ./nginx/conf:/etc/nginx/conf.d
      - ./nginx/uwsgi_params:/etc/nginx/uwsgi_params
      - ./src/static:/static
    depends_on:
      - web
```
webコンテナのcommandsでは、先ほどはDjango内の開発用サーバーを起動するようにしていましたが、今回はuwsgiを起動するようにします。引数の`--module`の後には`<プロジェクト名>.wsgi`という形になるように値を指定してください。
(Djangoプロジェクトを作成した際にできたwsgi.pyを指定してあげます。作成したDjangoプロジェクトがdocker_djangoであれば`docker_django.wsgi`となります。)

nginxコンテナのvolumesでは、nginxのconfig情報、uwsgi_paramsの情報、staticファイルを入れるディレクトリをそれぞれマウントします。

次にnginxのconfigファイルを作成します。
```conf:nginx.conf
upstream django {
    ip_hash;
    server web:8001;
}

server {
    listen      8000;
    server_name 127.0.0.1;
    charset     utf-8;

    client_max_body_size 75M;

    location /static {
        alias /static;
    }

    location / {
        uwsgi_pass  django;
        include     /etc/nginx/uwsgi_params;
    }
}
```
簡単に中身を見ると、server_nameというIPアドレスの8000番ポートで要求を待ち、staticなリクエストであればnginxがレスポンスを返し、それ以外はDjangoにリクエストを投げている。

### uwsgiの追加
nginxとDjangoが通信をする橋渡し役としてuwsgiを使用します。pipを使用してインストールするため、requirements.txtに追加します。
```txt:requirements.txt
Django==2.1.1
mysqlclient==1.4.6
uwsgi==2.0.18         // 追加
```
そして再びbuildをし直します
```
$ docker-compose build
```

次にuwsgi_paramsファイルを作成します。これはnginxからuwsgiに渡される情報を定義しています。
```uwsgi_params
uwsgi_param  QUERY_STRING       $query_string;
uwsgi_param  REQUEST_METHOD     $request_method;
uwsgi_param  CONTENT_TYPE       $content_type;
uwsgi_param  CONTENT_LENGTH     $content_length;

uwsgi_param  REQUEST_URI        $request_uri;
uwsgi_param  PATH_INFO          $document_uri;
uwsgi_param  DOCUMENT_ROOT      $document_root;
uwsgi_param  SERVER_PROTOCOL    $server_protocol;
uwsgi_param  REQUEST_SCHEME     $scheme;
uwsgi_param  HTTPS              $https if_not_empty;

uwsgi_param  REMOTE_ADDR        $remote_addr;
uwsgi_param  REMOTE_PORT        $remote_port;
uwsgi_param  SERVER_PORT        $server_port;
uwsgi_param  SERVER_NAME        $server_name;
```

### staticディレクトリの設定
cssやjavascriptのファイルを読み込むためのstaticディレクトリですが、これをDjangoが正しく読み込むことができるようにsettings.pyの内容を変更します。

まずsettings.pyに以下の内容を追加した後、
```py:src/docker_django/settings.py
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
```
以下のコマンドを実行します。
```
$ docker-compose run web ./manage.py collectstatic
```

### 動作確認
再び動作確認を行います。次のコマンドを、docker-compose.ymlがあるディレクトリで実行します。
```
$ docker-compose up
```
`http://localhost:8000/`にアクセスするとおなじみのDjangoのロケットの画面が出たら成功です。

