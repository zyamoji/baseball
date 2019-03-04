import getYahooBaseballInfo

# 試合日
# game date
# format: YYYYMMDDNN
# N means game number in day. should set 01 to 06
gameDate = "2019042406" # 試合の日付とその日の何試合目か

# 保存するSQLite DB
# sqlite3 database name
saveDBName = "baseballResult.db"

# TODO
# parameter check

# データ取得
# fetch data
getYahooBaseballInfo.fetchData(gameDate, saveDBName)