# docker-django
dockerを使用したDjango + MySQL + nginxの構成のwebアプリケーションのテンプレートリポジトリ

**このブランチは、Djangoプロジェクトの作成が終わり、サンプルアプリが作成されているもの**

## 使用方法
1. このリポジトリのmainブランチをclone
2. 以下の値が定義された.envファイルをrootディレクトリに作成
    - MYSQL_DATABASE_NAME
    - MYSQL_USER_NAME
    - MYSQL_USER_PASSWORD
    - MYSQL_ROOT_PASSWORD
3. rootディレクトリで`docker-compose run web django-admin startproject <任意のプロジェクト名> .`を実行し、Djangoのプロジェクトを作成
4. 以下の記述に従って、settings.pyを変更
    - [DjangoのDB設定の変更](https://github.com/ryutaro-kodama/docker-django/blob/main/document/document.md#django%E3%81%AEdb%E8%A8%AD%E5%AE%9A%E3%81%AE%E5%A4%89%E6%9B%B4)
    - [staticディレクトリの設定](https://github.com/ryutaro-kodama/docker-django/blob/main/document/document.md#static%E3%83%87%E3%82%A3%E3%83%AC%E3%82%AF%E3%83%88%E3%83%AA%E3%81%AE%E8%A8%AD%E5%AE%9A)
5. `docker-compose run web ./manage.py collectstatic`を実行(省略可)
6. docker-compose.ymlのコメントアウトを外し、"<任意のプロジェクト名>"を先ほど指定したプロジェクト名に置き換える
    - [docker-compose.yml#10](https://github.com/ryutaro-kodama/docker-django/blob/main/docker-compose.yml#L10)
7. `docker-compose up`を実行
    - `http://localhost:8000/`にアクセスし、ロケットが飛んでいればOK

## その他
- 詳細は[documant](https://github.com/ryutaro-kodama/docker-django/blob/main/document/document.md)を参照
- [docker_djangoブランチ](https://github.com/ryutaro-kodama/docker-django/tree/docker_django)にDjangoプロジェクト作成済みのソースコードあり
