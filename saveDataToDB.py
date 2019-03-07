import getYahooBaseballInfo
import argparse

# 試合日を引数で受け取る
# TODO Type Check
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("gameDate", help="set game date. fomat YYYYMMDDNN NN shoud set from 01 to 06")
args = arg_parser.parse_args()

# 試合日
# Game date
# format: YYYYMMDDNN
# N means game number in day. should set 01 to 06
gameDate = args.gameDate # 試合の日付とその日の何試合目か

# 保存するSQLite DB
# Sqlite3 database name
saveDBName = "baseballResult.db"

# TODO
# parameter check

# データ取得
# Fetch data
getYahooBaseballInfo.fetchData(gameDate, saveDBName)