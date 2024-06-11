import os
import sqlite3
import pandas as pd

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
    print(query)
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
        id_episodios = recomendar_perfil(username)
        algoritmo = "perfil"   
    # elif cant_valorados <= 10: ## 10 es número mágico
    #     id_libros = recomendar_contenido(id_lector)
    # else:
    #     id_libros = recomendar_perfil(id_lector)

    print(id_episodios)
    recomendaciones = datos_episodios(id_episodios)
    return recomendaciones, algoritmo

## 
## algoritmos de recomendacion
##
def recomendar_top_9(username):
    query = f"""
        SELECT episode_code, AVG(vote) as rating, SUM(CASE WHEN vote>=4 THEN 1 ELSE 0 END) AS q_pos_reviews
        FROM reviews
        WHERE episode_code NOT IN (SELECT episode_code FROM reviews WHERE username = ?)
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
        WHERE a.username = ?  """, con, params=(username,))  
    
    df_user = df_user[['ponderador'] + columns_for_profile]
    df_user = df_user.loc[:, df_user.columns != 'ponderador'].mul(df_user['ponderador'], axis=0).sum().transpose()
   
   # Info de Ratings
    df_ratings = pd.read_sql_query(f"""
        SELECT episode_code, AVG(vote) as rating, SUM(CASE WHEN vote>=4 THEN 1 ELSE 0 END) AS q_pos_reviews
        FROM reviews
        WHERE episode_code NOT IN (SELECT episode_code FROM reviews WHERE username = ?)
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


def recomendar_contenido(id_lector):
    return []
