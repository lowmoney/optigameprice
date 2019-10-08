from bs4 import BeautifulSoup
import requests

SEARCH_URL = 'https://gg.deals/games/?title='
GAME_URL = 'https://gg.deals'

def search(key):

    # Load a page with games
    page = requests.get(SEARCH_URL+str(key)).text
    soup = BeautifulSoup(page,'html.parser')

    # Scrape through the searches and find the most relevant game ie. the first game
    title = ((soup.find('div','details')).find('a','ellipsis title').text.strip())

    # Get the link for the game
    link_to_game = soup.find('a','game-link')['href']
    
    
    try:
        page = requests.get(GAME_URL + link_to_game ).text
        soup = BeautifulSoup(page,'html.parser')

        shop = soup.find('a','shop-link').img['alt']
        price = soup.find('span','numeric').text.strip().replace('~','').replace('$','').split('\n')[0]
        link = requests.get('http://tinyurl.com/api-create.php?url='+str('https://gg.deals'+ soup.find('a','game-hoverable full-link')['href'])).text
    except:
        title = None
        shop = None
        price = None
        link = None



    # Return an array of shops and prices
    return [title, shop, price, link]
