# 月曜1限 ネットワークプログラミング特論 最終課題
先取り履修を行った上記科目の課題です。

# システムの構造

## 使った技術
1. サーバ用API(Discord API)
2. サーバ用API(バスの時刻表 API)

## 全体の構造
(既にBotをDiscordサーバ(Discordアプリケーション内のチャンネルの集合体)に呼んでおり、アプリケーションも起動しているものとする)
1. ユーザが```/stat```または```/univ```コマンドを入力する
2. Discordのサーバがアプリケーションに通知を行う
3. 受け取ったアプリケーションはコマンドによって処理を行う
4. 処理の結果をDiscordのサーバに送信する
5. DiscordのサーバはDiscordサーバ(チャンネルの集合体)に結果を表示させる
6. ユーザが結果を閲覧できる

## 細かな工夫した点
- Token流出を発生させないために```config.ini```を作成した
- logを出力することでエラーが起きたときに気づけるようにした

## 使用した外部パッケージ
- Discord.py
- bs4
