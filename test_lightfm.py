
import os
import sqlite3
import numpy as np
import pandas as pd
import lightfm as lfm
from lightfm import data

min_vote = 1
    
# Armamos Dataset    
con = sqlite3.connect("datos/data.db")   

df_int = pd.read_sql_query("SELECT * FROM reviews WHERE vote >= ?", con, params=(min_vote,))
df_ep = pd.read_sql_query("SELECT * FROM episodes WHERE episode_code in (select distinct episode_code from reviews WHERE vote >= ?) ", con, params=(min_vote,))

df_ep = df_ep[["episode_code", "directed_by", "written_by", "season_bin"]]

ds = lfm.data.Dataset()
ds.fit(users=df_int["username"].unique(),
        items=df_int["episode_code"].unique(),
        item_features=df_ep["directed_by"].unique().tolist() + df_ep["written_by"].unique().tolist() + df_ep["season_bin"].unique().tolist()
        )

(interactions, weights) = ds.build_interactions(df_int[['username', 'episode_code', 'vote']].itertuples(index=False))

# Item Features
ifs = []
for _, row in df_ep.iterrows():
    ifs.append( (row["episode_code"], [row["directed_by"], row["written_by"], row["season_bin"]]) )

item_features = ds.build_item_features(ifs)

# Entrenamos
model = lfm.LightFM(no_components=3, loss="warp", k=5, n=5, learning_rate=0.1, item_alpha=0.0, user_alpha=0.0)
try:
    model.fit(interactions=interactions, sample_weight=weights, item_features=item_features, epochs=10, num_threads=2, verbose=True)
except MemoryError:
    print("MemoryError: Not enough memory to train the model.")
except Exception as e:
    print(f"An error occurred: {e}")

# Obtenemos los Mappings
user_id_mapping, user_feature_mapping, item_id_mapping, item_feature_mapping = ds.mapping()
    
# Lista de episodios a predecir: solo los que no vio y estan en el mapping
print("..")    
tmp = pd.read_sql_query("SELECT episode_code FROM episodes WHERE episode_code in (select distinct episode_code from reviews WHERE vote >= ?) ", con, params=(min_vote,)) #solo predecimos los libros con los que entrenamos
already_seen = pd.read_sql_query("SELECT episode_code FROM reviews WHERE username = ?", con, params=(username,))
tmp = tmp[~tmp.episode_code.isin(already_seen.episode_code.unique())]
list_episodes = tmp.episode_code.unique()

# Predecimos y obtenemos top9
print("..")
predicted_scores = model.predict(user_id_mapping[username], np.array([item_id_mapping[m] for m in list_episodes]), item_features=item_features, num_threads=2)
top_indices = np.argsort(predicted_scores)[-9:][::-1]  # Get the indices of the top 9 scores in descending order
recomendations = [list_episodes[i] for i in top_indices]