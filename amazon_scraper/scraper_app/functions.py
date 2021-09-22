from selectorlib import Extractor
import requests
import re


e = Extractor.from_yaml_file('scraper_app/static/selectors/selectors.yml')

def scrape(url):

    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    r = requests.get(url, headers=headers)

    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print(
                "Page %s was blocked by Amazon. Please try using better proxies\n" % url)

        return None

    return (e.extract(r.text))


def process_data(data):
    if data:
        if data['bsr']:
            bsr = data['bsr'].replace(
                'Best Sellers Rank', '').replace(':', '').strip()
            bsr = re.sub('\(\s.*\s\)', ',', bsr)
            bsr = bsr.split(' , ')

            rankings = []

            cat_ranking = bsr[0].split('in')
            ranking = cat_ranking[0].replace('#', '').replace(',', "").strip() 
            category = cat_ranking[1].strip() 
            cat_ranking = {'Main Category': category,
                        'Main Category Ranking': ranking}
            rankings.append(cat_ranking)

            if bsr[1]:
                sub_cat_ranking = bsr[1].split('#')[1]
                sub_cat_ranking = sub_cat_ranking.split('in')
                sub_ranking = sub_cat_ranking[0].replace('#', '').replace(',', "").strip()
                sub_category = sub_cat_ranking[1].strip()
                sub_cat_ranking = {'Sub Category': sub_category,
                                'Sub Category Ranking': sub_ranking}
                rankings.append(sub_cat_ranking)

            data['ranking'] = rankings

        if data['rating']:
            rating = data['rating']
            rating = rating.split('out')[0].strip()
            data['rating'] = rating

        if data['no_of_reviews']:
            nor = data['no_of_reviews']
            nor = nor.split(' ')[0].strip()
            nor = nor.replace(',', "")

            data['no_of_reviews'] = nor

        if data['products_bought_together']:
            x = data['products_bought_together']
            x.pop(0)
            data['products_bought_together'] = x

        if data['variants']:
            variants = data['variants']
            variants = list(filter(lambda a: a != '', variants))
            data['variants'] = variants

        if data['brand']:
            brand = data['brand']
            if 'Visit the' in brand:
                brand = brand.replace('Visit the ', "").strip()
            elif 'Brand:' in brand:
                brand = brand.replace('Brand:', "").strip()
            elif 'Brand' in brand:
                brand = brand.replace('Brand', "").strip()

            data['brand'] = brand

        bullet_points = data['bullet_points']

        if bullet_points:
            bullet_dict = {}

            for x in range(0, len(bullet_points)):
                bullet_dict[x] = bullet_points[x]

            data['bullet_points'] = bullet_dict
    else:
        data={"none":"none"}
    return data
