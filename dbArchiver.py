# データ保存用関数
# Data save function
import bz2
import sqlite3
import pickle
PICKLE_PROTOCOL = pickle.HIGHEST_PROTOCOL
# dbに格納
# Save to database
def ptoz(obj):
    return bz2.compress(pickle.dumps(obj, PICKLE_PROTOCOL), 3)

# dbから読み出し
# Read from database
def ztop(b):
    return pickle.loads(bz2.decompress(b)) 