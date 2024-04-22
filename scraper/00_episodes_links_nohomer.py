# ===================================================== #
# === Scraper a Links de Reviews de Episodios ========= #
# ===================================================== #

# Se busca obtener los links a las paguinas que tienen los reviews de los episodios
# https://nohomers.net/forums/index.php?threads/rate-review-for-all-episodes-go-here-to-rate-review-any-episode.10558/

import requests
import lxml.html
import pandas as pd

url ="https://nohomers.net/forums/index.php?threads/rate-review-for-all-episodes-go-here-to-rate-review-any-episode.10558/"
r=requests.get(url)
print(r.status_code) #si no es error esta bien
#r.text #nos da el codigo html de la pagina

# User-Post that contains all the reviews links
tree = lxml.html.fromstring(r.content)
article_episodes = tree.xpath('//*[@id="js-post-172093"]')

# Extract all links within the article element that match class
episodes = article_episodes[0].xpath('.//a[@class="link link--internal"]')

episode_names = []
episode_links = []
    
# Iterate over each link and print its URL and text
for episode in episodes:
    episode_link = episode.get('href') #obtain ep link
    episode_name = episode.text_content() #obtain ep text
    
    episode_names.append(episode_name)
    episode_links.append(episode_link)
    
data = pd.DataFrame({'episode_name': episode_names, 'episode_link': episode_links})
data.to_csv("00_episodes_links_nohomer.csv", index=False, sep='|')
    
    

    
    

