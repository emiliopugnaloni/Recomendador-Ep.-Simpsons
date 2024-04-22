# ============================================== #
# === Scraper a Datos de los Episodios ========= #
# ============================================== #

# Se busca obtener los datos de los episodios de WiKiSimpsons, por ejemplo:
# https://simpsonswiki.com/wiki/My_Life_as_a_Vlog

import requests
import lxml.html
import pandas as pd
import numpy as np
import time

#  === Read Datast of Episodes Links ==== #

episodes = pd.read_csv('01d_episodes_links_wikisimpsons_nohomer.csv', sep='|')
#episodes = episodes.iloc[[3]]#, 679, 711, 127, 128]] #para probar

episodes['episode_number'] = np.nan
episodes['episode_code'] = np.nan
episodes['episode_airdate'] = np.nan
episodes['directed_by'] = np.nan
episodes['written_by'] = np.nan
episodes['sinopsis'] = np.nan
episodes['chapter_image'] = np.nan
episodes['gallery_images'] = np.nan
episodes['characters'] = np.nan

# === Iterate over each link and add the episode data to the DataFrame ==== #

for idx, episode in episodes.iterrows():
    
    print(episode['episode_name_wikisimpsons'])    
    url = episode['episode_link_wikisimpsons']    
    r=requests.get(url)  
    tree = lxml.html.fromstring(r.content)
   
   # === Get table of episode info === #
    try:
        xpath_query = '//*[@id="mw-content-text"]//table[contains(@style, "background: #f0e3a2; border:2px solid #e9d677;") and @align="right"]'
        episode_info = tree.xpath(xpath_query)[0]
    except:
        print("     No se pudo encontrar la tabla del episodio")
        continue
       
    # === Extract episode data === #
    try:
        episode_table = episode_info.xpath('tr[2]/td/table')[0]    
        episodes.loc[idx,'episode_number']  = episode_table.xpath('tr[1]/td')[0].text_content().strip()
        episodes.loc[idx,'episode_code'] = episode_table.xpath('tr[3]/td')[0].text_content().strip()
        episodes.loc[idx, 'episode_airdate'] = episode_table.xpath('tr[4]/td')[0].text_content().strip()
        episodes.loc[idx,'directed_by'] = episode_table.xpath('tr[th[contains(text(), "Directed by")]]/td')[0].text_content().strip()
        episodes.loc[idx, 'written_by']  = episode_table.xpath('tr[th[contains(text(), "Written by")]]/td')[0].text_content().strip()
    except:
        print("     No se pudo extraer la informacion de la tabla de episodio")
        
    # === Extract Excritor/es === #
    try:
        writen_by = episode_table.xpath('tr[th[contains(text(), "Written by")]]/td/a')
        writers_list = []
        for w in writen_by:
            writer = w.text_content().strip()
            writers_list.append(writer)
            writers_str = '| '.join(writers_list)
        episodes.loc[idx, 'written_by'] = writers_str
    
    except:
        print("     No se pudo extraer los escritores del episodio")
    
    # === Extract Director/s === #
    try:
        directed_by = episode_table.xpath('tr[th[contains(text(), "Directed by")]]/td/a')
        directors_list = []
        for d in directed_by:
            director = d.text_content().strip()
            directors_list.append(director)
            directors_str = '| '.join(directors_list)
        episodes.loc[idx, 'directed_by'] = directors_str
    
    except:
        print("     No se pudo extraer los directores del episodio")
          
          
    # === Extract Chapter Image === #
    try:
        chapter_image = episode_info.xpath('tr[1]/td/table/tr/td/a/img')[0].get('src')
        episodes.loc[idx, 'chapter_image'] = chapter_image
    except:
        print("     No se pudo extraer la imagen del episodio")
    
    # === Extract sinopsis === #
    try:
        #episodes.loc[idx,'sinopsis'] = tree.xpath('//*[@id="mw-content-text"]/dl/dd/span/i')[-1].text_content()
        sinopsis = tree.xpath('//*[@id="mw-content-text"]/dl/dd/span')
        
        texto = ''
        for s in sinopsis:
            s_texto = s.text_content()    
            texto = texto + s_texto + ' '
        episodes.loc[idx,'sinopsis'] = texto          

    except:
        print("     No se pudo extraer la sinopsis del episodio")   

    # === Extract Images in Gallery === #
    # Se necesita hacer un request a la paguina de galeria de imagenes, y extraer las imagenes
    
    url_gallery = url.replace('/wiki/', '/wiki/Category:Images_-_')
    r_gallery=requests.get(url_gallery)  
         
    try:
        # Buscamos en la paguina la galleria. Y de esta, retornamos los "gallery-box"
        tree_gallery = lxml.html.fromstring(r_gallery.content)         
        gallery = tree_gallery.xpath('.//ul[@class="gallery mw-gallery-traditional"]')[0]
        gallery_images = tree_gallery.xpath('.//li[@class="gallerybox"]')
        list_gallery_images = []
        
        # Para cada imagen, extraemos la url
        for image in gallery_images:
            image_url = image.xpath('div/div/div/a/img')[0].get('src')
            list_gallery_images.append(image_url)

        # Convertimos la lista de imagenes a un string separado por '|'
        list_gallery_images_str = '|'.join(list_gallery_images)
        episodes.loc[idx, 'gallery_images'] = list_gallery_images_str
        
    except: 
        print("     No se pudo extraer la galeria de imagenes")
        

    # === Extract Voiced Characterts === #    
    # Se necesita hacer un request a la paguina de apariciones, y extraer los personajes
    
    url_appearances = url+'/Appearances'
    r2=requests.get(url_appearances)
    tree2 = lxml.html.fromstring(r2.content)

    # Extraemos los personajes
    try:
        characters = tree2.xpath('.//div[@class="gallerytext"]')
    except:
        print("     No se pudo extraer los personajes")
        continue
    
    # Iteramos sobre los personajes y nos quedamos solo con los que hablan (o eso dice el tag)
    list_characters = []
        
    for character in characters:
        character_voiced = character.xpath('.//sup[@id="ref_voiced"]') #only the voiced
        
        if character_voiced:
            character_name = character.xpath('.//a')[0].text_content().strip()
            list_characters.append(character_name)
            
    # Convertimos la lista a separada por | y la guardamos en el dataframe
    characters_str = '| '.join(list_characters)
    episodes.loc[idx, 'characters'] = characters_str
    
    # === Sleep === #
    time.sleep(2)
    

print("Fin del proceso")

# Guardamos el dataframe
episodes.to_csv("02_episodes_data.csv", index=False, sep='|')

# Control:
print("Episodios sin informacion:")
print(episodes.loc[episodes.sinopsis.isnull(), 'episode_name_wikisimpsons'])
print("Episodios sin Escritor:")
print(episodes.loc[episodes.written_by.isnull(), 'episode_name_wikisimpsons'])
print("Episodios sin Director:")
print(episodes.loc[episodes.directed_by.isnull(), 'episode_name_wikisimpsons'])
print("Episodios sin Imagen de Capitulo:")
print(episodes.loc[episodes.chapter_image.isnull(), 'episode_name_wikisimpsons'])
print("Episodios sin Imagenes de Galeria:")
print(episodes.loc[episodes.gallery_images.isnull(), 'episode_name_wikisimpsons'])
print("Episodios sin Personajes:")
print(episodes.loc[episodes.characters.isnull(), 'episode_name_wikisimpsons'])
