from sqlite3 import connect
import os

# Get the exact folder path where dbhelper.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
database: str = os.path.join(BASE_DIR, "accounts.db")

# Print this so you can see in the terminal exactly where it is looking!
print(f"--> CONNECTING TO DATABASE AT: {database}")

def getprocess(sql: str, vals: list) -> list:
    print(sql)
    conn = None
    cursor = None
    data = []
    try:
        conn = connect(database)
        
        # --- NEW FIX: Auto-create table if it's a brand new empty file ---
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS accounts 
                          (email TEXT PRIMARY KEY, 
                           full_name TEXT NOT NULL, 
                           password TEXT NOT NULL)''')
        conn.commit()
        # -----------------------------------------------------------------

        cursor.execute(sql, vals)
        data = cursor.fetchall()
    except Exception as e:
        print(f"Database Error (GET): {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return data
        
def postprocess(sql: str, vals: list) -> bool:
    print(sql)
    conn = None
    cursor = None
    success = False
    try:
        conn = connect(database)
        cursor = conn.cursor()
        cursor.execute(sql, vals)
        conn.commit()
        success = cursor.rowcount > 0
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Database Error (POST): {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return success
        
def getall(table: str) -> list:
    sql = f"SELECT * FROM `{table}`"
    return getprocess(sql, [])
    
def getrecord(table: str, **kwargs) -> list:
    keys = list(kwargs.keys())
    vals = list(kwargs.values())
    flds = []
    for key in keys:
        flds.append(f"`{key}`=?")
    fld = " AND ".join(flds)
    sql = f"SELECT * FROM `{table}` WHERE {fld}"
    return getprocess(sql, vals)
    
def deleterecord(table: str, **kwargs) -> bool:
    keys = list(kwargs.keys())
    vals = list(kwargs.values())
    flds = []
    for key in keys:
        flds.append(f"`{key}`=?")
    fld = " AND ".join(flds)
    sql = f"DELETE FROM `{table}` WHERE {fld}"
    return postprocess(sql, vals)
    
def addrecord(table: str, **kwargs) -> bool:
    keys = list(kwargs.keys())
    vals = list(kwargs.values())
    q = ['?'] * len(keys)
    qmarks = ",".join(q)
    flds = "`,`".join(keys)
    sql = f"INSERT INTO `{table}`(`{flds}`) VALUES({qmarks})"
    return postprocess(sql, vals)
    
def updaterecord(table: str, **kwargs) -> bool:
    keys = list(kwargs.keys())
    vals = list(kwargs.values())
    flds = []
    newvals = []
    for i in range(1, len(keys)):
        flds.append(f"`{keys[i]}`=?")
        newvals.append(vals[i])
    fld = ",".join(flds)
    sql = f"UPDATE `{table}` SET {fld} WHERE `{keys[0]}`='{vals[0]}'"
    return postprocess(sql, newvals)