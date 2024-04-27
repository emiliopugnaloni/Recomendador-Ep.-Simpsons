import sqlite3
import pandas as pd

# Csv files and table names
csv_files = [
    ('scraper/episodes.csv', 'episodes'),
    ('scraper/reviews.csv', 'reviews'),
    ('scraper/users.csv', 'users')
]

# SQLite database name
db_name = 'the_simpsons_tables.db'

# Create SQLite connection
conn = sqlite3.connect(db_name)

# Iterate over CSV files and create tables
for csv_file, table_name in csv_files:

    df = pd.read_csv(csv_file, sep='|')
        
    # Write DataFrame to SQLite database
    df.to_sql(table_name, conn, index=False, if_exists='replace')

# Commit changes and close connection
conn.commit()
conn.close()


# Read SQLite database
conn = sqlite3.connect(db_name)
pd.read_sql_query('SELECT * FROM episodes LIMIT 10', conn).columns


