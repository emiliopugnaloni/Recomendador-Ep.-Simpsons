import pandas as pd
import sqlite3

# Read database
conn = sqlite3.connect('datos/data.db')

#Show tables
pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)

# Episodes
episodes = pd.read_sql_query("SELECT * FROM episodes", conn)
print(episodes.columns.values)
episodes.directed_by.value_counts(dropna=False)
episodes.written_by.value_counts(dropna=False)
episodes.chr_Homer_Simpson.value_counts(dropna=False)

# Users
users = pd.read_sql_query("SELECT * FROM users limit 10", conn)
print(users.columns.values)

# Users
users = pd.read_sql_query("SELECT * FROM users", conn)
print(users.columns.values)
users.gender.value_counts(dropna=False)

# Reviews
reviews = pd.read_sql_query("SELECT * FROM reviews", conn)
print(reviews.columns.values)
users.gender.value_counts(dropna=False)

query = f"""
        SELECT episode_code, AVG(vote) as rating, count(*) AS cant
          FROM reviews
         WHERE vote > 0
         GROUP BY 1
         HAVING cant > 10
         ORDER BY 2 DESC, 3 DESC
         LIMIT 9
    """
    
pd.read_sql_query(query, conn)


episodes.columns