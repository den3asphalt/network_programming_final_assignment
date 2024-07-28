# パッケージ読み込み
import discord
import configparser
import logging
import requests
import datetime
from bs4 import BeautifulSoup


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
        バスのデータを取得する関数\n主に通信部分

        Returns
        -------
        dict
            バスのデータ
    """
    response:requests.Response = requests.get(url_bus)            # データ取得
    json_data:dict = response.json()                      # json形式で読み込み

    today_URL = "http://bus.shibaura-it.ac.jp/ts/today_sheet.php"
    response = requests.get(today_URL)            # データ取得

    # 今日のバスのデータのタイトルを取得する
    soup = BeautifulSoup(response.text, "html5lib")
    title_tag = soup.select_one("body > div.content.ts > h2")

    # アクセスできなかった場合？
    if title_tag is None:
        raise Exception("今日のバスのデータが取得できませんでした")
    
    # タイトルの取得
    title:str = title_tag.text

    time_sheet:list = json_data["timesheet"]

    # 返却するデータ
    data:dict

    for i in time_sheet:
        if i["title"].replace(" ", "") == title.replace(" ", ""):
            data = i["list"]
            break

    return data

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

    
    all_data:dict = calender    # 全てのバスデータ
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
    memo:str = bus_data["memo1"]

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
        
        # 狭めている範囲ではない時
        min_data:list = [int(i) for i in bus_data["num2"].split(".")]
    else:
        # 間隔を狭めていない時
        min_data:list = [int(i) for i in bus_data["num1"].split(".")]
     
    

    minute = 0

    # 次のバスのデータを取得
    for i in min_data:
        if now_minute < i:
            minute = i
            break
    
    # この時間にもうバスがない場合
    if minute == 0:
        return await bus(flag, now_hour+1, 0)

    # メッセージの作成
    if flag:
        mes = f"次の大学行きバスは{now_hour}:{minute}です"
    else:
        mes = f"次の駅行きバスは{now_hour}:{minute}です"

    return mes


@client.event
async def on_ready() -> None:
    """
        Botが起動したときに動作する関数
    """

    print("Discord Bot is ready...")
    # コマンドの登録
    await commands.sync()


@commands.command(name="univ", description="次の大学行きバスを取得します")
async def univ(interaction: discord.Interaction) -> None:
    """
        univコマンド実行時の処理
    """
    
    # メッセージの作成
    mes = await bus(True)

    # メッセージの送信 ephermal=Trueで自分だけに見える
    await interaction.response.send_message(mes, ephemeral=True)


@commands.command(name="stat", description="次の駅行きバスを取得します")
async def stat(interaction: discord.Interaction) -> None:
    """
        statコマンド実行時の処理
    """

    # メッセージの作成
    mes = await bus(False)

    # メッセージの送信 ephermal=Trueで自分だけに見える
    await interaction.response.send_message(mes, ephemeral=True)

# bot起動時にバスのデータ読み込み
calender = get_data()

# Botのトークン
TOKEN = config_ini['DISCORD']['TOKEN']

# Botの起動
client.run(TOKEN, log_handler=handler)

