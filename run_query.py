# run_query.py
from sqlalchemy import create_engine, text
from app.config import Config

# 創建 engine
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI, 
    connect_args={"check_same_thread": False} if Config.SQLALCHEMY_DATABASE_URI.startswith("sqlite") else {}
)

def run_query(sql_file: str):
    with open(sql_file, 'r', encoding='utf-8') as file:
        sql = file.read()
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        # 打印列名
        print(" | ".join(result.keys()))
        print("-" * 40)
        # 打印每一行
        for row in result:
            print(row)

if __name__ == "__main__":
    run_query("query_test.sql")
