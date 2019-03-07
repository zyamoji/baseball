from bs4 import BeautifulSoup
import requests
import re
import time
import sqlite3
import dbArchiver


def fetchData(gameDate, saveDBName):
    """
    スポナビの一球速報から試合データを取得する。

    Parameters
    ----------
    gameDate : string
        試合日
    saveDBName : string
        データを保存するsqlite3データベース
    """
    # アドレス解析用
    # URL parameter
    r = re.compile("inn=([0-9]+)&tb=([0-9]+)&bat=([0-9]+)")

    # 基準となるアドレス
    # Base URL(yahoo japan baseball page)
    url = "https://baseball.yahoo.co.jp/live/npb/game/"

    inn = 1 # イニング Inning
    tb = 1  # 表裏 Top or bottom
    bat = 1 # 何人目のバッターか Batters in inning

    # 取得アドレス構築
    # Set up fetch url.
    getUrl = url+str(gameDate)+"/score?inn="+str(inn)+"&tb="+str(tb)+"&bat="+str(bat)

    # 結果を格納する辞書オブジェクト
    # Save result data in dictionary.
    ballHistory = {}
    # 最初に取得するデータを初期化
    # Init first data.
    ballHistory[str(inn)+"_"+str(tb)+"_"+str(bat)] = []

    # SQLite接続
    # Connect sqlite database.
    conn = sqlite3.connect(saveDBName)
    c = conn.cursor()

    # すべての打者に対してループ実行
    # Operate for all batters.
    while True:
        # アドレスからイニングと表裏、何人目のバッターか抽出
        # Get parameter, inning, top or bottom, batters in inning.
        m = r.search(getUrl)
        inn, tb, bat = m.group(1), m.group(2), m.group(3)
        # デバッグ用に表示
        # Pring for debug.
        print(m.group(1), m.group(2), m.group(3))
        # 取得するアドレスにアクセス
        # Fetch data.
        baseballPage = requests.get(getUrl)
        # BeautifulSoupで取得
        # Parse response data with beautiful soup.
        soup = BeautifulSoup(baseballPage.text, "html.parser")
        # 投球回データ取得
        # Get inning data.
        baseballIning = soup.select("#livedetail > #column-center  .mb20p tr td")
        ballHistory[str(inn)+"_"+str(tb)+"_"+str(bat)] = []

        # 投球コースを処理
        # Get pitch area.
        kindOfBall = soup.select("#kdL td")
        
        # 投球データを保存する辞書オブジェクト
        # Save pitch data in dictionary.
        kindOfBallJson = {}

        # 投球データ
        # Get pitch data.
        kindOfBall = soup.select(".kyusyu-mark td")
        j = 1
        
        # 投球数の分だけ繰り返す
        # Iterate each pitch.
        for eachBall in kindOfBall:
            if eachBall.text != "":
                # 球数を保存
                # Save pitch number.
                ballNum = eachBall.text.count("\n")
                # 1球以下なら保存して終わり
                # If only one pitch, save and finish.
                if ballNum <= 1:
                    kindOfBallJson[eachBall.text[1:].strip()] = j
                    pass
                # 複数球あれば都度保存
                # Save data for each pitch.
                else:
                    tempBall = eachBall.text.split("\n")
                    for i in range(ballNum):
                        kindOfBallJson[tempBall[i][1:]] = j
            j+=1
        
        i = 0
        eachBallDict = {}

        # 投球詳細データを処理
        # Scraping pitch detail data.
        for eachBall in baseballIning:
            if i%6 == 0: # 球種と打者への球数 Save data, ball, pitch for batter, pitch area.
                eachBallDict["kind"] = eachBall.text[:1]
                eachBallDict["ballForBatter"] = eachBall.text[1:]
                eachBallDict["course"] = kindOfBallJson[str(eachBallDict["ballForBatter"])]
                i+=1
            elif i%6 == 1: # 投手の投げた球数 Balls in game
                eachBallDict["totalBall"] = eachBall.text
                i+=1
            elif i%6 == 2: # 球種 Kind of pitch e.g. fast, slider etc.
                eachBallDict["ballName"] = eachBall.text
                i+=1
            elif i%6 == 3: # 球速 Speed of ball.
                eachBallDict["speed"] = eachBall.text
                i+=1
            elif i%6 == 4: # 結果 Result
                eachBallDict["result"] = eachBall.text
                i+=1
            elif i%6 == 5: # BSOカウント The count
                countText = eachBall.text.split()
                eachBallDict["B"] = countText[0]
                eachBallDict["S"] = countText[1]
                eachBallDict["O"] = countText[2]

                ballHistory[str(inn)+"_"+str(tb)+"_"+str(bat)].append(eachBallDict.copy())

                eachBallDict = {}
                i+=1

        # 次へボタンを取得
        # Get next button element.
        isNextButton = soup.find(id="btn_next")
        
        # 次へボタンが無ければ終了
        # Finish if last page
        # TODO catch error
        if not isNextButton.has_attr("href"):
            break

        # 次に取得するアドレス
        # Next URL
        nextUrl = isNextButton["href"]
        print(nextUrl)
        
        # アドレスが無ければ終了
        # Finish if last page
        if nextUrl == "":
            break
        else:
            getUrl = nextUrl

        # 1秒待つ
        # Wait for legal access, not attack.
        time.sleep(1)

    # 取得したオブジェクトを表示
    # Print result object
    print(ballHistory)

    # 以下、試合の全体的なデータを取得
    # Get meta data, in below.

    # アドレス
    # Fetch URL
    baseballPage = requests.get(getUrl)
    soup = BeautifulSoup(baseballPage.text, "html.parser")
    # スコアデータ取得
    # Get score
    scoreboard = soup.select("#scoreboard > table > tbody > tr")
    metaData = {}
    metaData['date'] = gameDate

    # 各チームのスコアを格納
    # Save each team score
    for scoreIndex in range(1, 3):
        tempScore = []
        # ビジター
        # Visitor team
        if scoreIndex == 1:
            metaData['visitorTeam'] = scoreboard[scoreIndex].select('th')[0].text
            for inningScore in scoreboard[scoreIndex].select("td"):
                tempScore.append(inningScore.text)
            metaData[metaData['visitorTeam']] = tempScore
        # ホーム
        # Home team
        else:
            metaData['homeTeam'] = scoreboard[scoreIndex].select('th')[0].text
            for inningScore in scoreboard[scoreIndex].select("td"):
                tempScore.append(inningScore.text)
            metaData[metaData['homeTeam']] = tempScore

    # デバッグ用に表示
    # Print for debug
    print(metaData)


    # DBに接続
    # Connect database
    conn = sqlite3.connect(saveDBName)
    c = conn.cursor()

    # 挿入用SQL insert SQL
    # バイナリ化して入れる Save converted binary data
    insert_sql = "insert into baseballData (id, metaData, gotData) values (?, ?, ?)"
    newList = []
    newList.append(gameDate)
    newList.append(dbArchiver.ptoz(metaData))
    newList.append(dbArchiver.ptoz(ballHistory))

    # 実行
    # Execute SQL
    c.execute(insert_sql, newList)
    conn.commit()

    # Close
    conn.close()