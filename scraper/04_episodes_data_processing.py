# ====================== #
# PROCESSING EPISODES DATA
# ======================= #

# El objetivo de este script es procesar los datos de los episodios de los Simpsons, 
# que fueron recolectados. 
# La idea es generar variables segun los directores, escritores y personajes.
# Ademas, se van a filtrar los episodios que no tienen reviews, o que estas no estan en escala de 1 a 5


import pandas as pd

#Leemos dataset con info episodios (wikisimpsons) y datos de #reviews y puntaje (nohomers)
episodes = pd.read_csv('scraper/03_episodes_data.csv', sep='|')  

# === Agregado de Columnas === #

#Nos quedamos solo con los que tienen Reviews
episodes_with_reviews = pd.read_csv('scraper/reviews.csv', sep='|').episode_name.unique()
episodes = episodes[episodes.episode_name_wikisimpsons.isin(episodes_with_reviews)].sort_values('episode_number', ascending=True)
print(episodes.shape)

# === Corregimos data_types === #
episodes['episode_season'] = episodes['episode_season'].astype(int)

# === Juntamos Imagenes (galeria con chapter)=== #
episodes['gallery_images'] = episodes['chapter_image'] +'|' + episodes['gallery_images']

# Calculamos algunas columnas
episodes['q_votes'] = episodes['1/5_votes'] + episodes['2/5_votes'] + episodes['3/5_votes'] + episodes['4/5_votes'] + episodes['5/5_votes']
episodes['rating'] = round((episodes['1/5_votes'] + 2*episodes['2/5_votes'] + 3*episodes['3/5_votes'] + 4*episodes['4/5_votes'] + 5*episodes['5/5_votes'])/episodes['q_votes'],2)


# === Directores === #

# Contamos la cantidad de directores. Nos quedamos con quienes aparecen mas de 10 veces
directors_occurences = episodes.directed_by.str.split('|').explode().str.strip().value_counts()
directors = directors_occurences[directors_occurences > 10].index.values
director_columns = ['dir_' + director.strip().replace(' ', '_') for director in directors]

# Agregamos variables dummies si el director parece en el episodio
for director, director_column in zip(directors,director_columns):
    episodes[director_column] = episodes.directed_by.apply(lambda x: int(director in x))
    
 # === Escritores === #   

# Contamos la cantidad de escritores. Nos quedamos con quienres aparecen mas de 10 veces
writters_occurences = episodes.written_by.str.split('|').explode().str.strip().value_counts()
writters = writters_occurences[writters_occurences > 10].index.values
writter_columns = ['wrt_'+ writter.strip().replace(' ', '_') for writter in writters]

# Agregamos variables dummies si el escritor aparece en el episodio
for writter, writter_column in zip(writters,writter_columns) :
    episodes[writter_column] = episodes.written_by.apply(lambda x: int(writter in x))


# === Personajes === #

# Contamos la cantidad de personajes. Nos quedamos con quienres aparecen mas de 10 veces
characters_occurences = episodes.characters.str.split('|').explode().str.strip().value_counts()
characters = characters_occurences[characters_occurences > 20].index.values
character_columns = ['chr_' + character.strip().replace(' ', '_') for character in characters]

episodes.characters = episodes.characters.fillna('')


# Agregamos variables dummies si el personaje aparece en el episodio
for character, character_column in zip(characters,character_columns) :
    #print(character, character_column)
    episodes[character_column] = episodes.characters.apply(lambda x: int(character in x))


# ==== Personajes en Sinopsis ==== #

episodes.sinopsis.fillna('', inplace=True)

episodes['sinopsis_homer'] = episodes.sinopsis.str.lower().str.contains('homer').astype(int)
episodes['sinopsis_bart'] = episodes.sinopsis.str.lower().str.contains('bart').astype(int)
episodes['sinopsis_lisa'] = episodes.sinopsis.str.lower().str.contains('lisa').astype(int)
episodes['sinopsis_marge'] = episodes.sinopsis.str.lower().str.contains('marge').astype(int)

episodes[['sinopsis_homer', 'sinopsis_bart', 'sinopsis_lisa', 'sinopsis_marge']].value_counts().sort_index()

# === Temporadas === #
#Create dummies for cutpoints 0,5,10,15,20,25,30,35
#episodes['season'] =
episodes['season_bin'] = pd.cut(episodes['episode_season'], bins=[0,5,10,15,20,25,30,35], labels=['0_4', '5_9', '10_14', '15_19', '20_24', '25_29', '30_35'], right=False)
episodes = pd.get_dummies(episodes, columns=['season_bin'], drop_first=False, dtype='int')
episodes['season_bin'] = pd.cut(episodes['episode_season'], bins=[0,5,10,15,20,25,30,35], labels=['0_4', '5_9', '10_14', '15_19', '20_24', '25_29', '30_35'], right=False)

    
# === Eliminamos Columnas Inesesarias === #

episodes.drop(columns=['1/5_votes', '2/5_votes', '3/5_votes', '4/5_votes', '5/5_votes', 'rating_1_to_10', 'votes_details_fl'], inplace=True) #calculadas
episodes.drop(['episode_name_nohomers', 'episode_link_nohomers', 'episode_link_wikisimpsons'], axis=1, inplace=True) #usadas para joins y scappers
episodes.drop(['characters'], axis=1, inplace=True) #usadas para dummies


# ==== Renombramos Columnas ==== #
episodes.rename(columns={'episode_name_wikisimpsons': 'episode_name'}, inplace=True)
print(episodes.shape)
episodes.head()
episodes.columns.values
episodes.sinopsis_bart.value_counts(dropna=False)

# === Guardamos Dataset === #
episodes.to_csv("scraper/episodes.csv", index=False, sep='|')  
