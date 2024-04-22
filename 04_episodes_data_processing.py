# ====================== #
# PROCESSING EPISODES DATA
# ======================= #

# El objetivo de este script es procesar los datos de los episodios de los Simpsons, 
# que fueron recolectados. 
# La idea es generar variables segun los directores, escritores y personajes.
# Ademas, se van a filtrar los episodios que no tienen reviews, o que estas no estan en escala de 1 a 5


import pandas as pd

#Leemos dataset con info episodios (wikisimpsons) y datos de #reviews y puntaje (nohomers)
episodes = pd.read_csv('03_episodes_data.csv', sep='|')  

# === Agregado de Columnas === #

#Nos quedamos solo con los que tienen Reviews
episodes_with_reviews = pd.read_csv('reviews.csv', sep='|').episode_name.unique()
episodes = episodes[episodes.episode_name_wikisimpsons.isin(episodes_with_reviews)].sort_values('episode_number', ascending=True)
print(episodes.shape)

# Calculamos algunas columnas
episodes['q_votes'] = episodes['1/5_votes'] + episodes['2/5_votes'] + episodes['3/5_votes'] + episodes['4/5_votes'] + episodes['5/5_votes']
episodes['rating'] = round((episodes['1/5_votes'] + 2*episodes['2/5_votes'] + 3*episodes['3/5_votes'] + 4*episodes['4/5_votes'] + 5*episodes['5/5_votes'])/episodes['q_votes'],2)


# === Directores === #

# Contamos la cantidad de directores. Nos quedamos con quienes aparecen mas de 10 veces
directors_occurences = episodes.directed_by.str.split('|').explode().value_counts()
directors = directors_occurences[directors_occurences > 10].index.values
directors = [director.strip().replace(' ', '_') for director in directors]

# Agregamos variables dummies si el director parece en el episodio
for director in directors:
    episodes[director] = episodes.directed_by.apply(lambda x: director in x)
    
 # === Escritores === #   

# Contamos la cantidad de escritores. Nos quedamos con quienres aparecen mas de 10 veces
writters_occurences = episodes.written_by.str.split('|').explode().value_counts()
writters = writters_occurences[writters_occurences > 10].index.values
writters = [writter.strip().replace(' ', '_') for writter in writters]

# Agregamos variables dummies si el escritor aparece en el episodio
for writter in writters:
    episodes[writter] = episodes.written_by.apply(lambda x: writter in x)


# === Personajes === #

# Contamos la cantidad de personajes. Nos quedamos con quienres aparecen mas de 10 veces
characters_occurences = episodes.characters.str.split('|').explode().value_counts()
characters = characters_occurences[characters_occurences > 20].index.values
characters = [characters.strip().replace(' ', '_') for characters in characters]

# Agregamos variables dummies si el personaje aparece en el episodio
for character in characters:
    episodes[character] = episodes.directed_by.apply(lambda x: character in x)
    

# === Eliminamos Columnas Inesesarias === #

episodes.drop(columns=['1/5_votes', '2/5_votes', '3/5_votes', '4/5_votes', '5/5_votes', 'rating_1_to_10', 'votes_details_fl'], inplace=True) #calculadas
episodes.drop(['episode_name_nohomers', 'episode_link_nohomers', 'episode_link_wikisimpsons'], axis=1, inplace=True) #usadas para joins y scappers
episodes.drop(['written_by', 'directed_by', 'characters'], axis=1, inplace=True) #usadas para dummies


# ==== Renombramos Columnas ==== #
episodes.rename(columns={'episode_name_wikisimpsons': 'episode_name'}, inplace=True)
print(episodes.shape)
episodes.head()

# === Guardamos Dataset === #
episodes.to_csv("episodes.csv", index=False, sep='|')  
