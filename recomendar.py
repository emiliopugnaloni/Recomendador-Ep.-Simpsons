import os
import sqlite3

THIS_FOLDER = os.path.dirname(os.path.abspath("__file__"))

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
    if params:
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

    id_episodios = recomendar_top_9(username)
    # if cant_valorados <= 5: ## 5 es número mágico
    #     id_libros = recomendar_top_9(id_lector)        
    # elif cant_valorados <= 10: ## 10 es número mágico
    #     id_libros = recomendar_contenido(id_lector)
    # else:
    #     id_libros = recomendar_perfil(id_lector)

    recomendaciones = datos_episodios(id_episodios)
    return recomendaciones

## 
## algoritmos de recomendacion
##
def recomendar_top_9(username):
    query = f"""
        SELECT episode_code, AVG(vote) as rating, count(*) AS cant
          FROM reviews
         WHERE episode_code NOT IN (SELECT episode_code FROM reviews WHERE username = ?)
           AND vote > 0
         GROUP BY 1
         HAVING cant > 20
         ORDER BY 2 DESC, 3 DESC
         LIMIT 9
    """
    id_episodios = [r["episode_code"] for r in sql_select(query, (username,))]
    return id_episodios

def recomendar_perfil(id_lector):
    return []

def recomendar_contenido(id_lector):
    return []
