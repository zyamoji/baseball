
# -*- coding: utf-8 -*-
import dbArchiver

# データが保存されているDB
# Sqlite3 database name
saveDBName = "baseballResult.db"

# 試合日
# Game date
# format: YYYYMMDDNN
# N means game number in day. should set 01 to 06
gameDate = "2019030301" # 試合の日付とその日の何試合目か

# DBに接続
# Connect database
conn = dbArchiver.sqlite3.connect(saveDBName)
c = conn.cursor()

# 取得用SQL
# Select SQL
select_sql = f'select * from baseballData where id={gameDate}'

# データ取得
# 1行分しか無いはず
# Got data should only one
for row in c.execute(select_sql):
    # デバッグ用にデータ表示
    # Print for debug
    print(dbArchiver.ztop(row[1]))
    ballHistory = dbArchiver.ztop(row[2])

conn.close()