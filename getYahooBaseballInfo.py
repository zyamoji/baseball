from bs4 import BeautifulSoup
import requests
import re
import time
import sqlite3
import pickle
PICKLE_PROTOCOL = pickle.HIGHEST_PROTOCOL

# 試合日
gameDate = "2019022406" # 試合の日付とその日の何試合目か

# 保存するSQLite DB
saveDBName = "baseballResult.db"

# アドレス解析用
r = re.compile("inn=([0-9]+)&tb=([0-9]+)&bat=([0-9]+)")

# 基準となるアドレス
url = "https://baseball.yahoo.co.jp/live/npb/game/"

inn = 1 # イニング
tb = 1  # 表裏
bat = 1 # 何人目のバッターか

# 取得アドレス構築
getUrl = url+str(gameDate)+"/score?inn="+str(inn)+"&tb="+str(tb)+"&bat="+str(bat)

# 結果を格納する辞書オブジェクト
ballHistory = {}
# 最初に取得するデータを初期化
ballHistory[str(inn)+"_"+str(tb)+"_"+str(bat)] = []

# SQLite接続
conn = sqlite3.connect(saveDBName)
c = conn.cursor()

# すべての打者に対してループ実行
while True:
    # アドレスからイニングと表裏、何人目のバッターか抽出
    m = r.search(getUrl)
    inn, tb, bat = m.group(1), m.group(2), m.group(3)
    # デバッグ用に表示
    print(m.group(1), m.group(2), m.group(3))
    # 取得するアドレス
    baseballPage = requests.get(getUrl)
    # BeautifulSoupで取得
    soup = BeautifulSoup(baseballPage.text, "html.parser")
    # 投球データ取得
    baseballIning = soup.select("#livedetail > #column-center  .mb20p tr td")
    ballHistory[str(inn)+"_"+str(tb)+"_"+str(bat)] = []

    # 投球コースを処理
    kindOfBall = soup.select("#kdL td")
    
    # 投球データを保存する辞書オブジェクト
    kindOfBallJson = {}

    # 投球データ
    kindOfBall = soup.select(".kyusyu-mark td")
    j = 1
    
    # 投球数の分だけ繰り返す
    for eachBall in kindOfBall:
        if eachBall.text != "":
            # 球数を保存
            ballNum = eachBall.text.count("\n")
            # 1球以下なら保存して終わり
            if ballNum <= 1:
                kindOfBallJson[eachBall.text[1:].strip()] = j
                pass
            # 複数球あれば都度保存
            else:
                tempBall = eachBall.text.split("\n")
                for i in range(ballNum):
                    kindOfBallJson[tempBall[i][1:]] = j
        j+=1
    
    i = 0
    eachBallDict = {}

    # 投球詳細データを処理
    for eachBall in baseballIning:
        if i%6 == 0: # 球種と打者への球数
            eachBallDict["kind"] = eachBall.text[:1]
            eachBallDict["ballForBatter"] = eachBall.text[1:]
            eachBallDict["course"] = kindOfBallJson[str(eachBallDict["ballForBatter"])]
            i+=1
        elif i%6 == 1: # 投手の投げた球数
            eachBallDict["totalBall"] = eachBall.text
            i+=1
        elif i%6 == 2: # 球種
            eachBallDict["ballName"] = eachBall.text
            i+=1
        elif i%6 == 3: # 球速
            eachBallDict["speed"] = eachBall.text
            i+=1
        elif i%6 == 4: # 結果
            eachBallDict["result"] = eachBall.text
            i+=1
        elif i%6 == 5: # BSOカウント
            countText = eachBall.text.split()
            eachBallDict["B"] = countText[0]
            eachBallDict["S"] = countText[1]
            eachBallDict["O"] = countText[2]

            ballHistory[str(inn)+"_"+str(tb)+"_"+str(bat)].append(eachBallDict.copy())

            eachBallDict = {}
            i+=1

    # 次へボタンを取得
    isNextButton = soup.find(id="btn_next")
    
    # 次へボタンが無ければ終了
    if not isNextButton.has_attr("href"):
        break

    # 次に取得するアドレス
    nextUrl = isNextButton["href"]
    print(nextUrl)
    
    # アドレスが無ければ終了
    if nextUrl == "":
        break
    else:
        getUrl = nextUrl

    # 1秒待つ
    time.sleep(1)

# 取得したオブジェクトを表示
print(ballHistory)

# 以下、試合の全体的なデータを取得

# アドレス
baseballPage = requests.get(getUrl)
soup = BeautifulSoup(baseballPage.text, "html.parser")
# スコアデータ取得
scoreboard = soup.select("#scoreboard > table > tbody > tr")
metaData = {}
metaData['date'] = gameDate

# 各チームのスコアを格納
for scoreIndex in range(1, 3):
    tempScore = []
    # ビジター
    if scoreIndex == 1:
        metaData['visitorTeam'] = scoreboard[scoreIndex].select('th')[0].text
        for inningScore in scoreboard[scoreIndex].select("td"):
            tempScore.append(inningScore.text)
        metaData[metaData['visitorTeam']] = tempScore
    # ホーム
    else:
        metaData['homeTeam'] = scoreboard[scoreIndex].select('th')[0].text
        for inningScore in scoreboard[scoreIndex].select("td"):
            tempScore.append(inningScore.text)
        metaData[metaData['homeTeam']] = tempScore

# デバッグ用に表示    
print(metaData)

# データ保存用関数
import bz2
# dbに格納
def ptoz(obj):
    return bz2.compress(pickle.dumps(obj, PICKLE_PROTOCOL), 3)

# dbから読み出し
def ztop(b):
    return pickle.loads(bz2.decompress(b)) 

# DBに接続
conn = sqlite3.connect(saveDBName)
c = conn.cursor()

# 挿入用SQL
# バイナリ化して入れる
insert_sql = "insert into baseballData (id, metaData, gotData) values (?, ?, ?)"
insert_objs = ballHistory
newList = []
newList.append(gameDate)
newList.append(ptoz(metaData))
newList.append(ptoz(ballHistory))

# 実行
print(len(pickle.dumps(ballHistory)))
c.execute(insert_sql, newList)
conn.commit()

# Closeすべきでは？