import sqlite3
p = 'c:/expense-splitter/backend/db.sqlite3'
con = sqlite3.connect(p)
cur = con.cursor()
try:
    cur.execute("ALTER TABLE expenses_expense RENAME COLUMN paid_by TO paid_by_id")
    con.commit()
    print('RENAMED column')
except Exception as e:
    print('ERROR', e)
    # show schema for manual inspection
    cur.execute("PRAGMA table_info('expenses_expense')")
    for r in cur.fetchall():
        print(r)
finally:
    con.close()
