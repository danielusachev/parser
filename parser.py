import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
import sys
import random
user_agent_list = [
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
]
smartphones_url = 'http://www.citilink.ru/catalog/smartfony/?sorting=price_desc'
notebooks_url = 'https://www.citilink.ru/catalog/noutbuki/?sorting=price_desc'
tv_url = 'https://www.citilink.ru/catalog/televizory/?sorting=price_desc'
N = 100

def get_titles(url, N, p):
    currentUrl = url+ '&p=' + str(p)
    if (N <= 0):
        return ''
    user_agent = random.choice(user_agent_list)
    headers = {'User-Agent': user_agent}
    r = requests.get(currentUrl,headers=headers)
    soup = BeautifulSoup(r.text)
    titles=soup.find_all('a', {'class': 'ProductCardHorizontal__title'})
    names = list()
    for item in titles:
        names.append(item.text)
    if (len(names) >= N):
        return names[:N]
    else:
        return names + get_titles(url, N - len(names), p + 1)

def get_prices(url, N, p):
    currentUrl = url+ '&p=' + str(p)
    if (N <= 0):
        return ''
    user_agent = random.choice(user_agent_list)
    headers = {'User-Agent': user_agent}
    r = requests.get(currentUrl,headers=headers)
    soup = BeautifulSoup(r.text)
    prices=soup.find_all('div', {'class': 'ProductCardHorizontal__buy-block'})
    costs = list()
    for item in prices:
        costs.append(re.findall('\d+', item.text)[0]+re.findall('\d+', item.text)[1])
    if (len(costs) >= N):
        return costs[:N]
    else:
        return costs + get_prices(url, N - len(costs), p + 1)

def get_links(url, N, p):
    currentUrl = url+ '&p=' + str(p)
    if (N <= 0):
        return ''
    user_agent = random.choice(user_agent_list)
    headers = {'User-Agent': user_agent}
    r = requests.get(currentUrl,headers=headers)
    soup = BeautifulSoup(r.text)
    links = soup.find_all('div', {'class': 'ProductCardHorizontal__header-block'})
    product_links = list()
    for item in links:
        for div in item.find_all('a', href=True):
            name = div['href']
            if ('https' not in name):
                product_links.append(name)
    if (len(product_links) >= N):
        return product_links[:N]
    else:
        return product_links + get_links(url, N - len(product_links), p + 1)

def get_total_amount(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    titles=soup.find_all('div', {'class': 'Subcategory__title-container'})
    for item in titles:
        return int(re.findall('\d+', item.text)[0])


def parse(url, N):
    titles = get_titles(url,N,1)
    prices = get_prices(url,N,1)
    links = get_links(url,N,1)
    for i in range(len(links)):
        links[i] = 'http://www.citilink.ru' + links[i]
    d = {'Наименование': titles, 'Цена': prices, 'Ссылка': links}
    df = pd.DataFrame(data=d)
    return df

if (len(sys.argv) > 1):
    N = int(sys.argv[1])

response = requests.get('http://citilink.ru/')
if (response.status_code == 403):
    sys.exit('Запустите скрипт позднее')
if (response.status_code == 429):
    sys.exit('Слишком частые запросы')
if (response.status_code == 404):
    sys.exit('Страница не найдена')
if (response.status_code == 500):
    sys.exit('Ошибка сервера')


smartphones_total = get_total_amount(smartphones_url)
notebooks_total = get_total_amount(notebooks_url)
tv_total = get_total_amount(tv_url)
if smartphones_total == None or notebooks_total == None or tv_total == None:
    sys.exit('Сайт временно недоступен')

if N > smartphones_total or N > notebooks_total or N > tv_total:
    N = min(smartphones_total, notebooks_total, tv_total)

parse(smartphones_url, N).to_excel('smartphones.xlsx')
parse(notebooks_url, N).to_excel('notebooks.xlsx')
parse(tv_url, N).to_excel('tv.xlsx')
