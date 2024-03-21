
from twit import *
import json
import pandas as pd
from selenium.common.exceptions import TimeoutException

# obtiene los posts y agrega todos los post a una lista en gorma de jason

def getRedditPost(driver, cycle):
    listposts = []
    shreddit_feed = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//reddit-feed[contains(@label, "search-results-page-tab-posts")]')))
    start_index = 25 * cycle
    end_index = (cycle+1)*25
    xpath_expression = '(.//faceplate-tracker[contains(@noun, "post") and contains(@role, "article")])[position() >= {} and position() <= {}]'.format(start_index, end_index)
    try:
        articulos = WebDriverWait(shreddit_feed, 5).until(EC.presence_of_all_elements_located((By.XPATH, xpath_expression)))

        for art in articulos:
            infodelpost = art.get_attribute("data-faceplate-tracking-context")
            post_info = json.loads(infodelpost)
            listposts.append(post_info)
    
        return listposts
  
    except TimeoutException:
        return listposts[-end_index:]
    

    
# Tina el texto de cada post y devuelve los textos en un lista 
def get_content_from_url(driver,df_reddit):
    texto = []
    for url in df_reddit:
        driver.get(url)
        try:
            div = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "text-neutral-content") and contains(@slot, "text-body")]')))
            texto.append(div.text)

        except Exception:
            texto.append(None)
    return texto
    
#  Crea el dataframe final 
def GPDataFrameReddit(driver, listaposts):
    listafinal = []
    posts = listaposts
    
    for ar in posts:
        if isinstance(ar, dict) and set(ar.keys()) == {'post', 'action_info', 'subreddit'}:
            listafinal.append(ar['post'])
    try:
        datos_seleccionados = [{k: v for k, v in diccionario.items() if k in ['subreddit_id', 'subreddit_name', 'title', 'url', 'type', 'score', 'number_comments']} for diccionario in listafinal]
        df_final = pd.DataFrame(datos_seleccionados)
        df_final['url'] = 'https://www.reddit.com' + df_final['url']
        return df_final
    except KeyError:
        return df_final


def save_reddit_data_to_csv(driver, records, filepath, mode='a+'):
    with open(filepath, mode=mode, newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        df = GPDataFrameReddit(driver, records)
        if mode == 'a+' and f.tell() == 0:
            writer.writerow(df.columns)
        writer.writerows(df.values)

def mainReddit(filepath, prompt):
# toma el archivo y 
    last_position = None
    end_of_scroll_region = False
    unique_posts = set()
    qry, _ = query(prompt)
    driver = create_webdriver_instance(_)
    a = 0
    while not end_of_scroll_region:
        
        lista_posts = getRedditPost(driver,a)
        lista_final = []
        a+=1
        try:
            for card in lista_posts:
                post_id = generate_tweet_id()

                if post_id not in unique_posts:
                    unique_posts.add(post_id)
                    lista_final.append(card)

        except TypeError:
            continue

        print('BIEN:', lista_final)
        last_position, end_of_scroll_region = scroll_down_page(driver, last_position)
    driver.quit()
    
if __name__ == '__main__':
    filepath = 'pysimplegui.csv'
    prompt = 'testing'
    
    mainReddit(filepath, prompt)