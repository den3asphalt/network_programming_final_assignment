# パッケージ読み込み
import discord
import configparser
import logging
import requests
import json
import datetime


# 設定ファイルの読み込み
config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')

# ログの設定
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')


# クライアントの作成
intents = discord.Intents.default()
client = discord.Client(intents=intents)
commands = discord.app_commands.CommandTree(client)

# バスのデータ用URL
url_bus = "http://bus.shibaura-it.ac.jp/db/bus_data.json"

# 詳しくはここを参照
# http://bus.shibaura-it.ac.jp/developer.html

# バスのデータ入手
def get_data() -> dict:
    """
        バスのデータを取得する関数

        Returns
        -------
        dict
            バスのデータ
    """
    response = requests.get(url_bus)            # データ取得
    data = response.json()                      # json形式に変換
    json_data = json.dumps(data, indent=4, ensure_ascii=False)  # json形式に変換
    return json_data

async def bus(flag:bool,
              now_hour:int = datetime.datetime.now().hour, 
              now_minute:int = datetime.datetime.now().minute) -> str:
    """
    次のバスのデータを取得する関数

    Parameters
    ----------
    flag : bool
        大学行きか駅行きかのフラグ \n
        大学行きの場合はTrue, 駅行きの場合はFalse
    hour : int
        時間 \n
        入力されない場合は現在の時間を取得
    minute : int
        分 \n
        入力されない場合は現在の分を取得

    Returns
    -------
    str
        次のバスのデータ
    """

    # 返却するデータ
    mes:str = ""

    
    all_data:dict = calender["list"]    # 全てのバスデータ
    hour_data:dict                      # 時間ごとのデータ
    bus_data:dict                       # バスのデータ  
    
    

    # これからバスがある場合
    if now_hour < 7:
        now_hour = 7
    
    # 今日はもうバスがない場合
    if now_hour > 22:
        return "バスはありません"
    else:
        hour_data = all_data[now_hour-7]

    # 大学行きの場合
    if flag:
        bus_data = hour_data["bus_left"]
    else:
        bus_data = hour_data["bus_right"]

    # 間隔を狭めている時のデータ
    memo:str = hour_data["memo1"]

    # 間隔を狭めているとき
    if "間隔を狭めて" in memo:

        # ～より間隔を狭めて
        # ～まで間隔を狭めて
        # 上の組み合わせのみ
        before:int = 0
        after:int = 59

        # より
        if "より" in memo:
            before = int(memo.split("より")[0].split(":")[1])

        # まで
        if "まで" in memo:
            after = int(memo.split("まで")[1].split(":")[1])

        # 今の分が間隔を狭めている時間内の場合
        if before <= now_minute and now_minute <= after:
            return memo

    # 間隔を狭めていない時 or 狭めている範囲ではない時
    min_data:list = [int(i) for i in bus_data["num2"].split(".")]

    minute = 0

    # 次のバスのデータを取得
    for i in min_data:
        if now_minute < i:
            minute = i
            break
    
    if minute == 0:
        return await bus(flag, now_hour+1, 0)

    # メッセージの作成
    if flag:
        mes = f"次の大学行きバスは{minute}分です"
    else:
        mes = f"次の駅行きバスは{minute}分です"

    return mes

# 起動時に動作する処理
@client.event
async def on_ready() -> None:
    print("Discord Bot is ready...")
    # コマンドの登録
    await commands.sync()

# univコマンド実行時の処理
@commands.command(name="univ", description="次の大学行きバスを取得します")
async def univ(interaction: discord.Interaction) -> None:
    
    # メッセージの作成
    mes = await bus(True)

    # メッセージの送信
    await interaction.response.send_message(mes)


# statコマンド実行時の処理
@commands.command(name="stat", description="次の駅行きバスを取得します")
async def stat(interaction: discord.Interaction) -> None:
    
    # メッセージの作成
    mes = await bus(False)

    # メッセージの送信
    await interaction.response.send_message(mes)

# bot起動時にバスのデータ読み込み
calender = get_data()

client.run(config_ini['DISCORD']['TOKEN'], log_handler=handler)

