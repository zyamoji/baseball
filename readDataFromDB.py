
# -*- coding: utf-8 -*-
import time
import sqlite3
import pickle
PICKLE_PROTOCOL = pickle.HIGHEST_PROTOCOL
# データが保存されているDB
saveDBName = "baseballResult.db"

import bz2
# dbに格納
def ptoz(obj):
    return bz2.compress(pickle.dumps(obj, PICKLE_PROTOCOL), 3)

# DBから読み出し
def ztop(b):
    return pickle.loads(bz2.decompress(b)) 

# DBに接続
conn = sqlite3.connect(saveDBName)
c = conn.cursor()

# 取得用SQL
select_sql = 'select * from baseballData where id=2019022403'

# データ取得
# 1行分しか無いはず
for row in c.execute(select_sql):
    # デバッグ用にデータ表示
    print(ztop(row[1]))
    ballHistory = ztop(row[2])

conn.close()