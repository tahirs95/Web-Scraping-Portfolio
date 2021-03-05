from bs4 import BeautifulSoup
import json
import zomatoApi
import requests
from urllib.parse import urlparse, urljoin


user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"

start_urls = [
    "https://www.zomato.com/santiago/quinta-normal-restaurants",
    "https://www.zomato.com/santiago/colina-restaurants",
    "https://www.zomato.com/santiago/renca-restaurants",
    "https://www.zomato.com/santiago/pirque-restaurants"

]


def get_url_parts(url):

    session = requests.Session()
    session.headers.update({'User-Agent': user_agent})

    response = session.get(url)

    soup = BeautifulSoup(response.text, features='html.parser')

    next_page = soup.find('a', {"class": ['next']})

    links = soup.find_all('a', {"class": "result-title"})

    for restaurant in links:
        url_part = urlparse(restaurant['href']).path.replace('/es', '').strip()
        zomatoApi.api_func(url_part)

    while next_page:
        next_page_url = urljoin('https://www.zomato.com', next_page['href'])

        response = session.get(next_page_url)

        soup = BeautifulSoup(response.text, features='html.parser')

        next_page = soup.find('a', {"class": ['next']})

        links = soup.find_all('a', {"class": "result-title"})

        for restaurant in links:
            url_part = urlparse(restaurant['href']).path.replace(
                '/es', '').strip()
            zomatoApi.api_func(url_part)


with open("track.json", "r") as fp:
    data_json = json.load(fp)
    restaurant_list = data_json['restaurant_list']

if restaurant_list:
    index = start_urls.index(restaurant_list)
    for url in start_urls[index:]:
        with open("track.json", "w") as fp:
            data_json['restaurant_list'] = url
            json.dump(data_json, fp)
        print(url)
        get_url_parts(url)

else:
    for url in start_urls:
        with open("track.json", "w") as fp:
            data_json['restaurant_list'] = url
            json.dump(data_json, fp)
        print(url)
        get_url_parts(url)
