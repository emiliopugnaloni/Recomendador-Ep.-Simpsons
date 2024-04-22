# ===================================================== #
# === Scraper a Reviews de Episodios ================= #
# ===================================================== #

# Se busca obtener los links a las paguinas que tienen los reviews de los episodios, por ejemplo:
# https://nohomers.net/forums/index.php?threads/r-r-simpsons-roasting-on-an-open-fire.19086/

# En la paguina tenemos (generalmente) la cantidad de votaciones de 1 a 5, y haciedno click nos da 
# los usuarios que votaron (generalmente). Hay que recuperar los links a los 5 votos, acceder a esa
# paguina y luego recuperar los usuarios que votaron.

# Tambien, completamos los datos de los episodios de los simpsons con la # votos y la puntuacion general

import requests
import lxml.html
import pandas as pd
import numpy as np
import time

def retoranar_votantes(url_votos, ep_name, ep_cod):

    time.sleep(1)
    url = 'https://nohomers.net' + url_votos    
    
    r_votantes = requests.get(url)
    tree_votantes = lxml.html.fromstring(r_votantes.content)    
    votos = [] #para guardar los votantes y sus interacciones
    
    try:
        lista_votantes = tree_votantes.xpath('//a[@class="username "]')
        
        # Iteramos sobre los votantes y guardamos sus datos
        for votante in lista_votantes:
            url_votante = 'https://nohomers.net' + votante.get('href')       
            username = votante.text_content().strip()
            
            datos_voto = {
                'username': username,
                'url_username': url_votante,
                'episode_name': ep_name,
                'episode_cod': ep_cod
            }
            votos.append(datos_voto)          

        return votos    
    except:
        return votos


# === Read Datast of Episodes Data ==== #

episodes = pd.read_csv('02_episodes_data.csv', sep='|')
#episodes = episodes.iloc[[1,30,50,100,200,220, 250, 300, 350, 400,600]] #para probar
i_max = episodes.shape[0]

episodes['1/5_votes'] = np.nan
episodes['2/5_votes'] = np.nan
episodes['3/5_votes'] = np.nan
episodes['4/5_votes'] = np.nan
episodes['5/5_votes'] = np.nan
episodes['votes_details_fl'] = 0
episodes['rating_1_to_10'] = 0

reviews = [] #para guardar todas las interacciones
a_revisar = []

# === Iterate over each episode link in NoHomers==== #

for idx,episode in episodes.iterrows():
        
    episode_name = episode['episode_name_wikisimpsons']
    episode_cod = episode['episode_code']
    
        
    print(f"{round(idx/i_max,2)}%: {episode_name}") 
    r=requests.get(episode['episode_link_nohomers'])    
    
    tree = lxml.html.fromstring(r.content)
    
    # Agarramos la tabla de votos y los puntajes
    try: 
        tabla_votos = tree.xpath('//ul[@class="listPlain"]')[0]
        puntajes = tabla_votos.xpath('./li')
    except:
        episodes.loc[idx,'votes_details_fl'] = 0
        print("Paguina con error")
        continue
    
    # Iteramos sobre los distintso puntajes (a veces el primero es el mejor, a veces el peor..)
    for puntaje in puntajes: 
            
        texto_puntaje = puntaje.xpath('.//h3[@class="pollResult-response"]/text()')[0].strip()
        
        # === 5/5 Votes === #
        
        if ('5/5' in texto_puntaje) | ('V/V' in texto_puntaje) | (texto_puntaje.startswith('5')):
            votos = puntaje.xpath('.//span[@class="pollResult-votes"]')[0].xpath('.//span[@class="u-muted"]')[0].tail.strip()
            episodes.loc[idx,'5/5_votes'] = int(votos)
            
            # Si hay votos, recuperamos los votantes
            if int(votos) > 0:                
                try:
                    link_votos = puntaje.xpath('.//div[contains(@class, "pollResult-voters")]')[0].get('data-href')
                    lista_votos = retoranar_votantes(link_votos, episode_name, episode_cod)
                    reviews = reviews + lista_votos   
                    episodes.loc[idx,'votes_details_fl'] = 1        
                except:
                    continue      
    
        # === 4/5 Votes === #
                
        elif ('4/5' in texto_puntaje) | ('IV/V' in texto_puntaje) | (texto_puntaje.startswith('4')):
            votos = puntaje.xpath('.//span[@class="pollResult-votes"]')[0].xpath('.//span[@class="u-muted"]')[0].tail.strip()
            episodes.loc[idx,'4/5_votes'] = int(votos)
            
            # Si hay votos, recuperamos los votantes            
            if int(votos) > 0:
                try:
                    link_votos = puntaje.xpath('.//div[contains(@class, "pollResult-voters")]')[0].get('data-href')
                    lista_votos = retoranar_votantes(link_votos, episode_name, episode_cod)
                    reviews = reviews + lista_votos         
                    episodes.loc[idx,'votes_details_fl'] = 1                      
                except:
                    continue            
   
        # === 3/5 Votes === #  

        elif ('3/5' in texto_puntaje) | ('III/V' in texto_puntaje) | (texto_puntaje.startswith('3')):
            votos = puntaje.xpath('.//span[@class="pollResult-votes"]')[0].xpath('.//span[@class="u-muted"]')[0].tail.strip()
            episodes.loc[idx,'3/5_votes'] = int(votos)
            
            # Si hay votos, recuperamos los votantes            
            if int(votos) > 0:
                try:
                    link_votos = puntaje.xpath('.//div[contains(@class, "pollResult-voters")]')[0].get('data-href')
                    lista_votos = retoranar_votantes(link_votos, episode_name, episode_cod)
                    reviews = reviews + lista_votos           
                    episodes.loc[idx,'votes_details_fl'] = 1
                except:
                    continue

            
        # === 2/5 Votes === #     

        elif ('2/5' in texto_puntaje) | ('II/V' in texto_puntaje) | (texto_puntaje.startswith('2')):
            votos = puntaje.xpath('.//span[@class="pollResult-votes"]')[0].xpath('.//span[@class="u-muted"]')[0].tail.strip()
            episodes.loc[idx,'2/5_votes'] = int(votos)
            
            # Si hay votos, recuperamos los votantes           
            if int(votos) > 0:
                try:
                    link_votos = puntaje.xpath('.//div[contains(@class, "pollResult-voters")]')[0].get('data-href')
                    lista_votos = retoranar_votantes(link_votos, episode_name, episode_cod)
                    reviews = reviews + lista_votos           
                    episodes.loc[idx,'votes_details_fl'] = 1
                except:
                    continue
            
        # === 1/5 Votes === #   

        elif ('1/5' in texto_puntaje) | ('I/V' in texto_puntaje) | (texto_puntaje.startswith('1')):
            votos = puntaje.xpath('.//span[@class="pollResult-votes"]')[0].xpath('.//span[@class="u-muted"]')[0].tail.strip()
            episodes.loc[idx,'1/5_votes'] = int(votos)
            
            # Si hay votos, recuperamos los votantes
            if int(votos) > 0:                
                try:
                    link_votos = puntaje.xpath('.//div[contains(@class, "pollResult-voters")]')[0].get('data-href')
                    lista_votos = retoranar_votantes(link_votos, episode_name, episode_cod)
                    reviews = reviews + lista_votos           
                    episodes.loc[idx,'votes_details_fl'] = 1
                except:
                    continue          
                
        elif texto_puntaje.startswith('10'):
            episodes.loc[idx,'rating_1_to_10'] = 1 
        
        else:
            a_revisar.append(episode_name) #para revisar porque no entraron
                   
    time.sleep(2)
   
    
reviews_df = pd.DataFrame(reviews)    
reviews_df.to_csv("reviews.csv", index=False, sep='|')
episodes.to_csv("03_episodes_data.csv", index=False, sep='|')   #guardamos el dataframe que tiene datos del episodio + puntaje y votaciones
