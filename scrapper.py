from bs4 import BeautifulSoup
import requests

SEARCH_URL = 'https://gg.deals/games/?title='
GAME_URL = 'https://gg.deals/game/'

def search(key):

    # Load a page with games
    page = requests.get(SEARCH_URL+str(key)).text
    soup = BeautifulSoup(page,'html.parser')

    # Scrape through the searches and find the top three games
    titles = []
    games = soup.find_all('div','details')
    titles.append(games[0].find('a','ellipsis title').text.strip())
    
    # Now find the best prices for the three games
    shops = []
    prices = []
    links = []
    for title in titles:
        page = requests.get(GAME_URL + title.replace(" ",'-') + '/').text
        soup = BeautifulSoup(page,'html.parser')
        pageShops = soup.find_all('a','shop-link')
        pagePrices = soup.find_all('span','numeric')
        shopLinks = soup.find_all('a','game-hoverable full-link')
        # loop through all the shops and prices 
        shops.append(pageShops[0].img['alt'])

        # This should fix issue when adding to database due to string value
        prices.append(pagePrices[0].text.strip().replace('~','').replace('$','').split('\n')[0])
        if isinstance(prices[0],str):
            prices[0] = 0.00

        links.append(requests.get('http://tinyurl.com/api-create.php?url='+str('https://gg.deals'+shopLinks[0]['href'])).text)

    # Return an array of shops and prices
    return [titles.pop(), shops.pop(), prices.pop(), links.pop()]
