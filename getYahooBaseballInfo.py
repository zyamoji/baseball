from bs4 import BeautifulSoup
import requests
import re
import time
import sqlite3
import pickle
PICKLE_PROTOCOL = pickle.HIGHEST_PROTOCOL
saveDBName = "baseballResult.db"

r = re.compile("inn=([0-9]+)&tb=([0-9]+)&bat=([0-9]+)")

url = "https://baseball.yahoo.co.jp/live/npb/game/"
gameDate = "2019022406" # 試合の日付とその日の何試合目か
inn = 1 # イニング
tb = 1  # 表裏
bat = 1 # 何人目のバッターか
getUrl = url+str(gameDate)+"/score?inn="+str(inn)+"&tb="+str(tb)+"&bat="+str(bat)

ballHistory = {}
ballHistory[str(inn)+"_"+str(tb)+"_"+str(bat)] = []

conn = sqlite3.connect(saveDBName)
c = conn.cursor()

# ループ
while True:
    # アドレスからイニングと表裏、何人目のバッターか抽出
    m = r.search(getUrl)
    inn, tb, bat = m.group(1), m.group(2), m.group(3)
    print(m.group(1), m.group(2), m.group(3))
    # アドレス
    baseballPage = requests.get(getUrl)
    #baseballPage = requests.get(url+str(gameDate)+"/score")
    soup = BeautifulSoup(baseballPage.text, "html.parser")
    # 投球データ取得
    #baseballIning = soup.select("#livedetail > #column-center  .mb20p tr .txt_c")
    baseballIning = soup.select("#livedetail > #column-center  .mb20p tr td")
    ballHistory[str(inn)+"_"+str(tb)+"_"+str(bat)] = []

    # 次へボタンが有るか
    #isNextButton = soup.find(id="btn_next")
    #print(isNextButton["href"])

    # 先に投球コースを処理
    kindOfBall = soup.select("#kdL td")
    j = 1
    kindOfBallJson = {}
    # 投球コースをJSONに格納  要DEBUGGING
    #for ballCourse in kindOfBall:
    #    if ballCourse.text != "":
    #        print(str(j) + ":" + eachBall.text)
    #        kindOfBallJson[ballCourse.text[1:].strip()] = j
    #    j+=1
    #print(kindOfBallJson)

    kindOfBall = soup.select(".kyusyu-mark td")
    j = 1
    kindOfBallJson = {}
    for eachBall in kindOfBall:
        #print(eachBall.text)
        if eachBall.text != "":
            #print(str(j) + ":" + eachBall.text)
            ballNum = eachBall.text.count("\n")
            if ballNum <= 1:
                kindOfBallJson[eachBall.text[1:].strip()] = j
                #print(eachBall.text[1:].strip())
                pass
            else:
                tempBall = eachBall.text.split("\n")
                for i in range(ballNum):
                    kindOfBallJson[tempBall[i][1:]] = j
                    #print(tempBall[i])
                    #pass
        j+=1
    #print(kindOfBallJson)
    

    
    i = 0
    eachBallDict = {}

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
            #print("space: "+eachBall.text)
            countText = eachBall.text.split()
            eachBallDict["B"] = countText[0]
            eachBallDict["S"] = countText[1]
            eachBallDict["O"] = countText[2]

            ballHistory[str(inn)+"_"+str(tb)+"_"+str(bat)].append(eachBallDict.copy())
            #print(ballHistory)
            eachBallDict = {}
            i+=1
            #print(ballHistory)
        #print(eachBall.text)
    isNextButton = soup.find(id="btn_next")
    #print(ballHistory)
    if not isNextButton.has_attr("href"):
        break
    nextUrl = isNextButton["href"]
    print(nextUrl)
    
    if nextUrl == "":
        break
    else:
        getUrl = nextUrl

    time.sleep(1)
print(ballHistory)

#url = "https://baseball.yahoo.co.jp/live/npb/game/"
#gameDate = "2017090301" # 試合の日付とその日の何試合目か
#getUrl = url+str(gameDate)+"/score?inn="+str(inn)+"&tb="+str(tb)+"&bat="+str(bat)

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
    
print(metaData)
metaData
#metaData['日本ハム'][9] = '0'
#metaData

import bz2
# dbに格納
def ptoz(obj):
    return bz2.compress(pickle.dumps(obj, PICKLE_PROTOCOL), 3)

def ztop(b):
    return pickle.loads(bz2.decompress(b)) 
conn = sqlite3.connect(saveDBName)
c = conn.cursor()

insert_sql = "insert into baseballData (id, metaData, gotData) values (?, ?, ?)"
insert_objs = ballHistory
newList = []
newList.append(gameDate)
newList.append(ptoz(metaData))
newList.append(ptoz(ballHistory))

print(len(pickle.dumps(ballHistory)))
c.execute(insert_sql, newList)
conn.commit()