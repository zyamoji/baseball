import getYahooBaseballInfo
import argparse
import sys

# 試合日を引数で受け取る
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("gameDate", help="set game date. fomat YYYYMMDDNN NN shoud set from 01 to 06")
args = arg_parser.parse_args()

# gameDate parameter check
# gameDate must be 10 digits
if len(args.gameDate) != 10 or not (args.gameDate.isdecimal()):
    print("Please check parameter. gameDate format is YYYYMMDDNN. all digits.")
    sys.exit(1)


# 試合日
# game date
# format: YYYYMMDDNN
# N means game number in day. should set 01 to 06
gameDate = args.gameDate # 試合の日付とその日の何試合目か

# 保存するSQLite DB
# sqlite3 database name
saveDBName = "baseballResult.db"

# データ取得
# fetch data
getYahooBaseballInfo.fetchData(gameDate, saveDBName)