import pandas as pd
import sqlite3

# Read database
conn = sqlite3.connect('data.db')

#Show tables
pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)

# Episodes
episodes = pd.read_sql_query("SELECT * FROM episodes limit 10", conn)
print(episodes.columns.values)

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
