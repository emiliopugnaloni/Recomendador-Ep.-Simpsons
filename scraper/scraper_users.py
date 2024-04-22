# =========================== #
# Scraper de Usuarios NoHomer #
# =========================== #

# La idea es obtener informacion de los usuarios que votaron en NoHomer.
# Por ejemplo: https://nohomers.net/forums/index.php?members/%D0%9C%D0%B0%D1%85-power.67553


import pandas as pd
import numpy as np
import requests
import lxml.html
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

# === Congifuracion del driver para selenium === #

path = 'C:/Users/emiba/Downloads/chromedriver-win64/chromedriver.exe'
service = Service(executable_path=path)
driver = webdriver.Chrome(service=service)

# === Leemos dataset de reviews y generamos unos de usuarios ==== #

reviews_df = pd.read_csv('reviews.csv', sep='|')
users_df = reviews_df.groupby(['username','url_username'])['episode_name'].count().rename('q_reviews').reset_index()
del reviews_df 

# === Iterate over dataset and get the info === #

users_df['join_date'] = np.nan
users_df['gender'] = np.nan
#users_df = users_df.iloc[[50,50,50, 50, 50, 50, 50, 50]]
#users_df = users_df.iloc[0:5]


gender_element_html_list = []

for idx, user in users_df.iterrows():
    
    print(user['username'])
    
    url = user['url_username'] + '#about'
    driver.get(url)
    
    # Identificamos Join Date
    
    member_headers = driver.find_elements(by='xpath', value = './/div[@class="memberHeader-blurb"]')
    
    for member_header in member_headers:
        try:
            if member_header.find_elements(by='xpath', value = './/dl/dt')[0].text == 'Joined':
                users_df.loc[idx, 'join_date'] = member_header.find_elements(by='xpath', value = './/dl/dd')[0].text.strip()
        except:
            continue
        
    # Identificamos genero
    
    gender_element_html = 0
        
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, './/dl[@data-field="gender"]')))  # esperamos a que aparezca el elemento
        element_html = element.get_attribute('outerHTML') # lo guardamos en string, porque el elemento luego cambia de lugar (sale error)
        gender_element = lxml.html.fromstring(element_html) # lo pasamos a html para poder parsearlo
        users_df.loc[idx, 'gender'] = gender_element.xpath('.//dd')[0].text.strip() # extraemos el texto del genero
        
        #gender_element_html = driver.find_elements(by='xpath', value = './/dl[@data-field="gender"]')[0].get_attribute('outerHTML')  # lo guardamos en string, porque el elemento luego cambia de lugar (sale error)
        #gender_element = lxml.html.fromstring(gender_element_html)                 
        #users_df.loc[idx, 'gender'] = gender_element.xpath('.//dd')[0].text.strip()
        
    except:
        print('  No gender found')
    
    gender_element_html_list.append(gender_element_html)
    
    time.sleep(1)


users_df.to_csv('users.csv', sep='|', index=False)

#users_df.iloc[0:5]
#gender_element_html_list
#users_df.iloc[0:5].url_username.values
