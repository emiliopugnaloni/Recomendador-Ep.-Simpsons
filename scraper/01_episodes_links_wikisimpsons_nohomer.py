# =========================================== #
# Scraper a Links de Episodios en WikiSimpson #
#         y Join con los de NoHomers          #
# =========================================== #

# Se busca obtener los links a las paguinas que tienen los datos los episodios, por ejemplo:
# https://simpsonswiki.com/wiki/The_Way_We_Was
# Estos estan en la paguina de WikiSimpsons

import requests
import lxml.html
import pandas as pd

url =  'https://simpsonswiki.com/wiki/List_of_episodes'
n_seasons = 35


r=requests.get(url)
print(r.status_code) #si no es error esta bien

tree = lxml.html.fromstring(r.content)

episode_names = []
episode_links = []
episode_season = []
base_url = 'https://simpsonswiki.com'

for season in range(1, n_seasons+1):

    table_element = tree.xpath(f'//*[@id="mw-content-text"]/table[{season}]')[0]
       
    # Extract episode names and links
    for row in table_element.xpath('.//tr[position() > 1]'):  # Exclude the first row (header row)
        link_element = row.xpath('.//td[1]/b/a')[0]  # Extract the <a> tag containing the episode link and name
        episode_name = link_element.text.strip()  # Get the text content of the <a> tag (episode name)
        episode_link = link_element.get('href')  # Get the value of the href attribute (episode link)
        
        episode_names.append(episode_name)
        episode_links.append(base_url+episode_link)
        episode_season.append(season)
        
    
data = pd.DataFrame({'episode_name': episode_names, 'episode_link': episode_links, 'episode_season': episode_season})
    
data.to_csv("01_episodes_links_wikisimpsons.csv", index=False, sep='|')


# ========================================= #
# HACEMOS JOIN CON LOS EPISODIOS EN NOHOMERS
# ========================================= #

# Necesitamos vincular estos episodios con los de NoHomer. Para ello, normalizamos los nombres de los episodios y hacemos un join
# Algunos nombres de episodios de NoHomer tienen errores gramaticales, por lo que hay que usar una tabla externa

def normalizacion(episodio):
    episodio = episodio.upper()
    episodio = episodio.replace("-", " ")
    episodio = episodio.replace("'", "")
    episodio = episodio.replace("?", "")
    episodio = episodio.replace("&", "AND") 
    episodio = episodio.replace('"', '')
    episodio = episodio.replace(':', '')
    episodio = episodio.replace(',', '')
    episodio = episodio.replace('.', '')
    episodio = episodio.replace('SIMPSONS', 'SIMPSON')
    episodio = episodio.replace('THE', '')
    episodio = episodio.replace('DOH', '(ANNOYED GRUNT)')
    episodio = episodio.replace('!', '')
    episodio = episodio.replace('*', '')
    episodio = episodio.replace('AND', '')
    episodio = episodio.replace(' ', '')
    episodio = episodio.strip() 
        
    return episodio

# Levantamos los episodios de NoHomers y WikiSimpsons
episodes_nohomers = pd.read_csv("00_episodes_links_nohomer.csv", sep='|')
episodes_wikisimpsons = pd.read_csv("01a_episodes_links_wikisimpsons.csv", sep='|')

episodes_nohomers['episode_name_norm'] = episodes_nohomers['episode_name'].apply(normalizacion)  
episodes_wikisimpsons['episode_name_norm'] = episodes_wikisimpsons['episode_name'].apply(normalizacion)  

# Join de los episodios
episodes_join = episodes_nohomers.merge(episodes_wikisimpsons, how='left', on='episode_name_norm',suffixes=('_nohomers', '_wikisimpsons'))           
episodes_join.to_csv("01b_episodes_links_wikisimpsons_nohomer.csv", index=False, sep='|')  

# Importamos Excel auxiliar para los match que no se generaron
episodes_aux = pd.read_excel("01c_episodes_links_wikisimpsons_nohomer.xlsx")
episodes_join = pd.concat([episodes_join, episodes_aux], axis=0)
episodes_join = episodes_join.drop_duplicates(subset='episode_name_norm', keep='last')

if episodes_join.episode_name_wikisimpsons.isnull().sum() == 0:
    print("Todos los episodios de NoHomer tienen match en WikiSimpsons")
else:
    print("Existen episodios de NoHomer que no tienen match en WikiSimpsons:")
    print(episodes_join[episodes_join.episode_name_wikisimpsons.isnull(), 'episode_name_noHomer'])
    print("Completar la lista de episodios en el archivo NoHomer_WikiSimpsons_Episodes_Links_AUX.xlsx y volver a correr el script. Usar WikiSimpsons_episodes_links.csv para completar  ")


# Guardamos el join final
episodes_join.drop('episode_name_norm', axis=1, inplace=True)
episodes_join.to_csv("01d_episodes_links_wikisimpsons_nohomer.csv", index=False, sep='|')  
