
import os, sqlite3, csv
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE = Path(__file__).resolve().parents[1]
CSV_FILE = BASE / "data" / "transactions.csv"
DB_FILE = BASE / "finassist.db"

def get_conn():
    # SQLite is the zero-setup default for the demo.
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn=get_conn()
    conn.execute("""CREATE TABLE IF NOT EXISTS transactions(
      transaction_id TEXT PRIMARY KEY, customer_id TEXT, date TEXT,
      merchant TEXT, category TEXT, transaction_type TEXT,
      amount REAL, payment_method TEXT, status TEXT
    )""")
    count=conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    if count==0:
        with open(CSV_FILE,newline="",encoding="utf-8") as f:
            reader=csv.DictReader(f)
            conn.executemany("""INSERT INTO transactions VALUES(?,?,?,?,?,?,?,?,?)""",
                [(r["transaction_id"],r["customer_id"],r["date"],r["merchant"],r["category"],
                  r["transaction_type"],float(r["amount"]),r["payment_method"],r["status"]) for r in reader])
    conn.commit(); conn.close()

def recent_transactions(limit=8):
    conn=get_conn()
    rows=conn.execute("SELECT * FROM transactions ORDER BY date DESC LIMIT ?",(limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def spending_total():
    conn=get_conn()
    v=conn.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE status='SUCCESS'").fetchone()[0]
    conn.close(); return float(v)

def category_summary():
    conn=get_conn()
    rows=conn.execute("""SELECT category,SUM(amount) total FROM transactions
                         WHERE status='SUCCESS' GROUP BY category ORDER BY total DESC""").fetchall()
    conn.close(); return [{"category":r["category"],"total":float(r["total"])} for r in rows]

def search_transactions(term, limit=10):
    conn=get_conn()
    like=f"%{term}%"
    rows=conn.execute("""SELECT * FROM transactions
        WHERE merchant LIKE ? OR category LIKE ? OR transaction_id LIKE ?
        ORDER BY date DESC LIMIT ?""",(like,like,like,limit)).fetchall()
    conn.close(); return [dict(r) for r in rows]
