
# -*- coding: utf-8 -*-
import dbArchiver

# データが保存されているDB
# sqlite3 database name
saveDBName = "baseballResult.db"

# 試合日
# game date
# format: YYYYMMDDNN
# N means game number in day. should set 01 to 06
gameDate = "2019030301" # 試合の日付とその日の何試合目か

# DBに接続
# connect database
conn = dbArchiver.sqlite3.connect(saveDBName)
c = conn.cursor()

# 取得用SQL
# select SQL
select_sql = f'select * from baseballData where id={gameDate}'

# データ取得
# 1行分しか無いはず
# got data should only one
for row in c.execute(select_sql):
    # デバッグ用にデータ表示
    # print for debug
    print(dbArchiver.ztop(row[1]))
    ballHistory = dbArchiver.ztop(row[2])

conn.close()