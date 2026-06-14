import sqlite3
p = 'c:/expense-splitter/backend/db.sqlite3'
con = sqlite3.connect(p)
cur = con.cursor()
try:
    cur.execute("PRAGMA table_info('expenses_expense')")
    rows = cur.fetchall()
    print('columns:')
    for r in rows:
        print(r)
except Exception as e:
    print('ERROR', e)
finally:
    con.close()
