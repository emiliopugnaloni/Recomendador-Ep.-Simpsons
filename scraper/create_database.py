import sqlite3
import pandas as pd

# Database
conn = sqlite3.connect('scraper/data.db')

# Reviews Table
reviews = pd.read_csv('scraper/reviews.csv', sep='|')
reviews = reviews[['username', 'episode_cod', 'vote']].rename(columns={'episode_cod': 'episode_code'})
reviews.to_sql('reviews', conn, index=False, if_exists='replace')

# Users Table
users = pd.read_csv('scraper/users.csv', sep='|')
users = users[['username', 'gender']]
users.to_sql('users', conn, index=False, if_exists='replace')

# Episodes Table
episodes = pd.read_csv('scraper/episodes.csv', sep='|')
episodes.to_sql('episodes', conn, index=False, if_exists='replace')


# Commit changes and close connection
conn.commit()
conn.close()

# Read SQLite database
conn = sqlite3.connect('scraper/data.db')
pd.read_sql_query('SELECT * FROM episodes LIMIT 10', conn).columns


