# Dockerでアプリケーションを新規作成する
環境構築ができたところで、Djangoのプロジェクト内にアプリケーションを作成していきます。

(参考: [https://qiita.com/maejima_f/items/85432868c9b10087e057](https://qiita.com/maejima_f/items/85432868c9b10087e057))

## アプリケーションの作成

### アプリケーションのひな型の作成
まずは下のコマンドを実行しましょう
```
$ docker-compose run web ./manage.py startapp <任意のアプリ名>
```
これだけでアプリのひな型が完成します。ここからはsample_appとして話を進めます

これによって`src`ディレクトリ以下に`sample_app`というディレクトリが出来たと思います。
```
.
├── src
│   ├── manage.py
│   ├── docker_django
│   ├── static
│   └── sample_app
│       ├── migrations
│       │   └── __init__.py
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── tests.py
│       └── views.py
```

### settings.pyの変更
`./src/docker_django/settings.py`の`INSTALLED_APPS`のリストの中に、今作成したアプリ名を追加します。(パス中の`docker_django`はプロジェクト名なので、常にこのパスとは限りません。)
```py:./src/docker_django/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'sample_app'    # 追加
]
```

### URLの登録
次にこのアプリにリクエストがあった場合、どのview(メソッド)を呼び出すかのルーティングを記述します。

まずプロジェクト名直下のディレクトリにある`urls.py`にアプリのルートURLの登録を行います。
```py:./src/docker_django/urls.py
from django.contrib import admin
from django.urls import include, path       # includeを追加

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sample_app/', include('sample_app.urls')),   # `<アプリ名>.urls`の文字列をincludeする
]
```
これで、各アプリ毎にルーティングをurls.pyに記述することで、それが読み込まれるようになりました。

そこで次に各アプリごとにルーティングを記述していきます。`./src/docker_django/sample_app`内に`urls.py`を新しく作成し、以下の内容を書き込みます
```py:./src/sample_app/urls.py
from django.urls import path
from . import views            # 同じディレクトリのviews.pyから全てのメソッドを読み込み

app_name = 'sample_app'        # ここは先ほど指定したアプリ名
urlpatterns = [
    path('', views.index, name='index'),    # URLに応じて、どのメソッドを呼び出すかを記載
]
```
以上により、URLと呼び出されるメソッドの対応付けができました。この例では、`localhost:8000/sample_app/`にアクセスがあった場合、views.pyのindexメソッドを呼び出すようになっています。`./src/docker_django/urls.py`で`path('', include('sample_app.urls'))`としたので、ここで定義したURLは`localhost:8000/`ではなく`localhost:8000/sample_app/`であることに注意してください。

### Templatesの作成
まずはディレクトリとhtmlファイルを追加します。
```
.
├── src
│   ├── manage.py
│   ├── docker_django
│   ├── static
│   ├── sample_app
│   └── templates
│       └── sample_app
│           └── index.html
```
srcディレクトリ以下にtemplatesディレクトリを作成し、sample_app/index.htmlを作成してください。

次に今作成したtemplates内にあるhtmlファイルを探すようにDjangoに教えてあげます。settings.pyの内容に以下を追加します。
```py:src/docker_django/settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],    # 変更
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```
これでDjangoプロジェクトのルートディレクトリ下のtemplatesというディレクトリ内にあるhtmlファイルを探すようになります。

また該当のindex.htmlは次のようにします
```html:./src/templates/sample_app/index.html
<!DOCTYPE html>
<html lang="ja">
    <head>
        <meta charset="utf-8">
        <title>Sample APP</title>
    </head>
    <body>
        <h3>{{ today }}</h3>
    </body>
</html>
```

### viewの作成
viewとは言いますが、MVCのモデルで言うところのコントローラーに当たると思います。要するにあるURLにアクセスがあった場合、どのような処理を行うかを定義する部分です。

今回は簡単のため、htmlファイルを読み込んで今日の日付をクライアント側に返すのみにします。
```py:./src/sample_app/views.py
from django.shortcuts import render

# Create your views here.

import datetime

def index(request):
    today = datetime.date.today()
    return render(request, 'sample_app/index.html', {'today': today})
```
詳細は省きますが、`templates/sample_app/inex.html`にあるhtmlファイルを返し、html側のtodayの部分に`today`変数の値を入れるようなメソッドになっています。


### 動作確認
ここまで終わったら、`docker-compose up`を実行してサーバーを立ち上げ、`localhost:8000/sample_app`を開いて見ましょう。今日の日付が表示されればOKです。