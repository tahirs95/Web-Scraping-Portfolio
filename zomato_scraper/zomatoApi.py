import requests
import json
import math
from db import db_functions

import re

import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydb"]
mycol = mydb["zomato"]


def deEmojify(text):
    regrex_pattern = re.compile(pattern="["
                                u"\U0001F600-\U0001F64F"  # emoticons
                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                "]+", flags=re.UNICODE)
    return regrex_pattern.sub(r'', text)


duplicate_class = db_functions.DuplicatesPipeline()
push_reviews_class = db_functions.ReviewsPipeline()


def api_func(url_part):
    url = "https://www.zomato.com/webroutes/getPage?page_url={}/reviews&location=&isMobile=0".format(
        url_part)

    # url = "https://www.zomato.com/webroutes/getPage?page_url=/santiago/peluquer%C3%ADa-francesa-boulevard-lavaud-santiago-centro/reviews&location=&isMobile=0"
    print("*****MAIN URL*****", url)

    session = requests.Session()
    session.headers.update({'User-Agent': 'Custom user agent'})

    response = session.get(url)
    response_body = json.loads(response.text)
    try:
        res_id = response_body['page_info']['resId']
    except Exception as e:
        print(str(e))
        print(response_body)
        return

    total_reviews_pages = math.ceil(int(
        response_body["page_data"]["sections"]["SECTION_BASIC_INFO"]["rating"]["votes"])/5)

    done_query = {"res_id": res_id, "status":"done"}
    mydoc = mycol.find(done_query)
    if mydoc.count() > 0:
        return

    myquery = {"res_id": res_id, "status":None}
    mydoc = mycol.find(myquery)
    if mydoc.count() > 0:
        count = mydoc[0].get("count")
    else:
        count = 1

    for i in range(count, total_reviews_pages+1):
        try:
            review_url = f"https://www.zomato.com/webroutes/reviews/loadMore?sort=dd&filter=reviews-dd&res_id={res_id}&page={i}"
            print("Review {}".format(i))

            response = session.get(review_url)
            response_body = json.loads(response.text)

            ratings = response_body['entities']['RATING']
            reviews = response_body['entities']['REVIEWS']

            for k, v in reviews.items():
                review = v['reviewText']
                if len(review) == 0:
                    pass
                else:
                    rating_id = str(v['rating']['entities'][0]['entity_ids'][0])

                    item = {
                        "review": deEmojify(review),
                        "score": ratings[rating_id]['rating'],
                        "source":"zomato"
                    }

                    duplicate_check = duplicate_class.process_item(item)

                    if not duplicate_check:
                        push_reviews_class.process_item(item)
            if i == (total_reviews_pages):
                mycol.update_one(
                {"res_id" : res_id},
                {"$set": {"count":i, "status":"done"}},
                upsert=True)
            else:
                mycol.update_one(
                {"res_id" : res_id},
                {"$set": {"count":i, "status":"in progress"}},
                upsert=True)
        except Exception as e:
            print(str(e))
            continue