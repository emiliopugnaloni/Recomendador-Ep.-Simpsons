import os
import sqlite3
import numpy as np
import pandas as pd
#import surprise as sp
import lightfm as lfm
from lightfm import data

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

def sql_execute(query, params=None):
    con = sqlite3.connect(os.path.join(THIS_FOLDER, "datos/data.db"))
    cur = con.cursor()    
    if params:
        res = cur.execute(query, params)
    else:
        res = cur.execute(query)

    con.commit()
    con.close()
    return

def sql_select(query, params=None):
    con = sqlite3.connect(os.path.join(THIS_FOLDER, "datos/data.db"))
    con.row_factory = sqlite3.Row # esto es para que devuelva registros en el fetchall
    cur = con.cursor()    
    if params is not None:
        res = cur.execute(query, params)
    else:
        res = cur.execute(query)

    ret = res.fetchall()
    con.close()

    return ret

def crear_usuario(username):
    query = "INSERT INTO users(username) VALUES (?) ON CONFLICT DO NOTHING;" # si el id_lector existia, se produce un conflicto y le digo que no haga nada
    sql_execute(query, (username,))
    return

def datos_episodios(id_episodios):
    query = f"SELECT DISTINCT * FROM episodes WHERE episode_code IN ({','.join(['?']*len(id_episodios))})"
    episodios = sql_select(query, id_episodios)
    return episodios

def valorados(username):
    valorados = sql_select(f"SELECT * FROM reviews WHERE username = ? AND vote > 0", (username,))
    return valorados

def ignorados(username):    
    ignorados = sql_select(f"SELECT * FROM reviews WHERE username = ? AND vote = 0", (username,))
    return ignorados

def recomendar(username):
    cant_valorados = len(valorados(username))

    if cant_valorados <= 5:
         id_episodios = recomendar_top_9(username)   
         algoritmo = "top9"  
    else:
        id_episodios = recomendar_personalizada_warp(username)
        algoritmo = "warp"   
    # else:
    #     id_episodios = recomendar_personalizada(username)
    #     algoritmo = "personalizada"

    print(id_episodios)
    recomendaciones = datos_episodios(id_episodios)
    return recomendaciones, algoritmo

## 
## algoritmos de recomendacion
##
def recomendar_top_9(username):
    query = f"""
        SELECT episode_code, 
            AVG(vote) as rating, 
            SUM(CASE WHEN vote>=4 THEN 1 ELSE 0 END) AS q_pos_reviews
        FROM reviews
        WHERE episode_code NOT IN (SELECT episode_code FROM reviews WHERE username = ?)
            AND vote>0
        GROUP BY 1
        ORDER BY 3 DESC, 2 DESC
        LIMIT 9
    """
    id_episodios = [r["episode_code"] for r in sql_select(query, (username,))]
    return id_episodios

def recomendar_perfil(username):
    
    con = sqlite3.connect(os.path.join(THIS_FOLDER, "datos/data.db"))
        
    # Perfil de Episodios
    df_episodes = pd.read_sql_query(f"SELECT * FROM episodes", con).set_index('episode_code')
    columns_for_profile = [col for col in df_episodes.columns if col.startswith(('dir_', 'wrt_', 'season_bin_'))]
    df_episodes =  df_episodes[columns_for_profile]
        
    # Pefil de Usuarios
    df_user = pd.read_sql_query(f""" 
        SELECT a.username,  vote-2 as ponderador,   b.*
        FROM reviews AS a
        JOIN episodes b ON a.episode_code = b.episode_code
        WHERE a.username = ?  
            AND vote>0
        """, con, params=(username,))  
    
    df_user = df_user[['ponderador'] + columns_for_profile]
    df_user = df_user.loc[:, df_user.columns != 'ponderador'].mul(df_user['ponderador'], axis=0).sum().transpose()
   
   # Info de Ratings
    df_ratings = pd.read_sql_query(f"""
        SELECT episode_code, AVG(vote) as rating, SUM(CASE WHEN vote>=4 THEN 1 ELSE 0 END) AS q_pos_reviews
        FROM reviews
        WHERE episode_code NOT IN (SELECT episode_code FROM reviews WHERE username = ?)
            AND vote>0
        GROUP BY 1
        ORDER BY 3 DESC, 2 DESC""", con, params=(username,)).set_index('episode_code')
    con.close()
    
    # Multiplicacion de Vector - Matriz
    df_recomendacion = df_episodes.mul(df_user.values, axis=1)
    del df_user, df_episodes
    df_recomendacion = df_recomendacion.sum(axis=1).rename('pnt_perfil')

    # Ordenamiento de Recomendacion (1ro por perfil, 2do por rating)
    df_recomendacion = pd.merge(df_recomendacion, df_ratings, left_index=True, right_index=True, how='inner')
    df_recomendacion = df_recomendacion.sort_values(['pnt_perfil', 'q_pos_reviews', 'rating'], ascending=[False, False, False]) 
    return df_recomendacion.index.unique()[:9].values


def recomendar_personalizada_svd(username):
 
    # Creamos algoritmo SVD 
    con = sqlite3.connect(os.path.join(THIS_FOLDER, "datos/data.db"))        
    df_ratings = pd.read_sql_query(f"SELECT * FROM ratings WHERE vote>0", con).set_index('episode_code')   

    reader = sp.reader.Reader(rating_scale=(1, 5))
    df_ratings = sp.dataset.Dataset.load_from_df(df_ratings[['username', 'episode_code', 'vote']], reader)
    trainset = df_ratings.build_full_trainset()

    algo = sp.SVD(n_factors= 30, n_epochs= 70, reg_all= 0.1, random_state=42)
    algo.fit(trainset)
    
    # Obtenemos los ya vistos
    query_already_seen = "SELECT episode_code FROM reviews WHERE username = ?"
    tmp = pd.read_sql_query(query_already_seen, con, params=(username,))
    already_seen = tmp.episode_code.unique()
    
    # Obtenemos la lista de episodios
    tmp = pd.read_sql_query("SELECT episode_code FROM episodes", con)
    list_episodes = tmp.episode_code.unique() 
    
    # Obtenemos las predicciones para cada episiodio
    df_pred = []
    dict_pred = {}   
    
    for iid in list_episodes:
        if iid not in already_seen:
            pred = algo.predict(username, iid)
            dict_pred = {'ep_code': iid, 'rating_pred': pred.est}
            df_pred.append(dict_pred)

    df_pred = pd.DataFrame(df_pred)
    df_pred = df_pred.sort_values('rating_pred', ascending=False)
    recomendations = df_pred.ep_code.unique()[:9]

    return recomendations
    
def recomendar_personalizada_warp(username):
 
    min_vote = 1
    
    # Armamos Dataset    
    con = sqlite3.connect(os.path.join(THIS_FOLDER, "datos/data.db"))     
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
    model.fit(interactions=interactions, sample_weight=weights, item_features=item_features, epochs=30, num_threads=1)

    # Obtenemos los Mappings
    print("..")
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
    
    return recomendations