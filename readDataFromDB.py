
# -*- coding: utf-8 -*-
import time
import sqlite3
import pickle
PICKLE_PROTOCOL = pickle.HIGHEST_PROTOCOL
saveDBName = "baseballResult.db"

import bz2
# dbに格納
def ptoz(obj):
    return bz2.compress(pickle.dumps(obj, PICKLE_PROTOCOL), 3)

def ztop(b):
    return pickle.loads(bz2.decompress(b)) 

conn = sqlite3.connect(saveDBName)
c = conn.cursor()
select_sql = 'select * from baseballData where id=2019022403'
for row in c.execute(select_sql):
    #print(len(row[2]))
    print(ztop(row[1]))
    ballHistory = ztop(row[2])
    #print(ztop(row[2]))
    #print(ztop(row[1]))
    #print(ztop(row[2]))
conn.close()